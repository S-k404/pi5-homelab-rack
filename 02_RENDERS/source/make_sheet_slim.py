"""Contact sheet of the Slim Cargo Prototype renders."""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

REN = "02_RENDERS/SLIM_CARGO_PROTOTYPE"
F = "/System/Library/Fonts/Helvetica.ttc"
f_lab = ImageFont.truetype(F, 28, index=1)
f_title = ImageFont.truetype(F, 46, index=1)
f_sub = ImageFont.truetype(F, 24)

CAP = {
    "01_slim_cargo_rack_loaded_front": "Slim Cargo 9U: Loaded Isometric (All 4 Units)",
    "02_slim_cargo_rack_loaded_rear": "Slim Cargo 9U: Rear Service & Cable Envelope",
    "03_slim_cargo_rack_side_profile": "Slim Cargo 9U: 140 mm Ultra-Slim Profile",
    "04_slim_cargo_rack_empty_isometric": "Slim Cargo 9U: Empty Frame & Structural Bracing",
}

shots = [k for k in CAP if os.path.exists(os.path.join(REN, k + ".png"))]
cols, cw, ch, pad, cap = 2, 850, 950, 30, 60
rows = (len(shots) + cols - 1) // cols
sheet = Image.new("RGB", (cols * cw + (cols + 1) * pad, 200 + rows * (ch + cap + pad) + pad), (236, 238, 241))
d = ImageDraw.Draw(sheet)

d.text((pad, 30), "Pi 5 Mini Rack: 140 mm Slim Cargo Prototype (9U Portable Homelab)", font=f_title, fill=(28, 31, 36))
d.text((pad, 92), "140 mm ultra-compact depth (-30% volume) · 2.4 mm heavy-duty walls · Flush travel handles (445 mm total height)",
       font=f_sub, fill=(90, 96, 106))
d.text((pad, 130), "Fits standard 20-inch carry-on luggage · All cables routed 100% internally behind EIA-310 rails",
       font=f_sub, fill=(90, 96, 106))

for i, k in enumerate(shots):
    im = Image.open(os.path.join(REN, k + ".png")).convert("RGB")
    im.thumbnail((cw, ch), Image.LANCZOS)
    x = pad + (i % cols) * (cw + pad)
    y = 200 + (i // cols) * (ch + cap + pad)
    sheet.paste(im, (x + (cw - im.width) // 2, y + (ch - im.height) // 2))
    d.text((x + 8, y + ch + 12), CAP[k], font=f_lab, fill=(28, 31, 36))

out_path = os.path.join(REN, "SLIM_CARGO_SHEET.png")
sheet.save(out_path, optimize=True)
print(f"Slim cargo sheet created: {out_path} ({len(shots)} shots)")

