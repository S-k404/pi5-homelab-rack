"""
Printable 10-inch 8U mini rack in the style of the DeskPi RackMate T0 that Jeff Geerling used for
Mini Rack 001 and 002: 280 W x 200 D, solid side walls with the rails built into the front and rear
posts, a perforated top cap, two U handles on top and feet at the four corners. It is 8U tall
(like the RackMate T1) so it holds the Pi unit (2U), the B1 face-out dock (3U) and the 7" screen (3U).

Parts (all fit a 220 mm bed):
  side module 2U base (x2)   wall + posts + ribs, plinth with corner feet and base-bar ledges
  side module 3U (x4)        wall + posts + ribs (the middle and the top modules are the same part)
  cap half (x2)              perforated top, front/rear bands, corner columns, dovetails at the seam
  handle (x2), base bar (x3)
Every right-hand part is front/rear symmetric, so the left-hand one is the same part turned 180 degrees.

Joints: module to module, three M5 x 12 screws per side down through the upper module's bottom rib into
heat-set inserts in the lower module's top rib, plus two keys that drop into pockets. Cap to the top
modules: four M5 x 12 screws (the top modules' key pockets are simply unused under the cap). Handles: four M5 x 12 into inserts in the cap columns. Base bars: two M5 x 12
each, from below through the ledges into inserts in the bar ends. Units: M5 inserts in the rails.

Coordinates (mm): x across (0 = centre), y up (0 = bottom of the rack space), z depth (0 = front rail face).
"""
import math
import cadquery as cq
from b1_drawer import box, cyl_z

U = 44.45
MODULES = (2, 3, 3)               # bottom to top: Pi unit, B1 dock, 7" screen
H = sum(MODULES) * U              # 355.6
D = 200.0                         # depth, as the RackMate T0 / T1
X_OUT = 140.0                     # 280 mm overall
WALL = 1.6                        # side wall skin (8 layers)
X_WALL = X_OUT - WALL             # inside face of the wall
X_IN = 112.0                      # inner face of the posts and ribs: 224 mm clear opening
HOLE_X = 236.525 / 2              # EIA-310 10-inch hole spacing
EIA = (6.35, 22.225, 38.1)        # hole offsets inside each U
POST = 14.0                       # post depth: front z 0..14, rear D-14..D
RIB = 4.0                         # top and bottom ribs
RIB_X0 = 122.0                    # ribs run from here out to the wall (the posts reach in to X_IN)
INS_D, INS_DEPTH = 6.4, 10.0      # M5 heat-set insert hole
CLR = 5.5                         # M5 clearance hole
CB_D = 10.5                       # counterbore for an M5 button head
CHAMFER = 1.0                     # outer front and rear edges of the walls
SCREW_X = 129.0                   # module-joint and cap screws run along the middle of the ribs
JOINT_Z = (24.0, D / 2, D - 24.0)
BOSS = 13.0
KEY_Z = (62.0, D - 62.0)          # alignment keys at every joint (module/module and cap/module)
KEY_X0, KEY_L, KEY_DROP = 124.0, 10.0, 3.0
FIT = 0.25

# plinth: the 2U base module's walls carry on below the rack space to the desk
PLINTH = 20.0
RELIEF = 3.0                      # wall bottom stands 3 mm up between the corner feet
PAD_L, PAD_T = 30.0, 8.0          # corner feet (rubber feet stick under these)
LEDGE_X = 100.0                   # base-bar ledges reach in to here (below the rack space only)
LAP_H = 11.0                      # base-bar end laps: y -11..0, sitting on the ledges
LEDGE_Z = ((1.0, 12.0), (80.0, 92.0), (D - 92.0, D - 80.0), (D - 12.0, D - 1.0))
BAR_Z = (LEDGE_Z[0], LEDGE_Z[1], LEDGE_Z[3])     # front, middle (Pi shelf rest), rear
BAR_SCREW_X = (LEDGE_X + X_IN) / 2               # 106

# cap
CAP_H = 30.0
PT = 2.0                          # perforated top plate
BAND_T = 3.0                      # front and rear bands
SEAM, SEAM_W, SEAM_H = 0.2, 12.0, 6.0
DOVE_Z = (50.0, D - 50.0)         # right half: tab at the first, socket at the second
COL_Z = ((0.0, 56.0), (D - 56.0, D))
COL_X0 = 118.0                    # corner columns: x 118..140, on the top ribs and the posts
CB_FLOOR = 5.0                    # column material under the cap-screw heads
SLOT_W, SLOT_L = 3.5, 9.0         # vent slots (x by z), like the T0's punched grid
SLOT_X = [18.5 + 7.0 * i for i in range(13)]
SLOT_Z = [15.0 + 13.0 * j for j in range(14)]

# handles (RackMate-style U handles over the side walls, running front to back)
HANDLE_X, HANDLE_T = 128.0, 14.0
RISE, GRIP = 45.0, 14.0
LEG_Z0, LEG_L = 14.0, 26.0        # front leg z 14..40, rear leg mirrored
FOOT_Z = (48.0, D - 48.0)         # one screw per leg, through a foot tab into the cap column
FOOT_T = 8.0
EYE_D = 11.0                      # round hole through each leg, like the T0's handles


def cyl_x(x0, x1, y, z, d):
    return cq.Workplane("YZ").circle(d / 2).extrude(x1 - x0).translate((x0, y, z))


def cyl_y(x, z, y0, y1, d):
    return cq.Workplane("XZ").circle(d / 2).extrude(-(y1 - y0)).translate((x, y0, z))


def prism_y(pts_xz, y0, y1):
    return cq.Workplane("XZ").polyline(pts_xz).close().extrude(-(y1 - y0)).translate((0, y0, 0))


def mirror_lr(s):
    """right side -> left side: turn 180 degrees about the vertical axis through the rack centre"""
    return s.rotate((0, 0, D / 2), (0, 1, D / 2), 180)


def module_bottoms():
    return [sum(MODULES[:i]) * U for i in range(len(MODULES))]


def side_module(n, base=False):
    """right-hand side module, n U tall, in its own frame (y = 0 at its bottom joint)"""
    Hm = n * U
    yb = -PLINTH if base else 0.0                                  # bottom of posts / feet
    yw = -PLINTH + RELIEF if base else 0.0                          # bottom of the wall between the feet
    m = box(X_WALL, X_OUT, yw, Hm, 0, D)                           # wall
    for z0, z1 in ((0, POST), (D - POST, D)):
        m = m.union(box(X_IN, X_OUT, yb, Hm, z0, z1))              # posts with the rails
    m = m.union(box(RIB_X0, X_OUT, Hm - RIB, Hm, 0, D))            # top rib
    if base:
        m = m.union(box(RIB_X0, X_OUT, yw, yw + RIB, 0, D))        # plinth rib
        for z0, z1 in ((0, PAD_L), (D - PAD_L, D)):
            m = m.union(box(X_IN, X_OUT, yb, yb + PAD_T, z0, z1))  # corner feet
        for z0, z1 in LEDGE_Z:
            m = m.union(box(LEDGE_X, X_OUT, yw, -LAP_H, z0, z1))   # base-bar ledges
    else:
        m = m.union(box(RIB_X0, X_OUT, 0, RIB, 0, D))              # bottom rib
        for kz in KEY_Z:                                           # keys drop into the module below
            m = m.union(box(KEY_X0, X_WALL, -KEY_DROP, 0.01, kz - KEY_L / 2, kz + KEY_L / 2))
    # bosses under the top rib: joint inserts and key pockets, run out to the wall so they print on it
    for zc in JOINT_Z:
        m = m.union(box(SCREW_X - BOSS / 2, X_OUT, Hm - 12, Hm, zc - BOSS / 2, zc + BOSS / 2))
    for kz in KEY_Z:
        m = m.union(box(KEY_X0 - 3, X_OUT, Hm - 8, Hm, kz - KEY_L / 2 - 3, kz + KEY_L / 2 + 3))
    # chamfer the outer front and rear edges
    for zc, s in ((0.0, 1), (D, -1)):
        tri = [(X_OUT + 1, zc - s * 1), (X_OUT - CHAMFER - 1, zc - s * 1), (X_OUT + 1, zc + s * (CHAMFER + 1))]
        m = m.cut(prism_y(tri, yb - 1, Hm + 1))
    # rail holes: M5 inserts front and rear at every EIA position
    for k in range(n):
        for off in EIA:
            y = k * U + off
            m = m.cut(cyl_z(HOLE_X, y, -0.1, INS_DEPTH, INS_D))
            m = m.cut(cyl_z(HOLE_X, y, D - INS_DEPTH, D + 0.1, INS_D))
    # joint inserts in the top rib, clearance holes in the bottom rib
    for zc in JOINT_Z:
        m = m.cut(cyl_y(SCREW_X, zc, Hm - INS_DEPTH, Hm + 0.1, INS_D))
        if not base:
            m = m.cut(cyl_y(SCREW_X, zc, -0.1, RIB + 0.1, CLR))
    for kz in KEY_Z:
        m = m.cut(box(KEY_X0 - FIT, X_WALL, Hm - KEY_DROP - 0.3, Hm + 0.1,
                      kz - KEY_L / 2 - FIT, kz + KEY_L / 2 + FIT))
    if base:                                                       # base-bar screws come up from below
        for z0, z1 in LEDGE_Z:
            zc = (z0 + z1) / 2
            m = m.cut(cyl_y(BAR_SCREW_X, zc, yw - 0.1, -LAP_H + 0.1, CLR))
            m = m.cut(cyl_y(BAR_SCREW_X, zc, yw - 0.1, yw + 2.0, CB_D))
    return m


def base_bar(z0, z1):
    """cross bar under the bottom unit; the end laps sit on the ledges of the two base modules"""
    xm, xe = LEDGE_X - 0.3, X_IN - 0.3
    yw = -PLINTH + RELIEF
    b = box(-xm, xm, yw, 0, z0, z1)
    for s in (1, -1):
        a0, a1 = sorted((s * xm, s * xe))
        b = b.union(box(a0, a1, -LAP_H, 0, z0, z1))
        b = b.cut(cyl_y(s * BAR_SCREW_X, (z0 + z1) / 2, -LAP_H - 0.1, -LAP_H + INS_DEPTH, INS_D))
    return b


def dovetail(x_sign, zc, grow=0.0):
    """dovetail in plan (x, z): neck 8 at the seam, head 12 at 8 deep, going towards x_sign"""
    pts = [(SEAM - x_sign * 1.0, zc - 4 - grow), (SEAM + x_sign * (8 + grow), zc - 6 - grow),
           (SEAM + x_sign * (8 + grow), zc + 6 + grow), (SEAM - x_sign * 1.0, zc + 4 + grow)]
    if x_sign < 0:
        pts[0] = (SEAM, pts[0][1])
        pts[3] = (SEAM, pts[3][1])
    return prism_y(pts, H + CAP_H - SEAM_H, H + CAP_H)


def cap_half():
    """right-hand half of the top cap, in place. The left half is the same part turned round."""
    y0, y1 = H, H + CAP_H
    t = box(SEAM, X_OUT, y1 - PT, y1, 0, D)                        # perforated top plate
    t = t.union(box(SEAM, X_OUT, y0, y1, 0, BAND_T))               # front band
    t = t.union(box(SEAM, X_OUT, y0, y1, D - BAND_T, D))           # rear band
    t = t.union(box(X_WALL, X_OUT, y0, y1, 0, D))                  # side band, flush with the wall
    for za, zb in COL_Z:
        t = t.union(box(COL_X0, X_OUT, y0, y1, za, zb))            # corner columns on the top ribs
    t = t.union(box(SEAM, SEAM + SEAM_W, y1 - SEAM_H, y1, BAND_T, D - BAND_T))
    t = t.union(dovetail(-1, DOVE_Z[0]))                           # tab into the other half
    t = t.cut(dovetail(1, DOVE_Z[1], grow=0.2))                    # socket for the other half's tab
    slots = (cq.Workplane("XZ").pushPoints([(x, z) for x in SLOT_X for z in SLOT_Z])
             .rect(SLOT_W, SLOT_L).extrude(-(PT + 2)).translate((0, y1 - PT - 1, 0)))
    t = t.cut(slots)
    for zc in (JOINT_Z[0], JOINT_Z[2]):                            # cap screws down into the top ribs
        t = t.cut(cyl_y(SCREW_X, zc, y0 - 0.1, y1 + 0.1, CLR))
        t = t.cut(cyl_y(SCREW_X, zc, y0 + CB_FLOOR, y1 + 0.1, CB_D))
    for fz in FOOT_Z:                                              # handle inserts
        t = t.cut(cyl_y(HANDLE_X, fz, y1 - INS_DEPTH, y1 + 0.1, INS_D))
    for zc, s in ((0.0, 1), (D, -1)):                              # same edge chamfer as the walls
        tri = [(X_OUT + 1, zc - s * 1), (X_OUT - CHAMFER - 1, zc - s * 1), (X_OUT + 1, zc + s * (CHAMFER + 1))]
        t = t.cut(prism_y(tri, y0 - 1, y1 + 1))
    return t


def handle():
    """right-hand U handle over the side wall, front to back, with a round eye in each leg"""
    y0 = H + CAP_H
    hx0, hx1 = HANDLE_X - HANDLE_T / 2, HANDLE_X + HANDLE_T / 2
    za, zb = LEG_Z0, D - LEG_Z0
    h = box(hx0, hx1, y0, y0 + RISE, za, zb)
    h = h.cut(box(hx0 - 1, hx1 + 1, y0 - 1, y0 + RISE - GRIP, za + LEG_L, zb - LEG_L))
    h = h.edges("|X and >Y").fillet(6.0)
    for fz in FOOT_Z:                                              # foot tabs reach in from each leg
        f0, f1 = (za + LEG_L - 1, fz + 8) if fz < D / 2 else (fz - 8, zb - LEG_L + 1)
        h = h.union(box(hx0, hx1, y0, y0 + FOOT_T, f0, f1))
        h = h.cut(cyl_y(HANDLE_X, fz, y0 - 0.1, y0 + FOOT_T + 0.1, CLR))
        h = h.cut(cyl_y(HANDLE_X, fz, y0 + FOOT_T - 3.0, y0 + FOOT_T + 0.1, CB_D))
    for z0 in (za - 1, zb - LEG_L - 1):
        h = h.cut(cyl_z(HANDLE_X, y0 + 19.0, z0, z0 + LEG_L + 2, EYE_D))
    return h


def assembly():
    parts = {}
    for i, (n, yb) in enumerate(zip(MODULES, module_bottoms())):
        m = side_module(n, base=(i == 0)).translate((0, yb, 0))
        parts[f"side_{i}_{n}U_R"] = m
        parts[f"side_{i}_{n}U_L"] = mirror_lr(m)
    for nm, (z0, z1) in zip(("front", "middle", "rear"), BAR_Z):
        parts[f"bar_{nm}"] = base_bar(z0, z1)
    c = cap_half()
    parts["cap_R"], parts["cap_L"] = c, mirror_lr(c)
    hd = handle()
    parts["handle_R"], parts["handle_L"] = hd, mirror_lr(hd)
    return parts


if __name__ == "__main__":
    for nm, s in (("base2U", side_module(2, True)), ("mod3U", side_module(3)), ("bar", base_bar(*BAR_Z[0])),
                  ("cap", cap_half()), ("handle", handle())):
        v = s.val(); bb = v.BoundingBox()
        print(nm, v.isValid(), len(s.solids().vals()), round(v.Volume()),
              [round(a, 1) for a in (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax)])
