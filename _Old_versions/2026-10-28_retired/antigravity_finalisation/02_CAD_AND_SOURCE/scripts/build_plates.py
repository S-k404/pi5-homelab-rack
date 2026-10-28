import os
import shutil
import zipfile
import xml.etree.ElementTree as ET
from xml.sax.saxutils import quoteattr
import numpy as np
import trimesh

BASE = os.path.dirname(os.path.abspath(__file__))
SRC_PRINT = os.path.join(BASE, "PRINT_THIS")
DEST_PRINT = os.path.join(BASE, "antigravity_finalisation", "01_PRINT_READY_PLATES")
CAD_OUT = os.path.join(BASE, "antigravity_finalisation", "02_CAD_AND_SOURCE")

os.makedirs(DEST_PRINT, exist_ok=True)

# Copy all plates from PRINT_THIS
for item in os.listdir(SRC_PRINT):
    s = os.path.join(SRC_PRINT, item)
    d = os.path.join(DEST_PRINT, item)
    if os.path.isdir(s) and not item.startswith("."):
        if os.path.exists(d):
            shutil.rmtree(d)
        shutil.copytree(s, d)
    elif os.path.isfile(s) and not item.startswith("."):
        shutil.copy2(s, d)

print("Base plates copied.")

# ----------------- Update Plate 11 -----------------
P11_DIR = os.path.join(DEST_PRINT, "11_PETG_Pi-board-tray+lid+faceplate")
shutil.copy2(os.path.join(CAD_OUT, "Rack_Faceplate_2U_10in_final.stl"), P11_DIR)
shutil.copy2(os.path.join(CAD_OUT, "UPS_Switch_Extender.stl"), P11_DIR)
shutil.copy2(os.path.join(CAD_OUT, "Rack_Faceplate_Left_final.stl"), P11_DIR)
shutil.copy2(os.path.join(CAD_OUT, "Rack_Faceplate_Right_final.stl"), P11_DIR)

# Write 3MF for Plate 11 with the final faceplate and switch extender
def write_3mf(path, placed_meshes):
    objs, build = [], []
    for i, (name, m) in enumerate(placed_meshes, start=1):
        vs = "".join(f'<vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>' for x, y, z in m.vertices)
        ts = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in m.faces)
        objs.append(f'<object id="{i}" name={quoteattr(name)} type="model"><mesh><vertices>{vs}</vertices><triangles>{ts}</triangles></mesh></object>')
        build.append(f'<item objectid="{i}"/>')
    model = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
             '<metadata name="Title">' + os.path.basename(path)[:-4] + '</metadata>'
             '<resources>' + "".join(objs) + '</resources><build>' + "".join(build) + '</build></model>')
    ct = ('<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", model)

# Load meshes
bt_mesh = trimesh.load(os.path.join(P11_DIR, "Pi5_UPS_v3_board_tray_HDMIexit.stl"))
lid_mesh = trimesh.load(os.path.join(P11_DIR, "Pi5_UPS_v3_lid.stl"))
fp_mesh = trimesh.load(os.path.join(P11_DIR, "Rack_Faceplate_2U_10in_final.stl"))
sw_mesh = trimesh.load(os.path.join(P11_DIR, "UPS_Switch_Extender.stl"))

def place_at(m, x, y):
    b = m.bounds
    dx = x - b[0][0]
    dy = y - b[0][1]
    dz = -b[0][2]
    m_copy = m.copy()
    m_copy.apply_translation([dx, dy, dz])
    return m_copy

# Layout on 256x256 bed:
# Board tray: x=8, y=10
# Lid: x=132, y=10
# Faceplate: x=1, y=140
# Switch Extender: x=8, y=128
p_bt = place_at(bt_mesh, 8, 10)
p_lid = place_at(lid_mesh, 132, 10)
p_fp = place_at(fp_mesh, 1, 140)
p_sw = place_at(sw_mesh, 8, 128)

placed = [
    ("Pi5_UPS_v3_board_tray_HDMIexit", p_bt),
    ("Pi5_UPS_v3_lid", p_lid),
    ("Rack_Faceplate_2U_10in_final", p_fp),
    ("UPS_Switch_Extender", p_sw)
]

mf3_path = os.path.join(P11_DIR, "Plate11_FINAL_hidden-slit_switch.3mf")
write_3mf(mf3_path, placed)
print("Plate 11 3MF written:", mf3_path)

# Update Plate 11 SETTINGS.txt
p11_settings = """11_PETG_Pi-board-tray+lid+faceplate (UPDATED v7.3 Antigravity Final)
======================================================================
Status: print now (brim OFF: faceplate is 254 of 256 mm bed width)
Recommended file to print:
  - Plate11_FINAL_hidden-slit_switch.3mf:
    Contains all 4 parts for the Pi unit:
      1. Board tray (Pi5_UPS_v3_board_tray_HDMIexit.stl)
      2. Lid (Pi5_UPS_v3_lid.stl)
      3. Faceplate with hidden cable slit & switch access (Rack_Faceplate_2U_10in_final.stl)
         - Hidden cable slit: vertical channel on inside face (front stays solid) so the cable
           from UPS OUT to Waveshare board is 100% hidden from the front!
         - Switch access opening: allows direct finger access to the Cuzor UPS switch.
      4. UPS Switch Extender (UPS_Switch_Extender.stl): snaps onto the UPS switch nub to provide
         a front-panel sliding toggle button!

Alternative files preserved for reference:
  - Plate11_WITH-DC-notch.3mf: older version with bottom edge notch for external 12V lead.
  - Plate11.3mf: plain faceplate.

Bed Settings (Bambu P1S):
  - Profile: 0.20mm Standard @BBL P1S
  - Filament: Generic PETG (black / dark grey)
  - Wall loops: 3
  - Sparse infill: 20% gyroid
  - Supports: OFF
  - Plate: Textured PEI, no glue
  - Enclosure: CLOSED
  - Brim: OFF (faceplate is 254 mm on a 256 mm bed)
"""
with open(os.path.join(P11_DIR, "SETTINGS.txt"), "w") as f:
    f.write(p11_settings)

# ----------------- Plate 14: Dedicated Switch Extender -----------------
P14_DIR = os.path.join(DEST_PRINT, "14_PETG_UPS-switch-extender")
os.makedirs(P14_DIR, exist_ok=True)
shutil.copy2(os.path.join(CAD_OUT, "UPS_Switch_Extender.stl"), P14_DIR)
p_sw_solo = place_at(sw_mesh, 120, 120)
mf3_p14 = os.path.join(P14_DIR, "Plate14_PETG_UPS-switch-extender.3mf")
write_3mf(mf3_p14, [("UPS_Switch_Extender", p_sw_solo)])

p14_settings = """14_PETG_UPS-switch-extender
============================
Status: Optional standalone print (also included on Plate 11)
Print time: ~8 minutes (approx 2.5 g PETG)

What it is:
  A custom switch extender lever that clips onto the Cuzor Mini UPS Pro on/off switch nub.
  It passes through the faceplate switch slot to provide an ergonomic front-panel sliding toggle
  with tactile grip ridges.

Settings (Bambu P1S):
  - Profile: 0.20mm Standard @BBL P1S
  - Filament: Generic PETG (or PLA)
  - Walls: 3
  - Infill: 100%
  - Supports: OFF
"""
with open(os.path.join(P14_DIR, "SETTINGS.txt"), "w") as f:
    f.write(p14_settings)

# Also copy the updated Plate 11 and Plate 14 back to root PRINT_THIS for convenience
shutil.copy2(os.path.join(CAD_OUT, "Rack_Faceplate_2U_10in_final.stl"), os.path.join(SRC_PRINT, "11_PETG_Pi-board-tray+lid+faceplate"))
shutil.copy2(os.path.join(CAD_OUT, "UPS_Switch_Extender.stl"), os.path.join(SRC_PRINT, "11_PETG_Pi-board-tray+lid+faceplate"))
shutil.copy2(mf3_path, os.path.join(SRC_PRINT, "11_PETG_Pi-board-tray+lid+faceplate"))
shutil.copy2(os.path.join(P11_DIR, "SETTINGS.txt"), os.path.join(SRC_PRINT, "11_PETG_Pi-board-tray+lid+faceplate"))
if os.path.exists(os.path.join(SRC_PRINT, "14_PETG_UPS-switch-extender")):
    shutil.rmtree(os.path.join(SRC_PRINT, "14_PETG_UPS-switch-extender"))
shutil.copytree(P14_DIR, os.path.join(SRC_PRINT, "14_PETG_UPS-switch-extender"))

print("All plates populated and verified!")
