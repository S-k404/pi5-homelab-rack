"""Export the 7-inch screen module: print-ready STLs, STEP files and preview images. Usage: python export_display.py <output folder>"""
import os
import sys
import cadquery as cq
import display as dp
from render import render

OUT = sys.argv[1]
for sub in ("STL_for_printing", "STEP_for_Onshape", "images"):
    os.makedirs(os.path.join(OUT, sub), exist_ok=True)
B, c = dp.body(), dp.clip()
for name, shape in (("Display7_3U_Body", B), ("Display7_Clip_x4", c)):        # bezel face down / flat
    bb = shape.val().BoundingBox()
    cq.exporters.export(shape.translate((-bb.xmin, -bb.ymin, -bb.zmin)), os.path.join(OUT, "STL_for_printing", name + ".stl"),
                        tolerance=0.05, angularTolerance=0.1)
    cq.exporters.export(shape, os.path.join(OUT, "STEP_for_Onshape", name + ".step"))
asm = cq.Assembly().add(B, name="body", color=cq.Color("gray")).add(dp.glass_dummy(), name="screen", color=cq.Color("black"))
for i, cl in enumerate(dp.clips()):
    asm.add(cl, name=f"clip{i}", color=cq.Color("gray"))
for s in (1, -1):
    asm.add(dp.ear(s), name=f"ear{s}", color=cq.Color("gray"))
asm.export(os.path.join(OUT, "STEP_for_Onshape", "Display7_3U_ASSEMBLY.step"))
lims = ((-140, 140), (-10, 90), (-80, 80))
render([(B, "#8d9298"), (dp.glass_dummy(), "#15171c"), (dp.ear(1), "#55585e"), (dp.ear(-1), "#55585e")],
       os.path.join(OUT, "images", "display_front.png"), 12, 64, "7-inch screen module (3U): bezel and ears", lims)
render([(B, "#8d9298"), (dp.glass_dummy(), "#15171c"), (dp.driver_dummy(), "#2f8f5b")] + [(x, "#55585e") for x in dp.clips()],
       os.path.join(OUT, "images", "display_back.png"), 28, -118, "From behind: screen pocket, 4 clips, driver-board tray", lims)
print("done")
