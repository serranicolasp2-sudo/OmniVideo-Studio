"""
ui_theme.py — Sistema de Diseño Premium Minimalista "Tu Tiendita IA"
Sitio web oficial de la marca: https://tutiendita-ia.store

Colores oficiales de marca:
  • Birome: #1E3C96 (Azul principal de acción)
  • Tinta:   #16205A (Azul marino noche)
  • Malvón:  #E0435C (Coral acento / vivo)
  • Yema:    #FFD23F (Amarillo cálido / insignia)
  • Cinta:   #1A1712 (Carbón cinta / texto sobre yema)
  • Papel:   #F6F7FA (Blanco papel suave / texto principal)
  • Plata:   #8B97B0 (Gris plata suave / subtítulos)
  • Celeste: #AFC0FF (Periwinkle micro-acento)

Los fondos derivan de Tinta (azul noche) en lugar de un negro neutro, así toda
la interfaz respira la marca. Los íconos de cada app viven en ./iconos.
"""

import sys
import ctypes
from pathlib import Path
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
from PIL import Image, ImageDraw, ImageTk

ICONS_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)) / "iconos"

# --- PALETA OFICIAL "TU TIENDITA IA" ---
COLOR_BIROME = "#1E3C96"
COLOR_BIROME_HOVER = "#2A4FC0"
COLOR_BIROME_LIGHT = "#3A62DE"
COLOR_TINTA = "#16205A"
COLOR_MALVON = "#E0435C"
COLOR_MALVON_HOVER = "#EC5770"
COLOR_YEMA = "#FFD23F"
COLOR_CINTA = "#1A1712"
COLOR_PAPEL = "#F6F7FA"
COLOR_PLATA = "#8B97B0"
COLOR_PERIWINKLE = "#AFC0FF"

# Superficies & Fondos (Noche Tinta Studio)
BG_APP = "#0A1024"
BG_CARD = "#111A38"
BG_CARD_BORDER = "#222F5C"
BG_INPUT = "#0C1430"
BG_INPUT_BORDER = "#28376B"
BG_CONSOLE = "#080D1F"
BG_CONSOLE_BORDER = "#1B264C"

# Chips / insignias secundarias
CHIP_BG = "#17224A"
CHIP_BORDER = "#2E3F7C"

# Textos
TEXT_MAIN = "#F6F7FA"
TEXT_MUTED = "#95A2C2"
TEXT_DIM = "#56658F"

# Tipografías
FONT_HERO = ("Segoe UI Semibold", 15)
FONT_TITLE = ("Segoe UI Semibold", 11)
FONT_SUB = ("Segoe UI", 9)
FONT_LABEL = ("Segoe UI Semibold", 9)
FONT_BODY = ("Segoe UI", 9)
FONT_MONO = ("Consolas", 9)
FONT_BTN = ("Segoe UI Semibold", 9)
FONT_BADGE = ("Segoe UI", 8, "bold")


# ------------------------------------------------------------------ utilidades
def _rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _mix(c1, c2, t):
    """Mezcla dos colores hex (t=0 → c1, t=1 → c2)."""
    a, b = _rgb(c1), _rgb(c2)
    return "#%02X%02X%02X" % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _pill_image(w, h, radius, fill, border, scale=3, gradient=0.0):
    """Rectángulo redondeado suavizado; gradient>0 aclara la parte superior."""
    sw, sh = w * scale, h * scale
    sr = min(radius * scale, sh // 2, sw // 2)
    mask = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, sw - 1, sh - 1), radius=sr, fill=255)

    if gradient:
        top, bottom = _rgb(_mix(fill, "#FFFFFF", gradient)), _rgb(fill)
        body = Image.new("RGB", (1, sh))
        for y in range(sh):
            t = y / max(1, sh - 1)
            body.putpixel((0, y), tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
        body = body.resize((sw, sh))
    else:
        body = Image.new("RGB", (sw, sh), fill)

    img = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    img.paste(body, (0, 0), mask)
    if border:
        ImageDraw.Draw(img).rounded_rectangle((1, 1, sw - 2, sh - 2), radius=sr, outline=border, width=scale)
    return img.resize((w, h), Image.Resampling.LANCZOS)


def _parent_bg(parent):
    try:
        return parent.cget("bg") or BG_APP
    except tk.TclError:
        return BG_APP


def style_titlebar(win):
    """Barra de título oscura en color Tinta (Windows 11; en Windows 10 queda oscura simple)."""
    try:
        win.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(win.winfo_id())
        dwm = ctypes.windll.dwmapi

        def attr(code, value):
            v = ctypes.c_int(value)
            dwm.DwmSetWindowAttribute(hwnd, code, ctypes.byref(v), ctypes.sizeof(v))

        def colorref(hex_color):
            r, g, b = _rgb(hex_color)
            return r | (g << 8) | (b << 16)

        attr(20, 1)                          # DWMWA_USE_IMMERSIVE_DARK_MODE
        attr(35, colorref(BG_APP))           # DWMWA_CAPTION_COLOR
        attr(36, colorref(TEXT_MAIN))        # DWMWA_TEXT_COLOR
        attr(34, colorref(BG_CARD_BORDER))   # DWMWA_BORDER_COLOR
    except Exception:
        pass


def load_icon_image(name, size):
    """PhotoImage del ícono de la app (iconos/<name>.png) al tamaño pedido."""
    path = ICONS_DIR / f"{name}.png"
    if not path.exists():
        return None
    img = Image.open(path).convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)


def apply_app_icon(root, name):
    """Ícono de ventana y de barra de tareas (en vez de la pluma de Tk / el logo de Python)."""
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(f"TuTienditaIA.{name}")
    except Exception:
        pass
    ico = ICONS_DIR / f"{name}.ico"
    if ico.exists():
        try:
            root.iconbitmap(default=str(ico))   # default= también aplica a los diálogos
        except tk.TclError:
            pass


# ------------------------------------------------------------------ tema ttk
def setup_app_theme(root, app_icon=None):
    """Aplica el tema 'clam' estilizado con los tokens de 'Tu tiendita IA'.

    app_icon: nombre del ícono en ./iconos (omniboost, omniflow, omniscale).
    """
    root.configure(bg=BG_APP)
    if app_icon:
        apply_app_icon(root, app_icon)
    style_titlebar(root)

    style = ttk.Style()
    try:
        style.theme_use('clam')
    except Exception:
        pass

    # Combobox
    style.configure(
        'TCombobox',
        fieldbackground=BG_INPUT,
        background=BG_INPUT,
        foreground=TEXT_MAIN,
        darkcolor=BG_INPUT,
        lightcolor=BG_INPUT,
        bordercolor=BG_INPUT_BORDER,
        arrowcolor=COLOR_PERIWINKLE,
        selectbackground=BG_INPUT,
        selectforeground=TEXT_MAIN,
        arrowsize=13,
        padding=(8, 6)
    )
    style.map(
        'TCombobox',
        fieldbackground=[('readonly', BG_INPUT), ('focus', BG_INPUT)],
        background=[('active', CHIP_BG), ('readonly', BG_INPUT)],
        foreground=[('readonly', TEXT_MAIN)],
        selectbackground=[('readonly', BG_INPUT)],
        selectforeground=[('readonly', TEXT_MAIN)],
        bordercolor=[('focus', COLOR_BIROME_LIGHT), ('hover', '#3A4C8C')],
        arrowcolor=[('hover', COLOR_YEMA), ('focus', COLOR_YEMA)]
    )

    # Menú desplegable del Combobox (Listbox emergente)
    root.option_add('*TCombobox*Listbox.background', BG_CARD)
    root.option_add('*TCombobox*Listbox.foreground', TEXT_MAIN)
    root.option_add('*TCombobox*Listbox.selectBackground', COLOR_BIROME)
    root.option_add('*TCombobox*Listbox.selectForeground', '#FFFFFF')
    root.option_add('*TCombobox*Listbox.font', FONT_BODY)
    root.option_add('*TCombobox*Listbox.relief', 'flat')
    root.option_add('*TCombobox*Listbox.borderWidth', '0')

    # Selección de texto en campos y consola
    for cls in ('Entry', 'Text'):
        root.option_add(f'*{cls}.selectBackground', COLOR_BIROME)
        root.option_add(f'*{cls}.selectForeground', '#FFFFFF')

    # Anillo de foco: al escribir, el contenedor del campo se ilumina en Birome
    def _ring(event, color):
        well = event.widget.master
        try:
            if int(well.cget('highlightthickness')) == 1:
                well.configure(highlightbackground=color)
        except (tk.TclError, AttributeError):
            pass

    root.bind_class('Entry', '<FocusIn>', lambda e: _ring(e, COLOR_BIROME_LIGHT), add='+')
    root.bind_class('Entry', '<FocusOut>', lambda e: _ring(e, BG_INPUT_BORDER), add='+')

    # Progressbar: Yema sobre canal Tinta
    style.configure(
        'Horizontal.TProgressbar',
        troughcolor=BG_INPUT,
        background=COLOR_YEMA,
        lightcolor=COLOR_YEMA,
        darkcolor='#F2B807',
        bordercolor=BG_APP,
        thickness=8
    )

    # Checkbutton
    style.configure(
        'TCheckbutton',
        background=BG_CARD,
        foreground=TEXT_MAIN,
        font=FONT_BODY,
        focuscolor=BG_CARD,
        indicatorbackground=BG_INPUT,
        indicatorforeground=COLOR_CINTA,
        upperbordercolor=BG_INPUT_BORDER,
        lowerbordercolor=BG_INPUT_BORDER,
        indicatormargin=(0, 0, 8, 0)
    )
    style.map(
        'TCheckbutton',
        background=[('active', BG_CARD)],
        foreground=[('active', COLOR_YEMA)],
        indicatorbackground=[('selected', COLOR_YEMA), ('active', CHIP_BG)]
    )

    # Scrollbar fina sin flechas (consola)
    style.layout('Omni.Vertical.TScrollbar', [
        ('Vertical.Scrollbar.trough', {'sticky': 'ns', 'children': [
            ('Vertical.Scrollbar.thumb', {'expand': '1', 'sticky': 'nswe'})
        ]})
    ])
    style.configure(
        'Omni.Vertical.TScrollbar',
        troughcolor=BG_CONSOLE,
        background=CHIP_BORDER,
        bordercolor=BG_CONSOLE,
        lightcolor=CHIP_BORDER,
        darkcolor=CHIP_BORDER,
        gripcount=0,
        width=8
    )
    style.map(
        'Omni.Vertical.TScrollbar',
        background=[('pressed', COLOR_PERIWINKLE), ('active', COLOR_BIROME_LIGHT)],
        lightcolor=[('pressed', COLOR_PERIWINKLE), ('active', COLOR_BIROME_LIGHT)],
        darkcolor=[('pressed', COLOR_PERIWINKLE), ('active', COLOR_BIROME_LIGHT)]
    )


# ------------------------------------------------------------------ componentes
class PillBadge(tk.Canvas):
    """Insignia redondeada (pill badge) estilo Tu tiendita IA."""
    def __init__(self, parent, text='IA', bg_color=COLOR_YEMA, fg_color=COLOR_CINTA, border_color=None,
                 height=22, font=FONT_BADGE, **kwargs):
        f_obj = tkfont.Font(font=font)
        w = f_obj.measure(text) + 18
        super().__init__(parent, width=w, height=height, bg=_parent_bg(parent), highlightthickness=0, **kwargs)

        img = _pill_image(w, height, height // 2, bg_color, border_color or bg_color)
        self.tk_img = ImageTk.PhotoImage(img)
        self.create_image(0, 0, anchor='nw', image=self.tk_img)
        self.create_text(w // 2, height // 2, text=text, fill=fg_color, font=font)


class PillButton(tk.Canvas):
    """Botón redondeado antialiasing con soporte para hover, estado disabled y auto-anchura."""
    def __init__(self, parent, text='', command=None, style='primary',
                 height=36, width=None, radius=None, font=FONT_BTN, **kwargs):
        self.style_type = style
        self.text = text
        self.command = command
        self.btn_height = height
        self.font = font
        self.custom_width = width
        self.radius = radius or (height // 2)
        self.is_hover = False
        self.is_pressed = False
        self.state = 'normal'
        self.tk_img = None

        self._init_colors()
        super().__init__(parent, height=height, bg=_parent_bg(parent), highlightthickness=0, cursor='hand2', **kwargs)

        if width:
            self.configure(width=width)
        else:
            f_obj = tkfont.Font(font=font)
            self.configure(width=f_obj.measure(text) + 40)

        self.bind('<Configure>', self._on_resize)
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_click)

    def _init_colors(self):
        self.gradient = 0.0
        if self.style_type == 'primary':    # Birome Blue
            self.fill_normal = COLOR_BIROME
            self.fill_hover = COLOR_BIROME_HOVER
            self.border = '#3A62DE'
            self.fg = '#FFFFFF'
            self.gradient = 0.16
        elif self.style_type == 'accent':   # Malvón Coral
            self.fill_normal = COLOR_MALVON
            self.fill_hover = COLOR_MALVON_HOVER
            self.border = '#F26077'
            self.fg = '#FFFFFF'
            self.gradient = 0.14
        elif self.style_type == 'yema':     # Yema Gold
            self.fill_normal = COLOR_YEMA
            self.fill_hover = '#FFDD66'
            self.border = '#FFE68F'
            self.fg = COLOR_CINTA
            self.gradient = 0.25
        elif self.style_type == 'danger':   # Danger vino/malvón
            self.fill_normal = '#2A1426'
            self.fill_hover = '#3C1A31'
            self.border = '#6A2540'
            self.fg = '#FF7A90'
        else:                               # Secondary Tinta
            self.fill_normal = CHIP_BG
            self.fill_hover = '#203063'
            self.border = CHIP_BORDER
            self.fg = TEXT_MAIN
            self.gradient = 0.04

    def _on_enter(self, e):
        if self.state == 'normal':
            self.is_hover = True
            self._redraw()

    def _on_leave(self, e):
        if self.state == 'normal':
            self.is_hover = False
            self.is_pressed = False
            self._redraw()

    def _on_press(self, e):
        if self.state == 'normal':
            self.is_pressed = True
            self._redraw()

    def _on_click(self, e):
        was_pressed = self.is_pressed
        self.is_pressed = False
        if self.state == 'normal':
            self._redraw()
            inside = 0 <= e.x <= self.winfo_width() and 0 <= e.y <= self.winfo_height()
            if was_pressed and inside and self.command:
                self.command()

    def configure_state(self, state):
        self.state = state
        self.is_hover = False
        self.is_pressed = False
        self.configure(cursor='hand2' if state == 'normal' else 'arrow')
        self._redraw()

    def configure_text(self, new_text):
        self.text = new_text
        if not self.custom_width:
            f_obj = tkfont.Font(font=self.font)
            self.configure(width=f_obj.measure(new_text) + 40)
        self._redraw()

    def _on_resize(self, event):
        self._redraw(event.width, event.height)

    def _redraw(self, w=None, h=None):
        w = w or self.winfo_width()
        h = h or self.btn_height
        if w < 10 or h < 10:
            return

        if self.state == 'disabled':
            fill, border, fg, grad = '#121B3A', '#1E2A52', '#4A5A85', 0.0
        else:
            fill = self.fill_hover if self.is_hover else self.fill_normal
            if self.is_pressed:
                fill = _mix(fill, '#000000', 0.15)
            border, fg, grad = self.border, self.fg, self.gradient

        img = _pill_image(w, h, self.radius, fill, border, scale=2, gradient=grad)
        self.tk_img = ImageTk.PhotoImage(img)
        self.delete('all')
        self.create_image(0, 0, anchor='nw', image=self.tk_img)
        self.create_text(w // 2, h // 2 + (1 if self.is_pressed else 0), text=self.text, fill=fg, font=self.font)


class RoundedCard(tk.Canvas):
    """Tarjeta con esquinas redondeadas y superficie elevada 'Tu tiendita IA'."""
    def __init__(self, parent, bg_app=BG_APP, card_bg=BG_CARD, border_color=BG_CARD_BORDER,
                 radius=14, pad=16, auto_height=True, bg_color=None, **kwargs):
        if bg_color is not None:
            card_bg = bg_color
        super().__init__(parent, bg=bg_app, highlightthickness=0, **kwargs)
        self.bg_app = bg_app
        self.card_bg = card_bg
        self.border_color = border_color
        self.radius = radius
        self.pad = pad
        self.auto_height = auto_height
        self.tk_img = None
        self._last_w = 0
        self._last_h = 0

        self.body = tk.Frame(self, bg=card_bg)
        self.win_id = self.create_window(pad, pad, window=self.body, anchor='nw')

        self.bind('<Configure>', self._on_resize)
        if self.auto_height:
            self.body.bind('<Configure>', self._on_body_resize)

    def _on_body_resize(self, event=None):
        if not self.auto_height:
            return
        req_h = self.body.winfo_reqheight() + self.pad * 2
        if abs(self.winfo_height() - req_h) > 2:
            self.configure(height=req_h)

    def _on_resize(self, event):
        w, h = event.width, event.height
        if w < 10 or h < 10 or (w == self._last_w and h == self._last_h):
            return
        self._last_w, self._last_h = w, h

        if self.auto_height:
            self.itemconfig(self.win_id, width=w - self.pad * 2)
        else:
            self.itemconfig(self.win_id, width=w - self.pad * 2, height=h - self.pad * 2)

        img = _pill_image(w, h, self.radius, self.card_bg, self.border_color, scale=2)
        # Filete luminoso superior: da sensación de superficie elevada
        hl = ImageDraw.Draw(img)
        hl.line((self.radius, 1, w - self.radius, 1), fill=_mix(self.border_color, '#FFFFFF', 0.12), width=1)

        self.tk_img = ImageTk.PhotoImage(img)
        self.delete('card_bg')
        self.create_image(0, 0, anchor='nw', image=self.tk_img, tags='card_bg')
        self.tag_lower('card_bg')


class SegmentedSwitch(tk.Frame):
    """Selector de pestañas segmentado tipo pill control moderno."""
    def __init__(self, parent, options, on_change=None, **kwargs):
        super().__init__(parent, bg=BG_INPUT, padx=3, pady=3,
                         highlightbackground=BG_CARD_BORDER, highlightthickness=1, **kwargs)
        self.options = options
        self.on_change = on_change
        self.selected_idx = 0
        self.buttons = []

        for idx, opt in enumerate(options):
            lbl = tk.Label(self, text=opt, font=FONT_BTN, cursor='hand2', padx=16, pady=6)
            lbl.bind('<Button-1>', lambda e, i=idx: self.select(i))
            lbl.bind('<Enter>', lambda e, i=idx: self._hover(i, True))
            lbl.bind('<Leave>', lambda e, i=idx: self._hover(i, False))
            lbl.pack(side='left', padx=1)
            self.buttons.append(lbl)

        self._update_styles()

    def select(self, idx):
        if self.selected_idx != idx:
            self.selected_idx = idx
            self._update_styles()
            if self.on_change:
                self.on_change(idx)

    def _hover(self, idx, inside):
        if idx != self.selected_idx:
            self.buttons[idx].configure(fg=TEXT_MAIN if inside else TEXT_MUTED,
                                        bg=CHIP_BG if inside else BG_INPUT)

    def _update_styles(self):
        for idx, btn in enumerate(self.buttons):
            if idx == self.selected_idx:
                btn.configure(bg=COLOR_BIROME, fg='#FFFFFF')
            else:
                btn.configure(bg=BG_INPUT, fg=TEXT_MUTED)


class ModernSlider(tk.Canvas):
    """Slider plano con relleno Birome, perilla Yema y valor a la derecha.

    Reemplazo directo de tk.Scale: acepta variable, from_, to y length.
    """
    def __init__(self, parent, variable, from_=0, to=100, length=220, accent=COLOR_YEMA, **kwargs):
        self.var = variable
        self.from_, self.to = from_, to
        self.track_w = length
        self.accent = accent
        self.h = 26
        self.value_w = 34
        self.pad = 9
        self.hover = False
        self.tk_img = None
        bg = _parent_bg(parent)
        self.bg = bg
        super().__init__(parent, width=length + self.value_w, height=self.h, bg=bg,
                         highlightthickness=0, cursor='hand2', **kwargs)

        self.bind('<Button-1>', self._set_from_event)
        self.bind('<B1-Motion>', self._set_from_event)
        self.bind('<MouseWheel>', lambda e: self._nudge(1 if e.delta > 0 else -1))
        self.bind('<Enter>', lambda e: self._set_hover(True))
        self.bind('<Leave>', lambda e: self._set_hover(False))
        self.var.trace_add('write', lambda *a: self._redraw())
        self._redraw()

    def _set_hover(self, value):
        self.hover = value
        self._redraw()

    def _nudge(self, step):
        self.var.set(max(self.from_, min(self.to, round(self.var.get()) + step)))

    def _set_from_event(self, e):
        x0, x1 = self.pad, self.track_w - self.pad
        t = min(1.0, max(0.0, (e.x - x0) / (x1 - x0)))
        self.var.set(round(self.from_ + t * (self.to - self.from_)))

    def _redraw(self):
        try:
            val = float(self.var.get())
        except (tk.TclError, ValueError):
            return
        t = (val - self.from_) / ((self.to - self.from_) or 1)
        t = min(1.0, max(0.0, t))

        s = 3
        w, h = self.track_w, self.h
        img = Image.new('RGBA', (w * s, h * s), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        cy = h * s // 2
        x0, x1 = self.pad * s, (w - self.pad) * s
        th = 3 * s
        d.rounded_rectangle((x0, cy - th, x1, cy + th), radius=th, fill=BG_INPUT_BORDER)
        kx = x0 + (x1 - x0) * t
        if kx - x0 > 1:
            d.rounded_rectangle((x0, cy - th, kx, cy + th), radius=th, fill=COLOR_BIROME_LIGHT)
        kr = (8 if self.hover else 7) * s
        if self.hover:
            halo = 12 * s
            d.ellipse((kx - halo, cy - halo, kx + halo, cy + halo), fill=_rgb(self.accent) + (40,))
        d.ellipse((kx - kr, cy - kr, kx + kr, cy + kr), fill=self.accent, outline=BG_APP, width=2 * s)
        img = img.resize((w, h), Image.Resampling.LANCZOS)

        self.tk_img = ImageTk.PhotoImage(img)
        self.delete('all')
        self.create_image(0, 0, anchor='nw', image=self.tk_img)
        self.create_text(w + self.value_w - 2, h // 2, text=f"{int(round(val))}", anchor='e',
                         fill=TEXT_MAIN if self.hover else TEXT_MUTED, font=FONT_LABEL)


class ConsoleText(tk.Text):
    """Consola de registro con scrollbar fina estilizada (reemplazo de ScrolledText)."""
    def __init__(self, master=None, **kw):
        bg = kw.pop('bg', BG_CONSOLE)
        self.frame = tk.Frame(master, bg=bg)
        self.vbar = ttk.Scrollbar(self.frame, orient='vertical', style='Omni.Vertical.TScrollbar')
        self.vbar.pack(side='right', fill='y', padx=(6, 0))

        kw.setdefault('fg', '#A9B8DA')
        kw.setdefault('relief', 'flat')
        kw.setdefault('borderwidth', 0)
        kw.setdefault('font', FONT_MONO)
        kw.setdefault('insertbackground', TEXT_MAIN)
        kw.setdefault('padx', 4)
        kw.setdefault('pady', 2)
        kw.setdefault('spacing1', 1)
        kw.setdefault('wrap', 'word')
        kw['yscrollcommand'] = self.vbar.set
        super().__init__(self.frame, bg=bg, **kw)
        self.pack(side='left', fill='both', expand=True)
        self.vbar.configure(command=self.yview)

        # Igual que ScrolledText: pack/grid/place actúan sobre el marco contenedor
        text_meths = vars(tk.Text).keys()
        methods = (vars(tk.Pack).keys() | vars(tk.Grid).keys() | vars(tk.Place).keys()) - text_meths
        for m in methods:
            if m[0] != '_' and m not in ('config', 'configure'):
                setattr(self, m, getattr(self.frame, m))

    def write(self, text):
        self.configure(state='normal')
        self.insert(tk.END, str(text))
        self.see(tk.END)
        self.configure(state='disabled')


class BrandStripe(tk.Canvas):
    """Filete de marca: Birome · Malvón · Yema, separa el encabezado del contenido."""
    def __init__(self, parent, height=2, **kwargs):
        super().__init__(parent, height=height, bg=_parent_bg(parent), highlightthickness=0, **kwargs)
        self.bind('<Configure>', self._draw)

    def _draw(self, e):
        self.delete('all')
        w, h = e.width, e.height
        a, b = int(w * 0.62), int(w * 0.86)
        self.create_rectangle(0, 0, a, h, fill=COLOR_BIROME_LIGHT, width=0)
        self.create_rectangle(a, 0, b, h, fill=COLOR_MALVON, width=0)
        self.create_rectangle(b, 0, w, h, fill=COLOR_YEMA, width=0)


def create_header(parent, title, subtitle="", badge_text="IA", rtx_text="RTX P7 ACTIVE", icon=None):
    """Construye un encabezado premium minimalista con ícono de la app e insignias oficiales."""
    h_box = tk.Frame(parent, bg=BG_APP)
    h_box.pack(fill='x', padx=22, pady=(16, 10))

    if icon:
        img = load_icon_image(icon, 52)
        if img:
            ic = tk.Label(h_box, image=img, bg=BG_APP)
            ic.image = img
            ic.pack(side='left', padx=(0, 14))

    # Título + Badge Yema "IA"
    left_f = tk.Frame(h_box, bg=BG_APP)
    left_f.pack(side='left', fill='y')

    top_row = tk.Frame(left_f, bg=BG_APP)
    top_row.pack(anchor='w')

    tk.Label(top_row, text=title, font=FONT_HERO, fg=TEXT_MAIN, bg=BG_APP).pack(side='left', padx=(0, 10))

    if badge_text:
        PillBadge(top_row, text=badge_text, bg_color=COLOR_YEMA, fg_color=COLOR_CINTA).pack(side='left')

    if subtitle:
        tk.Label(left_f, text=subtitle, font=FONT_SUB, fg=TEXT_MUTED, bg=BG_APP).pack(anchor='w', pady=(2, 0))

    # Lado Derecho: Badge de Aceleración de Hardware
    if rtx_text:
        right_f = tk.Frame(h_box, bg=BG_APP)
        right_f.pack(side='right', anchor='n', pady=(4, 0))
        PillBadge(right_f, text="●  " + rtx_text, bg_color=CHIP_BG, fg_color=COLOR_PERIWINKLE,
                  border_color=CHIP_BORDER).pack(side='right')

    BrandStripe(parent).pack(fill='x', padx=22, pady=(0, 10))
    return h_box


def prompt_rename_dialog(root, title, prompt, default_val, subtext=""):
    """Diálogo modal para confirmar o renombrar con estética Tu tiendita IA."""
    res = {"value": None}
    dlg = tk.Toplevel(root)
    dlg.title(title)
    dlg.configure(bg=BG_APP)
    dlg.resizable(False, False)
    dlg.transient(root)

    w, h = 560, 240
    root.update_idletasks()
    x = root.winfo_rootx() + max(0, (root.winfo_width() - w) // 2)
    y = root.winfo_rooty() + max(0, (root.winfo_height() - h) // 2)
    dlg.geometry(f"{w}x{h}+{x}+{y}")
    style_titlebar(dlg)
    dlg.grab_set()

    card = RoundedCard(dlg, radius=12, pad=18)
    card.pack(fill='both', expand=True, padx=14, pady=14)

    tk.Label(card.body, text=prompt, bg=BG_CARD, fg=TEXT_MAIN, font=FONT_TITLE,
             justify="left", wraplength=500).pack(anchor="w", pady=(0, 4))

    if subtext:
        tk.Label(card.body, text=subtext, bg=BG_CARD, fg=TEXT_MUTED, font=FONT_SUB,
                 justify="left", wraplength=500).pack(anchor="w", pady=(0, 10))

    val_var = tk.StringVar(value=default_val)

    in_box = tk.Frame(card.body, bg=BG_INPUT, highlightbackground=BG_INPUT_BORDER, highlightthickness=1)
    in_box.pack(fill="x", pady=(0, 16))
    entry = tk.Entry(in_box, textvariable=val_var, bg=BG_INPUT, fg=TEXT_MAIN, insertbackground=TEXT_MAIN,
                     font=FONT_BODY, relief="flat")
    entry.pack(fill="x", ipady=7, padx=8)
    entry.focus_set()
    entry.select_range(0, tk.END)

    btn_box = tk.Frame(card.body, bg=BG_CARD)
    btn_box.pack(fill="x", side="bottom")

    def on_ok(event=None):
        val = val_var.get().strip()
        if val:
            res["value"] = val
            dlg.destroy()

    def on_cancel(event=None):
        dlg.destroy()

    dlg.bind("<Return>", on_ok)
    dlg.bind("<Escape>", on_cancel)

    PillButton(btn_box, text="Confirmar y Procesar", style="primary", command=on_ok, height=34).pack(side="right", padx=(8, 0))
    PillButton(btn_box, text="Cancelar", style="secondary", command=on_cancel, height=34).pack(side="right")

    root.wait_window(dlg)
    return res["value"]
