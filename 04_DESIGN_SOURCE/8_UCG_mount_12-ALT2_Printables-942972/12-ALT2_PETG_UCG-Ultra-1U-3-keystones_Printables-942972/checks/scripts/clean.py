"""Clean the downloaded mount: drop degenerate bodies, union the keystone receptacles into the panel.
Writes clean_local.stl in the download's own frame moved to the origin (x across, y up, z: 0 = tray back, 136 = panel front)."""
import sys, numpy as np, trimesh
m = trimesh.load(sys.argv[1], force="mesh")
m.apply_translation(-m.bounds[0])
bodies = [b for b in m.split(only_watertight=False) if len(b.faces) > 10 and b.is_watertight]
print("kept bodies", len(bodies), [len(b.faces) for b in bodies])
u = trimesh.boolean.union(bodies, engine="manifold")
print("union: watertight", u.is_watertight, "bodies", len(u.split()), "volume", round(u.volume, 1),
      "sum", round(sum(b.volume for b in bodies), 1), "bounds", u.bounds.round(2).tolist())
u.export(sys.argv[2])
# overhang survey, panel face down: build direction = -z_local; a face overhangs if its normal points down the build
nb = -u.face_normals[:, 2]                     # component along build-up direction
h = 136.0 - u.triangles_center[:, 2]           # height above the bed
down = (nb < -0.70) & (h > 0.3)                # steeper than 45 deg, facing the bed, above the first layer
print("panel face down: overhang area %.0f mm2" % u.area_faces[down].sum())
sub = u.submesh([np.where(down)[0]], append=True)
for p in sub.split(only_watertight=False):
    lo, hi = p.bounds
    if p.area > 5:
        print("   patch at height %.1f-%.1f: x %.1f-%.1f y %.1f-%.1f area %.0f" % (136-hi[2], 136-lo[2], lo[0], hi[0], lo[1], hi[1], p.area))
# floor down alternative
nb2 = u.face_normals[:, 1]; h2 = u.triangles_center[:, 1]
down2 = (nb2 < -0.70) & (h2 > 0.3)
print("floor down: overhang area %.0f mm2" % u.area_faces[down2].sum())
sub2 = u.submesh([np.where(down2)[0]], append=True)
for p in sub2.split(only_watertight=False):
    lo, hi = p.bounds
    if p.area > 20:
        print("   patch at y %.1f: x %.1f-%.1f z %.1f-%.1f area %.0f" % (lo[1], lo[0], hi[0], lo[2], hi[2], p.area))
