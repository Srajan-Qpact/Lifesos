#!/usr/bin/env python3
"""Generate LifeLine iOS app icon + splash from the heart-EKG mark.

iOS specifics:
  - AppIcon: single 1024x1024 PNG, NO alpha, full-bleed square (iOS masks
    the rounded corners itself), gradient + white heart / crimson EKG.
  - Splash: 2732x2732 white field with a centered red-gradient heart /
    white EKG, written to the 1x/2x/3x slots the template expects.
"""
import io, os
import cairosvg
from PIL import Image

ASSETS = "/home/claude/lifeline-android/ios/App/App/Assets.xcassets"
ICONSET = f"{ASSETS}/AppIcon.appiconset"
SPLASHSET = f"{ASSETS}/Splash.imageset"
PREVIEW = "/home/claude/lifeline-android/tools/preview"
os.makedirs(PREVIEW, exist_ok=True)

HEART = "M0,-40 C 22,-78 70,-78 86,-44 C 102,-12 76,26 0,92 C -76,26 -102,-12 -86,-44 C -70,-78 -22,-78 0,-40 Z"
EKG   = "M -78,8 L -28,8 L -14,8 L -2,-26 L 13,44 L 26,-8 L 38,8 L 80,8"

# White heart + crimson EKG (icon over the red gradient)
FG_SVG = f"""<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 220 220'>
 <g transform='translate(110,108)'>
  <path fill='#FFFFFF' d='{HEART}'/>
  <path fill='none' stroke='#C62828' stroke-width='11' stroke-linecap='round' stroke-linejoin='round' d='{EKG}'/>
 </g></svg>"""

# Red gradient heart + white EKG (splash on white, matches the web splash)
SPLASH_SVG = f"""<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 220 220'>
 <defs><linearGradient id='hg' x1='0' y1='0' x2='0' y2='1'>
  <stop offset='0' stop-color='#E53935'/><stop offset='1' stop-color='#C62828'/></linearGradient></defs>
 <g transform='translate(110,108)'>
  <path fill='url(#hg)' d='{HEART}'/>
  <path fill='none' stroke='#FFFFFF' stroke-width='11' stroke-linecap='round' stroke-linejoin='round' d='{EKG}'/>
 </g></svg>"""

GRAD_TOP = (244, 82, 97)   # #F45262 sampled from the approved icon
GRAD_BOT = (210, 44, 59)   # #D32C3B

def render_svg(svg, px):
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=px, output_height=px)
    return Image.open(io.BytesIO(png)).convert("RGBA")

FG_MASTER = render_svg(FG_SVG, 1400)
SP_MASTER = render_svg(SPLASH_SVG, 1400)

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

# --- iOS App Icon: 1024, full-bleed, NO alpha ---
icon = paste_center(gradient_square(1024), FG_MASTER, round(1024 * 0.60)).convert("RGB")
icon.save(f"{ICONSET}/AppIcon-512@2x.png")  # 1024x1024 universal slot

# --- iOS Splash: 2732 white field, centered red heart, no alpha ---
def make_splash(size):
    bg = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    gp = round(size * 0.17)           # tasteful centered mark
    g = SP_MASTER.resize((gp, gp), Image.LANCZOS)
    bg.alpha_composite(g, ((size - gp) // 2, (size - gp) // 2))
    return bg.convert("RGB")

splash = make_splash(2732)
for name in ("splash-2732x2732.png", "splash-2732x2732-1.png", "splash-2732x2732-2.png"):
    splash.save(f"{SPLASHSET}/{name}")

# previews
icon.resize((256, 256), Image.LANCZOS).save(f"{PREVIEW}/ios_icon.png")
make_splash(640).save(f"{PREVIEW}/ios_splash.png")
print("iOS assets generated OK")
print("icon:", Image.open(f'{ICONSET}/AppIcon-512@2x.png').size,
      Image.open(f'{ICONSET}/AppIcon-512@2x.png').mode)
print("splash:", Image.open(f'{SPLASHSET}/splash-2732x2732.png').size,
      Image.open(f'{SPLASHSET}/splash-2732x2732.png').mode)
