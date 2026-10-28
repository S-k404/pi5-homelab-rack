"""Labelled sheet of every printed part from the Blender renders, plus web-size JPEGs for the gallery page.
Usage: python make_sheet.py <scene dir> <render dir> <web dir>"""
import json
import os
import sys
from PIL import Image, ImageDraw, ImageFont

SCENE, REN, WEB = sys.argv[1:4]
os.makedirs(os.path.join(WEB, "parts"), exist_ok=True)
data = json.load(open(os.path.join(SCENE, "scene.json")))
F = "/System/Library/Fonts/Helvetica.ttc"
f_lab, f_sub, f_title = ImageFont.truetype(F, 30, index=1), ImageFont.truetype(F, 24), ImageFont.truetype(F, 52, index=1)

cols, cell, pad, cap = 5, 560, 24, 96
parts = data["parts"]
rows = (len(parts) + cols - 1) // cols
sheet = Image.new("RGB", (cols * cell + (cols + 1) * pad, 130 + rows * (cell + cap + pad) + pad), (236, 238, 241))
d = ImageDraw.Draw(sheet)
d.text((pad, 40), "Pi 5 Mini Rack v7.2 — every printed part (Blender, Cycles)", font=f_title, fill=(28, 31, 36))
for i, p in enumerate(parts):
    im = Image.open(os.path.join(REN, "parts", f"{p['key']}.png")).convert("RGB")
    x, y = pad + (i % cols) * (cell + pad), 130 + (i // cols) * (cell + cap + pad)
    sheet.paste(im.resize((cell, cell), Image.LANCZOS), (x, y))
    d.text((x + 6, y + cell + 10), p["label"], font=f_lab, fill=(28, 31, 36))
    sub = f"{p['file']}  ·  print {p['qty']}  ·  ≈{p['grams']} g"
    size = 24
    while size > 14 and d.textlength(sub, font=ImageFont.truetype(F, size)) > cell - 12:
        size -= 1                              # long file names shrink to fit their cell
    d.text((x + 6, y + cell + 50), sub, font=ImageFont.truetype(F, size), fill=(90, 96, 106))
    im.resize((640, 640), Image.LANCZOS).save(os.path.join(WEB, "parts", f"{p['key']}.jpg"), quality=84, optimize=True)
sheet.save(os.path.join(REN, "all_parts_sheet.png"), optimize=True)

for f in sorted(os.listdir(REN)):
    if f.endswith(".png") and f[:2].isdigit():
        im = Image.open(os.path.join(REN, f)).convert("RGB")
        im.thumbnail((1400, 1400), Image.LANCZOS)
        im.save(os.path.join(WEB, f.replace(".png", ".jpg")), quality=85, optimize=True)
print("sheet + web images written")
