"""
7-inch display module — 10-inch 3U rack unit for the REES52 7" 1024x600 HDMI capacitive-touch screen.
Published size of the screen: 165 x 100 x 5 mm, active area 154.08 x 85.92 mm, 5 V 1-2 A, USB touch.
The glass sits in a pocket behind a bezel and is held by four corner clips; the HDMI driver board and touch
controller ride on a slotted tray behind it (zip ties or foam tape). The ears are the same part as the B1 dock's.
Coordinates (mm): x across, y up (0 = centre), z back. The ears' back face is z = 3 (rail face).
"""
import cadquery as cq
from b1_drawer import box, cyl_z
from b1_dock import PANEL_H, EAR_T, EAR_SCREW_X, EAR_SCREW_Y, INSERT_D, INSERT_DEPTH, ear  # noqa: F401

GLASS = (165.0, 100.0, 5.0)        # measure yours: W x H x thickness
ACTIVE = (154.08, 85.92)
WINDOW = (156.0, 88.0)             # bezel opening, 1 mm round the active area
FIT = 0.3                          # clearance round the glass
BODY_W, BODY_H = 214.0, 130.0
Z0 = EAR_T                         # body front face
FACE_T = 2.4                       # bezel thickness
WALL = 2.4                         # glass pocket wall
FOAM = 1.0                         # foam tape between the clips and the glass
TRAY_D = 70.0                      # tray depth behind the front face
TRAY_T = 2.4
CLIP = 16.0                        # corner clip size
CLIP_T = 3.0
CLIP_POS = (88.0, 55.0)            # clip screw centre (x, y), mirrored to all four corners
M3_INS_D, M3_INS_DEPTH = 4.0, 6.0


def body():
    hw, hh = BODY_W / 2, BODY_H / 2
    gw, gh = GLASS[0] / 2 + FIT, GLASS[1] / 2 + FIT
    zf = Z0 + FACE_T                                               # glass rests against the bezel's back face
    zg = zf + GLASS[2] + FOAM                                      # clips sit here
    b = box(-hw, hw, -hh, hh, Z0, zf)                              # bezel
    b = b.cut(cq.Workplane("XY").rect(*WINDOW).extrude(FACE_T + 2).edges("|Z").fillet(2.0).translate((0, 0, Z0 - 1)))
    # glass pocket walls, gapped in the middle of each side so the ribbon cables can leave on any edge
    walls = box(-gw - WALL, gw + WALL, -gh - WALL, gh + WALL, zf, zg).cut(box(-gw, gw, -gh, gh, zf - 1, zg + 1))
    walls = walls.cut(box(-30, 30, -gh - WALL - 1, gh + WALL + 1, zf - 1, zg + 1))
    walls = walls.cut(box(-gw - WALL - 1, gw + WALL + 1, -25, 25, zf - 1, zg + 1))
    b = b.union(walls)
    # clip bosses at the four corners
    for sx in (1, -1):
        for sy in (1, -1):
            b = b.union(cq.Workplane("XY").circle(4.5).extrude(zg - zf).translate((sx * CLIP_POS[0], sy * CLIP_POS[1], zf)))
    # ear posts with M3 inserts (same positions as the B1 dock)
    for sx in (1, -1):
        x0, x1 = sorted((sx * (EAR_SCREW_X - 6), sx * hw))
        for sy in (1, -1):
            y0, y1 = sorted((sy * (EAR_SCREW_Y - 8), sy * (EAR_SCREW_Y + 8)))
            b = b.union(box(x0, x1, y0, y1, Z0, Z0 + 10))
    # tray for the driver board, with side cheeks tying it to the bezel
    b = b.union(box(-hw + 7, hw - 7, -hh, -hh + TRAY_T, Z0, Z0 + TRAY_D))
    for sx in (1, -1):
        x0, x1 = sorted((sx * (hw - 7), sx * (hw - 9.4)))
        b = b.union(box(x0, x1, -hh, -hh + 40, Z0, Z0 + TRAY_D))
    # zip-tie slots in the tray (3 x 10 mm, on a 20 mm grid) - also make it lighter
    for x in range(-80, 81, 20):
        for z in (20.0, 40.0, 60.0):
            b = b.cut(box(x - 5, x + 5, -hh - 1, -hh + TRAY_T + 1, Z0 + z - 1.5, Z0 + z + 1.5))
    # holes: ear inserts, clip inserts
    for sx in (1, -1):
        for sy in (1, -1):
            b = b.cut(cyl_z(sx * EAR_SCREW_X, sy * EAR_SCREW_Y, Z0 - 0.1, Z0 + INSERT_DEPTH, INSERT_D))
            b = b.cut(cyl_z(sx * CLIP_POS[0], sy * CLIP_POS[1], zg - M3_INS_DEPTH, zg + 0.1, M3_INS_D))
    return b


def clip():
    """corner clip, in place at the (+x, +y) corner: overlaps the glass by ~5 mm, one M3 screw"""
    zg = Z0 + FACE_T + GLASS[2] + FOAM
    cx, cy = CLIP_POS[0] - 2, CLIP_POS[1] - 2
    c = box(cx - CLIP / 2, cx + CLIP / 2, cy - CLIP / 2, cy + CLIP / 2, zg, zg + CLIP_T)
    c = c.cut(cyl_z(CLIP_POS[0], CLIP_POS[1], zg - 1, zg + CLIP_T + 1, 3.4))
    return c


def clips():
    c = clip()
    return [c, c.mirror("YZ"), c.mirror("XZ"), c.mirror("YZ").mirror("XZ")]


def glass_dummy():
    zf = Z0 + FACE_T
    return box(-GLASS[0] / 2, GLASS[0] / 2, -GLASS[1] / 2, GLASS[1] / 2, zf, zf + GLASS[2])


def driver_dummy():
    """typical HDMI driver board + touch controller, sitting on the tray"""
    hh = BODY_H / 2
    return box(-50, 50, -hh + TRAY_T, -hh + TRAY_T + 20, Z0 + 15, Z0 + 65)


if __name__ == "__main__":
    for n, s in (("body", body()), ("clip", clip())):
        v = s.val(); bb = v.BoundingBox()
        print(n, v.isValid(), len(s.solids().vals()), round(v.Volume()),
              [round(a, 1) for a in (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax)])
