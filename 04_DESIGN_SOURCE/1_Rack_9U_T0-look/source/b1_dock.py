"""
NIIMBOT B1 face-out dock — 10-inch 3U rack unit (v5: the real B1, 132 x 91 x 62)
The printer stands with its TOP face (label slot, power button, light, lid) facing out of the
rack, leaned back 8 degrees. Open front window, open top, open back.
v5 (27 Oct 2026): sized to the official 132 x 91 x 62 mm (no spacers), and laid out from the user's photos:
the open slide is on the side that faces UP, so (seen from the front) the lid end is on the RIGHT (-x), and the
printer sits 20 mm left of centre (+x, seen from the front) with no guide at the lid end, so the lid can swing open while the printer is racked. The lip only runs
under the left (non-lid) part of the face.
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

B1_L, B1_W, B1_H = 132.0, 91.0, 62.0      # printer: L across, W up (stood on its long side), H = depth
# Official NIIMBOT manual: 132 x 91 x 62 mm (another manual edition: 132 x 91.2 x 61.6). The 67 mm Galaxus figure
# behind the v4 spacers was wrong.
X_SHIFT = 20.0                            # printer centre +x (your LEFT seen from the front): room for the lid to swing out
# note: seen from the front (looking along +z, y up), +x is on your LEFT
# real shape, printer-local (x along the 132 side, y up the 91 side, z from the face back), from the photos:
R_CORNER, R_EDGE = 10.0, 5.0              # face-outline corners, face and back perimeter edges
LID_X1, LID_Y1 = 4.0, 81.5                # black lid: face from the -x (lid) end to x = LID_X1, below the grey top band
LSLOT_X, LSLOT_Y = 5.3, (11.5, 67.5)      # label slot just under the lid edge; labels come straight out
LED_XY, BTN_XY, BTN_D = (39.1, 57.8), (35.6, 20.5), 10.0
SLIDE_X, SLIDE_Z = (-26.0, -8.0), (8.0, 16.0)  # open slide on the top side
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
LIP = 5.0                                 # lip stands 5 mm above the printer's bottom edge (past its 5 mm edge round)
LIP_X0 = X_SHIFT + LID_X1 + 4.0           # ... and stops short of the lid, which swings out over the bar

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
        r = box(X_SHIFT + xc - RIB / 2, X_SHIFT + xc + RIB / 2, -40, 0, -4, zb + REST_T)
        c = r if c is None else c.union(r)
    # back rest, full width, down to the floor
    c = c.union(box(X_SHIFT - hx - GUIDE_T, X_SHIFT + hx + GUIDE_T, -40, REST_H, zb, zb + REST_T))
    # low guide at the bottom end (+x) only: the lid end (-x) stays free so the lid can swing out
    c = c.union(box(X_SHIFT + hx, X_SHIFT + hx + GUIDE_T, -40, GUIDE_H, -4, zb))
    # cable notch in the back rest, open at the top (prints without bridging)
    c = c.cut(box(X_SHIFT - NOTCH_HALF_W, X_SHIFT + NOTCH_HALF_W, NOTCH_Y0, REST_H + 1, zb - 1, zb + REST_T + 1))
    # lightening windows in the back rest: below the printer between the ribs, and two in the upper part
    for xa, xb in ((5, 29), (39, 62)):
        for sg in (1, -1):
            x0, x1 = sorted((X_SHIFT + sg * xa, X_SHIFT + sg * xb))
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
    b = b.union(box(-WIN_HALF, WIN_HALF, Y_BOT, PIVOT_Y - 1.0, COLLAR_D - 4, COLLAR_D))   # bottom bar, 4 mm wall, below the printer
    b = b.union(box(LIP_X0, WIN_HALF, Y_BOT, PIVOT_Y + LIP, COLLAR_D - 4, COLLAR_D))      # front lip, non-lid part only
    b = b.union(cradle())
    # ear rebates + M3 inserts
    for s in (1, -1):
        x0, x1 = sorted((s * EAR_X0, s * (hw + 1)))
        b = b.cut(box(x0, x1, Y_BOT - 1, -Y_BOT + 1, -1, EAR_T))
        for y in (EAR_SCREW_Y, -EAR_SCREW_Y):
            b = b.cut(cyl_z(s * EAR_SCREW_X, y, EAR_T - 0.1, EAR_T + INSERT_DEPTH, INSERT_D))
    # (v4's thumb scoop is gone: with no lip under the lid half, the printer's right half is free to grip)
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


def b1_local(h=B1_H):
    """the real B1 in its local frame, as separate solids: body (grey), lid (black), slide (white), led, button"""
    L, W = B1_L, B1_W
    shell = (cq.Workplane("XY").box(L, W, h, centered=False).translate((X_SHIFT - L / 2, 0, 0))
             .edges("|Z").fillet(R_CORNER).faces("<Z or >Z").edges().fillet(R_EDGE))
    lid_zone = box(X_SHIFT - L / 2 - 1, X_SHIFT + LID_X1, -1, LID_Y1, -1, h + 1)
    slot = box(X_SHIFT + LSLOT_X - 1.0, X_SHIFT + LSLOT_X + 1.0, LSLOT_Y[0], LSLOT_Y[1], -1, 3.0)
    lid = shell.intersect(lid_zone).cut(slot)
    body = shell.cut(lid_zone).cut(slot)
    seam = box(X_SHIFT + LID_X1, X_SHIFT + LID_X1 + 0.3, -1, LID_Y1, -1, 0.6)          # visible lid parting line
    body = body.cut(seam)
    btn = (cq.Workplane("XY").circle(BTN_D / 2).extrude(0.8).translate((X_SHIFT + BTN_XY[0], BTN_XY[1], -0.8)))
    led = box(X_SHIFT + LED_XY[0] - 1.2, X_SHIFT + LED_XY[0] + 1.2, LED_XY[1] - 4, LED_XY[1] + 4, -0.3, 0.5)
    slide = box(X_SHIFT + SLIDE_X[0], X_SHIFT + SLIDE_X[1], W - 0.5, W + 0.8, SLIDE_Z[0], SLIDE_Z[1])
    return {"body": body, "lid": lid, "slide": slide, "led": led, "button": btn}


def b1_parts(lift=0.0, h=B1_H):
    """the real B1, coloured parts, resting in the cradle (world frame)"""
    return {k: local_to_world(v.translate((0, 0.05 + lift, 0.05))) for k, v in b1_local(h).items()}


def b1_dummy(lift=0.0, h=B1_H):
    """the printer as one solid (real outline: rounded body + lid), for fit checks"""
    p = b1_local(h)
    one = p["body"].union(p["lid"]).union(p["slide"]).union(p["button"]).union(p["led"])
    return local_to_world(one.translate((0, 0.05 + lift, 0.05)))


def lid_open(angle, lift=0.0):
    """the lid opened by angle (deg) about its top/rear clamshell hinge opposite the label exit"""
    lid = b1_local()["lid"].translate((0, 0.05 + lift, 0.05))
    hy = LID_Y1 - R_EDGE
    hz = B1_H - R_EDGE
    return local_to_world(lid.rotate((0, hy, hz), (1, hy, hz), angle))


if __name__ == "__main__":
    for n, s in (("body", body()), ("ear", ear()), ("b1", b1_dummy())):
        v = s.val(); bb = v.BoundingBox()
        print(n, v.isValid(), len(s.solids().vals()), round(v.Volume()),
              [round(a, 1) for a in (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax)])
