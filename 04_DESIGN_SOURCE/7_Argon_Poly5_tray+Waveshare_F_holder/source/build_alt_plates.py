"""Plate folders for the alternative Pi-unit trays: STLs, a pre-arranged 3MF, a layout picture, SETTINGS.txt,
plus a top-down plan of each tray with the case and plugs drawn in.
Usage: python build_alt_plates.py <v7.2 bundle> <alt out folder (has STL_for_printing)> <dest folder>"""
import os
import shutil
import sys
import numpy as np
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import argon_tray as A

SRC, ALT, DEST = sys.argv[1], sys.argv[2], sys.argv[3]
BED, MARGIN, GAP = 256.0, 1.0, 2.0
FACE = os.path.join(SRC, "4_Pi_Unit_2U", "STL_for_printing", "Rack_Faceplate_2U_10in.stl")
F = {"NEO5": (os.path.join(ALT, "STL_for_printing", "Pi5_ArgonNEO5_tray.stl"), "Argon NEO 5 tray"),
     "POLY5": (os.path.join(ALT, "STL_for_printing", "Pi5_ArgonPoly5_tray.stl"), "Argon Poly+5 tray"),
     "face": (FACE, "Pi faceplate (1 piece)")}
MESH = {k: trimesh.load(p, force="mesh") for k, (p, _) in F.items()}
PLATES = [
    ("11A_PETG_Argon-NEO-5-tray+faceplate_WAIT-measure-case", "Plate11A", "NEO5"),
    ("11B_PETG_Argon-Poly+5-tray+faceplate_WAIT-measure-case", "Plate11B", "POLY5"),
]


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
        res.append((ok, f"{os.path.basename(F[key][0])}: x {lo[0]:.1f}-{hi[0]:.1f}, y {lo[1]:.1f}-{hi[1]:.1f}, {hi[2]:.1f} tall, on the bed"))
    (a0, a1), (b0, b1) = boxes
    gap = max(b0[0] - a1[0], a0[0] - b1[0], b0[1] - a1[1], a0[1] - b1[1])
    res.append((gap >= GAP, f"gap between the parts {gap:.1f} mm"))
    return res


def write_3mf(path, placed):
    """plain 3MF core file, positions baked in, read back and compared (same as the PRINT_THIS builder)"""
    import zipfile
    import xml.etree.ElementTree as ET
    from xml.sax.saxutils import quoteattr
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
    ns = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
    got = ET.fromstring(zipfile.ZipFile(path).read("3D/3dmodel.model")).findall(".//m:object", ns)
    assert len(got) == len(placed), path
    for o, (key, M) in zip(got, placed):
        v = np.array([[float(e.get(a)) for a in "xyz"] for e in o.findall(".//m:vertex", ns)])
        t = np.array([[int(e.get(a)) for a in ("v1", "v2", "v3")] for e in o.findall(".//m:triangle", ns)])
        mm = trimesh.Trimesh(v, t, process=False)
        ref = MESH[key].copy().apply_transform(M)
        assert np.allclose(mm.bounds, ref.bounds, atol=1e-3) and abs(mm.volume - ref.volume) < 1e-3 * ref.volume, (path, key)
    return True


def draw_plate(ax, placed, title):
    ax.add_patch(plt.Rectangle((0, 0), BED, BED, fc="#f4f4f2", ec="#555", lw=1.2))
    for key, M in placed:
        m = MESH[key]
        v = trimesh.transform_points(m.vertices, M)
        ax.add_collection(PolyCollection(v[m.faces][:, :, :2], facecolors="#3f6fb0", edgecolors="none", alpha=0.9))
        c = (v.min(0) + v.max(0)) / 2
        ax.text(c[0], c[1], F[key][1], ha="center", va="center", fontsize=7, bbox=dict(fc="white", ec="none", alpha=0.8, pad=1))
    ax.set_xlim(-4, BED + 4); ax.set_ylim(-4, BED + 4); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(title, fontsize=8)


def draw_plan(path, key):
    """top view in the rack: rear (cables) at the bottom, faceplate at the top"""
    m = trimesh.load(os.path.join(ALT, "STL_for_printing", A.NAMES[key] + ".stl"), force="mesh")
    m.apply_translation((A.X0, A.Y0, A.PLENUM_TOP))           # back to the v3 frame (STL was moved to the origin)
    tri = m.vertices[m.faces]
    up = m.face_normals[:, 2] > 0.5
    zc = tri[up][:, :, 2].mean(1)
    shade = np.clip((zc - A.ZS) / 10.0, 0, 1)
    cols = [(0.62 - 0.35 * s, 0.70 - 0.35 * s, 0.85 - 0.30 * s) for s in shade]
    fig, ax = plt.subplots(figsize=(8.6, 8.4))
    order = np.argsort(zc)
    ax.add_collection(PolyCollection(tri[up][order][:, :, :2], facecolors=[cols[i] for i in order], edgecolors="none"))
    c = A.CASES[key]
    for size, ls, lab in (("nominal", "-", "case, listed size"), ("max", ":", "largest published size")):
        L, Wc, _ = c[size]
        ax.add_patch(plt.Rectangle((A.X_DATUM - Wc, A.Y_DATUM), Wc, L, fill=(size == "nominal"), fc=(0.85, 0.3, 0.22, 0.18),
                                   ec="#b0351f", lw=1.4, ls=ls, label=f"{c['title'].title()}: {lab} {L} x {Wc}"))
    Wn = c["nominal"][1]
    left = A.X_DATUM - Wn
    for nm, d in (("USB-C power", 11.2), ("micro-HDMI 0", 25.8), ("micro-HDMI 1", 39.2)):
        yc = 2.5 + 85.0 - d
        ax.annotate("", xy=(left - 30, yc), xytext=(left, yc), arrowprops=dict(arrowstyle="->", color="#2e7d32", lw=1.6))
        ax.text(left - 31, yc, nm, ha="right", va="center", fontsize=8, color="#2e7d32")
    ax.annotate("", xy=((left + A.X_DATUM) / 2, -22), xytext=((left + A.X_DATUM) / 2, 0),
                arrowprops=dict(arrowstyle="->", color="#2e7d32", lw=1.6))
    ax.text((left + A.X_DATUM) / 2, -24, "USB x4 + Ethernet: plug in at the rack rear", ha="center", va="top", fontsize=8, color="#2e7d32")
    cx, cy, w, h = A.LEAD_HOLE
    ax.annotate("12 V lead up from the UPS\n(under the tray)", xy=(cx, cy), xytext=(cx - 6, cy + 22), fontsize=7.5,
                ha="center", arrowprops=dict(arrowstyle="->", lw=0.8))
    ax.annotate("zip-tie the 12 V to 5 V\nUSB-C converter here", xy=(20, 104), xytext=(20, 136), fontsize=7.5,
                ha="center", arrowprops=dict(arrowstyle="->", lw=0.8))
    for jx, jy in A.JOINTS:
        ax.plot(jx, jy, "o", ms=5, mfc="white", mec="black")
    ax.plot([], [], "o", ms=5, mfc="white", mec="black", label="M3 x 12 joint screw (fit before the case)")
    ax.text(57, 121, "FACEPLATE  (rack front)", ha="center", fontsize=9, weight="bold")
    ax.text(57, -40, "RACK REAR  (cables)", ha="center", fontsize=9, weight="bold")
    ax.text(A.X1 + 3, 50, "right fence (datum)", rotation=90, va="center", fontsize=7.5)
    ax.set_xlim(-48, 128); ax.set_ylim(-46, 146); ax.set_aspect("equal")
    ax.set_xlabel("mm"); ax.legend(loc="upper right", fontsize=7, framealpha=0.9)
    ax.set_title(f"{c['title'].title()} tray, top view in the rack (darker = taller)", fontsize=10)
    fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)


SETTINGS = ["Bambu Studio profile: 0.20mm Standard @BBL P1S", "Filament: Generic PETG", "Wall loops: 3",
            "Sparse infill: 20% gyroid", "Supports: OFF", "Plate: Textured PEI, no glue", "Enclosure: CLOSED"]
report = []
for folder, name, key in PLATES:
    d = os.path.join(DEST, folder); os.makedirs(d, exist_ok=True)
    placed = place([(key, 8, 10), ("face", 1, 140)])
    res = check(placed)
    write_3mf(os.path.join(d, name + ".3mf"), placed)
    res.append((True, f"{name}.3mf written and read back: same 2 parts, same places, same volumes"))
    report.append((name, res))
    fig, ax = plt.subplots(figsize=(5, 5))
    draw_plate(ax, placed, f"{name} · PETG 0.20 mm · 256 x 256 bed")
    fig.savefig(os.path.join(d, name + "_layout.png"), dpi=130, bbox_inches="tight"); plt.close(fig)
    draw_plan(os.path.join(d, name + "_plan_in_rack.png"), key)
    for k in (key, "face"):
        shutil.copy2(F[k][0], os.path.join(d, os.path.basename(F[k][0])))
    c = A.CASES[key]
    Lm, Wm, _ = c["max"]
    lines = [folder, "=" * len(folder),
             f"Status: WAIT until the {c['title'].title()} case arrives and you've measured it (see below)",
             "Material: PETG, about 107 g (tray ~42 g + faceplate ~65 g)", "",
             "Print this INSTEAD OF plate 11 when the Pi lives in this case. Still print plate 10 (shelf + UPS tray).",
             "", "How: double-click the .3mf (or File > Open Project in Bambu Studio). Both parts are already placed.",
             "If Bambu Studio asks, choose to load the geometry only. Then pick the settings below and Slice.", "", "Settings:"]
    lines += ["  - " + x for x in SETTINGS] + ["",
              "Notes:",
              "  Brim: OFF. The faceplate is 254 mm on a 256 mm bed, so a brim would run off the plate.",
              f"  Measure the case first: length (port end to microSD end), width (side ports to GPIO side), height.",
              f"  The tray takes any case up to {Lm + A.CLR:.1f} long x {Wm + A.CLR:.1f} wide (the largest published size",
              f"  is {Lm} x {Wm}). Listed size {c['nominal'][0]} x {c['nominal'][1]} x {c['nominal'][2]}.",
              "  - Bigger than that: don't print, ask Claude to widen the pocket.",
              "  - Up to ~3 mm smaller: fine. Push it into the rear-right corner and stick it down with the foam tape.",
              "  - More than ~3 mm smaller: it still works on the foam tape, or ask Claude for a snug version.",
              "  The faceplate is the same file as plate 11's. If you've already printed plate 11, you only need the tray:",
              "  in Bambu Studio, delete the faceplate from the plate before slicing.", "",
              "On this plate:", f"  - {F[key][1]} x1   ({os.path.basename(F[key][0])})",
              f"  - {F['face'][1]} x1   ({os.path.basename(FACE)})"]
    open(os.path.join(d, "SETTINGS.txt"), "w").write("\n".join(lines) + "\n")

fails = 0
txt = []
for name, res in report:
    txt.append(f"{name} (PETG, 0.20 mm)")
    for ok, t in res:
        fails += not ok
        txt.append(f"  {'PASS' if ok else 'FAIL'}  {t}")
txt.append(f"\n{sum(len(r) for _, r in report) - fails} PASS, {fails} FAIL")
os.makedirs(os.path.join(DEST, "checks"), exist_ok=True)
open(os.path.join(DEST, "checks", "plate_layout_check.txt"), "w").write("\n".join(txt) + "\n")
print("\n".join(txt))
