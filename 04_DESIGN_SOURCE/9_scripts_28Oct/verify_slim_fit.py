"""
Does the 28 Oct build fit the Slim Cargo 140 mm rack? (ultrareview, 28 Oct 2026)
Loads the slim rack parts (04_DESIGN_SOURCE/10_Slim_Cargo_Rack_140mm/STL_for_printing/in_rack_coords, rack frame) and every unit,
device, plug and cable of the standard build (scene from export_final.py, same rack frame) and checks: depth, collisions,
what the Pi shelf and the brick cradle stand on. Calculations on the models, not a physical test.
Usage: python verify_slim_fit.py <slim in_rack_coords dir> <scene dir> <report.txt>
"""
import glob
import os
import sys
import numpy as np
import trimesh
from manifold3d import Manifold, Mesh

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))                 # scene_load.py sits next to it
from scene_load import load  # noqa: E402

SLIM, SCENE, REPORT = sys.argv[1:4]
D = 140.0
out, cnt = [], {"PASS": 0, "FAIL": 0, "WARN": 0}


def rec(st, name, detail=""):
    cnt[st] = cnt.get(st, 0) + 1
    out.append(f"{st:<5} {name}  {detail}".rstrip())


def man(tm):
    m = Manifold(Mesh(vert_properties=np.asarray(tm.vertices, np.float32), tri_verts=np.asarray(tm.faces, np.uint32)))
    if m.status().name != "NoError" or m.volume() <= 0:
        h = tm.convex_hull
        m = Manifold(Mesh(vert_properties=np.asarray(h.vertices, np.float32), tri_verts=np.asarray(h.faces, np.uint32)))
    return m


rack = {os.path.basename(f)[:-4]: trimesh.load(f, force="mesh") for f in sorted(glob.glob(os.path.join(SLIM, "*.stl")))}
rmz = max(m.bounds[1][2] for m in rack.values())
out.append("Slim Cargo 140 mm rack with the 28 Oct build in it: checks (ultrareview, 28 Oct 2026)")
out.append("Rack frame: x across, y up from the base-bar tops, z back from the front rails, mm. The units, devices, plugs and the")
out.append("12 V cables are the standard build's (export_final.py); the slim rack parts are its in_rack_coords STLs.")
out.append("")
rec("PASS" if all(m.is_watertight for m in rack.values()) else "FAIL", "slim rack parts are watertight solids",
    f"({len(rack)} parts; rack depth {rmz:.1f})")
objs = [o for o in load(SCENE, ("dock", "screen", "ucg", "pi", "pi_cables"))]
out.append("")
out.append("== Depth: what sticks out behind a 140 mm rack ==")
groups = {}
for o in objs:
    g = "Pi unit" if o["group"] in ("pi", "pi_cables") else o["group"]
    groups.setdefault(g, []).append(o)
BEHIND = ("c13", "mains")                                         # the mains plug and cord leave the back in either rack
for g, lst in groups.items():
    lst = [o for o in lst if o["mesh_key"] not in BEHIND]
    worst = max(lst, key=lambda o: o["mesh"].bounds[1][2])
    z = worst["mesh"].bounds[1][2]
    st = "PASS" if z <= D - 0.5 else "FAIL"
    rec(st, f"{g}: deepest part ends at z {z:.1f}", f"({worst['name']}{'' if st == 'PASS' else f': {z - D:.1f} mm behind the rack'})")
over = sorted([(o["mesh"].bounds[1][2], o["name"]) for o in objs if o["mesh"].bounds[1][2] > D], reverse=True)
if over:
    rec("INFO", "everything past z 140 (the mains plug and cord leave the back in the standard rack too)", "(" + "; ".join(f"{n} to z {z:.0f}" for z, n in over) + ")")
out.append("")
out.append("== Collisions with the slim rack parts ==")
rm = {k: man(v) for k, v in rack.items()}
hits = []
for o in objs:
    mo = man(o["mesh"])
    lo, hi = o["mesh"].bounds
    for k, m in rack.items():
        if (m.bounds[0] > hi).any() or (m.bounds[1] < lo).any():
            continue
        v = (mo ^ rm[k]).volume()
        if v > 0.5:
            hits.append((v, o["name"], k))
hits.sort(reverse=True)
rec("PASS" if not hits else "FAIL", "no unit, device or cable runs into the slim rack",
    "(" + ("nothing" if not hits else "; ".join(f"{n} into {k}: {v:.0f} mm3" for v, n, k in hits[:8])) + ")")
out.append("")
out.append("== What the Pi unit stands on ==")
bars = sorted([rack[k] for k in rack if k.startswith("bar_")], key=lambda m: m.bounds[0][2])
rec("INFO", "slim base bars at z", "(" + ", ".join(f"{b.bounds[0][2]:.0f}..{b.bounds[1][2]:.0f}" for b in bars) + "; the standard rack's are "
    "1..12, 80..92, 188..199: the Pi shelf rests on the front and middle ones, the brick cradle straddles the middle and rear)")
shelf = next(o for o in objs if o["mesh_key"] == "pi_shelf")["mesh"]
cradle = next(o for o in objs if o["mesh_key"] == "cradle")["mesh"]
for nm, part in (("Pi shelf", shelf), ("brick cradle", cradle)):
    # contact area: underside points of the part within 0.3 mm of a bar top
    pts, _ = trimesh.sample.sample_surface_even(part, 40000, seed=1)
    low = pts[pts[:, 1] < part.bounds[0][1] + 0.3]
    on = [b for b in bars if ((low[:, 0] > b.bounds[0][0]) & (low[:, 0] < b.bounds[1][0]) & (low[:, 2] > b.bounds[0][2]) &
                              (low[:, 2] < b.bounds[1][2])).sum() > 20 and abs(b.bounds[1][1] - part.bounds[0][1]) < 0.5]
    zs = ", ".join(f"z {b.bounds[0][2]:.0f}..{b.bounds[1][2]:.0f}" for b in on)
    if nm == "Pi shelf":
        rec("PASS" if len(on) >= 2 else "FAIL", f"{nm} stands on at least two base bars", f"(on {len(on)}: {zs or 'none'})")
    else:
        rec("PASS" if len(on) >= 2 and cradle.bounds[1][2] <= D else "FAIL", f"{nm} stands on two bars and fits the depth",
            f"(on {len(on)}: {zs or 'none'}; it is {cradle.extents[2]:.0f} mm long and ends at z {cradle.bounds[1][2]:.0f})")
out.append("")
out.append(f"{cnt['PASS']} PASS, {cnt['FAIL']} FAIL, {cnt.get('WARN', 0)} WARN")
open(REPORT, "w").write("\n".join(out) + "\n")
print("\n".join(out))
