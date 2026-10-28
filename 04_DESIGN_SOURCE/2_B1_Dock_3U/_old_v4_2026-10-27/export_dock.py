"""Export the B1 face-out dock: print-ready STLs, STEP files and preview images. Usage: python export_dock.py <output folder>"""
import os
import sys
import cadquery as cq
import b1_dock as d
from render import render

OUT = sys.argv[1]
for sub in ("STL_for_printing", "STEP_for_Onshape", "images"):
    os.makedirs(os.path.join(OUT, sub), exist_ok=True)


def to_bed(shape, rots):
    s = shape
    for axis, ang in rots:
        s = s.rotate((0, 0, 0), axis, ang)
    bb = s.val().BoundingBox()
    return s.translate((-bb.xmin, -bb.ymin, -bb.zmin))


B, EL, ER = d.body(), d.ear(-1), d.ear(1)
prints = {
    "B1_Dock_3U_Body": (B, [((1, 0, 0), 90)]),                         # floor down
    "B1_Dock_3U_Ear_x2": (ER, []),                                     # flat
    "B1_Spacer_5mm_x2": (d.spacer(1, local=True), [((0, 1, 0), 90)]),  # on its side, hook profile on the bed
}
if __name__ == "__main__":
    for name, (shape, rots) in prints.items():
        p = to_bed(shape, rots)
        bb = p.val().BoundingBox()
        print(f"{name:22s} on the bed {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:5.1f}")
        cq.exporters.export(p, os.path.join(OUT, "STL_for_printing", name + ".stl"), tolerance=0.05, angularTolerance=0.1)
        cq.exporters.export(shape, os.path.join(OUT, "STEP_for_Onshape", name + ".step"))
    asm = cq.Assembly()
    for n, s, c in (("body", B, "gray"), ("ear_a", EL, "gray"), ("ear_b", ER, "gray"),
                    ("niimbot_b1_67mm", d.b1_dummy(), "lightblue")):
        asm.add(s, name=n, color=cq.Color(c))
    asm.export(os.path.join(OUT, "STEP_for_Onshape", "B1_Dock_3U_ASSEMBLY.step"))
    grey, dark, blue, orange = "#a3a8ad", "#6b7075", "#4f9fe0", "#e8833a"
    lims = ((-140, 140), (-10, 110), (-75, 75))
    render([(B, grey), (EL, dark), (ER, dark), (d.b1_dummy(), blue)], os.path.join(OUT, "images", "dock_front.png"), 14, 60,
           "3U face-out dock: the B1's top (labels, button, light, lid) faces you", lims)
    render([(B, grey), (EL, dark), (ER, dark), (d.b1_dummy(h=d.B1_H_THIN), blue), (d.spacer(1), orange), (d.spacer(-1), orange)],
           os.path.join(OUT, "images", "dock_spacers.png"), 30, 150,
           "62 mm B1: two clip-in 5 mm spacers (orange) on the back rest", lims)
    render([(B, grey), (EL, dark), (ER, dark)], os.path.join(OUT, "images", "dock_empty.png"), 38, 62,
           "Empty: cradle, low side guides, finger room, cable notch", lims)
    print("done")
