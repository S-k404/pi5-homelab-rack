"""Contact sheet of the final-build renders. Usage: python make_sheet_final.py <render dir>"""
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
    "05_pi_unit": "Pi unit",
    "06_pi_unit_back_ports": "Pi unit, rear ports",
    "07_pi_unit_exploded": "Pi unit, exploded",
    "08_pi_unit_faceplate_off": "Faceplate off: Poly+ 5, holder, brick cradle",
    "09_pi_unit_holder_open": "Holder lid off: adapter (F) + NVMe",
    "10_b1_dock": "B1 dock v5 with the B1",
    "11_b1_dock_lid_open": "B1 dock: clamshell lid open (paper roll bay)",
    "12_screen_module": "7\" screen module (prints after 4 Nov)",
    "13_ucg_mount": "UCG-Ultra mount (Printables 942972)",
    "14_ucg_mount_back": "UCG-Ultra mount, back",
    "15_pi_power_rear_ups_out_plug": "Rear: right-angle plug in the UPS OUT",
    "16_pi_power_path_cutaway": "Cutaway: UPS OUT lead route",
    "17_rack_wiring_side_open": "Wiring, side panel off",
    "18_rack_wiring_rear": "Wiring, from the back",
}
shots = [k for k in CAP if os.path.exists(os.path.join(REN, k + ".png"))]
cols, cw, ch, pad, cap = 4, 600, 600, 22, 54
rows = (len(shots) + cols - 1) // cols
sheet = Image.new("RGB", (cols * cw + (cols + 1) * pad, 190 + rows * (ch + cap + pad) + pad), (236, 238, 241))
d = ImageDraw.Draw(sheet)
d.text((pad, 30), "Pi 5 Mini Rack: final build (01_PRINT_FILES, ultrareview 28 Oct)", font=f_title, fill=(28, 31, 36))
d.text((pad, 92), "PLA silver: rack, B1 dock, ears, clips, screen module · PETG black: Pi unit, Poly+ 5 tray, adapter (F) holder, DC-notch faceplate, brick cradle, UCG-Ultra mount",
       font=f_sub, fill=(90, 96, 106))
d.text((pad, 128), "Poly+ 5, adapter (F) and UPS jack positions are stand-ins (listings, Waveshare drawing, CAD model), not measured · cables routed as in VERIFICATION_wiring_all-cables · 28 Oct 2026",
       font=f_sub, fill=(90, 96, 106))
for i, k in enumerate(shots):
    im = Image.open(os.path.join(REN, k + ".png")).convert("RGB")
    im.thumbnail((cw, ch), Image.LANCZOS)
    x, y = pad + (i % cols) * (cw + pad), 190 + (i // cols) * (ch + cap + pad)
    sheet.paste(im, (x + (cw - im.width) // 2, y + (ch - im.height) // 2))
    d.text((x + 6, y + ch + 10), CAP[k], font=f_lab, fill=(28, 31, 36))
sheet.save(os.path.join(REN, "FINAL_sheet.png"), optimize=True)
print("sheet:", len(shots), "renders")
