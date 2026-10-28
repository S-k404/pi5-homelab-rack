import os
import sys
import cadquery as cq

# Parameters from pi_rack.py
W, IW = 2.2, 113.9
CASE_X0, CASE_X1 = -W, IW + W          # -2.2 .. 116.1
CASE_Y0 = -W                           # port face (rack rear)
CASE_Y1 = 110.0 + W                    # board tray / lid back face (rack front) = 112.2
CASE_ZBOT = -5.0
U = 44.45
PANEL_W, PANEL_H, PANEL_T = 254.0, 2 * U - 0.8, 4.0     # 254 x 88.1
HOLE_PITCH = 236.525                                     # rail hole spacing
EAR_SLOT = (10.0, 6.5)                                   # M6 slot w x h
EAR_Z = (6.35, 2 * U - 6.35)                             # from panel bottom

GAP = 0.3
SHELF_T = 4.5
Z0 = -8.0                           # desk level = panel bottom
SHELF_TOP = Z0 + SHELF_T            # -3.5
TRAY_FLOOR_Z = -2.0
PIN_D, PIN_H, PIN_HOLE = 4.0, 1.6, 4.4
CX = (CASE_X0 + CASE_X1) / 2        # 56.95 centre line
PX0, PX1 = CX - PANEL_W / 2, CX + PANEL_W / 2
PY0 = CASE_Y1 + GAP                 # faceplate rear face = 112.5
PY1 = PY0 + PANEL_T                 # faceplate front face = 116.5

FEET = [(9, 9), (IW - 9, 9), (9, 87.0 - 9), (IW - 9, 87.0 - 9)]
BTN_X, BTN_Z = 56.9 + 18.4, 41.9 + 3.04                            # Pi power-button tube = 75.3, 44.94
DCIN_X, DCIN_Z = (80.0, 112.0), (5.0, 29.0)                         # UPS tray window
V3_BACK_VENT_X = list(range(84, 106, 5)) + list(range(8, 37, 5))
BACK_VENTS_Z = (36.9 + 9, 36.9 + 21)

SH_X0, SH_X1 = -46.0, CASE_X1 + 8.0
SH_Y0, SH_Y1 = CASE_Y0 - 2.0, PY0
POST_X = [(CASE_X0 - 8.0, CASE_X0 - 2.0), (CASE_X1 + 2.0, CASE_X1 + 8.0)]
POST_Y = (PY0 - 8.0, PY0)
POST_Z1 = 60.0
LIP_Z1 = 2.0
M3_INSERT = 4.0
FP_SCREWS = [(sum(POST_X[0]) / 2, 12.0), (sum(POST_X[0]) / 2, 50.0),
             (sum(POST_X[1]) / 2, 12.0), (sum(POST_X[1]) / 2, 50.0),
             (30.0, -3.0), (85.0, -3.0)]

def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))

def cyl_y(x, y0, y1, z, d):
    return cq.Workplane("XZ").center(x, z).circle(d / 2).extrude(-(y1 - y0)).translate((0, y0, 0))

def rounded_slot_y(xc, zc, w, h, y0, y1, r=None):
    r = (min(w, h) / 2 - 0.01) if r is None else r
    return (cq.Workplane("XZ").center(xc, zc).rect(w, h).extrude(-(y1 - y0))
            .edges("|Y").fillet(r).translate((0, y0, 0)))

def faceplate_v73():
    """Faceplate with:
    1. UPS on/off switch space at x=62.6, z=13.0 (beveled window for finger or switch extender)
    2. UPS DC-IN / OUT window at x=80..112, z=5..29
    3. Hidden internal cable slit on the rear face (y=PY0..PY0+2.5, x=98..106, z=4..38)
       keeping the front surface 100% solid and hidden!
    """
    p = box(PX0, PX1, PY0, PY1, Z0, Z0 + PANEL_H).edges("|Y").fillet(2.0)
    # M6 ear slots
    for xs in (CX - HOLE_PITCH / 2, CX + HOLE_PITCH / 2):
        for zs in EAR_Z:
            p = p.cut(rounded_slot_y(xs, Z0 + zs, EAR_SLOT[0], EAR_SLOT[1], PY0 - 1, PY1 + 1))
    
    # Pi power button
    p = p.cut(cyl_y(BTN_X, PY0 - 1, PY1 + 1, BTN_Z, 8.0))
    p = p.cut(cyl_y(BTN_X, PY1 - 1.0, PY1 + 1, BTN_Z, 11.0))

    # UPS DC-IN / OUT access window
    p = p.cut(rounded_slot_y(sum(DCIN_X) / 2, sum(DCIN_Z) / 2, DCIN_X[1] - DCIN_X[0] + 4, DCIN_Z[1] - DCIN_Z[0] + 4, PY0 - 1, PY1 + 1, r=4.0))

    # UPS ON/OFF switch access slot (centered at x=62.6, z=13.0)
    # Slot 16 mm wide x 11 mm high with 3 mm fillets
    SW_X, SW_Z = 62.6, 13.0
    p = p.cut(rounded_slot_y(SW_X, SW_Z, 16.0, 11.0, PY0 - 1, PY1 + 1, r=3.0))
    # Bevel / finger dish on front face of switch slot
    p = p.cut(rounded_slot_y(SW_X, SW_Z, 20.0, 15.0, PY1 - 1.2, PY1 + 1, r=4.0))

    # Hidden cable slit on the inside (rear) face of the faceplate:
    # Routes 12V cable vertically from UPS level (z=5) up to board tray level (z=38)
    # Deep into rear face (2.5 mm deep), leaving front 1.5 mm solid!
    p = p.cut(box(97.0, 106.0, PY0 - 0.5, PY0 + 2.5, 4.0, 38.0).edges("|Y").fillet(1.5))

    # vent slots
    for vx in V3_BACK_VENT_X:
        p = p.cut(rounded_slot_y(vx, sum(BACK_VENTS_Z) / 2, 3.0, BACK_VENTS_Z[1] - BACK_VENTS_Z[0] + 2.0, PY0 - 1, PY1 + 1))
    for xa, xb in ((PX0 + 20, CASE_X0 - 14), (CASE_X1 + 14, PX1 - 20)):
        for k in range(7):
            z = Z0 + 18 + k * 8
            p = p.cut(rounded_slot_y((xa + xb) / 2, z, xb - xa, 3.0, PY0 - 1, PY1 + 1))
    
    # countersunk M3 screws into the shelf
    for sx, sz in FP_SCREWS:
        p = p.cut(cyl_y(sx, PY0 - 1, PY1 + 1, sz, 3.4))
        p = p.cut(cq.Workplane("XZ").center(sx, sz).circle(3.4)
                  .workplane(offset=-1.8).circle(1.7).loft().translate((0, PY1 + 0.001, 0)))
    return p

def ups_switch_extender():
    """Separate 3D printed switch extender:
    Fits into the UPS on/off switch slot, connects to switch nub and provides
    an ergonomic, tactile front-panel slider button.
    Prints flat on print bed.
    """
    # Switch nub pocket: 5 mm wide x 4 mm high x 4 mm deep
    # Shank: 30 mm long, 5 mm wide x 4 mm high
    # Front knob: 14 mm wide x 9 mm high x 3.5 mm thick with grip ridges
    # Sliding retention flange: 12 mm wide x 7 mm high x 1.5 mm thick
    
    # Coordinate system for printing: flat on bed (Z = up)
    # Total length Y: ~36 mm
    body = cq.Workplane("XY").box(6.0, 34.0, 4.0, centered=True)
    # Nub pocket at rear (y = -17)
    pocket = cq.Workplane("XY").box(4.2, 4.0, 3.0, centered=True).translate((0, -15.5, 0))
    body = body.cut(pocket)
    
    # Front button cap (y = +17)
    cap = cq.Workplane("XY").box(14.0, 3.5, 9.0, centered=True).translate((0, 17.0 + 1.75, 0)).edges("|Y").fillet(1.2)
    # Grip ridges on front face of cap
    for offset_z in [-2.5, 0.0, 2.5]:
        ridge = cq.Workplane("XY").box(10.0, 0.8, 0.8, centered=True).translate((0, 17.0 + 3.5 + 0.2, offset_z))
        cap = cap.union(ridge)
        
    # Guide retention flange (slides behind faceplate inner wall)
    flange = cq.Workplane("XY").box(11.0, 2.0, 7.0, centered=True).translate((0, 17.0 - 5.0, 0)).edges("|Y").fillet(0.8)
    
    extender = body.union(cap).union(flange)
    return extender

print("Testing script definition...")
fp = faceplate_v73()
print("Faceplate valid:", fp.val().isValid())
ext = ups_switch_extender()
print("Switch extender valid:", ext.val().isValid())
