#!/usr/bin/env python3
"""Generate LifeLine Android launcher icons + splash assets from the heart-EKG mark."""
import io, os, math
import cairosvg
from PIL import Image, ImageDraw

RES = "/home/claude/lifeline-android/android/app/src/main/res"
PREVIEW = "/home/claude/lifeline-android/tools/preview"
os.makedirs(PREVIEW, exist_ok=True)

HEART = "M0,-40 C 22,-78 70,-78 86,-44 C 102,-12 76,26 0,92 C -76,26 -102,-12 -86,-44 C -70,-78 -22,-78 0,-40 Z"
EKG   = "M -78,8 L -28,8 L -14,8 L -2,-26 L 13,44 L 26,-8 L 38,8 L 80,8"

# White heart + crimson EKG  (for launcher foreground / icon over red bg)
FG_SVG = f"""<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 220 220'>
 <g transform='translate(110,108)'>
  <path fill='#FFFFFF' d='{HEART}'/>
  <path fill='none' stroke='#C62828' stroke-width='11' stroke-linecap='round' stroke-linejoin='round' d='{EKG}'/>
 </g></svg>"""

# Red gradient heart + white EKG  (for splash on white bg, matches the web splash)
SPLASH_SVG = f"""<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 220 220'>
 <defs><linearGradient id='hg' x1='0' y1='0' x2='0' y2='1'>
  <stop offset='0' stop-color='#E53935'/><stop offset='1' stop-color='#C62828'/></linearGradient></defs>
 <g transform='translate(110,108)'>
  <path fill='url(#hg)' d='{HEART}'/>
  <path fill='none' stroke='#FFFFFF' stroke-width='11' stroke-linecap='round' stroke-linejoin='round' d='{EKG}'/>
 </g></svg>"""

GRAD_TOP = (244, 82, 97)
GRAD_BOT = (210, 44, 59)

def render_svg(svg, px):
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=px, output_height=px)
    return Image.open(io.BytesIO(png)).convert("RGBA")

# render glyphs once at high res, downscale as needed
FG_MASTER = render_svg(FG_SVG, 1200)
SP_MASTER = render_svg(SPLASH_SVG, 1200)

def gradient_square(size):
    img = Image.new("RGB", (size, size))
    px = img.load()
    for y in range(size):
        t = y / max(1, size - 1)
        r = round(GRAD_TOP[0] + (GRAD_BOT[0] - GRAD_TOP[0]) * t)
        g = round(GRAD_TOP[1] + (GRAD_BOT[1] - GRAD_TOP[1]) * t)
        b = round(GRAD_TOP[2] + (GRAD_BOT[2] - GRAD_TOP[2]) * t)
        for x in range(size):
            px[x, y] = (r, g, b)
    return img.convert("RGBA")

def paste_center(bg, glyph_master, glyph_px):
    g = glyph_master.resize((glyph_px, glyph_px), Image.LANCZOS)
    out = bg.copy()
    off = ((bg.width - glyph_px) // 2, (bg.height - glyph_px) // 2)
    out.alpha_composite(g, off)
    return out

def circle_mask(img):
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, img.size[0], img.size[1]), fill=255)
    out = img.copy()
    out.putalpha(mask)
    return out

def save(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)

# --- Launcher icons (square + round) ---
ICON = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
for d, s in ICON.items():
    sq = paste_center(gradient_square(s), FG_MASTER, round(s * 0.60))
    save(sq.convert("RGB"), f"{RES}/mipmap-{d}/ic_launcher.png")
    save(circle_mask(sq), f"{RES}/mipmap-{d}/ic_launcher_round.png")

# --- Adaptive foreground (transparent, glyph sized for the 108dp safe zone) ---
FG = {"mdpi": 108, "hdpi": 162, "xhdpi": 216, "xxhdpi": 324, "xxxhdpi": 432}
for d, s in FG.items():
    canvas = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    fg = paste_center(canvas, FG_MASTER, round(s * 0.45))
    save(fg, f"{RES}/mipmap-{d}/ic_launcher_foreground.png")

# --- Play Store icon (512, full-bleed square) ---
save(paste_center(gradient_square(512), FG_MASTER, round(512 * 0.60)).convert("RGB"),
     f"/home/claude/lifeline-android/playstore-icon-512.png")

# --- Splash (white bg, red heart, port + land per density) ---
SP_PORT = {"mdpi": (320, 480), "hdpi": (480, 800), "xhdpi": (720, 1280),
           "xxhdpi": (960, 1600), "xxxhdpi": (1280, 1920)}
def make_splash(w, h):
    bg = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    gp = round(min(w, h) * 0.30)
    g = SP_MASTER.resize((gp, gp), Image.LANCZOS)
    bg.alpha_composite(g, ((w - gp) // 2, (h - gp) // 2))
    return bg.convert("RGB")

for d, (w, h) in SP_PORT.items():
    save(make_splash(w, h), f"{RES}/drawable-port-{d}/splash.png")
    save(make_splash(h, w), f"{RES}/drawable-land-{d}/splash.png")
save(make_splash(480, 800), f"{RES}/drawable/splash.png")

# previews for visual check
paste_center(gradient_square(256), FG_MASTER, round(256*0.60)).convert("RGB").save(f"{PREVIEW}/icon_square.png")
circle_mask(paste_center(gradient_square(256), FG_MASTER, round(256*0.60))).save(f"{PREVIEW}/icon_round.png")
make_splash(360, 640).save(f"{PREVIEW}/splash.png")
print("Assets generated OK")
