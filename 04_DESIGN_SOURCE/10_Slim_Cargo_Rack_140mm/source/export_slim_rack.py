"""
Export Slim Cargo Mini Rack (140 mm Depth):
- Print-ready STLs (laid flat for 220x220 mm bed)
- STEP models for each individual part
- Complete 9U Slim Cargo Rack Assembly STEP for Onshape
"""
import os
import sys
import cadquery as cq

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)
import slim_rack as sr

OUT_STL = os.path.abspath(os.path.join(DIR, "..", "STL_for_printing"))
OUT_STEP = os.path.abspath(os.path.join(DIR, "..", "STEP_for_Onshape"))
os.makedirs(OUT_STL, exist_ok=True)
os.makedirs(OUT_STEP, exist_ok=True)

def to_bed(shape, rots):
    s = shape
    for axis, ang in rots:
        s = s.rotate((0, 0, 0), axis, ang)
    bb = s.val().BoundingBox()
    return s.translate((-bb.xmin, -bb.ymin, -bb.zmin))

prints = {
    "SlimCargo_SideModule_2U_Base_x2": (sr.side_module(2, base=True), [((0, 1, 0), 90)]),
    "SlimCargo_SideModule_3U_x4": (sr.side_module(3), [((0, 1, 0), 90)]),
    "SlimCargo_SideModule_1U_Top_x2": (sr.side_module(1), [((0, 1, 0), 90)]),
    "SlimCargo_CapHalf_x2": (sr.cap_half(), [((1, 0, 0), -90)]),
    "SlimCargo_LowProfile_Handle_x2": (sr.handle(), [((0, 1, 0), 90)]),
    "SlimCargo_BaseBar_x3": (sr.base_bar(*sr.BAR_Z[0]), [((0, 0, 1), 45)]),
}

if __name__ == "__main__":
    print("=== Exporting Slim Cargo Rack (140 mm Depth) ===")
    for name, (shape, rots) in prints.items():
        p = to_bed(shape, rots)
        bb = p.val().BoundingBox()
        print(f"{name:35s} Bed: {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:5.1f} mm")
        cq.exporters.export(p, os.path.join(OUT_STL, name + ".stl"), tolerance=0.05, angularTolerance=0.1)
        cq.exporters.export(shape, os.path.join(OUT_STEP, name + ".step"))

    print("\nBuilding Full 9U Slim Cargo Assembly...")
    P = sr.assembly()
    asm = cq.Assembly()
    for n, s in P.items():
        col = cq.Color(0.85, 0.85, 0.87) if "cap" in n or "handle" in n else cq.Color(0.75, 0.77, 0.80)
        asm.add(s, name=n, color=col)

    asm_step_path = os.path.join(OUT_STEP, "SlimCargo_Rack_9U_140mm_ASSEMBLY.step")
    asm.export(asm_step_path)
    print(f"Exported Assembly STEP for Onshape -> {asm_step_path}")
    print("All exports completed successfully!")

