"""Pi 5 + Waveshare Pi5 Connector Adapter (F) + Cuzor Mini UPS PRO case, v2.
Run: python3 make_case_v2.py  -> base.stl, lid.stl, fitcheck_assembly.stl, layout_top.png
Axes: X = case length, Y = case width, Z up. Origin = outer front-left-bottom corner.
Source tags:  [W] measured from Waveshare outline drawing (+-0.5)   [P] Raspberry Pi 5 mechanical standard
              [A] ASSUMED, verify with calipers before printing."""
import numpy as np, trimesh
from manifold3d import Manifold as M

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

def bx(x0, x1, y0, y1, z0, z1): return M.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])
def cyl(x, y, z, h, r): return M.cylinder(h, r, r, 48).translate([x, y, z])


CR, FIL = 5.0, 3.0      # UPS-style: plan corner radius, bottom/top edge fillet
def rrect(x0, x1, y0, y1, z0, z1, r):
    """rounded-corner prism"""
    return M.batch_hull([M.cylinder(z1 - z0, r, r, 64).translate([x, y, z0]) for x in (x0 + r, x1 - r) for y in (y0 + r, y1 - r)])
def filleted(x1, y1, h, r, f, bottom=True, n=6):
    """rounded prism, outer corner radius r, edge fillet f on bottom (or top) face"""
    layers = []
    for i in range(n + 1):
        th = (np.pi / 2) * i / n
        inset = f - f * np.sin(th)          # 0 at full size
        z = f - f * np.cos(th)
        layers.append(rrect(inset, x1 - inset, inset, y1 - inset, z, z + 0.01, r - inset if r - inset > 0.5 else 0.5))
    layers.append(rrect(0, x1, 0, y1, f, h, r))
    return M.batch_hull(layers)

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

def save(m, name):
    me = m.to_mesh()
    t_ = trimesh.Trimesh(np.array(me.vert_properties)[:, :3], np.array(me.tri_verts), process=True)
    t_.merge_vertices(); t_.export(name)
    print(f"{name}: watertight={t_.is_watertight} size={np.round(t_.extents, 1)}")
    return t_

save(base, "base.stl"); save(lid, "lid.stl")

# ---------------- FIT-CHECK ASSEMBLY (reference bodies, not for printing) ----------------
parts = {}
parts["pi_pcb"] = bx(BX, BX + PI_L, pi_y0, port_y, pcb_z, pcb_top)
parts["pi_usb_eth"] = bx(BX, BX + 21, pi_y0 + 1, port_y - 1, pcb_top, pcb_top + 16)
parts["cooler"] = bx(sx - COOLER_X / 2, sx + COOLER_X / 2, sy - COOLER_Y / 2, sy + COOLER_Y / 2, pcb_top, pcb_top + COOLER_H)
parts["ws_pcb"] = bx(BX, BX + BD_L, BY, BY + BD_W, pcb_z, pcb_top)
parts["ws_rj45"] = bx(BX - LEFT_PROTRUDE, BX + 17.5, BY + RJ45_Y[0], BY + RJ45_Y[1], pcb_top, pcb_top + 13.5)
parts["ws_hdmi"] = bx(BX - LEFT_PROTRUDE, BX + 11, BY + HDMI_Y[0], BY + HDMI_Y[1], pcb_top, pcb_top + 6.5)
parts["ws_terminal"] = bx(BX + 78.4, BX + BD_L + TERM_PROTRUDE, BY + TERM_Y[0], BY + TERM_Y[1], pcb_top, pcb_top + 10)
parts["ws_ssd2242"] = bx(BX + 34, BX + 76, BY + 11.6, BY + 33.6, pcb_top + 3.5, pcb_top + 6.0)
parts["ups"] = bx(ups_x0, ups_x1, ups_y0, ups_y0 + UPS_L, FLOOR, FLOOR + UPS_H)
asm = None
for p in parts.values(): asm = p if asm is None else asm + p
save(asm, "fitcheck_assembly.stl")
import os; os.makedirs("parts", exist_ok=True)
for _n, _p in parts.items(): save(_p, f"parts/{_n}.stl")

print("\nINTERFERENCE vs printed base (mm^3, want ~0):")
for n, p in parts.items():
    v = (p ^ base).volume()
    print(f"  {n:12s} {v:8.2f}")
print(f"\ninner {inner_x:.1f} x {inner_y:.1f} x {inner_h:.1f}  outer {out_x:.1f} x {out_y:.1f} x {out_h:.1f}  (+{LID} lid)")
print("hole centres (x,y):")
for lab, x, y in holes: print(f"  {lab} {x:6.1f} {y:6.1f}")
print("lid bosses:", [(round(x, 1), round(y, 1)) for x, y in bosses])

# ---------------- TOP-VIEW PNG ----------------
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
fig, ax = plt.subplots(figsize=(11, 8))
R = lambda x0, x1, y0, y1, **k: ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, **k))
R(0, out_x, 0, out_y, fill=False, lw=2, ec="k")
R(WALL, WALL + inner_x, WALL, WALL + inner_y, fill=False, lw=1, ec="gray")
R(BX, BX + PI_L, pi_y0, port_y, fc="#9ed9a0", ec="g", alpha=.8)
R(BX, BX + BD_L, BY, BY + BD_W, fc="#7fb2e5", ec="b", alpha=.8)
R(sx - COOLER_X / 2, sx + COOLER_X / 2, sy - COOLER_Y / 2, sy + COOLER_Y / 2, fc="#555", alpha=.5)
R(ups_x0, ups_x1, ups_y0, ups_y0 + UPS_L, fc="#e8c36a", ec="#a07800", alpha=.7)
R(BX - LEFT_PROTRUDE, BX + 17.5, BY + RJ45_Y[0], BY + RJ45_Y[1], fc="silver", ec="k")
R(BX - LEFT_PROTRUDE, BX + 11, BY + HDMI_Y[0], BY + HDMI_Y[1], fc="gold", ec="k")
R(BX + 78.4, BX + BD_L + TERM_PROTRUDE, BY + TERM_Y[0], BY + TERM_Y[1], fc="#2fa84f", ec="k")
R(BX + 34, BX + 76, BY + 11.6, BY + 33.6, fc="none", ec="purple", ls="--")
for lab, x, y in holes: ax.add_patch(Circle((x, y), STANDOFF_OD / 2, fc="orange", ec="k"))
for x, y in bosses: ax.add_patch(Circle((x, y), BOSS_R, fc="red", ec="k"))
ax.text(BX + 40, pi_y0 + 8, "Raspberry Pi 5 (rotated 180°)", ha="center"); ax.text(BX + 20, BY + 46, "Waveshare (F)", ha="center")
ax.text(sx, sy, "cooler\n(assumed)", ha="center", color="w", fontsize=8); ax.text(ups_x0 + UPS_W / 2, ups_y0 + 20, "Cuzor UPS\n(assumed size)", ha="center")
ax.text(BX + 62, BY + 24, "M.2 2242", color="purple", fontsize=8)
ax.text(out_x - 3, cy0 + 20, "UPS ctrl\nwindow →", ha="right", fontsize=8)
ax.set_xlim(-8, out_x + 8); ax.set_ylim(-8, out_y + 8); ax.set_aspect("equal")
ax.set_title(f"Top view  |  orange = M2.5 standoffs (8)  red = M3 lid bosses (6)  |  {out_x:.0f} x {out_y:.0f} mm")
plt.savefig("layout_top.png", dpi=130, bbox_inches="tight")
