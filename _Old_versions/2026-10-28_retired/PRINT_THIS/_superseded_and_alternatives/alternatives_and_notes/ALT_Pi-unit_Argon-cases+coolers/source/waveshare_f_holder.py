"""
Standalone holder ("side board") for the Waveshare Pi5 Connector Adapter (F), sitting on the free left part of the
Argon Poly+5 tray, beside the case. Styled after the Poly+5: matt black PETG, a lid with diagonal grooves and a round
louvred vent window.

Board data: Waveshare's dimension drawing (docs.waveshare.com/Pi5-Connector-Adapter-F, read 27 Oct 2026):
  PCB 85.00 x 52.50 (86.00 over the top-right SH1.0 connector), M2.5 holes 58.00 x 46.50 apart,
  RJ45 + full-size HDMI at one short end (ports), USB-C + micro-HDMI plugs + SH1.0 on one long edge (the plug edge),
  7-24 V screw terminal at the plug-edge / far-end corner (it sticks out ~12 mm past the PCB, wire entry faces away
  from the ports), M.2 M-key slot near the far end.
  Port positions measured off the drawing: HDMI-A centre 10.05 mm and RJ45 centre 30.7 mm from the plug edge
  (the same numbers the v3 case used).

Frame = v3 frame (as argon_tray.py): x left -> right, y from the rack REAR (-) to the FRONT (+), z up.
The holder rests on the Argon tray's floor (z 36.9) and straddles the tray's left rim and rear rim in two slots.

Run: python waveshare_f_holder.py <out folder>
     writes STEP (v3 frame) and STL laid out for printing (base plinth-down, lid top-face-down).
"""
import os
import sys
import math
import cadquery as cq

# ---------------------------------------------------------------- tray / rack facts (argon_tray.py, pi_rack.py)
ZS = 36.9                      # Argon tray floor top
RIM_TOP = ZS + 5.0             # tray rim height (left + rear rims)
RIM_X = (-2.2, 0.0)            # left rim (full length)
RIM_REAR_Y = (-2.2, 0.0)       # rear rim (x up to 31.2)
RIM_REAR_XMAX = 31.2
TRAY_VENT_X = [6, 11, 16, 21, 26, 31]   # tray floor slots (x), 44 long centred y 40 (36 skipped here: posts)

# ---------------------------------------------------------------- adapter (F), drawing frame -> v3 frame
PCB_L, PCB_W, PCB_T = 85.0, 52.5, 1.6
HOLES_D = [(24.05, 3.0), (82.05, 3.0), (24.05, 49.5), (82.05, 49.5)]   # (x_d along 85, y_d along 52.5 from plug edge)
XP = 43.2                      # plug edge x (PCB right edge)
PCB_Y0 = -1.15                 # ports end (PCB rear edge)
def d2v(xd, yd):
    return XP - yd, PCB_Y0 + xd
PCB_X0 = XP - PCB_W

# ---------------------------------------------------------------- holder
CLR = 0.35
INX0, INX1 = PCB_X0 - CLR, XP + CLR
INY0 = PCB_Y0 - 1.0 - 0.45                       # rear wall inner: jack faces overhang the PCB by 1.0
INY1 = PCB_Y0 + 97.0 + 0.55                      # front wall inner: terminal block reaches x_d 97
W_L, W_R, W_REAR, W_FRONT = 1.6, 1.2, 2.0, 1.6
OX0, OX1 = INX0 - W_L, INX1 + W_R
OY0, OY1 = INY0 - W_REAR, INY1 + W_FRONT
R_OUT = 2.0

PLINTH_H = 5.4                 # clears the 5.0 mm tray rims
DECK_Z0 = ZS + PLINTH_H
DECK_T = 1.8
DECK_Z1 = DECK_Z0 + DECK_T
POST_H = 2.5
ZB = DECK_Z1 + POST_H          # PCB underside
PCB_TOP = ZB + PCB_T
LID_Z0 = PCB_TOP + 14.5        # lid underside: 1.0 mm over the RJ45 (13.5)
LID_T = 3.0
LID_Z1 = LID_Z0 + LID_T

SILL_REAR = ZB + 0.4           # port notches are open at the top and closed by the lid
SILL_RIGHT = DECK_Z1 + 0.7
PLUG_WIN = (28.0, 79.0)        # y span of the plug-edge window (SH1.0 / micro-HDMI / USB-C plugs)
RJ45_X = (XP - 30.7 - 9.2, XP - 30.7 + 9.2)        # 18.4 wide
HDMI_X = (XP - 10.05 - 9.3, XP - 10.05 + 9.3)      # 18.6 wide
TERM_X = (28.0, 42.0)          # front notch for the 12 V lead (terminal wire entries face the front)

POST_D, COL_D, PILOT_D, PILOT_DEPTH = 6.2, 7.0, 2.1, 8.0
TUBE_D, THRU_D, CB_D, CB_DEPTH = 5.0, 2.8, 5.4, 1.4
HOLES_V = [d2v(xd, yd) for xd, yd in HOLES_D]    # PCB holes in the v3 frame

# vent window in the lid: over the RTL8125 / SSD area
VENT_C = d2v(48.0, 30.0)
VENT_R = 12.0
GROOVE_ANG = 60.0
GROOVE_W, GROOVE_DEPTH, GROOVE_PITCH = 1.4, 0.9, 7.0
SLAT_W, SLAT_PITCH = 2.0, 3.6


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def cyl(x, y, z0, z1, d):
    return cq.Workplane("XY").circle(d / 2).extrude(z1 - z0).translate((x, y, z0))


def base():
    outer = box(OX0, OX1, OY0, OY1, DECK_Z0, LID_Z0).edges("|Z").fillet(R_OUT)
    b = outer.cut(box(INX0, INX1, INY0, INY1, DECK_Z1, LID_Z0 + 1.0))

    # ---- plinth: ribs along y (between the tray's floor vents), transverse end walls, relief slots for the tray rims
    ribs = [(OX0, OX0 + 1.8), (-4.8, -3.0), (0.4, 2.2)]
    ribs += [(c - 0.9, c + 0.9) for c in (8.5, 13.5, 18.5, 23.5, 28.5, 33.5)]
    ribs += [(38.2, 40.0), (OX1 - 1.8, OX1)]
    pl = box(OX0, OX0 + 0.1, OY0, OY0 + 0.1, ZS, ZS + 0.1)
    for xa, xb in ribs:
        pl = pl.union(box(xa, xb, OY0, OY1, ZS, DECK_Z0 + 0.01))
    pl = pl.union(box(OX0, OX1, OY0, OY0 + W_REAR, ZS, DECK_Z0 + 0.01))
    pl = pl.union(box(OX0, OX1, OY1 - W_FRONT, OY1, ZS, DECK_Z0 + 0.01))
    # slot A: straddles the tray's left rim (x -2.2..0, full length), 0.4 clearance each side
    pl = pl.cut(box(RIM_X[0] - 0.4, RIM_X[1] + 0.4, OY0 - 1, OY1 + 1, ZS - 0.1, DECK_Z0))
    # slot B: straddles the tray's rear rim (y -2.2..0, x up to 31.2)
    pl = pl.cut(box(OX0 - 1, RIM_REAR_XMAX + 0.4, RIM_REAR_Y[0] - 0.4, RIM_REAR_Y[1] + 0.4, ZS - 0.1, DECK_Z0))
    # keep the plinth inside the outer outline (fillet) so nothing pokes past the corners
    pl = pl.intersect(box(OX0, OX1, OY0, OY1, ZS - 1, DECK_Z0 + 1).edges("|Z").fillet(R_OUT))
    # corner relief: the shelf's front-left post has a gusset that reaches y 97.15 at the floor (x -10.2..-4.2, z <= 38.4)
    pl = pl.cut(box(OX0 - 1, -3.2, 96.0, OY1 + 1, ZS - 0.1, DECK_Z0))
    b = b.union(pl)

    # ---- deck vents: line up with the tray's floor slots (44 long, centred y 40)
    for vx in TRAY_VENT_X:
        b = b.cut(cq.Workplane("XY").slot2D(44.0, 2.4, 90).extrude(DECK_T + 2).translate((vx, 40.0, DECK_Z0 - 1)))

    # ---- board posts: solid column through the plinth, post under the PCB, pilot for a self-tapping M2.5
    for hx, hy in HOLES_V:
        b = b.union(cyl(hx, hy, ZS, DECK_Z1 + 0.01, COL_D))
        b = b.union(cyl(hx, hy, DECK_Z1, ZB, POST_D))
        b = b.cut(cyl(hx, hy, ZB - PILOT_DEPTH, ZB + 0.1, PILOT_D))

    # ---- port notches: open at the top, the lid closes them
    for xa, xb in (RJ45_X, HDMI_X):
        b = b.cut(box(xa, xb, OY0 - 1, INY0 + 0.01, SILL_REAR, LID_Z0 + 1))
    b = b.cut(box(INX1 - 0.01, OX1 + 1, PLUG_WIN[0], PLUG_WIN[1], SILL_RIGHT, LID_Z0 + 1))
    b = b.cut(box(TERM_X[0], TERM_X[1], INY1 - 0.01, OY1 + 1, SILL_REAR, LID_Z0 + 1))
    return b


def lid():
    L = box(OX0, OX1, OY0, OY1, LID_Z0, LID_Z1).edges("|Z").fillet(R_OUT)
    # pillars down to just above the PCB (they carry the clamping screws), M2.5 clearance through the lid
    for hx, hy in HOLES_V:
        L = L.union(cyl(hx, hy, PCB_TOP + 0.2, LID_Z0 + 0.01, TUBE_D))
    # decorative diagonal grooves on the top face, kept off the vent and the screw heads
    reach = 160.0
    keep_out = cq.Workplane("XY").circle(VENT_R + 4.0).extrude(5).translate((VENT_C[0], VENT_C[1], LID_Z1 - GROOVE_DEPTH - 0.5))
    for hx, hy in HOLES_V:
        keep_out = keep_out.union(cyl(hx, hy, LID_Z1 - GROOVE_DEPTH - 0.5, LID_Z1 + 1, CB_D + 3.0))
    zone = box(OX0 + 3.0, OX1 - 3.0, OY0 + 3.0, OY1 - 3.0, LID_Z1 - GROOVE_DEPTH, LID_Z1 + 1).cut(keep_out)
    cx, cy = (OX0 + OX1) / 2, (OY0 + OY1) / 2
    grooves = None
    n = int(reach / GROOVE_PITCH)
    for i in range(-n, n + 1):
        g = (cq.Workplane("XY").rect(reach * 2, GROOVE_W).extrude(GROOVE_DEPTH + 1)
             .translate((0, i * GROOVE_PITCH, LID_Z1 - GROOVE_DEPTH))
             .rotate((0, 0, 0), (0, 0, 1), GROOVE_ANG).translate((cx, cy, 0)))
        grooves = g if grooves is None else grooves.union(g)
    L = L.cut(grooves.intersect(zone))
    # round louvred vent window: slats parallel to the grooves, clipped to the circle
    disc = cq.Workplane("XY").circle(VENT_R).extrude(LID_T + 2).translate((VENT_C[0], VENT_C[1], LID_Z0 - 1))
    slats = None
    for i in range(-5, 6):
        s = (cq.Workplane("XY").rect(reach, SLAT_W).extrude(LID_T + 2)
             .translate((0, i * SLAT_PITCH, LID_Z0 - 1))
             .rotate((0, 0, 0), (0, 0, 1), GROOVE_ANG).translate((VENT_C[0], VENT_C[1], 0)))
        slats = s if slats is None else slats.union(s)
    L = L.cut(slats.intersect(disc))
    # clamping-screw holes (M2.5 pan head in a counterbore) through lid + pillar
    for hx, hy in HOLES_V:
        L = L.cut(cyl(hx, hy, PCB_TOP, LID_Z1 + 1, THRU_D))
        L = L.cut(cyl(hx, hy, LID_Z1 - CB_DEPTH, LID_Z1 + 1, CB_D))
    # label, engraved like the tray's
    txt = (cq.Workplane("XY").text("PI5 ADAPTER (F)", 4.2, -0.5, kind="bold", halign="center", valign="center")
           .translate(((OX0 + OX1) / 2 + 4.0, OY1 - 7.0, LID_Z1)))
    L = L.cut(txt)
    return L


def to_bed(shape, flip=False):
    s = shape.rotate((0, 0, 0), (1, 0, 0), 180) if flip else shape
    bb = s.val().BoundingBox()
    return s.translate((-bb.xmin, -bb.ymin, -bb.zmin))


if __name__ == "__main__":
    OUT = sys.argv[1]
    for sub in ("STL_for_printing", "STEP_for_Onshape"):
        os.makedirs(os.path.join(OUT, sub), exist_ok=True)
    parts = {"Waveshare_F_holder_base": (base(), False), "Waveshare_F_holder_lid": (lid(), True)}
    for nm, (shp, flip) in parts.items():
        assert len(shp.solids().vals()) == 1, (nm, len(shp.solids().vals()))
        cq.exporters.export(shp, os.path.join(OUT, "STEP_for_Onshape", nm + ".step"))
        cq.exporters.export(to_bed(shp, flip), os.path.join(OUT, "STL_for_printing", nm + ".stl"),
                            tolerance=0.02, angularTolerance=0.1)
        b = shp.val().BoundingBox()
        print(f"{nm:26s} {b.xlen:6.1f} x {b.ylen:6.1f} x {b.zlen:5.1f}  valid={shp.val().isValid()}  "
              f"vol={shp.val().Volume()/1000:.1f} cm3")
    print(f"PCB underside z={ZB:.1f}, PCB top z={PCB_TOP:.1f}, lid underside z={LID_Z0:.1f}, lid top z={LID_Z1:.1f}")
    print(f"x {OX0:.2f}..{OX1:.2f}  y {OY0:.2f}..{OY1:.2f}")
