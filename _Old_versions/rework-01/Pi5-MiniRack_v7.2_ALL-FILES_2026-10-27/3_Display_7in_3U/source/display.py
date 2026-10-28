"""
7-inch display module (C-type) — 10-inch 3U rack unit for a Waveshare "7inch HDMI LCD (C)"-type screen, which is
what the REES52 7" 1024x600 HDMI touch listing shows (glass with the driver board bonded to its back, four corner
ears with holes, HDMI and micro-USB facing sideways out of one short edge).
Screen data is Waveshare's own 3D model (Component_Models/Waveshare_7inch_HDMI_LCD_C.step):
165 x 124.2 mm over the ears, glass 165 x 100.1, 8.0 mm from the glass front to the board back, 14.1 with connectors.
The screen lies face-down on the bezel, is located by the top/bottom flanges and four corner walls, and is held by
four clips on its ears. Both sides are open behind the bezel so the HDMI and USB plugs fit whichever way round the
screen goes. The ears are the same part as the B1 dock's.
Coordinates (mm): x across, y up (0 = centre), z back. The ears' back face is z = 3 (rail face).
"""
import os
import cadquery as cq
from b1_drawer import box, cyl_z
from b1_dock import PANEL_H, EAR_T, EAR_SCREW_X, EAR_SCREW_Y, INSERT_D, INSERT_DEPTH, ear  # noqa: F401

# ---- screen (Waveshare 7inch HDMI LCD (C) model; measure yours) ----
SCR_W, SCR_H = 165.0, 124.16       # board + ears outline (the ears set the height)
GLASS_H = 100.1                    # glass height; its centre sits 1.45 mm off the board centre
GLASS_DY = 1.45
STACK = 6.3                        # glass front -> board front (glass + LCD)
BOARD_BACK = 8.0                   # glass front -> board back (the ears' back face)
ACTIVE = (154.21, 85.92)
AA_DX, AA_DY = 1.75, 2.35          # active area offset from the LCD centre (panel drawing), either sign
LCD_DY = 2.95                      # LCD centre from the board centre (model)
EAR_X = (77.0, 82.5)               # ear strip, |x|
EAR_Y0 = 53.5                      # ears run from |y| 53.5 to 62.08
STEP_NAME = "Waveshare_7inch_HDMI_LCD_C.step"

# ---- module ----
FIT = 0.4                          # clearance round the screen outline
WINDOW = (160.0, 94.0)             # bezel opening: shows the active area even 2.9 mm (x) or 4 mm (y) off centre
BODY_W, BODY_H = 214.0, 130.0
Z0 = EAR_T                         # body front face
FACE_T = 2.4                       # bezel thickness
ZF = Z0 + FACE_T                   # glass front face rests here
FLANGE_D = 30.0                    # top and bottom flanges, depth behind the front face
WALL = 2.4                         # corner locating walls
WALL_Y0 = 50.0                     # corner walls run from |y| 50 to the flanges (connectors stop at |y| 44)
FOAM = 1.0                         # foam tape between the clips and the ears
ZC = ZF + BOARD_BACK + FOAM        # clip underside
CLIP_T = 3.0
CLIP_X, CLIP_Y = (76.0, 96.0), (52.5, 61.5)   # clip bar (+x, +y corner), mirrored
BOSS = (90.0, 57.0)                # clip screw / boss centre
BOSS_D = 9.0
POST_D = 7.5                       # rack-ear posts, depth behind the front face (insert 6 deep + 1.5)
M3_INS_D, M3_INS_DEPTH = 4.0, 6.0


def body():
    hw, hh = BODY_W / 2, BODY_H / 2
    sx_in, sy_in = SCR_W / 2 + FIT, SCR_H / 2 + FIT
    b = box(-hw, hw, -hh, hh, Z0, ZF)                              # bezel
    b = b.cut(cq.Workplane("XY").rect(*WINDOW).extrude(FACE_T + 2).edges("|Z").fillet(2.0).translate((0, 0, Z0 - 1)))
    # top and bottom flanges: stiffen the bezel and stop the ears; zip-tie slots for the cables
    for sy in (1, -1):
        y0, y1 = sorted((sy * sy_in, sy * hh))
        b = b.union(box(-hw + 7, hw - 7, y0, y1, Z0, Z0 + FLANGE_D))
    # corner walls locate the ears sideways; the middle of each side stays open for the plugs
    for sx in (1, -1):
        x0, x1 = sorted((sx * sx_in, sx * (sx_in + WALL)))
        for sy in (1, -1):
            y0, y1 = sorted((sy * WALL_Y0, sy * sy_in))
            b = b.union(box(x0, x1, y0, y1, ZF, ZF + BOARD_BACK))
    # clip bosses
    for sx in (1, -1):
        for sy in (1, -1):
            b = b.union(cyl_z(sx * BOSS[0], sy * BOSS[1], ZF, ZC, BOSS_D))
    # ear posts with M3 inserts (same positions as the B1 dock), kept short so the plugs pass behind them
    for sx in (1, -1):
        x0, x1 = sorted((sx * (EAR_SCREW_X - 6), sx * hw))
        for sy in (1, -1):
            y0, y1 = sorted((sy * (EAR_SCREW_Y - 8), sy * (EAR_SCREW_Y + 8)))
            b = b.union(box(x0, x1, y0, y1, Z0, Z0 + POST_D))
    for x in (-90, -70, 70, 90):
        for sy in (1, -1):
            yc = sy * (hh - (hh - sy_in) / 2)
            b = b.cut(box(x - 5, x + 5, yc - 3, yc + 3, Z0 + 18.5, Z0 + 21.5))
    # holes: ear inserts, clip inserts
    for sx in (1, -1):
        for sy in (1, -1):
            b = b.cut(cyl_z(sx * EAR_SCREW_X, sy * EAR_SCREW_Y, Z0 - 0.1, Z0 + INSERT_DEPTH, INSERT_D))
            b = b.cut(cyl_z(sx * BOSS[0], sy * BOSS[1], ZC - M3_INS_DEPTH, ZC + 0.1, M3_INS_D))
    return b


def clip():
    """corner clip, in place at the (+x, +y) corner: a bar over the ear, one M3 screw into the boss"""
    c = box(CLIP_X[0], CLIP_X[1], CLIP_Y[0], CLIP_Y[1], ZC, ZC + CLIP_T).edges("|Z").fillet(1.5)
    return c.cut(cyl_z(BOSS[0], BOSS[1], ZC - 1, ZC + CLIP_T + 1, 3.4))


def clips():
    c = clip()
    return [c, c.mirror("YZ"), c.mirror("XZ"), c.mirror("YZ").mirror("XZ")]


def _step_path():
    here = os.path.dirname(os.path.abspath(__file__))
    for d in ("../Component_Models", ".", "../../Display7C_3U_screen-module_2026-10-27/Component_Models",
              "../../3_Display_7in_3U/Component_Models"):
        p = os.path.normpath(os.path.join(here, d, STEP_NAME))
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f"{STEP_NAME} not found next to the source or in ../Component_Models")


_SCREEN = None


def screen_dummy(flip=False):
    """Waveshare's model, face-down on the bezel. flip=True turns it 180 deg (connectors on the other side)."""
    global _SCREEN
    if _SCREEN is None:
        m = cq.Workplane().add(cq.importers.importStep(_step_path()).val())
        _SCREEN = m.rotate((0, 0, 0), (1, 0, 0), 90).translate((0, 0, ZF + 3.4))   # model y (depth) -> z, front at ZF
    return _SCREEN.rotate((0, 0, 0), (0, 0, 1), 180) if flip else _SCREEN


def plugs(flip=False):
    """space the cable plugs need: a flat HDMI plug (20 x 9, 27 mm out of the socket) with its cable folded back,
    and a micro-USB plug (11 x 8, 20 mm out). Sockets as in the model: HDMI centre y 36.4, z ZF+11.05;
    micro-USB centre y 17.15, z ZF+9.4, both on the -x edge (x = -83.5)."""
    zh, zu = ZF + 11.05, ZF + 9.4
    p = [box(-83.5 - 27, -83.5, 36.4 - 10, 36.4 + 10, zh - 4.5, zh + 4.5),
         box(-83.5 - 27, -83.5 - 21, 36.4 - 7, 36.4 + 7, zh + 4.5, zh + 40),          # flat cable turning back
         box(-83.3 - 20, -83.3, 17.15 - 5.5, 17.15 + 5.5, zu - 4, zu + 4)]
    if flip:
        p = [s.rotate((0, 0, 0), (0, 0, 1), 180) for s in p]
    return p


# names the rack scripts (units.display_parts) use
def glass_dummy():
    """the whole screen (glass, board and connectors), for the rack's collision checks"""
    return screen_dummy()


def driver_dummy():
    """this screen has its driver on its back, so this is the space the HDMI and USB plugs need"""
    p = plugs()
    return p[0].union(p[1]).union(p[2])


if __name__ == "__main__":
    for n, s in (("body", body()), ("clip", clip())):
        v = s.val(); bb = v.BoundingBox()
        print(n, v.isValid(), len(s.solids().vals()), round(v.Volume()),
              [round(a, 1) for a in (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax)])
    bb = screen_dummy().val().BoundingBox()
    print("screen", [round(a, 2) for a in (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax)])
