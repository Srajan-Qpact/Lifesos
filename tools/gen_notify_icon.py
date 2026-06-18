#!/usr/bin/env python3
"""White heart silhouette for the Android status-bar notification icon.
Status-bar icons are tinted by the system, so they must be pure white on transparent."""
import io, os, cairosvg
from PIL import Image

RES = "/home/claude/lifeline-android/android/app/src/main/res"
HEART = "M0,-40 C 22,-78 70,-78 86,-44 C 102,-12 76,26 0,92 C -76,26 -102,-12 -86,-44 C -70,-78 -22,-78 0,-40 Z"
SVG = f"""<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 220 220'>
 <g transform='translate(110,104)'><path fill='#FFFFFF' d='{HEART}'/></g></svg>"""

master = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=SVG.encode(),
                    output_width=400, output_height=400))).convert("RGBA")

# density -> status bar icon size in px (24dp base)
sizes = {"drawable-mdpi": 24, "drawable-hdpi": 36, "drawable-xhdpi": 48,
         "drawable-xxhdpi": 72, "drawable-xxxhdpi": 96}
for folder, px in sizes.items():
    d = f"{RES}/{folder}"
    os.makedirs(d, exist_ok=True)
    canvas = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    g = round(px * 0.86)
    glyph = master.resize((g, g), Image.LANCZOS)
    canvas.alpha_composite(glyph, ((px - g) // 2, (px - g) // 2))
    canvas.save(f"{d}/ic_stat_notify.png")
    print("wrote", folder, px)
print("done")
