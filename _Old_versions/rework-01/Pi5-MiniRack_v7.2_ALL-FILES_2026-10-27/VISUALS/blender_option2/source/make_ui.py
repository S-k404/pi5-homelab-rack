"""Draw the two images shown on the emissive panels: a home-lab dashboard for the 7" screen and a status line for the
UCG-Ultra's front display. Usage: python make_ui.py <out dir>"""
import math
import os
import sys
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
FONT = "/System/Library/Fonts/Helvetica.ttc"


def font(size, bold=False):
    try:
        return ImageFont.truetype(FONT, size, index=1 if bold else 0)
    except OSError:
        return ImageFont.load_default()


BG, CARD, LINE, TEXT, DIM = (14, 18, 26), (26, 32, 44), (52, 62, 80), (232, 236, 242), (140, 152, 170)
ACC = [(86, 180, 255), (98, 214, 150), (255, 184, 77), (236, 110, 140)]

W, H = 1542, 859                     # 154.2 x 85.9 mm at 10 px/mm
im = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(im)
d.text((40, 26), "pi5 · homelab", font=font(46, True), fill=TEXT)
d.text((W - 40, 36), "Tue 27 Oct  ·  14:32", font=font(32), fill=DIM, anchor="ra")
tiles = [("CPU", "23 %", ACC[0]), ("SoC temp", "48 °C", ACC[1]), ("UPS", "100 %  on mains", ACC[2]), ("NVMe", "41 / 512 GB", ACC[3])]
tw, th, y0 = (W - 40 * 2 - 3 * 24) // 4, 150, 110
for i, (k, v, c) in enumerate(tiles):
    x = 40 + i * (tw + 24)
    d.rounded_rectangle((x, y0, x + tw, y0 + th), 18, fill=CARD)
    d.rectangle((x, y0 + 20, x + 6, y0 + th - 20), fill=c)
    d.text((x + 28, y0 + 22), k, font=font(28), fill=DIM)
    d.text((x + 28, y0 + 66), v, font=font(46 if len(v) < 10 else 34, True), fill=TEXT)
gx0, gy0, gx1, gy1 = 40, 290, W - 40, H - 40
d.rounded_rectangle((gx0, gy0, gx1, gy1), 18, fill=CARD)
d.text((gx0 + 28, gy0 + 20), "Network  ·  2.5G link to the UCG-Ultra", font=font(30), fill=DIM)
for k in range(1, 5):
    y = gy0 + 80 + k * (gy1 - gy0 - 110) / 5
    d.line((gx0 + 28, y, gx1 - 28, y), fill=LINE, width=2)
for series, (amp, ph, base, col) in enumerate([(70, 0.0, 0.55, ACC[0]), (45, 1.7, 0.75, ACC[1])]):
    pts = []
    for i in range(160):
        t = i / 159
        y = base - 0.18 * math.sin(t * 9 + ph) * math.exp(-((t - 0.6) ** 2) * 3) - 0.06 * math.sin(t * 31 + ph)
        pts.append((gx0 + 28 + t * (gx1 - gx0 - 56), gy0 + 80 + y * (gy1 - gy0 - 110)))
    d.line(pts, fill=col, width=5, joint="curve")
d.text((gx1 - 28, gy0 + 20), "up 412 Mb/s   down 1.31 Gb/s", font=font(30, True), fill=TEXT, anchor="ra")
im.save(os.path.join(OUT, "screen_ui.png"))

im = Image.new("RGB", (480, 240), (6, 8, 12))       # 24 x 12 mm
d = ImageDraw.Draw(im)
d.text((240, 52), "UCG-Ultra", font=font(54, True), fill=(235, 240, 248), anchor="mm")
d.text((240, 130), "Internet  OK", font=font(46), fill=(98, 214, 150), anchor="mm")
d.text((240, 196), "12 clients", font=font(40), fill=(150, 160, 175), anchor="mm")
im.save(os.path.join(OUT, "ucg_ui.png"))
print("ui images written")
