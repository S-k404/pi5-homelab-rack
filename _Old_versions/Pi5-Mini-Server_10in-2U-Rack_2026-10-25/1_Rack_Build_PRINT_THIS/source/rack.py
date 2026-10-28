"""
10-inch, 2U rack conversion for the v3 Pi 5 + UPS case (freestanding-ready).

Frame = v3 frame: x left->right as seen from v3's PORT side, y from port side (-) to
button side (+), z up. In the rack the PORT side faces the REAR; the faceplate sits on
v3's button side (+y).

Prints (each one solid):
  Rack_Faceplate_2U_10in      254 x 88.1 x 4   (needs a >=256 mm bed)
  Rack_Faceplate_Left/Right   two halves for 220 mm beds; each screws to the shelf
  Rack_Shelf                  base: foot sockets, faceplate posts, UGREEN HDMI port tower
Also patches v3's board tray with a cable exit for the UGREEN micro-HDMI extender.
"""
import os
import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "rack_out")
os.makedirs(OUT, exist_ok=True)


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def cyl_y(x, y0, y1, z, d):
    return cq.Workplane("XZ").center(x, z).circle(d / 2).extrude(-(y1 - y0)).translate((0, y0, 0))


def rounded_slot_y(xc, zc, w, h, y0, y1, r=None):
    """through-cut along y, rounded rectangle w (x) by h (z); default r = full stadium"""
    r = (min(w, h) / 2 - 0.01) if r is None else r
    return (cq.Workplane("XZ").center(xc, zc).rect(w, h).extrude(-(y1 - y0))
            .edges("|Y").fillet(r).translate((0, y0, 0)))


# ---- v3 geometry (from case_v3.py) ---------------------------------------
W, IW = 2.2, 113.9
CASE_X0, CASE_X1 = -W, IW + W          # -2.2 .. 116.1
CASE_Y0 = -W                           # port face (rack rear)
CASE_Y1 = 110.0 + W                    # board tray / lid back face (rack front) = 112.2
CASE_ZBOT = -5.0                       # underside of the v3 feet
FEET = [(9, 9), (IW - 9, 9), (9, 87.0 - 9), (IW - 9, 87.0 - 9)]   # r 5
BTN_X, BTN_Z = 56.9 + 18.4, 41.9 + 3.04                            # Pi power-button tube
DCIN_X, DCIN_Z = (80.0, 112.0), (5.0, 29.0)                         # UPS tray back window
V3_BACK_VENT_X = list(range(84, 106, 5)) + list(range(8, 37, 5))  # from case_v3.py
BACK_VENTS_Z = (36.9 + 9, 36.9 + 21)

# ---- rack standard (EIA-310 dims applied to a 10" panel) -------------------
U = 44.45
PANEL_W, PANEL_H, PANEL_T = 254.0, 2 * U - 0.8, 4.0     # 254 x 88.1
HOLE_PITCH = 236.525                                     # rail hole spacing
EAR_SLOT = (10.0, 6.5)                                   # M6 slot w x h
EAR_Z = (6.35, 2 * U - 6.35)                             # from panel bottom

GAP = 0.3
SOCKET = 1.5                        # foot socket depth
SHELF_T = 4.5
Z0 = -8.0                           # desk level = panel bottom
SHELF_TOP = Z0 + SHELF_T            # -3.5; feet sit in sockets whose floor is z=-5
CX = (CASE_X0 + CASE_X1) / 2        # 56.95 centre line
PX0, PX1 = CX - PANEL_W / 2, CX + PANEL_W / 2
PY0 = CASE_Y1 + GAP                 # faceplate rear face
PY1 = PY0 + PANEL_T

# ---- shelf --------------------------------------------------------------
SH_X0, SH_X1 = -46.0, CASE_X1 + 8.0
SH_Y0, SH_Y1 = CASE_Y0 - 2.0, PY0
POST_X = [(CASE_X0 - 8.0, CASE_X0 - 2.0), (CASE_X1 + 2.0, CASE_X1 + 8.0)]
POST_Y = (PY0 - 8.0, PY0)
POST_Z1 = 60.0
LIP_Z1 = 2.0                        # front lip top, below the DC-IN window (z 5)
M3_INSERT = 4.0
FP_SCREWS = [(sum(POST_X[0]) / 2, 12.0), (sum(POST_X[0]) / 2, 50.0),
             (sum(POST_X[1]) / 2, 12.0), (sum(POST_X[1]) / 2, 50.0),
             (30.0, -3.0), (85.0, -3.0)]

# ---- UGREEN 20134 HDMI-female end: port tower left of the case ---------
# Socket flush with the case's rear port face, same height as the adapter's HDMI.
HF_W, HF_H, HF_L, HC = 23.0, 12.0, 38.0, 0.3        # measure yours and edit
TW_WALL = 1.6
AIR_GAP = 10.0                                      # open air channel between tower and case wall
TW_X1 = CASE_X0 - AIR_GAP                           # tower right outer face (-12.2)
CAV_X1 = TW_X1 - TW_WALL                            # cavity right (-4.6)
CAV_X0 = CAV_X1 - (HF_W + 2 * HC)                   # cavity left (-28.2)
TW_X0 = CAV_X0 - TW_WALL                            # tower left outer face (-29.8)
HDMI_ZC = 47.6                                      # socket centre height (adapter HDMI ~47.1)
CAV_Z0 = HDMI_ZC - (HF_H / 2 + HC)                  # 41.3
CAV_Z1 = HDMI_ZC + (HF_H / 2 + HC)                  # 53.9
TW_Y0 = CASE_Y0                                     # flush with the port face (-2.2)
LIP_T = 1.5
HOUSING_Y0 = TW_Y0 + LIP_T                          # socket face (-0.7)
CHAMBER_Y0 = HOUSING_Y0 + HF_L + HC                 # end of housing (37.6)
TW_Y1 = 56.0                                        # rear wall outer face
LIP_OPEN = (20.6, 9.6)                              # front opening (plug overmold passes)


def ugreen_end_routed():
    """UGREEN HDMI end in the tower, cable turning 90 deg into the case exit (v3 frame)."""
    x0, y0, z0 = ugreen_origin()
    housing = box(x0 - HF_W, x0, y0, y0 + HF_L, z0, z0 + HF_H)
    sock = box(x0 - HF_W / 2 - 7, x0 - HF_W / 2 + 7, y0 - 0.01, y0 + 6, HDMI_ZC - 2.25, HDMI_ZC + 2.25)
    yc, zc = y0 + HF_L + 7.0, HDMI_ZC + 2.0
    stub = cq.Workplane("XZ").center(x0 - HF_W / 2, HDMI_ZC).circle(2.4).extrude(-(yc - (y0 + HF_L))).translate((0, y0 + HF_L, 0))
    elbow = cq.Workplane("XY").sphere(2.4).translate((x0 - HF_W / 2, yc, HDMI_ZC))
    rise = box(x0 - HF_W / 2 - 2.4, x0 - HF_W / 2 + 2.4, yc - 2.4, yc + 2.4, HDMI_ZC, zc)
    run = cq.Workplane("YZ").center(yc, zc).circle(2.4).extrude(-1.0 - (x0 - HF_W / 2)).translate((x0 - HF_W / 2, 0, 0))
    return housing.cut(sock).union(stub).union(elbow).union(rise).union(run).val()


def ugreen_origin():
    """placement of the UGREEN end model: local x->+y, local y->-x, local z->z"""
    return (CAV_X1 - HC, HOUSING_Y0, CAV_Z0 + HC)


# ---- cable exit in the v3 board tray left wall ------------------------------
EXIT_Y, EXIT_Z = (38.0, 50.0), (47.0, 57.0)


def faceplate(x_lo=PX0, x_hi=PX1):
    p = box(PX0, PX1, PY0, PY1, Z0, Z0 + PANEL_H).edges("|Y").fillet(2.0)
    # M6 ear slots
    for xs in (CX - HOLE_PITCH / 2, CX + HOLE_PITCH / 2):
        for zs in EAR_Z:
            p = p.cut(rounded_slot_y(xs, Z0 + zs, EAR_SLOT[0], EAR_SLOT[1], PY0 - 1, PY1 + 1))
    # Pi power button (press through to the v3 tube)
    p = p.cut(cyl_y(BTN_X, PY0 - 1, PY1 + 1, BTN_Z, 8.0))
    p = p.cut(cyl_y(BTN_X, PY1 - 1.0, PY1 + 1, BTN_Z, 11.0))     # finger dish
    # UPS DC-IN access window (plug reaches the recessed jack)
    p = p.cut(rounded_slot_y(sum(DCIN_X) / 2, sum(DCIN_Z) / 2, DCIN_X[1] - DCIN_X[0] + 4, DCIN_Z[1] - DCIN_Z[0] + 4, PY0 - 1, PY1 + 1, r=4.0))
    # vent slots exactly in line with every v3 back-wall vent slot (2 mm slots -> 3 mm here)
    for vx in V3_BACK_VENT_X:
        p = p.cut(rounded_slot_y(vx, sum(BACK_VENTS_Z) / 2, 3.0, BACK_VENTS_Z[1] - BACK_VENTS_Z[0] + 2.0,
                                 PY0 - 1, PY1 + 1))
    # side-panel vent slots in the empty panel areas (decor + airflow)
    for xa, xb in ((PX0 + 20, CASE_X0 - 14), (CASE_X1 + 14, PX1 - 20)):
        for k in range(7):
            z = Z0 + 18 + k * 8
            p = p.cut(rounded_slot_y((xa + xb) / 2, z, xb - xa, 3.0, PY0 - 1, PY1 + 1))
    # countersunk M3 screws into the shelf
    for sx, sz in FP_SCREWS:
        p = p.cut(cyl_y(sx, PY0 - 1, PY1 + 1, sz, 3.4))
        p = p.cut(cq.Workplane("XZ").center(sx, sz).circle(3.4)
                  .workplane(offset=-1.8).circle(1.7).loft().translate((0, PY1 + 0.001, 0)))
    if (x_lo, x_hi) != (PX0, PX1):
        p = p.intersect(box(x_lo, x_hi, PY0 - 1, PY1 + 1, Z0 - 1, Z0 + PANEL_H + 1))
    return p


def ugreen_tower():
    t = box(TW_X0, TW_X1, TW_Y0, TW_Y1, SHELF_TOP, CAV_Z1 + 1.0)
    # hollow column below the cavity floor (2 mm floor slab bridges 23.6 mm)
    t = t.cut(box(TW_X0 + TW_WALL, TW_X1 - TW_WALL, TW_Y0 + TW_WALL, TW_Y1 - TW_WALL,
                  SHELF_TOP + 2.0, CAV_Z0 - 2.0))
    # side windows in the hollow base (air + less plastic), 45-degree tops so they print
    for xa, xb in ((TW_X0 - 0.1, TW_X0 + TW_WALL + 0.1), (TW_X1 - TW_WALL - 0.1, TW_X1 + 0.1)):
        win = (cq.Workplane("YZ").polyline([(4.0, SHELF_TOP + 4), (TW_Y1 - 6, SHELF_TOP + 4),
                                            (TW_Y1 - 6, CAV_Z0 - 14), (TW_Y1 - 16, CAV_Z0 - 4),
                                            (14.0, CAV_Z0 - 4), (4.0, CAV_Z0 - 14)]).close()
               .extrude(xb - xa).translate((xa, 0, 0)))
        t = t.cut(win)
    # housing cavity + cable chamber, open at the top for snap-in
    t = t.cut(box(CAV_X0, CAV_X1, HOUSING_Y0, TW_Y1 - TW_WALL, CAV_Z0, CAV_Z1 + 1.1))
    # front lip with the plug opening
    xc = (CAV_X0 + CAV_X1) / 2
    t = t.cut(box(xc - LIP_OPEN[0] / 2, xc + LIP_OPEN[0] / 2, TW_Y0 - 0.1, HOUSING_Y0 + 0.1,
                  HDMI_ZC - LIP_OPEN[1] / 2, HDMI_ZC + LIP_OPEN[1] / 2).edges("|Y").fillet(1.5))
    # snap lips along the top edges of the housing section
    for xl in (CAV_X0, CAV_X1 - 1.0):
        t = t.union(box(xl, xl + 1.0, HOUSING_Y0 + 4, CHAMBER_Y0 - 4, CAV_Z1, CAV_Z1 + 1.0))
    # cable window in the right wall, facing the case's cable exit
    t = t.cut(box(CAV_X1 - 0.1, TW_X1 + 0.1, CHAMBER_Y0, TW_Y1 - TW_WALL, CAV_Z0, CAV_Z1 + 1.1))
    return t


def shelf():
    s = box(SH_X0, SH_X1, SH_Y0, SH_Y1, Z0, Z0 + SHELF_T).edges("|Z").fillet(3.0)
    # sockets for the v3 feet (r5 -> r5.4, 1.5 deep)
    for fx, fy in FEET:
        s = s.cut(cq.Workplane("XY").circle(5.4).extrude(SOCKET + 0.1).translate((fx, fy, CASE_ZBOT)))
    # rear stop (port side) and side guides
    s = s.union(box(10, 104, SH_Y0, CASE_Y0 - GAP, SHELF_TOP, SHELF_TOP + 3))
    for xa, xb in ((CASE_X0 - 4 - GAP, CASE_X0 - GAP), (CASE_X1 + GAP, CASE_X1 + GAP + 4)):
        s = s.union(box(xa, xb, 15, 75, SHELF_TOP, SHELF_TOP + 4))
    # front lip (behind the faceplate, below the DC-IN window) and posts
    s = s.union(box(SH_X0 + 30, SH_X1, POST_Y[0], POST_Y[1], Z0, LIP_Z1))
    for xa, xb in POST_X:
        s = s.union(box(xa, xb, POST_Y[0], POST_Y[1], Z0, POST_Z1))
        # triangular gusset back along the shelf
        g = (cq.Workplane("YZ").polyline([(POST_Y[0], Z0 + SHELF_T), (POST_Y[0] - 30, Z0 + SHELF_T),
                                          (POST_Y[0], POST_Z1 - 10)]).close().extrude(xb - xa)
             .translate((xa, 0, 0)))
        s = s.union(g)
    # heat-set insert holes (M3, horizontal, from the faceplate side)
    for sx, sz in FP_SCREWS:
        s = s.cut(cyl_y(sx, PY0 - 6.0, PY0 + 0.1, sz, M3_INSERT))
    # vents under v3's side-channel floor slots (x 104.2, y 14..80)
    # one slot between the feet sockets (feet at y 9 and y 78, socket r 5.4)
    s = s.cut(box(101.0, 107.5, 16.0, 71.0, Z0 - 0.1, SHELF_TOP + 0.1).edges("|Z").fillet(3.0))
    # UGREEN HDMI port tower beside the case (socket in line with the other rear ports)
    s = s.union(ugreen_tower())
    # weight-saving slots in the open area left of the case
    for k in range(3):                      # clear of the HDMI tower (ends y 56)
        y = 62 + k * 12
        s = s.cut(box(SH_X0 + 8, CASE_X0 - 10, y, y + 6, Z0 - 0.1, Z0 + SHELF_T + 0.1).edges("|Z").fillet(2.9))
    # rubber-foot recesses
    for fx, fy in ((SH_X0 + 10, SH_Y0 + 10), (SH_X1 - 10, SH_Y0 + 10), (SH_X1 - 10, SH_Y1 - 18), (SH_X0 + 10, SH_Y1 - 18)):
        s = s.cut(cq.Workplane("XY").circle(5.0).extrude(1.0).translate((fx, fy, Z0 - 0.01)))
    return s


def patched_board_tray(path):
    bt = cq.importers.importStep(path).val()
    cut = (cq.Workplane("YZ").center(sum(EXIT_Y) / 2, sum(EXIT_Z) / 2)
           .rect(EXIT_Y[1] - EXIT_Y[0], EXIT_Z[1] - EXIT_Z[0]).extrude(W + 2.0)
           .edges("|X").fillet(3.0).translate((-W - 1.0, 0, 0)))
    return bt.cut(cut.val())


def export(solid, name, stl=True):
    cq.exporters.export(cq.Workplane().add(solid), os.path.join(OUT, name + ".step"))
    if stl:
        cq.exporters.export(cq.Workplane().add(solid), os.path.join(OUT, name + ".stl"),
                            tolerance=0.02, angularTolerance=0.1)


if __name__ == "__main__":
    fp = faceplate().val()
    fl = faceplate(PX0, CX).val()
    fr = faceplate(CX, PX1).val()
    sh = shelf().val()
    bt = patched_board_tray(os.path.join(HERE, "Pi5_UPS_v3_board_tray.step"))
    for nm, s in [("Rack_Faceplate_2U_10in", fp), ("Rack_Faceplate_Left", fl),
                  ("Rack_Faceplate_Right", fr), ("Rack_Shelf", sh),
                  ("Pi5_UPS_v3_board_tray_HDMIexit", bt)]:
        assert len(s.Solids()) == 1, (nm, len(s.Solids()))
        export(s, nm)
        b = s.BoundingBox()
        print(f"{nm:34s} {b.xlen:6.1f} x {b.ylen:6.1f} x {b.zlen:6.1f}  valid={s.isValid()}")
