"""
Cradle for the plug-in 12 V 5 A (60 W) power brick, in the empty bay to the right of the Pi unit (behind the right
half of the Pi faceplate). It drops onto the rack's middle and rear base bars, with no screws: notches under the
floor straddle both bars, so it can't slide front to back, and the Pi shelf and the right rear post box it in
sideways. Lift it out to service the brick.

The brick stands on its long edge (thickness across the rack), mains end at the back:
  - mains cord: out of the open rear end, to the wall socket behind the rack
  - 12 V lead: forward along the cradle, over the front base bar and out through a notch in the bottom edge of the
    Pi faceplate (Rack_Faceplate_2U_10in_DC-notch), then a few cm left into the UPS DC-IN window
  - spare 12 V lead: coiled in the front of the cradle, tied to the zip-tie anchor
One cradle takes bricks 30-38 mm thick: clip one printed spacer (2, 4, 6 or 8 mm) on the inner wall to take up the
slack (Robu's 110 x 50 x 30 brick: the 8 mm one), then hold the brick down with two hook-and-loop straps (or zip ties) round the cradle between the bars.

Coordinates (mm) are the rack's: x across (0 = centre), y up (0 = top of the base bars), z back from the front rail face.
Parts: brick_cradle(), spacer(t), faceplate_notch_cut() (in the Pi unit's v3 frame, for the faceplate STEP).
"""
import cadquery as cq


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


# rack geometry this sits on (rack_t0.py, checked again in verify_brick.py)
MID_BAR, REAR_BAR = (80.0, 92.0), (188.0, 199.0)   # base bars, tops at y = 0
SHELF_X1 = 67.15                                     # right edge of the Pi shelf
POST_X0 = 112.0                                      # inner face of the rear post

# cradle
X0, X1 = 68.0, 111.3                 # outer faces: 0.85 mm from the Pi shelf, 0.7 mm from the rear post
WT = 2.4                             # side walls
XI0, XI1 = X0 + WT, X1 - WT          # 70.4 .. 108.9: 38.5 mm inside
FT, FB = 2.4, -3.0                   # floor top; floor bottom between the bars (it drops 3 mm in front of and behind each bar)
WALL_TOP = FT + 30.0                 # 32.4: the walls reach a bit over half way up a 50 mm brick
Z0 = 14.0                            # front end, 2 mm behind the front base bar
CLR = 0.4                            # round the bars
MID_NOTCH = (MID_BAR[0] - CLR, MID_BAR[1] + CLR)
REAR_NOTCH = (REAR_BAR[0] - CLR, REAR_BAR[1] + CLR)
LIP_T = 2.0                          # rear lip behind the rear bar (sticks out 1.4 mm behind the rack's back face)
Z1 = REAR_NOTCH[1] + LIP_T           # 201.4
KERB = (Z1 - 3.0, Z1, 8.0)           # rear kerb the brick backs onto: z from, z to, height above the floor (the mains plug passes over it)
BRICK_REAR = KERB[0]                 # 198.4
ANCHOR = (89.65, 22.0, 30.0)         # zip-tie anchor for the spare 12 V lead: x centre, z from, z to
SLOT_X = [77.0, 83.5, 90.0, 96.5, 103.0]
SLOT_Z = [98.0, 121.0, 144.0, 167.0]
SLOT_W, SLOT_L = 4.0, 17.0           # floor vents in the brick zone, between the bars (the plinth below is open to the desk)

# spacers: hang on the inner wall, plate inside the channel, flange on the wall top
SPACERS = (2.0, 4.0, 6.0, 8.0)
SP_Z = (86.0, 196.0)
SP_Y0 = FT + 0.4
FLANGE_T = 2.0

# faceplate notch for the 12 V lead (rack x, rack y from the faceplate's bottom edge)
NOTCH_X, NOTCH_W, NOTCH_H = 74.0, 8.0, 9.0


def brick_cradle():
    c = box(X0, X1, FB, FT, Z0, Z1)                                   # floor
    for xa, xb in ((X0, XI0), (XI1, X1)):
        c = c.union(box(xa, xb, FT - 0.01, WALL_TOP, Z0, BRICK_REAR - 2.0))          # side walls, full height to 2 mm short of the brick's back
        c = c.union(box(xa, xb, FT - 0.01, FT + KERB[2], BRICK_REAR - 2.01, Z1))    # kerb height behind it: the mains plug is wider than a thin brick
    c = c.union(box(XI0 - 0.01, XI1 + 0.01, FT - 0.01, FT + KERB[2], KERB[0], KERB[1]))
    for z0, z1 in (MID_NOTCH, REAR_NOTCH):                           # notches over the bars (the floor above bridges them)
        c = c.cut(box(X0 - 1, X1 + 1, FB - 1, 0.0, z0, z1))
    xa = ANCHOR[0]                                                    # zip-tie anchor: a bar with a tunnel under it
    c = c.union(box(xa - 6, xa + 6, FT - 0.01, FT + 4.5, ANCHOR[1], ANCHOR[2]))
    c = c.cut(box(xa - 7, xa + 7, FT - 0.5, FT + 2.5, ANCHOR[1] + 1.5, ANCHOR[2] - 1.5))
    for x in SLOT_X:
        for z in SLOT_Z:
            c = c.cut(box(x - SLOT_W / 2, x + SLOT_W / 2, FB - 1, FT + 1, z, z + SLOT_L).edges("|Y").fillet(1.9))
    c = c.edges("|Z and >Y").fillet(1.0)                              # soften the wall tops
    return c


def spacer(t):
    s = box(XI0 + 0.0, XI0 + t, SP_Y0, WALL_TOP, SP_Z[0], SP_Z[1])
    return s.union(box(X0, XI0 + t, WALL_TOP, WALL_TOP + FLANGE_T, SP_Z[0], SP_Z[1]))


def brick_dummy(L, H, T, t_spacer, gap=0.05):
    """brick on its long edge against the outer wall, backed onto the kerb"""
    return box(XI1 - gap - T, XI1 - gap, FT + gap, FT + gap + H, BRICK_REAR - gap - L, BRICK_REAR - gap)


def spacer_for(T):
    """thickest spacer that still lets a brick T thick in"""
    fit = [t for t in (0.0,) + SPACERS if XI1 - XI0 - t >= T + 0.3]
    return max(fit) if fit else None


def faceplate_notch_cut():
    """notch in the bottom edge of Rack_Faceplate_2U_10in, in the Pi unit's v3 frame (x_rack = x - 56.95,
    y_rack = z + 8, the faceplate is y 112.5..116.5 there)"""
    cx, z0 = NOTCH_X + 56.95, -8.0
    r = NOTCH_W / 2
    u = box(cx - r, cx + r, 110.0, 120.0, z0 - 2.0, z0 + NOTCH_H - r)
    arc = cq.Workplane("XZ").center(cx, z0 + NOTCH_H - r).circle(r).extrude(-10.0).translate((0, 110.0, 0))
    return u.union(arc)


def to_bed(shape, axis, ang):
    s = shape.rotate((0, 0, 0), axis, ang)
    bb = s.val().BoundingBox()
    return s.translate((-bb.xmin, -bb.ymin, -bb.zmin))


PRINT = {   # STL name: (part, rotation that lays it on the bed)
    "Brick_Cradle_12V": (brick_cradle, ((1, 0, 0), 90)),            # floor down (rack y -> up)
    "Brick_Spacer_2mm": (lambda: spacer(2.0), ((0, 1, 0), 90)),     # brick-side face down
    "Brick_Spacer_4mm": (lambda: spacer(4.0), ((0, 1, 0), 90)),
    "Brick_Spacer_6mm": (lambda: spacer(6.0), ((0, 1, 0), 90)),
    "Brick_Spacer_8mm": (lambda: spacer(8.0), ((0, 1, 0), 90)),
}

if __name__ == "__main__":
    import os
    import sys
    bundle, out = sys.argv[1], sys.argv[2]
    for sub in ("STL_for_printing", "STEP_for_Onshape"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    for nm, (make, (axis, ang)) in PRINT.items():
        s = make()
        assert len(s.solids().vals()) == 1, nm
        cq.exporters.export(s, os.path.join(out, "STEP_for_Onshape", nm + ".step"))
        p = to_bed(s, axis, ang)
        cq.exporters.export(p, os.path.join(out, "STL_for_printing", nm + ".stl"), tolerance=0.02, angularTolerance=0.1)
        bb = p.val().BoundingBox()
        print(f"{nm:24s} on the bed {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:5.1f}  valid={s.val().isValid()}")
    # the Pi faceplate with the 12 V lead notch: same file as plate 11's, plus the notch
    step = os.path.join(bundle, "4_Pi_Unit_2U", "STEP_for_Onshape", "Rack_Faceplate_2U_10in.step")
    fp = cq.Workplane().add(cq.importers.importStep(step).val())
    fpn = fp.cut(faceplate_notch_cut())
    assert len(fpn.solids().vals()) == 1
    nm = "Rack_Faceplate_2U_10in_DC-notch"
    cq.exporters.export(fpn, os.path.join(out, "STEP_for_Onshape", nm + ".step"))
    p = to_bed(fpn, (1, 0, 0), -90)                                  # front face down, as pi_unit_fix.py lays plate 11's
    cq.exporters.export(p, os.path.join(out, "STL_for_printing", nm + ".stl"), tolerance=0.02, angularTolerance=0.1)
    bb = p.val().BoundingBox()
    print(f"{nm:24s} on the bed {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:5.1f}  valid={fpn.val().isValid()}  "
          f"notch {fp.val().Volume() - fpn.val().Volume():.0f} mm3")
