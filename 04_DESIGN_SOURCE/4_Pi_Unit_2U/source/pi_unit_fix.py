"""
Print fixes for the Pi 5 2U unit (25 Oct bundle), for the T0-look rack.
- The UPS tray loses its four 3 mm feet (they left the whole floor printing in mid-air) and gets four 4.4 mm
  locating holes instead; the shelf gets matching standoffs with pins (see pi_rack.shelf), so the tray sits
  at exactly the same height as before.
- Every STL is written laid out for printing (the old ones were in their assembled positions).
STEP files stay in the assembled (v3) frame for Onshape.
Run from this folder: python pi_unit_fix.py <folder with the 25 Oct STEP files> <output folder>
"""
import os
import sys
import cadquery as cq
import pi_rack as R

SRC, OUT = sys.argv[1], sys.argv[2]
for sub in ("STL_for_printing", "STEP_for_Onshape"):
    os.makedirs(os.path.join(OUT, sub), exist_ok=True)


def load(name):
    return cq.Workplane().add(cq.importers.importStep(os.path.join(SRC, name)).val())


def ups_tray_pinned():
    t = load("Pi5_UPS_v3_ups_tray.step")
    b = t.val().BoundingBox()
    t = t.cut(R.box(b.xmin - 1, b.xmax + 1, b.ymin - 1, b.ymax + 1, b.zmin - 1, R.TRAY_FLOOR_Z))   # feet off
    for fx, fy in R.FEET:
        t = t.cut(cq.Workplane("XY").circle(R.PIN_HOLE / 2).extrude(2.2).translate((fx, fy, R.TRAY_FLOOR_Z - 0.1)))
    return t


def to_bed(shape, rots=()):
    s = shape
    for axis, ang in rots:
        s = s.rotate((0, 0, 0), axis, ang)
    bb = s.val().BoundingBox()
    return s.translate((-bb.xmin, -bb.ymin, -bb.zmin))


parts = {
    # name: (assembled shape, rotations that lay it on the bed)
    "Pi5_UPS_v3_ups_tray_pinned": (ups_tray_pinned(), []),                     # floor down
    "Pi5_UPS_v3_board_tray_HDMIexit": (load("Pi5_UPS_v3_board_tray_HDMIexit.step"), []),   # floor down
    "Pi5_UPS_v3_lid": (load("Pi5_UPS_v3_lid.step"), [((1, 0, 0), 180)]),       # top face down
    "Rack_Shelf_pinned": (R.shelf(), []),                                       # base down
    "Rack_Faceplate_2U_10in": (load("Rack_Faceplate_2U_10in.step"), [((1, 0, 0), -90)]),   # front face down
    "Rack_Faceplate_Left": (load("Rack_Faceplate_Left.step"), [((1, 0, 0), -90)]),
    "Rack_Faceplate_Right": (load("Rack_Faceplate_Right.step"), [((1, 0, 0), -90)]),
    # 28 Oct: the clean front (brick lead behind the faceplate): no DC-IN window, no notch
    "Rack_Faceplate_2U_10in_clean": (R.faceplate(dcin_window=False), [((1, 0, 0), -90)]),
}
if __name__ == "__main__":
    for nm, (shape, rots) in parts.items():
        assert len(shape.solids().vals()) == 1, nm
        p = to_bed(shape, rots)
        cq.exporters.export(p, os.path.join(OUT, "STL_for_printing", nm + ".stl"), tolerance=0.02, angularTolerance=0.1)
        cq.exporters.export(shape, os.path.join(OUT, "STEP_for_Onshape", nm + ".step"))
        bb = p.val().BoundingBox()
        print(f"{nm:34s} on the bed {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:5.1f}  valid={shape.val().isValid()}")
