"""
Checks for the T0-look 9U rack, run on the CAD models with the real units in place (the Pi unit is loaded
from its STEP files). Usage: python verify_rack_t0.py <Pi unit STEP folder> <STL_for_printing folder>
Writes VERIFICATION_rack.txt in the current folder.
"""
import itertools
import math
import os
import sys
import numpy as np
import cadquery as cq
import trimesh
import rack_t0 as r
import units as un
from estimate_filament import grams

PI_STEP, STL_DIR = sys.argv[1], sys.argv[2]
out, fails = [], 0


def check(name, ok, detail=""):
    global fails
    out.append(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")
    fails += (not ok)


def note(name, detail):
    out.append(f"INFO  {name}  {detail}")


def bb_overlap(a, b):
    A, B = a.val().BoundingBox(), b.val().BoundingBox()
    return not (A.xmax < B.xmin or B.xmax < A.xmin or A.ymax < B.ymin or B.ymax < A.ymin or A.zmax < B.zmin or B.zmax < A.zmin)


def vol_int(a, b):
    if not bb_overlap(a, b):
        return 0.0
    try:
        return sum(s.Volume() for s in a.intersect(b).solids().vals())
    except Exception:
        return 0.0


def inside_any(parts, p):
    v = cq.Vector(*p)
    return [n for n, s in parts.items() if s.val().isInside(v)]


P = r.assembly()
PI = un.pi_unit(PI_STEP)
DOCK67, DISP, UCG = un.dock_parts(), un.display_parts(), un.ucg_parts()
YB = r.module_bottoms()

# ---- 1. parts ----
singles = {"side module 2U base": r.side_module(2, True), "side module 3U": r.side_module(3), "side module 1U top": r.side_module(1),
           "base bar": r.base_bar(*r.BAR_Z[0]), "cap half": r.cap_half(), "handle": r.handle(), "UCG shelf": un.ug.body()}
check("every part is one valid solid", all(len(s.solids().vals()) == 1 and s.val().isValid() for s in singles.values()),
      f"({', '.join(singles)})")

# ---- 2. collisions ----
worst = max(((vol_int(P[a], P[b]), a, b) for a, b in itertools.combinations(P, 2)), key=lambda t: t[0])
check("no collisions between rack parts", worst[0] < 0.01, f"({len(P)} parts, worst {worst[0]:.3f} mm3 {worst[1]}/{worst[2]})")
for label, units in (("Pi unit (real STEP parts), B1 dock with the real B1 (132 x 91 x 62), 7\" screen", {**PI, **DOCK67, **DISP, **UCG}),):
    worst = max(((vol_int(P[a], units[b]), a, b) for a in P for b in units), key=lambda t: t[0])
    check(f"no collisions with the rack: {label}", worst[0] < 0.01, f"(worst {worst[0]:.3f} mm3 {worst[1]}/{worst[2]})")
groups = (PI, DOCK67, DISP, UCG)
worst = max(((vol_int(ga[a], gb[b]), a, b) for ga, gb in itertools.combinations(groups, 2) for a in ga for b in gb),
            key=lambda t: t[0])
check("units clear each other", worst[0] < 0.01, f"(worst {worst[0]:.3f} mm3)")
gw, sh = UCG["UCG-Ultra"], UCG["UCG shelf"]
held = (vol_int(gw, sh) < 0.01 and vol_int(gw.translate((0, -0.1, 0)), sh) > 1      # stands on the floor
        and vol_int(gw.translate((0, 0, -0.3)), sh) > 1                              # stops on the window lip
        and vol_int(gw.translate((0, 0, 1.0)), sh) > 1                               # rear stops 0.6 mm behind it
        and all(vol_int(gw.translate((dx, 0, 0)), sh) > 1 for dx in (0.8, -0.8)))  # rails 0.6 mm each side
check("UCG-Ultra (141.8 x 127.6 x 30) fits its tray and is held: floor, window lip, side rails, rear stops", held,
      "(0.6 mm clearance round it)")

# ---- 3. the Pi unit sits on the base bars, with its slots on the rail inserts ----
bars = {n: P[n] for n in P if n.startswith("bar_")}
touch = sum(vol_int(PI["Pi shelf"].translate((0, -0.2, 0)), b) for b in bars.values())
gap0 = sum(vol_int(PI["Pi shelf"], b) for b in bars.values())
check("Pi shelf rests on the front and middle base bars (no gap, no overlap)", gap0 < 0.01 and touch > 1, f"({touch:.0f} mm3 overlap if 0.2 mm lower)")
fp = PI["Pi faceplate"]
fpb = fp.val().BoundingBox()
slots_ok = all(not fp.val().isInside(cq.Vector(sx * r.HOLE_X, y, (fpb.zmin + fpb.zmax) / 2))
               and fp.val().isInside(cq.Vector(sx * r.HOLE_X, y + 3.6, (fpb.zmin + fpb.zmax) / 2))
               for sx in (1, -1) for y in (6.35, 82.55))
check("Pi faceplate slots sit on the rail inserts (EIA 6.35 / 82.55)", slots_ok, f"(faceplate bottom at y = {fpb.ymin:.2f})")
# Pi shelf rubber-foot spots: if feet are fitted they hang in the plinth, clear of the bars
shelf = PI["Pi shelf"]
feet_clear = all(vol_int(b, box) < 0.01 for b in bars.values()
                 for box in [cq.Workplane("XY").box(10, 3, 10).translate((fx, -1.5, fz))
                             for fx, fz in ((-92.95, 18.0), (57.15, 18.0), (57.15, 106.7), (-92.95, 106.7))])
check("Pi shelf rubber feet (optional) hang clear of the base bars", feet_clear, "(Ø10 x 3 mm feet at the shelf's four recesses)")
tray_rest = vol_int(PI["Pi UPS tray"].translate((0, -0.1, 0)), shelf) > 0.5 and vol_int(PI["Pi UPS tray"], shelf) < 0.01
check("Pi UPS tray rests on the shelf standoffs, pins in its holes", tray_rest, "(tray floor at the same height as the old feet)")

# ---- 4. screw lines: holes clear through, inserts behind them ----
allp = dict(P)
def clear_line(x, z, ys):
    return all(not inside_any(allp, (x, y, z)) for y in ys)
joint_ok = all(clear_line(sx * r.SCREW_X, z, [yj + 2.5, yj - 1, yj - 5, yj - 9.5])
               for sx in (1, -1) for yj in YB[1:] for z in r.JOINT_Z)
check(f"module joints: {6 * (len(YB) - 1)} screws clear through the upper rib and into an insert below", joint_ok, "(3 per joint per side)")
key_in = all(vol_int(P[f"side_{i}_{r.MODULES[i]}U_{s}"], cq.Workplane("XY").box(13, 2.5, 9).translate((sx * 131, YB[i] - 1.5, kz))) > 1
             for i in range(1, len(YB)) for s, sx in (("R", 1), ("L", -1)) for kz in r.KEY_Z)
check("module joints: keys drop 3 mm into their pockets", key_in, "(2 per joint per side, 0.25 mm clearance)")
H = r.H
cap_ok = all(clear_line(sx * r.SCREW_X, z, [H + 2, H + 6, H + 20, H - 1, H - 5, H - 9.5]) for sx in (1, -1) for z in (r.JOINT_Z[0], r.JOINT_Z[2]))
check("cap: 4 screws down through the corner columns into the top ribs", cap_ok)
y1 = H + r.CAP_H
hand_ok = all(clear_line(sx * r.HANDLE_X, z, [y1 + 2, y1 + 6, y1 - 1, y1 - 5, y1 - 9.5]) for sx in (1, -1) for z in r.FOOT_Z)
check("handles: 4 screws through the foot tabs into inserts in the cap columns", hand_ok)
yw = -r.PLINTH + r.RELIEF
bar_ok = all(clear_line(sx * r.BAR_SCREW_X, (z0 + z1) / 2, [yw + 1, yw + 4, -r.LAP_H - 0.5, -r.LAP_H + 1, -r.LAP_H + 9])
             for sx in (1, -1) for z0, z1 in r.BAR_Z)
check("base bars: 6 screws up through the ledges into inserts in the bar ends", bar_ok)

# ---- 5. rails and the 10-inch standard ----
NU = sum(r.MODULES)
exp = [k * r.U + o for k in range(NU) for o in r.EIA]
rail_ok = all(not inside_any(allp, (sx * r.HOLE_X, y, z)) for y in exp for sx in (1, -1) for z in (5.0, r.D - 5.0))
check(f"{len(exp)} EIA insert holes per post, front and rear, continuous across the joints", rail_ok, f"(first {exp[0]:.2f}, last {exp[-1]:.2f} mm)")
check("10-inch standard: 236.525 mm hole spacing, 224 mm clear between the posts", abs(2 * r.HOLE_X - 236.525) < 1e-6 and 2 * r.X_IN >= 222)
bbs = [s.val().BoundingBox() for s in P.values()]
W = max(b.xmax for b in bbs) - min(b.xmin for b in bbs)
Dp = max(b.zmax for b in bbs) - min(b.zmin for b in bbs)
Ht = max(b.ymax for b in bbs) - min(b.ymin for b in bbs)
check("RackMate T0 footprint: 280 W x 200 D", abs(W - 280) < 0.01 and abs(Dp - 200) < 0.01, f"({W:.0f} x {Dp:.0f} mm, {Ht:.0f} mm tall to the handle tops)")
for nm, yc, slot in (("B1 dock", un.YC_DOCK, un.dk.SLOT_Y), ("7\" screen", un.YC_DISP, un.dk.SLOT_Y),
                     ("UCG-Ultra shelf", un.YC_UCG, un.ug.SLOT_Y)):
    ys = (yc - slot, yc + slot)
    check(f"{nm} ear slots line up with rail inserts", all(min(abs(y - e) for e in exp) < 0.01 for y in ys), f"(y = {ys[0]:.2f}, {ys[1]:.2f})")
w_rail = r.HOLE_X - r.INS_D / 2 - r.X_IN
w_floor = r.POST - r.INS_DEPTH
w_boss = (r.BOSS - r.INS_D) / 2
w_col = 3.0                                     # handle-insert bosses are Ø(INS_D + 6) inside the hollow columns
w_bar = min(r.BAR_SCREW_X - r.INS_D / 2 - (r.LEDGE_X - 0.3), (r.X_IN - 0.3) - r.BAR_SCREW_X - r.INS_D / 2,
            (r.BAR_Z[0][1] - r.BAR_Z[0][0] - r.INS_D) / 2)
check("rail inserts: >= 3 mm wall round them, >= 2 mm floor behind them", w_rail >= 3.0 and w_floor >= 2.0, f"({w_rail:.2f} mm wall, {w_floor:.1f} mm floor)")
check("wall round the other inserts >= 2 mm", min(w_boss, w_col, w_bar) >= 2.0,
      f"(joint bosses {w_boss:.1f}, cap columns {w_col:.1f}, bar ends {w_bar:.1f} mm)")
disp_top = max(s.val().BoundingBox().ymax for s in DISP.values())
ucg_bot, ucg_top = UCG["UCG shelf"].val().BoundingBox().ymin, UCG["UCG shelf"].val().BoundingBox().ymax
check("UCG shelf sits clear above the screen module", disp_top < ucg_bot, f"(screen module top {disp_top:.1f} vs shelf {ucg_bot:.1f})")
gw_top = UCG["UCG-Ultra"].val().BoundingBox().ymax
check("cap sits clear above the top unit", ucg_top < H, f"(UCG shelf top {ucg_top:.1f}, gateway top {gw_top:.1f}, cap {H:.1f}: "
      f"{H - gw_top:.1f} mm of air over the gateway, then the vent grid)")
deep = max(s.val().BoundingBox().zmax for s in {**PI, **DOCK67, **DISP, **UCG}.values())
check("deepest unit leaves room for cables at the back", deep < r.D - 40, f"({deep:.0f} mm of {r.D:.0f})")

# ---- 6. printing ----
def fits(path):
    m = trimesh.load(path, force="mesh")
    pts = m.vertices[:, :2]
    best = min(max(np.ptp(pts @ np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]]).T, axis=0))
               for a in np.radians(np.arange(0, 90, 1)))
    n = m.face_normals
    zc = m.triangles_center[:, 2] - m.bounds[0][2]
    bed = m.area_faces[(n[:, 2] < -0.99) & (zc < 0.05)].sum()
    return best, bed, m.is_watertight
for f in sorted(os.listdir(STL_DIR)):
    if f.startswith("Rack_"):
        best, bed, wt = fits(os.path.join(STL_DIR, f))
        check(f"{f}: watertight, fits a 220 mm bed, flat on the bed", wt and best <= 220 and bed > 50,
              f"(needs {best:.0f} mm, {bed:.0f} mm2 first layer)")

# ---- 7. stability and strength (hand calcs; PETG printed taken as E = 1.2 GPa) ----
g = 9.81
STL_OF = (("side_0", "Rack_SideModule_2U_Base_x2.stl"), ("side_3", "Rack_SideModule_1U_Top_x2.stl"), ("side_", "Rack_SideModule_3U_x4.stl"), ("bar_", "Rack_BaseBar_x3.stl"),
          ("cap_", "Rack_CapHalf_x2.stl"), ("handle_", "Rack_Handle_x2.stl"))
mass = {}        # name: (kg, z and y of its centre)
for nm, s in P.items():
    path = next(f for k, f in STL_OF if nm.startswith(k))
    bb = s.val().BoundingBox()
    mass[nm] = (grams(os.path.join(STL_DIR, path), 3, 0.15) / 1000, (bb.zmin + bb.zmax) / 2, (bb.ymin + bb.ymax) / 2)
rack_kg = sum(m for m, _, _ in mass.values()) + 0.15                 # + screws and inserts
unit = {"Pi unit (Pi 5, UPS with cells, case, shelf)": (1.0, 60.0, 45.0), "B1 dock + B1": (0.17 + 0.29, 45.0, 155.0),
        "screen module + screen": (0.14 + 0.25, 30.0, 289.0), "UCG shelf + UCG-Ultra": (0.09 + 0.52, 65.0, un.YC_UCG - 5)}
items = list(mass.values()) + [(0.15, r.D / 2, 150.0)] + list(unit.values())
M = sum(m for m, _, _ in items)
com_z = sum(m * z for m, z, _ in items) / M
note("mass and centre of mass", f"rack {rack_kg:.2f} kg (assumed units: Pi 1.0, B1 + dock 0.46, screen 0.39, UCG + shelf 0.61 kg), total {M:.2f} kg, "
     f"centre of mass {com_z:.0f} mm behind the rails")
foot = 15.0                                                           # rubber feet, centred on the corner pads
z_rear, z_front = r.D - r.PAD_L / 2, r.PAD_L / 2                      # take the pivot at the foot centres (conservative)
desk = -r.PLINTH
resist_back = M * g * (z_rear - com_z)
resist_fwd = M * g * (com_z - z_front)
for label, F, y in (("a firm 5 N press on the B1 button", 5.0, un.YC_DOCK + 20), ("a 2 N tap on the touch screen", 2.0, un.YC_DISP)):
    push = F * (y - desk)
    check(f"doesn't tip back under {label}", resist_back > 2.0 * push,
          f"(holds {resist_back / 1000:.2f} N.m vs {push / 1000:.2f}; it would take {resist_back / (y - desk):.0f} N there)")
pull = 5.0 * (un.YC_DOCK - desk)
check("doesn't tip forward when you tear off a label (5 N pull)", resist_fwd > 1.2 * pull,
      f"(holds {resist_fwd / 1000:.2f} N.m vs {pull / 1000:.2f}; it would take {resist_fwd / (un.YC_DOCK - desk):.0f} N)")
note("plugging a cable into the gateway's back pushes the top forward",
     f"it takes about {resist_fwd / (un.YC_UCG - desk):.0f} N there to tip it and an RJ45 plug can need up to 20 N, "
     "so steady the rack with your other hand (or plug in before racking the shelf)")
E = 1200.0
# carrying by one handle (worst case): grip as a beam between the legs, two foot screws in tension
span = (r.D - r.LEG_Z0 - r.LEG_L) - (r.LEG_Z0 + r.LEG_L)
Fc = M * g
st = (Fc * span / 4) / (r.HANDLE_T * r.GRIP ** 2 / 6)
check(f"carry the loaded rack ({M:.1f} kg) by ONE handle", st < 8 and Fc / 2 < 300,
      f"({st:.1f} MPa in the grip, {Fc / 2:.0f} N per foot screw; an M5 insert in PLA or PETG holds well over 1 kN)")
# side-wall panels: a firm 20 N thumb press in the middle of a panel (simply supported plate, centre point load)
def plate_w(F, a, b, t, E=2500.0, nu=0.35):
    alpha = 0.0116 + (0.0165 - 0.0116) * min(max(b / a - 1.0, 0.0), 1.0) / 1.0   # Timoshenko, b/a 1 -> 2
    return alpha * F * a ** 2 / (E * t ** 3 / (12 * (1 - nu ** 2)))
pa = sorted(((r.D - 2 * r.POST - r.STIFF_T) / 2, (3 * r.U - 2 * r.RIB - r.STIFF_T) / 2))
w_new = plate_w(20.0, pa[0], pa[1], r.WALL)
w_v70 = plate_w(20.0, 3 * r.U - 8, r.D - 28, 1.6)                     # v7.0: 1.6 mm wall, no stiffening ribs
check("side panels: a 20 N press in the middle of a panel moves it less than in v7.0", w_new < w_v70,
      f"({w_new:.1f} mm vs {w_v70:.1f} mm; {r.WALL} mm wall with 10 mm stiffening ribs taken as panel edges, PLA)")
# 5 kg on the middle of the cap: front and rear bands carry it across the 224 mm span
L = 2 * r.X_IN
I = 2 * r.BAND_T * r.CAP_H ** 3 / 12
F = 50.0
defl, sb = F * L ** 3 / (48 * E * I), (F * L / 4) * (r.CAP_H / 2) / I
check("5 kg on the middle of the cap: sag < 2 mm, stress < 8 MPa", defl < 2 and sb < 8, f"({defl:.2f} mm, {sb:.1f} MPa; bands only, top plate ignored)")
# Pi unit on the base bars: 1 kg in the middle of one bar (worst case)
bw, bh = r.BAR_Z[0][1] - r.BAR_Z[0][0], r.PLINTH - r.RELIEF
Ib = bw * bh ** 3 / 12
Lb = 2 * r.BAR_SCREW_X
defl, sb = 10 * Lb ** 3 / (48 * E * Ib), (10 * Lb / 4) * (bh / 2) / Ib
check("1 kg on the middle of one base bar: sag < 0.5 mm", defl < 0.5, f"({defl:.2f} mm, {sb:.1f} MPa)")

out.append(f"\n{sum(1 for l in out if l.startswith('PASS'))} PASS, {fails} FAIL")
open("VERIFICATION_rack.txt", "w").write("Printable 10-inch 9U mini rack, RackMate T0 look (v7.2: v7.1 + UCG-Ultra 1U) — checks\n"
                                         "Calculations on the 3D models and hand calcs, not a physical test.\n\n" + "\n".join(out) + "\n")
print("\n".join(out))
