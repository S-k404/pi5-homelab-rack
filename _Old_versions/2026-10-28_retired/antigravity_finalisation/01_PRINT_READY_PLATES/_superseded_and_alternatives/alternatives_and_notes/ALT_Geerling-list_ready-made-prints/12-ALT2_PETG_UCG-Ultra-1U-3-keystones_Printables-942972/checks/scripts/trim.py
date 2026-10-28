"""Rack-fit version: take 0.8 mm off the top so the panel is a standard 43.65 mm 1U (0.8 mm under the cap)."""
import sys, trimesh
u = trimesh.load(sys.argv[1], force="mesh")
keep = trimesh.creation.box(bounds=[[-5, -5, -5], [260, 44.45 - 0.8, 141]])
t = trimesh.boolean.intersection([u, keep], engine="manifold")
print("trimmed: watertight", t.is_watertight, "bodies", len(t.split()), "bounds", t.bounds.round(2).tolist(), "vol", round(t.volume))
t.export(sys.argv[2])
