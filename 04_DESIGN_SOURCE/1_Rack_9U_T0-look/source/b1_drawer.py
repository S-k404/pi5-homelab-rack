"""
NIIMBOT B1 pull-out drawer — 10-inch 2U rack unit
Coordinates (mm): x = right, y = up, z = backward (depth). Rack front face at z = 0.
Parts: carcass (fixed sleeve with front collar), tray (slides), fascia (front of tray),
left/right rack ears. Matches the Pi 5 2U unit: 254 x 88.1 mm panel, slots 236.5 mm apart.
"""
import cadquery as cq

# ---------------- parameters ----------------
PANEL_W, PANEL_H = 254.0, 88.1
SLOT_PITCH_X = 236.5          # 10-inch rack hole centres
SLOT_Y = PANEL_H / 2 - 5.95   # EIA outer holes of a 2U panel (38.1 from centre)
SLOT_L, SLOT_W = 10.0, 6.6    # takes M6 or #10-32 (RackMate uses #10-32)

B1 = (91.0, 62.0, 132.0)      # NIIMBOT B1  W x H x L  (published 132 x 91 x 62)

CAR_W, CAR_H, CAR_D = 214.0, 86.0, 178.0   # carcass outer
WALL = 3.0
FLOOR_TOP = -CAR_H / 2 + WALL               # -40
CEIL = CAR_H / 2 - WALL                     # +40
COLLAR_D = 20.0
OPEN_HALF_W = 96.0                          # collar opening x = +/-96
OPEN_TOP = 35.0                             # collar opening y = -40 .. 35
REBATE_X0 = 99.0                            # ear rebate x 99..107, 4 deep
EAR_T = 4.0
INSERT_D, INSERT_DEPTH = 4.0, 6.0           # M3 heat-set inserts
EAR_SCREW_X, EAR_SCREW_Y = 103.0, 30.0

TRAY_HALF_W = 95.5
TRAY_L = 174.0
TRAY_WALL = 2.4
TRAY_FLOOR = 2.4
SIDE_TOP = FLOOR_TOP + TRAY_FLOOR + 25.0    # low locating walls (-12.6)
FRONT_WALL_T, FRONT_WALL_TOP = 8.0, 20.0
POCKET_W, POCKET_L = 95.0, 136.0            # 2 mm clearance round the B1
TAB_W, TAB_T, TAB_TOP = 14.0, 5.0, CEIL - 1.0

FASCIA_HALF_W, FASCIA_T, FASCIA_TOP = 101.0, 4.0, 39.0
TRAVEL = (TRAY_L - TAB_T) - (COLLAR_D + (TAB_TOP - OPEN_TOP))   # tab front vs chamfered lip


def box(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY")
            .box(x1 - x0, y1 - y0, z1 - z0, centered=False)
            .translate((x0, y0, z0)))


def cyl_z(x, y, z0, z1, d):
    return (cq.Workplane("XY").circle(d / 2).extrude(z1 - z0)
            .translate((x, y, z0)))


def prism_yz(pts, x0, x1):
    """triangle in (y,z) extruded along x"""
    return (cq.Workplane("YZ").polyline(pts).close().extrude(x1 - x0)
            .translate((x0, 0, 0)))


def prism_xz(pts, y0, y1):
    """triangle in (x,z) extruded along y"""
    wp = cq.Workplane("XZ").polyline([(x, z) for x, z in pts]).close().extrude(-(y1 - y0))
    return wp.translate((0, y0, 0))


# ---------------- carcass ----------------
def carcass():
    hw, hh = CAR_W / 2, CAR_H / 2
    c = box(-hw, hw, -hh, hh, 0, CAR_D)
    c = c.cut(box(-hw + WALL, hw - WALL, FLOOR_TOP, CEIL, COLLAR_D, CAR_D + 1))      # open back
    c = c.cut(box(-OPEN_HALF_W, OPEN_HALF_W, FLOOR_TOP, OPEN_TOP, -1, COLLAR_D + 1))  # drawer opening
    # 45-degree chamfers on the back of the collar lips (print without supports, back face down)
    c = c.union(prism_yz([(OPEN_TOP, COLLAR_D), (CEIL, COLLAR_D), (CEIL, COLLAR_D + (CEIL - OPEN_TOP))],
                         -hw + WALL, hw - WALL))
    lip = hw - WALL - OPEN_HALF_W
    for s in (1, -1):
        pts = [(s * OPEN_HALF_W, COLLAR_D), (s * (hw - WALL), COLLAR_D), (s * (hw - WALL), COLLAR_D + lip)]
        c = c.union(prism_xz(pts, FLOOR_TOP, CEIL))
    # ear rebates + M3 insert holes
    for s in (1, -1):
        x0, x1 = sorted((s * REBATE_X0, s * (hw + 1)))
        c = c.cut(box(x0, x1, -hh - 1, hh + 1, -1, EAR_T))
        for y in (EAR_SCREW_Y, -EAR_SCREW_Y):
            c = c.cut(cyl_z(s * EAR_SCREW_X, y, EAR_T - 0.1, EAR_T + INSERT_DEPTH, INSERT_D))
    # vent slots in the top (keeps the closed drawer from trapping heat, saves plastic)
    for i in range(7):
        x = -72 + i * 24
        c = c.cut(box(x - 4, x + 4, CEIL - 1, hh + 1, 40, 150))
    return c


# ---------------- tray ----------------
POCKET_X0 = -TRAY_HALF_W + TRAY_WALL
POCKET_X1 = POCKET_X0 + POCKET_W
DIV_X1 = POCKET_X1 + TRAY_WALL
POCKET_Z0 = FRONT_WALL_T
POCKET_Z1 = POCKET_Z0 + POCKET_L
POCKET_CX = (POCKET_X0 + POCKET_X1) / 2


def tray():
    hw = TRAY_HALF_W
    y0 = FLOOR_TOP
    yf = y0 + TRAY_FLOOR
    t = box(-hw, hw, y0, yf, 0, TRAY_L)                                   # floor
    t = t.union(box(-hw, -hw + TRAY_WALL, y0, SIDE_TOP, 0, TRAY_L))        # side walls
    t = t.union(box(hw - TRAY_WALL, hw, y0, SIDE_TOP, 0, TRAY_L))
    t = t.union(box(-hw, hw, y0, FRONT_WALL_TOP, 0, FRONT_WALL_T))         # front wall
    t = t.union(box(POCKET_X1, DIV_X1, y0, SIDE_TOP, 0, POCKET_Z1 + TRAY_WALL))   # divider
    t = t.union(box(-hw, hw, y0, SIDE_TOP, POCKET_Z1, POCKET_Z1 + TRAY_WALL))     # pocket back
    t = t.union(box(-hw, hw, y0, SIDE_TOP, TRAY_L - TAB_T, TRAY_L))               # rear wall
    for s in (1, -1):                                                       # travel-stop tabs
        x0, x1 = sorted((s * hw, s * (hw - TAB_W)))
        t = t.union(box(x0, x1, y0, TAB_TOP, TRAY_L - TAB_T, TRAY_L))
    # USB-C cable notches (pocket back + rear wall) behind the printer
    for z0, z1 in ((POCKET_Z1 - 1, POCKET_Z1 + TRAY_WALL + 1), (TRAY_L - TAB_T - 1, TRAY_L + 1)):
        t = t.cut(box(POCKET_CX - 8, POCKET_CX + 8, yf + 1.2, SIDE_TOP + 1, z0, z1))
    # finger notches either side of the printer, to lift it out
    zc = POCKET_Z0 + POCKET_L / 2
    t = t.cut(box(-hw - 1, -hw + TRAY_WALL + 1, yf + 8, SIDE_TOP + 1, zc - 20, zc + 20))
    t = t.cut(box(POCKET_X1 - 1, DIV_X1 + 1, yf + 8, SIDE_TOP + 1, zc - 20, zc + 20))
    # M3 inserts in the front wall for the fascia
    for x in (-60, 60):
        t = t.cut(cyl_z(x, 0, -0.1, INSERT_DEPTH, INSERT_D))
    return t


# ---------------- fascia ----------------
def fascia():
    f = box(-FASCIA_HALF_W, FASCIA_HALF_W, FLOOR_TOP, FASCIA_TOP, -FASCIA_T, 0)
    grip = (cq.Workplane("XY").slot2D(70, 13).extrude(FASCIA_T + 2)
            .translate((0, 28.5, -FASCIA_T - 1)))
    f = f.cut(grip)
    for x in (-60, 60):   # countersunk M3 from the front
        f = f.cut(cyl_z(x, 0, -FASCIA_T - 1, 1, 3.4))
        f = f.cut(cq.Workplane("XY").circle(3.25).workplane(offset=3.25 - 1.7).circle(1.7)
                  .loft().translate((x, 0, -FASCIA_T)))
    return f


# ---------------- ears ----------------
def ear(side=1):
    x_in, x_out = side * REBATE_X0, side * PANEL_W / 2
    x0, x1 = sorted((x_in, x_out))
    e = box(x0, x1, -PANEL_H / 2, PANEL_H / 2, 0, EAR_T)
    sx = side * SLOT_PITCH_X / 2
    for y in (SLOT_Y, -SLOT_Y):
        e = e.cut(cq.Workplane("XY").slot2D(SLOT_L, SLOT_W).extrude(EAR_T + 2)
                  .translate((sx, y, -1)))
    for y in (EAR_SCREW_Y, -EAR_SCREW_Y):
        e = e.cut(cyl_z(side * EAR_SCREW_X, y, -1, EAR_T + 1, 3.4))
        e = e.cut(cq.Workplane("XY").circle(3.25).workplane(offset=1.6).circle(1.7)
                  .loft().translate((side * EAR_SCREW_X, y, 0)))
    return e


def b1_dummy():
    w, h, l = B1
    x0 = POCKET_X0 + (POCKET_W - w) / 2
    return box(x0, x0 + w, FLOOR_TOP + TRAY_FLOOR, FLOOR_TOP + TRAY_FLOOR + h,
               POCKET_Z0 + 0.5, POCKET_Z0 + 0.5 + l)


if __name__ == "__main__":
    print("travel", TRAVEL)
