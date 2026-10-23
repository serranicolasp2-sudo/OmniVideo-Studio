"""
OmniVideo Studio — Suite Audiovisual Unificada (Mejora, Fluidez 60 FPS, Escalado 4K & Modo Cadena)
Diseño: Premium Minimalista "Tu Tiendita IA" (https://tutiendita-ia.store)
Motor unificado mediante omni_core (100% offline con aceleración por hardware NVENC/AMF/CPU).
"""

import os
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

# Asegurar path para importar ui_theme y omni_core
CURRENT_DIR = Path(__file__).resolve().parent
APPS_DIR = CURRENT_DIR.parent
if str(APPS_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_DIR))

from ui_theme import (
    COLOR_BIROME, COLOR_BIROME_HOVER, COLOR_TINTA, COLOR_MALVON, COLOR_MALVON_HOVER,
    COLOR_YEMA, COLOR_CINTA, COLOR_PAPEL, COLOR_PLATA, COLOR_PERIWINKLE,
    BG_APP, BG_CARD, CHIP_BG, CHIP_BORDER, BG_CARD_BORDER, BG_INPUT, BG_INPUT_BORDER, BG_CONSOLE, BG_CONSOLE_BORDER,
    TEXT_MAIN, TEXT_MUTED, TEXT_DIM,
    FONT_HERO, FONT_TITLE, FONT_SUB, FONT_LABEL, FONT_BODY, FONT_MONO, FONT_BTN, FONT_BADGE,
    PillBadge, PillButton, RoundedCard, SegmentedSwitch, ModernSlider, ConsoleText
)
from omni_core import (
    FFmpegEngine,
    BaseVideoApp,
    build_boost_filter,
    build_flow_filter,
    build_scale_filter,
    build_chain_pipeline
)


class OmniVideoStudioApp(BaseVideoApp):
    """Aplicación audiovisual unificada con procesamiento individual y Modo Cadena de una sola pasada."""

    def __init__(self, root: tk.Tk):
        super().__init__(
            root,
            app_title="OmniVideo Studio — Suite Audiovisual Todo-en-Uno (Tu Tiendita IA)",
            app_icon="omnisuite",
            default_tag="omnivideo"
        )
        self.root.geometry("900x920")
        self.root.minsize(820, 780)

        # Variables de los modos
        self.mode_var = tk.StringVar(value="cadena")  # "cadena", "boost", "flow", "scale"

        # Parámetros Modo Cadena
        self.chain_enable_boost = tk.BooleanVar(value=True)
        self.chain_enable_flow = tk.BooleanVar(value=True)
        self.chain_enable_scale = tk.BooleanVar(value=True)

        # Parámetros de Mejora (Boost)
        self.sharp_var = tk.DoubleVar(value=50)
        self.clarity_var = tk.DoubleVar(value=40)
        self.denoise_var = tk.DoubleVar(value=35)
        self.deband_var = tk.DoubleVar(value=30)
        self.color_var = tk.DoubleVar(value=50)
        self.preset_boost_var = tk.StringVar(value="🌟 Universal / Equilibrado")

        # Parámetros de Fluidez (Flow)
        self.flow_fps_var = tk.StringVar(value="60 FPS (Ultra Fluidez Estándar)")
        self.flow_method_var = tk.StringVar(value="Universal Adaptativo (Cortes Limpios)")

        # Parámetros de Escalado (Scale)
        self.scale_res_var = tk.StringVar(value="Auto-Adaptativo 4K UHD (3840x2160 / 2160x3840)")
        self.scale_method_var = tk.StringVar(value="Detalle Fino (Lanczos + CAS FidelityFX)")

        # Sub-pestaña de Entrada/Salida (0: Archivo Único, 1: Lote)
        self.io_tab_idx = 0

        self._build_ui()

    def _build_ui(self):
        # 1. Encabezado con marca oficial
        self._build_header(
            title="OmniVideo Studio",
            subtitle="Suite Audiovisual Todo-en-Uno: Mejora, Fluidez a 60 FPS, Escalado 4K y Modo Cadena",
            badge_text="EDICIÓN CREADORES",
            tag_text="MOTOR UNIFICADO",
            brand_link="https://tutiendita-ia.store"
        )

        # Contenedor principal con scroll o adaptable
        main_frame = tk.Frame(self.root, bg=BG_APP)
        main_frame.pack(fill="both", expand=True, padx=22, pady=(0, 6))

        # 2. Selector de Modo Principal (Pill Bar)
        tab_box = tk.Frame(main_frame, bg=BG_APP)
        tab_box.pack(fill="x", pady=(0, 8))

        self.mode_switch = SegmentedSwitch(
            tab_box,
            options=[
                "🔗 Modo Cadena (1 Pasada)",
                "🎨 Solo Mejorar (Boost)",
                "⚡ Solo Fluidez (60 FPS)",
                "🔍 Solo Escalar (Upscale)"
            ],
            on_change=self._on_mode_change
        )
        self.mode_switch.pack(anchor="w")

        # 3. Contenedor de Opciones del Modo Activo
        self.mode_container = tk.Frame(main_frame, bg=BG_APP)
        self.mode_container.pack(fill="x", pady=(0, 8))

        self.mode_pages = []
        self._build_mode_cadena_ui()
        self._build_mode_boost_ui()
        self._build_mode_flow_ui()
        self._build_mode_scale_ui()

        # Mostrar por defecto el Modo Cadena
        self._on_mode_change(0)

        # 4. Tarjeta de Entrada y Salida (Archivo Único vs Lote)
        io_card = RoundedCard(main_frame, card_bg=BG_CARD, border_color=BG_CARD_BORDER)
        io_card.pack(fill="x", pady=(0, 8))
        io_body = io_card.body

        io_top = tk.Frame(io_body, bg=BG_CARD)
        io_top.pack(fill="x", pady=(0, 6))

        tk.Label(io_top, text="Archivos a Procesar:", bg=BG_CARD, fg=TEXT_MAIN, font=FONT_TITLE).pack(side="left")

        self.io_switch = SegmentedSwitch(
            io_top,
            options=["📄 Archivo Único", "📁 Carpeta Completa (Lote)"],
            on_change=self._on_io_tab_change
        )
        self.io_switch.pack(side="right")

        self.io_container = tk.Frame(io_body, bg=BG_CARD)
        self.io_container.pack(fill="x")

        # Página Archivo Único
        self.p_single = tk.Frame(self.io_container, bg=BG_CARD)
        self._build_single_io_content(self.p_single)

        # Página Lote
        self.p_batch = tk.Frame(self.io_container, bg=BG_CARD)
        self._build_batch_io_content(self.p_batch)

        self._on_io_tab_change(0)

        # 5. Tarjeta de Aceleración y Progreso
        prog_card = RoundedCard(main_frame, card_bg=BG_CARD, border_color=BG_CARD_BORDER)
        prog_card.pack(fill="both", expand=True, pady=(0, 8))
        pb = prog_card.body

        # Selector de Hardware
        hw_row = tk.Frame(pb, bg=BG_CARD)
        hw_row.pack(fill="x", pady=(0, 8))

        tk.Label(hw_row, text="Acelerador / Motor:", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_LABEL).pack(side="left", padx=(0, 8))

        self.hw_cb = ttk.Combobox(hw_row, textvariable=self.hw_var, state="readonly", width=46)
        self.hw_cb['values'] = (
            "NVIDIA GeForce RTX (NVENC p7 + Spatial/Temporal AQ)",
            "NVIDIA GeForce RTX — HEVC / H.265 (Ultra Calidad 4K)",
            "AMD Radeon — AMF Hardware (RX 6000 / 7000 Series)",
            "CPU / Software Universal (libx264 — Máxima compatibilidad)"
        )
        self.hw_cb.current(0)
        self.hw_cb.pack(side="left")

        # Botones de control
        btn_box = tk.Frame(pb, bg=BG_CARD)
        btn_box.pack(fill="x", pady=(0, 8))

        self.btn_run = PillButton(btn_box, text="▶ INICIAR PROCESAMIENTO", style="primary", height=38, command=self._start_processing)
        self.btn_run.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.btn_cancel = PillButton(btn_box, text="⏹ Cancelar", style="danger", height=38, width=105, command=self._cancel, state="disabled")
        self.btn_cancel.pack(side="left", padx=(0, 8))

        self.btn_open = PillButton(btn_box, text="📂 Abrir Carpeta", style="secondary", height=38, command=self._open_output_dir)
        self.btn_open.pack(side="left")

        # Barra y Estado
        self.progress_bar = ttk.Progressbar(pb, variable=self.progress_val, maximum=100)
        self.progress_bar.pack(fill="x", pady=(0, 6))

        lbl_status = tk.Label(pb, textvariable=self.status_var, bg=BG_CARD, fg=COLOR_PERIWINKLE, font=FONT_SUB)
        lbl_status.pack(anchor="w", pady=(0, 6))

        # Consola
        self.console = ConsoleText(pb, height=7)
        self.console.pack(fill="both", expand=True)
        self.console.write("OmniVideo Studio listo. Selecciona tus clips para procesar con aceleración por hardware.\n")

    # =========================================================================
    # CONSTRUCCIÓN DE SUB-MODOS
    # =========================================================================

    def _build_mode_cadena_ui(self):
        """Pestaña 0: Modo Cadena (Single-Pass Pipeline)."""
        card = RoundedCard(self.mode_container, card_bg=BG_CARD, border_color=BG_CARD_BORDER)
        self.mode_pages.append(card)
        f = card.body

        top_info = tk.Frame(f, bg=BG_CARD)
        top_info.pack(fill="x", pady=(0, 6))

        tk.Label(top_info, text="🔗 Pipeline en Cadena (1 Sola Pasada de FFmpeg)", bg=BG_CARD, fg=TEXT_MAIN, font=FONT_TITLE).pack(side="left")
        PillBadge(top_info, text="SIN PÉRDIDA GENERACIONAL", bg_color=CHIP_BG, fg_color=COLOR_YEMA, border_color=CHIP_BORDER).pack(side="left", padx=8)

        tk.Label(
            f,
            text="Aplica optimización de imagen, fluidez a 60 FPS y escalado a resolución destino en un único comando de FFmpeg.\nAhorra hasta un 65% de tiempo de exportación y preserva la máxima calidad de color y nitidez.",
            bg=BG_CARD, fg=TEXT_MUTED, font=FONT_SUB, justify="left"
        ).pack(anchor="w", pady=(0, 8))

        stages_row = tk.Frame(f, bg=BG_CARD)
        stages_row.pack(fill="x", pady=2)

        chk1 = tk.Checkbutton(
            stages_row, text="1. Limpieza & Color (Boost)", variable=self.chain_enable_boost,
            bg=BG_CARD, fg=TEXT_MAIN, selectcolor=BG_INPUT, activebackground=BG_CARD, font=FONT_LABEL
        )
        chk1.pack(side="left", padx=(0, 16))

        chk2 = tk.Checkbutton(
            stages_row, text="2. Interpolación 60 FPS (Flow)", variable=self.chain_enable_flow,
            bg=BG_CARD, fg=TEXT_MAIN, selectcolor=BG_INPUT, activebackground=BG_CARD, font=FONT_LABEL
        )
        chk2.pack(side="left", padx=(0, 16))

        chk3 = tk.Checkbutton(
            stages_row, text="3. Escalado 4K UHD (Scale)", variable=self.chain_enable_scale,
            bg=BG_CARD, fg=TEXT_MAIN, selectcolor=BG_INPUT, activebackground=BG_CARD, font=FONT_LABEL
        )
        chk3.pack(side="left")

    def _build_mode_boost_ui(self):
        """Pestaña 1: Solo Mejorar (Boost)."""
        card = RoundedCard(self.mode_container, card_bg=BG_CARD, border_color=BG_CARD_BORDER)
        self.mode_pages.append(card)
        f = card.body

        tk.Label(f, text="🎨 Optimización de Imagen y Nitidez CAS", bg=BG_CARD, fg=TEXT_MAIN, font=FONT_TITLE).pack(anchor="w", pady=(0, 4))

        p_row = tk.Frame(f, bg=BG_CARD)
        p_row.pack(fill="x", pady=(0, 6))

        tk.Label(p_row, text="Perfil / Preset:", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_LABEL).pack(side="left", padx=(0, 8))
        cb = ttk.Combobox(p_row, textvariable=self.preset_boost_var, state="readonly", width=42)
        cb['values'] = (
            "🌟 Universal / Equilibrado",
            "🎬 Cine & Películas Reales",
            "🎨 Animación 3D & CGI",
            "⛩️ Anime & Animación 2D",
            "🤖 Videos de IA (Anti-Banding)",
            "📼 Restauración & Denoise"
        )
        cb.pack(side="left")
        cb.bind("<<ComboboxSelected>>", self._on_preset_boost_change)

        # Sliders
        sf = tk.Frame(f, bg=BG_CARD)
        sf.pack(fill="x")

        tk.Label(sf, text="Nitidez CAS:", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_LABEL).grid(row=0, column=0, sticky="w", padx=(0, 4), pady=2)
        ModernSlider(sf, from_=0, to=100, variable=self.sharp_var, length=160).grid(row=0, column=1, sticky="w", pady=2)

        tk.Label(sf, text="Denoise:", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_LABEL).grid(row=0, column=2, sticky="w", padx=(12, 4), pady=2)
        ModernSlider(sf, from_=0, to=100, variable=self.denoise_var, length=160).grid(row=0, column=3, sticky="w", pady=2)

        tk.Label(sf, text="De-Banding:", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_LABEL).grid(row=1, column=0, sticky="w", padx=(0, 4), pady=2)
        ModernSlider(sf, from_=0, to=100, variable=self.deband_var, length=160).grid(row=1, column=1, sticky="w", pady=2)

        tk.Label(sf, text="Color HDR:", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_LABEL).grid(row=1, column=2, sticky="w", padx=(12, 4), pady=2)
        ModernSlider(sf, from_=0, to=100, variable=self.color_var, length=160).grid(row=1, column=3, sticky="w", pady=2)

    def _build_mode_flow_ui(self):
        """Pestaña 2: Solo Fluidez (Flow)."""
        card = RoundedCard(self.mode_container, card_bg=BG_CARD, border_color=BG_CARD_BORDER)
        self.mode_pages.append(card)
        f = card.body

        tk.Label(f, text="⚡ Multiplicador de Fluidez a 60 / 120 FPS", bg=BG_CARD, fg=TEXT_MAIN, font=FONT_TITLE).pack(anchor="w", pady=(0, 4))

        r1 = tk.Frame(f, bg=BG_CARD)
        r1.pack(fill="x", pady=2)

        tk.Label(r1, text="Tasa de FPS Deseada:", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_LABEL).pack(side="left", padx=(0, 8))
        cb_fps = ttk.Combobox(r1, textvariable=self.flow_fps_var, state="readonly", width=36)
        cb_fps['values'] = ("60 FPS (Ultra Fluidez Estándar)", "120 FPS (Pantallas High Refresh)")
        cb_fps.pack(side="left")

        r2 = tk.Frame(f, bg=BG_CARD)
        r2.pack(fill="x", pady=2)

        tk.Label(r2, text="Método de Interpolación:", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_LABEL).pack(side="left", padx=(0, 8))
        cb_m = ttk.Combobox(r2, textvariable=self.flow_method_var, state="readonly", width=36)
        cb_m['values'] = (
            "Universal Adaptativo (Cortes Limpios)",
            "Anime & Animación 2D",
            "Motion Blend (Transición Suave)",
            "Cadencia Pura (Duplicación)",
            "Vectorial MCI (Flujo Óptico Bidir - Lento)"
        )
        cb_m.pack(side="left")

    def _build_mode_scale_ui(self):
        """Pestaña 3: Solo Escalar (Scale)."""
        card = RoundedCard(self.mode_container, card_bg=BG_CARD, border_color=BG_CARD_BORDER)
        self.mode_pages.append(card)
        f = card.body

        tk.Label(f, text="🔍 Escalado de Resolución Inteligente", bg=BG_CARD, fg=TEXT_MAIN, font=FONT_TITLE).pack(anchor="w", pady=(0, 4))

        r1 = tk.Frame(f, bg=BG_CARD)
        r1.pack(fill="x", pady=2)

        tk.Label(r1, text="Resolución Objetivo:", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_LABEL).pack(side="left", padx=(0, 8))
        cb_res = ttk.Combobox(r1, textvariable=self.scale_res_var, state="readonly", width=42)
        cb_res['values'] = (
            "Auto-Adaptativo 4K UHD (3840x2160 / 2160x3840)",
            "Auto-Adaptativo 1080p (1920x1080 / 1080x1920)",
            "Auto-Adaptativo 2K QHD (2560x1440 / 1440x2560)",
            "1080p Full HD (1920x1080)",
            "4K Ultra HD (3840x2160)",
            "9:16 Vertical (1080x1920)",
            "9:16 Vertical (2160x3840)",
            "1:1 Cuadrado (1080x1080)",
            "Auto 2x (Duplicar Resolución)",
            "Auto 4x (Cuadruplicar Resolución)"
        )
        cb_res.pack(side="left")

        r2 = tk.Frame(f, bg=BG_CARD)
        r2.pack(fill="x", pady=2)

        tk.Label(r2, text="Filtro de Reconstrucción:", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_LABEL).pack(side="left", padx=(0, 8))
        cb_m = ttk.Combobox(r2, textvariable=self.scale_method_var, state="readonly", width=42)
        cb_m['values'] = (
            "Detalle Fino (Lanczos + CAS FidelityFX)",
            "Lanczos Puro (Alta Definición)",
            "Spline Suave (Cine / Granular)",
            "Nitidez Acentuada (Unsharp)"
        )
        cb_m.pack(side="left")

    def _build_single_io_content(self, parent):
        tk.Label(parent, text="Archivo de entrada (Video o Imagen):", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_LABEL).pack(anchor="w", pady=(0, 2))
        r1 = tk.Frame(parent, bg=BG_CARD)
        r1.pack(fill="x", pady=(0, 4))
        w1 = tk.Frame(r1, bg=BG_INPUT, highlightbackground=BG_INPUT_BORDER, highlightthickness=1)
        w1.pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Entry(w1, textvariable=self.single_input_var, bg=BG_INPUT, fg=TEXT_MAIN, relief="flat", font=FONT_BODY).pack(fill="x", ipady=4, padx=6)
        PillButton(r1, text="Examinar...", style="secondary", width=110, command=self._browse_single_input).pack(side="right")

        tk.Label(parent, textvariable=self.single_info_var, bg=BG_CARD, fg=COLOR_PERIWINKLE, font=FONT_SUB).pack(anchor="w", pady=(0, 4))

        tk.Label(parent, text="Destino personalizado:", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_LABEL).pack(anchor="w", pady=(0, 2))
        r2 = tk.Frame(parent, bg=BG_CARD)
        r2.pack(fill="x")
        w2 = tk.Frame(r2, bg=BG_INPUT, highlightbackground=BG_INPUT_BORDER, highlightthickness=1)
        w2.pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Entry(w2, textvariable=self.single_out_var, bg=BG_INPUT, fg=TEXT_MAIN, relief="flat", font=FONT_BODY).pack(fill="x", ipady=4, padx=6)
        PillButton(r2, text="Guardar en...", style="secondary", width=110, command=self._browse_single_output).pack(side="right")

    def _build_batch_io_content(self, parent):
        tk.Label(parent, text="Carpeta de origen con clips:", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_LABEL).pack(anchor="w", pady=(0, 2))
        r1 = tk.Frame(parent, bg=BG_CARD)
        r1.pack(fill="x", pady=(0, 4))
        w1 = tk.Frame(r1, bg=BG_INPUT, highlightbackground=BG_INPUT_BORDER, highlightthickness=1)
        w1.pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Entry(w1, textvariable=self.batch_input_var, bg=BG_INPUT, fg=TEXT_MAIN, relief="flat", font=FONT_BODY).pack(fill="x", ipady=4, padx=6)
        PillButton(r1, text="Elegir Carpeta...", style="secondary", width=120, command=self._browse_batch_input).pack(side="right")

        tk.Label(parent, text="Carpeta de salida:", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_LABEL).pack(anchor="w", pady=(0, 2))
        r2 = tk.Frame(parent, bg=BG_CARD)
        r2.pack(fill="x", pady=(0, 4))
        w2 = tk.Frame(r2, bg=BG_INPUT, highlightbackground=BG_INPUT_BORDER, highlightthickness=1)
        w2.pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Entry(w2, textvariable=self.batch_out_var, bg=BG_INPUT, fg=TEXT_MAIN, relief="flat", font=FONT_BODY).pack(fill="x", ipady=4, padx=6)
        PillButton(r2, text="Elegir Destino...", style="secondary", width=120, command=self._browse_batch_output).pack(side="right")

        tk.Checkbutton(
            parent, text="Incluir clips dentro de subcarpetas (recursivo)", variable=self.batch_recursive_var,
            bg=BG_CARD, fg=TEXT_MAIN, selectcolor=BG_INPUT, activebackground=BG_CARD, font=FONT_BODY
        ).pack(anchor="w")

    def _on_mode_change(self, idx: int):
        self.current_mode_idx = idx
        mode_keys = ["cadena", "boost", "flow", "scale"]
        self.mode_var.set(mode_keys[idx])
        self.default_tag = f"omni_{mode_keys[idx]}"

        for i, page in enumerate(self.mode_pages):
            if i == idx:
                page.pack(fill="x")
            else:
                page.pack_forget()

    def _on_io_tab_change(self, idx: int):
        self.io_tab_idx = idx
        if idx == 0:
            self.p_single.pack(fill="x")
            self.p_batch.pack_forget()
        else:
            self.p_batch.pack(fill="x")
            self.p_single.pack_forget()

    def _on_preset_boost_change(self, event=None):
        val = self.preset_boost_var.get()
        if "Universal" in val:
            self.sharp_var.set(50); self.clarity_var.set(40); self.denoise_var.set(35); self.deband_var.set(30); self.color_var.set(50)
        elif "Cine" in val:
            self.sharp_var.set(40); self.clarity_var.set(30); self.denoise_var.set(20); self.deband_var.set(40); self.color_var.set(50)
        elif "Animación 3D" in val:
            self.sharp_var.set(60); self.clarity_var.set(55); self.denoise_var.set(30); self.deband_var.set(45); self.color_var.set(65)
        elif "Anime" in val:
            self.sharp_var.set(75); self.clarity_var.set(45); self.denoise_var.set(50); self.deband_var.set(60); self.color_var.set(60)
        elif "Videos de IA" in val:
            self.sharp_var.set(55); self.clarity_var.set(50); self.denoise_var.set(45); self.deband_var.set(75); self.color_var.set(55)
        elif "Restauración" in val:
            self.sharp_var.set(35); self.clarity_var.set(30); self.denoise_var.set(85); self.deband_var.set(70); self.color_var.set(45)

    def _build_active_vf(self, in_w: int, in_h: int, path: str) -> str:
        """Construye el filtro según el modo activo."""
        mode = self.mode_var.get()

        if mode == "cadena":
            target_fps = 120 if "120" in self.flow_fps_var.get() else 60
            return build_chain_pipeline(
                enable_boost=self.chain_enable_boost.get(),
                boost_params={
                    "sharp": self.sharp_var.get() / 100.0,
                    "clarity": self.clarity_var.get() / 100.0,
                    "denoise": self.denoise_var.get() / 100.0,
                    "deband": self.deband_var.get() / 100.0,
                    "color": self.color_var.get() / 100.0
                },
                enable_flow=self.chain_enable_flow.get(),
                flow_params={
                    "target_fps": target_fps,
                    "method_str": self.flow_method_var.get()
                },
                enable_scale=self.chain_enable_scale.get(),
                scale_params={
                    "res_choice": self.scale_res_var.get(),
                    "method_str": self.scale_method_var.get()
                },
                in_w=in_w,
                in_h=in_h
            )
        elif mode == "boost":
            return build_boost_filter(
                sharp=self.sharp_var.get() / 100.0,
                clarity=self.clarity_var.get() / 100.0,
                denoise=self.denoise_var.get() / 100.0,
                deband=self.deband_var.get() / 100.0,
                color=self.color_var.get() / 100.0,
                res_choice="Mantener resolución original",
                in_w=in_w,
                in_h=in_h
            )
        elif mode == "flow":
            target_fps = 120 if "120" in self.flow_fps_var.get() else 60
            return build_flow_filter(target_fps=target_fps, method_str=self.flow_method_var.get())
        elif mode == "scale":
            return build_scale_filter(
                res_choice=self.scale_res_var.get(),
                method_str=self.scale_method_var.get(),
                in_w=in_w,
                in_h=in_h
            )
        return "null"

    def _start_processing(self):
        if self.is_running:
            return

        is_single = (self.io_tab_idx == 0)
        mode = self.mode_var.get()

        if is_single:
            inp = self.single_input_var.get().strip()
            out = self.single_out_var.get().strip()
            if not inp or not os.path.exists(inp):
                messagebox.showerror("Error", "Selecciona un archivo de entrada válido.")
                return
            if not out:
                p = Path(inp)
                out = str(p.parent / f"{p.stem}_{self.default_tag}{p.suffix}")
                self.single_out_var.set(out)
            targets = [(inp, out)]
        else:
            in_dir = self.batch_input_var.get().strip()
            out_dir = self.batch_out_var.get().strip()
            if not in_dir or not os.path.exists(in_dir):
                messagebox.showerror("Error", "Selecciona una carpeta de entrada válida.")
                return
            if not out_dir:
                out_dir = str(Path(in_dir) / f"Videos_{self.default_tag.title()}")
                self.batch_out_var.set(out_dir)
            targets = FFmpegEngine.find_batch_files(
                in_dir=in_dir,
                out_dir=out_dir,
                recursive=self.batch_recursive_var.get(),
                tag=self.default_tag
            )
            if not targets:
                messagebox.showwarning("Atención", "No se encontraron videos ni imágenes válidas en la carpeta indicada.")
                return

        self.is_running = True
        self.cancel_requested = False
        self.btn_run.configure(state="disabled")
        self.btn_cancel.configure(state="normal")
        self.btn_open.configure(state="disabled")
        self.progress_val.set(0.0)

        self._log(f"\n=======================================================")
        self._log(f"Iniciando OmniVideo Studio — Modo activo: {mode.upper()}")
        self._log(f"Total de elementos en cola: {len(targets)}")
        self._log(f"=======================================================")

        th = threading.Thread(
            target=self.run_worker_pipeline,
            args=(targets, self._build_active_vf, self.default_tag),
            daemon=True
        )
        th.start()


def main():
    root = tk.Tk()
    app = OmniVideoStudioApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
