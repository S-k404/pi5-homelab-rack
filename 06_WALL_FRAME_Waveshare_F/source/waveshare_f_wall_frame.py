"""
Wall frame (shadow box) for the Waveshare Pi5 Connector Adapter (F), on its own, hung on a wall like a picture.
Two prints: the box (back plate with 2 keyholes, 4 board posts, side walls with the port openings) and the front frame
(a picture-frame bezel held by 4 countersunk M3 screws).

Board data: Waveshare's dimension drawing (docs.waveshare.com/Pi5-Connector-Adapter-F, image
"Pi5-Connector-Adapter-F-details-size"), measured by pixel analysis on 8 Nov 2026 relative to the four hole centres
(6.775 px/mm along, 6.817 px/mm across; the photo is good to about +-0.3 mm, see checks/DIMENSIONS_adapter_F.txt):
  PCB 85.00 x 52.50 (86.00 over the UART socket; waveshare.com lists 86.0 x 52.5), Ø2.8-3.0 holes (M2.5)
  58.00 x 46.50 apart, 3.0 mm in from the plug edge and the top edge, 24.05 / 82.05 from the ports end.
  RJ45 (y 22.2..38.5) and full-size HDMI (y 0.6..18.6) at the ports end, faces 3.1-3.4 mm past the PCB edge (the 27 Oct
  holder assumed 1.0: both cases are checked). A 2.2 mm "PWR" rod (y 45.0..47.2) sticks 3.4 mm out of that end. The plug
  edge is cut back ~2.7 mm between the two corner tabs; the micro-HDMI (centre x 60.2) and USB-C (74.4) plugs reach
  5.9-6.35 mm past the tabs (the Pi 5 drawing's port spacing, 11.2 / 25.8 from its edge, puts them at 59.75 / 74.35).
  The pluggable 7-24 V terminal (y 6.85..15.4) reaches x 97.84, wire entries facing +x.

Frame: x along the 85 mm side (0 = ports-end PCB edge, + to the terminal end), y along the 52.5 mm side
(0 = plug edge, + up the wall), z out of the wall (0 = the back face on the wall). Hung landscape, plug edge down,
so the FFC and any cables at the plug edge drop out of the bottom slot.

Run: python waveshare_f_wall_frame.py <out folder>
     writes STEP (assembled frame) and STL laid out for printing (both parts flat face down).
"""
import os
import sys
import cadquery as cq

# ---------------------------------------------------------------- the adapter (drawing frame = this frame)
PCB_L, PCB_W, PCB_T = 85.0, 52.5, 1.6
HOLES = [(24.05, 3.0), (82.05, 3.0), (24.05, 49.5), (82.05, 49.5)]
JACK_FACE_X = -3.3             # RJ45 / HDMI faces, from the drawing (3.1..3.4 measured)
RJ45_Y, RJ45_H = (22.0, 38.5), 13.5
HDMI_Y, HDMI_H = (0.6, 18.6), 6.5
ROD_Y = (44.8, 47.4)
PLUG_TIP_Y = -6.4              # micro-HDMI and USB-C plug tips (5.9..6.35 measured)
TERM_X1, TERM_Y = 97.9, (6.4, 15.4)

# ---------------------------------------------------------------- box
CLR = 0.4
PLATE_T = 3.0                  # back plate
POST_D, PILOT_D = 6.4, 2.1     # board posts, pilot for self-tapping M2.5
ZB = 9.5                       # PCB underside
PCB_TOP = ZB + PCB_T
WALL_Z1 = PCB_TOP + 15.0       # bezel seat: 1.5 mm over the RJ45
WALL = 2.4
INX0, INX1 = 0.0 - CLR, TERM_X1 + 1.2
INY0 = PLUG_TIP_Y - 1.2
INY1 = PCB_W + (0.0 - INY0)    # same margin top and bottom, so the board sits centred top to bottom
OX0, OX1 = INX0 - WALL, INX1 + WALL
OY0, OY1 = INY0 - WALL, INY1 + WALL
R_OUT = 3.0

# openings
SIDE_OPEN_Y = (-2.6, 49.5)     # ports end: HDMI, RJ45 and the PWR rod, open to the bezel
SIDE_SILL = PLATE_T + 1.0      # low enough for a 12 mm HDMI plug moulding if the jack face is recessed
BOT_SLOT_X = (27.0, 80.0)      # plug edge: FFC, micro-HDMI / USB-C plugs, the 3-pin socket
BOT_SILL = PLATE_T + 2.0
TERM_NOTCH_Y = (4.5, 17.5)     # terminal end: wires, and the green plug slides out through it
TERM_SILL = ZB - 1.5
VENT_X = [14 + 8 * i for i in range(10)]
VENT_W, VENT_Z = 2.0, (PCB_TOP + 1.0, WALL_Z1 - 4.0)

# corner columns for the bezel screws (M3 x 12 countersunk, self-tapping into the pilot)
COL_IN = 4.0                   # centre, from the outer edges
COL_D, COL_PILOT_D, COL_PILOT_DEPTH = 7.0, 2.5, 10.0
COLS = [(OX0 + COL_IN, OY0 + COL_IN), (OX1 - COL_IN, OY0 + COL_IN),
        (OX0 + COL_IN, OY1 - COL_IN), (OX1 - COL_IN, OY1 - COL_IN)]

# keyholes: wall screw shank <= 4.0, head <= 9.0 across and <= 2.8 tall, its underside 2-3 mm off the wall
# (8 Nov clearance check: the first 3.2 mm head pocket only took a head standing 1.8-2.2 mm off the wall)
KEY_X = [(OX0 + OX1) / 2 - 14.0, (OX0 + OX1) / 2 + 14.0]
KEY_ENTRY_Y, KEY_TRAVEL = 33.0, 8.0     # the head enters at y 33 and the frame drops 8 mm onto it
KEY_ENTRY_D, KEY_NECK_W, KEY_HEAD_W = 9.6, 4.6, 9.6
KEY_NECK_T, KEY_CAV_T, KEY_ROOF_T = 1.8, 4.2, 1.5
KEY_BOSS_Z1 = KEY_NECK_T + KEY_CAV_T + KEY_ROOF_T

# ---------------------------------------------------------------- bezel
BEZ_T = 4.5
BEZ_Z0, BEZ_Z1 = WALL_Z1, WALL_Z1 + BEZ_T
BORDER = 8.0
WIN_X = (OX0 + BORDER, OX1 - BORDER)
WIN_Y = (OY0 + BORDER, OY1 - BORDER)
BEVEL = 1.0                    # 45 degree mat bevel round the window
EDGE_CH = 0.8                  # outer front edge
CSK_D, CSK_THRU = 6.2, 3.4     # M3 countersunk (DIN 7991 head 5.5)
LABEL = "PI5 CONNECTOR ADAPTER (F)"
LABEL_H, LABEL_DEPTH = 3.2, 0.6


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def cyl(x, y, z0, z1, d):
    return cq.Workplane("XY").circle(d / 2).extrude(z1 - z0).translate((x, y, z0))


def slot_y(x, y0, y1, w, z0, z1):
    """Round-ended slot along y, centres y0..y1."""
    return (cq.Workplane("XY").slot2D(y1 - y0 + w, w, 90).extrude(z1 - z0)
            .translate((x, (y0 + y1) / 2, z0)))


def frame_box():
    b = box(OX0, OX1, OY0, OY1, 0, WALL_Z1).edges("|Z").fillet(R_OUT)
    b = b.faces("<Z").chamfer(0.6)
    b = b.cut(box(INX0, INX1, INY0, INY1, PLATE_T, WALL_Z1 + 1))

    # corner columns (they merge into the walls)
    for cx, cy in COLS:
        b = b.union(cyl(cx, cy, PLATE_T - 0.01, WALL_Z1, COL_D).intersect(box(OX0, OX1, OY0, OY1, 0, WALL_Z1)))

    # board posts
    for hx, hy in HOLES:
        b = b.union(cyl(hx, hy, PLATE_T - 0.01, ZB, POST_D))

    # keyhole bosses, then the keyholes
    for kx in KEY_X:
        b = b.union(box(kx - 6.5, kx + 6.5, KEY_ENTRY_Y - 6.5, KEY_ENTRY_Y + KEY_TRAVEL + 6.5,
                        PLATE_T - 0.01, KEY_BOSS_Z1).edges("|Z").fillet(2.0))
        b = b.cut(cyl(kx, KEY_ENTRY_Y, -1, KEY_BOSS_Z1 + 1, KEY_ENTRY_D))                        # head goes in
        b = b.cut(slot_y(kx, KEY_ENTRY_Y, KEY_ENTRY_Y + KEY_TRAVEL, KEY_NECK_W, -1, KEY_NECK_T))  # shank
        b = b.cut(slot_y(kx, KEY_ENTRY_Y, KEY_ENTRY_Y + KEY_TRAVEL, KEY_HEAD_W,
                         KEY_NECK_T, KEY_NECK_T + KEY_CAV_T))                                    # head rests

    # pilots: board posts (not through the back) and bezel columns
    for hx, hy in HOLES:
        b = b.cut(cyl(hx, hy, 1.0, ZB + 0.1, PILOT_D))
    for cx, cy in COLS:
        b = b.cut(cyl(cx, cy, WALL_Z1 - COL_PILOT_DEPTH, WALL_Z1 + 0.1, COL_PILOT_D))

    # openings, all open to the bezel
    b = b.cut(box(OX0 - 1, INX0 + 0.01, SIDE_OPEN_Y[0], SIDE_OPEN_Y[1], SIDE_SILL, WALL_Z1 + 1))
    b = b.cut(box(BOT_SLOT_X[0], BOT_SLOT_X[1], OY0 - 1, INY0 + 0.01, BOT_SILL, WALL_Z1 + 1))
    b = b.cut(box(INX1 - 0.01, OX1 + 1, TERM_NOTCH_Y[0], TERM_NOTCH_Y[1], TERM_SILL, WALL_Z1 + 1))
    # convection vents in the top wall (air comes in at the bottom slot)
    for vx in VENT_X:
        b = b.cut(box(vx - VENT_W / 2, vx + VENT_W / 2, INY1 - 0.01, OY1 + 1, VENT_Z[0], VENT_Z[1]))
    return b


def bezel():
    z = BEZ_Z0
    f = box(OX0, OX1, OY0, OY1, z, BEZ_Z1).edges("|Z").fillet(R_OUT)
    f = f.faces(">Z").chamfer(EDGE_CH)
    w = WIN_X[1] - WIN_X[0]
    h = WIN_Y[1] - WIN_Y[0]
    cxw, cyw = (WIN_X[0] + WIN_X[1]) / 2, (WIN_Y[0] + WIN_Y[1]) / 2
    win = box(WIN_X[0], WIN_X[1], WIN_Y[0], WIN_Y[1], z - 1, BEZ_Z1 - BEVEL + 0.01)
    bev = (cq.Workplane("XY").workplane(offset=BEZ_Z1 - BEVEL).center(cxw, cyw).rect(w, h)
           .workplane(offset=BEVEL + 0.01).rect(w + 2 * (BEVEL + 0.01), h + 2 * (BEVEL + 0.01)).loft())
    f = f.cut(win).cut(bev)
    # countersunk M3 holes over the columns
    for cx, cy in COLS:
        f = f.cut(cyl(cx, cy, z - 1, BEZ_Z1 + 1, CSK_THRU))
        cone = cq.Solid.makeCone(CSK_THRU / 2, CSK_D / 2 + 0.01, (CSK_D - CSK_THRU) / 2 + 0.01,
                                 pnt=cq.Vector(cx, cy, BEZ_Z1 - (CSK_D - CSK_THRU) / 2))
        f = f.cut(cq.Workplane("XY").add(cone))
    # engraved label on the bottom border
    if LABEL:
        txt = (cq.Workplane("XY").text(LABEL, LABEL_H, -LABEL_DEPTH, kind="bold", halign="center", valign="center")
               .translate(((OX0 + OX1) / 2, (OY0 + WIN_Y[0]) / 2, BEZ_Z1)))
        f = f.cut(txt)
    return f


def to_bed(shape, flip=False):
    s = shape.rotate((0, 0, 0), (1, 0, 0), 180) if flip else shape
    bb = s.val().BoundingBox()
    return s.translate((-bb.xmin, -bb.ymin, -bb.zmin))


if __name__ == "__main__":
    OUT = sys.argv[1]
    for sub in ("STL_for_printing", "STEP_for_Onshape"):
        os.makedirs(os.path.join(OUT, sub), exist_ok=True)
    # both print with their flat back on the bed: the box on its wall face, the bezel on its underside
    parts = {"WallFrame_F_box": frame_box(), "WallFrame_F_front": bezel()}
    for nm, shp in parts.items():
        assert len(shp.solids().vals()) == 1, (nm, len(shp.solids().vals()))
        cq.exporters.export(shp, os.path.join(OUT, "STEP_for_Onshape", nm + ".step"))
        cq.exporters.export(to_bed(shp), os.path.join(OUT, "STL_for_printing", nm + ".stl"),
                            tolerance=0.02, angularTolerance=0.1)
        b = shp.val().BoundingBox()
        print(f"{nm:20s} {b.xlen:6.1f} x {b.ylen:6.1f} x {b.zlen:5.1f}  valid={shp.val().isValid()}  "
              f"vol={shp.val().Volume()/1000:.1f} cm3")
    print(f"outline x {OX0:.1f}..{OX1:.1f} ({OX1-OX0:.1f}), y {OY0:.1f}..{OY1:.1f} ({OY1-OY0:.1f}), "
          f"depth {BEZ_Z1:.1f}; PCB underside z {ZB}, top {PCB_TOP:.1f}; window x {WIN_X[0]:.1f}..{WIN_X[1]:.1f}, "
          f"y {WIN_Y[0]:.1f}..{WIN_Y[1]:.1f}; keyholes x {KEY_X[0]:.1f}, {KEY_X[1]:.1f} ({KEY_X[1]-KEY_X[0]:.1f} apart)")
