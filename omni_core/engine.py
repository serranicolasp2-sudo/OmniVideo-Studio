"""
omni_core.engine — Motor común de FFmpeg y análisis de medios para Tu Tiendita IA.
Detección de aceleración por hardware (NVENC, AMF, CPU), análisis con ffprobe y utilidades de proceso.
"""

import os
import sys
import subprocess
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple, Set

MEDIA_EXTS_VIDEO: Set[str] = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".flv", ".ts", ".m4v"}
MEDIA_EXTS_IMAGE: Set[str] = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
MEDIA_EXTS_ALL: Set[str] = MEDIA_EXTS_VIDEO | MEDIA_EXTS_IMAGE


@dataclass
class MediaInfo:
    width: int
    height: int
    fps: float
    duration: float
    is_video: bool
    is_image: bool
    orientation: str  # "vertical", "horizontal", "square", "unknown"

    @property
    def orientation_label(self) -> str:
        if self.orientation == "vertical":
            return "📱 Vertical (9:16)"
        elif self.orientation == "square":
            return "⏹ Cuadrado (1:1)"
        elif self.orientation == "horizontal":
            return "🖥 Horizontal (16:9)"
        return "📐 Proporción personalizada"


class FFmpegEngine:
    """Motor centralizado para ejecutar y sondear operaciones con FFmpeg y FFprobe."""

    @staticmethod
    def ensure_path(custom_dirs: Optional[List[Path]] = None) -> None:
        """Asegura que ffmpeg y ffprobe estén en el PATH del sistema o en subcarpetas bin/."""
        candidates = []
        if custom_dirs:
            candidates.extend(custom_dirs)

        bundle_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
        candidates.extend([
            bundle_dir,
            bundle_dir / "bin",
            Path(sys.executable).parent / "bin",
            Path(sys.executable).parent,
            Path(__file__).resolve().parent.parent / "bin",
        ])

        for cand in candidates:
            if (cand / "ffmpeg.exe").exists() or (cand / "ffmpeg").exists():
                cand_str = str(cand)
                if cand_str not in os.environ.get("PATH", ""):
                    os.environ["PATH"] = cand_str + os.pathsep + os.environ.get("PATH", "")
                break

    @classmethod
    def probe(cls, file_path: str) -> Optional[MediaInfo]:
        """Analiza un archivo de video o imagen mediante ffprobe y extrae sus metadatos principales."""
        cls.ensure_path()
        try:
            cmd = [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height,r_frame_rate,duration,codec_type",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1",
                str(file_path)
            ]
            creation_flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            res = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=creation_flags
            )
            lines = res.stdout.strip().splitlines()
            data: Dict[str, str] = {}
            for line in lines:
                if "=" in line:
                    k, v = line.split("=", 1)
                    data[k.strip()] = v.strip()

            try:
                width = int(data.get("width", 0))
            except (ValueError, TypeError):
                width = 0

            try:
                height = int(data.get("height", 0))
            except (ValueError, TypeError):
                height = 0

            try:
                duration_val = float(data.get("duration", 0))
            except (ValueError, TypeError):
                duration_val = 0.0

            suffix = Path(file_path).suffix.lower()
            is_image = suffix in MEDIA_EXTS_IMAGE
            is_video = (duration_val > 0.1 or suffix in MEDIA_EXTS_VIDEO) and not is_image

            r_fps = data.get("r_frame_rate", "24/1")
            if "/" in r_fps:
                try:
                    num, den = r_fps.split("/")
                    fps_val = round(float(num) / float(den), 2)
                except Exception:
                    fps_val = 24.0
            else:
                try:
                    fps_val = round(float(r_fps), 2)
                except Exception:
                    fps_val = 24.0

            orientation = "unknown"
            if width > 0 and height > 0:
                if height > width:
                    orientation = "vertical"
                elif width == height:
                    orientation = "square"
                else:
                    orientation = "horizontal"

            return MediaInfo(
                width=width,
                height=height,
                fps=fps_val,
                duration=round(duration_val, 2),
                is_video=is_video,
                is_image=is_image,
                orientation=orientation
            )
        except Exception:
            return None

    @staticmethod
    def get_encoder_args(hw_choice: str, crf: int = 16) -> List[str]:
        """Devuelve los parámetros optimizados de codificación según el hardware seleccionado."""
        if "NVIDIA" in hw_choice:
            codec = "hevc_nvenc" if "HEVC" in hw_choice else "h264_nvenc"
            return [
                "-c:v", codec,
                "-preset", "p7",
                "-tune", "hq",
                "-multipass", "fullres",
                "-rc", "vbr",
                "-cq", str(crf),
                "-b:v", "0",
                "-spatial-aq", "1",
                "-temporal-aq", "1",
                "-pix_fmt", "yuv420p"
            ]
        elif "AMD Radeon" in hw_choice or "AMF" in hw_choice:
            return [
                "-c:v", "h264_amf",
                "-quality", "quality",
                "-rc", "cqp",
                "-qp_i", str(crf),
                "-qp_p", str(crf),
                "-pix_fmt", "yuv420p"
            ]
        else:
            return [
                "-c:v", "libx264",
                "-crf", str(crf),
                "-preset", "slow",
                "-pix_fmt", "yuv420p"
            ]

    @staticmethod
    def get_cpu_fallback_args(crf: int = 16) -> List[str]:
        """Argumentos seguros de fallback para CPU universal."""
        return [
            "-c:v", "libx264",
            "-crf", str(crf),
            "-preset", "slow",
            "-pix_fmt", "yuv420p"
        ]

    @staticmethod
    def find_batch_files(
        in_dir: str,
        out_dir: str,
        recursive: bool = False,
        tag: str = "procesado",
        exts: Optional[Set[str]] = None
    ) -> List[Tuple[str, str]]:
        """Escanea una carpeta en búsqueda de archivos de video o imagen y genera las rutas de destino."""
        if exts is None:
            exts = MEDIA_EXTS_ALL

        targets = []
        in_path = Path(in_dir)
        out_path = Path(out_dir)

        if not in_path.exists() or not in_path.is_dir():
            return targets

        iterator = in_path.rglob("*") if recursive else in_path.glob("*")

        for p in iterator:
            if p.is_file() and p.suffix.lower() in exts:
                # Evitar procesar archivos ya procesados o la carpeta de salida si está adentro
                if f"_{tag}" in p.stem.lower() or out_path in p.parents or p.parent == out_path:
                    continue
                rel = p.relative_to(in_path)
                dest = out_path / rel.parent / f"{p.stem}_{tag}{p.suffix}"
                targets.append((str(p), str(dest)))

        return targets

    @staticmethod
    def parse_time_progress(line: str) -> Optional[float]:
        """Extrae el tiempo actual en segundos desde la salida estándar de FFmpeg (time=HH:MM:SS.ms)."""
        m = re.search(r"time=(\d+):(\d+):(\d+\.\d+)", line)
        if m:
            hours, mins, secs = float(m.group(1)), float(m.group(2)), float(m.group(3))
            return hours * 3600 + mins * 60 + secs
        return None
