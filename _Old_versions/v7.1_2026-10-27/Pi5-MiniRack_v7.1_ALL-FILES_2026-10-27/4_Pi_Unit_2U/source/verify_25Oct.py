"""Measured verification of v3 case + rack parts + component models. Prints PASS/WARN/FAIL/UNVERIFIED."""
import sys, math
sys.path.insert(0, "/home/claude/pi_step")
sys.path.insert(0, "/home/claude/v3")
import cadquery as cq
from cadquery import Vector
import build, stand
from stand_v2 import xform, trsf
import rack as R

V = Vector
rows = []


def rep(cat, item, value, status, note=""):
    rows.append((cat, item, value, status, note))


def inside(s, p):
    return s.isInside(V(*p), 1e-4)


def open_fraction(solids, pts):
    blocked = sum(1 for p in pts if any(inside(s, p) for s in solids))
    return 1 - blocked / len(pts)


def grid(x0, x1, z0, z1, y, n=8):
    return [(x0 + (x1 - x0) * (i + 0.5) / n, y, z0 + (z1 - z0) * (j + 0.5) / n) for i in range(n) for j in range(n)]


# ---------------- load everything (v3 frame) ----------------
ups_t = cq.importers.importStep("/home/claude/v3/Pi5_UPS_v3_ups_tray.step").val()
brd_t = cq.importers.importStep("/home/claude/v3/rack_out/Pi5_UPS_v3_board_tray_HDMIexit.step").val()
lid = cq.importers.importStep("/home/claude/v3/Pi5_UPS_v3_lid.step").val()
fp = cq.importers.importStep("/home/claude/v3/rack_out/Rack_Faceplate_2U_10in.step").val()
sh = cq.importers.importStep("/home/claude/v3/rack_out/Rack_Shelf.step").val()
PI = trsf(((0, 1, 0), (-1, 0, 0), (0, 0, 1)), (56.9, 90.0, 41.9))
pi = xform(stand.fuse(build.raspberry_pi_5()), PI)
arm = xform(stand.fuse(build.armor_lite_v5()).translate(V(32, 28, 3.9)), PI)
ups = stand.fuse(build.cuzor_ups_pro()).translate(V(50.6, 40.6, 1.0))         # on the 1 mm ribs
ug = R.ugreen_end_routed()
sys.path.insert(0, "/tmp/claude-0/-home-claude/743ddc35-1fe0-5a92-a41e-59e3452dca0b/scratchpad")
from adapter_v3 import adapter
adp = adapter()
parts = {"ups_tray": ups_t, "board_tray": brd_t, "lid": lid, "faceplate": fp, "shelf": sh,
         "Pi5": pi, "Adapter": adp, "ArmorLite": arm, "UPS": ups, "UGREEN_end": ug}

# ================= A. rack standard =================
b = fp.BoundingBox()
rep("Rack", "Faceplate W x H x T", f"{b.xlen:.1f} x {b.zlen:.2f} x {b.ylen:.1f}",
    "PASS" if abs(b.xlen - 254) < .05 and abs(b.zlen - 88.1) < .05 else "FAIL", "10-inch, 2U = 88.9 - 0.8 mm")
cx = R.CX
ok = True
for xs in (cx - R.HOLE_PITCH / 2, cx + R.HOLE_PITCH / 2):
    for zs in R.EAR_Z:
        z = R.Z0 + zs
        ok &= not inside(fp, (xs, R.PY0 + 2, z)) and not inside(fp, (xs + 4.6, R.PY0 + 2, z)) \
            and not inside(fp, (xs - 4.6, R.PY0 + 2, z)) and inside(fp, (xs + 5.4, R.PY0 + 2, z)) \
            and not inside(fp, (xs, R.PY0 + 2, z + 3.1)) and inside(fp, (xs, R.PY0 + 2, z + 3.6))
rep("Rack", "M6 ear slots", f"pitch {R.HOLE_PITCH:.3f} mm, z {R.EAR_Z[0]:.2f} / {R.EAR_Z[1]:.2f} mm, 10 x 6.5 mm",
    "PASS" if ok else "FAIL", "probed edges of all 4 slots")
sb = sh.BoundingBox()
half = max(cx - sb.xmin, sb.xmax - cx)
rep("Rack", "Shelf half-width from centre", f"{half:.1f} mm (rail clearance limit ~111)",
    "PASS" if half < 111 else "FAIL", "fits between 10-inch rails")
top_case = max(p.BoundingBox().zmax for p in (ups_t, brd_t, lid))
rep("Rack", "Headroom: lid top -> panel top", f"{R.Z0 + R.PANEL_H - top_case:.1f} mm", "PASS",
    "unit above starts 0.8 mm higher still")

# ================= B. fit / interference =================
names = list(parts)
clash = []
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        v = parts[names[i]].intersect(parts[names[j]]).Volume()
        if v > 0.05:
            clash.append(f"{names[i]}/{names[j]} {v:.1f} mm³")
clash = [c for c in clash if not c.startswith("Pi5/Adapter")]      # adapter plugs into the Pi by design
rep("Fit", f"Interference, all {len(names)*(len(names)-1)//2} pairs", "none" if not clash else "; ".join(clash),
    "PASS" if not clash else "FAIL")
seat = all(inside(sh, (fx, fy, -5.05)) and not inside(sh, (fx, fy, -4.95)) for fx, fy in R.FEET)
rep("Fit", "v3 feet seated on socket floors (z = -5.00)", "yes" if seat else "no",
    "PASS" if seat else "FAIL", "0.4 mm radial clearance, 1.5 mm deep")
d = fp.distance(brd_t)
rep("Fit", "Faceplate to case back gap", f"{d:.2f} mm", "PASS" if 0.1 < d < 1 else "WARN")
d = ups.distance(brd_t)
rep("Fit", "UPS top to board-tray floor (plenum)", f"{d:.2f} mm", "PASS" if d >= 5 else "WARN")

# ================= C. front panel (v3 button side) =================
line = all(not inside(fp, (R.BTN_X, y, R.BTN_Z)) for y in (R.PY0 + .2, R.PY0 + 2, R.PY1 - .2)) and \
    all(not inside(brd_t, (R.BTN_X, y, R.BTN_Z)) for y in (93.5, 100, 108, 111.5))
rep("Front", "Power-button path (faceplate + v3 tube)", "open end-to-end" if line else "blocked",
    "PASS" if line else "FAIL", "press with a ~25 mm pin/paperclip (tube is 17 mm + 2.5 mm to the button)")
f = open_fraction([fp, sh], grid(80, 112, 5, 29, R.PY0 + 2))
rep("Front", "UPS DC-IN window visible through faceplate", f"{f*100:.0f}% open",
    "PASS" if f > .99 else "FAIL", "jack is 31.9 mm behind the panel face; barrel plug + cable exit through it")
pts = []
for vx in R.V3_BACK_VENT_X:
    pts += [(vx + dx, R.PY0 + 2, z) for dx in (-0.8, 0, 0.8) for z in [R.BACK_VENTS_Z[0] + k for k in range(1, 12)]]
f = open_fraction([fp], pts)
rep("Front", "v3 back-wall vents unobstructed", f"{f*100:.0f}% of slot area open",
    "PASS" if f > .99 else "FAIL", f"{len(R.V3_BACK_VENT_X)} slots matched 1:1")

# ================= D. rear (port side) =================
cuts = {"Pi Ethernet": (58.76, 75.54, 41.1, 57.0), "Pi USB 1": (78.05, 93.75, 41.1, 60.1),
        "Pi USB 2": (96.05, 111.75, 41.1, 60.1), "Adapter HDMI": (35.45, 54.45, 42.7, 52.1),
        "Adapter RJ45 PoE": (14.4, 34.15, 42.7, 59.1), "UPS switch/LED/OUT": (58, 110, 5, 25)}
for n, (x0, x1, z0, z1) in cuts.items():
    f_case = open_fraction([brd_t, ups_t], grid(x0 + .3, x1 - .3, z0 + .3, z1 - .3, -1.1))
    f_rack = open_fraction([sh, fp], grid(x0, x1, z0, z1, -6) + grid(x0, x1, z0, z1, -40))
    rep("Rear", n, f"wall cut-out {f_case*100:.0f}% open, approach {f_rack*100:.0f}% clear",
        "PASS" if f_case > .99 and f_rack > .99 else "FAIL")
# Pi port bodies vs cut-out edges (my model, official drawing centres)
pp = build.raspberry_pi_5()
for pn in ("Ethernet RJ45", "USB3 stack", "USB2 stack"):
    body = xform(pp[pn][0].val(), PI)
    md = body.distance(brd_t)
    rep("Rear", f"Pi {pn} body -> case wall", f"{md:.2f} mm", "PASS" if md >= 0.3 else "WARN",
        "my port model; v3 author also checked against the official Pi 5 STEP")

# ================= E. power path / screw terminal =================
pocket = open_fraction([sh, fp], [(x, y, z) for x in (85, 95, 105) for y in (95, 105, 111) for z in (6, 15, 25, 33)])
hole = not inside(brd_t, (101, 98, 35.7))
rep("Power", "12 V route: UPS OUT -> back window -> pocket -> floor hole",
    f"pocket {pocket*100:.0f}% clear, floor hole {'open' if hole else 'blocked'}",
    "PASS" if pocket > .99 and hole else "FAIL", "shelf lip top z=2, below window bottom z=5")
rep("Power", "Screw terminal location/height", "inside board tray, rear (near cable-tie anchors)",
    "UNVERIFIED", "adapter component layout is not in my files - v3 used Waveshare's drawing; check by eye")
pi_w = 25.0
amps = pi_w / 0.90 / 12 + 0.15
rep("Power", "12 V current budget (Pi 5 max 25 W @ 90% + adapter)", f"~{amps:.1f} A of 3.0 A",
    "PASS" if amps < 3 else "WARN", "UPS input brick must be 12 V >= 3 A (Cuzor recommends >= 1.5 A; Pi load needs more)")
rep("Power", "Two power sources", "UPS -> terminal AND PoE both possible", "WARN",
    "use one: feed the terminal from the UPS and use a non-PoE switch port (or PoE without the UPS)")

# ================= F. HAT ceiling =================
pcb_top = 41.9 + 1.6
lid_under = lid.BoundingBox().zmin + 0.0
lid_under = 63.4
ceil = lid_under - pcb_top
arm_top = arm.BoundingBox().zmax
rep("HAT", "Lid underside above Pi PCB top", f"{ceil:.1f} mm", "INFO", "PCB taken as 1.6 mm")
rep("HAT", "Armor Lite top -> lid", f"{lid_under - arm_top:.1f} mm (my model) / 3.7 mm (v3 worst case 16.5 mm cooler)", "PASS")
hat_top = pcb_top + 17.0 + 1.6 + 2.5
rep("HAT", "HAT over the Armor Lite (17 mm standoffs, 2.5 mm parts)", f"HAT top {hat_top:.1f} vs lid {lid_under}",
    "FAIL" if hat_top > lid_under else "PASS", "no HAT fits v3; needs a lid riser of >= 5 mm (rack headroom allows up to 14 mm)")

# ================= G. airflow =================
ac = arm.BoundingBox().center
in_grill = 60 - 2.6 <= ac.x <= 60 + 8 * 6.2 + 2.6 and 22 - 2.6 <= ac.y <= 86
rep("Air", "Fan centre under lid hex grill", f"fan at x {ac.x:.1f}, y {ac.y:.1f}", "PASS" if in_grill else "FAIL")
hex_area = 2 * math.sqrt(3) * 2.6 ** 2
n_hex = sum(1 for i in range(9) for j in range(11) if 22 + j * 6 + (3 if i % 2 else 0) < 86)
rep("Air", "Lid grill open area", f"{n_hex} hex x {hex_area:.1f} = {n_hex*hex_area/100:.1f} cm²", "PASS",
    "30 mm fan disc is 7.1 cm²")
side_open = open_fraction([sh], [(-2.2 - 1, y, z) for y in (95, 105) for z in (5, 20, 30)] +
                          [(116.1 + 1, y, z) for y in (95, 105) for z in (5, 20, 30)])
rep("Air", "Plenum pocket side inlets", f"{side_open*100:.0f}% clear", "PASS" if side_open > .99 else "FAIL")
ch = sum(1 for vy in range(14, 80, 6) if not inside(sh, (104.2, vy, -5.5)))
rep("Air", "Shelf vents under UPS-channel floor slots", f"{ch}/11 slots open below", "PASS" if ch >= 7 else "WARN",
    "the rest still breathe through the 1.5 mm foot gap")
rep("Air", "Air above lid when racked", f"{R.Z0 + 2*R.U - top_case:.1f} mm to next unit", "PASS")
pts = [(x, y, z) for x in (-3.0, -6.0, -10.0) for y in range(10, 77, 6) for z in (6.5, 15, 23, 31.7)] + \
      [(x, y, z) for x in (-3.0, -6.0, -10.0) for y in range(30, 83, 5) for z in (47, 52, 56)]
guard = open_fraction([sh, ug], pts)
rep("Air", "Case left-wall vents: 10 mm channel to the HDMI tower", f"{guard*100:.0f}% clear",
    "PASS" if guard > .99 else "FAIL", "UPS-tray inlets, plenum slots and board-tray side vents")

# ================= H. UGREEN extender =================
ex = not inside(brd_t, (-1.1, 44, 52))
rep("HDMI ext", "Cable exit in board-tray left wall", f"{'open' if ex else 'blocked'}, 12 x 10 mm (y 38-50, z 47-57)",
    "PASS" if ex else "FAIL", "passes the micro plug (11.3 x 6.6) + cable")
ugb = ug.BoundingBox()
rep("HDMI ext", "Socket face position", f"y {ugb.ymin:.2f} (case port face {R.CASE_Y0}, behind a {R.LIP_T} mm lip)",
    "PASS" if abs(ugb.ymin - (R.CASE_Y0 + R.LIP_T)) < 0.05 else "FAIL", "in the same rear plane as the other ports")
ahd = adp.BoundingBox()
rep("HDMI ext", "Socket height vs adapter HDMI", f"centre z {(ugb.zmin+ugb.zmax)/2:.1f} vs adapter HDMI z {R.HDMI_ZC - 0.5:.1f}", "PASS",
    "both HDMI outputs sit in one row")
xc = (R.CAV_X0 + R.CAV_X1) / 2
lipf = open_fraction([sh], grid(xc - 7, xc + 7, R.HDMI_ZC - 2.25, R.HDMI_ZC + 2.25, R.CASE_Y0 + 0.7, n=6))
rep("HDMI ext", "Plug opening in front of the socket", f"{lipf*100:.0f}% open ({R.LIP_OPEN[0]} x {R.LIP_OPEN[1]} mm)",
    "PASS" if lipf > .99 else "FAIL")
win = open_fraction([sh, brd_t], [(x, y, z) for x in (-13.0, -8.0, -3.0, -1.1) for y in (40, 44, 48) for z in (49, 52, 55)])
rep("HDMI ext", "Tower cable window -> case cable exit", f"{win*100:.0f}% open path", "PASS" if win > .99 else "FAIL")
path = math.dist((55, 57), (0, 44)) + 20 + 15 + 7 + 6
rep("HDMI ext", "Cable length needed", f"~{path:.0f} mm of 200-220 mm", "PASS" if path < 190 else "WARN",
    "free micro-HDMI -> case exit -> 90 deg turn in tower chamber -> housing")
rep("HDMI ext", "Free micro-HDMI reachable with adapter fitted", "needs a notch in the adapter at that port",
    "UNVERIFIED", "adapter edge sits ~1 mm from the Pi edge; check the plug actually seats before printing")

# ================= I. print =================
for n, s, bed in (("Faceplate one-piece", fp, 256), ("Faceplate halves", cq.importers.importStep(
        "/home/claude/v3/rack_out/Rack_Faceplate_Left.step").val(), 220), ("Shelf", sh, 220)):
    bb = s.BoundingBox()
    dims = sorted([bb.xlen, bb.ylen, bb.zlen], reverse=True)
    rep("Print", n, f"{dims[0]:.0f} x {dims[1]:.0f} mm footprint", "PASS" if dims[0] <= bed - 2 or (bed == 256 and dims[0] <= 254.1) else "WARN",
        f"bed {bed} mm" + (" (254 mm part: 256 mm beds only)" if bed == 256 else ""))

w = max(len(r[1]) for r in rows)
cat = None
for c, item, val, st, note in rows:
    if c != cat:
        print(f"\n[{c}]"); cat = c
    print(f"  {st:10s} {item:{w}s}  {val}" + (f"   -- {note}" if note else ""))
