"""Build FINAL_PRINTS_2026-10-28: the one print set for the chosen build
(v7.2 rack + B1 dock v5 + Display7C + Argon Poly+ 5 tray (11B) + Waveshare F holder + DC-notch faceplate
+ Printables 942972 UCG mount (12-ALT2) + 12 V brick cradle (plate 13)).

Copies the checked STLs (by md5 against the sources), writes the two new plate 3MFs, a layout PNG for each new plate,
measures every part and audits every 3MF in the folder.
Usage: python build_final.py <project root> <rework-01 v7.2 bundle> <dest folder>
"""
import hashlib
import math
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

ROOT, RB, DEST = sys.argv[1:4]
sys.path.insert(0, os.path.join(RB, "1_Rack_9U_T0-look", "source"))
from estimate_filament import grams  # noqa: E402

PT = os.path.join(ROOT, "PRINT_THIS")
ALT = os.path.join(PT, "_superseded_and_alternatives", "alternatives_and_notes")
ARG = os.path.join(ALT, "ALT_Pi-unit_Argon-cases+coolers")
A2 = os.path.join(ALT, "ALT_Geerling-list_ready-made-prints", "12-ALT2_PETG_UCG-Ultra-1U-3-keystones_Printables-942972")
P11S = os.path.join(PT, "_superseded_and_alternatives", "plate11_superseded")
BED = 256.0
PETG = 1.27 / 1.24

# (dest name, source, qty, material, walls, infill, status, where it goes, expected md5 prefix)
PARTS = [
    ("01_Rack_SideModule_2U_Base__x2__PLA.stl", f"{PT}/01_PLA_side-modules-2U-base/Rack_SideModule_2U_Base_x2.stl", 2, "PLA", 3, .15, "now", "rack: bottom side modules (L + R)", "334ce544"),
    ("02_Rack_SideModule_3U__x4__PLA.stl", f"{PT}/02_PLA_3U-module+base-bars/Rack_SideModule_3U_x4.stl", 4, "PLA", 3, .15, "now", "rack: 3U side modules (2 per side)", "e2c8198e"),
    ("03_Rack_SideModule_1U_Top__x2__PLA.stl", f"{PT}/05_PLA_3U-module+1U-tops/Rack_SideModule_1U_Top_x2.stl", 2, "PLA", 3, .15, "now", "rack: 1U top side modules", "081c5f69"),
    ("04_Rack_CapHalf__x2__PLA.stl", f"{PT}/06_PLA_cap-half+ear/Rack_CapHalf_x2.stl", 2, "PLA", 3, .15, "now", "rack: vented cap (2 halves)", "712bf088"),
    ("05_Rack_Handle__x2__PLA.stl", f"{PT}/03_PLA_PRINT-FIRST_3U-module+handles/Rack_Handle_x2.stl", 2, "PLA", 4, .20, "now", "rack: U handles on the cap", "6d730c77"),
    ("06_Rack_BaseBar__x3__PLA.stl", f"{PT}/02_PLA_3U-module+base-bars/Rack_BaseBar_x3.stl", 3, "PLA", 3, .15, "now", "rack: base tie bars (front, middle, rear)", "6b994028"),
    ("07_Unit_Ear_3U__x4__PLA.stl", f"{PT}/04_PLA_3U-module+ears+clips/B1_Dock_3U_Ear_x2.stl", 4, "PLA", 3, .15, "now", "ears: 2 for the B1 dock + 2 for the screen module", "ee7076f1"),
    ("08_Display7C_Clip__x4__PLA.stl", f"{PT}/04_PLA_3U-module+ears+clips/Display7C_Clip_x4.stl", 4, "PLA", 3, .30, "now", "screen module: corner clips", "42d40f6d"),
    ("09_B1_Dock_v5_Body__x1__PLA.stl", f"{PT}/08_PLA_B1-dock/B1_Dock_3U_Body.stl", 1, "PLA", 3, .15, "now", "B1 dock v5 (real B1 132 x 91 x 62)", "961c71e0"),
    ("10_Pi_Rack_Shelf_pinned__x1__PETG.stl", f"{PT}/10_PETG_Pi-shelf+UPS-tray+shims/Rack_Shelf_pinned.stl", 1, "PETG", 3, .20, "now", "Pi unit: shelf on the rack base", "9250148d"),
    ("11_Pi_UPS_Tray_pinned__x1__PETG.stl", f"{PT}/10_PETG_Pi-shelf+UPS-tray+shims/Pi5_UPS_v3_ups_tray_pinned.stl", 1, "PETG", 3, .20, "now", "Pi unit: Cuzor UPS tray (bottom)", "b181d5d6"),
    ("12_Pi_Faceplate_2U_DC-notch__x1__PETG.stl", f"{P11S}/Rack_Faceplate_2U_10in_DC-notch.stl", 1, "PETG", 3, .20, "now", "Pi unit: 2U faceplate with the notch for the 12 V brick lead", "f1dcfac4"),
    ("13_Brick_Cradle_12V__x1__PETG.stl", f"{PT}/13_PETG_12V-brick-cradle/Brick_Cradle_12V.stl", 1, "PETG", 3, .20, "now", "12 V brick cradle, bay right of the Pi unit", "cc0e1ff4"),
    ("14_Brick_Spacer_8mm__x1__PETG.stl", f"{PT}/13_PETG_12V-brick-cradle/Brick_Spacer_8mm.stl", 1, "PETG", 3, .20, "now", "spacer for a 29-30.5 mm thick brick (Robu's 30 mm)", "d80bd582"),
    ("15_UCG-Ultra_1U_Mount_Printables-942972__x1__PETG.stl", f"{A2}/UCG-Ultra_1U_3-keystones_Printables-942972.stl", 1, "PETG", 3, .15, "now", "UCG-Ultra 1U mount, 3 keystones (ready-made, trimmed 0.8 mm)", "218ddda4"),
    ("W1_Argon_Poly5_Tray__x1__PETG__WAIT-measure-case.stl", f"{ARG}/11B_PETG_Argon-Poly+5-tray+faceplate_WAIT-measure-case/Pi5_ArgonPoly5_tray.stl", 1, "PETG", 3, .20, "wait", "Pi unit: tray for the Poly+ 5 (takes a case up to 96.0 x 66.5)", "8882606c"),
    ("W2_Display7C_3U_Body__x1__PLA__WAIT-measure-screen.stl", f"{PT}/09_PLA_screen-module_WAIT-measure-screen-first/Display7C_3U_Body.stl", 1, "PLA", 3, .15, "wait", "7in screen module body", "f89567e4"),
    ("W3_Waveshare_F_Holder_Base__x1__PETG__WAIT-test-fit.stl", f"{ARG}/11B-SIDE_PETG_Waveshare-F-holder_beside-Poly+5/Waveshare_F_holder_base.stl", 1, "PETG", 3, .20, "wait", "adapter (F) holder base: only if the adapter plugs into the Pi through the case", "65f45876"),
    ("W4_Waveshare_F_Holder_Lid__x1__PETG__WAIT-test-fit.stl", f"{ARG}/11B-SIDE_PETG_Waveshare-F-holder_beside-Poly+5/Waveshare_F_holder_lid.stl", 1, "PETG", 3, .20, "wait", "adapter (F) holder lid", "982fa284"),
    ("O1_Brick_Spacer_6mm__x1__PETG__only-if-brick-30.5-32.5mm.stl", f"{PT}/13_PETG_12V-brick-cradle/Brick_Spacer_6mm.stl", 1, "PETG", 3, .20, "opt", "spacer for a 30.5-32.5 mm brick", "e7fa68d9"),
    ("O2_Brick_Spacer_4mm__x1__PETG__only-if-brick-32.5-34.5mm.stl", f"{PT}/13_PETG_12V-brick-cradle/Brick_Spacer_4mm.stl", 1, "PETG", 3, .20, "opt", "spacer for a 32.5-34.5 mm brick", "a193c01e"),
    ("O3_Brick_Spacer_2mm__x1__PETG__only-if-brick-34.5-36.5mm.stl", f"{PT}/13_PETG_12V-brick-cradle/Brick_Spacer_2mm.stl", 1, "PETG", 3, .20, "opt", "spacer for a 34.5-36.5 mm brick", "2e86a9bb"),
]
FOLDER = {"now": "1_ORDER-NOW", "wait": "2_WAIT_measure-first", "opt": "3_OPTIONAL"}


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def write_3mf(path, title, placed):
    """placed: [(name, trimesh in plate coords)]. Plain 3MF core, positions baked in (as the other plates)."""
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
    out = []
    for it in x.iter(NS + "item"):
        nm, m = objs[it.get("objectid")]
        m = m.copy()
        if it.get("transform"):
            T = np.eye(4)
            T[:3, :4] = np.array([float(v) for v in it.get("transform").split()]).reshape(4, 3).T
            m.apply_transform(T)
        out.append((nm, m))
    return out


def layout_png(path, title, placed):
    fig, ax = plt.subplots(figsize=(6, 6.4))
    ax.add_patch(plt.Rectangle((0, 0), BED, BED, fill=False, lw=1.5))
    cols = ["#4C78A8", "#F58518", "#54A24B", "#B279A2", "#E45756"]
    for i, (nm, m) in enumerate(placed):
        tri = m.vertices[m.faces][:, :, :2]
        down = m.face_normals[:, 2] < -0.5
        ax.add_collection(PolyCollection(tri[down] if down.any() else tri, facecolor=cols[i % 5], edgecolor="none", alpha=.85))
        lo, hi = m.bounds
        ax.text((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, nm.replace("__", "\n"), ha="center", va="center", fontsize=6.5)
    ax.set_xlim(-5, BED + 5); ax.set_ylim(-5, BED + 5); ax.set_aspect("equal")
    ax.set_title(title, fontsize=9); fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)


def place(m, x, y, rot=0):
    m = m.copy()
    if rot:
        a = math.radians(rot)
        R = np.eye(4); R[:2, :2] = [[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]]
        m.apply_transform(R)
    m.apply_translation([x - m.bounds[0][0], y - m.bounds[0][1], -m.bounds[0][2]])
    return m


if os.path.exists(DEST):
    sys.exit(f"{DEST} exists: refusing to overwrite")
for d in list(FOLDER.values()) + ["4_P1S_plates_3MF", "checks", "source"]:
    os.makedirs(os.path.join(DEST, d))

# ---- 1. copy STLs, md5-checked ------------------------------------------------------------------------------
meas = ["| File | Qty | Mat | Measured size on the bed (mm) | Solid | ≈ g each | Bed fit | md5 = checked source |",
        "|---|---|---|---|---|---|---|---|"]
fails = 0
ref = {}
gtot = {"PLA": {"now": 0, "wait": 0, "opt": 0}, "PETG": {"now": 0, "wait": 0, "opt": 0}}
for name, src, q, mat, walls, inf, st, where, h in PARTS:
    dst = os.path.join(DEST, FOLDER[st], name)
    shutil.copy2(src, dst)
    ok_hash = md5(dst).startswith(h)
    m = trimesh.load(dst, force="mesh")
    nb = len(m.split(only_watertight=False))
    e = m.extents
    fits = max(e[0], e[1]) <= BED - 2 or math.hypot(e[0], e[1]) <= BED * math.sqrt(2) - 4  # 45 deg plates
    g = grams(dst, walls, inf) * (PETG if mat == "PETG" else 1.0)
    gtot[mat][st] += g * q
    ref[name] = abs(m.volume)
    good = ok_hash and m.is_watertight and nb == 1 and abs(m.bounds[0][2]) < 1e-6 and fits
    fails += not good
    meas.append(f"| `{name}` | {q} | {mat} | {e[0]:.1f} × {e[1]:.1f} × {e[2]:.1f} | {'1 body, watertight' if (m.is_watertight and nb == 1) else f'{nb} bodies!'} "
                f"| {g:.0f} | {'yes' if fits else 'NO'} | {'yes' if ok_hash else 'NO: ' + md5(dst)[:8]} |")

# ---- 2. plates for the P1S -----------------------------------------------------------------------------------
PL = os.path.join(DEST, "4_P1S_plates_3MF")
copy_plates = [("01_PLA", f"{PT}/01_PLA_side-modules-2U-base", "Plate01"), ("02_PLA", f"{PT}/02_PLA_3U-module+base-bars", "Plate02"),
               ("03_PLA_PRINT-FIRST", f"{PT}/03_PLA_PRINT-FIRST_3U-module+handles", "Plate03"),
               ("04_PLA", f"{PT}/04_PLA_3U-module+ears+clips", "Plate04"), ("05_PLA", f"{PT}/05_PLA_3U-module+1U-tops", "Plate05"),
               ("06_PLA", f"{PT}/06_PLA_cap-half+ear", "Plate06"), ("07_PLA", f"{PT}/07_PLA_cap-half+ear", "Plate07"),
               ("08_PLA", f"{PT}/08_PLA_B1-dock", "Plate08"), ("09_PLA_WAIT", f"{PT}/09_PLA_screen-module_WAIT-measure-screen-first", "Plate09"),
               ("12-ALT2_PETG", A2, "Plate12-ALT2"), ("13_PETG", f"{PT}/13_PETG_12V-brick-cradle", "Plate13")]
for tag, folder, stem in copy_plates:
    shutil.copy2(os.path.join(folder, stem + ".3mf"), os.path.join(PL, f"{stem}.3mf"))
    shutil.copy2(os.path.join(folder, stem + "_layout.png"), os.path.join(PL, f"{stem}_layout.png"))
    shutil.copy2(os.path.join(folder, "SETTINGS.txt"), os.path.join(PL, f"{stem}_SETTINGS.txt"))

# plate 10 without the shims (they were for the adapter in the v3 board tray; the F holder doesn't use them)
p10 = [(n, m) for n, m in read_3mf(f"{PT}/10_PETG_Pi-shelf+UPS-tray+shims/Plate10.3mf") if "shims" not in n]
write_3mf(os.path.join(PL, "Plate10.3mf"), "Plate10", p10)
layout_png(os.path.join(PL, "Plate10_layout.png"), "Plate 10 (PETG): Pi shelf + UPS tray (no shims)", p10)

byname = {p[0]: os.path.join(DEST, FOLDER[p[6]], p[0]) for p in PARTS}
ld = lambda pre: trimesh.load(next(v for k, v in byname.items() if k.startswith(pre)), force="mesh")
fp, hb, hl, pt = ld("12_Pi_Faceplate"), ld("W3_"), ld("W4_"), ld("W1_")
p11 = [("Faceplate_2U_DC-notch", place(fp, (BED - fp.extents[0]) / 2, (BED - fp.extents[1]) / 2))]
write_3mf(os.path.join(PL, "Plate11.3mf"), "Plate11", p11)
layout_png(os.path.join(PL, "Plate11_layout.png"), "Plate 11 (PETG, brim OFF): DC-notch faceplate", p11)
p11w = [("Argon_Poly5_tray", place(pt, 6.0, (BED - pt.extents[1]) / 2)),
        ("F_holder_base", place(hb, 6.0 + pt.extents[0] + 6.0, (BED - hb.extents[1]) / 2)),
        ("F_holder_lid", place(hl, 6.0 + pt.extents[0] + 6.0 + hb.extents[0] + 6.0, (BED - hl.extents[1]) / 2))]
write_3mf(os.path.join(PL, "Plate11W_WAIT.3mf"), "Plate11W", p11w)
layout_png(os.path.join(PL, "Plate11W_WAIT_layout.png"), "Plate 11W (PETG) WAIT: Poly+ 5 tray (measure case) + F holder (test fit)", p11w)

# ---- 3. audit every 3MF in the plates folder ---------------------------------------------------------------------
aud = []
counts = {}
for f in sorted(os.listdir(PL)):
    if not f.endswith(".3mf"):
        continue
    items = read_3mf(os.path.join(PL, f))
    lo = np.min([m.bounds[0] for _, m in items], 0); hi = np.max([m.bounds[1] for _, m in items], 0)
    on = lo[0] >= -0.01 and lo[1] >= -0.01 and hi[0] <= BED + 0.01 and hi[1] <= BED + 0.01 and abs(lo[2]) < 0.05
    names = []
    for _, m in items:
        v = abs(m.volume)
        k = min(ref, key=lambda r: abs(ref[r] - v))
        hit = abs(ref[k] - v) <= max(2.0, 0.003 * v)
        names.append(k if hit else f"UNKNOWN {v:.0f} mm3")
        counts[k] = counts.get(k, 0) + 1
    fails += (not on) or any(n.startswith("UNKNOWN") for n in names)
    aud.append(f"{'PASS' if on else 'FAIL'}  {f}: {len(items)} part(s), x {lo[0]:.1f}..{hi[0]:.1f}, y {lo[1]:.1f}..{hi[1]:.1f}, "
               f"tallest {hi[2]:.1f} mm  ->  " + ", ".join(names))
aud.append("")
aud.append("Totals across all plates vs the parts list (3MF count / parts-list qty):")
for p in PARTS:
    name, q, st = p[0], p[2], p[6]
    c = counts.get(name, 0)
    want = q if st != "opt" else 1
    ok = c == want
    fails += not ok
    aud.append(f"{'PASS' if ok else 'FAIL'}  {name}: {c} on the plates, {want} needed")

open(os.path.join(DEST, "checks", "MEASUREMENTS_every_part.md"), "w").write(
    "# Every final part, measured from the STL in this folder (28 Oct 2026)\n\n"
    "≈ g = slicer-like estimate (0.2 mm layers; rack/dock/screen PLA 3 walls 15 %, handles 4 walls 20 %, clips 30 %, "
    "PETG parts 3 walls 20 %, UCG mount 15 %). 'md5 = checked source' means the file is byte-identical to the one the checks ran on.\n\n"
    + "\n".join(meas) + "\n\n"
    + "| Totals | PLA ≈ g | PETG ≈ g |\n|---|---|---|\n"
    + f"| Order now | {gtot['PLA']['now']:.0f} | {gtot['PETG']['now']:.0f} |\n"
    + f"| Wait (Poly+ 5 tray, screen body) | {gtot['PLA']['wait']:.0f} | {gtot['PETG']['wait']:.0f} |\n"
    + f"| Optional spare spacers | {gtot['PLA']['opt']:.0f} | {gtot['PETG']['opt']:.0f} |\n")
open(os.path.join(DEST, "checks", "PLATES_3MF_audit.txt"), "w").write(
    "3MF plate audit (read back from the files): every part on the 256 x 256 bed, identified by volume\n\n" + "\n".join(aud) + "\n")
shutil.copy2(__file__, os.path.join(DEST, "source", os.path.basename(__file__)))
print("\n".join(meas)); print(); print("\n".join(aud)); print()
print({k: {s: round(v) for s, v in d.items()} for k, d in gtot.items()})
print(f"FAILS: {fails}")
