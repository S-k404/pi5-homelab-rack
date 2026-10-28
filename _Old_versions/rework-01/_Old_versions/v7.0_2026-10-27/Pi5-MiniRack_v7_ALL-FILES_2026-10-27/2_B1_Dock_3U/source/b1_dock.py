"""
NIIMBOT B1 face-out dock — 10-inch 3U rack unit (v4: fits a 62 or 67 mm thick B1)
The printer stands with its TOP face (label slot, power button, light, lid) facing out of the
rack, leaned back 8 degrees. Open front window, open top, open back.
Coordinates (mm): x across, y up, z backward (depth). Rack front face at z = 0.
"""
import math
import cadquery as cq
from b1_drawer import box, cyl_z, PANEL_W, SLOT_PITCH_X, SLOT_L, SLOT_W, INSERT_D, INSERT_DEPTH

# ---------------- parameters ----------------
PANEL_H = 3 * 44.45 - 0.8                 # 132.55, 3U
SLOT_Y = PANEL_H / 2 - 5.95               # outer EIA holes of a 3U panel (60.325)
EAR_X0, EAR_T = 99.0, 3.0
EAR_SCREW_X, EAR_SCREW_Y = 103.0, 45.0

B1_L, B1_W, B1_H = 132.0, 91.0, 67.0      # printer: L across, W up (stood on its long side), H = depth
# Listings give the B1 as 62 mm (Walmart, 2.4 in) or 67 mm (Galaxus) thick, so the cradle is sized for 67 and
# two clip-in 5 mm spacers on the back rest take up the difference for a 62 mm printer.
B1_H_THIN = 62.0
SPACER_T = B1_H - B1_H_THIN               # 5 mm
SPACER_X = (28.0, 62.0)                   # one spacer each side of the cable notch
TILT = 8.0                                # lean back, degrees
CLR = 1.5                                 # clearance round the printer

BODY_W, BODY_H, BODY_D = 214.0, 130.0, 95.0
SIDE_T, FLOOR_T = 2.4, 2.4
COLLAR_D = 12.0
WIN_HALF = 95.0                           # front window x = +/-95, open to the top
Y_BOT = -BODY_H / 2                       # -65
FLOOR_TOP = Y_BOT + FLOOR_T               # -62
PIVOT_Z = COLLAR_D + 1.0                  # printer front face 1 mm behind the collar
PIVOT_Y = -48.0                           # printer front-bottom edge
LIP = 2.5                                 # bottom bar stands 2.5 mm above the printer's bottom edge

GUIDE_T, GUIDE_H = 3.0, 18.0
REST_T, REST_H = 3.0, 60.0               # back rest (local), shorter than the printer
NOTCH_HALF_W, NOTCH_Y0 = 25.0, 25.0       # cable notch in the back rest, open at the top
SIDE_WIN_H, SIDE_WIN_W = 104.0, 62.0      # lite windows in the side walls (tall x deep)
RIB, RIB_X = 4.0, (0.0, 34.0, -34.0)      # cradle ribs
SIGIL = False                             # cybersigil cut-outs in the ears (off)


def local_to_world(shape):
    """printer-local frame: front-bottom edge on the x axis, front face at z=0, y up the face"""
    return (shape.rotate((0, 0, 0), (1, 0, 0), TILT)
                 .translate((0, PIVOT_Y, PIVOT_Z)))


def cradle():
    hx = B1_L / 2 + CLR
    zb = B1_H + CLR                                           # back face of the printer + clearance
    # ribs instead of a solid slab: the printer rests on their tilted tops (v3, light)
    c = None
    for xc in RIB_X:
        r = box(xc - RIB / 2, xc + RIB / 2, -40, 0, -4, zb + REST_T)
        c = r if c is None else c.union(r)
    # back rest, full width, down to the floor
    c = c.union(box(-hx - GUIDE_T, hx + GUIDE_T, -40, REST_H, zb, zb + REST_T))
    # low side guides, run down to the floor so they print as plain walls (finger room above them)
    for s in (1, -1):
        x0, x1 = sorted((s * hx, s * (hx + GUIDE_T)))
        c = c.union(box(x0, x1, -40, GUIDE_H, -4, zb))
    # cable notch in the back rest, open at the top (prints without bridging)
    c = c.cut(box(-NOTCH_HALF_W, NOTCH_HALF_W, NOTCH_Y0, REST_H + 1, zb - 1, zb + REST_T + 1))
    # lightening windows in the back rest: below the printer between the ribs, and two in the upper part
    for xa, xb in ((5, 29), (39, 62)):
        for sg in (1, -1):
            x0, x1 = sorted((sg * xa, sg * xb))
            c = c.cut(box(x0, x1, -34, -6, zb - 1, zb + REST_T + 1))
            if xa > 30:
                c = c.cut(box(x0, x1, 8, 50, zb - 1, zb + REST_T + 1))
    c = local_to_world(c)
    # clip to the inside of the body (above the floor, behind the collar, in front of the back)
    keep = box(-BODY_W / 2 + SIDE_T, BODY_W / 2 - SIDE_T, FLOOR_TOP - 0.01, BODY_H / 2, COLLAR_D, BODY_D)
    return c.intersect(keep)


def body():
    hw = BODY_W / 2
    b = box(-hw, hw, Y_BOT, Y_BOT + FLOOR_T, 0, BODY_D)                       # floor
    for s in (1, -1):
        x0, x1 = sorted((s * hw, s * (hw - SIDE_T)))
        b = b.union(box(x0, x1, Y_BOT, -Y_BOT, 0, BODY_D))                     # side walls
        x0, x1 = sorted((s * WIN_HALF, s * hw))
        b = b.union(box(x0, x1, Y_BOT, -Y_BOT, 0, COLLAR_D))                   # collar posts
        x0, x1 = sorted((s * 98.0, s * 106.0))
        b = b.cut(box(x0, x1, -36, 36, 5, COLLAR_D + 0.1))                    # hollow between the ear inserts
    b = b.union(box(-WIN_HALF, WIN_HALF, Y_BOT, PIVOT_Y + LIP, COLLAR_D - 4, COLLAR_D))   # bottom bar = front lip, 4 mm wall
    b = b.union(cradle())
    # ear rebates + M3 inserts
    for s in (1, -1):
        x0, x1 = sorted((s * EAR_X0, s * (hw + 1)))
        b = b.cut(box(x0, x1, Y_BOT - 1, -Y_BOT + 1, -1, EAR_T))
        for y in (EAR_SCREW_Y, -EAR_SCREW_Y):
            b = b.cut(cyl_z(s * EAR_SCREW_X, y, EAR_T - 0.1, EAR_T + INSERT_DEPTH, INSERT_D))
    # thumb scoop in the bottom bar so the printer is easy to tip forward and lift out
    scoop = (cq.Workplane("XY").slot2D(60, 16).extrude(COLLAR_D + 2)
             .translate((0, PIVOT_Y + LIP, -1)))
    b = b.cut(scoop.intersect(box(-40, 40, PIVOT_Y - 6, PIVOT_Y + LIP + 1, -2, COLLAR_D + 2)))
    # floor windows between the ribs (open to the bed, so no overhangs)
    for xa, xb in ((5, 29), (39, 62), (76, 100)):
        for sg in (1, -1):
            x0, x1 = sorted((sg * xa, sg * xb))
            b = b.cut(box(x0, x1, Y_BOT - 1, FLOOR_TOP + 0.5, 24, 84))
    # lite cut-outs (idea from the B1 Pro wall organizer): tall rounded windows in both side walls.
    # Saves filament and lets air through; rounded ends print without bridging.
    zc = COLLAR_D + (BODY_D - COLLAR_D) / 2
    for x0 in (hw - SIDE_T - 1, -hw - 1):
        win = (cq.Workplane("YZ").center(0, zc).slot2D(SIDE_WIN_H, SIDE_WIN_W).extrude(SIDE_T + 2)
               .translate((x0, 0, 0)))
        b = b.cut(win)
    return b


def ear(side=1):
    x0, x1 = sorted((side * EAR_X0, side * PANEL_W / 2))
    e = box(x0, x1, -PANEL_H / 2, PANEL_H / 2, 0, EAR_T)
    for y in (SLOT_Y, -SLOT_Y):
        e = e.cut(cq.Workplane("XY").slot2D(SLOT_L, SLOT_W).extrude(EAR_T + 2)
                  .translate((side * SLOT_PITCH_X / 2, y, -1)))
    for y in (EAR_SCREW_Y, -EAR_SCREW_Y):
        e = e.cut(cyl_z(side * EAR_SCREW_X, y, -1, EAR_T + 1, 3.4))
        e = e.cut(cq.Workplane("XY").circle(3.25).workplane(offset=1.6).circle(1.7)
                  .loft().translate((side * EAR_SCREW_X, y, 0)))
    if SIGIL:
        # cybersigil cut through the ear: a long pointed spindle with two pairs of barbs (the rack post shows through)
        from sigil import stroke_poly, bez
        xc = side * 116.0
        cuts = [stroke_poly(bez([(xc, -37), (xc - side * 2.5, 0), (xc, 37)], 40),
                            lambda t: 1.4 + 4.6 * math.sin(math.pi * t) ** 1.6)]
        for yb in (-15.0, 15.0):
            sy = 1 if yb > 0 else -1
            cuts.append(stroke_poly(bez([(xc, yb), (xc + side * 4, yb + sy * 3), (xc + side * 7, yb + sy * 11)], 20),
                                    lambda t: 2.6 * (1 - t) + 1.2 * t))
        for poly in cuts:
            e = e.cut(cq.Workplane("XY").polyline(poly).close().extrude(EAR_T + 2).translate((0, 0, -1)))
    return e


def b1_dummy(lift=0.0, h=B1_H):
    """printer resting in the cradle; its top face (labels/button/lid) faces -z (out of the rack)"""
    p = box(-B1_L / 2, B1_L / 2, 0.05 + lift, B1_W + lift, 0.05, h)
    return local_to_world(p)


def spacer(side=1, local=False):
    """clip-in spacer for a 62 mm thick B1: a 5 mm pad in front of the back rest, hooked over its top edge.
    Print two (the same part), lying on its side so the hook profile is on the bed."""
    zb = B1_H + CLR                                           # front face of the back rest
    z0 = B1_H_THIN + CLR                                      # front face of the spacer
    x0, x1 = sorted((side * SPACER_X[0], side * SPACER_X[1]))
    s = box(x0, x1, 4.0, REST_H + 3.4, z0, zb - 0.1)            # pad
    s = s.union(box(x0, x1, REST_H + 0.4, REST_H + 3.4, z0, zb + REST_T + 2.9))   # hook over the rest
    s = s.union(box(x0, x1, REST_H - 10.0, REST_H + 3.4, zb + REST_T + 0.4, zb + REST_T + 2.9))   # and down behind it
    return s if local else local_to_world(s)


if __name__ == "__main__":
    for n, s in (("body", body()), ("ear", ear()), ("b1", b1_dummy())):
        v = s.val(); bb = v.BoundingBox()
        print(n, v.isValid(), len(s.solids().vals()), round(v.Volume()),
              [round(a, 1) for a in (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax)])
