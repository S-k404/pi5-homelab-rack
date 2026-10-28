"""
Checks for the 12 V brick cradle (plate 13) and the Pi faceplate with the 12 V lead notch, with the whole rack and
every unit in place. Calculations on the CAD models, not a physical test.
Usage: python verify_brick.py <v7.2 bundle> <out folder from brick_cradle.py>
Writes <out>/checks/VERIFICATION_brick.txt and <out>/checks/rack_step_DC-notch/ (the Pi STEP set with the notched
faceplate, for verify_rack_t0.py).
"""
import math
import os
import shutil
import sys
import numpy as np
import cadquery as cq
import trimesh
import brick_cradle as B

BUNDLE, OUT = sys.argv[1], sys.argv[2]
RACK_SRC = os.path.join(BUNDLE, "1_Rack_9U_T0-look", "source")
sys.path.insert(0, RACK_SRC)
import rack_t0 as r                      # noqa: E402
import units as un                       # noqa: E402
from estimate_filament import grams      # noqa: E402

PI_STEP = os.path.join(BUNDLE, "4_Pi_Unit_2U", "STEP_for_Onshape")
STL = os.path.join(OUT, "STL_for_printing")
PETG = 1.27 / 1.24                       # estimate_filament.grams() is for PLA
out, fails = [], 0


def check(name, ok, detail=""):
    global fails
    out.append(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")
    fails += (not ok)


def info(name, detail):
    out.append(f"INFO  {name}  {detail}")


def vol_int(a, b):
    A, C = a.val().BoundingBox(), b.val().BoundingBox()
    if A.xmax < C.xmin or C.xmax < A.xmin or A.ymax < C.ymin or C.ymax < A.ymin or A.zmax < C.zmin or C.zmax < A.zmin:
        return 0.0
    try:
        return sum(s.Volume() for s in a.intersect(b).solids().vals())
    except Exception:
        return 0.0


def worst(a, parts):
    return max(((vol_int(a, s), n) for n, s in parts.items()), key=lambda t: t[0])


def wtxt(w):
    return f"worst {w[0]:.3f} mm3 with {w[1]}" if w[0] > 0 else "no overlap with anything"


def tube(points, d):
    """a cable of diameter d along a polyline"""
    s = None
    for p, q in zip(points, points[1:]):
        p, q = cq.Vector(*p), cq.Vector(*q)
        seg = cq.Solid.makeCylinder(d / 2, (q - p).Length, p, q - p)
        s = seg if s is None else s.fuse(seg)
    for p in points[1:-1]:
        s = s.fuse(cq.Solid.makeSphere(d / 2, cq.Vector(*p), angleDegrees1=-90, angleDegrees2=90))
    return cq.Workplane().add(s)


# ---- the rack, the units, the new parts ----
P = r.assembly()
PI = un.pi_unit(PI_STEP)
try:                                     # the 27 Oct dock (67 mm B1 + the 62 mm variant with spacers)
    DOCKS = {**un.dock_parts(), **un.dock_parts(thin=True)}
except TypeError:                        # dock v5 (rework-01): one B1 size, no spacers
    DOCKS = un.dock_parts()
UNITS = {**PI, **DOCKS, **un.display_parts(), **un.ucg_parts()}
cradle = B.brick_cradle()
spacers = {t: B.spacer(t) for t in B.SPACERS}
d = os.path.join(OUT, "checks", "rack_step_DC-notch")
os.makedirs(d, exist_ok=True)
for f in os.listdir(PI_STEP):
    if f.endswith(".step") and f != "Rack_Faceplate_2U_10in.step":
        shutil.copy2(os.path.join(PI_STEP, f), os.path.join(d, f))
shutil.copy2(os.path.join(OUT, "STEP_for_Onshape", "Rack_Faceplate_2U_10in_DC-notch.step"), os.path.join(d, "Rack_Faceplate_2U_10in.step"))
FACE_N = un.pi_unit(d)["Pi faceplate"]
FACE_0 = PI["Pi faceplate"]
EVERYTHING = {**P, **{k: v for k, v in UNITS.items() if k != "Pi faceplate"}, "Pi faceplate (notched)": FACE_N}

out.append("12 V brick cradle (plate 13) + Pi faceplate with the 12 V lead notch: checks")
out.append("Calculations on the 3D models, not a physical test. Rack frame: x across, y up from the base-bar tops, z back from the front rails.")
out.append("")
out.append("== Parts ==")
for nm, s in [("cradle", cradle)] + [(f"{t:.0f} mm spacer", s) for t, s in spacers.items()] + [("notched faceplate", FACE_N)]:
    check(f"{nm}: one valid solid", len(s.solids().vals()) == 1 and s.val().isValid())
check("cradle sizes match the rack it sits on (bars, Pi shelf edge, rear post)",
      (r.BAR_Z[1], r.BAR_Z[2]) == (B.MID_BAR, B.REAR_BAR) and abs(PI["Pi shelf"].val().BoundingBox().xmax - B.SHELF_X1) < 0.05
      and r.X_IN == B.POST_X0, f"(middle bar z {r.BAR_Z[1]}, rear bar z {r.BAR_Z[2]}, shelf edge x {PI['Pi shelf'].val().BoundingBox().xmax:.2f})")

out.append("")
out.append("== Cradle in the rack ==")
w = worst(cradle, EVERYTHING)
check("cradle clears every rack part and every unit", w[0] < 0.01, f"({len(EVERYTHING)} parts: {wtxt(w)})")
for t, s in spacers.items():
    w = worst(s, {**EVERYTHING, "cradle": cradle})
    check(f"{t:.0f} mm spacer hung on the inner wall clears the cradle, rack and units", w[0] < 0.01, f"({wtxt(w)})")
bars = {n: P[n] for n in ("bar_middle", "bar_rear")}
low = cradle.translate((0, -0.2, 0))
check("rests on the middle and rear base bars (no gap, no overlap)",
      all(vol_int(cradle, b) < 0.01 and vol_int(low, b) > 1 for b in bars.values()),
      "(" + ", ".join(f"{vol_int(low, b):.0f} mm3 into the {n[4:]} bar if 0.2 mm lower" for n, b in bars.items()) + ")")
check("can't slide front to back: the floor notches straddle both bars",
      all(vol_int(cradle.translate((0, 0, dz)), P["bar_middle"]) > 1 for dz in (-(B.CLR + 0.1), B.CLR + 0.1)),
      f"({B.CLR} mm play each way)")
side_l = vol_int(cradle.translate((-(B.X0 - B.SHELF_X1) - 0.1, 0, 0)), PI["Pi shelf"])
side_r = vol_int(cradle.translate((B.POST_X0 - B.X1 + 0.1, 0, 0)), P["side_0_2U_R"])
check("boxed in sideways: the Pi shelf on the left, the right rear post on the right", side_l > 0.5 and side_r > 0.5,
      f"({B.X0 - B.SHELF_X1:.2f} and {B.POST_X0 - B.X1:.2f} mm play)")
cb = cradle.val().BoundingBox()
check("stays inside the rack's width and the Pi unit's 2U, behind the faceplate",
      cb.xmax < r.X_IN and cb.ymax < un.YB[1] and cb.zmin > 0, f"(x {cb.xmin:.1f}..{cb.xmax:.1f}, y {cb.ymin:.1f}..{cb.ymax:.1f}, z {cb.zmin:.1f}..{cb.zmax:.1f})")
info("rear lip", f"the lip behind the rear bar ends {cb.zmax - r.D:.1f} mm behind the rack's back face (the front faceplates stand 4 mm proud)")
gap = r.X_WALL - B.X1
info("air round the brick", f"{B.X0 - PI['Pi UPS tray'].val().BoundingBox().xmax:.1f} mm from the cradle to the UPS tray wall, "
     f"open above, behind and below (floor vents over the open plinth), faceplate vents in front")

out.append("")
out.append("== Bricks it takes (L x H x T: length, height standing on edge, thickness across the rack) ==")
BRICKS = [("Robu 'Standard 12V 5A 60W' (the one in your cart, listed 110 x 50 x 30)", 110.0, 50.0, 30.0),
          ("Mean Well GST60A12-P1J (the BOM's example)", 125.0, 50.0, 31.5),
          ("generic 12 V 5 A desktop brick (Pro Elec PSU50004 size)", 110.0, 50.0, 33.0),
          ("Ideal Power 15DYS865 size", 120.0, 53.0, 32.0),
          ("CUI SDI65-12 size (thickest common)", 115.0, 53.0, 38.0),
          ("thinnest it holds well", 120.0, 48.0, 29.0),
          ("largest it takes", 140.0, 60.0, B.XI1 - B.XI0 - 0.3)]
dock_bot = min(s.val().BoundingBox().ymin for s in un.dock_parts().values())
lead = None
for nm, L, H, T in BRICKS:
    t = B.spacer_for(T)
    br = B.brick_dummy(L, H, T, t)
    fixed = {**EVERYTHING, "cradle": cradle}
    if t:
        fixed["spacer"] = spacers[t]
    w = worst(br, fixed)
    play = (B.XI1 - B.XI0 - t) - T
    held = (vol_int(br.translate((0.1, 0, 0)), cradle) > 0.05 and vol_int(br.translate((0, 0, 0.1)), cradle) > 0.05
            and vol_int(br.translate((-(play + 0.1), 0, 0)), spacers[t] if t else cradle) > 0.05
            and vol_int(br.translate((0, -0.1, 0)), cradle) > 0.05)
    sp = f"{t:.0f} mm spacer" if t else "no spacer"
    check(f"{nm}, {L:.0f} x {H:.0f} x {T:.1f}: fits with {"the " + sp if t else sp}, held by the floor, walls and kerb",
          w[0] < 0.01 and held, f"({play:.1f} mm side play for the straps to take up; {dock_bot - (B.FT + H):.0f} mm of air over it)")
    bb = br.val().BoundingBox()
    xc, yc = (bb.xmin + bb.xmax) / 2, (bb.ymin + bb.ymax) / 2
    plug = B.box(xc - 16.75, xc + 16.75, yc - 12.0, yc + 12.0, bb.zmax, bb.zmax + 50.0)       # IEC C13 plug + strain relief
    w = worst(plug, fixed)
    check("   its mains plug (C13, 33.5 x 24 x 50) goes straight out of the open rear end, over the kerb", w[0] < 0.01, f"({wtxt(w)})")
    if lead is None:
        lead = (xc, yc, bb.zmin)

out.append("")
out.append("== 12 V lead to the UPS DC-IN ==")
xc, yc, zf = lead
nx = B.NOTCH_X
path = [(xc, yc, zf), (xc, 4.4, 80.0), (nx, 4.4, 18.0), (nx, 4.4, 14.0), (nx, 3.4, 4.0), (nx, 3.4, -2.0)]
cable = tube(path, 5.5)
w = worst(cable, EVERYTHING)
check("a 5.5 mm lead runs from the brick's front, along the cradle, over the front base bar and out through the notch",
      w[0] < 0.01, f"({wtxt(w)}; checked on the Robu brick)")
check("   ... and the plate 11 faceplate without the notch would block it (so the notch is what lets it out)",
      vol_int(cable, FACE_0) > 1, f"({vol_int(cable, FACE_0):.0f} mm3 into the plain faceplate)")
win_x1 = (112.0 - 56.95) + 2.0                                           # DC-IN window right edge (pi_rack.py: x 80..112 + 2 mm)
info("outside the faceplate", f"the lead turns left: {nx - B.NOTCH_W / 2 - win_x1:.0f} mm from the notch to the DC-IN window's right edge, "
     "then the plug goes into the window as before")
fb0, fbn = FACE_0.val().BoundingBox(), FACE_N.val().BoundingBox()
same_box = all(abs(a - c) < 1e-3 for a, c in ((fb0.xmin, fbn.xmin), (fb0.xmax, fbn.xmax), (fb0.ymin, fbn.ymin), (fb0.ymax, fbn.ymax), (fb0.zmin, fbn.zmin), (fb0.zmax, fbn.zmax)))
removed = FACE_0.val().Volume() - FACE_N.val().Volume()
slab = B.box(nx - B.NOTCH_W / 2, nx + B.NOTCH_W / 2, 0.0, B.NOTCH_H, fb0.zmin, fb0.zmax)
nominal = (B.NOTCH_W * (B.NOTCH_H - B.NOTCH_W / 2) + math.pi * (B.NOTCH_W / 2) ** 2 / 2) * (fb0.zmax - fb0.zmin)
check("notched faceplate = the plate 11 faceplate minus the notch, nothing else", same_box and abs(removed - nominal) < 3.0,
      f"(same outline; {removed:.0f} mm3 removed, notch alone {nominal:.0f} mm3: it runs into no other hole)")
lowest_vent = 18.0 - 1.5                                                  # pi_rack.py: side vents at y 18 + 8k, 3 mm tall
check("notch is clear of the vents, screw holes and rail slots", B.NOTCH_H + 3 <= lowest_vent and nx - B.NOTCH_W / 2 > win_x1 + 5,
      f"(notch x {nx - B.NOTCH_W / 2:.0f}..{nx + B.NOTCH_W / 2:.0f}, up to y {B.NOTCH_H:.0f}; lowest vent slot from y {lowest_vent:.1f}; "
      f"rail slot at x {r.HOLE_X:.1f})")

out.append("")
out.append("== Printing (PETG, 0.20 mm, 3 walls, 20 % gyroid, no supports) ==")
total = 0.0
for f in ("Brick_Cradle_12V.stl", "Brick_Spacer_2mm.stl", "Brick_Spacer_4mm.stl", "Brick_Spacer_6mm.stl", "Brick_Spacer_8mm.stl",
          "Rack_Faceplate_2U_10in_DC-notch.stl"):
    m = trimesh.load(os.path.join(STL, f), force="mesh")
    lo, hi = m.bounds
    n = m.face_normals
    zc = m.triangles_center[:, 2]
    first = m.area_faces[(n[:, 2] < -0.999) & (zc < lo[2] + 1e-4)].sum()
    down = (n[:, 2] < -0.71) & (zc > lo[2] + 1e-3)                         # faces that need holding up: > 45 deg overhang
    spans = []
    if down.any():
        sub = m.submesh([np.where(down)[0]], append=True)
        for part in sub.split(only_watertight=False):
            e = part.bounds[1] - part.bounds[0]
            spans.append(min(e[0], e[1]))
    ok = m.is_watertight and abs(lo[2]) < 1e-6 and max(hi[0] - lo[0], hi[1] - lo[1]) <= 254.0 and first > 50 and all(s <= 15.0 for s in spans)
    g = grams(os.path.join(STL, f), 3, 0.20) * PETG
    if "Faceplate" not in f:
        total += g
    check(f"{f}: watertight, flat on the bed, fits, no unsupported overhang", ok,
          f"({hi[0] - lo[0]:.1f} x {hi[1] - lo[1]:.1f} x {hi[2] - lo[2]:.1f} mm, {first:.0f} mm2 first layer, "
          f"{len(spans)} bridge(s) up to {max(spans) if spans else 0:.1f} mm, about {g:.0f} g)")
info("filament", f"plate 13 (cradle + 4 spacers) about {total:.0f} g PETG")

out.append("")
out.append("== Stability (same hand calc and assumed weights as verify_rack_t0.py) ==")
RSTL = os.path.join(BUNDLE, "1_Rack_9U_T0-look", "STL_for_printing")
STL_OF = (("side_0", "Rack_SideModule_2U_Base_x2.stl"), ("side_3", "Rack_SideModule_1U_Top_x2.stl"), ("side_", "Rack_SideModule_3U_x4.stl"),
          ("bar_", "Rack_BaseBar_x3.stl"), ("cap_", "Rack_CapHalf_x2.stl"), ("handle_", "Rack_Handle_x2.stl"))
items = []
for nm, s in P.items():
    path = next(f for k, f in STL_OF if nm.startswith(k))
    bb = s.val().BoundingBox()
    items.append((grams(os.path.join(RSTL, path), 3, 0.15) / 1000, (bb.zmin + bb.zmax) / 2))
items += [(0.15, r.D / 2), (1.0, 60.0), (0.46, 45.0), (0.39, 30.0), (0.61, 65.0)]
BRICK_KG = 0.25                                                            # Robu's brick (190 g) + part of its leads
bb = B.brick_dummy(110.0, 50.0, 30.0, 8.0).val().BoundingBox()
add = [(BRICK_KG, (bb.zmin + bb.zmax) / 2), (total / 1000, (cb.zmin + cb.zmax) / 2)]
g_ = 9.81
desk = -r.PLINTH
z_front, z_rear = r.PAD_L / 2, r.D - r.PAD_L / 2


def tip(its):
    M = sum(m for m, _ in its)
    cz = sum(m * z for m, z in its) / M
    return M, cz, M * g_ * (cz - z_front) / (un.YC_UCG - desk), M * g_ * (z_rear - cz) / (un.YC_DOCK + 20 - desk)


M0, c0, f0, b0 = tip(items)
M1, c1, f1, b1 = tip(items + add)
info("with the brick in its cradle", f"total {M0:.2f} -> {M1:.2f} kg, centre of mass {c0:.0f} -> {c1:.0f} mm behind the rails")
check("the brick low at the back makes the rack harder to tip forward from the gateway", f1 > f0,
      f"(push on the back of the UCG-Ultra to tip it: {f0:.1f} -> {f1:.1f} N. Still well under an RJ45's 20 N, so the "
      "desk fixing / plug-in-first advice stands)")
check("and it still doesn't tip back under a firm 5 N press on the B1 button", b1 > 2 * 5.0,
      f"(it would take {b0:.0f} -> {b1:.0f} N at the button)")

out.append("")
out.append(f"{sum(1 for l in out if l.startswith('PASS'))} PASS, {fails} FAIL")
os.makedirs(os.path.join(OUT, "checks"), exist_ok=True)
open(os.path.join(OUT, "checks", "VERIFICATION_brick.txt"), "w").write("\n".join(out) + "\n")
print("\n".join(out))
