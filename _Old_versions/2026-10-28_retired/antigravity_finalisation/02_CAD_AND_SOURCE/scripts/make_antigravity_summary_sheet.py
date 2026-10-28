"""
Contact sheet of the Antigravity Finalized renders.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

BASE = "~/Downloads/Pi 5 HomeLab 1"
REN = os.path.join(BASE, "antigravity_finalisation", "03_BLENDER_RENDERS")

F = "/System/Library/Fonts/Helvetica.ttc"
f_lab = ImageFont.truetype(F, 28, index=1)
f_title = ImageFont.truetype(F, 48, index=1)
f_sub = ImageFont.truetype(F, 24)

CAP = {
    "01_rack_loaded_front": "Rack, Loaded (Front 3/4)",
    "02_rack_loaded_back": "Rack, Loaded (Rear Cabling)",
    "03_rack_front_straight": "Clean Front (Hidden Cable & Switch)",
    "04_rack_exploded": "Full Rack Exploded View",
    "05_pi_unit_faceplate_switch_cableslit": "Pi Unit (Switch & Slit Detail)",
    "06_pi_unit_exploded": "Pi Unit Exploded",
    "07_pi_unit_lid_off": "Pi Unit (Active Cooler)",
    "08_b1_dock": "NIIMBOT B1 Dock v5",
    "09_screen_module": "7\" Touch Display Module",
    "10_ucg_mount": "UniFi UCG-Ultra 1U Mount",
    "11_pi_unit_switch_detail": "UPS Switch & Hidden Slit Close-up"
}

shots = [k for k in CAP if os.path.exists(os.path.join(REN, k + ".png"))]
cols, cw, ch, pad, cap = 4, 600, 600, 22, 54
rows = (len(shots) + cols - 1) // cols
sheet = Image.new("RGB", (cols * cw + (cols + 1) * pad, 150 + rows * (ch + cap + pad) + pad), (236, 238, 241))
d = ImageDraw.Draw(sheet)
d.text((pad, 30), "Pi 5 HomeLab Mini Rack: Antigravity Finalization", font=f_title, fill=(28, 31, 36))
d.text((pad, 92), "v7.3 Final · Hidden UPS-to-Board Cable Slit · Front-Panel UPS Switch Access · Switch Extender Print · B1 Dock v5 · Active Cooler",
       font=f_sub, fill=(90, 96, 106))

for i, k in enumerate(shots):
    im = Image.open(os.path.join(REN, k + ".png")).convert("RGB")
    im.thumbnail((cw, ch), Image.LANCZOS)
    x, y = pad + (i % cols) * (cw + pad), 150 + (i // cols) * (ch + cap + pad)
    sheet.paste(im, (x + (cw - im.width) // 2, y + (ch - im.height) // 2))
    d.text((x + 6, y + ch + 10), CAP[k], font=f_lab, fill=(28, 31, 36))

out_path = os.path.join(REN, "FINAL_summary_sheet.png")
sheet.save(out_path, optimize=True)
print("Saved summary sheet to:", out_path)

# Also copy to root Renders folder
root_renders = os.path.join(BASE, "Pi 5 Mini Rack Renders")
if os.path.exists(root_renders):
    sheet.save(os.path.join(root_renders, "FINAL_summary_sheet.png"), optimize=True)
