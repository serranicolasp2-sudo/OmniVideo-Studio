"""
generar_iconos.py — Íconos de las apps Omni* con la paleta "Tu Tiendita IA".

Dibuja cada ícono a 1024 px y lo reduce con Lanczos para que quede nítido.
Genera, por app: <nombre>.png (1024), <nombre>_256.png y <nombre>.ico multi-tamaño.
También arma vista_previa.png con los tres juntos.

Uso:  python generar_iconos.py
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

OUT = Path(__file__).resolve().parent
S = 1024                      # lienzo de trabajo
M = 44                        # margen del azulejo
R = 236                       # radio de las esquinas
ICO_SIZES = [16, 20, 24, 32, 40, 48, 64, 96, 128, 256]

BIROME = "#1E3C96"
TINTA = "#16205A"
MALVON = "#E0435C"
YEMA = "#FFD23F"
PAPEL = "#F6F7FA"
CELESTE = "#AFC0FF"


def hex_rgb(h, a=255):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


def tile_mask():
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).rounded_rectangle((M, M, S - M, S - M), radius=R, fill=255)
    return m


def diagonal_gradient(c1, c2):
    """Degradé diagonal (arriba-izquierda → abajo-derecha)."""
    a, b = hex_rgb(c1), hex_rgb(c2)
    small = Image.new("RGBA", (256, 256))
    px = small.load()
    for y in range(256):
        for x in range(256):
            t = min(1.0, max(0.0, (x * 0.45 + y * 0.85) / (255 * 1.3)))
            px[x, y] = tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(4))
    return small.resize((S, S), Image.Resampling.BICUBIC)


def radial_glow(cx, cy, radius, color, alpha):
    g = Image.new("L", (S, S), 0)
    ImageDraw.Draw(g).ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=alpha)
    g = g.filter(ImageFilter.GaussianBlur(radius * 0.45))
    layer = Image.new("RGBA", (S, S), hex_rgb(color, 0))
    layer.putalpha(g)
    return layer


def base_tile(c1, c2, glow=None):
    mask = tile_mask()
    tile = diagonal_gradient(c1, c2)
    if glow:
        tile = Image.alpha_composite(tile, radial_glow(*glow))

    # Brillo superior suave
    sheen = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(sheen)
    for y in range(M, S // 2):
        d.line((0, y, S, y), fill=int(46 * (1 - (y - M) / (S // 2 - M)) ** 1.6))
    white = Image.new("RGBA", (S, S), (255, 255, 255, 0))
    white.putalpha(sheen)
    tile = Image.alpha_composite(tile, white)

    # Borde interior luminoso
    ring = Image.new("L", (S, S), 0)
    ImageDraw.Draw(ring).rounded_rectangle((M + 3, M + 3, S - M - 3, S - M - 3), radius=R - 3, outline=60, width=7)
    w2 = Image.new("RGBA", (S, S), (255, 255, 255, 0))
    w2.putalpha(ring)
    tile = Image.alpha_composite(tile, w2)

    tile.putalpha(ImageChops.multiply(tile.getchannel("A"), mask))
    return tile


def with_shadow(glyph, color=(5, 8, 25), alpha=110, offset=18, blur=26):
    """Sombra proyectada debajo del glifo para dar volumen."""
    a = glyph.getchannel("A").point(lambda v: v * alpha // 255)
    sh = Image.new("RGBA", glyph.size, color + (0,))
    sh.putalpha(a)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    out = Image.new("RGBA", glyph.size, (0, 0, 0, 0))
    out.alpha_composite(sh, (0, offset))
    return Image.alpha_composite(out, glyph)


def sparkle(draw, cx, cy, r, fill, pinch=3.2):
    """Destello de 4 puntas con lados cóncavos (tipo astroide)."""
    pts = []
    for i in range(240):
        t = 2 * math.pi * i / 240
        c, s = math.cos(t), math.sin(t)
        x = math.copysign(abs(c) ** pinch, c)
        y = math.copysign(abs(s) ** pinch, s)
        pts.append((cx + r * x, cy + r * y))
    draw.polygon(pts, fill=fill)


def rounded_triangle(draw, pts, fill, rad):
    draw.polygon(pts, fill=fill)
    draw.line(pts + [pts[0]], fill=fill, width=rad, joint="curve")
    for x, y in pts:
        draw.ellipse((x - rad / 2, y - rad / 2, x + rad / 2, y + rad / 2), fill=fill)


# ---------------------------------------------------------------- OmniBoost
def icon_boost():
    tile = base_tile("#3A62DE", TINTA, glow=(700, 300, 330, CELESTE, 90))
    g = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    # Play redondeado
    rounded_triangle(d, [(318, 318), (318, 742), (680, 530)], hex_rgb(PAPEL), 92)
    tile = Image.alpha_composite(tile, with_shadow(g))

    s = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ds = ImageDraw.Draw(s)
    sparkle(ds, 716, 300, 168, hex_rgb(YEMA))
    sparkle(ds, 832, 494, 64, hex_rgb(CELESTE))
    sparkle(ds, 548, 196, 46, hex_rgb(PAPEL, 230))
    return Image.alpha_composite(tile, with_shadow(s, alpha=90, offset=12, blur=18))


# ---------------------------------------------------------------- OmniFlow
def icon_flow(small=False):
    tile = base_tile("#FF7389", "#A51F3A", glow=(300, 260, 300, YEMA, 70))
    g = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    w, h, top = (420, 470, 277) if small else (330, 420, 302)
    x0 = 330 if small else 416
    # Fotogramas fantasma (interpolación)
    for dx, a in ((-220, 70), (-110, 140)):
        d.rounded_rectangle((x0 + dx, top, x0 + dx + w, top + h), radius=64, fill=hex_rgb(PAPEL, a))
    d.rounded_rectangle((x0, top, x0 + w, top + h), radius=64, fill=hex_rgb(PAPEL))
    # Perforaciones de película en el cuadro principal (se omiten en tamaños chicos)
    for i in range(0 if small else 4):
        yy = top + 52 + i * 96
        d.rounded_rectangle((x0 + 26, yy, x0 + 58, yy + 44), radius=10, fill=hex_rgb("#C93450"))
        d.rounded_rectangle((x0 + w - 58, yy, x0 + w - 26, yy + 44), radius=10, fill=hex_rgb("#C93450"))
    font = ImageFont.truetype("C:/Windows/Fonts/seguibl.ttf", 250 if small else 176)
    d.text((x0 + w / 2, top + h / 2 + 4), "60", font=font, fill=hex_rgb(TINTA), anchor="mm")
    # Líneas de velocidad
    if not small:
        for y, ln in ((372, 120), (512, 170), (652, 120)):
            d.rounded_rectangle((96, y - 17, 96 + ln, y + 17), radius=17, fill=hex_rgb(YEMA))
    return Image.alpha_composite(tile, with_shadow(g))


# ---------------------------------------------------------------- OmniScale
def icon_scale():
    tile = base_tile("#FFE68A", "#F0A500", glow=(720, 300, 300, PAPEL, 120))
    g = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    ink = hex_rgb(TINTA)
    lw = 62
    # Esquinas del marco grande (resolución destino)
    a0, a1, arm = 226, 798, 170
    for (x, y, dx, dy) in ((a0, a0, 1, 1), (a1, a0, -1, 1), (a1, a1, -1, -1)):
        d.line([(x + dx * arm, y), (x, y), (x, y + dy * arm)], fill=ink, width=lw, joint="curve")
        for px, py in ((x + dx * arm, y), (x, y + dy * arm), (x, y)):
            d.ellipse((px - lw / 2, py - lw / 2, px + lw / 2, py + lw / 2), fill=ink)
    # Cuadro chico (origen)
    d.rounded_rectangle((196, 538, 486, 828), radius=56, fill=hex_rgb(BIROME))
    d.rounded_rectangle((196, 538, 486, 828), radius=56, outline=ink, width=22)
    # Flecha diagonal de expansión
    d.line([(450, 574), (690, 334)], fill=hex_rgb(MALVON), width=70)
    rounded_triangle(d, [(728, 296), (560, 316), (708, 464)], hex_rgb(MALVON), 40)
    return Image.alpha_composite(tile, with_shadow(g, color=(90, 50, 0), alpha=80, offset=14, blur=22))


def export(name, img, small_img=None):
    """small_img: versión simplificada para 16–24 px, donde el detalle se pierde."""
    img.save(OUT / f"{name}.png")
    img.resize((256, 256), Image.Resampling.LANCZOS).save(OUT / f"{name}_256.png")
    frames = [((small_img if small_img and s <= 24 else img)).resize((s, s), Image.Resampling.LANCZOS) for s in ICO_SIZES]
    frames[-1].save(OUT / f"{name}.ico", sizes=[(s, s) for s in ICO_SIZES], append_images=frames[:-1])
    return img


if __name__ == "__main__":
    flow_small = icon_flow(small=True)
    icons = [export("omniboost", icon_boost()), export("omniflow", icon_flow(), flow_small), export("omniscale", icon_scale())]

    # Vista previa: grande + tamaños chicos sobre fondo oscuro y claro
    prev = Image.new("RGBA", (3 * 300 + 40, 470), hex_rgb("#0A0F24"))
    light = Image.new("RGBA", (prev.width, 90), hex_rgb("#E9ECF3"))
    prev.alpha_composite(light, (0, 380))
    for i, ic in enumerate(icons):
        x = 20 + i * 300
        prev.alpha_composite(ic.resize((256, 256), Image.Resampling.LANCZOS), (x + 22, 20))
        cx = x + 22
        for s in (48, 32, 24, 16):
            src = flow_small if (i == 1 and s <= 24) else ic
            prev.alpha_composite(src.resize((s, s), Image.Resampling.LANCZOS), (cx, 300 + (48 - s)))
            prev.alpha_composite(src.resize((s, s), Image.Resampling.LANCZOS), (cx, 400 + (48 - s) // 2))
            cx += s + 18
    prev.save(OUT / "vista_previa.png")
    print("Íconos generados en", OUT)
