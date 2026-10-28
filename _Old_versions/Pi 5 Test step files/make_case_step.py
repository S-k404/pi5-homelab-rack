"""Pi 5 + Waveshare Pi5 Connector Adapter (F) + Cuzor Mini UPS PRO case, v2.
Run: python3 make_case_v2.py  -> base.stl, lid.stl, fitcheck_assembly.stl, layout_top.png
Axes: X = case length, Y = case width, Z up. Origin = outer front-left-bottom corner.
Source tags:  [W] measured from Waveshare outline drawing (+-0.5)   [P] Raspberry Pi 5 mechanical standard
              [A] ASSUMED, verify with calipers before printing."""
from build123d import *

# ---------------- PARAMS (mm) ----------------
WALL, FLOOR, LID = 2.4, 2.4, 2.4
# Pi 5 [P]: ports (USB-C, 2x micro-HDMI) on the long edge; holes 58x49 at 3.5 from edges
PI_L, PI_W = 85.0, 56.0
PI_HOLES = [(3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5)]   # std orientation, port edge at y=0
PI_USBC_X = 11.2                                                    # USB-C centre from the corner
# Waveshare (F) [W]
BD_L, BD_W = 85.0, 52.5                                             # PCB (86 overall in drawing)
BD_HOLES = [(23.0, 3.0), (81.0, 3.0), (23.0, 49.5), (81.0, 49.5)]   # 58 apart, 46.5 apart
PLUG_GAP = 6.7        # [W] male Type-C/micro-HDMI plug length = gap Pi port edge -> board edge
LEFT_PROTRUDE = 3.5   # [W] RJ45 + HDMI stick out past the PCB's left edge
TERM_PROTRUDE = 12.0  # [W] green screw terminal sticks out past the right edge
RJ45_Y, HDMI_Y, TERM_Y = (22.3, 38.8), (3.0, 19.1), (6.8, 15.6)    # [W] board-local y ranges
# Cooler [A]
COOLER_X, COOLER_Y, COOLER_H = 58.0, 40.0, 15.0   # [S] Armor Lite V5 product-size drawing: 58x40 footprint, 15 mm with fan
SOC = (32.0, 28.0)    # [S] from Armor Lite V5 install photo: heatsink hugs GPIO side, ~15% gap at port end; +-3 mm
# UPS [S] Cuzor shop page 100x80x28; port/switch layout [A]
UPS_L, UPS_W, UPS_H = 100.0, 80.0, 28.0
UPS_CTRL_FROM = 0.55  # [S] photos: switch ~0.63, LED ~0.78, OUT jack ~0.90 along the 100 mm face
# Hardware
STANDOFF_H, STANDOFF_OD, PILOT = 5.0, 6.0, 2.2     # M2.5 self-tap, screw M2.5x8
BOSS_R, BOSS_PILOT, LID_HOLE = 2.8, 2.5, 3.4       # M3x10 lid screws
M_LEFT, M_FRONT, M_BACK, RIGHT_GAP, TOP_CLR = 5.0, 5.0, 5.0, 6.0, 3.0
GPIO_SLOT = True      # cable slot in the front wall for the Pi GPIO header (e-paper)

# ---------------- derived layout ----------------
PCB_T = 1.6
pcb_z = FLOOR + STANDOFF_H            # underside of both PCBs
pcb_top = pcb_z + PCB_T
inner_x = M_LEFT + BD_L + TERM_PROTRUDE + RIGHT_GAP + UPS_W + 0.5
inner_y = max(M_FRONT + PI_W + PLUG_GAP + BD_W + M_BACK, UPS_L + 12)
inner_h = max(STANDOFF_H + PCB_T + COOLER_H + TOP_CLR, UPS_H + TOP_CLR)
out_x, out_y, out_h = inner_x + 2 * WALL, inner_y + 2 * WALL, FLOOR + inner_h

BX = WALL + M_LEFT                                  # boards' left edge
pi_y0 = WALL + M_FRONT + (inner_y - (M_FRONT + PI_W + PLUG_GAP + BD_W + M_BACK)) / 2
port_y = pi_y0 + PI_W                               # Pi port edge faces +Y
BY = port_y + PLUG_GAP                              # Waveshare PCB front edge
ups_x1 = WALL + inner_x
ups_x0 = ups_x1 - UPS_W
ups_y0 = WALL + (inner_y - UPS_L) / 2

def pi2case(px, py):   # Pi rotated 180 deg: USB-C corner at +X, Ethernet/USB at -X, port edge to +Y
    return BX + PI_L - px, port_y - py

def bx(x0, x1, y0, y1, z0, z1):
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=Align.MIN)
def cyl(x, y, z, h, r):
    return Pos(x, y, z) * Cylinder(r, h, align=(Align.CENTER, Align.CENTER, Align.MIN))

CR, FIL = 5.0, 3.0      # UPS-style: plan corner radius, bottom edge fillet
def rrect(x0, x1, y0, y1, z0, z1, r):
    b = bx(x0, x1, y0, y1, z0, z1)
    return fillet(b.edges().filter_by(Axis.Z), r)
def filleted(x1, y1, h, r, f, z_top_edges=False):
    b = rrect(0, x1, 0, y1, 0, h, r)
    face_edges = b.edges().filter_by_position(Axis.Z, h - 1e-3, h + 1e-3) if z_top_edges else b.edges().filter_by_position(Axis.Z, -1e-3, 1e-3)
    return fillet(face_edges, f)

# ---------------- BASE ----------------
base = filleted(out_x, out_y, out_h, CR, FIL) - rrect(WALL, WALL + inner_x, WALL, WALL + inner_y, FLOOR, out_h + 1, CR - WALL)
# UPS-style seam groove around the shell
base -= rrect(-1, out_x + 1, -1, out_y + 1, out_h - 9, out_h - 8.2, CR + 1) - rrect(0.6, out_x - 0.6, 0.6, out_y - 0.6, out_h - 10, out_h - 7, CR - 0.6)

holes = []   # (label, x, y) for the drawing / hardware list
for i, (hx, hy) in enumerate(PI_HOLES):
    x, y = pi2case(hx, hy); holes.append(("Pi", x, y))
for (hx, hy) in BD_HOLES:
    holes.append(("WS", BX + hx, BY + hy))
for _, x, y in holes:
    base += cyl(x, y, FLOOR, STANDOFF_H, STANDOFF_OD / 2) - cyl(x, y, FLOOR + 1, STANDOFF_H, PILOT / 2)

# UPS corner ribs (UPS rests against right wall; ribs on the other three sides)
t, rl, rh = 1.2, 14.0, 8.0
px0, px1, py0, py1 = ups_x0 - 0.0, ups_x1, ups_y0, ups_y0 + UPS_L
for yy in (py0 - t, py1):                       # end ribs
    base += bx(px0 - t, px0 + rl, yy, yy + t, FLOOR, FLOOR + rh) + bx(px1 - rl, px1, yy, yy + t, FLOOR, FLOOR + rh)
for (ya, yb) in ((py0, py0 + rl), (py1 - rl, py1)):  # left-side ribs
    base += bx(px0 - t, px0, ya, yb, FLOOR, FLOOR + rh)

# lid-screw bosses: 4 corners + 2 between boards and UPS
xm = BX + BD_L + TERM_PROTRUDE + RIGHT_GAP / 2
bosses = [(WALL + 2.5, WALL + 2.5), (out_x - WALL - 2.5, WALL + 2.5), (WALL + 2.5, out_y - WALL - 2.5),
          (out_x - WALL - 2.5, out_y - WALL - 2.5), (xm, WALL + 2.2), (xm, out_y - WALL - 2.2)]
for x, y in bosses:
    base += cyl(x, y, FLOOR, inner_h, BOSS_R) - cyl(x, y, out_h - 10, 11, BOSS_PILOT / 2)

# wall cutouts
pi_ylo, pi_yhi = pi_y0, port_y
base -= bx(-1, WALL + 1, pi_ylo, pi_yhi, pcb_top - 1.5, pcb_top + 17.5)                 # Pi USB/Ethernet
base -= bx(-1, WALL + 1, BY + RJ45_Y[0] - 0.8, BY + RJ45_Y[1] + 0.8, pcb_top - 0.5, pcb_top + 14.5)   # RJ45
base -= bx(-1, WALL + 1, BY + HDMI_Y[0] - 0.8, BY + HDMI_Y[1] + 0.8, pcb_top - 0.5, pcb_top + 8.5)    # HDMI
cy0 = ups_y0 + UPS_CTRL_FROM * UPS_L
base -= bx(out_x - WALL - 1, out_x + 1, cy0, ups_y0 + UPS_L, FLOOR + 1, FLOOR + UPS_H - 2)     # UPS switch/LED/OUT
# IN jack: 80 mm end face, ~7 % (6 mm) from one side edge, mid-height [S photo]; end not shown -> notch both ends
for y0, y1, ux in ((-1, WALL + 1, ups_x0 + 6), (out_y - WALL - 1, out_y + 1, ups_x1 - 6)):      # UPS input cable notches
    base -= bx(ux - 8, ux + 8, y0, y1, FLOOR + 5, FLOOR + 22)
if GPIO_SLOT:
    gx0, gy = pi2case(57.9, 0)[0], 0
    gx1 = pi2case(7.1, 0)[0]
    base -= bx(gx0, gx1, -1, WALL + 1, pcb_top, pcb_top + 10)

# ---------------- LID (print upside down) ----------------
lid = filleted(out_x, out_y, LID, CR, 2.0)
for x, y in bosses:
    lid -= cyl(x, y, -1, LID + 2, LID_HOLE / 2)
sx, sy = pi2case(*SOC)
for k in range(7):                                              # vents above the cooler
    lid -= bx(sx - 15, sx + 15, sy - 16 + k * 5.2 - 1.25, sy - 16 + k * 5.2 + 1.25, -1, LID + 1)


import os
os.makedirs("step", exist_ok=True)
for name, shp in (("base", base), ("lid", lid)):
    solids = shp.solids()
    print(name, "solids:", len(solids), "volume:", round(shp.volume), "valid:", shp.is_valid)
    export_step(Compound(solids) if len(solids) > 1 else solids[0], f"step/pi5_case_{name}.step")
