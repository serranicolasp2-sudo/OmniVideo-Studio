"""
omni_core.ui_base — Clase base de interfaz gráfica para las aplicaciones de procesamiento de video.
Provee manejo de hilos, cola de mensajes, selección de archivos/carpetas y barra de progreso.
"""

import os
import sys
import subprocess
import threading
import queue
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, List, Tuple, Callable

# Asegurar ui_theme en el path
PARENT_DIR = Path(__file__).resolve().parent.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

from ui_theme import (
    COLOR_BIROME, COLOR_BIROME_HOVER, COLOR_TINTA, COLOR_MALVON, COLOR_MALVON_HOVER,
    COLOR_YEMA, COLOR_CINTA, COLOR_PAPEL, COLOR_PLATA, COLOR_PERIWINKLE,
    BG_APP, BG_CARD, CHIP_BG, CHIP_BORDER, BG_CARD_BORDER, BG_INPUT, BG_INPUT_BORDER, BG_CONSOLE, BG_CONSOLE_BORDER,
    TEXT_MAIN, TEXT_MUTED, TEXT_DIM,
    FONT_HERO, FONT_TITLE, FONT_SUB, FONT_LABEL, FONT_BODY, FONT_MONO, FONT_BTN, FONT_BADGE,
    setup_app_theme, PillBadge, PillButton, RoundedCard, SegmentedSwitch, create_header,
    ConsoleText
)
from omni_core.engine import FFmpegEngine, MediaInfo, MEDIA_EXTS_ALL


class BaseVideoApp:
    """Clase base reutilizable para interfaces gráficas de procesamiento multimedia."""

    def __init__(self, root: tk.Tk, app_title: str, app_icon: str = "omnisuite", default_tag: str = "procesado"):
        self.root = root
        self.app_title = app_title
        self.app_icon = app_icon
        self.default_tag = default_tag

        self.root.title(app_title)
        self.root.geometry("860x860")
        self.root.minsize(760, 700)
        self.root.configure(bg=BG_APP)

        setup_app_theme(self.root, app_icon=app_icon)
        FFmpegEngine.ensure_path()

        self.process: Optional[subprocess.Popen] = None
        self.is_running: bool = False
        self.cancel_requested: bool = False
        self.msg_queue: queue.Queue = queue.Queue()
        self.last_output_dir: str = ""
        self.current_tab_idx: int = 0

        # Variables de entrada y salida
        self.single_input_var = tk.StringVar()
        self.single_out_var = tk.StringVar()
        self.single_info_var = tk.StringVar(value="Esperando selección de archivo...")

        self.batch_input_var = tk.StringVar()
        self.batch_out_var = tk.StringVar()
        self.batch_recursive_var = tk.BooleanVar(value=False)

        self.hw_var = tk.StringVar(value="Automático (Recomendado)")
        self.status_var = tk.StringVar(value="Listo.")
        self.progress_val = tk.DoubleVar(value=0.0)

        # Iniciar despachador periódico de la cola
        self.root.after(100, self._process_queue)

    def _build_header(
        self,
        title: str,
        subtitle: str,
        badge_text: str = "EDICIÓN CREADORES",
        badge_bg: str = COLOR_YEMA,
        badge_fg: str = COLOR_CINTA,
        tag_text: str = "100% OFFLINE",
        brand_link: str = "https://tutiendita-ia.store"
    ):
        """Construye el encabezado oficial de Tu Tiendita IA."""
        create_header(
            self.root,
            title=title,
            subtitle=subtitle,
            badge_text=badge_text,
            rtx_text=tag_text,
            icon=self.app_icon
        )

    def _build_single_io_card(self, parent: tk.Widget, card_title: str = "Selección de Archivo Único"):
        """Construye la tarjeta de archivo único."""
        card = RoundedCard(parent, card_bg=BG_CARD, border_color=BG_CARD_BORDER)
        card.pack(fill="x", pady=(0, 8))
        f = card.body

        tk.Label(f, text=card_title, bg=BG_CARD, fg=TEXT_MAIN, font=FONT_TITLE).pack(anchor="w", pady=(0, 6))
        tk.Label(f, text="Archivo de entrada (Video o Imagen):", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_LABEL).pack(anchor="w", pady=(0, 4))

        in_row = tk.Frame(f, bg=BG_CARD)
        in_row.pack(fill="x", pady=(0, 6))

        in_well = tk.Frame(in_row, bg=BG_INPUT, highlightbackground=BG_INPUT_BORDER, highlightthickness=1)
        in_well.pack(side="left", fill="x", expand=True, padx=(0, 8))

        entry_in = tk.Entry(in_well, textvariable=self.single_input_var, bg=BG_INPUT, fg=TEXT_MAIN, insertbackground=TEXT_MAIN, relief="flat", font=FONT_BODY)
        entry_in.pack(fill="x", ipady=6, padx=8)

        btn_browse = PillButton(in_row, text="Examinar...", style="secondary", width=120, command=self._browse_single_input)
        btn_browse.pack(side="right")

        lbl_info = tk.Label(f, textvariable=self.single_info_var, bg=BG_CARD, fg=COLOR_PERIWINKLE, font=FONT_SUB)
        lbl_info.pack(anchor="w", pady=(0, 6))

        tk.Label(f, text="Archivo de salida personalizado:", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_LABEL).pack(anchor="w", pady=(2, 4))

        out_row = tk.Frame(f, bg=BG_CARD)
        out_row.pack(fill="x")

        out_well = tk.Frame(out_row, bg=BG_INPUT, highlightbackground=BG_INPUT_BORDER, highlightthickness=1)
        out_well.pack(side="left", fill="x", expand=True, padx=(0, 8))

        entry_out = tk.Entry(out_well, textvariable=self.single_out_var, bg=BG_INPUT, fg=TEXT_MAIN, insertbackground=TEXT_MAIN, relief="flat", font=FONT_BODY)
        entry_out.pack(fill="x", ipady=6, padx=8)

        btn_browse_out = PillButton(out_row, text="Guardar en...", style="secondary", width=120, command=self._browse_single_output)
        btn_browse_out.pack(side="right")

    def _build_batch_io_card(self, parent: tk.Widget, card_title: str = "Procesamiento por Lotes"):
        """Construye la tarjeta de procesamiento por lotes."""
        card = RoundedCard(parent, card_bg=BG_CARD, border_color=BG_CARD_BORDER)
        card.pack(fill="x", pady=(0, 8))
        f = card.body

        tk.Label(f, text=card_title, bg=BG_CARD, fg=TEXT_MAIN, font=FONT_TITLE).pack(anchor="w", pady=(0, 6))
        tk.Label(f, text="Carpeta de origen con clips o imágenes:", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_LABEL).pack(anchor="w", pady=(0, 4))

        in_row = tk.Frame(f, bg=BG_CARD)
        in_row.pack(fill="x", pady=(0, 6))

        in_well = tk.Frame(in_row, bg=BG_INPUT, highlightbackground=BG_INPUT_BORDER, highlightthickness=1)
        in_well.pack(side="left", fill="x", expand=True, padx=(0, 8))

        entry_in = tk.Entry(in_well, textvariable=self.batch_input_var, bg=BG_INPUT, fg=TEXT_MAIN, insertbackground=TEXT_MAIN, relief="flat", font=FONT_BODY)
        entry_in.pack(fill="x", ipady=6, padx=8)

        btn_browse = PillButton(in_row, text="Elegir Carpeta...", style="secondary", width=130, command=self._browse_batch_input)
        btn_browse.pack(side="right")

        tk.Label(f, text="Carpeta de salida:", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_LABEL).pack(anchor="w", pady=(2, 4))

        out_row = tk.Frame(f, bg=BG_CARD)
        out_row.pack(fill="x", pady=(0, 6))

        out_well = tk.Frame(out_row, bg=BG_INPUT, highlightbackground=BG_INPUT_BORDER, highlightthickness=1)
        out_well.pack(side="left", fill="x", expand=True, padx=(0, 8))

        entry_out = tk.Entry(out_well, textvariable=self.batch_out_var, bg=BG_INPUT, fg=TEXT_MAIN, insertbackground=TEXT_MAIN, relief="flat", font=FONT_BODY)
        entry_out.pack(fill="x", ipady=6, padx=8)

        btn_browse_out = PillButton(out_row, text="Elegir Destino...", style="secondary", width=130, command=self._browse_batch_output)
        btn_browse_out.pack(side="right")

        chk_rec = tk.Checkbutton(
            f, text="Incluir clips dentro de subcarpetas (recursivo)",
            variable=self.batch_recursive_var, bg=BG_CARD, fg=TEXT_MAIN, selectcolor=BG_INPUT,
            activebackground=BG_CARD, activeforeground=TEXT_MAIN, font=FONT_BODY
        )
        chk_rec.pack(anchor="w", pady=(2, 0))

    def _build_progress_card(self, parent: tk.Widget, on_start: Callable):
        """Construye la tarjeta de consola, barra de progreso y botones de acción."""
        card = RoundedCard(parent, card_bg=BG_CARD, border_color=BG_CARD_BORDER)
        card.pack(fill="both", expand=True, pady=(0, 8))
        f = card.body

        btn_row = tk.Frame(f, bg=BG_CARD)
        btn_row.pack(fill="x", pady=(0, 8))

        self.btn_run = PillButton(btn_row, text="▶ Comenzar Procesamiento", style="primary", height=38, command=on_start)
        self.btn_run.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.btn_cancel = PillButton(btn_row, text="⏹ Cancelar", style="danger", height=38, command=self._cancel, state="disabled")
        self.btn_cancel.pack(side="left", padx=(0, 8))

        self.btn_open = PillButton(btn_row, text="📂 Abrir Carpeta", style="secondary", height=38, command=self._open_output_dir, state="disabled")
        self.btn_open.pack(side="left")

        # Barra de progreso moderna
        self.progress_bar = ttk.Progressbar(f, variable=self.progress_val, maximum=100)
        self.progress_bar.pack(fill="x", pady=(0, 6))

        # Etiqueta de estado
        lbl_status = tk.Label(f, textvariable=self.status_var, bg=BG_CARD, fg=TEXT_MUTED, font=FONT_SUB)
        lbl_status.pack(anchor="w", pady=(0, 6))

        # Consola de registro
        self.console = ConsoleText(f, height=8)
        self.console.pack(fill="both", expand=True)

    def _browse_single_input(self):
        f = filedialog.askopenfilename(
            title="Seleccionar Video o Imagen",
            filetypes=[
                ("Videos e Imágenes", "*.mp4 *.mov *.mkv *.avi *.webm *.png *.jpg *.jpeg *.webp"),
                ("Videos", "*.mp4 *.mov *.mkv *.avi *.webm"),
                ("Imágenes", "*.png *.jpg *.jpeg *.webp"),
                ("Todos los archivos", "*.*")
            ]
        )
        if f:
            self.single_input_var.set(f)
            p = Path(f)
            out_name = f"{p.stem}_{self.default_tag}{p.suffix}"
            self.single_out_var.set(str(p.parent / out_name))

            info = FFmpegEngine.probe(f)
            if info:
                tipo = "Video" if info.is_video else "Imagen"
                dur_str = f" · {info.duration}s" if info.is_video else ""
                self.single_info_var.set(f"{tipo}: {info.width}x{info.height} ({info.orientation_label}) · {info.fps} FPS{dur_str}")
            else:
                self.single_info_var.set("Archivo seleccionado listo para procesar.")

    def _browse_single_output(self):
        cur = self.single_out_var.get()
        init_file = os.path.basename(cur) if cur else f"video_{self.default_tag}.mp4"
        init_dir = os.path.dirname(cur) if cur else ""
        f = filedialog.asksaveasfilename(
            title="Guardar archivo como",
            initialdir=init_dir,
            initialfile=init_file,
            filetypes=[("Mismo formato", "*.*"), ("Video MP4", "*.mp4"), ("Video MKV", "*.mkv")]
        )
        if f:
            self.single_out_var.set(f)

    def _browse_batch_input(self):
        d = filedialog.askdirectory(title="Seleccionar Carpeta de Origen")
        if d:
            self.batch_input_var.set(d)
            if not self.batch_out_var.get():
                tag_folder = f"Videos_{self.default_tag.title()}"
                self.batch_out_var.set(str(Path(d) / tag_folder))

    def _browse_batch_output(self):
        d = filedialog.askdirectory(title="Seleccionar Carpeta de Destino")
        if d:
            self.batch_out_var.set(d)

    def _open_output_dir(self):
        d = self.last_output_dir
        if not d or not os.path.exists(d):
            s_out = self.single_out_var.get()
            b_out = self.batch_out_var.get()
            if s_out and os.path.exists(os.path.dirname(s_out)):
                d = os.path.dirname(s_out)
            elif b_out and os.path.exists(b_out):
                d = b_out

        if d and os.path.exists(d):
            if os.name == 'nt':
                os.startfile(d)
            else:
                subprocess.Popen(["xdg-open", d])

    def _log(self, text: str):
        self.msg_queue.put(("log", text))

    def _set_status(self, text: str, progress: Optional[float] = None):
        self.msg_queue.put(("status", (text, progress)))

    def _cancel(self):
        if self.is_running:
            self.cancel_requested = True
            if self.process:
                try:
                    self.process.terminate()
                except Exception:
                    pass
            self._log("⚠️ Cancelación solicitada por el usuario.")
            self._set_status("Cancelando proceso...")

    def _process_queue(self):
        try:
            while True:
                msg, data = self.msg_queue.get_nowait()
                if msg == "log":
                    if hasattr(self, 'console'):
                        self.console.write(data + "\n")
                elif msg == "status":
                    text, prog = data
                    self.status_var.set(text)
                    if prog is not None:
                        self.progress_val.set(prog)
                elif msg == "finished":
                    self._on_worker_finished(data)
        except queue.Empty:
            pass
        self.root.after(100, self._process_queue)

    def _on_worker_finished(self, data):
        self.is_running = False
        self.btn_run.configure(state="normal")
        self.btn_cancel.configure(state="disabled")
        self.btn_open.configure(state="normal")

        success, total, total_time = data
        if self.cancel_requested:
            self._set_status(f"Proceso cancelado. ({success}/{total} completados)")
            self._log("\n🛑 Proceso detenido por el usuario.")
        else:
            self._set_status(f"¡Completado! {success}/{total} archivos procesados en {total_time}s.", progress=100)
            self._log(f"\n🎉 Todos los archivos fueron procesados exitosamente en {total_time} segundos.")
            if success > 0:
                messagebox.showinfo("Proceso Finalizado", f"Se procesaron {success} de {total} archivos correctamente en {total_time}s.")

    def run_worker_pipeline(
        self,
        targets: List[Tuple[str, str]],
        build_vf_func: Callable[[int, int, str], str],
        tag: str = "procesado",
        audio_action: str = "copy"
    ):
        """Worker centralizado que ejecuta la cola de archivos mediante FFmpeg con fallback GPU -> CPU."""
        total = len(targets)
        success_count = 0
        start_time = time.time()
        hw_choice = self.hw_var.get()

        for idx, (inp_path, out_path) in enumerate(targets, 1):
            if self.cancel_requested:
                break

            fname = os.path.basename(inp_path)
            self._set_status(f"Procesando [{idx}/{total}]: {fname}", progress=((idx - 1) / total) * 100)
            self._log(f"\n▶ [{idx}/{total}] Procesando: {fname}")

            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            self.last_output_dir = os.path.dirname(out_path)

            info = FFmpegEngine.probe(inp_path)
            in_w = info.width if info else 0
            in_h = info.height if info else 0
            duration = info.duration if info else 0.0
            is_image = info.is_image if info else (Path(inp_path).suffix.lower() in MEDIA_EXTS_ALL - MEDIA_EXTS_VIDEO)

            if in_w > 0 and in_h > 0:
                self._log(f"  Geometría origen: {in_w}x{in_h} [{info.orientation_label if info else 'Desconocida'}]")

            # Construir filtro
            vf = build_vf_func(in_w, in_h, inp_path)

            creation_flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

            if is_image:
                cmd = [
                    "ffmpeg", "-y", "-hide_banner",
                    "-i", inp_path,
                    "-vf", vf,
                    "-frames:v", "1",
                    "-update", "1",
                    out_path
                ]
            else:
                enc_args = FFmpegEngine.get_encoder_args(hw_choice)
                cmd = [
                    "ffmpeg", "-y", "-hide_banner",
                    "-i", inp_path,
                    "-vf", vf
                ] + enc_args + [
                    "-map", "0:v:0",
                    "-map", "0:a?",
                    "-c:a", audio_action,
                    out_path
                ]

            try:
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    creationflags=creation_flags
                )

                while True:
                    line = self.process.stderr.readline()
                    if not line and self.process.poll() is not None:
                        break
                    if line and not is_image and duration > 0:
                        curr_time = FFmpegEngine.parse_time_progress(line)
                        if curr_time is not None:
                            clip_pct = min(curr_time / duration, 1.0)
                            overall_pct = ((idx - 1 + clip_pct) / total) * 100
                            self._set_status(f"Procesando [{idx}/{total}]: {fname} ({int(clip_pct * 100)}%)", progress=overall_pct)

                self.process.wait()

                if self.process.returncode == 0:
                    success_count += 1
                    self._log(f"  ✓ Guardado: {os.path.basename(out_path)}")
                else:
                    # Intento de Fallback a CPU si falló GPU
                    if not self.cancel_requested and ("NVIDIA" in hw_choice or "AMD" in hw_choice):
                        self._log("  ⚠️ GPU no compatible para este clip. Reintentando con CPU de alta fidelidad...")
                        fallback_cmd = [
                            "ffmpeg", "-y", "-hide_banner",
                            "-i", inp_path,
                            "-vf", vf
                        ] + FFmpegEngine.get_cpu_fallback_args() + [
                            "-map", "0:v:0",
                            "-map", "0:a?",
                            "-c:a", audio_action,
                            out_path
                        ]
                        self.process = subprocess.Popen(
                            fallback_cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            bufsize=1,
                            universal_newlines=True,
                            creationflags=creation_flags
                        )
                        while True:
                            line = self.process.stderr.readline()
                            if not line and self.process.poll() is not None:
                                break
                        self.process.wait()
                        if self.process.returncode == 0:
                            success_count += 1
                            self._log(f"  ✓ Guardado (CPU): {os.path.basename(out_path)}")
                        else:
                            self._log(f"  ✗ Error al procesar {fname}")
                    else:
                        if not self.cancel_requested:
                            self._log(f"  ✗ Error al procesar {fname}")
            except Exception as e:
                self._log(f"  ✗ Excepción: {e}")

        total_time = round(time.time() - start_time, 1)
        self.msg_queue.put(("finished", (success_count, total, total_time)))
