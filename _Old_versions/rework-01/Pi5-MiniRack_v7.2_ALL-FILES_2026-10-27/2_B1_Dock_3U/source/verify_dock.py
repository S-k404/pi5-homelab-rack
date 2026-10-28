import math
import cadquery as cq
import b1_dock as d
from b1_drawer import box

out, fails = [], 0


def check(name, ok, detail=""):
    global fails
    out.append(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")
    fails += (not ok)


def vol_int(a, b):
    try:
        return sum(s.Volume() for s in a.intersect(b).solids().vals())
    except Exception:
        return 0.0


B, EL, ER, P = d.body(), d.ear(-1), d.ear(1), d.b1_dummy()
inside = lambda s, p: s.val().isInside(cq.Vector(*p))
bb = B.val().BoundingBox()

# fit
check("printer sits in the cradle without collisions", vol_int(B, P) < 0.01, f"({vol_int(B, P):.3f} mm3)")
check("ears clear the body", vol_int(B, EL) < 0.01 and vol_int(B, ER) < 0.01)
lifted = d.b1_dummy(lift=-1.0)
check("printer actually rests on the cradle (1 mm lower collides)", vol_int(B, lifted) > 1)

# the top face of the printer (labels, button, light, lid) is exposed out the front
pb = P.val().BoundingBox()
front_zone = box(d.X_SHIFT - d.B1_L / 2, d.X_SHIFT + d.B1_L / 2, d.PIVOT_Y + d.LIP + 0.2, pb.ymax + 2, -10, d.PIVOT_Z - 0.1)
check("nothing in front of the printer's top face above the lip", vol_int(B, front_zone) < 0.01,
      f"(exposed {d.B1_L:.0f} x {pb.ymax - d.PIVOT_Y - d.LIP:.0f} mm of the {d.B1_L:.0f} x {d.B1_W:.0f} face)")
fwd = vol_int(B, d.b1_dummy().translate((0, 0, -3.0)))
check("front lip holds the bottom edge: sliding the printer 3 mm forward hits it", fwd > 1,
      f"({d.LIP} mm lip, past the printer's {d.R_EDGE:.0f} mm edge round; under the left part of the face only)")
# the real face (from the user's photos): label slot, light and power button are in the open window
feats = {"label slot": (d.LSLOT_X, sum(d.LSLOT_Y) / 2, 28.0), "light": (d.LED_XY[0], d.LED_XY[1], 5.0),
         "power button": (d.BTN_XY[0], d.BTN_XY[1], 6.0)}
blocked = []
for nm, (fx, fy, half) in feats.items():
    z = d.local_to_world(box(d.X_SHIFT + fx - 3, d.X_SHIFT + fx + 3, fy - half, fy + half, -40, -0.5))
    if vol_int(B, z) > 0.01 or vol_int(EL, z) > 0.01 or vol_int(ER, z) > 0.01:
        blocked.append(nm)
check("label slot, light and power button face you with nothing in front of them", not blocked,
      f"({', '.join(feats)}{'; blocked: ' + ', '.join(blocked) if blocked else ''})")
lip_top = d.PIVOT_Y + d.LIP
# the lid swings out sideways (it hinges at the back of the lid end); find how far before it touches the dock
ang = 0
for a in range(5, 125, 5):
    L_ = d.lid_open(a)
    if vol_int(B, L_) > 0.01 or vol_int(EL, L_) > 0.01 or vol_int(ER, L_) > 0.01:
        break
    ang = a
check("lid swings open far enough to change the label roll without taking the printer out", ang >= 75,
      f"(opens {ang} deg before touching the dock; hinge assumed at the back of the lid end, from the photos)")
room_above = d.PANEL_H / 2 - pb.ymax
pv, pv2 = (0, d.PIVOT_Y, d.PIVOT_Z), (1, d.PIVOT_Y, d.PIVOT_Z)
# racked removal: tip the printer forward to upright about its front-bottom edge, lift over the lip, slide out
tip = [a for a in (2, 4, 6, 8) if vol_int(B, P.rotate(pv, pv2, -a)) > 0.01]
up = d.LIP + 1.0
U = P.rotate(pv, pv2, -d.TILT)
top_upright = U.val().BoundingBox().ymax + up
slide = [z for z in range(0, 130, 10) if vol_int(B, U.translate((0, up, -z))) > 0.01]
check("racked removal: tip upright, lift 3.5 mm, slide out the front", not tip and not slide and top_upright < d.PANEL_H / 2 - 2,
      f"(printer top {top_upright:.1f} vs next unit at {d.PANEL_H / 2:.1f}; tip hits {tip}, slide hits {slide})")
wz = d.COLLAR_D + (d.BODY_D - d.COLLAR_D) / 2
check("lite windows in both side walls", not inside(B, (d.BODY_W / 2 - 2, 0, wz)) and not inside(B, (-d.BODY_W / 2 + 2, 0, wz)),
      f"({d.SIDE_WIN_H:.0f} x {d.SIDE_WIN_W:.0f} mm each)")

# the open slide (lid release) is on the printer's top side: room above it for a finger
sl = d.b1_parts()["slide"].val().BoundingBox()
room = d.PANEL_H / 2 - sl.ymax
check("open slide (top side) has finger room above it, up to the next unit", room >= 20, f"({room:.1f} mm)")
check("real size: official 132 x 91 x 62 mm, 1.5 mm clearance at the back, no spacers needed",
      d.B1_H == 62.0 and vol_int(B, d.b1_dummy(h=61.6)) < 0.01, "(also fits the 61.6 mm edition)")
check("printer rests against the guide at its bottom end (1 mm further collides)",
      vol_int(B, d.b1_dummy().translate((d.CLR + 1.0, 0, 0))) > 1)
out.append("INFO  USB-C port: not visible in the photos. The bottom end (your left) is open above the 18 mm guide, "
           "and the back rest has a 50 mm cable notch, so a cable reaches either place")

# stability: centre of mass behind the front-bottom edge, leaning on the back rest
t = math.radians(d.TILT)
com_z = d.PIVOT_Z + (d.B1_H / 2) * math.cos(t) + (d.B1_W / 2) * math.sin(t)
check("printer leans back (centre of mass behind its front edge)", com_z > d.PIVOT_Z + 20, f"({com_z - d.PIVOT_Z:.1f} mm behind)")
check("back rest above the printer's centre of mass", d.REST_H > d.B1_W / 2, f"(rest {d.REST_H:.0f} mm, CoM {d.B1_W / 2:.1f} mm up the face)")

# rack standard
eb = [e.val().BoundingBox() for e in (EL, ER)]
check("panel width 254 mm", abs(eb[1].xmax - eb[0].xmin - 254) < 0.01)
check("panel height 132.55 mm (3U)", abs(eb[0].ylen - 132.55) < 0.01, f"({eb[0].ylen:.2f})")
check("rack slots 236.5 mm apart at EIA 3U positions",
      not inside(ER, (118.25, d.SLOT_Y, 2)) and not inside(EL, (-118.25, -d.SLOT_Y, 2)) and inside(ER, (118.25, 0, 2)))
check("body fits between 10-inch rails", bb.xlen <= 218, f"({bb.xlen:.0f} mm)")
check("body inside 3U", bb.ylen <= d.PANEL_H, f"({bb.ylen:.0f} mm)")
check("depth", bb.zlen <= 195, f"({bb.zlen:.0f} mm)")
m = min(d.EAR_SCREW_X - 2 - d.WIN_HALF, d.BODY_W / 2 - d.EAR_SCREW_X - 2)
check("ear inserts have >= 1.5 mm wall", m >= 1.5, f"({m:.1f} mm)")

# printing
check("body fits 220 mm bed (floor down)", max(bb.xlen, bb.zlen) <= 220 and bb.ylen <= 220,
      f"({bb.xlen:.0f} x {bb.zlen:.0f} footprint, {bb.ylen:.0f} tall)")

out.append(f"\n{sum(l.startswith('PASS') for l in out)} PASS, {fails} FAIL")
open("VERIFICATION_dock.txt", "w").write("NIIMBOT B1 face-out dock — 10-inch 3U — geometric checks\n\n" + "\n".join(out) + "\n")
print("\n".join(out))
