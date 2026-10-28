"""
Export the T0-look rack: print-ready STLs (each laid out on the bed), STEP files for Onshape, an assembly STEP
with the units in place, and preview images. Usage: python export_rack.py <Pi unit STEP folder> <output folder>
"""
import os
import sys
import cadquery as cq
import rack_t0 as r
import units as un
from render import render

PI_STEP, OUT = sys.argv[1], sys.argv[2]
for sub in ("STL_for_printing", "STEP_for_Onshape", "images"):
    os.makedirs(os.path.join(OUT, sub), exist_ok=True)


def to_bed(shape, rots):
    s = shape
    for axis, ang in rots:
        s = s.rotate((0, 0, 0), axis, ang)
    bb = s.val().BoundingBox()
    return s.translate((-bb.xmin, -bb.ymin, -bb.zmin))


prints = {
    "Rack_SideModule_2U_Base_x2": (r.side_module(2, base=True), [((0, 1, 0), 90)]),   # outer face down
    "Rack_SideModule_3U_x4": (r.side_module(3), [((0, 1, 0), 90)]),                   # outer face down
    "Rack_SideModule_1U_Top_x2": (r.side_module(1), [((0, 1, 0), 90)]),               # outer face down
    "Rack_CapHalf_x2": (r.cap_half(), [((1, 0, 0), -90)]),                            # perforated top down
    "Rack_Handle_x2": (r.handle(), [((0, 1, 0), 90)]),                                # on its side
    "Rack_BaseBar_x3": (r.base_bar(*r.BAR_Z[0]), [((0, 0, 1), 45)]),                  # front face down, diagonal
}
if __name__ == "__main__":
    for name, (shape, rots) in prints.items():
        p = to_bed(shape, rots)
        bb = p.val().BoundingBox()
        print(f"{name:30s} on the bed {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:5.1f}")
        cq.exporters.export(p, os.path.join(OUT, "STL_for_printing", name + ".stl"), tolerance=0.05, angularTolerance=0.1)
        cq.exporters.export(shape, os.path.join(OUT, "STEP_for_Onshape", name + ".step"))

    P = r.assembly()
    PI = un.pi_unit(PI_STEP)
    DOCK, DISP, UCG = un.dock_parts(), un.display_parts(), un.ucg_parts()
    asm = cq.Assembly()
    for n, s in P.items():
        asm.add(s, name=n, color=cq.Color(0.78, 0.80, 0.82))
    for n, s in {**PI, **DOCK, **DISP, **UCG}.items():
        col = (cq.Color(0.3, 0.62, 0.88) if n.startswith("B1 (") else
               cq.Color(0.94, 0.94, 0.95) if n == "UCG-Ultra" else cq.Color(0.2, 0.21, 0.23))
        asm.add(s, name=n.replace(" ", "_").replace('"', "in").replace("(", "").replace(")", ""), color=col)
    asm.export(os.path.join(OUT, "STEP_for_Onshape", "Rack_9U_T0look_ASSEMBLY_with_units.step"))

    silver, dark, black, blue = "#c8ccd1", "#45484d", "#1d1f22", "#4f9fe0"
    rack = [(s, silver) for s in P.values()]
    pi = [(PI["Pi faceplate"], dark), (PI["Pi shelf"], dark), (PI["Pi lid"], "#2e3135"),
          (PI["Pi board tray"], "#2e3135"), (PI["Pi UPS tray"], "#2e3135")]
    dock = [(DOCK["B1 dock"], dark), (DOCK["dock ear R"], black), (DOCK["dock ear L"], black), (DOCK["B1 (67 mm)"], blue)]
    disp = [(DISP["display"], dark), (DISP["screen glass"], black), (DISP["display ear R"], black), (DISP["display ear L"], black)]
    ucg = [(UCG["UCG shelf"], dark), (UCG["UCG-Ultra"], "#eef0f2")]
    loaded = rack + pi + dock + disp + ucg
    lims = ((-160, 160), (-20, 220), (-30, 485))
    render(loaded, os.path.join(OUT, "images", "rack_loaded.png"), 14, 35,
           "RackMate T0 look, 9U: Pi unit, B1 dock, 7-inch screen, UCG-Ultra", lims)
    render(loaded, os.path.join(OUT, "images", "rack_front.png"), 4, 90,
           "Front: 280 mm wide, units on the built-in rails", lims)
    render(rack, os.path.join(OUT, "images", "rack_empty.png"), 22, 30,
           "Empty: side modules, cap with vent grid, U handles, corner feet", lims)
    render(loaded, os.path.join(OUT, "images", "rack_back.png"), 16, -140,
           "Back: open for cables, rear rails for a PDU", lims)
    # exploded view of one side
    ex = []
    for i, (n, yb) in enumerate(zip(r.MODULES, r.module_bottoms())):
        ex.append((r.side_module(n, base=(i == 0)).translate((0, yb + 25 * i, 0)), silver))
    ex.append((r.cap_half().translate((0, 25 * len(r.MODULES), 0)), silver))
    ex.append((r.handle().translate((0, 25 * len(r.MODULES) + 25, 0)), silver))
    for z0, z1 in r.BAR_Z:
        ex.append((r.base_bar(z0, z1).translate((-60, -20, 0)), "#9aa0a6"))
    render(ex, os.path.join(OUT, "images", "rack_exploded.png"), 18, 30,
           "One side, exploded: 2U base, two 3U modules, 1U top module, cap half, handle, base bars",
           ((-180, 160), (-20, 220), (-60, 610)))
    print("done")
