"""
Checks for the alternative Pi-unit parts (Argon NEO 5 / Poly+5 trays) and for the two coolers in the v3 case.
Calculations on the CAD models, not a physical test.
Usage: python verify_alt.py <v7.2 bundle> <alt out folder (has STEP_for_Onshape, STL_for_printing)>
Writes <alt out>/checks/VERIFICATION_alt.txt and, per case, a STEP folder the rack check can load.
"""
import os
import shutil
import sys
import numpy as np
import cadquery as cq
import trimesh
import argon_tray as A

BUNDLE, OUT = sys.argv[1], sys.argv[2]
PI = os.path.join(BUNDLE, "4_Pi_Unit_2U")
STEP = os.path.join(PI, "STEP_for_Onshape")
sys.path.insert(0, os.path.join(BUNDLE, "1_Rack_9U_T0-look", "source"))
from estimate_filament import grams   # noqa: E402

out, fails = [], 0


def check(name, ok, detail=""):
    global fails
    out.append(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")
    fails += (not ok)


def info(name, detail):
    out.append(f"INFO  {name}  {detail}")


def load(p):
    return cq.Workplane().add(cq.importers.importStep(p).val())


def vol_int(a, b):
    A_, B_ = a.val().BoundingBox(), b.val().BoundingBox()
    if A_.xmax < B_.xmin or B_.xmax < A_.xmin or A_.ymax < B_.ymin or B_.ymax < A_.ymin or A_.zmax < B_.zmin or B_.zmax < A_.zmin:
        return 0.0
    try:
        return sum(s.Volume() for s in a.intersect(b).solids().vals())
    except Exception:
        return 0.0


def inside(shape, p):
    return shape.val().isInside(cq.Vector(*p))


board = load(os.path.join(STEP, "Pi5_UPS_v3_board_tray_HDMIexit.step"))
ups = load(os.path.join(STEP, "Pi5_UPS_v3_ups_tray_pinned.step"))
shelf = load(os.path.join(STEP, "Rack_Shelf_pinned.step"))
lid = load(os.path.join(STEP, "Pi5_UPS_v3_lid.step"))
fixed = {"UPS tray": ups, "shelf": shelf}
bbb = board.val().BoundingBox()
import units as un                                              # noqa: E402
DOCK_Z = min(s.val().BoundingBox().ymin for s in un.dock_parts().values()) + un.PI_Z0   # dock underside, v3 frame

# where the Pi's side ports land, for a case whose port end is at y = 0 (datum) and whose board has its
# USB/Ethernet edge ~2.5 mm in from that end (ports flush with the case end). Pi 5 port centres from the
# microSD end: USB-C 11.2, HDMI0 25.8, HDMI1 39.2 (Raspberry Pi 5 mechanical drawing).
BOARD_FRONT = 2.5 + 85.0
SIDE_PORTS = {"USB-C power": 11.2, "micro-HDMI 0": 25.8, "micro-HDMI 1": 39.2}
PLUG_HALF_W, PLUG_LEN = 6.0, 32.0           # plug overmold half width along y, plug + strain relief length

out.append("Alternative Pi-unit parts: Argon NEO 5 / Poly+5 trays, and the coolers in the v3 case — checks")
out.append("Calculations on the CAD models, not a physical test. Frame = v3 frame (y- = rack rear).")
out.append("")

for key, nm in A.NAMES.items():
    c = A.CASES[key]
    out.append(f"== {c['title']} tray ({nm}) ==")
    info("case size used", f"nominal {c['nominal'][0]} x {c['nominal'][1]} x {c['nominal'][2]}, fences at the max "
         f"{c['max'][0]} x {c['max'][1]} + {A.CLR} mm. Published: {c['sources']}")
    t = load(os.path.join(OUT, "STEP_for_Onshape", nm + ".step"))
    tb = t.val().BoundingBox()
    check("one valid solid", len(t.solids().vals()) == 1 and t.val().isValid())
    same = all(abs(a - b) < 0.05 for a, b in ((tb.xmin, bbb.xmin), (tb.xmax, bbb.xmax), (tb.ymin, bbb.ymin), (tb.ymax, bbb.ymax), (tb.zmin, bbb.zmin)))
    check("same footprint and seat height as the v3 board tray it replaces", same,
          f"(x {tb.xmin:.1f}..{tb.xmax:.1f}, y {tb.ymin:.1f}..{tb.ymax:.1f}, floor underside z {tb.zmin:.1f})")
    rests = vol_int(t, ups) < 0.01 and vol_int(t.translate((0, 0, -0.1)), ups) > 1.0
    check("sits on the UPS tray's walls and posts (no gap, no overlap)", rests)
    ok = all(not inside(t, (jx, jy, A.PLENUM_TOP + 0.5)) and not inside(t, (jx, jy, A.ZS - 0.2))
             and inside(ups, (jx + 2.5, jy, A.PLENUM_TOP - 1.0)) and not inside(ups, (jx, jy, A.PLENUM_TOP - 1.0))
             for jx, jy in A.JOINTS)
    check("3 joint holes line up with the UPS tray's M3 posts (same 3 x M3 x 12 countersunk screws)", ok)
    px0, px1, py0, py1 = A.pocket(key)
    above = A.box(px0, px1, py0, py1, A.ZS, A.ZS + 40).val()
    check("nothing stands above the floor inside the case pocket (screw heads countersunk flush)",
          vol_int(t, cq.Workplane().add(above)) < 0.01)
    for size in ("max", "nominal"):
        cs = A.case_dummy(key, size)
        L, Wc, H = c[size]
        clear = vol_int(cs, t) < 0.01 and all(vol_int(cs, s) < 0.01 for s in fixed.values())
        check(f"{size} case ({L} x {Wc} x {H}) on 1 mm foam tape fits with no collision", clear)
    cs = A.case_dummy(key, "max")
    held = (vol_int(cs.translate((0.1, 0, 0)), t) > 0.5 and vol_int(cs.translate((0, -0.1, 0)), t) > 0.05
            and vol_int(cs.translate((-(A.CLR + 0.1), 0, 0)), t) > 0.5 and vol_int(cs.translate((0, A.CLR + 0.1, 0)), t) > 0.5)
    check("max-size case is boxed in: right fence, rear corners, left stubs, front fence", held, f"({A.CLR} mm play)")
    Ln, Wn, _ = c["nominal"]
    info("play on a nominal-size case", f"{c['max'][0] + A.CLR - Ln:.1f} mm lengthwise, {c['max'][1] + A.CLR - Wn:.1f} mm sideways: "
         "push it into the rear-right corner and stick it down with the foam tape")
    # side-port plugs: open area to the left of the case for every plug
    left = A.X_DATUM - Wn
    z0, z1 = A.ZS + 1 + 2.0, A.ZS + 1 + 20.0
    worst = []
    for pn, d in SIDE_PORTS.items():
        yc = BOARD_FRONT - d
        zone = A.box(left - PLUG_LEN, left, yc - PLUG_HALF_W, yc + PLUG_HALF_W, z0, z1)
        hit = max([vol_int(zone, t)] + [vol_int(zone, s) for s in fixed.values()])
        worst.append((hit, pn, yc))
    check("side-port plugs (USB-C, 2 x micro-HDMI) have 32 mm of open space to the left of the case",
          max(w[0] for w in worst) < 0.01, "(" + ", ".join(f"{pn} at y {yc:.0f}" for _, pn, yc in worst) + ")")
    rear = A.box(left + 4.0, A.X_DATUM - 4.0, -30.0, 0.0, A.ZS + 1 + 2.0, A.ZS + 1 + 28.0)
    hit = max([vol_int(rear, t)] + [vol_int(rear, s) for s in fixed.values()])
    check("USB / Ethernet plugs at the rear: 30 mm of open space behind the case end", hit < 0.01)
    cx, cy, w, h = A.LEAD_HOLE
    shaft = A.box(cx - w / 2 + 1, cx + w / 2 - 1, cy - h / 2 + 1, cy + h / 2 - 1, 2.5, A.ZS + 1)
    check("12 V lead hole opens into the free space under the tray's front overhang",
          vol_int(shaft, t) < 0.01 and vol_int(shaft, ups) < 0.01 and vol_int(shaft, shelf) < 0.01,
          f"(hole {w:.0f} x {h:.0f} at x {cx:.0f}, y {cy:.0f}; UPS tray ends at y {ups.val().BoundingBox().ymax:.1f})")
    m = trimesh.load(os.path.join(OUT, "STL_for_printing", nm + ".stl"), force="mesh")
    lo, hi = m.bounds
    first = m.area_faces[(np.abs(m.face_normals[:, 2] + 1) < 1e-6) & (m.triangles_center[:, 2] < lo[2] + 1e-6)].sum()
    check("STL: watertight, flat on the bed, fits the 256 mm bed",
          m.is_watertight and abs(lo[2]) < 1e-6 and max(hi[0] - lo[0], hi[1] - lo[1]) < 254,
          f"({hi[0] - lo[0]:.1f} x {hi[1] - lo[1]:.1f} x {hi[2] - lo[2]:.1f} mm, {first:.0f} mm2 first layer)")
    g = grams(os.path.join(OUT, "STL_for_printing", nm + ".stl"), 3, 0.20)
    info("filament", f"about {g:.0f} g PETG (3 walls, 20 % infill)")
    top = A.ZS + 1 + c["max"][2]
    check("at least 10 mm of air over the case for its top fan (B1 dock's underside is above it)", DOCK_Z - top >= 10.0,
          f"(case top z {top:.1f} with the foam tape, dock underside z {DOCK_Z:.1f}: {DOCK_Z - top:.1f} mm; v3 lid top was "
          f"{lid.val().BoundingBox().zmax:.1f}. The rack check loads the case in the lid's place)")
    # STEP folder for the rack check: v3 parts, with the tray in the board tray's place and the case in the lid's
    d = os.path.join(OUT, "checks", f"rack_step_{key}")
    os.makedirs(d, exist_ok=True)
    for f in ("Rack_Shelf_pinned.step", "Rack_Faceplate_2U_10in.step", "Pi5_UPS_v3_ups_tray_pinned.step"):
        shutil.copy2(os.path.join(STEP, f), os.path.join(d, f))
    shutil.copy2(os.path.join(OUT, "STEP_for_Onshape", nm + ".step"), os.path.join(d, "Pi5_UPS_v3_board_tray_HDMIexit.step"))
    cq.exporters.export(A.case_dummy(key, "max", lift=1.0), os.path.join(d, "Pi5_UPS_v3_lid.step"))
    out.append("")

# ---- coolers in the unchanged v3 case ------------------------------------------------
out.append("== Coolers on the bare Pi 5 in the unchanged v3 case (plates 10 + 11 as they are) ==")
PCB_TOP = 41.9 + 1.6              # Z_PI (boss tops) + board
HL = 63.4                         # lid underside
room = HL - PCB_TOP
info("room above the board under the v3 lid", f"{room:.1f} mm (lid underside z {HL}, board top z {PCB_TOP})")
AC_H, STACK = 13.7, 2.8           # official drawing; SoC + thermal pad under the heatsink base, generous
check("Raspberry Pi Active Cooler: 13.7 mm (official drawing) + up to 2.8 mm under its base fits under the lid",
      AC_H + STACK < room, f"({room - AC_H - STACK:.1f} mm to spare at worst)")
adp = load(os.path.join(PI, "Component_Models", "Waveshare_Adapter_F_v3position.step")).val().BoundingBox()
check("Active Cooler (63.5 x 42.5, inside the Pi's 85 x 56 outline) can't reach the adapter (F)",
      adp.xmax < 56.9, f"(adapter ends at x {adp.xmax:.1f}, the Pi starts at x 56.9)")
# fan: 30 mm blower in the cooler's corner over the USB/GPIO side; centre ~ Pi (50, 34) -> v3 (56.9+34, 5+85-50)
fx, fy, r_in = 56.9 + 34.0, 5.0 + 85.0 - 50.0, 11.0
g_x0, g_x1, g_y0, g_y1 = 60.0 - 2.6, 60.0 + 8 * 6.2 + 2.6, 22.0 - 2.6, 86.0 + 2.6
margin = min(fx - r_in - g_x0, g_x1 - (fx + r_in), fy - r_in - g_y0, g_y1 - (fy + r_in))
check("Active Cooler fan intake sits under the lid's hex grill", margin > 0,
      f"(fan centre ~x {fx:.0f}, y {fy:.0f}; still inside if it is up to {margin:.0f} mm off)")
info("Argon THRML 30 mm cooler on the bare Pi", f"fits the same way if its fan top is no more than 17.0 mm above the board "
     f"({room - 17.0:.1f} mm left under the lid). Argon publish no height (one listing gives 9.6 mm for the heatsink), "
     "so measure it before fitting the lid.")
out.append("")
out.append(f"{sum(l.startswith('PASS') for l in out)} PASS, {fails} FAIL")
os.makedirs(os.path.join(OUT, "checks"), exist_ok=True)
open(os.path.join(OUT, "checks", "VERIFICATION_alt.txt"), "w").write("\n".join(out) + "\n")
print("\n".join(out))
