"""
Clearance check of the delivered STEP files, plus a dimensioned clearance schematic.

The two print STEPs are read back from disk, moved to their assembled place (and compared with the assembled STEPs),
then measured with exact OpenCASCADE distances against: every part of the adapter model (adapter_model.py, from
Waveshare's drawing), the screws (board M2.5 x 6, front M3 x 12 countersunk, wall screws in the keyholes) and the
cable plugs / leads that have to get past the frame. The schematic is drawn from sections through the same meshes,
with the front view laid over Waveshare's own dimension drawing (registered on the four hole centres).

Run: python step_clearance_check.py <folder with WallFrame_F_*.step (print)> <folder with assembled STEPs>
                                    <Waveshare drawing png> <out folder>
"""
import os
import sys
import numpy as np
import trimesh
import cadquery as cq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch
from PIL import Image
from shapely.geometry import Polygon, box as sbox
from shapely.ops import nearest_points
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import waveshare_f_wall_frame as F
import adapter_model as A

PRINT_DIR, ASM_DIR, DRAWING, OUT = sys.argv[1:5]
os.makedirs(OUT, exist_ok=True)
lines, cnt = [], {"PASS": 0, "FAIL": 0, "TIGHT": 0}
MIN_GAP = 0.25          # below this a printed part may rub (PETG walls come out ~0.1-0.2 fat)


def rec(status, what, detail=""):
    if status in cnt:
        cnt[status] += 1
    lines.append(f"{status:5s} {what}" + (f"  ({detail})" if detail else ""))


def wp_box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0)).val()


def wp_cyl(x, y, z0, z1, d):
    return cq.Workplane("XY").circle(d / 2).extrude(z1 - z0).translate((x, y, z0)).val()


def mesh_of(shape, tol=0.01):
    v, t = shape.tessellate(tol, 0.1)
    return trimesh.Trimesh(np.array([p.toTuple() for p in v]), np.array(t), process=False)


# ------------------------------------------------------------------ 1. read the delivered STEPs back
lines += ["Wall frame for the Waveshare adapter (F): clearance check of the delivered STEP files",
          "Exact OpenCASCADE distances between the STEP solids (read back from disk, moved to their assembled place) and",
          "the adapter model, the screws and the cable plugs. Adapter positions: Waveshare's drawing, +-0.3 mm",
          f"(DIMENSIONS_adapter_F.txt). TIGHT = under {MIN_GAP} mm, may rub once printed. Not a physical test.", ""]
frame = {}
for nm, z0 in (("WallFrame_F_box", 0.0), ("WallFrame_F_front", F.BEZ_Z0)):
    s = cq.importers.importStep(os.path.join(PRINT_DIR, nm + ".step")).val()
    lo = mesh_of(s, 0.005).bounds[0]
    s = s.translate(cq.Vector(F.OX0 - lo[0], F.OY0 - lo[1], z0 - lo[2]))
    asm = cq.importers.importStep(os.path.join(ASM_DIR, nm + ".step")).val()
    diff = s.cut(asm).Volume() + asm.cut(s).Volume()
    rec("PASS" if s.isValid() and diff < 0.01 else "FAIL", f"{nm}.step (print position) read back; moved to its assembled place "
        f"it is the same solid as STEP_for_Onshape/{nm}.step", f"difference {diff:.4f} mm3, volume {s.Volume() / 1000:.3f} cm3")
    frame[nm] = s
BOX, FRONT = frame["WallFrame_F_box"], frame["WallFrame_F_front"]
lines.append("")

# ------------------------------------------------------------------ 2. what goes in and past the frame
T, B = F.PCB_TOP, F.ZB
parts = A.parts()
hw = {}
for i, (hx, hy) in enumerate(F.HOLES):
    hw[f"board screw {i + 1} M2.5 x 6 pan head"] = wp_cyl(hx, hy, T, T + 1.8, 4.5).fuse(wp_cyl(hx, hy, T - 6.0, T, 2.5))
for i, (cx, cy) in enumerate(F.COLS):
    head = cq.Solid.makeCone(1.5, 2.75, 1.25, pnt=cq.Vector(cx, cy, F.BEZ_Z1 - 1.25))
    hw[f"front screw {i + 1} M3 x 12 countersunk"] = head.fuse(wp_cyl(cx, cy, F.BEZ_Z1 - 12.0, F.BEZ_Z1 - 1.2, 3.0))
for i, kx in enumerate(F.KEY_X):
    ky = F.KEY_ENTRY_Y + F.KEY_TRAVEL
    for off in (2.0, 3.0):          # head underside 2-3 mm off the wall, as the README asks
        hw[f"wall screw {i + 1} head {off:.0f} mm off the wall (9.0 x 2.8, shank 4.0)"] = (
            wp_cyl(kx, ky, off, off + 2.8, 9.0).fuse(wp_cyl(kx, ky, -8, off, 4.0)))
rj_c = (sum(F.RJ45_Y) / 2, T + F.RJ45_H / 2)
hd_c = (sum(F.HDMI_Y) / 2, T + F.HDMI_H / 2)
env = {
    "RJ45 plug + boot 14 x 15, pushed home": wp_box(F.JACK_FACE_X - 40, F.JACK_FACE_X - 0.2, rj_c[0] - 7, rj_c[0] + 7, rj_c[1] - 7.5, rj_c[1] + 7.5),
    "HDMI plug moulding 22 x 12, pushed home": wp_box(F.JACK_FACE_X - 40, F.JACK_FACE_X - 0.2, hd_c[0] - 11, hd_c[0] + 11, hd_c[1] - 6, hd_c[1] + 6),
    "HDMI moulding if the jack sits 1.0 back": wp_box(-41.0, -1.2, hd_c[0] - 11, hd_c[0] + 11, hd_c[1] - 6, hd_c[1] + 6),
    "terminal plug pulled 25 mm out": wp_box(85.0, F.TERM_X1 + 25, *F.TERM_Y, T - 0.5, T + 12.0),
    "FFC 10 wide, out of the bottom": wp_box(55.5, 65.5, F.OY0 - 20, 14.3, T + 4.0, T + 4.6),
    "lead on the micro-HDMI plug": wp_box(55.2, 65.2, F.OY0 - 30, F.PLUG_TIP_Y, T - 1.0, T + 7.0),
    "lead on the USB-C plug": wp_box(69.5, 79.2, F.OY0 - 30, F.PLUG_TIP_Y, T - 1.0, T + 7.0),
    "lead on the 3-pin socket": wp_box(27.5, 40.6, F.OY0 - 30, 2.2, T - 1.0, T + 7.0),
}


def gaps(shape):
    out = {}
    for fn, fs in (("box", BOX), ("front", FRONT)):
        try:
            ov = shape.intersect(fs).Volume()
        except Exception:
            ov = float("nan")
        out[fn] = (shape.distance(fs), ov)
    return out


lines.append(f"{'':5s} {'part':58s} {'to box':>8s} {'to front':>9s}")
for name, (shape, finish) in parts.items():
    g = gaps(shape)
    ov = g["box"][1] + g["front"][1]
    gmin = min(g["box"][0], g["front"][0])
    est = " (est.)" if "est." in name else ""
    if name == "PCB":
        st = "PASS" if ov < 0.01 else "FAIL"
        note = "sits on the 4 posts" if g["box"][0] < 1e-6 and ov < 0.01 else ""
    else:
        st = "FAIL" if ov > 0.01 else ("TIGHT" if gmin < MIN_GAP else "PASS")
        note = ""
    rec(st, f"{name:58s} {g['box'][0]:8.2f} {g['front'][0]:9.2f}", note or (f"overlap {ov:.2f} mm3" if ov > 0.01 else ""))
lines.append("")
for name, shape in hw.items():
    g = gaps(shape)
    if name.startswith("board screw"):
        bite = (B - (T - 6.0))
        spare = (T - 6.0) - 1.0
        rec("PASS" if spare > 0.5 else "FAIL", f"{name:58s} {'thread':>8s} {g['front'][0]:9.2f}",
            f"{bite:.1f} mm into the post's Ø{F.PILOT_D} pilot, tip {spare:.1f} mm above its floor")
    elif name.startswith("front screw"):
        bite = F.WALL_Z1 - (F.BEZ_Z1 - 12.0)
        spare = (F.BEZ_Z1 - 12.0) - (F.WALL_Z1 - F.COL_PILOT_DEPTH)
        board_gap = min(shape.distance(p[0]) for p in parts.values())
        rec("PASS" if spare > 0.5 and board_gap > MIN_GAP else "FAIL", f"{name:58s} {'thread':>8s} {'csk':>9s}",
            f"{bite:.1f} mm into the column's Ø{F.COL_PILOT_D} pilot, tip {spare:.1f} mm above its floor; {board_gap:.2f} to the board")
    else:
        lo_, hi_ = F.KEY_NECK_T, F.KEY_NECK_T + F.KEY_CAV_T - 2.8
        rec("FAIL" if g["box"][1] > 0.01 else "PASS", f"{name:58s} {g['box'][0]:8.2f} {g['front'][0]:9.2f}",
            f"set by hand, not a printed fit: a 2.8 mm head works from {lo_:.1f} to {hi_:.1f} mm off the wall")
lines.append("")
for name, shape in env.items():
    g = gaps(shape)
    ov = g["box"][1] + g["front"][1]
    gmin = min(g["box"][0], g["front"][0])
    rec("FAIL" if ov > 0.01 else ("TIGHT" if gmin < MIN_GAP else "PASS"), f"{name:58s} {g['box'][0]:8.2f} {g['front'][0]:9.2f}",
        f"overlap {ov:.2f} mm3" if ov > 0.01 else "")
lines.append("")
# headline gaps, as plain numbers
wall_gaps = {
    "PCB edge to the left wall (top-left stub)": parts["PCB"][0].distance(BOX.intersect(wp_box(-5, 0, 49.5, 60, 0, 30))),
    "terminal end to the right wall": F.INX1 - F.TERM_X1,
    "plug tips to the bottom wall line": F.PLUG_TIP_Y - F.INY0,
    "RJ45 top to the front frame": F.BEZ_Z0 - (T + F.RJ45_H),
    "jack faces proud of the left wall": F.OX0 - F.JACK_FACE_X,
    "keyhole boss top to the PCB underside": B - F.KEY_BOSS_Z1,
}
for k, v in wall_gaps.items():
    rec("INFO", k, f"{v:.2f} mm")

lines += ["", f"{cnt['PASS']} PASS, {cnt['TIGHT']} TIGHT, {cnt['FAIL']} FAIL",
          "Parts marked est. have estimated heights or positions (the drawing is a top view); pin tails are a guess."]
open(os.path.join(OUT, "CLEARANCES_from_STEP.txt"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines))

# ------------------------------------------------------------------ 3. the schematic
meshes = {"box": mesh_of(BOX, 0.01), "front": mesh_of(FRONT, 0.01)}
style = {"box": dict(fc="#5a5a5a", ec="#111", lw=0.6, alpha=1.0), "front": dict(fc="#7a7a7a", ec="#111", lw=0.6, alpha=1.0)}
fin = {"pcb": "#1f6b41", "steel": "#b9bec4", "gold": "#d9a93c", "green": "#3cb371", "white": "#efe6cf",
       "ferrite": "#2a2a2a", "alu": "#c9c9cf", "ssd": "#36463d", "hidden": "#e9c46a"}
for name, (shape, finish) in parts.items():
    meshes[name] = mesh_of(shape, 0.02)
    style[name] = dict(fc=fin[finish], ec="#222", lw=0.4, alpha=0.95 if finish != "hidden" else 0.5,
                       hatch="////" if finish == "hidden" else None)
for name, shape in hw.items():
    meshes[name] = mesh_of(shape, 0.02)
    style[name] = dict(fc="#3a6fd8", ec="#123", lw=0.4, alpha=0.9)
for name, shape in env.items():
    meshes[name] = mesh_of(shape, 0.05)
    style[name] = dict(fc="none", ec="#e67e22", lw=1.0, ls="--", alpha=1.0)

AX2D = {0: (2, 1), 1: (0, 2), 2: (0, 1)}       # x-section: (z, y); y-section: (x, z); z-section: (x, y)


def section(mesh, axis, c):
    sec = mesh.section(plane_origin=np.eye(3)[axis] * c, plane_normal=np.eye(3)[axis])
    if sec is None:
        return Polygon()
    i, j = AX2D[axis]
    g = Polygon()
    for loop in sec.discrete:
        if len(loop) >= 3:
            g = g.symmetric_difference(Polygon(loop[:, [i, j]]).buffer(0))
    return g


def draw(ax, g, **st):
    polys = [g] if g.geom_type == "Polygon" else [p for p in getattr(g, "geoms", []) if p.geom_type == "Polygon"]
    for p in polys:
        if p.is_empty:
            continue
        paths = [MPath(np.asarray(p.exterior.coords))] + [MPath(np.asarray(r.coords)) for r in p.interiors]
        kw = {k: v for k, v in st.items() if v is not None}
        ax.add_patch(PathPatch(MPath.make_compound_path(*paths), **kw))


def gap_arrow(ax, ga, gb, clip=None, dx=0.0, dy=0.0, color="#d62828"):
    if clip is not None:
        ga, gb = ga.intersection(clip), gb.intersection(clip)
    if ga.is_empty or gb.is_empty:
        return
    pa, pb = nearest_points(ga, gb)
    d = pa.distance(pb)
    (x0, y0), (x1, y1) = pa.coords[0], pb.coords[0]
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="<->", color=color, lw=1.1, shrinkA=0, shrinkB=0))
    ax.annotate(f"{d:.2f}", xy=((x0 + x1) / 2, (y0 + y1) / 2), xytext=((x0 + x1) / 2 + dx, (y0 + y1) / 2 + dy),
                color=color, fontsize=7.5, weight="bold", ha="center", va="center",
                bbox=dict(fc="white", ec=color, lw=0.5, pad=1.2),
                arrowprops=dict(arrowstyle="-", color=color, lw=0.5) if (dx or dy) else None)


def dim(ax, p0, p1, text, off, color="#1d3557", horiz=True):
    (x0, y0), (x1, y1) = p0, p1
    if horiz:
        y = y0 + off
        ax.plot([x0, x0], [y0, y], color=color, lw=0.4)
        ax.plot([x1, x1], [y1, y], color=color, lw=0.4)
        ax.annotate("", xy=(x1, y), xytext=(x0, y), arrowprops=dict(arrowstyle="<->", color=color, lw=0.7))
        ax.text((x0 + x1) / 2, y + (1.2 if off > 0 else -1.2), text, color=color, fontsize=7.5, ha="center",
                va="bottom" if off > 0 else "top")
    else:
        x = x0 + off
        ax.plot([x0, x], [y0, y0], color=color, lw=0.4)
        ax.plot([x1, x], [y1, y1], color=color, lw=0.4)
        ax.annotate("", xy=(x, y1), xytext=(x, y0), arrowprops=dict(arrowstyle="<->", color=color, lw=0.7))
        ax.text(x + (1.2 if off > 0 else -1.2), (y0 + y1) / 2, text, color=color, fontsize=7.5, rotation=90,
                ha="left" if off > 0 else "right", va="center")


def panel(ax, axis, c, title, names, arrows, xlabel, ylabel, lim):
    secs = {n: section(meshes[n], axis, c) for n in names}
    order = ["box", "front"] + [n for n in names if n not in ("box", "front")]
    for n in order:
        if not secs[n].is_empty:
            draw(ax, secs[n], **style[n])
    for a in arrows:
        n1, n2 = a[0], a[1]
        kw = a[2] if len(a) > 2 else {}
        gap_arrow(ax, secs[n1], secs[n2], **kw)
    ax.set_title(title, fontsize=10, loc="left", weight="bold")
    ax.set_xlabel(xlabel, fontsize=7.5)
    ax.set_ylabel(ylabel, fontsize=7.5)
    ax.set_xlim(*lim[0])
    ax.set_ylim(*lim[1])
    ax.set_aspect("equal")
    ax.tick_params(labelsize=6.5)
    ax.grid(True, lw=0.25, alpha=0.4)
    return secs


fig, axs = plt.subplots(2, 3, figsize=(23.4, 15.0))
fig.suptitle("Waveshare Pi5 Connector Adapter (F) wall frame: clearances measured on the delivered STEP files "
             "(mm; red = gap, orange dashed = cable plug / lead space, blue = screws, hatched = estimated pin tails)",
             fontsize=12, weight="bold", x=0.01, ha="left")

# --- front view over Waveshare's drawing (registered on the hole centres: x = 24.05 + (px - 337.05) / 6.775 ...)
ax = axs[0, 0]
img = np.asarray(Image.open(DRAWING).convert("RGB"))
h, w = img.shape[:2]
ext = (24.05 + (0 - 337.05) / 6.775, 24.05 + (w - 337.05) / 6.775, 49.5 - (h - 120.25) / 6.817, 49.5 - (0 - 120.25) / 6.817)
ax.imshow(img, extent=ext, origin="upper", alpha=0.85, zorder=0)
zc = T + 3.0
fs = {n: section(meshes[n], 2, zc) for n in ("box", "PCB", "7-24 V terminal (est. 12 tall)", "USB-C plug", "micro-HDMI plug")}
fs["PCB"] = section(meshes["PCB"], 2, (B + T) / 2)
draw(ax, fs["box"], fc="#d62828", ec="#7a0000", lw=0.6, alpha=0.45)
draw(ax, fs["PCB"], fc="none", ec="#00a651", lw=1.0, ls="--")
for n in ("7-24 V terminal (est. 12 tall)", "USB-C plug", "micro-HDMI plug"):
    draw(ax, fs[n], fc="none", ec="#00a651", lw=0.8, ls="--")
win = section(meshes["front"], 2, F.BEZ_Z0 + 0.5)
for r in ([win] if win.geom_type == "Polygon" else win.geoms):
    for ring in r.interiors:
        xs, ys = np.asarray(ring.coords).T
        ax.plot(xs, ys, color="#1d3557", lw=1.0, ls="-.")
gap_arrow(ax, fs["PCB"], fs["box"], clip=sbox(-6, 46, 6, 66), dx=-9, dy=6)
gap_arrow(ax, fs["7-24 V terminal (est. 12 tall)"], fs["box"], clip=sbox(90, 4, 106, 20), dx=6, dy=9)
gap_arrow(ax, fs["USB-C plug"], fs["box"], clip=sbox(60, -14, 90, 10), dx=8, dy=-6)
gap_arrow(ax, fs["PCB"], fs["box"], clip=sbox(30, 50, 60, 66), dx=6, dy=0)
dim(ax, (F.OX0, F.OY1), (F.OX1, F.OY1), f"{F.OX1 - F.OX0:.1f}", 5)
dim(ax, (F.OX1, F.OY0), (F.OX1, F.OY1), f"{F.OY1 - F.OY0:.1f}", 5, horiz=False)
for kx in F.KEY_X:
    ax.add_patch(plt.Circle((kx, F.KEY_ENTRY_Y), F.KEY_ENTRY_D / 2, fill=False, ec="#1d3557", ls=":", lw=0.8))
dim(ax, (F.KEY_X[0], F.KEY_ENTRY_Y), (F.KEY_X[1], F.KEY_ENTRY_Y), "28.0 keyholes (behind)", -40)
ax.set_title(f"A  Front: frame cut at z {zc:.1f} (red) over Waveshare's drawing;\n"
             f"    model board dashed green, front window dash-dot", fontsize=10, loc="left", weight="bold")
ax.set_xlim(-26, 117)
ax.set_ylim(-26, 80)
ax.set_aspect("equal")
ax.tick_params(labelsize=6.5)
ax.set_xlabel("x along the board (0 = ports-end PCB edge)", fontsize=7.5)
ax.set_ylabel("y up the wall (0 = plug edge)", fontsize=7.5)

allp = [n for n in parts]
rjc = sum(F.RJ45_Y) / 2
panel(axs[0, 1], 1, rjc, f"B  Section y = {rjc:.1f}: RJ45, left keyhole boss",
      ["box", "front"] + allp + ["RJ45 plug + boot 14 x 15, pushed home"],
      [("RJ45 (13.5 tall)", "front", dict(dx=10, dy=6)),
       ("PCB", "box", dict(clip=sbox(28, 4, 43, 12), dx=0, dy=-7)),
       ("PCB", "box", dict(clip=sbox(85, 9, 110, 12), dx=0, dy=8)),
       ("RJ45 plug + boot 14 x 15, pushed home", "front", dict(dx=-14, dy=8))],
      "x", "z out of the wall (0 = wall)", ((-46, 108), (-4, 36)))
hdc = 10.9
panel(axs[0, 2], 1, hdc, f"C  Section y = {hdc:.1f}: HDMI jack, 7-24 V terminal",
      ["box", "front"] + allp + ["HDMI plug moulding 22 x 12, pushed home", "terminal plug pulled 25 mm out"],
      [("HDMI-A (6.5 tall)", "front", dict(dx=8, dy=0)),
       ("7-24 V terminal (est. 12 tall)", "front", dict(dx=-8, dy=4)),
       ("7-24 V terminal (est. 12 tall)", "box", dict(dx=5, dy=-6)),
       ("HDMI plug moulding 22 x 12, pushed home", "box", dict(dx=-7, dy=-6)),
       ("terminal plug pulled 25 mm out", "front", dict(dx=8, dy=6))],
      "x", "z out of the wall", ((-46, 126), (-4, 36)))
usb = 74.35
panel(axs[1, 0], 0, usb, f"D  Section x = {usb:.2f}: USB-C plug, bottom slot, top wall",
      ["box", "front"] + allp + ["lead on the USB-C plug"],
      [("USB-C plug", "box", dict(dx=6, dy=-5)),
       ("lead on the USB-C plug", "box", dict(dx=-6, dy=-8)),
       ("PCB", "box", dict(clip=sbox(8, 50, 14, 66), dx=8, dy=0)),
       ("inductors (est. 7 tall)", "front", dict(dx=5, dy=5))],
      "z out of the wall (0 = wall)", "y up the wall", ((-6, 40), (-42, 68)))
kx = F.KEY_X[0]
panel(axs[1, 1], 0, kx, f"E  Section x = {kx:.1f}: left keyhole, wall screw head 3 mm out",
      ["box", "front"] + allp + [n for n in hw if n.startswith("wall screw 1 head 3")],
      [("wall screw 1 head 3 mm off the wall (9.0 x 2.8, shank 4.0)", "box", dict(dx=6, dy=6)),
       ("PCB", "box", dict(clip=sbox(3, 25, 10, 50), dx=6, dy=-4)),
       ("PoE transformer (est. 10 tall)", "front", dict(dx=4, dy=5)),
       ("3-pin socket (est. 6 tall)", "front", dict(dx=5, dy=-4))],
      "z out of the wall", "y up the wall", ((-10, 40), (-14, 66)))
cx = F.COLS[1][0]
panel(axs[1, 2], 0, cx, f"F  Section x = {cx:.1f}: right-hand front screws, terminal",
      ["box", "front"] + allp + [n for n in hw if n.startswith("front screw")],
      [("7-24 V terminal (est. 12 tall)", "front", dict(dx=6, dy=5)),
       ("front screw 2 M3 x 12 countersunk", "7-24 V terminal (est. 12 tall)", dict(dx=-6, dy=4))],
      "z out of the wall", "y up the wall", ((-6, 40), (-14, 66)))
for ax in axs.flat:
    for sp in ax.spines.values():
        sp.set_linewidth(0.5)
fig.text(0.01, 0.005, "Sections are cut through the delivered STEP files (read back from disk) and the adapter model; "
         "red arrows measure within each section, the table gives the 3D minimum. "
         "Board positions from Waveshare's drawing (+-0.3 mm); parts marked est. have estimated heights. "
         "Full numbers: CLEARANCES_from_STEP.txt.", fontsize=8)
fig.tight_layout(rect=(0, 0.015, 1, 0.97))
for ext_ in ("png", "pdf"):
    fig.savefig(os.path.join(OUT, f"CLEARANCE_SCHEMATIC.{ext_}"), dpi=170)
print("schematic written")
