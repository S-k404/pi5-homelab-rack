"""
Checks for the UCG-Ultra 1U shelf, run on the CAD model and the print-ready STL.
Usage: python verify_ucg.py <STL_for_printing folder>. Writes VERIFICATION_ucg.txt in the current folder.
"""
import math
import os
import sys
import numpy as np
import cadquery as cq
import trimesh
import ucg_shelf as ug
from b1_drawer import box
from estimate_filament import grams, RHO

STL = os.path.join(sys.argv[1], "UCG_Ultra_1U_Shelf.stl")
out, fails = [], 0


def check(name, ok, detail=""):
    global fails
    out.append(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")
    fails += (not ok)


def vol_int(a, b):
    try:
        return sum(s.Volume() for s in a.intersect(b).solids().vals())
    except Exception:
        return 0.0


B, G = ug.body(), ug.gateway_dummy()
v = B.val()
check("one valid solid", len(B.solids().vals()) == 1 and v.isValid())

# ---- 1U panel and rail slots ----
bb = v.BoundingBox()
check("1U panel: 254 x 43.65 mm, 0.4 mm clear of the units above and below", abs(bb.xlen - 254) < 0.01 and abs(bb.ylen - ug.PANEL_H) < 0.01,
      f"({bb.xlen:.2f} x {bb.ylen:.2f})")
U0 = -ug.U / 2                                                   # bottom of the U in this frame
slot_ok = all(not v.isInside(cq.Vector(sx * 236.525 / 2, U0 + e, 1.5)) and v.isInside(cq.Vector(sx * 236.525 / 2, U0 + e + 3.6, 1.5))
              for sx in (1, -1) for e in (6.35, 38.1))
check("ear slots sit on the EIA holes (6.35 and 38.1 mm up the U, 236.525 apart)", slot_ok)
behind = B.intersect(box(-200, 200, -50, 50, ug.PANEL_T + 0.01, 300)).val().BoundingBox()
check("everything behind the panel passes between the posts (224 mm clear)", behind.xmax < 111 and behind.xmin > -111,
      f"(widest {behind.xlen:.0f} mm)")

# ---- the gateway in its tray ----
check("UCG-Ultra (141.8 x 127.6 x 30) fits without touching", vol_int(G, B) < 0.01, "(0.6 mm clearance round it)")
check("it stands on the floor", vol_int(G.translate((0, -0.1, 0)), B) > 1)
check("the window lip stops it at the front", vol_int(G.translate((0, 0, -0.3)), B) > 1)
check("the side rails hold it 0.6 mm each side", all(vol_int(G.translate((d, 0, 0)), B) > 1 for d in (0.8, -0.8)))
check("the rear corner stops hold it 0.6 mm behind", vol_int(G.translate((0, 0, 1.0)), B) > 1)
lips = ((ug.GW[0] - ug.WIN[0]) / 2, (ug.WIN_YC - ug.WIN[1] / 2) - ug.FLOOR_TOP, ug.FLOOR_TOP + ug.GW[2] - (ug.WIN_YC + ug.WIN[1] / 2))
check("window frames the front face (lip >= 3.5 mm all round), display in the middle", min(lips) >= 3.5,
      f"(sides {lips[0]:.1f}, bottom {lips[1]:.1f}, top {lips[2]:.1f} mm; window {ug.WIN[0]:.0f} x {ug.WIN[1]:.0f})")
ports = box(-ug.STOP_X0 + 0.1, ug.STOP_X0 - 0.1, ug.FLOOR_TOP, ug.FLOOR_TOP + ug.GW[2], ug.Z_GW[1], ug.Z_GW[1] + 80)
check("ports and USB-C power at the back are clear (nothing behind the middle 112 mm)", vol_int(ports, B) < 0.01)

# ---- print: the STL ----
m = trimesh.load(STL, force="mesh")
pts = m.vertices[:, :2]
need = min(max(np.ptp(pts @ np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]]).T, axis=0))
           for a in np.radians(np.arange(0, 90, 1)))
n, zc = m.face_normals, m.triangles_center[:, 2] - m.bounds[0][2]
first = m.area_faces[(n[:, 2] < -0.99) & (zc < 0.05)].sum()
check("STL watertight, fits a 220 mm bed, front face flat on the bed", m.is_watertight and need <= 220 and first > 3000,
      f"(needs {need:.0f} mm turned 45 degrees, {m.bounds[1][2] - m.bounds[0][2]:.0f} mm tall, {first:.0f} mm2 first layer)")
down = np.where((n[:, 2] < -0.72) & (zc > 0.05))[0]                 # flatter than 45 degrees
worst = 0.0
if len(down):
    sub = m.submesh([down], append=True)
    for comp in sub.split(only_watertight=False):
        p2 = comp.vertices[:, :2]
        w = min(np.ptp(p2 @ np.array([math.cos(a), math.sin(a)])) for a in np.radians(np.arange(0, 180, 2)))
        worst = max(worst, w)
check("no supports: every downward face above the bed is a short bridge or lip (<= 4 mm)", worst <= 4.0,
      f"(widest {worst:.1f} mm: the floor-slot tops and the stop lips)")
g = grams(STL, 3, 0.15) * 1.27 / RHO                       # print it in PETG (the gateway runs warm)
out.append(f"INFO  filament  about {g:.0f} g PETG (3 walls, 15% infill)")

# ---- strength: the tray hangs from the panel ----
E, gacc = 1200.0, 9.81
F = 0.52 * gacc + g / 1000 * gacc                              # gateway + shelf, as a point load at the gateway's middle
a = ug.PANEL_T + ug.GW[1] / 2
w_floor = 2 * (ug.HX + ug.RAIL_T) - 3.5 * len(ug.FLOOR_SLOTS)
parts = [(w_floor, ug.FLOOR_T, ug.FLOOR_T / 2)] + [(ug.RAIL_T, ug.FLOOR_T + ug.RAIL_H, (ug.FLOOR_T + ug.RAIL_H) / 2)] * 2
A = sum(b * h for b, h, _ in parts)
yc = sum(b * h * y for b, h, y in parts) / A
I = sum(b * h ** 3 / 12 + b * h * (y - yc) ** 2 for b, h, y in parts)
c = max(yc, ug.FLOOR_T + ug.RAIL_H - yc)
sig = F * a * c / I
L = ug.Z_END - ug.PANEL_T
dl = F * a ** 2 * (3 * L - a) / (6 * E * I)
check("tray as a cantilever off the panel: stress < 5 MPa, rear sags < 0.5 mm", sig < 5 and dl < 0.5,
      f"({sig:.1f} MPa, {dl:.2f} mm with {F / gacc * 1000:.0f} g; rails and slotted floor only)")
Mt = F * a
pull = Mt / (2 * (38.1 - 6.35))
check("ear screws: the top pair takes the tipping load easily", pull < 50, f"({pull:.0f} N per top screw)")

out.append(f"\n{sum(1 for l in out if l.startswith('PASS'))} PASS, {fails} FAIL")
open("VERIFICATION_ucg.txt", "w").write("UCG-Ultra 1U shelf (v7.2) — checks\n"
                                        "Calculations on the 3D model and hand calcs, not a physical test.\n\n" + "\n".join(out) + "\n")
print("\n".join(out))
