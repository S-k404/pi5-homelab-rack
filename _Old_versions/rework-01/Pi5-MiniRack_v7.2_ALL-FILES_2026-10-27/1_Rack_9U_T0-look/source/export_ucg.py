"""
Export the UCG-Ultra 1U shelf: the print-ready STL (front face down, turned 45 degrees to fit a 220 mm bed),
STEP files for Onshape and preview images. Usage: python export_ucg.py <output folder>
"""
import os
import sys
import cadquery as cq
import ucg_shelf as ug
from b1_drawer import box
from render import render

OUT = sys.argv[1]
for sub in ("STL_for_printing", "STEP_for_Onshape", "images"):
    os.makedirs(os.path.join(OUT, sub), exist_ok=True)

if __name__ == "__main__":
    body, gw = ug.body(), ug.gateway_dummy()
    bed = body.rotate((0, 0, 0), (0, 0, 1), 45)                 # front face already on z = 0
    bb = bed.val().BoundingBox()
    bed = bed.translate((-bb.xmin, -bb.ymin, -bb.zmin))
    bb = bed.val().BoundingBox()
    print(f"UCG_Ultra_1U_Shelf on the bed {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:5.1f}")
    cq.exporters.export(bed, os.path.join(OUT, "STL_for_printing", "UCG_Ultra_1U_Shelf.stl"), tolerance=0.05, angularTolerance=0.1)
    cq.exporters.export(body, os.path.join(OUT, "STEP_for_Onshape", "UCG_Ultra_1U_Shelf.step"))
    asm = cq.Assembly()
    asm.add(body, name="UCG_shelf", color=cq.Color(0.2, 0.21, 0.23))
    asm.add(gw, name="UCG_Ultra", color=cq.Color(0.94, 0.94, 0.95))
    asm.export(os.path.join(OUT, "STEP_for_Onshape", "UCG_Ultra_1U_ASSEMBLY.step"))

    dark, white = "#45484d", "#eef0f2"
    lims = ((-135, 135), (-10, 150), (-30, 30))
    render([(body, dark), (gw, white)], os.path.join(OUT, "images", "ucg_front.png"), 18, 35,
           "UCG-Ultra 1U shelf: the window frames the gateway's front and its display", lims)
    render([(body, dark), (gw, white)], os.path.join(OUT, "images", "ucg_back.png"), 28, -140,
           "Back: ports clear between the two corner stops", lims)
    render([(body, dark)], os.path.join(OUT, "images", "ucg_empty.png"), 40, -130,
           "Empty tray: side rails, floor vents, rear corner stops", lims)
    # print pose: front face down on a 220 mm bed, turned 45 degrees
    pose = body.rotate((0, 0, 0), (1, 0, 0), -90).rotate((0, 0, 0), (0, 1, 0), 45)
    plate = box(-110, 110, -0.6, 0, -110, 110)
    render([(plate, "#b9c3cc"), (pose, dark)], os.path.join(OUT, "images", "ucg_on_bed.png"), 30, 35,
           "Print: front face down, turned 45 degrees on a 220 mm bed, no supports",
           ((-115, 115), (-115, 115), (-1, 140)))
    print("done")
