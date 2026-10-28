"""
Upright mini server stand — matches the user's Onshape arrangement:
  * Pi 5 and Waveshare adapter stand on edge, side by side in one plane
    (adapter on top, Pi below, Pi USB/Ethernet end to the LEFT, GPIO edge DOWN)
  * Cuzor UPS stands upright IN FRONT of the boards' component side,
    stopping short of the Pi's USB/Ethernet stacks
One printed part (Stand_Upright), one solid.

Modelled in the Pi's own frame (Pi corner = origin, Z out of the component side),
then rotated to the upright orientation for the STEP files:
  world X (right) = -Pi X,  world Y (back) = -Pi Z,  world Z (up) = -Pi Y
Print orientation STL = lying on the back plate (Pi frame, Z up). Units mm.
"""
import os
import cadquery as cq
from cadquery import Assembly, Location, Vector, Color
from OCP.gp import gp_Trsf
import build, stand

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stand_v2_out")
os.makedirs(OUT, exist_ok=True)


def box(x0, y0, z0, dx, dy, dz):
    return cq.Workplane("XY").box(dx, dy, dz, centered=False).translate((x0, y0, z0))


def span(a0, a1):
    return a0, a1 - a0


# ---------------- layout (Pi frame) ---------------------------------------
STANDOFF_H = 5.0               # board underside at Z=0, back plate below
BACK_T = 3.0
BACK_Z0 = -STANDOFF_H - BACK_T  # -8

# UPS envelope (100 along Pi Y, 80 along Pi X, 28 deep along Pi Z)
AIR_GAP = 8.0                  # fan intake gap above the tallest part under the UPS
TALLEST_UNDER = 15.1           # adapter RJ45 / Armor Lite top above board underside
UPS_X0, UPS_X1 = -11.5, 68.5   # ends before the Pi's USB/Ethernet stacks
UPS_Y0, UPS_Y1 = -54.0, 46.0
UPS_Z0 = TALLEST_UNDER + AIR_GAP          # 23.1
UPS_Z1 = UPS_Z0 + 28.0
C = 0.5                        # clearance around the UPS
WALL, LIP, LIP_IN = 3.0, 2.0, 2.5

# frame extents
X_RIGHT0 = UPS_X0 - C - WALL   # world-right wall (Pi -X side)
FOOT_Y0 = 57.0                 # just below the Pi's lower edge (56)
FOOT_T = 3.0
BACK_X1, BACK_Y0 = 88.0, -60.0
FRONT_Z = UPS_Z1 + C + LIP     # front of the UPS bay

# UGREEN HDMI cradle (on the foot, beyond the Pi's port end)
HF_W, HF_H, HF_L = stand.HDMI_F_W, stand.HDMI_F_H, stand.HDMI_F_L
HC = stand.HDMI_CLEAR
CR_X0 = BACK_X1 + 0.5
CR_IW, CR_IH, CR_IL = HF_W + 2 * HC, HF_H + 2 * HC, HF_L + HC
CR_W = CR_IW + 2 * WALL - 2.0          # 2 mm side walls
CR_X1 = CR_X0 + CR_W
CR_Z0 = BACK_Z0                        # back wall sits on the print bed
CR_Z1 = CR_Z0 + 2.0 + CR_IL
FOOT_X1 = CR_X1


def stand_upright():
    # back plate (boards mount to it)
    s = box(X_RIGHT0, BACK_Y0, BACK_Z0, BACK_X1 - X_RIGHT0, FOOT_Y0 + FOOT_T - BACK_Y0, BACK_T)
    # foot (sits on the desk)
    s = s.union(box(X_RIGHT0, FOOT_Y0, BACK_Z0, FOOT_X1 - X_RIGHT0, FOOT_T, FRONT_Z - BACK_Z0))
    # world-right side wall: back plate -> front of UPS bay
    s = s.union(box(X_RIGHT0, BACK_Y0, BACK_Z0, WALL, FOOT_Y0 + FOOT_T - BACK_Y0, FRONT_Z - BACK_Z0))
    # UPS riser (below UPS) and top strap (above UPS), only in front of the boards
    bay_z0 = UPS_Z0 - C - LIP
    s = s.union(box(X_RIGHT0, UPS_Y1 + C, bay_z0, UPS_X1 - X_RIGHT0, FOOT_Y0 - (UPS_Y1 + C), FRONT_Z - bay_z0))
    s = s.union(box(X_RIGHT0, UPS_Y0 - C - WALL, bay_z0, UPS_X1 - X_RIGHT0, WALL, FRONT_Z - bay_z0))
    # front lips and rear ledges hold the UPS in Z; it slides in from the open left end
    for z0 in (UPS_Z1 + C, bay_z0):
        s = s.union(box(X_RIGHT0, UPS_Y1 + C - LIP_IN, z0, UPS_X1 - X_RIGHT0, LIP_IN, LIP))   # lower edge
        s = s.union(box(X_RIGHT0, UPS_Y0 - C, z0, UPS_X1 - X_RIGHT0, LIP_IN, LIP))            # upper edge
        s = s.union(box(X_RIGHT0 + WALL, UPS_Y0 - C, z0, LIP_IN, UPS_Y1 - UPS_Y0 + 2 * C, LIP))  # right edge
    # windows in the right wall: board zone (microSD, adapter USB-C/terminal) and UPS jack face
    s = s.cut(box(X_RIGHT0 - 0.1, -54.0, -3.0, WALL + 0.2, 108.0, 23.0 - 3.0 + 0.1 - 3.0))
    s = s.cut(box(X_RIGHT0 - 0.1, UPS_Y0 + 6, UPS_Z0 + 3, WALL + 0.2, UPS_Y1 - UPS_Y0 - 12, 22.0))
    # vents in the back plate behind each board
    for y_lo, y_hi in ((8.0, 48.0), (-52.0, -10.0)):
        for i in range(9):
            s = s.cut(box(10.0 + i * 6.0, y_lo, BACK_Z0 - 0.1, 3.0, y_hi - y_lo, BACK_T + 0.2))
    # standoffs (Pi exact, adapter placeholder) with M2.5 pilots
    holes = stand.PI_HOLES + stand.ADAPTER_HOLES
    for hx, hy in holes:
        s = s.union(cq.Workplane("XY").circle(stand.STANDOFF_OD / 2).extrude(STANDOFF_H)
                    .translate((hx, hy, -STANDOFF_H)))
    for hx, hy in holes:   # pilots drilled down into each standoff (and 2 mm into the plate)
        s = s.cut(cq.Workplane("XY").circle(stand.PILOT_D / 2).extrude(STANDOFF_H + 2.0)
                  .translate((hx, hy, -STANDOFF_H - 2.0 + 0.01)))
    # UGREEN HDMI cradle: socket faces the front, snap in from above
    floor_y0 = FOOT_Y0 - 2.0
    top_y = floor_y0 - CR_IH - 1.0
    blk = box(CR_X0, top_y, CR_Z0, CR_W, FOOT_Y0 - top_y, CR_Z1 - CR_Z0)
    blk = blk.cut(box(CR_X0 + 2.0, top_y - 0.1, CR_Z0 + 2.0, CR_IW, floor_y0 - top_y + 0.1, CR_IL + 0.1))
    for xl in (CR_X0 + 2.0, CR_X0 + 2.0 + CR_IW - 1.0):
        blk = blk.union(box(xl, top_y, CR_Z0 + 6.0, 1.0, 1.0, CR_IL - 10.0))
    blk = blk.cut(box(CR_X0 + CR_W / 2 - 3.0, top_y - 0.1, CR_Z0 - 0.1, 6.0, floor_y0 - top_y + 0.1, 2.2))
    s = s.union(blk)
    return s


# ---------------- transforms -------------------------------------------------
class trsf:
    """Rigid transform (3x3 rotation rows + translation) usable as shape.transformShape arg."""
    def __init__(self, rows, t):
        self.tr = gp_Trsf()
        (a, b, c), (d, e, f), (g, h, i) = [[float(v) for v in r] for r in rows]
        self.tr.SetValues(a, b, c, float(t[0]), d, e, f, float(t[1]), g, h, i, float(t[2]))


def xform(shape, t):
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
    return cq.Shape.cast(BRepBuilderAPI_Transform(shape.wrapped, t.tr, True).Shape())


TO_WORLD = trsf(((-1, 0, 0), (0, 0, -1), (0, -1, 0)), (0, 0, FOOT_Y0 + FOOT_T))


def fuse(parts):
    return stand.fuse(parts)


if __name__ == "__main__":
    st = stand_upright().val()
    assert len(st.Solids()) == 1
    bb = st.BoundingBox()
    print(f"Stand (print orientation) {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f}")
    print_shape = st.translate(Vector(0, 0, -BACK_Z0))
    cq.exporters.export(cq.Workplane().add(print_shape), os.path.join(OUT, "Stand_Upright_PRINT.stl"),
                        tolerance=0.02, angularTolerance=0.1)

    ups = fuse(build.cuzor_ups_pro()).rotate(Vector(0, 0, 0), Vector(0, 0, 1), 90).translate(
        Vector((UPS_X0 + UPS_X1) / 2, (UPS_Y0 + UPS_Y1) / 2, UPS_Z0))
    ug = xform(stand.ugreen_cable_end().val(),
        trsf(((0, 1, 0), (0, 0, -1), (-1, 0, 0)), (CR_X0 + 2.0 + HC, FOOT_Y0 - 2.0 - HC, CR_Z1)))
    comps = {
        "Stand_Upright": (st, Color(0.88, 0.48, 0.12)),
        "RaspberryPi5": (fuse(build.raspberry_pi_5()), Color(0.05, 0.45, 0.2)),
        "Waveshare_Adapter_F": (fuse(build.waveshare_adapter_f()).translate(Vector(0, -1.5, 0)), Color(0.1, 0.1, 0.1)),
        "EVM_2230_NVMe": (fuse(build.evm_2230_nvme()).translate(Vector(14.5, -41.5, 3.1)), Color(0.05, 0.2, 0.5)),
        "ArmorLite_V5": (fuse(build.armor_lite_v5()).translate(Vector(32, 28, 3.9)), Color(0.25, 0.25, 0.27)),
        "Cuzor_MiniUPS_Pro": (ups, Color(0.12, 0.12, 0.13)),
        "UGREEN_HDMI_end": (ug, Color(0.05, 0.05, 0.05)),
    }
    names = list(comps)
    clashes = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            v = comps[names[i]][0].intersect(comps[names[j]][0]).Volume()
            if v > 0.5:
                clashes.append((names[i], names[j], round(v, 1)))
    print("clashes:", clashes or "none")

    asm = Assembly(name="Pi5_upright_stand")
    world = {}
    for n, (s, col) in comps.items():
        w = xform(s, TO_WORLD)
        world[n] = w
        asm.add(w, name=n, color=col)
    asm.save(os.path.join(OUT, "Pi5_Upright_ASSEMBLY.step"), exportType="STEP")
    cq.exporters.export(cq.Workplane().add(world["Stand_Upright"]), os.path.join(OUT, "Stand_Upright.step"))
    wb = cq.Compound.makeCompound(list(world.values())).BoundingBox()
    print(f"Assembly upright: W {wb.xlen:.1f} x D {wb.ylen:.1f} x H {wb.zlen:.1f}; zmin {wb.zmin:.2f}")
