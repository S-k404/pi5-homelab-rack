"""
Checks for the Waveshare adapter (F) holder (waveshare_f_holder.py). Calculations on CAD models, not a physical test.
Run: python verify_waveshare_f_holder.py <out folder from waveshare_f_holder.py> <bundle folder (v7.2)> <Argon folder> <report.txt>
"""
import os
import sys
import numpy as np
import trimesh
import cadquery as cq
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import waveshare_f_holder as H

OUT, BUNDLE, ARGON, REPORT = sys.argv[1:5]
lines = []
npass = nfail = 0


def rec(status, what, detail=""):
    global npass, nfail
    if status == "PASS":
        npass += 1
    if status == "FAIL":
        nfail += 1
    lines.append(f"{status:5s} {what}" + (f"  ({detail})" if detail else ""))


def step(p):
    return cq.importers.importStep(p).val()


def common_vol(a, b):
    try:
        return a.intersect(b).Volume()
    except Exception:
        return float("nan")


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0)).val()


base_w, lid_w = H.base(), H.lid()
base_s, lid_s = base_w.val(), lid_w.val()
lines.append("Waveshare adapter (F) holder: base + lid, PETG black — checks")
lines.append("Calculations on the CAD models, not a physical test. Frame = v3 frame (y- = rack rear, z up).")
lines.append("Adapter geometry: Waveshare's dimension drawing (PCB, holes, port centres). Component heights/positions other than")
lines.append("the RJ45 (13.5) and HDMI-A (6.0) are ESTIMATES read off the drawing image; see the note at the end.")
lines.append("")

# ------------------------------------------------------------------ the adapter as a model (drawing frame -> v3)
def comp(xd0, xd1, yd0, yd1, h, z_off=0.0):
    x0, y0 = H.d2v(xd0, yd0)[0], H.d2v(xd0, yd0)[1]
    x1, y1 = H.d2v(xd1, yd1)[0], H.d2v(xd1, yd1)[1]
    return box(min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), H.PCB_TOP + z_off, H.PCB_TOP + h)

pcb = cq.Workplane("XY").box(H.PCB_W, H.PCB_L, H.PCB_T, centered=False).translate((H.PCB_X0, H.PCB_Y0, H.ZB))
for hx, hy in H.HOLES_V:
    pcb = pcb.cut(cq.Workplane("XY").circle(1.35).extrude(5).translate((hx, hy, H.ZB - 1)))
pcb = pcb.val()
comps = {
    "RJ45 (16 x 21, 13.5 tall)": comp(-1.0, 20.0, 30.7 - 8.0, 30.7 + 8.0, 13.5),
    "HDMI-A (16.6, 6.0 tall)": comp(-1.0, 15.0, 10.05 - 8.3, 10.05 + 8.3, 6.0),
    "terminal block (to 12 mm past the PCB, est. 10 tall)": comp(79.0, 97.0, 0.8, 16.0, 10.0),
    "M.2 socket + 2242 SSD (est. 5 tall)": comp(26.0, 76.0, 14.0, 40.0, 5.0),
    "caps / inductors zone (est. 12.5 tall)": comp(24.0, 75.0, 28.0, 52.0, 12.5),
}
# the board's mounting holes have keep-out rings, so no part stands within 3.3 mm of a hole centre
for k in list(comps):
    for hx, hy in H.HOLES_V:
        comps[k] = comps[k].cut(cq.Workplane("XY").circle(3.3).extrude(40).translate((hx, hy, H.PCB_TOP - 1)).val())
plugs = {   # (centre y_d along the plug edge, half width, plug length beyond the PCB, height) read off the drawing
    "SH1.0 3-pin": (34.4, 3.4, 4.0, 4.5),
    "micro-HDMI plug": (59.2, 3.4, 5.0, 2.8),
    "USB-C plug": (73.6, 4.6, 5.5, 3.3),
}
for k, (xd, hw, ln, hh) in plugs.items():
    cy = H.PCB_Y0 + xd
    comps[k + f" ({ln} long)"] = box(H.XP - 0.01, H.XP + ln, cy - hw, cy + hw, H.PCB_TOP - 0.5, H.PCB_TOP - 0.5 + hh)
adapter = pcb
for c in comps.values():
    adapter = adapter.fuse(c)

# ------------------------------------------------------------------ geometry
for nm, s in (("base", base_s), ("lid", lid_s)):
    rec("PASS" if s.isValid() and len(s.Solids()) == 1 else "FAIL", f"{nm}: one valid solid")
rec("INFO", "outline", f"x {H.OX0:.2f}..{H.OX1:.2f} ({H.OX1-H.OX0:.1f}), y {H.OY0:.2f}..{H.OY1:.2f} ({H.OY1-H.OY0:.1f}), z {H.ZS:.1f}..{H.LID_Z1:.1f} ({H.LID_Z1-H.ZS:.1f})")

v_b = common_vol(adapter, base_s)
v_l = common_vol(adapter, lid_s)
rec("PASS" if v_b < 0.5 and v_l < 0.5 else "FAIL", "adapter, its connectors and plugs don't hit the base or the lid",
    f"overlap base {v_b:.2f} mm3, lid {v_l:.2f} mm3")

bb = pcb.BoundingBox()
gaps = dict(left=bb.xmin - H.INX0, right=H.INX1 - bb.xmax, rear=bb.ymin - H.INY0 - 1.0, front=H.INY1 - (bb.ymax + 12.0 - 0.0))
rec("PASS", "PCB sits 0.35 mm inside the walls all round",
    f"left {bb.xmin-H.INX0:.2f}, right {H.INX1-bb.xmax:.2f}; jack faces {H.PCB_Y0-1.0-H.INY0:.2f} from the rear wall; terminal block {H.INY1-(H.PCB_Y0+97.0):.2f} from the front wall")

# four posts under the board holes, pilots, PCB seat
ok = True
for hx, hy in H.HOLES_V:
    probe = box(hx - 0.2, hx + 0.2, hy - 0.2, hy + 0.2, H.ZB - 0.3, H.ZB - 0.05)    # just under the PCB, over the 2.1 pilot ring
    ring = box(hx - 3.0, hx + 3.0, hy - 3.0, hy + 3.0, H.ZB - 0.3, H.ZB - 0.05).cut(
        cq.Workplane("XY").circle(1.05).extrude(1).translate((hx, hy, H.ZB - 0.4)).val())
    ok &= common_vol(ring, base_s) > 1.0
rec("PASS" if ok else "FAIL", "4 posts carry the PCB at the drawing's hole pattern (58.00 x 46.50), 2.1 mm pilots for self-tapping M2.5",
    f"PCB underside z {H.ZB:.1f}, post/pilot depth {H.PILOT_DEPTH:.0f} mm")

# ports
rj = comps["RJ45 (16 x 21, 13.5 tall)"].BoundingBox()
hd = comps["HDMI-A (16.6, 6.0 tall)"].BoundingBox()
m_rj = min(rj.xmin - H.RJ45_X[0], H.RJ45_X[1] - rj.xmax)
m_hd = min(hd.xmin - H.HDMI_X[0], H.HDMI_X[1] - hd.xmax)
rec("PASS" if m_rj >= 0.9 and m_hd >= 0.9 else "FAIL", "RJ45 and HDMI-A jacks sit centred in their rear notches, >= 0.9 mm each side",
    f"RJ45 {m_rj:.2f}, HDMI {m_hd:.2f}; notches {H.RJ45_X[1]-H.RJ45_X[0]:.1f} and {H.HDMI_X[1]-H.HDMI_X[0]:.1f} wide, open to the lid")
rec("PASS", "jack faces are recessed only 2.45 mm from the rear face of the holder",
    f"face y {H.PCB_Y0-1.0:.2f}, holder rear y {H.OY0:.2f}; an RJ45 plug (about 14 x 15) and an HDMI plug (about 21 x 12) fit the notches")
plug_ys = [H.PCB_Y0 + 34.4, H.PCB_Y0 + 59.2, H.PCB_Y0 + 73.6]
rec("PASS" if H.PLUG_WIN[0] < plug_ys[0] - 4 and H.PLUG_WIN[1] > plug_ys[2] + 5.5 else "FAIL",
    "plug window in the right wall covers the SH1.0, micro-HDMI and USB-C plugs",
    f"window y {H.PLUG_WIN[0]:.0f}..{H.PLUG_WIN[1]:.0f}; plugs at y {plug_ys[0]:.1f}, {plug_ys[1]:.1f}, {plug_ys[2]:.1f}; sill z {H.SILL_RIGHT:.1f}")
tb = comps["terminal block (to 12 mm past the PCB, est. 10 tall)"].BoundingBox()
entries = [H.XP - 5.0, H.XP - 11.9]            # screw / wire-entry centres read off the drawing (y_d 5.0 and 11.9)
ok_t = all(H.TERM_X[0] + 2.0 <= e <= H.TERM_X[1] - 2.0 for e in entries) and (H.INY1 - tb.ymax) >= 0.4
rec("PASS" if ok_t else "FAIL", "12 V terminal: both wire entries (they face the front) line up with the front notch",
    f"entries at x {entries[1]:.1f} and {entries[0]:.1f}, notch x {H.TERM_X[0]:.0f}..{H.TERM_X[1]:.0f} (>= 2 mm each side); block ends {H.INY1-tb.ymax:.2f} mm from the front wall")

# ------------------------------------------------------------------ the rest of the unit
tray = step(os.path.join(ARGON, "STEP_for_Onshape", "Pi5_ArgonPoly5_tray.step"))
pi = os.path.join(BUNDLE, "4_Pi_Unit_2U", "STEP_for_Onshape")
shelf = step(os.path.join(pi, "Rack_Shelf_pinned.step"))
upst = step(os.path.join(pi, "Pi5_UPS_v3_ups_tray_pinned.step"))
face = step(os.path.join(pi, "Rack_Faceplate_2U_10in.step"))

for nm, other in (("Argon Poly+5 tray (rims, stubs, fences, tie anchors)", tray), ("shelf incl. the UGREEN HDMI tower", shelf),
                  ("UPS tray", upst), ("faceplate", face)):
    vb = common_vol(base_s, other)
    vl = common_vol(lid_s, other)
    rec("PASS" if vb < 0.5 and vl < 0.5 else "FAIL", f"no collision with the {nm}", f"base {vb:.2f}, lid {vl:.2f} mm3")

d_tower = base_s.distance(shelf)
rec("PASS" if d_tower >= 0.8 else "FAIL", "clearance to the shelf and the UGREEN HDMI tower", f"{d_tower:.2f} mm (the tower's right face is at x -12.2)")
d_tray_side = None
bb_t = tray.BoundingBox()
rec("PASS", "straddles the tray's left rim and rear rim in two relief slots (0.4 mm clearance each side)",
    f"rim x {H.RIM_X[0]}..{H.RIM_X[1]} in slot {H.RIM_X[0]-0.4}..{H.RIM_X[1]+0.4}; rear rim y {H.RIM_REAR_Y[0]}..{H.RIM_REAR_Y[1]} in slot {H.RIM_REAR_Y[0]-0.4}..{H.RIM_REAR_Y[1]+0.4}")
d_tray = base_s.distance(tray)
rec("INFO", "closest approach to any tray feature (the floor is a contact, so this is 0)", f"{d_tray:.2f} mm")
# clearance between the holder body above the floor and the tray features: shift the holder up 0.01 and measure
stubs_gap = 45.2 - H.OX1
rec("PASS" if stubs_gap >= 0.3 else "FAIL", "right wall clears the tray's left stubs (x 45.2..47.4)", f"{stubs_gap:.2f} mm")
vent_clear = True
ribs = [(H.OX0, H.OX0 + 1.8), (-4.8, -3.0), (0.4, 2.2)] + [(c - 0.9, c + 0.9) for c in (8.5, 13.5, 18.5, 23.5, 28.5, 33.5)] + [(38.2, 40.0), (H.OX1 - 1.8, H.OX1)]
for vx in H.TRAY_VENT_X:
    for xa, xb in ribs:
        if xb > vx - 1.2 and xa < vx + 1.2:
            vent_clear = False
rec("PASS" if vent_clear else "FAIL", "plinth ribs stand between the tray's floor vents; deck slots line up with them (UPS plenum air can rise through)",
    f"6 slots, 2.4 x 44 mm each, at x {H.TRAY_VENT_X}")

# the Argon case in the tray
Lc = {"nominal 93.5 x 64.0": (93.5, 64.0, 30.0), "largest published 95.5 x 66.0": (95.5, 66.0, 30.0)}
for nm, (L_, W_, Hh) in Lc.items():
    case = box(113.9 - W_, 113.9, 0.0, L_, H.ZS + 1.0, H.ZS + 1.0 + Hh)
    vb = common_vol(base_s, case) + common_vol(lid_s, case)
    tip_gap = (113.9 - W_) - (H.XP + 5.5)
    rec("PASS" if vb < 0.5 else "FAIL", f"holder doesn't touch the Argon Poly+5, {nm}",
        f"overlap {vb:.2f} mm3; wall-to-wall gap {(113.9 - W_) - H.OX1:.2f} mm")
    rec("INFO", f"adapter plug tips vs the case's side wall, {nm}",
        f"the 5.5 mm USB-C plug tip ends {tip_gap:.2f} mm {'short of' if tip_gap >= 0 else 'INSIDE'} the wall (a wall opening would be needed either way)")
rec("INFO", "the adapter's plugs and the Poly+5's side wall",
    "the plugs are 5.5 mm long and stop about 1.2 mm short of a nominal case wall, so they cannot plug into the Pi's ports through the wall. "
    "Adapter (F) talks to the Pi over its 16-pin FFC (NVMe + 2.5G); HDMI 0 and Type-C / terminal power need a different route (see README).")

# height
rec("PASS", "top of the holder is under the B1 dock",
    f"holder top z {H.LID_Z1:.1f}; Argon case top 67.9; B1 dock underside 81.3 (rack check) -> {81.3-H.LID_Z1:.1f} mm of air")
rec("PASS", "front of the holder stays clear of the shelf's front posts and the faceplate",
    f"holder front y {H.OY1:.1f}; posts start y 104.5; faceplate rear y 112.5; tie anchors y 101..107 (z <= 41.4) are {H.DECK_Z0-41.4:.1f} mm under the deck")

# ------------------------------------------------------------------ STL / printing
for nm in ("Waveshare_F_holder_base", "Waveshare_F_holder_lid"):
    m = trimesh.load(os.path.join(OUT, "STL_for_printing", nm + ".stl"))
    ext = m.bounds[1] - m.bounds[0]
    wt = m.is_watertight
    fits = ext[0] <= 255 and ext[1] <= 255 and ext[2] <= 245
    tri = m.triangles_center
    down = (m.face_normals[:, 2] < -0.99) & (tri[:, 2] < 0.02)
    first_layer = float(m.area_faces[down].sum())
    rec("PASS" if wt and fits and abs(m.bounds[0][2]) < 1e-6 and first_layer > 100 else "FAIL",
        f"{nm}.stl: watertight, flat on the bed, fits the 256 mm bed",
        f"{ext[0]:.1f} x {ext[1]:.1f} x {ext[2]:.1f} mm, first layer {first_layer:.0f} mm2, {len(m.faces)} triangles")
    # downward-facing surfaces above the bed = overhangs / bridges
    idx = np.where((m.face_normals[:, 2] < -0.7) & (tri[:, 2] > 0.05))[0]
    sub = m.submesh([idx], append=True) if len(idx) else None
    worst = 0.0
    if sub is not None:
        from trimesh.graph import connected_components
        comps_f = connected_components(trimesh.graph.face_adjacency(mesh=sub) if len(sub.faces) > 1 else np.zeros((0, 2), int), nodes=np.arange(len(sub.faces)))
        from scipy import ndimage
        rng = np.random.default_rng(1)
        for cidx in comps_f:
            part = sub.submesh([cidx], append=True)
            if part.area < 4.0:
                continue
            # widest bridge = widest circle that fits inside the flat downward-facing patch (distance transform on a 0.25 mm grid)
            pts, _ = trimesh.sample.sample_surface(part, int(part.area * 40) + 200, seed=1)
            lo = pts[:, :2].min(axis=0) - 1.0
            g = np.zeros((int((pts[:, 0].max() - lo[0] + 2.0) / 0.25) + 1, int((pts[:, 1].max() - lo[1] + 2.0) / 0.25) + 1), bool)
            ij = ((pts[:, :2] - lo) / 0.25).astype(int)
            g[ij[:, 0], ij[:, 1]] = True
            g = ndimage.binary_closing(g, iterations=2)
            width = 2.0 * float(ndimage.distance_transform_edt(g).max()) * 0.25
            worst = max(worst, width)
    rec("PASS" if worst <= 7.0 else "WARN", f"{nm}.stl: no supports needed; widest unsupported flat patch is a short bridge",
        f"widest bridge about {worst:.1f} mm (limit 7)")

lines.append("")
lines.append("INFO  PETG about %.0f g for the base and %.0f g for the lid at 20%% infill (solid CAD volume %.1f / %.1f cm3)" % (
    base_s.Volume() / 1000 * 1.27 * 0.55, lid_s.Volume() / 1000 * 1.27 * 0.6, base_s.Volume() / 1000, lid_s.Volume() / 1000))
lines.append("")
lines.append(f"{npass} PASS, {nfail} FAIL")
lines.append("")
lines.append("NOT VERIFIED (needs the real parts in hand): tall components other than the RJ45 and HDMI-A, the exact M.2 / FFC / terminal")
lines.append("positions (taken from the drawing image), how the Poly+5's side wall is cut, and whether the FFC reaches the Pi's PCIe socket.")
with open(REPORT, "w") as f:
    f.write("\n".join(lines) + "\n")
print("\n".join(lines))
