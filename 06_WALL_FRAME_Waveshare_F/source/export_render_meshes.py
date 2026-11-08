"""Meshes for the Blender render, in the assembled position: the box, the front and the adapter split by finish.
Run: python export_render_meshes.py <out folder>   (writes <out>/render_meshes/*.stl)"""
import os
import sys
import cadquery as cq
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import waveshare_f_wall_frame as F
import adapter_model as A

OUT = os.path.join(sys.argv[1], "render_meshes")
os.makedirs(OUT, exist_ok=True)
cq.exporters.export(F.frame_box(), os.path.join(OUT, "frame_box.stl"), tolerance=0.03, angularTolerance=0.1)
cq.exporters.export(F.bezel(), os.path.join(OUT, "frame_front.stl"), tolerance=0.02, angularTolerance=0.1)
groups = {}
for name, (solid, finish) in A.parts().items():
    if finish != "hidden":
        groups[finish] = solid if finish not in groups else groups[finish].fuse(solid)
for finish, solid in groups.items():
    cq.exporters.export(cq.Workplane().add(solid), os.path.join(OUT, f"board_{finish}.stl"),
                        tolerance=0.03, angularTolerance=0.1)
print("wrote", sorted(os.listdir(OUT)))
