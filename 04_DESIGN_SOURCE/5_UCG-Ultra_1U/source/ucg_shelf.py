"""
UniFi Cloud Gateway Ultra shelf — 10-inch 1U rack unit, the top unit of the 9U T0-look rack (under the cap).
UCG-Ultra (Ubiquiti tech specs): 141.8 W x 127.6 D x 30 H mm, 520 g, 6.2 W max. The status display is on the
front face; the RJ45 ports and the USB-C power input are on the back.
One print: a 254 mm 1U front panel with the ears built in, a window that frames the gateway's front face, and a
tray with low side rails and two rear corner stops. Drop the gateway into the tray, then rack the shelf: the
window lip, the rails and the rear stops hold it, and the cap is 12 mm above it.
Prints front face down, turned 45 degrees on a 220 mm bed (it needs 211 mm), no supports.
Coordinates (mm): x across, y up (0 = unit centre), z back. The panel's back face is z = 3 (rail face).
"""
import cadquery as cq
from b1_drawer import box, PANEL_W, SLOT_PITCH_X, SLOT_L, SLOT_W

U = 44.45
PANEL_H = U - 0.8                         # 43.65, 1U
SLOT_Y = PANEL_H / 2 - 5.95               # EIA holes 6.35 and 38.1 of the U (15.875 from centre)
PANEL_T = 3.0                             # same as the dock and screen ears
GW = (141.8, 127.6, 30.0)                 # UCG-Ultra W x D x H
FIT = 0.6                                 # clearance each side and behind
FLOOR_T = 2.4
Y_BOT = -PANEL_H / 2                      # floor underside = panel bottom edge
FLOOR_TOP = Y_BOT + FLOOR_T               # the gateway stands here
HX = GW[0] / 2 + FIT                      # 71.5, inside face of the rails
RAIL_T, RAIL_H = 2.4, 12.0                # side rails, height above the floor top
Z_GW = (PANEL_T, PANEL_T + GW[1])         # gateway front face against the panel
STOP_Z0 = Z_GW[1] + FIT                   # rear corner stops behind the gateway
STOP_X0 = 56.0                            # corners only: the ports in the middle stay clear
STOP_LIP, STOP_H, STOP_D = 3.0, 8.0, 6.0  # 3 mm square lip against the gateway, then a 45 degree back up to 8 mm
Z_END = STOP_Z0 + STOP_D                  # 137.2
WIN = (132.0, 22.0)                       # window; the gateway's 141.8 x 30 face sits behind it
WIN_YC = FLOOR_TOP + GW[2] / 2            # centred on the gateway's face (display in the middle)
FRAME_HW, FRAME_D, FRAME_T = 107.0, 10.0, 2.4   # stiffening frame behind the panel, inside the posts
VENT_X, VENT_H = (80.0, 96.0), 3.0        # horizontal vent slots either side of the window
VENT_Y = (-12.0, -4.0, 4.0, 12.0)
FLOOR_SLOTS = [-60.0 + 10.0 * i for i in range(13)]   # 3.5 wide slots under the gateway, along z
FLOOR_SLOT_Z = (25.0, 110.0)


def stop(side):
    """rear corner stop, tied to the floor and the rail. Printed face down, its front is only a 3 mm overhang."""
    yz = [(Y_BOT, STOP_Z0), (FLOOR_TOP + STOP_LIP, STOP_Z0), (FLOOR_TOP + STOP_H, STOP_Z0 + STOP_H - STOP_LIP),
          (FLOOR_TOP + STOP_H, Z_END), (Y_BOT, Z_END)]
    x0, x1 = sorted((side * STOP_X0, side * (HX + 0.01)))
    return cq.Workplane("YZ").polyline(yz).close().extrude(x1 - x0).translate((x0, 0, 0))


def body():
    hw, hh = PANEL_W / 2, PANEL_H / 2
    b = box(-hw, hw, -hh, hh, 0, PANEL_T)                                          # panel with the ears
    # frame behind the panel: top and bottom bars, end posts (they stiffen the panel between tray and ears)
    b = b.union(box(-FRAME_HW, FRAME_HW, -hh, -hh + FRAME_T, PANEL_T, PANEL_T + FRAME_D))
    b = b.union(box(-FRAME_HW, FRAME_HW, hh - FRAME_T, hh, PANEL_T, PANEL_T + FRAME_D))
    for s in (1, -1):
        x0, x1 = sorted((s * (FRAME_HW - FRAME_T), s * FRAME_HW))
        b = b.union(box(x0, x1, -hh, hh, PANEL_T, PANEL_T + FRAME_D))
    # tray: floor, side rails, rear corner stops
    b = b.union(box(-HX - RAIL_T, HX + RAIL_T, Y_BOT, FLOOR_TOP, PANEL_T, Z_END))
    for s in (1, -1):
        x0, x1 = sorted((s * HX, s * (HX + RAIL_T)))
        b = b.union(box(x0, x1, Y_BOT, FLOOR_TOP + RAIL_H, PANEL_T, Z_END))
        b = b.union(stop(s))
    # window for the gateway's front face and display
    b = b.cut(cq.Workplane("XY").rect(*WIN).extrude(PANEL_T + 2).edges("|Z").fillet(3.0)
              .translate((0, WIN_YC, -1)))
    # vent slots either side of the window, and slots in the floor under the gateway
    for s in (1, -1):
        for y in VENT_Y:
            xa, xb = sorted((s * VENT_X[0], s * VENT_X[1]))
            b = b.cut(cq.Workplane("XY").center((xa + xb) / 2, y).slot2D(xb - xa, VENT_H)
                      .extrude(PANEL_T + 2).translate((0, 0, -1)))
    for x in FLOOR_SLOTS:
        zc = sum(FLOOR_SLOT_Z) / 2
        b = b.cut(cq.Workplane("XZ").center(x, zc).slot2D(FLOOR_SLOT_Z[1] - FLOOR_SLOT_Z[0], 3.5, angle=90)
                  .extrude(-(FLOOR_T + 2)).translate((0, Y_BOT - 1, 0)))
    # ear slots for the rail inserts
    for s in (1, -1):
        for y in (SLOT_Y, -SLOT_Y):
            b = b.cut(cq.Workplane("XY").slot2D(SLOT_L, SLOT_W).extrude(PANEL_T + 2)
                      .translate((s * SLOT_PITCH_X / 2, y, -1)))
    return b


def gateway_dummy():
    """UCG-Ultra as a rounded block, standing on the floor with its front face against the panel"""
    g = box(-GW[0] / 2, GW[0] / 2, FLOOR_TOP + 0.02, FLOOR_TOP + GW[2], Z_GW[0] + 0.02, Z_GW[1])
    return g.edges("|Y").fillet(8.0).edges(">Y").fillet(4.0)


if __name__ == "__main__":
    for n, s in (("body", body()), ("gateway", gateway_dummy())):
        v = s.val(); bb = v.BoundingBox()
        print(n, v.isValid(), len(s.solids().vals()), round(v.Volume()),
              [round(a, 1) for a in (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax)])
