"""
Pi unit (Argon Poly+ 5 build) power path: the right-angle DC plug on the UPS OUT, the lead from it to the Waveshare
adapter (F)'s 7-24 V screw terminal in the F holder, the brick's plug in the UPS DC-IN, and the Pi's side ports.
Calculations on the CAD models, not a physical test. Frame = v3 frame (x left -> right, y rack rear (-) -> front (+), z up).
Usage: python verify_pi_power_path.py <v7.2 bundle> <Argon folder> <DC-notch faceplate STEP> <report.txt>
"""
import os
import sys
import cadquery as cq
import argon_tray as A
import waveshare_f_holder as H

BUNDLE, ARGON, FP_STEP, REPORT = sys.argv[1:5]
PI = os.path.join(BUNDLE, "4_Pi_Unit_2U")
ld = lambda p: cq.importers.importStep(p).val()
shelf = ld(os.path.join(PI, "STEP_for_Onshape", "Rack_Shelf_pinned.step"))
upst = ld(os.path.join(PI, "STEP_for_Onshape", "Pi5_UPS_v3_ups_tray_pinned.step"))
tray = ld(os.path.join(ARGON, "STEP_for_Onshape", "Pi5_ArgonPoly5_tray.step"))
hb = ld(os.path.join(ARGON, "STEP_for_Onshape", "Waveshare_F_holder_base.step"))
hl = ld(os.path.join(ARGON, "STEP_for_Onshape", "Waveshare_F_holder_lid.step"))
fp = ld(FP_STEP)
ups = ld(os.path.join(PI, "Component_Models", "Cuzor_MiniUPS_Pro_12V3A.step")).translate(cq.Vector(50.6, 40.6, 1.0))
case_max = A.case_dummy("POLY5", "max").val()
case_nom = A.case_dummy("POLY5", "nominal").val()
lines, fails, warns = [], 0, 0


def rec(st, name, detail=""):
    global fails, warns
    lines.append(f"{st:<5} {name}  {detail}")
    fails += st == "FAIL"
    warns += st == "WARN"


def vol(a, b):
    try:
        return a.intersect(b).Volume()
    except Exception:
        return 0.0


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane().box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0)).val()


def tube(pts, d):
    r = d / 2
    s = cq.Workplane().sphere(r).translate(pts[0]).val()
    for a, b in zip(pts, pts[1:]):
        va, vb = cq.Vector(*a), cq.Vector(*b)
        L = (vb - va).Length
        if L < 1e-6:
            continue
        cyl = cq.Solid.makeCylinder(r, L, va, (vb - va).normalized())
        s = s.fuse(cyl).fuse(cq.Workplane().sphere(r).translate(b).val())
    return s.clean()


lines.append("Pi unit power path (Argon Poly+ 5 build): checks, 28 Oct 2026")
lines.append("Calculations on the CAD models, not a physical test. v3 frame: x left->right, y rack rear(-)->front(+), z up.")
lines.append("")

# ---------------------------------------------------------------- 1. the UPS itself
lines.append("== The UPS (Cuzor Mini UPS Pro 12 V 3 A) ==")
ub = ups.BoundingBox()
rec("INFO", "size used", f"{ub.xlen:.0f} x {ub.ylen:.0f} x {ub.zlen:.0f} (Cuzor's page: 10 x 8 x 2.8 cm). The tray takes up to "
    "101 x 81 x 28.5. One marketplace listing says 10.2 x 8 x 2.4: if yours is 102 long it is 1 mm too long, so measure it")
rec("INFO", "switch", "Cuzor's page: a SLIDE switch (0 / 1), not a rocker. Its position isn't published")
# the CAD model's two jacks (6 mm deep, dia 8 recesses)
OUT = (86.6, 0.6, 11.5)      # rear face (y 0.6): the v3 'switch / LED / OUT' face
IN_MODEL = (14.6, 80.6, 11.5)  # front face (y 80.6) in the CAD model
rec("INFO", "jacks in the CAD model", f"one on the rear face at x {OUT[0]}, z {OUT[2]} (taken as OUT) and one on the front face "
    f"at x {IN_MODEL[0]} (DC-IN). Cuzor publish no drawing; the v3 case says the jack positions came from product photos")
in_win = 80.0 + 5.5 <= IN_MODEL[0] <= 112.0 - 5.5
rec("PASS" if in_win else "WARN", "the CAD model's DC-IN lines up with the UPS tray's front window (x 80..112) and the faceplate window",
    f"(model DC-IN at x {IN_MODEL[0]}: {'inside' if in_win else 'OUTSIDE: behind the solid front wall of the UPS tray'}). "
    "The tray and faceplate windows assume DC-IN at the RIGHT end of the front face (x ~86-106). Check where your UPS's IN "
    "jack really is before printing plate 10 / the faceplate")
lines.append("")

# ---------------------------------------------------------------- 2. right-angle plug on the UPS OUT (rear)
lines.append("== Right-angle 5.5 x 2.1 plug in the UPS OUT (rack rear) ==")
BODY_W, BODY_H, BODY_D = 11.0, 12.0, 16.0      # overmould across x, z; depth out of the jack face (generous)
SR_D, SR_L = 6.5, 10.0                          # strain relief, coming out of the elbow sideways
CAB = 4.0                                       # pigtail cable dia (DC leads are 3.5-4.0)
ox, oy, oz = OUT
body = box(ox - BODY_W / 2, ox + BODY_W / 2, oy - BODY_D, oy, oz - BODY_H / 2, oz + BODY_H / 2)
ye = oy - BODY_D + 5.5                          # elbow centre line
sr = cq.Solid.makeCylinder(SR_D / 2, SR_L, cq.Vector(ox + BODY_W / 2, ye, oz), cq.Vector(1, 0, 0))
plug = body.fuse(sr)
win_ok = (58.0 + 3 <= ox - BODY_W / 2) and (ox + BODY_W / 2 <= 110.0 - 3) and (5.0 <= oz - BODY_H / 2) and (oz + BODY_H / 2 <= 25.0)
rec("PASS" if win_ok else "FAIL", f"plug body ({BODY_W:.0f} x {BODY_H:.0f}, {BODY_D:.0f} deep) passes the UPS tray's rear window (x 58..110, z 5..25)",
    f"(body x {ox - BODY_W / 2:.1f}..{ox + BODY_W / 2:.1f}, z {oz - BODY_H / 2:.1f}..{oz + BODY_H / 2:.1f})")
hits = {n: vol(plug, s) for n, s in [("UPS tray", upst), ("shelf (rear stop, HDMI tower)", shelf), ("Poly+ 5 tray", tray),
                                      ("holder base", hb), ("holder lid", hl), ("Poly+ 5 (max size)", case_max)]}
worst = max(hits, key=hits.get)
rec("PASS" if hits[worst] < 0.5 else "FAIL", "plug + strain relief (cable out to the right) touch nothing",
    f"(worst {worst}: {hits[worst]:.1f} mm3; the plug sticks out {BODY_D - 2.8:.0f} mm behind the case's rear face, into the open "
    "rack rear: the rear base bar is ~73 mm further back)")
m_x = min(ox - BODY_W / 2 - 58.0, 110.0 - (ox + BODY_W / 2)); m_z = min(oz - BODY_H / 2 - 5.0, 25.0 - (oz + BODY_H / 2))
rec("PASS" if m_z >= 1.0 else "WARN", "room round the plug body in the window",
    f"({m_x:.1f} mm each side across, {m_z:.1f} mm at the bottom: a 12 mm tall overmould centred on a jack at z {oz} sits "
    f"{m_z:.1f} mm above the window's bottom edge. If your jack is lower, or the plug fatter, file the window's bottom edge)")
lines.append("")

# ---------------------------------------------------------------- 3. lead: OUT -> right channel -> front pocket -> tray lead hole -> holder notch
lines.append("== Lead from the plug to the adapter (F)'s screw terminal (in the F holder) ==")
cx, cy, w, h = A.LEAD_HOLE
TX = sum(H.TERM_X) / 2
TZ = H.PCB_TOP + 5.0                            # terminal wire entries, mid-height of the ~10 mm block
TY_IN = H.PCB_Y0 + 97.0                         # face of the terminal block (entries)
path = [(ox + BODY_W / 2 + SR_L, ye, oz),       # end of strain relief, behind the case
        (104.5, ye + 2.0, oz), (106.3, -3.5, oz),   # turn forward
        (106.3, 4.0, oz),                       # through the rear window's right end, into the right channel
        (106.5, 22.0, 14.0),                    # along the channel (between the UPS and the right wall)
        (102.0, 33.0, 31.6), (102.0, 47.0, 31.6),   # over the UPS's top edge past the joint post (x 107.7, y 40)
        (107.0, 58.0, 16.0), (107.0, 84.0, 14.0),   # back down into the channel
        (107.0, 95.0, 14.0),                    # out through the front window into the pocket under the tray
        (100.0, 101.0, 27.0),                   # up, over the DC-IN plug
        (cx + 2.0, 101.0, 29.0),                # left along the pocket, under the Poly+ 5 tray
        (cx, cy, 33.0), (cx, cy, A.ZS + 4.0),   # up through the tray's lead hole
        (TX, H.OY1 + 4.0, TZ + 3.0),            # over to the holder's front notch
        (TX, H.OY1 + 0.5, TZ), (TX, TY_IN + 1.0, TZ)]   # in through the notch to the terminal entries
L = sum(((cq.Vector(*b) - cq.Vector(*a)).Length for a, b in zip(path, path[1:])))
rec("INFO", "route", "OUT plug (rear) -> right channel x 101.5..113.9 -> front window -> pocket behind the faceplate, under "
    f"the tray -> lead hole ({cx - w / 2:.0f}..{cx + w / 2:.0f}, {cy - h / 2:.0f}..{cy + h / 2:.0f}) -> holder front notch "
    f"(x {H.TERM_X[0]:.0f}..{H.TERM_X[1]:.0f}) -> terminal. Length about {L / 10:.0f} cm from the plug; pigtails are usually 15-30 cm")
for d in (CAB, 5.5):
    cab = tube(path, d)
    hits = {n: vol(cab, s) for n, s in [("UPS", ups), ("UPS tray", upst), ("shelf", shelf), ("Poly+ 5 tray", tray),
                                         ("holder base", hb), ("holder lid (fitted)", hl), ("faceplate", fp),
                                         ("Poly+ 5 (max size)", case_max)]}
    worst = max(hits, key=hits.get)
    rec("PASS" if hits[worst] < 0.5 else ("WARN" if d > CAB else "FAIL"),
        f"a {d:.1f} mm lead along that route touches nothing", f"(worst {worst}: {hits[worst]:.1f} mm3)")
jp = [j for j in A.JOINTS if j[0] > 100][0]
rec("INFO", "pinch in the right channel", f"the M3 joint post at x {jp[0]}, y {jp[1]} (dia 6.5, full height) leaves "
    f"{jp[0] - 3.25 - 101.5:.2f} / {113.9 - jp[0] - 3.25:.2f} mm either side in the 12.4 mm channel, too narrow for a 4 mm lead. "
    "The route lifts the lead over the UPS's top edge there, through the 5.5 mm air gap between the UPS and the tray floor")
# the brick's straight plug in DC-IN (assumed at the window centre, as the tray/faceplate windows intend)
dcin = cq.Solid.makeCylinder(5.5, 125.0 - 80.6, cq.Vector(96.0, 80.6, 17.0), cq.Vector(0, 1, 0))
rec("PASS" if vol(tube(path, CAB), dcin) < 0.5 else "FAIL", "the lead clears the brick's plug in DC-IN (dia 11, assumed at the window centre x 96, z 17)",
    f"({vol(tube(path, CAB), dcin):.1f} mm3)")
hole_ok = w >= 2 * CAB + 1 and h >= CAB + 2
rec("PASS" if hole_ok else "FAIL", f"the tray's lead hole ({w:.0f} x {h:.0f}) takes two {CAB:.0f} mm leads side by side "
    "(one to the terminal, one to a 12 V -> 5 V converter if you also use one)")
rec("INFO", "terminal access", f"the terminal block's wire entries face the front notch (y {TY_IN:.1f}); its screws are on top: "
    "lid off, strip ~7 mm, screw down, lid on. The ~13 mm strip in front of the holder (y 98..112) is also where the "
    "Argon plan puts the 12 V -> 5 V converter, so if you fit both, run this lead over the converter")
lines.append("")

# ---------------------------------------------------------------- 4. the Pi's side ports, with the F holder in place
lines.append("== The Pi's side ports (USB-C power, 2 x micro-HDMI) with the F holder beside the case ==")
SIDE = {"USB-C power": 11.2, "micro-HDMI 0": 25.8, "micro-HDMI 1": 39.2}
BOARD_FRONT = 2.5 + 85.0
for nm, cs in (("nominal 64 mm", case_nom), ("max 66 mm", case_max)):
    left = cs.BoundingBox().xmin
    z0, z1 = A.ZS + 1 + 2.0, A.ZS + 1 + 20.0
    res = []
    for pn, dd in SIDE.items():
        yc = BOARD_FRONT - dd
        zone = box(left - 32.0, left, yc - 6.0, yc + 6.0, z0, z1)
        res.append((pn, yc, vol(zone, hb) + vol(zone, hl)))
    blocked = [r for r in res if r[2] > 1.0]
    gap = left - hb.BoundingBox().xmax
    rec("FAIL" if blocked else "PASS", f"a USB-C / micro-HDMI plug (32 mm with its strain relief) fits into each side port, case {nm}",
        f"(holder is {gap:.1f} mm from the case's side; " + ", ".join(f"{pn} y {yc:.0f}: {v:.0f} mm3 of holder in the way" for pn, yc, v in res) + ")")
rec("INFO", "what this means",
    "The holder puts the adapter (F)'s own USB-C and micro-HDMI plugs in line with the Pi's side ports, ~1.2 mm short of "
    "the case wall. So EITHER the adapter's plugs reach the Pi through the Poly+ 5's side cut-outs (then the Pi is powered "
    "and drives HDMI through the adapter, fed by this UPS OUT -> terminal lead; no step-down converter or UGREEN needed), "
    "OR they don't, and then nothing else can plug into those ports either: the step-down converter's USB-C and the "
    "UGREEN micro-HDMI extender from the Argon plan have no room while the holder is there. Measure the Poly+ 5's side "
    "cut-outs (wall thickness, how far the Pi's USB-C sits behind the outside face) with the adapter in hand before printing "
    "the holder.")
lines.append("")
lines.append(f"{sum(l.startswith('PASS') for l in lines)} PASS, {fails} FAIL, {warns} WARN")
open(REPORT, "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
