"""
omni_core.filters — Constructores de grafos de filtros de FFmpeg para las tres modalidades y el Modo Cadena.
"""

from typing import Optional, List, Dict, Any


def build_boost_filter(
    sharp: float = 0.5,
    clarity: float = 0.4,
    denoise: float = 0.35,
    deband: float = 0.3,
    color: float = 0.5,
    res_choice: str = "Mantener resolución original",
    in_w: int = 0,
    in_h: int = 0
) -> str:
    """Construye la cadena de filtros para optimización de imagen (OmniBoost)."""
    filters: List[str] = []

    # 1. Anti-Banding
    if deband > 0.05:
        strength = round(0.8 + deband * 2.2, 2)
        filters.append(f"gradfun={strength}:16")

    # 2. Reducción de ruido
    if denoise > 0.05:
        spatial = round(0.5 + denoise * 2.0, 2)
        temporal = round(1.0 + denoise * 3.5, 2)
        filters.append(f"hqdn3d={spatial}:{spatial}:{temporal}:{temporal}")

    # 3. Escalado / Aspect ratio si se solicita
    is_vert = (in_h > in_w) if (in_w > 0 and in_h > 0) else False
    is_square = (abs(in_w - in_h) < 10) if (in_w > 0 and in_h > 0) else False

    if "Auto-Adaptativo 1080p" in res_choice:
        scale_part = "-2:1920" if is_vert else ("1080:1080" if is_square else "1920:-2")
        filters.append(f"scale={scale_part}:flags=lanczos+accurate_rnd+full_chroma_int")
    elif "Auto-Adaptativo 4K" in res_choice:
        scale_part = "-2:3840" if is_vert else ("2160:2160" if is_square else "3840:-2")
        filters.append(f"scale={scale_part}:flags=lanczos+accurate_rnd+full_chroma_int")
    elif "Auto-Adaptativo 2K" in res_choice:
        scale_part = "-2:2560" if is_vert else ("1440:1440" if is_square else "2560:-2")
        filters.append(f"scale={scale_part}:flags=lanczos+accurate_rnd+full_chroma_int")
    elif "1080x1920" in res_choice:
        filters.append("scale=-2:1920:flags=lanczos+accurate_rnd+full_chroma_int")
    elif "2160x3840" in res_choice:
        filters.append("scale=-2:3840:flags=lanczos+accurate_rnd+full_chroma_int")
    elif "4K Ultra HD" in res_choice or "3840x2160" in res_choice:
        filters.append("scale=3840:2160:force_original_aspect_ratio=decrease:flags=lanczos+accurate_rnd+full_chroma_int,pad=3840:2160:(ow-iw)/2:(oh-ih)/2")
    elif "4K Cinema" in res_choice or "4096x2160" in res_choice:
        filters.append("scale=4096:2160:force_original_aspect_ratio=decrease:flags=lanczos+accurate_rnd+full_chroma_int,pad=4096:2160:(ow-iw)/2:(oh-ih)/2")
    elif "2K" in res_choice or "2560x1440" in res_choice:
        filters.append("scale=2560:1440:force_original_aspect_ratio=decrease:flags=lanczos+accurate_rnd+full_chroma_int,pad=2560:1440:(ow-iw)/2:(oh-ih)/2")
    elif "1080p" in res_choice or "1920x1080" in res_choice:
        filters.append("scale=1920:1080:force_original_aspect_ratio=decrease:flags=lanczos+accurate_rnd+full_chroma_int,pad=1920:1080:(ow-iw)/2:(oh-ih)/2")

    # 4. Claridad / Micro-contraste
    if clarity > 0.05:
        amount = round(clarity * 0.9, 2)
        filters.append(f"unsharp=5:5:{amount}:5:5:0.0")

    # 5. Nitidez CAS (FidelityFX)
    if sharp > 0.05:
        cas_val = round(0.2 + sharp * 0.65, 2)
        filters.append(f"cas={cas_val}")

    # 6. Rango de color y contraste
    if color > 0.05:
        contrast_val = round(1.0 + (color - 0.5) * 0.16, 3)
        saturation_val = round(1.0 + (color - 0.5) * 0.30, 3)
        gamma_val = round(1.0 + (color - 0.5) * 0.06, 3)
        filters.append(f"eq=contrast={contrast_val}:brightness=0.01:saturation={saturation_val}:gamma={gamma_val}")

    return ",".join(filters) if filters else "null"


def build_flow_filter(target_fps: int = 60, method_str: str = "Universal Adaptativo") -> str:
    """Construye el filtro de interpolación temporal y tasa de fotogramas (OmniFlow)."""
    if "Anime" in method_str:
        return f"framerate=fps={target_fps}:interp_start=5:interp_end=250:scene=5.0"
    elif "Motion Blend" in method_str:
        return f"minterpolate=fps={target_fps}:mi_mode=blend"
    elif "Vectorial" in method_str or "MCI" in method_str or "Flujo" in method_str:
        return f"minterpolate=fps={target_fps}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1"
    elif "Cadencia Pura" in method_str:
        return f"fps={target_fps}"
    else:
        # Universal Adaptativo por defecto con detección de cortes de plano
        return f"framerate=fps={target_fps}:interp_start=15:interp_end=240:scene=8.2"


def build_scale_filter(
    res_choice: str = "1080p Full HD (1920x1080)",
    method_str: str = "Detalle Fino (Lanczos + CAS)",
    in_w: int = 0,
    in_h: int = 0
) -> str:
    """Construye el filtro de escalado de resolución y preservación de aspecto (OmniScale)."""
    is_vert = (in_h > in_w) if (in_w > 0 and in_h > 0) else False
    is_square = (abs(in_w - in_h) < 10) if (in_w > 0 and in_h > 0) else False

    if "Auto 2x" in res_choice:
        scale_part = f"iw*2:ih*2"
        pad_filter = ""
    elif "Auto 4x" in res_choice:
        scale_part = f"iw*4:ih*4"
        pad_filter = ""
    elif "Auto-Adaptativo 4K" in res_choice:
        scale_part = "-2:3840" if is_vert else ("2160:2160" if is_square else "3840:-2")
        pad_filter = ""
    elif "Auto-Adaptativo 2K" in res_choice:
        scale_part = "-2:2560" if is_vert else ("1440:1440" if is_square else "2560:-2")
        pad_filter = ""
    elif "Auto-Adaptativo 1080p" in res_choice:
        scale_part = "-2:1920" if is_vert else ("1080:1080" if is_square else "1920:-2")
        pad_filter = ""
    elif "9:16 Vertical (1080x1920)" in res_choice or "1080x1920" in res_choice:
        scale_part = "-2:1920"
        pad_filter = ""
    elif "9:16 Vertical (2160x3840)" in res_choice or "2160x3840" in res_choice:
        scale_part = "-2:3840"
        pad_filter = ""
    elif "1:1 Cuadrado" in res_choice:
        scale_part = "1080:1080"
        pad_filter = ""
    elif "4K Ultra HD" in res_choice or "3840x2160" in res_choice:
        scale_part = "3840:2160:force_original_aspect_ratio=decrease"
        pad_filter = ",pad=3840:2160:(ow-iw)/2:(oh-ih)/2"
    elif "2K" in res_choice or "2560x1440" in res_choice:
        scale_part = "2560:1440:force_original_aspect_ratio=decrease"
        pad_filter = ",pad=2560:1440:(ow-iw)/2:(oh-ih)/2"
    elif "4K Cinema" in res_choice or "4096x2160" in res_choice:
        scale_part = "4096:2160:force_original_aspect_ratio=decrease"
        pad_filter = ",pad=4096:2160:(ow-iw)/2:(oh-ih)/2"
    else:
        # 1080p Full HD por defecto
        scale_part = "1920:1080:force_original_aspect_ratio=decrease"
        pad_filter = ",pad=1920:1080:(ow-iw)/2:(oh-ih)/2"

    if "Lanczos + CAS" in method_str:
        return f"scale={scale_part}:flags=lanczos+accurate_rnd+full_chroma_int{pad_filter},cas=0.55"
    elif "Spline Suave" in method_str:
        return f"scale={scale_part}:flags=spline+accurate_rnd+full_chroma_int{pad_filter}"
    elif "Unsharp" in method_str:
        return f"scale={scale_part}:flags=spline+accurate_rnd+full_chroma_int{pad_filter},unsharp=5:5:0.6:5:5:0.3"
    else:
        return f"scale={scale_part}:flags=lanczos+accurate_rnd+full_chroma_int{pad_filter}"


def build_chain_pipeline(
    enable_boost: bool = True,
    boost_params: Optional[Dict[str, Any]] = None,
    enable_flow: bool = True,
    flow_params: Optional[Dict[str, Any]] = None,
    enable_scale: bool = True,
    scale_params: Optional[Dict[str, Any]] = None,
    in_w: int = 0,
    in_h: int = 0
) -> str:
    """
    Construye un grafo de filtros encadenado de FFmpeg en UNA SOLA PASADA (Single-Pass Pipeline).
    Ejecuta en secuencia sin recompresión intermedia:
      [Limpieza / Color / De-banding] ➔ [Interpolación 60 FPS] ➔ [Escalado + Nitidez final]
    """
    filter_chain: List[str] = []

    if enable_boost:
        bp = boost_params or {}
        # En la etapa de limpieza del pipeline no escalamos todavía (el escalado va al final para ahorrar CPU)
        clean_vf = build_boost_filter(
            sharp=bp.get("sharp", 0.5),
            clarity=bp.get("clarity", 0.4),
            denoise=bp.get("denoise", 0.35),
            deband=bp.get("deband", 0.3),
            color=bp.get("color", 0.5),
            res_choice="Mantener resolución original",
            in_w=in_w,
            in_h=in_h
        )
        if clean_vf != "null":
            filter_chain.append(clean_vf)

    if enable_flow:
        fp = flow_params or {}
        flow_vf = build_flow_filter(
            target_fps=fp.get("target_fps", 60),
            method_str=fp.get("method_str", "Universal Adaptativo")
        )
        filter_chain.append(flow_vf)

    if enable_scale:
        sp = scale_params or {}
        scale_vf = build_scale_filter(
            res_choice=sp.get("res_choice", "1080p Full HD (1920x1080)"),
            method_str=sp.get("method_str", "Detalle Fino (Lanczos + CAS)"),
            in_w=in_w,
            in_h=in_h
        )
        filter_chain.append(scale_vf)

    return ",".join(filter_chain) if filter_chain else "null"
