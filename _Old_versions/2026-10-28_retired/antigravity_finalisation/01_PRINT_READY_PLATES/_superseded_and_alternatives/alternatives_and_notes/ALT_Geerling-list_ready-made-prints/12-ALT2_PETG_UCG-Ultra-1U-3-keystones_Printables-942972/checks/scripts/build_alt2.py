"""File the checked Printables 942972 mount as PRINT_THIS plate 12-ALT2: bed-oriented STL, 3MF (read back), layout picture.
Usage: python -I build_alt2.py <rackfit_local.stl> <dest folder> <rack source dir>"""
import os, sys, math, zipfile, numpy as np, trimesh
import xml.etree.ElementTree as ET
from xml.sax.saxutils import quoteattr
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
SRC, DEST, RACKSRC = sys.argv[1:4]
sys.path.insert(0, RACKSRC)
from estimate_filament import grams
BED = 256.0
NAME = "UCG-Ultra_1U_3-keystones_Printables-942972"
os.makedirs(DEST, exist_ok=True)
m = trimesh.load(SRC, force="mesh")
R = np.eye(4); R[1, 1] = -1; R[2, 2] = -1             # turn 180 deg about x: panel front face (z = 136) onto the bed
m.apply_transform(R); m.apply_translation(-m.bounds[0])
stl = os.path.join(DEST, NAME + ".stl"); m.export(stl)
lo, hi = m.bounds
first = m.area_faces[(np.abs(m.face_normals[:, 2] + 1) < 1e-6) & (m.triangles_center[:, 2] < 1e-6)].sum()
g = grams(stl, 3, 0.20) * 1.27 / 1.24
# plate: turned 45 degrees and centred, like plate 12, so a brim fits
a = math.radians(45); Rz = np.eye(4); Rz[:2, :2] = [[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]]
v = trimesh.transform_points(m.vertices, Rz); vlo, vhi = v.min(0), v.max(0)
T = np.eye(4); T[:3, 3] = ((BED - (vhi[0] - vlo[0])) / 2 - vlo[0], (BED - (vhi[1] - vlo[1])) / 2 - vlo[1], -vlo[2])
P = T @ Rz
pm = m.copy().apply_transform(P)
plo, phi = pm.bounds
edge = min(plo[0], plo[1], BED - phi[0], BED - phi[1])
res = [(m.is_watertight and len(m.split()) == 1, f"{NAME}.stl: one watertight solid, panel face down"),
       (abs(lo[2]) < 1e-6 and first > 5000, f"flat on the bed: {first:.0f} mm2 first layer (the whole panel face)"),
       (edge >= 6.0, f"on the plate at 45 deg: x {plo[0]:.1f}-{phi[0]:.1f}, y {plo[1]:.1f}-{phi[1]:.1f}, {phi[2]:.1f} tall; "
                     f"{edge:.1f} mm to the bed edge, room for a 5 mm brim")]
# 3MF
mf = os.path.join(DEST, "Plate12-ALT2.3mf")
vs = "".join(f'<vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>' for x, y, z in pm.vertices)
ts = "".join(f'<triangle v1="{i}" v2="{j}" v3="{k}"/>' for i, j, k in pm.faces)
model = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" '
         'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><metadata name="Title">Plate12-ALT2</metadata>'
         f'<resources><object id="1" name={quoteattr(NAME)} type="model"><mesh><vertices>{vs}</vertices><triangles>{ts}</triangles></mesh></object>'
         '</resources><build><item objectid="1"/></build></model>')
ct = ('<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
      '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
      '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
rels = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
with zipfile.ZipFile(mf, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", ct); z.writestr("_rels/.rels", rels); z.writestr("3D/3dmodel.model", model)
ns = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
o = ET.fromstring(zipfile.ZipFile(mf).read("3D/3dmodel.model")).findall(".//m:object", ns)
vv = np.array([[float(e.get(c)) for c in "xyz"] for e in o[0].findall(".//m:vertex", ns)])
tt = np.array([[int(e.get(c)) for c in ("v1", "v2", "v3")] for e in o[0].findall(".//m:triangle", ns)])
back = trimesh.Trimesh(vv, tt, process=False)
res.append((len(o) == 1 and np.allclose(back.bounds, pm.bounds, atol=1e-3) and abs(back.volume - pm.volume) < 1e-3 * pm.volume,
            "Plate12-ALT2.3mf written and read back: same part, same place, same volume"))
# picture
fig, ax = plt.subplots(figsize=(5, 5))
ax.add_patch(plt.Rectangle((0, 0), BED, BED, fc="#f4f4f2", ec="#555", lw=1.2))
ax.add_collection(PolyCollection(pm.vertices[pm.faces][:, :, :2], facecolors="#3f6fb0", edgecolors="none", alpha=0.9))
c = (plo + phi) / 2
ax.text(c[0], c[1], "UCG-Ultra 1U mount\n(Printables 942972, panel face down)", ha="center", va="center", fontsize=7,
        bbox=dict(fc="white", ec="none", alpha=0.8, pad=1))
ax.set_xlim(-4, BED + 4); ax.set_ylim(-4, BED + 4); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
ax.set_title("Plate12-ALT2 · PETG 0.20 mm · 256 x 256 bed", fontsize=8)
fig.savefig(os.path.join(DEST, "Plate12-ALT2_layout.png"), dpi=130, bbox_inches="tight"); plt.close(fig)
txt = ["Plate12-ALT2 (PETG, 0.20 mm)"] + [f"  {'PASS' if ok else 'FAIL'}  {t}" for ok, t in res]
txt.append(f"\n{sum(ok for ok, _ in res)} PASS, {sum(not ok for ok, _ in res)} FAIL")
os.makedirs(os.path.join(DEST, "checks"), exist_ok=True)
open(os.path.join(DEST, "checks", "plate_layout_check.txt"), "w").write("\n".join(txt) + "\n")
print("\n".join(txt)); print(f"grams PETG ~{g:.0f}; on bed {hi[0]-lo[0]:.1f} x {hi[1]-lo[1]:.1f} x {hi[2]-lo[2]:.1f}")
