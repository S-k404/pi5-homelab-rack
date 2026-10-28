"""
Mini server stand for: Cuzor Mini UPS Pro (bottom bay) + Raspberry Pi 5 and
Waveshare Pi5 Connector Adapter (F) side by side on a deck above. Open top for HATs.

Two printed parts, each ONE solid:
  Stand_Base  — base plate, UPS bay rails, 4 corner posts (M3 heat-set holes on top)
  Stand_Deck  — deck plate with Pi + adapter standoffs, vents, cable slot, M3 holes
Both print flat with no supports. Units mm. Same XY frame as the Pi model
(Pi corner at 0,0; Pi USB/Ethernet end toward +X; adapter toward -Y).
"""
import os
import cadquery as cq
from cadquery import Assembly, Location, Vector, Color
import build

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stand_out")
os.makedirs(OUT, exist_ok=True)

# ---- overall footprint ---------------------------------------------------
X0, X1 = -7.0, 93.0          # 100 mm along Pi length
Y0, Y1 = -64.0, 64.0         # 128 mm across Pi + adapter
PLATE = 3.0                  # base and deck plate thickness
POST = 8.0                   # corner post square size

# ---- UPS bay -------------------------------------------------------------
UPS_X, UPS_Y, UPS_Z = 80.0, 100.0, 28.0   # UPS turned 90° (100 mm runs along Y)
UPS_CX, UPS_CY = 43.0, 0.0
CLEAR = 0.6                               # per side
BAY_H = UPS_Z + 1.5                       # gap above UPS
RAIL_H = 6.0

# ---- deck ----------------------------------------------------------------
DECK_Z = PLATE + BAY_H                    # underside of deck (32.5)
STANDOFF_H = 5.0                          # clears the Pi's microSD socket
STANDOFF_OD = 6.5
PILOT_D = 2.2                             # M2.5 self-tap pilot (use 3.6 for heat-set)
M3_CLEAR, M3_INSERT_D, M3_INSERT_DEPTH = 3.4, 4.0, 6.0

PI_HOLES = [(3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5)]               # exact
ADAPTER_SHIFT_Y = -1.5
ADAPTER_HOLES = [(x, y + ADAPTER_SHIFT_Y) for x, y in
                 [(3.5, -3.5), (61.5, -3.5), (3.5, -52.5), (61.5, -52.5)]]    # placeholder

POST_CENTERS = [(X0 + POST / 2, Y0 + POST / 2), (X1 - POST / 2, Y0 + POST / 2),
                (X0 + POST / 2, Y1 - POST / 2), (X1 - POST / 2, Y1 - POST / 2)]


def box(x0, y0, z0, dx, dy, dz):
    return cq.Workplane("XY").box(dx, dy, dz, centered=False).translate((x0, y0, z0))


def stand_base():
    base = box(X0, Y0, 0, X1 - X0, Y1 - Y0, PLATE).edges("|Z").fillet(4)
    # side rails locate the UPS in Y and tie the posts together
    ry = UPS_CY + UPS_Y / 2 + CLEAR
    for y_lo, y_hi in ((ry, Y1), (Y0, -ry)):
        base = base.union(box(X0, y_lo, PLATE, X1 - X0, y_hi - y_lo, RAIL_H))
    # small end stops at the back (+X) so the UPS can't slide through
    bx = UPS_CX + UPS_X / 2 + CLEAR
    for yc in (-35.0, 35.0):
        base = base.union(box(bx, yc - 5, PLATE, 3.0, 10.0, 4.0))
    # corner posts up to the deck
    for cx, cy in POST_CENTERS:
        base = base.union(box(cx - POST / 2, cy - POST / 2, PLATE, POST, POST, BAY_H))
    # heat-set insert holes in post tops
    base = (base.faces(">Z").workplane(origin=(0, 0, DECK_Z))
            .pushPoints(POST_CENTERS).hole(M3_INSERT_D, M3_INSERT_DEPTH))
    # vent slots under the UPS
    slots = cq.Workplane("XY")
    for i in range(7):
        x = UPS_CX - 30 + i * 10
        base = base.cut(box(x - 2.0, -35.0, -0.1, 4.0, 70.0, PLATE + 0.2))
    # rubber-foot recesses (Ø10 x 1) underneath
    feet = [(X0 + 10, Y0 + 10), (X1 - 10, Y0 + 10), (X0 + 10, Y1 - 10), (X1 - 10, Y1 - 10)]
    for fx, fy in feet:
        base = base.cut(cq.Workplane("XY").circle(5.0).extrude(1.0).translate((fx, fy, -0.01)))
    return base.union(hdmi_holder())


# ---- UGREEN 20134 micro-HDMI -> HDMI female cable: holder on the +Y side ----
# [E] UGREEN does not publish end dimensions; measure yours and edit these.
HDMI_F_W, HDMI_F_H, HDMI_F_L = 23.0, 12.0, 38.0   # female end housing
HDMI_CLEAR = 0.3                                  # per side, snug press fit
HOLDER_WALL, HOLDER_FLOOR, HOLDER_LIP = 2.0, 2.0, 1.0
CABLE_SLOT = 6.0


def hdmi_holder():
    """Cradle on the outside of the +Y rail. HDMI socket faces the front (-X),
    flush with the stand's front edge; back wall takes the plug-in force."""
    iw = HDMI_F_W + 2 * HDMI_CLEAR
    ih = HDMI_F_H + 2 * HDMI_CLEAR
    il = HDMI_F_L + HDMI_CLEAR
    ow = iw + 2 * HOLDER_WALL
    oh = ih + HOLDER_FLOOR + HOLDER_LIP
    y_in = Y1                                   # attaches to the base's +Y edge
    x_front = X0
    blk = box(x_front, y_in, 0, il + HOLDER_WALL, ow, oh)
    # cavity, open at the front and the top
    blk = blk.cut(box(x_front - 0.1, y_in + HOLDER_WALL, HOLDER_FLOOR, il + 0.1, iw, ih + HOLDER_LIP + 0.1))
    # retaining lips at the top edges (1 mm each side) — snap the end in from above
    for yl in (y_in + HOLDER_WALL, y_in + HOLDER_WALL + iw - 1.0):
        blk = blk.union(box(x_front + 4, yl, HOLDER_FLOOR + ih, il - 8, 1.0, HOLDER_LIP))
    # cable slot through the back wall
    blk = blk.cut(box(x_front + il - 0.1, y_in + ow / 2 - CABLE_SLOT / 2, HOLDER_FLOOR,
                      HOLDER_WALL + 0.2, CABLE_SLOT, oh))
    return blk


def ugreen_cable_end():
    """Simple single-solid model of the HDMI female end + 30 mm of cable."""
    housing = box(0, 0, 0, HDMI_F_L, HDMI_F_W, HDMI_F_H)
    socket = box(-0.01, HDMI_F_W / 2 - 7.0, HDMI_F_H / 2 - 2.25, 6.0, 14.0, 4.5)
    cable = (cq.Workplane("YZ").circle(2.4).extrude(30.0)
             .translate((HDMI_F_L, HDMI_F_W / 2, HDMI_F_H / 2)))
    return housing.cut(socket).union(cable)


def stand_deck():
    deck = box(X0, Y0, 0, X1 - X0, Y1 - Y0, PLATE).edges("|Z").fillet(4)
    # M3 clearance holes over the posts (also used later to stack a top tier)
    deck = deck.faces(">Z").workplane().pushPoints(POST_CENTERS).hole(M3_CLEAR)
    # vent slots under the Pi and under the adapter (kept clear of standoffs)
    for y_lo, y_hi in ((10.0, 46.0), (-50.0, -12.0)):
        for i in range(8):
            x = 10.0 + i * 6.0
            deck = deck.cut(box(x, y_lo, -0.1, 3.0, y_hi - y_lo, PLATE + 0.2))
    # cable pass-through at the -X end (UPS OUT -> adapter 7-24 V terminal)
    deck = deck.cut(box(-6.0, -42.0, -0.1, 4.5, 16.0, PLATE + 0.2).edges("|Z").fillet(1.5))
    # standoffs
    for hx, hy in PI_HOLES + ADAPTER_HOLES:
        so = (cq.Workplane("XY").circle(STANDOFF_OD / 2).extrude(STANDOFF_H)
              .translate((hx, hy, PLATE)))
        deck = deck.union(so)
    deck = (deck.faces(">Z").workplane(origin=(0, 0, PLATE + STANDOFF_H))
            .pushPoints(PI_HOLES + ADAPTER_HOLES).hole(PILOT_D, STANDOFF_H))
    return deck


def fuse(parts):
    shapes = [s for wp, _ in parts.values() for s in wp.solids().vals()]
    return shapes[0].fuse(*shapes[1:]).clean() if len(shapes) > 1 else shapes[0]


if __name__ == "__main__":
    base = stand_base().val()
    deck = stand_deck().val()
    for name, solid in (("Stand_Base", base), ("Stand_Deck", deck)):
        assert len(solid.Solids()) == 1, name
        cq.exporters.export(cq.Workplane().add(solid), os.path.join(OUT, name + ".step"))
        cq.exporters.export(cq.Workplane().add(solid), os.path.join(OUT, name + ".stl"),
                            tolerance=0.02, angularTolerance=0.1)
        bb = solid.BoundingBox()
        print(f"{name:12s} {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f}")

    board_z = DECK_Z + PLATE + STANDOFF_H          # Pi / adapter underside
    ups_rot = Location(Vector(UPS_CX, UPS_CY, PLATE), Vector(0, 0, 1), 90)
    comps = {
        "Stand_Base": (base, Location(), Color(0.85, 0.45, 0.10)),
        "Stand_Deck": (deck, Location(Vector(0, 0, DECK_Z)), Color(0.85, 0.45, 0.10)),
        "Cuzor_MiniUPS_Pro": (fuse(build.cuzor_ups_pro()), ups_rot, Color(0.12, 0.12, 0.13)),
        "RaspberryPi5": (fuse(build.raspberry_pi_5()), Location(Vector(0, 0, board_z)), Color(0.05, 0.45, 0.2)),
        "Waveshare_Adapter_F": (fuse(build.waveshare_adapter_f()),
                                Location(Vector(0, ADAPTER_SHIFT_Y, board_z)), Color(0.1, 0.1, 0.1)),
        "EVM_2230_NVMe": (fuse(build.evm_2230_nvme()),
                          Location(Vector(14.5, -41.5, board_z + 3.1)), Color(0.05, 0.2, 0.5)),
        "ArmorLite_V5": (fuse(build.armor_lite_v5()),
                         Location(Vector(32, 28, board_z + 3.9)), Color(0.2, 0.2, 0.22)),
        "UGREEN_HDMI_end": (ugreen_cable_end().val(),
                            Location(Vector(X0, Y1 + HOLDER_WALL + HDMI_CLEAR, HOLDER_FLOOR + HDMI_CLEAR)),
                            Color(0.1, 0.1, 0.1)),
    }
    cq.exporters.export(cq.Workplane().add(comps["UGREEN_HDMI_end"][0]),
                        os.path.join(OUT, "UGREEN_20134_HDMI_end.step"))
    asm = Assembly(name="Pi5_mini_server_stand")
    for n, (s, loc, col) in comps.items():
        asm.add(s, name=n, loc=loc, color=col)
    asm.save(os.path.join(OUT, "Pi5_Stand_ASSEMBLY.step"), exportType="STEP")

    # interference check between every pair
    placed = {n: s.moved(loc) for n, (s, loc, _) in comps.items()}
    names = list(placed)
    clashes = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = placed[names[i]], placed[names[j]]
            v = a.intersect(b).Volume()
            if v > 0.5:
                clashes.append((names[i], names[j], round(v, 1)))
    print("clashes (>0.5 mm³):", clashes or "none")
    bb = cq.Compound.makeCompound(list(placed.values())).BoundingBox()
    print(f"overall {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f}")
