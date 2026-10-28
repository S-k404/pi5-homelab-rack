"""Contact sheet of the option-2 renders. Usage: python make_sheet_opt2.py <render dir>"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

REN = sys.argv[1]
F = "/System/Library/Fonts/Helvetica.ttc"
f_lab, f_title, f_sub = ImageFont.truetype(F, 30, index=1), ImageFont.truetype(F, 50, index=1), ImageFont.truetype(F, 26)
CAP = {
    "01_rack_loaded_front": "Rack, loaded",
    "02_rack_loaded_back": "Rack, from the back",
    "03_rack_front_straight": "Straight on",
    "04_rack_exploded": "Exploded",
    "06_pi_unit": "Pi unit",
    "07_pi_unit_back_ports": "Pi unit, rear ports",
    "08_pi_unit_exploded": "Pi unit, exploded",
    "15_pi_unit_lid_off_active_cooler": "Pi unit, lid off: official Active Cooler",
    "09_b1_dock": "B1 dock v5 with the real B1",
    "14_b1_dock_lid_open": "B1 lid swung open in the rack",
    "10_screen_module": "7\" screen module",
    "12_ucg_mount_option2": "UCG-Ultra mount (Printables 942972)",
    "13_ucg_mount_option2_back": "UCG-Ultra mount, back",
}
shots = [k for k in CAP if os.path.exists(os.path.join(REN, k + ".png"))]
cols, cw, ch, pad, cap = 4, 600, 600, 22, 54
rows = (len(shots) + cols - 1) // cols
sheet = Image.new("RGB", (cols * cw + (cols + 1) * pad, 150 + rows * (ch + cap + pad) + pad), (236, 238, 241))
d = ImageDraw.Draw(sheet)
d.text((pad, 30), "Pi 5 Mini Rack: option 2", font=f_title, fill=(28, 31, 36))
d.text((pad, 92), "B1 dock v5 (real B1 132 x 91 x 62) · official Active Cooler · ready-made UCG-Ultra mount (Printables 942972) · 27 Oct 2026",
       font=f_sub, fill=(90, 96, 106))
for i, k in enumerate(shots):
    im = Image.open(os.path.join(REN, k + ".png")).convert("RGB")
    im.thumbnail((cw, ch), Image.LANCZOS)
    x, y = pad + (i % cols) * (cw + pad), 150 + (i // cols) * (ch + cap + pad)
    sheet.paste(im, (x + (cw - im.width) // 2, y + (ch - im.height) // 2))
    d.text((x + 6, y + ch + 10), CAP[k], font=f_lab, fill=(28, 31, 36))
sheet.save(os.path.join(REN, "option2_sheet.png"), optimize=True)
print("sheet:", len(shots), "renders")
