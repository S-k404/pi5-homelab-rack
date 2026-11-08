"""
STEP files of the two prints in the same position as their STLs (flat on the bed), exported from the exact CAD model,
then checked against the STLs: the STEP is read back from disk, and every STL vertex must lie on its surface.
Run: python export_print_step.py <STL folder> <report.txt>
"""
import os
import sys
import numpy as np
import trimesh
import cadquery as cq
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import waveshare_f_wall_frame as F

STL_DIR, REPORT = sys.argv[1:3]
lines = []
for nm, shp in (("WallFrame_F_box", F.frame_box()), ("WallFrame_F_front", F.bezel())):
    step_path = os.path.join(STL_DIR, nm + ".step")
    cq.exporters.export(F.to_bed(shp), step_path)

    back = cq.importers.importStep(step_path)
    solid = back.val()
    faces = back.faces().vals()
    kinds = {}
    for f in faces:
        kinds[f.geomType()] = kinds.get(f.geomType(), 0) + 1
    # fine tessellation of the STEP read back from disk, to measure how far the STL's vertices are from its surface
    verts, tris = solid.tessellate(0.002, 0.05)
    ref = trimesh.Trimesh(np.array([v.toTuple() for v in verts]), np.array(tris), process=False)
    stl = trimesh.load(os.path.join(STL_DIR, nm + ".stl"))
    _, d, _ = trimesh.proximity.closest_point(ref, stl.vertices)
    # sizes from the surface itself: OCC's BoundingBox() pads curved / spline faces (the engraved text) by up to 0.5 mm
    lo, hi = ref.bounds
    ext = hi - lo
    ok = (solid.isValid() and len(back.solids().vals()) == 1 and d.max() < 0.03
          and np.allclose(lo, stl.bounds[0], atol=0.02) and np.allclose(ext, stl.extents, atol=0.02))
    lines.append(f"{'PASS' if ok else 'FAIL'}  {nm}.step: one valid solid, same place and size as {nm}.stl")
    lines.append(f"      {ext[0]:.2f} x {ext[1]:.2f} x {ext[2]:.2f} mm (STL {stl.extents[0]:.2f} x {stl.extents[1]:.2f} x "
                 f"{stl.extents[2]:.2f}); volume STEP {solid.Volume() / 1000:.3f} cm3, "
                 f"STL {stl.volume / 1000:.3f} cm3")
    lines.append(f"      STL vertices from the STEP surface: max {d.max():.4f} mm, mean {d.mean():.4f} mm "
                 f"({len(stl.vertices)} vertices)")
    lines.append(f"      {len(faces)} exact faces: " + ", ".join(f"{v} {k.lower()}" for k, v in sorted(kinds.items())))

open(REPORT, "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
