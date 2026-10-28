"""Build PRINT_FILES_FINAL: every print file for the chosen build in one folder, sorted by what you can do with it.
Build (28 Oct 2026): v7.2 rack + B1 dock v5 + Display7C + Argon Poly+ 5 tray + Waveshare adapter (F) holder
+ faceplate + Printables 942972 UCG mount (12-ALT2) + 12 V brick cradle (plate 13).
28 Oct (ultrareview): the clean front. The shelf (10) has an arch in its right gusset for the brick's 12 V lead, and the
faceplate (C2) has no DC-IN window and no notch: the lead stays behind it (04_DESIGN_SOURCE/4_Pi_Unit_2U/source/brick_lead_route.py).

  1_PRINT-NOW/            STLs + P1S plates you can order / print today
  2_CHECK-UPS-FIRST/      UPS tray + faceplate: check the real Cuzor's jack positions first
  3_WAIT/                 Poly+ 5 tray (measure the case), adapter (F) holder (fit test), screen body (4 Nov)
  4_OPTIONAL_spare-spacers/
Each status folder: the STLs (one part per file, qty in the name) and P1S_plates/ (3MF + layout + SETTINGS).

Copies the checked STLs (md5 against the sources), writes the new plates, measures every part, audits every 3MF.
Usage: python build_print_files.py <project root> <rework-01 v7.2 bundle> <dest folder>
It reads the checked sources from the retired PRINT_THIS (_Old_versions/2026-10-28_retired/PRINT_THIS) and writes <dest>/checks and
<dest>/source: move those into 03_CHECKS / 04_DESIGN_SOURCE/9_scripts_28Oct, as the project layout keeps them there.
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

PT = next(p for p in (os.path.join(ROOT, "PRINT_THIS"), os.path.join(ROOT, "_Old_versions", "2026-10-28_retired", "PRINT_THIS")) if os.path.isdir(p))
ALT = os.path.join(PT, "_superseded_and_alternatives", "alternatives_and_notes")
ARG = os.path.join(ALT, "ALT_Pi-unit_Argon-cases+coolers")
A2 = os.path.join(ALT, "ALT_Geerling-list_ready-made-prints", "12-ALT2_PETG_UCG-Ultra-1U-3-keystones_Printables-942972")
P11S = os.path.join(PT, "_superseded_and_alternatives", "plate11_superseded")
# 28 Oct (ultrareview): the adapter (F) holder comes from 04_DESIGN_SOURCE (its rear wall got an HDMI plug relief)
HOLDER = os.path.join(ROOT, "04_DESIGN_SOURCE", "7_Argon_Poly5_tray+Waveshare_F_holder", "11B-SIDE_PETG_Waveshare-F-holder_beside-Poly+5")
PIU = os.path.join(ROOT, "04_DESIGN_SOURCE", "4_Pi_Unit_2U", "STL_for_printing")      # 28 Oct: shelf with the gusset arch, clean faceplate
BED = 256.0
PETG = 1.27 / 1.24

# (dest name, source, qty, material, walls, infill, status, where it goes, expected md5 prefix)
PARTS = [
    ("01_Rack_SideModule_2U_Base__x2__PLA.stl", f"{PT}/01_PLA_side-modules-2U-base/Rack_SideModule_2U_Base_x2.stl", 2, "PLA", 3, .15, "now", "rack: bottom side modules", "334ce544"),
    ("02_Rack_SideModule_3U__x4__PLA.stl", f"{PT}/02_PLA_3U-module+base-bars/Rack_SideModule_3U_x4.stl", 4, "PLA", 3, .15, "now", "rack: 3U side modules", "e2c8198e"),
    ("03_Rack_SideModule_1U_Top__x2__PLA.stl", f"{PT}/05_PLA_3U-module+1U-tops/Rack_SideModule_1U_Top_x2.stl", 2, "PLA", 3, .15, "now", "rack: 1U top side modules", "081c5f69"),
    ("04_Rack_CapHalf__x2__PLA.stl", f"{PT}/06_PLA_cap-half+ear/Rack_CapHalf_x2.stl", 2, "PLA", 3, .15, "now", "rack: vented cap halves", "712bf088"),
    ("05_Rack_Handle__x2__PLA.stl", f"{PT}/03_PLA_PRINT-FIRST_3U-module+handles/Rack_Handle_x2.stl", 2, "PLA", 4, .20, "now", "rack: U handles", "6d730c77"),
    ("06_Rack_BaseBar__x3__PLA.stl", f"{PT}/02_PLA_3U-module+base-bars/Rack_BaseBar_x3.stl", 3, "PLA", 3, .15, "now", "rack: base bars", "6b994028"),
    ("07_Unit_Ear_3U__x4__PLA.stl", f"{PT}/04_PLA_3U-module+ears+clips/B1_Dock_3U_Ear_x2.stl", 4, "PLA", 3, .15, "now", "ears: 2 for the dock + 2 for the screen module", "ee7076f1"),
    ("08_Display7C_Clip__x4__PLA.stl", f"{PT}/04_PLA_3U-module+ears+clips/Display7C_Clip_x4.stl", 4, "PLA", 3, .30, "now", "screen-module corner clips", "42d40f6d"),
    ("09_B1_Dock_v5_Body__x1__PLA.stl", f"{PT}/08_PLA_B1-dock/B1_Dock_3U_Body.stl", 1, "PLA", 3, .15, "now", "B1 dock v5 (real B1 132 x 91 x 62)", "961c71e0"),
    ("10_Pi_Rack_Shelf_pinned__x1__PETG.stl", f"{PIU}/Rack_Shelf_pinned.stl", 1, "PETG", 3, .20, "now", "Pi unit: shelf (gusset arch for the 12 V lead)", "8f1b7825"),
    ("11_Brick_Cradle_12V__x1__PETG.stl", f"{PT}/13_PETG_12V-brick-cradle/Brick_Cradle_12V.stl", 1, "PETG", 3, .20, "now", "12 V brick cradle, bay beside the Pi unit", "cc0e1ff4"),
    ("12_Brick_Spacer_8mm__x1__PETG.stl", f"{PT}/13_PETG_12V-brick-cradle/Brick_Spacer_8mm.stl", 1, "PETG", 3, .20, "now", "spacer for Robu's 30 mm thick brick", "d80bd582"),
    ("13_UCG-Ultra_1U_Mount_Printables-942972__x1__PETG.stl", f"{A2}/UCG-Ultra_1U_3-keystones_Printables-942972.stl", 1, "PETG", 3, .15, "now", "UCG-Ultra 1U mount, 3 keystones (ready-made, trimmed 0.8 mm)", "218ddda4"),
    ("C1_Pi_UPS_Tray_pinned__x1__PETG__CHECK-UPS-jacks.stl", f"{PT}/10_PETG_Pi-shelf+UPS-tray+shims/Pi5_UPS_v3_ups_tray_pinned.stl", 1, "PETG", 3, .20, "check", "Pi unit: Cuzor UPS tray", "b181d5d6"),
    ("C2_Pi_Faceplate_2U_clean__x1__PETG.stl", f"{PIU}/Rack_Faceplate_2U_10in_clean.stl", 1, "PETG", 3, .20, "check", "Pi unit: faceplate, clean front (no DC-IN window, no notch)", "c3ef0b14"),
    ("W1_Argon_Poly5_Tray__x1__PETG__WAIT-measure-case.stl", f"{ARG}/11B_PETG_Argon-Poly+5-tray+faceplate_WAIT-measure-case/Pi5_ArgonPoly5_tray.stl", 1, "PETG", 3, .20, "wait", "Pi unit: Poly+ 5 tray (case up to 96.0 x 66.5)", "8882606c"),
    ("W2_Waveshare_F_Holder_Base__x1__PETG__WAIT-fit-test.stl", f"{HOLDER}/Waveshare_F_holder_base.stl", 1, "PETG", 3, .20, "wait", "adapter (F) holder base: only if the fit test passes", "6b9cad7e"),
    ("W3_Waveshare_F_Holder_Lid__x1__PETG__WAIT-fit-test.stl", f"{HOLDER}/Waveshare_F_holder_lid.stl", 1, "PETG", 3, .20, "wait", "adapter (F) holder lid", "982fa284"),
    ("W4_Display7C_3U_Body__x1__PLA__WAIT-screen-4Nov.stl", f"{PT}/09_PLA_screen-module_WAIT-measure-screen-first/Display7C_3U_Body.stl", 1, "PLA", 3, .15, "wait", "7in screen module body", "f89567e4"),
    ("O1_Brick_Spacer_6mm__x1__PETG__only-if-brick-30.5-32.5mm.stl", f"{PT}/13_PETG_12V-brick-cradle/Brick_Spacer_6mm.stl", 1, "PETG", 3, .20, "opt", "spacer for a 30.5-32.5 mm brick", "e7fa68d9"),
    ("O2_Brick_Spacer_4mm__x1__PETG__only-if-brick-32.5-34.5mm.stl", f"{PT}/13_PETG_12V-brick-cradle/Brick_Spacer_4mm.stl", 1, "PETG", 3, .20, "opt", "spacer for a 32.5-34.5 mm brick", "a193c01e"),
    ("O3_Brick_Spacer_2mm__x1__PETG__only-if-brick-34.5-36.5mm.stl", f"{PT}/13_PETG_12V-brick-cradle/Brick_Spacer_2mm.stl", 1, "PETG", 3, .20, "opt", "spacer for a 34.5-36.5 mm brick", "2e86a9bb"),
]
FOLDER = {"now": "1_PRINT-NOW", "check": "2_CHECK-UPS-FIRST", "wait": "3_WAIT", "opt": "4_OPTIONAL_spare-spacers"}
STATUS_TXT = {"now": "print / order now", "check": "check the UPS first", "wait": "wait", "opt": "optional"}


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
        ax.text((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, nm, ha="center", va="center", fontsize=6.5)
    ax.set_xlim(-5, BED + 5); ax.set_ylim(-5, BED + 5); ax.set_aspect("equal")
    ax.set_title(title, fontsize=8); fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)


def place(m, x, y):
    m = m.copy()
    m.apply_translation([x - m.bounds[0][0], y - m.bounds[0][1], -m.bounds[0][2]])
    return m


PETG_SET = ("Settings (Bambu P1S): 0.20mm Standard @BBL P1S, Generic PETG, 3 walls, 20% gyroid, supports OFF,\n"
            "Textured PEI no glue, enclosure CLOSED.\n")

if os.path.exists(DEST):
    sys.exit(f"{DEST} exists: refusing to overwrite")
for st in FOLDER.values():
    os.makedirs(os.path.join(DEST, st, "P1S_plates"))
for d in ("checks", "source"):
    os.makedirs(os.path.join(DEST, d))

# ---- 1. STLs, md5-checked, measured ----------------------------------------------------------------------------
meas = ["| File | Status | Qty | Mat | Measured size on the bed (mm) | Solid | ≈ g each | Bed fit | md5 = checked source |",
        "|---|---|---|---|---|---|---|---|---|"]
fails, ref, path_of = 0, {}, {}
gtot = {m: {s: 0.0 for s in FOLDER} for m in ("PLA", "PETG")}
for name, src, q, mat, walls, inf, st, where, h in PARTS:
    dst = os.path.join(DEST, FOLDER[st], name)
    shutil.copy2(src, dst)
    path_of[name] = dst
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
    meas.append(f"| `{name}` | {STATUS_TXT[st]} | {q} | {mat} | {e[0]:.1f} × {e[1]:.1f} × {e[2]:.1f} | "
                f"{'1 body, watertight' if (m.is_watertight and nb == 1) else f'{nb} bodies!'} | {g:.0f} | {'yes' if fits else 'NO'} | "
                f"{'yes' if ok_hash else 'NO: ' + md5(dst)[:8]} |")

# ---- 2. P1S plates, one status per plate ---------------------------------------------------------------------------
PLN = os.path.join(DEST, FOLDER["now"], "P1S_plates")
for folder, stem in [("01_PLA_side-modules-2U-base", "Plate01"), ("02_PLA_3U-module+base-bars", "Plate02"),
                     ("03_PLA_PRINT-FIRST_3U-module+handles", "Plate03"), ("04_PLA_3U-module+ears+clips", "Plate04"),
                     ("05_PLA_3U-module+1U-tops", "Plate05"), ("06_PLA_cap-half+ear", "Plate06"), ("07_PLA_cap-half+ear", "Plate07"),
                     ("08_PLA_B1-dock", "Plate08"), (A2, "Plate12-ALT2"), ("13_PETG_12V-brick-cradle", "Plate13"),
                     ("09_PLA_screen-module_WAIT-measure-screen-first", "Plate09")]:
    src = folder if os.path.isabs(folder) else os.path.join(PT, folder)
    d = os.path.join(DEST, FOLDER["wait"] if stem == "Plate09" else FOLDER["now"], "P1S_plates")
    shutil.copy2(os.path.join(src, stem + ".3mf"), os.path.join(d, stem + ".3mf"))
    shutil.copy2(os.path.join(src, stem + "_layout.png"), os.path.join(d, stem + "_layout.png"))
    s = open(os.path.join(src, "SETTINGS.txt")).read()
    s = s.replace("Material: PLA, about 144 g", "Material: PLA, about 128 g (144 g was with the old v4 B1 spacers, which are gone)")
    # 28 Oct (ultrareview): plate 09's caliper list, measured on Waveshare's STEP of the screen
    s = s.replace("  - Filament: Generic PLA (black / dark grey)", "  - Filament: Generic PLA, silver like the rest of the PLA parts (Robu: PLA silver, 15 %)")
    s = s.replace("  4. Tab hole center-to-center span: ~159 mm horizontal x ~114 mm vertical\n  If all 4 numbers match within ±0.5 mm, slice Plate09.3mf and print immediately!",
                  "  4. Tab holes (short slots, Ø3.3): centres 157.0 mm apart across; up/down the slot centres are ~114.9 mm apart\n"
                  "     (112.8 between the slots' inner ends, 117.0 between their outer ends). Corrected 28 Oct from \"~159 x ~114\":\n"
                  "     measured on Waveshare's STEP of the screen.\n"
                  "  If numbers 1-3 match within ±0.5 mm and the holes are where item 4 says, slice Plate09.3mf and print.")
    s = s.replace("""The 12 V power lead routes forward along the cradle, passes over the front base bar, and connects cleanly behind
the Pi faceplate via the rear concealed cable slit (featured on the final Plate 11 faceplate). The mains lead exits
directly out the rear. (An alternate bottom-edge notched faceplate is preserved in _superseded_and_alternatives/).""",
                  """The 12 V lead stays behind the faceplate (28 Oct): a 30 cm right-angle 5.5 x 2.1 extension goes from the UPS
DC-IN along the shelf floor, through the arch in the shelf's right gusset, into this cradle's open front, where the
brick's own plug pushes into its socket. Coil the brick's spare lead beside the join. The mains lead goes straight
out of the back.""")
    open(os.path.join(d, stem + "_SETTINGS.txt"), "w").write(s)

# plate 10: the Pi shelf alone (the UPS tray moved to plate 11; the shims are gone: the F holder doesn't use them)
p10 = [("Rack_Shelf_pinned", place(trimesh.load(path_of["10_Pi_Rack_Shelf_pinned__x1__PETG.stl"], force="mesh"), 43.0, 12.0))]   # 28 Oct shelf
write_3mf(os.path.join(PLN, "Plate10.3mf"), "Plate10", p10)
layout_png(os.path.join(PLN, "Plate10_layout.png"), "Plate 10 (PETG): Pi shelf", p10)
open(os.path.join(PLN, "Plate10_SETTINGS.txt"), "w").write(
    "Plate 10 (PETG): Pi shelf\n=========================\nStatus: print now\nMaterial: PETG black, about 96 g\n\n" + PETG_SET +
    "\nOn this plate:\n  - Rack_Shelf_pinned x1   (../10_Pi_Rack_Shelf_pinned__x1__PETG.stl)\n"
    "Hardware: 6 x M3 heat-set inserts (dia 4 hole) in its two front posts, for the faceplate screws.\n"
    "28 Oct: the right post's gusset has a 9 x 7 mm arch at its foot for the brick's 12 V lead (no supports needed: 3 mm round top).\n")

ld = lambda pre: trimesh.load(next(v for k, v in path_of.items() if k.startswith(pre)), force="mesh")
fp, ut, pt, hb, hl = ld("C2_"), ld("C1_"), ld("W1_"), ld("W2_"), ld("W3_")
PLC = os.path.join(DEST, FOLDER["check"], "P1S_plates")
p11 = [("Faceplate_2U_clean", place(fp, (BED - fp.extents[0]) / 2, 8.0)),
       ("UPS_tray_pinned", place(ut, (BED - ut.extents[0]) / 2, 8.0 + fp.extents[1] + 14.0))]
write_3mf(os.path.join(PLC, "Plate11_CHECK-UPS.3mf"), "Plate11", p11)
layout_png(os.path.join(PLC, "Plate11_CHECK-UPS_layout.png"), "Plate 11 (PETG, brim OFF): clean faceplate + UPS tray - check the UPS first", p11)
open(os.path.join(PLC, "Plate11_CHECK-UPS_SETTINGS.txt"), "w").write(
    "Plate 11 (PETG): faceplate (clean front) + UPS tray  --  CHECK THE UPS FIRST\n"
    "============================================================================\n"
    "28 Oct: the faceplate has no DC-IN window and no notch any more (the brick's lead stays behind it), so it no longer\n"
    "depends on the UPS: it's here because it shares the plate. The UPS tray and the right-angle DC-IN plug still do.\n"
    "Status: print once you've checked the real Cuzor Mini UPS Pro (a photo of it is enough):\n"
    "  - switch, LED and OUT on one end face (it goes to the rack REAR: tray window x 58..110 of the 100 mm face)\n"
    "  - DC-IN on the opposite end face, at the end that lines up with the UPS tray's DC-IN window (x 80..112)\n"
    "  - at most 101 x 81 x 28.5 mm (Cuzor's page: 10 x 8 x 2.8 cm; one listing says 10.2 long)\n"
    "  If the DC-IN sits at the other end of its face, don't print: ask Claude to move the windows.\n"
    "Material: PETG black, about 130 g (faceplate ~68 g, UPS tray ~62 g)\n\n"
    "BRIM OFF: the faceplate is 254 mm long on the 256 mm bed (1 mm from each edge). Faceplate front face down,\n"
    "UPS tray floor down.\n" + PETG_SET +
    "\nOn this plate:\n  - Faceplate, 2U, clean front x1               (../C2_Pi_Faceplate_2U_clean__x1__PETG.stl)\n"
    "  - UPS tray (pinned) x1                         (../C1_Pi_UPS_Tray_pinned__x1__PETG__CHECK-UPS-jacks.stl)\n"
    "Hardware: 6 x M3 x 8 countersunk (faceplate to the shelf); foam tape on the UPS tray's ribs.\n")
PLW = os.path.join(DEST, FOLDER["wait"], "P1S_plates")
p11w = [("Argon_Poly5_tray", place(pt, 6.0, (BED - pt.extents[1]) / 2)),
        ("F_holder_base", place(hb, 6.0 + pt.extents[0] + 6.0, (BED - hb.extents[1]) / 2)),
        ("F_holder_lid", place(hl, 6.0 + pt.extents[0] + 6.0 + hb.extents[0] + 6.0, (BED - hl.extents[1]) / 2))]
write_3mf(os.path.join(PLW, "Plate11W_WAIT.3mf"), "Plate11W", p11w)
layout_png(os.path.join(PLW, "Plate11W_WAIT_layout.png"), "Plate 11W (PETG) WAIT: Poly+ 5 tray (measure case) + F holder (fit test)", p11w)
open(os.path.join(PLW, "Plate11W_WAIT_SETTINGS.txt"), "w").write(
    "Plate 11W (PETG): Argon Poly+ 5 tray + Waveshare adapter (F) holder base + lid  --  WAIT\n"
    "=====================================================================================\n"
    "1. The Poly+ 5 tray: measure the case. It takes up to 96.0 long x 66.5 wide (listed 93.5 x 64 x 30, +-1 cm).\n"
    "   Bigger: don't print, ask Claude to widen the pocket.\n"
    "2. The holder (base + lid): FIT TEST. The holder sits 3-5 mm from the case's side ports (USB-C power, both\n"
    "   micro-HDMI), so it only works if the adapter (F)'s own plugs reach the Pi through the Poly+ 5's side cut-outs.\n"
    "   Test: Pi in the Poly+ 5, lid on; hold the adapter flat beside it, plug edge to the case, push its USB-C and\n"
    "   micro-HDMI into the cut-outs. Both must click fully home (about 6 mm in) with the adapter level. Also check\n"
    "   the 16-pin FFC can leave the case. Fails: don't print the holder (delete it from the plate); power the Pi\n"
    "   from a 12 V -> 5 V USB-C step-down and use the UGREEN micro-HDMI extender (no NVMe / 2.5G then).\n"
    "Material: PETG black, about 95 g (tray ~43 g, holder base ~35 g, lid ~17 g)\n\n" + PETG_SET +
    "The holder lid is saved TOP FACE DOWN: print it as it is.\n"
    "\nOn this plate:\n  - Argon Poly+ 5 tray x1      (../W1_Argon_Poly5_Tray__x1__PETG__WAIT-measure-case.stl)\n"
    "  - Adapter (F) holder base x1 (../W2_Waveshare_F_Holder_Base__x1__PETG__WAIT-fit-test.stl)\n"
    "  - Adapter (F) holder lid x1  (../W3_Waveshare_F_Holder_Lid__x1__PETG__WAIT-fit-test.stl)\n"
    "Hardware: 3 x M3 x 12 countersunk (tray onto the UPS tray: fit them before the case, two end up under it);\n"
    "4 x M2.5 x 25 pan head + foam tape for the holder.\n")

# ---- 3. audit every 3MF ------------------------------------------------------------------------------------------
aud, counts = [], {}
for st, sub in FOLDER.items():
    pl = os.path.join(DEST, sub, "P1S_plates")
    for f in sorted(os.listdir(pl)):
        if not f.endswith(".3mf"):
            continue
        items = read_3mf(os.path.join(pl, f))
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
        aud.append(f"{'PASS' if on else 'FAIL'}  {sub}/P1S_plates/{f}: {len(items)} part(s), x {lo[0]:.1f}..{hi[0]:.1f}, "
                   f"y {lo[1]:.1f}..{hi[1]:.1f}, tallest {hi[2]:.1f} mm  ->  " + ", ".join(names))
aud += ["", "Totals across all plates vs the parts list (3MF count / parts-list qty):"]
for p in PARTS:
    name, q = p[0], p[2]
    c = counts.get(name, 0)
    fails += c != q
    aud.append(f"{'PASS' if c == q else 'FAIL'}  {name}: {c} on the plates, {q} needed")

tot = "| Totals | PLA ≈ g | PETG ≈ g |\n|---|---|---|\n" + "".join(
    f"| {STATUS_TXT[s]} | {gtot['PLA'][s]:.0f} | {gtot['PETG'][s]:.0f} |\n" for s in FOLDER)
open(os.path.join(DEST, "checks", "MEASUREMENTS_every_part.md"), "w").write(
    "# Every print file, measured from the STL in this folder (28 Oct 2026)\n\n"
    "≈ g = slicer-like estimate (0.2 mm layers; rack/dock/screen PLA 3 walls 15 %, handles 4 walls 20 %, clips 30 %, "
    "PETG parts 3 walls 20 %, UCG mount 15 %). 'md5 = checked source' means the file is byte-identical to the one the checks ran on.\n\n"
    + "\n".join(meas) + "\n\n" + tot)
open(os.path.join(DEST, "checks", "PLATES_3MF_audit.txt"), "w").write(
    "3MF plate audit (read back from the files): every part on the 256 x 256 bed, identified by volume\n\n" + "\n".join(aud) + "\n")
shutil.copy2(__file__, os.path.join(DEST, "source", os.path.basename(__file__)))
print("\n".join(meas)); print(); print("\n".join(aud)); print()
print({k: {s: round(v) for s, v in d.items()} for k, d in gtot.items()})
print(f"FAILS: {fails}")
