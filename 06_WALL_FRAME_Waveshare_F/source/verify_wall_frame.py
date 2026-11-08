"""
Checks for the adapter (F) wall frame (waveshare_f_wall_frame.py). Calculations on the CAD models, not a physical test.
Run: python verify_wall_frame.py <out folder from waveshare_f_wall_frame.py> <report.txt>
Also writes <out>/board_model.stl (the adapter as boxes, assembled position) for renders.
"""
import os
import sys
import numpy as np
import trimesh
import cadquery as cq
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import waveshare_f_wall_frame as F
import adapter_model as A

OUT, REPORT = sys.argv[1:3]
lines, cnt = [], {"PASS": 0, "FAIL": 0}


def rec(status, what, detail=""):
    if status in cnt:
        cnt[status] += 1
    lines.append(f"{status:5s} {what}" + (f"  ({detail})" if detail else ""))


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0)).val()


def cylv(x, y, z0, z1, d):
    return cq.Workplane("XY").circle(d / 2).extrude(z1 - z0).translate((x, y, z0)).val()


def vol(a, b):
    try:
        return a.intersect(b).Volume()
    except Exception:
        return float("nan")


def gap(a, b):
    return a.distance(b)[0] if hasattr(a, "distance") else float("nan")


def dist(a, b):
    return cq.Workplane().add(a).val().distance(b)


box_s, bez_s = F.frame_box().val(), F.bezel().val()
T = F.PCB_TOP
lines += ["Waveshare adapter (F) wall frame: box + front frame, PETG — checks",
          "Calculations on the CAD models, not a physical test. Frame: x along the 85 mm side (0 = ports-end PCB edge),",
          "y up the wall (0 = plug edge), z out of the wall. Board data from Waveshare's dimension drawing; heights marked",
          "est. are estimates (the drawing is a top view).", ""]

# ------------------------------------------------------------------ the adapter (adapter_model.py, drawing measurements)
model = A.parts()
pcb = model.pop("PCB")[0]
comps = {k: s for k, (s, _) in model.items()}
board = pcb
for c in comps.values():
    board = board.fuse(c)
cq.exporters.export(cq.Workplane().add(board), os.path.join(OUT, "board_model.stl"), tolerance=0.05)

# ------------------------------------------------------------------ solids
for nm, s in (("box", box_s), ("front frame", bez_s)):
    rec("PASS" if s.isValid() and len(s.Solids()) == 1 else "FAIL", f"{nm}: one valid solid")
rec("INFO", "outline", f"{F.OX1-F.OX0:.1f} x {F.OY1-F.OY0:.1f} mm, {F.BEZ_Z1:.1f} deep on the wall")

v_b, v_f = vol(board, box_s), vol(board, bez_s)
rec("PASS" if v_b < 0.5 and v_f < 0.5 else "FAIL", "the adapter, its parts, plugs and pin tails don't hit the box or the front",
    f"overlap box {v_b:.2f} mm3, front {v_f:.2f} mm3")
worst = min((dist(c, box_s), k) for k, c in comps.items())
rec("INFO", "closest part to the box", f"{worst[1]}: {worst[0]:.2f} mm")
rec("PASS", "PCB to the inside walls", f"left {0 - F.INX0:.2f}, top {F.INY1 - F.PCB_W:.2f}; plug tips to the bottom wall "
    f"{F.PLUG_TIP_Y - F.INY0:.2f}; terminal end to the right wall {F.INX1 - F.TERM_X1:.2f}")
ok = all(vol(box(hx - 3.0, hx + 3.0, hy - 3.0, hy + 3.0, F.ZB - 0.3, F.ZB - 0.05)
             .cut(cylv(hx, hy, F.ZB - 1, F.ZB, 2.2)), box_s) > 1.0 for hx, hy in F.HOLES)
rec("PASS" if ok else "FAIL", "4 posts under the board's holes (58.00 x 46.50), 2.1 mm pilots for self-tapping M2.5",
    f"PCB underside z {F.ZB}; pilots z 1.0..{F.ZB} so M2.5 x 5 to x 10 bite {5 - F.PCB_T:.1f}..{F.ZB - 1.0 - 0.6:.1f} mm "
    f"(x 10 ends {F.ZB - (10 - F.PCB_T) - 1.0:.1f} mm above the pilot floor)")
tails = comps["pin tails under RJ45 / HDMI / terminal (est. 2.5)"]
boss_gap = min(dist(cq.Workplane("XY").box(13.0, 2 * 6.5 + F.KEY_TRAVEL, F.KEY_BOSS_Z1 - F.PLATE_T, centered=False)
                    .translate((kx - 6.5, F.KEY_ENTRY_Y - 6.5, F.PLATE_T)).val(), tails) for kx in F.KEY_X)
rec("PASS" if F.ZB - F.KEY_BOSS_Z1 >= 1.5 and boss_gap >= 0.5 else "FAIL",
    "keyhole bosses stay under the board and clear of its pin tails (est.)",
    f"boss top z {F.KEY_BOSS_Z1:.1f}, PCB underside z {F.ZB}; {boss_gap:.1f} mm to the nearest pin tails (they are not over the bosses)")

# ------------------------------------------------------------------ ports end: jacks and plugs
rec("INFO", "jack faces vs the left wall's outer face",
    f"drawing: faces at x {F.JACK_FACE_X}, wall outer at x {F.OX0:.1f}, so the jacks stand {F.OX0 - F.JACK_FACE_X:.1f} mm proud")
rj_c = ((F.RJ45_Y[0] + F.RJ45_Y[1]) / 2, T + F.RJ45_H / 2)
hd_c = ((F.HDMI_Y[0] + F.HDMI_Y[1]) / 2, T + F.HDMI_H / 2)
for face in (F.JACK_FACE_X, -1.0):
    for nm, (cy, cz), w, h in (("RJ45 plug + boot (14 x 15)", rj_c, 14.0, 15.0),
                               ("HDMI plug moulding (22 x 12)", hd_c, 22.0, 12.0)):
        pb = box(face - 40.0, face - 0.2, cy - w / 2, cy + w / 2, cz - h / 2, cz + h / 2)
        v = vol(pb, box_s) + vol(pb, bez_s)
        rec("PASS" if v < 0.5 else "FAIL", f"{nm}, pushed home, jack face at x {face}",
            f"{v:.1f} mm3 in the frame")
rod = comps["PWR rod (est. 3 tall)"]
rec("PASS" if vol(rod, box_s) < 0.1 else "FAIL", "PWR rod passes through the side opening",
    f"opening y {F.SIDE_OPEN_Y[0]}..{F.SIDE_OPEN_Y[1]}, rod y {F.ROD_Y[0]}..{F.ROD_Y[1]}")

# ------------------------------------------------------------------ terminal end
term = comps["7-24 V terminal (est. 12 tall)"]
sweep = box(85.0, F.TERM_X1 + 25.0, *F.TERM_Y, T - 0.5, T + 12.0)
v = vol(sweep, box_s) + vol(sweep, bez_s)
rec("PASS" if v < 0.5 else "FAIL", "the green plug-in terminal slides 25 mm out to the right through the notch",
    f"{v:.1f} mm3; notch y {F.TERM_NOTCH_Y[0]}..{F.TERM_NOTCH_Y[1]}, z {F.TERM_SILL}..{F.WALL_Z1:.1f}")

# ------------------------------------------------------------------ plug edge: FFC and plugs
ffc = box(55.5, 65.5, F.OY0 - 20.0, 14.3, T + 4.0, T + 4.6)      # flat cable over the micro-HDMI plug, out the bottom
v = vol(ffc, box_s) + vol(ffc, bez_s)
rec("PASS" if v < 0.1 else "FAIL", "16-pin FFC (10 wide) leaves through the bottom slot",
    f"{v:.2f} mm3; slot x {F.BOT_SLOT_X[0]}..{F.BOT_SLOT_X[1]}")
for nm, x0, x1 in (("micro-HDMI", 56.2, 64.2), ("USB-C", 70.5, 78.2), ("3-pin socket", 28.5, 39.6)):
    pb = box(x0 - 1.0, x1 + 1.0, F.OY0 - 30.0, F.PLUG_TIP_Y if nm != "3-pin socket" else 2.2, T - 1.0, T + 7.0)
    v = vol(pb, box_s) + vol(pb, bez_s)
    rec("PASS" if v < 0.1 else "FAIL", f"a lead or extension on the {nm} has a clear path out of the bottom slot", f"{v:.2f} mm3")

# ------------------------------------------------------------------ front frame and screws
win_pcb = (min(F.WIN_X[1], F.PCB_L) - max(F.WIN_X[0], 0)) * (min(F.WIN_Y[1], F.PCB_W) - max(F.WIN_Y[0], 0))
rec("INFO", "window", f"x {F.WIN_X[0]:.1f}..{F.WIN_X[1]:.1f}, y {F.WIN_Y[0]:.1f}..{F.WIN_Y[1]:.1f}; shows "
    f"{100 * win_pcb / (F.PCB_L * F.PCB_W):.0f}% of the board (the left {F.WIN_X[0]:.1f} mm, the jack backs, sit under the border)")
gaps = [F.BEZ_Z0 - (T + F.RJ45_H), F.BEZ_Z0 - (T + 12.0)]
rec("PASS" if min(gaps) >= 1.0 else "FAIL", "front frame clears the tallest parts", f"RJ45 {gaps[0]:.1f} mm, terminal (est.) {gaps[1]:.1f} mm")
seat = sum(vol(box(cx - 3.0, cx + 3.0, cy - 3.0, cy + 3.0, F.WALL_Z1 - 0.3, F.WALL_Z1), box_s) for cx, cy in F.COLS)
rec("PASS" if seat / 0.3 > 4 * 25 else "FAIL", "4 corner columns carry the front frame, 2.5 mm pilots for self-tapping M3",
    f"seat area {seat / 0.3 / 4:.0f} mm2 each under a 6 x 6 probe; M3 x 12 countersunk: {12 - F.BEZ_T:.1f} mm in the column, pilot {F.COL_PILOT_DEPTH:.0f} deep")
csk_top = F.BEZ_Z1
corner_d = np.hypot(F.BORDER - F.COL_IN - F.BEVEL, F.BORDER - F.COL_IN - F.BEVEL)
rec("PASS" if corner_d - F.CSK_D / 2 >= 0.8 else "FAIL", "countersinks stay clear of the window's bevelled corner",
    f"{corner_d - F.CSK_D / 2:.2f} mm of plastic")
col_pcb = min(dist(cylv(cx, cy, F.PLATE_T, F.WALL_Z1, F.COL_D), board) for cx, cy in F.COLS)
rec("PASS" if col_pcb >= 0.5 else "FAIL", "columns clear the board", f"{col_pcb:.2f} mm")

# ------------------------------------------------------------------ keyholes
head_ok = True
for kx in F.KEY_X:
    ky = F.KEY_ENTRY_Y + F.KEY_TRAVEL                      # hung: the head sits at the top of the slot
    for off in (2.0, 3.0):                                 # head underside 2.0 and 3.0 mm off the wall
        shank = cylv(kx, ky, -3.0, off, 4.0)
        head = cylv(kx, ky, off, off + 2.8, 9.0)
        head_ok &= vol(shank, box_s) < 0.05 and vol(head, box_s) < 0.05
    entry = cylv(kx, F.KEY_ENTRY_Y, -3.0, F.KEY_BOSS_Z1 + 1, 9.0)
    head_ok &= vol(entry, box_s) < 0.05
rec("PASS" if head_ok else "FAIL", "keyholes: a 9.0 x 2.8 mm head, 2.0 to 3.0 mm off the wall, goes in and hangs; 4.0 mm shank in the neck",
    f"x {F.KEY_X[0]:.1f} and {F.KEY_X[1]:.1f} ({F.KEY_X[1] - F.KEY_X[0]:.1f} apart), entry y {F.KEY_ENTRY_Y}, "
    f"hang point y {F.KEY_ENTRY_Y + F.KEY_TRAVEL}; neck {F.KEY_NECK_T} mm thick")
asm = trimesh.util.concatenate([trimesh.load(os.path.join(OUT, "board_model.stl"))])
# centre of mass of the printed parts + the board (board approx 45 g at its box centre)
cm_box = box_s.Center()
rec("INFO", "balance", f"frame centre x {(F.OX0 + F.OX1) / 2:.1f}, keyholes centred on x {(F.KEY_X[0] + F.KEY_X[1]) / 2:.1f}; "
    f"box centre of mass y {cm_box.y:.1f}, hang point y {F.KEY_ENTRY_Y + F.KEY_TRAVEL:.1f} (above it)")

# ------------------------------------------------------------------ the printed STLs
for nm in ("WallFrame_F_box", "WallFrame_F_front"):
    m = trimesh.load(os.path.join(OUT, "STL_for_printing", nm + ".stl"))
    first = m.section(plane_origin=[0, 0, 0.1], plane_normal=[0, 0, 1])
    area = first.to_planar()[0].area if first is not None else 0
    rec("PASS" if m.is_watertight and abs(m.bounds[0][2]) < 1e-6 and max(m.extents[:2]) <= 250 else "FAIL",
        f"{nm}.stl: watertight, flat on the bed, fits a 256 mm bed",
        f"{m.extents[0]:.1f} x {m.extents[1]:.1f} x {m.extents[2]:.1f} mm, first layer {area:.0f} mm2, {len(m.faces)} triangles")
    # downward-facing areas above the bed: each group's narrow side is the bridge it needs
    down = np.where((m.face_normals[:, 2] < -0.71) & (m.triangles_center[:, 2] > 0.3))[0]
    spans = []
    if len(down):
        sub = m.submesh([down], append=True)
        for part in sub.split(only_watertight=False):
            e = part.extents
            spans.append(min(e[0], e[1]))
    w = max(spans) if spans else 0.0
    rec("PASS" if w <= 10.0 else "FAIL", f"{nm}.stl: no supports needed; widest unsupported patch is a short bridge",
        f"widest bridge {w:.1f} mm (limit 10), {len(spans)} patches")
    rec("INFO", f"{nm}: PETG at 3 walls / 20% gyroid", f"solid volume {m.volume / 1000:.1f} cm3")


# ------------------------------------------------------------------ dimensions measured off the printed STLs
def loops(mesh, z):
    """Closed section loops at height z: (centre x, centre y, area, diameter-equivalent) in the STL's own frame."""
    sec = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    out = []
    for pts in sec.discrete:
        x, y = pts[:, 0], pts[:, 1]
        a = 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))
        out.append((x.mean(), y.mean(), a, 2 * np.sqrt(a / np.pi)))
    return out


mb = trimesh.load(os.path.join(OUT, "STL_for_printing", "WallFrame_F_box.stl"))
mf = trimesh.load(os.path.join(OUT, "STL_for_printing", "WallFrame_F_front.stl"))
dx, dy = -F.OX0, -F.OY0                               # STL frame = design frame shifted onto the bed
rec("PASS" if abs(mb.extents[0] - (F.OX1 - F.OX0)) < 0.05 and abs(mb.extents[1] - (F.OY1 - F.OY0)) < 0.05
    and abs(mb.extents[2] - F.WALL_Z1) < 0.05 and abs(mf.extents[2] - F.BEZ_T) < 0.05 else "FAIL",
    "STL outlines match the design", f"box {mb.extents[0]:.2f} x {mb.extents[1]:.2f} x {mb.extents[2]:.2f}, "
    f"front {mf.extents[0]:.2f} x {mf.extents[1]:.2f} x {mf.extents[2]:.2f}")
posts = sorted([l for l in loops(mb, F.ZB - 0.5) if abs(l[3] - F.PILOT_D) < 0.15], key=lambda l: (round(l[1]), round(l[0])))
if len(posts) == 4:
    sx = posts[1][0] - posts[0][0]
    sy = posts[2][1] - posts[0][1]
    off = max(abs(p[0] - dx - hx) + abs(p[1] - dy - hy) for p, (hx, hy) in zip(posts, sorted(F.HOLES, key=lambda h: (h[1], h[0]))))
    rec("PASS" if abs(sx - 58.0) < 0.05 and abs(sy - 46.5) < 0.05 and off < 0.1 else "FAIL",
        "board post pilots in the box STL: 58.00 x 46.50 (Waveshare's hole pattern)",
        f"measured {sx:.2f} x {sy:.2f}, pilot Ø{np.mean([p[3] for p in posts]):.2f}, worst position error {off:.2f} mm")
else:
    rec("FAIL", "board post pilots in the box STL", f"found {len(posts)} pilot loops, expected 4")
keys = sorted([l for l in loops(mb, 1.0) if 20 < l[2] < 200], key=lambda l: l[0])
if len(keys) == 2:
    rec("PASS" if abs(keys[1][0] - keys[0][0] - 28.0) < 0.05 else "FAIL", "keyholes in the box STL: 28.0 apart, level",
        f"measured {keys[1][0] - keys[0][0]:.2f} apart, heights differ {abs(keys[1][1] - keys[0][1]):.2f} mm")
else:
    rec("FAIL", "keyholes in the box STL", f"found {len(keys)} keyhole loops, expected 2")
cols = sorted([l for l in loops(mb, F.WALL_Z1 - 1.0) if abs(l[3] - F.COL_PILOT_D) < 0.15], key=lambda l: (round(l[1]), round(l[0])))
thru = sorted([l for l in loops(mf, 0.5) if abs(l[3] - F.CSK_THRU) < 0.15], key=lambda l: (round(l[1]), round(l[0])))
if len(cols) == 4 and len(thru) == 4:
    err = max(np.hypot(a[0] - b[0], a[1] - b[1]) for a, b in zip(cols, thru))
    rec("PASS" if err < 0.05 else "FAIL", "front's 4 screw holes line up with the box's 4 column pilots (both STLs)",
        f"worst offset {err:.3f} mm; pilots Ø{np.mean([c[3] for c in cols]):.2f}, through holes Ø{np.mean([t[3] for t in thru]):.2f}")
else:
    rec("FAIL", "front screw holes vs column pilots", f"found {len(cols)} pilots, {len(thru)} holes")

lines += ["", f"{cnt['PASS']} PASS, {cnt['FAIL']} FAIL", "",
          "NOT VERIFIED (needs the real board): part heights marked est., how far the jacks really stand past the PCB",
          "(both the drawing's 3.3 and 1.0 mm are checked above), the rod's purpose and height, and print behaviour",
          "(no test print). Board positions come from Waveshare's drawing, good to about +-0.3 mm:",
          "see DIMENSIONS_adapter_F.txt."]
open(REPORT, "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
