"""Pi 5 + Waveshare Pi5 Connector Adapter (F) + Armor Lite V5 + Cuzor MiniUPS PRO — v3 (stacked, compact).

Three prints: UPS tray (bottom), board tray (top), lid.
Frame: x = left->right seen from the front, y = front->back, z = up.
Origin = inner front-left corner, top of the UPS-tray floor. All mm.
"""
from build123d import *

# ---------------- parameters ----------------
W = 2.2            # walls
IW = 113.9         # inner width (both trays)
R_OUT = 3.0
FOOT = 3.0

# UPS tray
LF = 2.0           # floor
LD = 87.0          # inner depth
UPS = (80.0, 100.0, 28.0)          # depth(y) x width(x) x height
UPS_X = (0.6, 100.6)               # switch/LED/OUT end at the right
UPS_Y = (0.6, 80.6)
RIB = 1.0
PLENUM_TOP = 34.5                  # = underside of board-tray floor (5.5 mm air gap over UPS)
CH_X = (101.5, IW)                 # side air/cable channel right of the UPS
JOINTS = [(107.7, 40.0), (14.0, 84.5), (75.0, 84.5)]   # M3 countersunk, board tray -> UPS tray

# board tray
UF = 2.4
ZS = PLENUM_TOP + UF               # 36.9 board-tray floor top
UD = 110.0                         # inner depth
HL = 63.4                          # lid underside
LT = 2.4

# Pi 5 placement (model frame: 85 x 56, port edge y=0, USB/ETH at x=85)
X_PI, Y0 = 56.9, 5.0
PI_BOSS = 5.0
Z_PI = ZS + PI_BOSS                # 41.9
PI_HOLES = [(3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5)]
def pi_xy(mx, my): return (X_PI + my, Y0 + 85 - mx)

# Adapter (drawing frame: x_d along 85, y_d along 52.5, plug edge y_d=0, ports at x_d=0)
AX, AY = 55.0, 4.45
PAD = 3.5                          # solid drill-anywhere pads
ZA_MIN, ZA_MAX = ZS + PAD + 1.1, ZS + PAD + 3.2   # shims 1.1..3.2 -> 41.5..43.6
AD_HOLES = [(24.05, 3.0), (82.05, 3.0), (24.05, 49.5), (82.05, 49.5)]
def ad_xy(xd, yd): return (AX - yd, AY + xd)

LID_POSTS = [(3.0, UD - 3.0), (IW - 3.0, UD - 3.0)]

def rrect(w, h, r):
    return RectangleRounded(w, h, r) if r > 0 and min(w, h) > 2 * r + 0.01 else Rectangle(w, h)
def box_at(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)
def cut_y(yface_out, x0, x1, z0, z1, r=1.0, depth=W):
    """through-cut in a wall normal to y, starting at the outer face yface_out going +y"""
    sk = Plane.XZ * Pos((x0 + x1) / 2, (z0 + z1) / 2) * rrect(x1 - x0, z1 - z0, r)
    return Pos(0, yface_out + depth + 1.0, 0) * extrude(sk, amount=depth + 2.0)
def cut_x(xface, y0, y1, z0, z1, r=1.0):
    sk = Plane.YZ * Pos((y0 + y1) / 2, (z0 + z1) / 2) * rrect(y1 - y0, z1 - z0, r)
    return Pos(xface - 1.0, 0, 0) * extrude(sk, amount=W + 2.0)
def slot_y(cx, cy, length, width, z0, z1):
    return Pos(cx, cy, z0) * extrude(SlotOverall(length, width, rotation=90), amount=z1 - z0)
def shell(depth, z0, z1):
    o = Pos(IW / 2, depth / 2, (z0 + z1) / 2) * Box(IW + 2 * W, depth + 2 * W, z1 - z0)
    return fillet(o.edges().filter_by(Axis.Z), R_OUT)

# =============== UPS TRAY ===============
low = shell(LD, -LF, PLENUM_TOP)
low -= Pos(IW / 2, LD / 2, PLENUM_TOP / 2 + 0.5) * Box(IW, LD, PLENUM_TOP + 1)
for fx, fy in [(9, 9), (IW - 9, 9), (9, LD - 9), (IW - 9, LD - 9)]:
    low += Pos(fx, fy, -LF - FOOT / 2) * Cylinder(5.0, FOOT)
for rx in [12, 37, 63, 88]:                                   # UPS ribs (stick foam tape on them)
    low += box_at(rx - 1, rx + 1, 6, 75, 0, RIB)
low += box_at(UPS_X[1] + 0.6, UPS_X[1] + 2.0, 0, 10, 0, 8)    # keeps UPS out of the channel
low += box_at(UPS_X[1] + 0.6, UPS_X[1] + 2.0, 62, 80.5, 0, 8)
for jx, jy in JOINTS:                                         # joint posts, M3 pilot
    low += Pos(jx, jy, PLENUM_TOP / 2) * Cylinder(3.25, PLENUM_TOP)
    low -= Pos(jx, jy, PLENUM_TOP - 6) * Cylinder(1.25, 12.2)
lcuts = [
    cut_y(-W, 58, 110, 5, 25, r=3),       # front: switch, LED, OUT (+ cable turns into side channel)
    cut_y(LD, 80, 112, 5, 29, r=3),       # back: DC-IN + cable exit to the overhang
]
for vy in range(10, 77, 6):              # left wall: low slots + plenum slots
    lcuts.append(cut_x(-W, vy - 1.2, vy + 1.2, 6, 24))
    lcuts.append(cut_x(-W, vy - 1.2, vy + 1.2, 29.8, 33.6, r=0.6))
for vy in range(10, 80, 6):              # right wall (channel)
    lcuts.append(cut_x(IW, vy - 1.2, vy + 1.2, 5, 31))
for vx in range(10, 52, 6):              # back wall vents behind the UPS
    lcuts.append(cut_y(LD, vx - 1.2, vx + 1.2, 6, 29))
for vy in range(14, 80, 6):              # floor slots in the channel
    lcuts.append(Pos(0, 0, -LF - 1) * extrude(Pos(104.2, vy) * SlotOverall(4.5, 2.4), amount=LF + 1.5))
for c in lcuts:
    low -= c

# =============== BOARD TRAY ===============
up = shell(UD, PLENUM_TOP, HL)
up -= Pos(IW / 2, UD / 2, (ZS + HL + 1) / 2) * Box(IW, UD, HL - ZS + 1)

# Pi bosses: d6, 2.2 pilot for M2.5 self-tap (or 3.6 heat-set: drill out)
for mx, my in PI_HOLES:
    x, y = pi_xy(mx, my)
    up += Pos(x, y, ZS + PI_BOSS / 2) * Cylinder(3.0, PI_BOSS)
    up += Pos(x, y, ZS + 0.75) * Cone(3.6, 3.0, 1.5)
    up -= Pos(x, y, ZS + PI_BOSS - 3.4) * Cylinder(1.1, 7.0)
# adapter drill-anywhere pads (adapter is located by its plugs, then mark+drill 2.0 mm)
for xd, yd in AD_HOLES:
    x, y = ad_xy(xd, yd)
    up += box_at(x - 0.35 - 5.0, x - 0.35 + 5.0, y - 4.5, y + 4.5, ZS, ZS + PAD)
# lid posts (M3 self-tap)
for px, py in LID_POSTS:
    up += Pos(px, py, (ZS + HL) / 2) * Cylinder(3.4, HL - ZS)
    up -= Pos(px, py, HL - 7) * Cylinder(1.25, 14.2)
# joint holes: countersunk M3 from inside
for jx, jy in JOINTS:
    up -= Pos(jx, jy, PLENUM_TOP + UF / 2) * Cylinder(1.7, UF + 1)
    up -= Pos(jx, jy, ZS - 1.65) * Cone(1.6, 3.15, 1.66, align=(Align.CENTER, Align.CENTER, Align.MIN))
# Pi power-button guide tube (back wall -> 2.5 mm short of the button)
BTN_X, BTN_Z = X_PI + 18.4, Z_PI + 3.04
up += Pos(BTN_X, (93.0 + UD) / 2, BTN_Z) * Rot(90, 0, 0) * Cylinder(3.5, UD - 93.0)
web = box_at(BTN_X - 1.0, BTN_X + 1.0, 93.0, UD, ZS, BTN_Z)
web -= box_at(BTN_X - 2, BTN_X + 2, 97, 106, ZS - 0.1, ZS + 4.5)   # cable arch under the tube
up += web
up -= Pos(BTN_X, (92 + UD + W + 1) / 2, BTN_Z) * Rot(90, 0, 0) * Cylinder(1.9, UD + W + 1 - 92)
up -= Pos(BTN_X, UD + W, BTN_Z) * Rot(90, 0, 0) * Cone(1.9, 3.2, 1.4)
# cable-tie anchors (back strip)
def tie_y(cx, cy):
    b = box_at(cx - 4, cx + 4, cy - 3, cy + 3, ZS, ZS + 4.5)
    return b - box_at(cx - 1.75, cx + 1.75, cy - 4, cy + 4, ZS - 0.1, ZS + 2.0)
up += tie_y(92, 106)
up += tie_y(60, 104)
# cable pass from the UPS (comes up under the rear overhang)
up -= Pos(101, 98, PLENUM_TOP - 1) * extrude(RectangleRounded(10, 8, 2), amount=UF + 2)

# front-wall port cut-outs (global z; Pi fixed, adapter allows slot travel + shim range)
dz = Z_PI - 7.5
ucuts = [
    cut_y(-W, 58.76, 75.54, 6.7 + dz, 22.6 + dz),         # Pi ETH
    cut_y(-W, 78.05, 93.75, 6.7 + dz, 25.7 + dz),         # Pi USB stack 1
    cut_y(-W, 96.05, 111.75, 6.7 + dz, 25.7 + dz),        # Pi USB stack 2
    cut_y(-W, 35.45, 54.45, ZA_MIN + 1.2, ZA_MAX + 8.5),   # adapter HDMI
    cut_y(-W, 14.4, 34.15, ZA_MIN + 1.2, ZA_MAX + 15.5),   # adapter RJ45
    cut_x(-W, 38.0, 50.0, 47.0, 57.0, r=3.0),             # UGREEN micro-HDMI extender cable exit (rack cradle)
]
# lid-tooth pockets in the front wall (1 mm deep)
for px in [(20, 30), (60, 70)]:
    ucuts.append(Pos(0, 0, 0) * box_at(px[0], px[1], -1.0, 0.1, HL - 3.1, HL - 1.5))
# wall vents
for vy in range(30, 83, 5):
    ucuts.append(cut_x(-W, vy - 1, vy + 1, ZS + 9, ZS + 20))
for vy in range(10, 86, 5):
    ucuts.append(cut_x(IW, vy - 1, vy + 1, ZS + 8, ZS + 20))
for vx in list(range(84, 106, 5)) + list(range(8, 37, 5)):
    ucuts.append(cut_y(UD, vx - 1, vx + 1, ZS + 9, ZS + 21))
# floor vents (into plenum / overhang): under Pi and under adapter
for vx in range(66, 105, 5):
    ucuts.append(slot_y(vx, 58, 44, 2.4, PLENUM_TOP - 1, ZS + 0.5))
for vx in range(14, 46, 5):
    ucuts.append(slot_y(vx, 58, 44, 2.4, PLENUM_TOP - 1, ZS + 0.5))
for c in ucuts:
    up -= c

# =============== LID ===============
lid = Pos(IW / 2, UD / 2, HL + LT / 2) * Box(IW + 2 * W, UD + 2 * W, LT)
lid = fillet(lid.edges().filter_by(Axis.Z), R_OUT)
for px, py in LID_POSTS:
    lid -= Pos(px, py, HL + LT / 2) * Cylinder(1.7, LT + 1)
    lid -= Pos(px, py, HL + LT - 1.5) * Cone(1.7, 3.3, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
# front teeth (hook into the wall pockets), side/back locating lugs
for px in [(21, 29), (61, 69)]:
    lid += box_at(px[0], px[1], 0.25, 1.75, HL - 3.6, HL)
    lid += box_at(px[0], px[1], -0.8, 0.25, HL - 2.9, HL - 1.7)
lid += box_at(0.3, 1.5, 92, 100, HL - 4, HL)
lid += box_at(IW - 1.5, IW - 0.3, 92, 100, HL - 4, HL)
lid += box_at(30, 40, UD - 1.5, UD - 0.3, HL - 4, HL)
# Pi / cooler hex grill
for i in range(9):
    gx = 60 + i * 6.2
    for j in range(11):
        gy = 22 + j * 6.0 + (3.0 if i % 2 else 0)
        if gy < 86:
            lid -= Pos(gx, gy, HL - 1) * extrude(RegularPolygon(2.6, 6, major_radius=False), amount=LT + 2)
for vx in range(14, 49, 5):                       # adapter / SSD slots
    lid -= slot_y(vx, 56, 46, 2.4, HL - 1, HL + LT + 1)
for vx in range(62, 109, 6):                      # rear exhaust slots
    lid -= Pos(vx, 100, HL - 1) * extrude(SlotOverall(12, 2.4, rotation=90), amount=LT + 2)

# =============== SMALL PARTS: shims ===============
parts = []
for k, t in enumerate([0.5, 1.0, 2.0]):
    for i in range(4):
        parts.append(Pos(i * 10, k * 10, t / 2) * (Cylinder(3.6, t) - Cylinder(1.45, t + 0.2)))
small = Compound(parts)

if __name__ == "__main__":
    import os; os.makedirs("out3", exist_ok=True)
    for nm, s in [("ups_tray", low), ("board_tray", up), ("lid", lid)]:
        export_step(s, f"out3/Pi5_UPS_v3_{nm}.step")
        export_stl(s, f"out3/Pi5_UPS_v3_{nm}.stl", tolerance=0.02, angular_tolerance=0.15)
        b = s.bounding_box(); print(nm, b.min, b.max, "valid", s.is_valid)
    export_stl(small, "out3/Pi5_UPS_v3_shims.stl", tolerance=0.01, angular_tolerance=0.1)
