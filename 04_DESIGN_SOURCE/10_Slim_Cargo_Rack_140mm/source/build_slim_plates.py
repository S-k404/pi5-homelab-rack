"""Slim Cargo 140 mm rack: P1S print plates, a plate audit, a filament estimate and an overhang check (28 Oct 2026).

The Slim Cargo rack is an ALTERNATIVE to the standard rack (plates 01-07 in 1_PRINT-NOW), not extra parts. Its seven
plates mirror those seven: 01S..07S replace Plate01..Plate07. Everything else (B1 dock, screen module, Pi unit, UCG mount)
is shared. The ears and clips (shared unit parts) ride on 04S, 06S and 07S exactly as on Plate04/06/07.

Reads the STLs in 01_PRINT_FILES/5_SLIM_CARGO_140mm_TRAVEL_PROTOTYPE (md5 = 04_DESIGN_SOURCE/10_Slim_Cargo_Rack_140mm/
STL_for_printing) and the ear/clip STLs in 01_PRINT_FILES/1_PRINT-NOW. Writes SlimPlate0N.3mf / _layout.png / _SETTINGS.txt
into <print folder>/P1S_plates and 03_CHECKS/VERIFICATION_slim-cargo_plates_28Oct.txt.
Needs numpy, trimesh, scipy, shapely, matplotlib, pillow.
Usage: python build_slim_plates.py <project root>
"""
import hashlib
import math
import os
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
from shapely.geometry import MultiPoint, box

ROOT = os.path.abspath(sys.argv[1])
sys.path.insert(0, os.path.join(ROOT, "04_DESIGN_SOURCE", "1_Rack_9U_T0-look", "source"))
from estimate_filament import grams  # noqa: E402

SLIMD = os.path.join(ROOT, "01_PRINT_FILES", "5_SLIM_CARGO_140mm_TRAVEL_PROTOTYPE")
STD = os.path.join(ROOT, "01_PRINT_FILES", "1_PRINT-NOW")
SRCSTL = os.path.join(ROOT, "04_DESIGN_SOURCE", "10_Slim_Cargo_Rack_140mm", "STL_for_printing")
PLD = os.path.join(SLIMD, "P1S_plates")
CHK = os.path.join(ROOT, "03_CHECKS", "VERIFICATION_slim-cargo_plates_28Oct.txt")
BED, MIN_GAP, MIN_EDGE = 256.0, 4.0, 4.0
PETG = 1.27 / 1.24

# key: (file, folder, qty, walls, infill, label). Walls / infill: the Slim README's (4-5 perimeters, 20-35 % gyroid).
P = {
    "base2u": ("SlimCargo_SideModule_2U_Base_x2.stl", SLIMD, 2, 4, .25, "Side 2U base"),
    "side3u": ("SlimCargo_SideModule_3U_x4.stl", SLIMD, 4, 4, .25, "Side 3U"),
    "top1u": ("SlimCargo_SideModule_1U_Top_x2.stl", SLIMD, 2, 4, .25, "Side 1U top"),
    "cap": ("SlimCargo_CapHalf_x2.stl", SLIMD, 2, 4, .20, "Cap half"),
    "handle": ("SlimCargo_LowProfile_Handle_x2.stl", SLIMD, 2, 5, .35, "Handle"),
    "bar": ("SlimCargo_BaseBar_x3.stl", SLIMD, 3, 5, .30, "Base bar"),
    "ear": ("07_Unit_Ear_3U__x4__PLA.stl", STD, 4, 4, .25, "Unit ear"),
    "clip": ("08_Display7C_Clip__x4__PLA.stl", STD, 4, 4, .30, "Screen clip"),
}
# the standard rack's own settings, for an apples-to-apples weight comparison: (walls, infill) per Slim part
STD_RECIPE = {"base2u": (3, .15), "side3u": (3, .15), "top1u": (3, .15), "cap": (3, .15), "handle": (4, .20), "bar": (3, .15)}
STD_FILES = {"base2u": "01_Rack_SideModule_2U_Base__x2__PLA.stl", "side3u": "02_Rack_SideModule_3U__x4__PLA.stl",
             "top1u": "03_Rack_SideModule_1U_Top__x2__PLA.stl", "cap": "04_Rack_CapHalf__x2__PLA.stl",
             "handle": "05_Rack_Handle__x2__PLA.stl", "bar": "06_Rack_BaseBar__x3__PLA.stl"}

# plates: (id, title, status note, [(key, x, y, rot_z_deg)]); positions are the bounding-box corner after rotating.
# x, y are filled in by lay() below from the measured extents, so the table only says what goes where.
PLATES = [
    ("01", "2U base modules x2", [("base2u",), ("base2u",)], "col"),
    ("02", "3U module + 3 base bars", [("side3u",), ("bar", -45), ("bar", -45), ("bar", -45)], "col"),
    ("03", "3U module + 2 handles (insert test)", [("side3u",), ("handle",), ("handle",)], "col"),
    ("04", "3U module + 2 ears + 4 clips", [("side3u",), ("ear",), ("ear",), ("clip",), ("clip",), ("clip",), ("clip",)], "ears"),
    ("05", "3U module + 2 x 1U top modules", [("side3u",), ("top1u",), ("top1u",)], "col"),
    ("06", "cap half + ear", [("cap",), ("ear",)], "row"),
    ("07", "cap half + ear", [("cap",), ("ear",)], "row"),
]
NEED = {k: v[2] for k, v in P.items()}

md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()


def load(key):
    f, d = P[key][0], P[key][1]
    return trimesh.load(os.path.join(d, f), force="mesh")


def rot_z(m, deg):
    m = m.copy()
    if deg:
        m.apply_transform(trimesh.transformations.rotation_matrix(math.radians(deg), [0, 0, 1], m.centroid))
    return m


def at(m, x, y):
    m = m.copy()
    m.apply_translation([x - m.bounds[0][0], y - m.bounds[0][1], -m.bounds[0][2]])
    return m


def lay(spec, kind):
    """Position the parts of one plate. 'col': stack along y, centred on x. 'row': side by side along x, centred on y.
    'ears': the 3U at the left, the two ears upright beside it, the four clips in a column to their right."""
    meshes = [(s[0], rot_z(load(s[0]), s[1] if len(s) > 1 else 0)) for s in spec]
    ext = [m.extents[:2] for _, m in meshes]
    gap = 6.0
    out = []
    if kind == "col":
        total = sum(e[1] for e in ext) + gap * (len(ext) - 1)
        y = (BED - total) / 2
        for (k, m), e in zip(meshes, ext):
            out.append((k, at(m, (BED - e[0]) / 2, y)))
            y += e[1] + gap
    elif kind == "row":
        total = sum(e[0] for e in ext) + gap * (len(ext) - 1)
        x = (BED - total) / 2
        for (k, m), e in zip(meshes, ext):
            out.append((k, at(m, x, (BED - e[1]) / 2)))
            x += e[0] + gap
    else:   # ears
        x = 8.0
        clip_i = 0
        for (k, m), e in zip(meshes, ext):
            if k == "clip":
                out.append((k, at(m, x, 10.0 + clip_i * (e[1] + 8.0))))
                clip_i += 1
                continue
            out.append((k, at(m, x, 10.0)))
            if k == "side3u":
                x += e[0] + gap
            elif k == "ear":
                x += e[0] + gap
        # clips go right of the last ear: x already advanced past it
    return out


def footprint(m):
    return MultiPoint(m.vertices[:, :2]).convex_hull


def write_3mf(path, title, placed):
    """Plain 3MF core, positions baked in (same writer as build_print_files.py)."""
    objs, items = [], []
    for i, (nm, m) in enumerate(placed, 1):
        vs = "".join(f'<vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>' for x, y, z in m.vertices)
        ts = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in m.faces)
        objs.append(f'<object id="{i}" name={quoteattr(nm)} type="model"><mesh><vertices>{vs}</vertices>'
                    f'<triangles>{ts}</triangles></mesh></object>')
        items.append(f'<item objectid="{i}"/>')
    model = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
             f'<metadata name="Title">{title}</metadata><resources>{"".join(objs)}</resources>'
             f'<build>{"".join(items)}</build></model>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                   '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr("3D/3dmodel.model", model)


def read_3mf(path):
    NS = "{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}"
    x = ET.fromstring(zipfile.ZipFile(path).read("3D/3dmodel.model"))
    objs = {}
    for o in x.iter(NS + "object"):
        vs = o.find(f".//{NS}vertices")
        if vs is None:
            continue
        V = np.array([[float(v.get(a)) for a in "xyz"] for v in vs])
        F = np.array([[int(t.get(a)) for a in ("v1", "v2", "v3")] for t in o.find(f".//{NS}triangles")])
        objs[o.get("id")] = (o.get("name"), trimesh.Trimesh(V, F, process=False))
    return [objs[it.get("objectid")] for it in x.iter(NS + "item")]


def layout_png(path, title, placed):
    fig, ax = plt.subplots(figsize=(6, 6.4))
    ax.add_patch(plt.Rectangle((0, 0), BED, BED, fill=False, lw=1.5))
    cols = ["#4C78A8", "#F58518", "#54A24B", "#B279A2", "#E45756"]
    for i, (nm, m) in enumerate(placed):
        tri = m.vertices[m.faces][:, :, :2]
        down = m.face_normals[:, 2] < -0.5
        ax.add_collection(PolyCollection(tri[down] if down.any() else tri, facecolor=cols[i % 5], edgecolor="none", alpha=.85))
        lo, hi = m.bounds
        ax.text((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, nm, ha="center", va="center", fontsize=6.5)
    ax.set_xlim(-5, BED + 5); ax.set_ylim(-5, BED + 5); ax.set_aspect("equal")
    ax.set_title(title, fontsize=8); fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)


def overhang(m, thr=math.sin(math.radians(45))):
    """Area of faces that point down steeper than 45 deg from vertical and aren't on the bed."""
    n, a = m.face_normals, m.area_faces
    off = m.triangles[:, :, 2].min(1) > 0.05
    flat = (n[:, 2] < -0.99) & off
    steep = (n[:, 2] < -thr) & (n[:, 2] >= -0.99) & off
    return a[flat].sum(), a[steep].sum(), m.area


os.makedirs(PLD, exist_ok=True)
log, fails = [], 0


def check(ok, text):
    global fails
    fails += not ok
    log.append(f"{'PASS' if ok else 'FAIL'}  {text}")


# ---- 1. parts: md5 against the exported source, watertight, one body, on the bed, filament ------------------------------
meshes, ref, gram = {}, {}, {}
log += ["1. The parts, measured from the STLs in the print folder", ""]
for k, (f, d, q, w, inf, label) in P.items():
    p = os.path.join(d, f)
    m = trimesh.load(p, force="mesh")
    meshes[k] = m
    ref[k] = abs(m.volume)
    gram[k] = grams(p, w, inf) * PETG
    e = m.extents
    if d == SLIMD:
        check(md5(p) == md5(os.path.join(SRCSTL, f)), f"{f}: byte-identical to 10_Slim_Cargo_Rack_140mm/STL_for_printing")
    check(m.is_watertight and len(m.split(only_watertight=False)) == 1 and abs(m.bounds[0][2]) < 1e-3,
          f"{f}: 1 body, watertight, sits on z=0; {e[0]:.1f} x {e[1]:.1f} x {e[2]:.1f} mm")

# ---- 2. plates -------------------------------------------------------------------------------------------------------
log += ["", "2. The plates (Bambu P1S, 256 x 256): written, then read back from the 3MF", ""]
PETG_SET = ("Settings (Bambu P1S): 0.20mm Standard @BBL P1S, Generic PETG, 4 walls, 25% gyroid, supports OFF (see Notes),\n"
            "Textured PEI no glue, enclosure CLOSED.\n")
plate_g, counts, summary = {}, {k: 0 for k in P}, []
for pid, title, spec, kind in PLATES:
    placed = lay(spec, kind)
    names = {k: P[k][5] for k in P}
    # check before writing: inside the bed, no two parts closer than MIN_GAP
    fps = [footprint(m) for _, m in placed]
    inside = all(box(MIN_EDGE, MIN_EDGE, BED - MIN_EDGE, BED - MIN_EDGE).contains(fp) for fp in fps)
    gaps = [fps[i].distance(fps[j]) for i in range(len(fps)) for j in range(i + 1, len(fps))]
    tag = f"SlimPlate{pid}"
    name3 = [(names[k], m) for k, m in placed]
    write_3mf(os.path.join(PLD, tag + ".3mf"), tag, name3)
    layout_png(os.path.join(PLD, tag + "_layout.png"), f"Slim Cargo plate {pid}S (PETG): {title}", name3)
    # read back and identify every object by volume
    items = read_3mf(os.path.join(PLD, tag + ".3mf"))
    lo = np.min([m.bounds[0] for _, m in items], 0)
    hi = np.max([m.bounds[1] for _, m in items], 0)
    found = []
    for _, m in items:
        v = abs(m.volume)
        k = min(ref, key=lambda r: abs(ref[r] - v))
        found.append(k if abs(ref[k] - v) <= max(2.0, 0.003 * v) else f"UNKNOWN {v:.0f} mm3")
    want = sorted(s[0] for s in spec)
    for k in found:
        if k in counts:
            counts[k] += 1
    check(inside and (not gaps or min(gaps) >= MIN_GAP) and sorted(found) == want and abs(lo[2]) < 0.05,
          f"{tag}.3mf: {len(items)} part(s), x {lo[0]:.1f}..{hi[0]:.1f}, y {lo[1]:.1f}..{hi[1]:.1f}, tallest {hi[2]:.1f} mm, "
          f"closest parts {min(gaps) if gaps else float('nan'):.1f} mm  ->  " + ", ".join(found))
    g = sum(gram[s[0]] for s in spec)
    plate_g[pid] = g
    summary.append((pid, title, spec, g, hi[2]))

log += ["", "Totals across the plates vs what the rack needs (Slim parts x qty; ears and clips as for the standard rack):"]
for k, (f, d, q, w, inf, label) in P.items():
    check(counts[k] == q, f"{f}: {counts[k]} on the plates, {q} needed")

# ---- 3. overhangs ----------------------------------------------------------------------------------------------------
log += ["", "3. Overhangs (faces pointing down steeper than 45 deg from vertical, not on the bed)",
        "   The Slim README said 'Supports: NONE required (all overhangs <= 45 deg)'. They are not all <= 45 deg:", ""]
for k in ("base2u", "side3u", "top1u", "cap", "handle", "bar"):
    fl, st, tot = overhang(meshes[k])
    sm = trimesh.load(os.path.join(STD, STD_FILES[k]), force="mesh")
    sfl, sst, stot = overhang(sm)
    log.append(f"   {P[k][0]:36s} flat ceilings {fl:6.0f} mm2, sloped {st:6.0f} mm2 ({100 * (fl + st) / tot:.1f}% of the surface)"
               f"   | standard rack's part: {sfl:6.0f} + {sst:6.0f} mm2 ({100 * (sfl + sst) / stot:.1f}%)")
log += ["   The Slim modules have the same joint bosses / key slots as the standard rack's, so the same small overhangs.",
        "   The standard rack is planned with supports OFF; the Slim plates say the same. Nothing was test-printed for either."]

# ---- 4. filament -----------------------------------------------------------------------------------------------------
log += ["", "4. Filament (slicer-like estimate, 0.2 mm layers; PETG = PLA grams x 1.27 / 1.24)", ""]
tot_petg = sum(gram[k] * P[k][2] for k in P if k not in ("ear", "clip"))
tot_pla = tot_petg / PETG
std_g = {k: grams(os.path.join(STD, STD_FILES[k]), *STD_RECIPE[k]) for k in STD_FILES}
tot_std = sum(std_g[k] * P[k][2] for k in std_g)
same = {k: grams(os.path.join(SLIMD, P[k][0]), *STD_RECIPE[k]) for k in STD_FILES}
tot_same = sum(same[k] * P[k][2] for k in same)
for k in ("base2u", "side3u", "top1u", "cap", "handle", "bar", "ear", "clip"):
    f, d, q, w, inf, label = P[k]
    log.append(f"   {f:36s} {w} walls {inf:.0%}: {gram[k]:6.1f} g PETG each x {q} = {gram[k] * q:6.1f} g")
shared = sum(gram[k] * P[k][2] for k in ("ear", "clip"))
log += ["", f"   Slim frame (6 files): {tot_petg:.0f} g PETG  (= {tot_pla:.0f} g if printed in PLA); plus the shared ears + clips {shared:.0f} g",
        f"   Standard frame (01-06, 3 walls / 15 %, PLA): {tot_std:.0f} g",
        f"   Slim parts at the STANDARD's settings (3 walls / 15 %, PLA): {tot_same:.0f} g  -> the Slim frame is "
        f"{100 * (tot_same / tot_std - 1):+.0f}% vs the standard at equal settings, {100 * (tot_pla / tot_std - 1):+.0f}% at the README's settings",
        "   Frame only: no Pi, UPS, brick, screen, dock or gateway, no screws."]

log += ["", f"FAILS: {fails}"]
open(CHK, "w").write("Slim Cargo 140 mm: print plates, overhangs and filament (28 Oct 2026)\n"
                      "Made by 04_DESIGN_SOURCE/10_Slim_Cargo_Rack_140mm/source/build_slim_plates.py. Nothing here has been printed.\n\n"
                      + "\n".join(log) + "\n")

# ---- 5. SETTINGS per plate ---------------------------------------------------------------------------------------------
OVR = {"cap": "Cap half: right-click > Sparse infill 20%.",
       "handle": "Handles: right-click each > Wall loops 5, Sparse infill 35%.",
       "bar": "Base bars: right-click each > Wall loops 5, Sparse infill 30%.",
       "clip": "Clips: right-click each > Sparse infill 30%."}
for pid, title, spec, g, tall in summary:
    keys = sorted(set(s[0] for s in spec))
    notes = [OVR[k] for k in keys if k in OVR]
    if any(k in keys for k in ("side3u", "top1u", "base2u", "cap", "handle", "bar", "ear", "clip")):
        notes.insert(0, "Supports OFF: the joint bosses and key slots have small overhangs, the same as the standard rack's modules\n"
                        "  (Slim check: 03_CHECKS/VERIFICATION_slim-cargo_plates_28Oct.txt). If a boss looks ragged, turn on tree supports\n"
                        "  for that plate only.")
    if "bar" in keys:
        notes.append("The bars are 223 mm long and lie straight on this plate. The loose SlimCargo_BaseBar_x3.stl is saved at 45 deg\n"
                     "  so it fits a 220 mm bed; on the P1S use this 3MF.")
    if pid == "03":
        notes.append("This is the Slim rack's insert-test plate (like Plate03 of the standard rack): when it's done, heat-set one M5 insert\n"
                     "  into a rail hole and one into a joint boss (6.4 mm x 10 mm deep). Loose or bulging: stop, the hole size needs changing.")
    on = "\n".join(f"  - {P[k][5]} x{sum(1 for s in spec if s[0] == k)}   ({P[k][0]})"
                   + ("  <- shared with the standard rack's units" if k in ("ear", "clip") else "") for k in keys)
    txt = (f"SlimPlate{pid} (PETG): {title}\n" + "=" * (len(f"SlimPlate{pid} (PETG): {title}")) + "\n"
           "Status: ALTERNATIVE rack. Print the Slim plates 01S-07S INSTEAD of Plate01-07 of the standard rack, not as well.\n"
           "It's not in the Robu order. The 12 V brick cradle (plate 13) does not fit this rack: see ../README.md.\n"
           f"Material: PETG, about {g:.0f} g  (the Slim README lists PETG / ABS / ASA; ABS / ASA need the enclosure closed too)\n\n"
           "How: double-click the .3mf (or File > Open Project in Bambu Studio). Every part is already placed.\n"
           "If Bambu Studio asks, choose to load the geometry only. Then pick the settings below and Slice.\n\n"
           + PETG_SET + ("\nNotes:\n  " + "\n  ".join(notes) + "\n" if notes else "") +
           f"\nOn this plate:\n{on}\n"
           "Hardware for the whole rack: 48 x M5 x 12 button head + 48 M5 heat-set inserts (the same as the standard rack).\n")
    open(os.path.join(PLD, f"SlimPlate{pid}_SETTINGS.txt"), "w").write(txt)

print("\n".join(log))
print()
for pid, title, spec, g, tall in summary:
    print(f"plate {pid}S  {g:6.0f} g PETG  tallest {tall:5.1f} mm  {title}")
