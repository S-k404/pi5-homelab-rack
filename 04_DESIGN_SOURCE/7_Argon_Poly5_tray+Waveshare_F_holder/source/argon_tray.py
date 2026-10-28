"""
Alternative top tray for the Pi 5 2U unit: holds a Pi 5 that lives in a ready-made Argon case
(NEO 5 or Poly+5) instead of the bare-board v3 board tray + lid.

The tray has the v3 board tray's footprint and its three joint holes, so it drops onto the same UPS tray with
the same 3 x M3 x 12 countersunk screws. The shelf, UPS tray and faceplate are unchanged.

Frame = v3 frame (as pi_rack.py): x left->right seen from the port side, y from the port side (rack REAR, -)
towards the faceplate (rack FRONT, +), z up.

The case sits in the rear-right corner (the datum): its USB/Ethernet end faces the rack rear like the v3 ports did,
and its side ports (USB-C power, 2 x micro-HDMI) face left into an open area for the plugs. The front fence and
left stubs sit at the largest published size, so foam tape takes up the slack on a smaller case.

Run: python argon_tray.py <out folder>     (writes STEP in the v3 frame and STL laid out for printing)
"""
import os
import sys
import cadquery as cq

# ---- v3 geometry (from case_v3.py) ---------------------------------------
W, IW, UD = 2.2, 113.9, 110.0
X0, X1, Y0, Y1 = -W, IW + W, -W, UD + W          # tray outline = board tray outline
PLENUM_TOP, UF = 34.5, 2.4
ZS = PLENUM_TOP + UF                              # 36.9 floor top
R_OUT = 3.0
JOINTS = [(107.7, 40.0), (14.0, 84.5), (75.0, 84.5)]   # M3 countersunk, tray -> UPS tray posts

# ---- cases ------------------------------------------------------------------
# nominal = the size most listings give; max = largest published figure (+0.5 clearance is added below)
CASES = {
    "NEO5": dict(title="ARGON NEO 5", nominal=(94.0, 70.0, 30.0), max=(95.5, 71.5, 30.0),
                 sources="94 x 70 x 30 (Tom's Hardware, Electrokit); 87.6 x 71.5 x 30 (Core, Little Bird); "
                         "93 x 68 x 27 (Botland); 95.5 x 71.5 x 30 (rcdrone)"),
    "POLY5": dict(title="ARGON POLY+5", nominal=(93.5, 64.0, 30.0), max=(95.5, 66.0, 30.0),
                  sources="93.5 x 64 x 30 (several seller listings, 'allow 0-1 cm measuring error'); no official figure"),
}
CLR = 0.5                 # clearance on the max size
FENCE_H = 10.0            # right fence
FRONT_H = 6.0             # front fence (lower, so the microSD end stays easy to grip)
STUB_H = 10.0             # left stubs
REAR_H, REAR_W = 5.0, 2.5  # rear corner returns: low and narrow, clear of the port plugs
RIM_H = 5.0               # stiffening rim round the free edges
T = 2.2                   # fence / rim thickness
X_DATUM = IW              # right fence inner face (case GPIO side)
Y_DATUM = 0.0             # rear returns' inner face (case port end)
STUB_REAR = (0.0, 28.0)   # left stub spans (y): clear of the HDMI plugs (y ~42..68) and USB-C (y ~70..83)
STUB_FRONT_LEN = 10.0
LEAD_HOLE = (20.0, 100.0, 12.0, 8.0)   # 12 V lead up from the overhang (cx, cy, w, h)
TIES = [(8.0, 104.0), (32.0, 104.0)]   # cable-tie anchors for the 12 V -> 5 V USB-C converter


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def pocket(key):
    """case footprint at its max size + clearance, pushed into the datum corner"""
    L, Wc, H = CASES[key]["max"]
    return X_DATUM - (Wc + CLR), X_DATUM, Y_DATUM, Y_DATUM + L + CLR


def case_dummy(key, size="max", lift=1.0):
    """the case as a plain box in the datum corner; lift = foam tape under it"""
    L, Wc, H = CASES[key][size]
    return box(X_DATUM - Wc, X_DATUM, Y_DATUM, Y_DATUM + L, ZS + lift, ZS + lift + H)


def tie(cx, cy):
    b = box(cx - 4, cx + 4, cy - 3, cy + 3, ZS, ZS + 4.5)
    return b.cut(box(cx - 1.75, cx + 1.75, cy - 4, cy + 4, ZS - 0.1, ZS + 2.0))


def tray(key):
    px0, px1, py0, py1 = pocket(key)
    t = box(X0, X1, Y0, Y1, PLENUM_TOP, ZS).edges("|Z").fillet(R_OUT)
    # right fence (full length, past the front fence) and rear-right return
    t = t.union(box(X_DATUM, X1, Y0, py1 + T, ZS, ZS + FENCE_H))
    t = t.union(box(X_DATUM - REAR_W, X_DATUM, Y0, Y_DATUM, ZS, ZS + REAR_H))
    # front fence across the case end, joined to the right fence
    t = t.union(box(px0 - T, X1, py1, py1 + T, ZS, ZS + FRONT_H))
    # left stubs (outside the case's port side, between the plugs) and the rear-left return
    t = t.union(box(px0 - T, px0, STUB_REAR[0], STUB_REAR[1], ZS, ZS + STUB_H))
    t = t.union(box(px0 - T, px0, py1 - STUB_FRONT_LEN, py1, ZS, ZS + STUB_H))
    t = t.union(box(px0 - T, px0 + REAR_W, Y0, Y_DATUM, ZS, ZS + REAR_H))
    # stiffening rim round the free edges: left edge, front edge, rear edge left of the case
    t = t.union(box(X0, X0 + T, Y0, Y1, ZS, ZS + RIM_H))
    t = t.union(box(X0, X1, Y1 - T, Y1, ZS, ZS + RIM_H))
    t = t.union(box(X0, px0 - T - 14.0, Y0, Y0 + T, ZS, ZS + RIM_H))     # 14 mm gap: a cable can leave at the rear
    # cable-tie anchors for the 12 V -> 5 V USB-C converter (front-left)
    for cx, cy in TIES:
        t = t.union(tie(cx, cy))
    # joint holes: M3 countersunk from the top, as the v3 board tray
    for jx, jy in JOINTS:
        t = t.cut(cq.Workplane("XY").circle(1.7).extrude(UF + 1).translate((jx, jy, PLENUM_TOP - 0.5)))
        t = t.cut(cq.Workplane().add(cq.Solid.makeCone(1.6, 3.15, 1.66, cq.Vector(jx, jy, ZS - 1.65))))
    # 12 V lead hole (from the overhang, under the front-left of the tray)
    cx, cy, w, h = LEAD_HOLE
    t = t.cut(cq.Workplane("XY").rect(w, h).extrude(UF + 2).edges("|Z").fillet(2.0)
              .translate((cx, cy, PLENUM_TOP - 1)))
    # floor vents in the free left area (the UPS plenum breathes up through them; not under the case)
    for vx in range(6, int(px0 - T - 3), 5):
        t = t.cut(cq.Workplane("XY").slot2D(44.0, 2.4, 90).extrude(UF + 2).translate((vx, 40.0, PLENUM_TOP - 1)))
    # label on the front strip
    txt = (cq.Workplane("XY").text(CASES[key]["title"], 5.0, -0.6, kind="bold", halign="center", valign="center")
           .translate(((px0 + X_DATUM) / 2, (py1 + T + Y1 - T) / 2, ZS)))
    t = t.cut(txt)
    return t


def to_bed(shape):
    bb = shape.val().BoundingBox()
    return shape.translate((-bb.xmin, -bb.ymin, -bb.zmin))


NAMES = {"NEO5": "Pi5_ArgonNEO5_tray", "POLY5": "Pi5_ArgonPoly5_tray"}

if __name__ == "__main__":
    OUT = sys.argv[1]
    for sub in ("STL_for_printing", "STEP_for_Onshape"):
        os.makedirs(os.path.join(OUT, sub), exist_ok=True)
    for key, nm in NAMES.items():
        t = tray(key)
        assert len(t.solids().vals()) == 1, (key, len(t.solids().vals()))
        cq.exporters.export(t, os.path.join(OUT, "STEP_for_Onshape", nm + ".step"))
        cq.exporters.export(to_bed(t), os.path.join(OUT, "STL_for_printing", nm + ".stl"), tolerance=0.02, angularTolerance=0.1)
        b = t.val().BoundingBox()
        print(f"{nm:24s} {b.xlen:6.1f} x {b.ylen:6.1f} x {b.zlen:5.1f}  pocket {pocket(key)}  valid={t.val().isValid()}")
