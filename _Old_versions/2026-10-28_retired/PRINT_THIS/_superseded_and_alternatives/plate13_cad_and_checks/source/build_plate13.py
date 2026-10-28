"""Plate 13 (12 V brick cradle + spacers) and plate 11's second file (the same plate with the 12 V lead notch in the
faceplate): pre-arranged 3MFs read back and compared, layout pictures, SETTINGS.txt, and a picture of the cradle
in the rack. Same 3MF writer and plate checks as the PRINT_THIS builder.
Usage: python build_plate13.py <v7.2 bundle> <out folder from brick_cradle.py> <PRINT_THIS folder>"""
import os
import shutil
import sys
import zipfile
import xml.etree.ElementTree as ET
from xml.sax.saxutils import quoteattr
import numpy as np
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import brick_cradle as B

BUNDLE, OUT, PT = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, os.path.join(BUNDLE, "1_Rack_9U_T0-look", "source"))
import rack_t0 as r          # noqa: E402
import units as un           # noqa: E402

BED, MARGIN, GAP = 256.0, 1.0, 2.0
STL = os.path.join(OUT, "STL_for_printing")
D13 = os.path.join(PT, "13_PETG_12V-brick-cradle")
D11 = os.path.join(PT, "11_PETG_Pi-board-tray+lid+faceplate")
F = {"cradle": (os.path.join(STL, "Brick_Cradle_12V.stl"), "Brick cradle"),
     **{f"sp{t:.0f}": (os.path.join(STL, f"Brick_Spacer_{t:.0f}mm.stl"), f"Spacer {t:.0f} mm") for t in B.SPACERS},
     "board": (os.path.join(D11, "Pi5_UPS_v3_board_tray_HDMIexit.stl"), "Board tray"),
     "lid": (os.path.join(D11, "Pi5_UPS_v3_lid.stl"), "Lid"),
     "face": (os.path.join(D11, "Rack_Faceplate_2U_10in.stl"), "Pi faceplate"),
     "faceN": (os.path.join(STL, "Rack_Faceplate_2U_10in_DC-notch.stl"), "Pi faceplate, 12 V lead notch")}
MESH = {k: trimesh.load(p, force="mesh") for k, (p, _) in F.items()}


def T(x, y, z=0.0):
    m = np.eye(4); m[:3, 3] = (x, y, z); return m


def place(items):
    out = []
    for key, x, y in items:
        lo = MESH[key].bounds[0]
        out.append((key, T(x, y) @ T(-lo[0], -lo[1], -lo[2])))
    return out


def check(placed):
    res, boxes = [], []
    for key, M in placed:
        b = trimesh.transform_points(MESH[key].vertices, M)
        lo, hi = b.min(0), b.max(0)
        boxes.append((lo, hi))
        ok = lo[0] >= MARGIN - 1e-6 and lo[1] >= MARGIN - 1e-6 and hi[0] <= BED - MARGIN + 1e-6 and hi[1] <= BED - MARGIN + 1e-6 and abs(lo[2]) < 1e-6
        res.append((ok, f"{F[key][1]}: x {lo[0]:.1f}-{hi[0]:.1f}, y {lo[1]:.1f}-{hi[1]:.1f}, {hi[2]:.1f} tall, on the bed"))
    gap = min(max(b0[0] - a1[0], a0[0] - b1[0], b0[1] - a1[1], a0[1] - b1[1])
              for i, (a0, a1) in enumerate(boxes) for (b0, b1) in boxes[i + 1:])
    res.append((gap >= GAP, f"smallest gap between parts {gap:.1f} mm"))
    return res


def write_3mf(path, placed):
    objs, build = [], []
    for i, (key, M) in enumerate(placed, start=1):
        m = MESH[key].copy().apply_transform(M)
        vs = "".join(f'<vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>' for x, y, z in m.vertices)
        ts = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in m.faces)
        nm = os.path.basename(F[key][0])[:-4]
        objs.append(f'<object id="{i}" name={quoteattr(nm)} type="model"><mesh><vertices>{vs}</vertices><triangles>{ts}</triangles></mesh></object>')
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
        z.writestr("[Content_Types].xml", ct); z.writestr("_rels/.rels", rels); z.writestr("3D/3dmodel.model", model)
    return read_back(path, [MESH[k].copy().apply_transform(M) for k, M in placed])


def read_back(path, refs):
    ns = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
    got = ET.fromstring(zipfile.ZipFile(path).read("3D/3dmodel.model")).findall(".//m:object", ns)
    if len(got) != len(refs):
        return False
    for o, ref in zip(got, refs):
        v = np.array([[float(e.get(a)) for a in "xyz"] for e in o.findall(".//m:vertex", ns)])
        t = np.array([[int(e.get(a)) for a in ("v1", "v2", "v3")] for e in o.findall(".//m:triangle", ns)])
        mm = trimesh.Trimesh(v, t, process=False)
        if not (np.allclose(mm.bounds, ref.bounds, atol=1e-3) and abs(mm.volume - ref.volume) < 1e-3 * ref.volume):
            return False
    return True


def draw_plate(path, placed, title):
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.add_patch(plt.Rectangle((0, 0), BED, BED, fc="#f4f4f2", ec="#555", lw=1.2))
    for key, M in placed:
        m = MESH[key]
        v = trimesh.transform_points(m.vertices, M)
        ax.add_collection(PolyCollection(v[m.faces][:, :, :2], facecolors="#3f6fb0", edgecolors="none", alpha=0.9))
        c = (v.min(0) + v.max(0)) / 2
        ax.text(c[0], c[1], F[key][1], ha="center", va="center", fontsize=7, bbox=dict(fc="white", ec="none", alpha=0.8, pad=1))
    ax.set_xlim(-4, BED + 4); ax.set_ylim(-4, BED + 4); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(title, fontsize=8)
    fig.savefig(path, dpi=130, bbox_inches="tight"); plt.close(fig)


def rect(ax, x0, x1, y0, y1, **kw):
    ax.add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, **kw))


def to_mesh(wp):
    vs, fs = wp.val().tessellate(0.1, 0.3)
    return trimesh.Trimesh([(v.x, v.y, v.z) for v in vs], fs, process=False)


def draw_plan(path):
    """left: top view of the bottom of the rack (front at the top); right: the front of the Pi unit"""
    fig, (a, b) = plt.subplots(1, 2, figsize=(13, 7.4), gridspec_kw=dict(width_ratios=[1.0, 1.15]))
    # --- top view: x across, z down the page = towards the rear
    rect(a, -r.X_OUT, r.X_OUT, 0, r.D, fc="none", ec="#999", lw=1)
    for z0, z1 in r.BAR_Z:
        rect(a, -r.X_IN, r.X_IN, z0, z1, fc="#d9d4c7", ec="#a89f88", lw=0.6)
    for s in (1, -1):
        for z0, z1 in ((0, r.POST), (r.D - r.POST, r.D)):
            rect(a, min(s * r.X_IN, s * r.X_OUT), max(s * r.X_IN, s * r.X_OUT), z0, z1, fc="#bbb", ec="#888", lw=0.6)
    sh = un.pi_unit(os.path.join(BUNDLE, "4_Pi_Unit_2U", "STEP_for_Onshape"))
    for nm, fc in (("Pi shelf", "#e8e8e8"), ("Pi board tray", "#c9d6e8")):
        bb = sh[nm].val().BoundingBox()
        rect(a, bb.xmin, bb.xmax, bb.zmin, bb.zmax, fc=fc, ec="#7a8aa0", lw=0.8)
    a.text(-20, 60, "Pi unit\n(UPS under the Pi)", ha="center", va="center", fontsize=9)
    rect(a, -127, 127, -4, 0, fc="#666", ec="none")
    m = to_mesh(B.brick_cradle())
    up = m.face_normals[:, 1] > 0.5
    tri = m.vertices[m.faces][up]
    yc = tri[:, :, 1].mean(1)
    cols = [(0.25, 0.42 - 0.2 * (y > 20), 0.7) for y in yc]
    a.add_collection(PolyCollection(tri[:, :, [0, 2]], facecolors=cols, edgecolors=cols, lw=0.3))
    br = B.brick_dummy(110.0, 50.0, 30.0, 8.0).val().BoundingBox()
    rect(a, br.xmin, br.xmax, br.zmin, br.zmax, fc="#3a3a3a", ec="black", lw=0.8, alpha=0.85)
    a.annotate("12 V brick\n110 x 50 x 30\n(standing on\nits long edge)", xy=(br.xmax - 4, 150), xytext=(122, 150), fontsize=7.5,
               va="center", arrowprops=dict(arrowstyle="->", lw=0.8))
    sp = B.spacer(8.0).val().BoundingBox()
    rect(a, B.XI0, sp.xmax, sp.zmin, sp.zmax, fc="#e3a33b", ec="none")
    a.annotate("8 mm spacer", xy=(B.XI0 + 4, 120), xytext=(30, 150), fontsize=7.5, arrowprops=dict(arrowstyle="->", lw=0.8))
    xc = (br.xmin + br.xmax) / 2
    path_xz = [(xc, br.zmin), (xc, 40.0), (B.NOTCH_X, 22.0), (B.NOTCH_X, 8.0), (B.NOTCH_X, -4.0), (B.NOTCH_X - 6, -10), (45, -10)]
    a.plot(*zip(*path_xz), color="#c62828", lw=2.4)
    a.text(118, 30, "12 V lead\n(spare coiled here,\ntied to the anchor)", color="#c62828", fontsize=7.5, ha="left", va="center")
    a.add_patch(plt.Rectangle((xc - 16.75, br.zmax), 33.5, 40, fc="none", ec="#2e7d32", lw=1.4, ls="--"))
    a.annotate("mains plug + cord\nout the back", xy=(xc, br.zmax + 30), xytext=(10, 228), color="#2e7d32", fontsize=7.5,
               arrowprops=dict(arrowstyle="->", color="#2e7d32", lw=0.8))
    a.text(0, -14, "FRONT (Pi faceplate)", ha="center", fontsize=9, weight="bold")
    a.text(0, 216, "REAR", ha="center", fontsize=9, weight="bold")
    a.text(-108, 86, "middle bar", fontsize=7, va="center"); a.text(-108, 194, "rear bar", fontsize=7, va="center")
    a.text(-108, 7, "front bar", fontsize=7, va="center")
    a.set_xlim(-145, 160); a.set_ylim(245, -30); a.set_aspect("equal"); a.set_xlabel("mm across the rack")
    a.set_title("Top view, bottom 2U: the cradle drops onto the middle and rear bars", fontsize=10)
    # --- front view of the Pi unit
    fpn = un.pi_unit(os.path.join(OUT, "checks", "rack_step_DC-notch"))["Pi faceplate"]
    fm = to_mesh(fpn)
    front = fm.face_normals[:, 2] < -0.5
    b.add_collection(PolyCollection(fm.vertices[fm.faces][front][:, :, :2], facecolors="#9aa3ad", edgecolors="#9aa3ad", lw=0.3))
    for s in (1, -1):
        rect(b, min(s * r.X_IN, s * r.X_OUT), max(s * r.X_IN, s * r.X_OUT), -r.PLINTH, 88.9, fc="#d0d0d0", ec="#999", lw=0.6)
    rect(b, -r.X_IN, r.X_IN, -17, 0, fc="#d9d4c7", ec="#a89f88", lw=0.6)
    b.plot([-150, 150], [-r.PLINTH, -r.PLINTH], color="#555", lw=1)
    dc_x, dc_y = (112.0 + 80.0) / 2 - 56.95, (5.0 + 29.0) / 2 + 8.0
    b.add_patch(plt.Circle((dc_x, dc_y), 5.5, fc="#222", ec="none"))
    lead = [(dc_x, dc_y - 5), (dc_x + 3, 6.0), (dc_x + 14, 3.0), (B.NOTCH_X, 3.0)]
    b.plot(*zip(*lead), color="#c62828", lw=2.6, solid_capstyle="round")
    b.annotate("12 V lead out of the notch,\n~2 cm across to the DC-IN window", xy=(B.NOTCH_X, 4), xytext=(60, -45), fontsize=8,
               color="#c62828", ha="center", arrowprops=dict(arrowstyle="->", color="#c62828", lw=0.8))
    b.annotate("DC-IN (plug in here, as before)", xy=(dc_x, dc_y + 6), xytext=(-20, 110), fontsize=8, ha="center",
               arrowprops=dict(arrowstyle="->", lw=0.8))
    b.annotate("the brick sits behind\nthese vents", xy=(90, 40), xytext=(150, 110), fontsize=8, ha="center",
               arrowprops=dict(arrowstyle="->", lw=0.8))
    b.set_xlim(-150, 190); b.set_ylim(-60, 125); b.set_aspect("equal"); b.set_xlabel("mm across the rack")
    b.set_title("Front of the Pi unit with the notched faceplate (plate 11's second file)", fontsize=10)
    fig.tight_layout(); fig.savefig(path, dpi=130, bbox_inches="tight"); plt.close(fig)


SETTINGS = ["Bambu Studio profile: 0.20mm Standard @BBL P1S", "Filament: Generic PETG", "Wall loops: 3",
            "Sparse infill: 20% gyroid", "Supports: OFF", "Plate: Textured PEI, no glue", "Enclosure: CLOSED"]
report = []

# ---- plate 13 ----
placed = place([("cradle", 12, 34)] + [(f"sp{t:.0f}", 80, 20 + 40 * i) for i, t in enumerate(B.SPACERS)])
res = check(placed)
res.append((write_3mf(os.path.join(D13, "Plate13.3mf"), placed), f"Plate13.3mf written and read back: same {len(placed)} parts, same places, same volumes"))
report.append(("Plate13", res))
draw_plate(os.path.join(D13, "Plate13_layout.png"), placed, "Plate13 · PETG 0.20 mm · 256 x 256 bed")
draw_plan(os.path.join(D13, "Plate13_in_the_rack.png"))
for k, _, _ in [(k, 0, 0) for k, _ in placed]:
    shutil.copy2(F[k][0], os.path.join(D13, os.path.basename(F[k][0])))
lines = ["13_PETG_12V-brick-cradle", "=" * 24,
         "Status: print now (it fits the brick in your Robu cart, and most other 60 W bricks)",
         "Material: PETG, about 116 g (cradle ~63 g, spacers 10-17 g each)", "",
         "What it is: a cradle for the 12 V 5 A brick, in the empty bay to the right of the Pi unit (behind the right half",
         "of the Pi faceplate). It drops onto the rack's middle and rear base bars. No screws. See Plate13_in_the_rack.png.",
         "To get the 12 V lead out to the UPS DC-IN, also print plate 11's second file, Plate11_WITH-DC-notch.3mf",
         "(the same plate with a small notch in the bottom edge of the faceplate).", "",
         "How: double-click the .3mf (or File > Open Project in Bambu Studio). Every part is already placed.",
         "If Bambu Studio asks, choose to load the geometry only. Then pick the settings below and Slice.", "", "Settings:"]
lines += ["  - " + x for x in SETTINGS] + ["",
          "Notes:",
          "  The cradle prints floor down. The two notches under the floor are short bridges (13 mm), fine in PETG.",
          "  Four spacers are on the plate; you'll use one. If you're short of PETG, delete the ones you won't need:",
          "    brick 29-30.5 mm thick -> 8 mm spacer (Robu's brick is listed 110 x 50 x 30)",
          "    30.5-32.5 -> 6 mm   32.5-34.5 -> 4 mm   34.5-36.5 -> 2 mm   36.5-38.2 -> none",
          "  Takes bricks up to 140 long x 60 tall (standing on edge) x 38.2 thick.", "",
          "Fitting it:",
          "  1. Clip the spacer over the cradle's LEFT wall (the side towards the Pi), flange on the wall top.",
          "  2. Stand the brick on its long edge in the cradle, mains socket at the BACK, pushed back against the low kerb.",
          "  3. Two hook-and-loop straps (or zip ties) round the cradle and the brick, between the two notches.",
          "  4. Lower it into the bay right of the Pi unit so the floor notches sit over the middle and rear base bars.",
          "  5. Mains cord: plug into the brick from behind the rack. 12 V lead: run it forward along the cradle, coil the",
          "     spare in front of the brick (zip-tie it to the anchor), then over the front base bar, out through the",
          "     faceplate notch and into the UPS DC-IN window. Fit the faceplate after the lead is in its notch.",
          "  The brick gets warm in use; the bay is open at the back, top and bottom, and the faceplate vents are in front.", "",
          "On this plate:", "  - 12 V brick cradle x1   (Brick_Cradle_12V.stl)"]
lines += [f"  - Spacer {t:.0f} mm x1   (Brick_Spacer_{t:.0f}mm.stl)" for t in B.SPACERS]
open(os.path.join(D13, "SETTINGS.txt"), "w").write("\n".join(lines) + "\n")

# ---- plate 11, second file: the faceplate with the notch, everything else as Plate11.3mf ----
items = [("board", 8, 10), ("lid", 132, 10), ("face", 1, 140)]
orig = os.path.join(D11, "Plate11.3mf")
same = read_back(orig, [MESH[k].copy().apply_transform(M) for k, M in place(items)])
placedN = place([("board", 8, 10), ("lid", 132, 10), ("faceN", 1, 140)])
res = check(placedN)
res.append((same, "Plate11.3mf rebuilt from its STLs matches the file in the folder (so only the faceplate differs)"))
res.append((write_3mf(os.path.join(D11, "Plate11_WITH-DC-notch.3mf"), placedN), "Plate11_WITH-DC-notch.3mf written and read back"))
report.append(("Plate11_WITH-DC-notch", res))
draw_plate(os.path.join(D11, "Plate11_WITH-DC-notch_layout.png"), placedN, "Plate11_WITH-DC-notch · PETG 0.20 mm · 256 x 256 bed")
shutil.copy2(F["faceN"][0], os.path.join(D11, os.path.basename(F["faceN"][0])))

txt = []
fails = 0
for name, res in report:
    txt.append(f"{name} (PETG, 0.20 mm)")
    for ok, t in res:
        fails += not ok
        txt.append(f"  {'PASS' if ok else 'FAIL'}  {t}")
txt.append(f"\n{sum(len(x) for _, x in report) - fails} PASS, {fails} FAIL")
os.makedirs(os.path.join(D13, "checks"), exist_ok=True)
open(os.path.join(D13, "checks", "plate_layout_check.txt"), "w").write("\n".join(txt) + "\n")
print("\n".join(txt))
