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
front_zone = box(-d.B1_L / 2, d.B1_L / 2, d.PIVOT_Y + d.LIP + 0.2, pb.ymax + 2, -10, d.PIVOT_Z - 0.1)
check("nothing in front of the printer's top face above the lip", vol_int(B, front_zone) < 0.01,
      f"(exposed {d.B1_L:.0f} x {pb.ymax - d.PIVOT_Y - d.LIP:.0f} mm of the {d.B1_L:.0f} x {d.B1_W:.0f} face)")
check("front lip holds the bottom edge", d.LIP >= 2, f"({d.LIP} mm)")
lip_top = d.PIVOT_Y + d.LIP
check("lid can swing out (no frame over the top or sides of the face)",
      d.WIN_HALF > d.B1_L / 2 + 20, f"(window +/-{d.WIN_HALF:.0f}, printer +/-{d.B1_L / 2:.0f})")
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

# finger room each side for the lid's open slide
gap = d.WIN_HALF - (d.B1_L / 2 + d.CLR + d.GUIDE_T)
check("finger room beside the printer (both sides)", gap >= 20, f"({gap:.1f} mm each side, guides only {d.GUIDE_H:.0f} mm tall)")

# a 62 mm thick B1 with the two clip-in spacers
P62 = d.b1_dummy(h=d.B1_H_THIN)
SP = [d.spacer(1), d.spacer(-1)]
worst = max(vol_int(a, b) for a, b in ((B, P62), (B, SP[0]), (B, SP[1]), (P62, SP[0]), (P62, SP[1])))
check("62 mm B1 + spacers: printer, spacers and body don't collide", worst < 0.01, f"(worst {worst:.3f} mm3)")
check("62 mm B1 + spacers: spacers sit on the back rest (1 mm lower collides)",
      all(vol_int(B, s.translate((0, -1.0, 0))) > 1 for s in SP))
gap = (d.B1_H_THIN + d.CLR) - d.B1_H_THIN
check("62 mm B1 + spacers: same 1.5 mm gap behind the printer as a 67 mm B1 without them", abs(gap - d.CLR) < 1e-6,
      f"({gap:.1f} mm; spacer {d.SPACER_T:.0f} mm thick)")
check("62 mm B1 + spacers: printer rests on the cradle", vol_int(B, d.b1_dummy(lift=-1.0, h=d.B1_H_THIN)) > 1)
sb = d.spacer(1, local=True).val().BoundingBox()
check("spacer prints on its side (hook profile on the bed) within a 220 mm bed", max(sb.ylen, sb.zlen) <= 220,
      f"({sb.zlen:.1f} x {sb.ylen:.1f} profile, {sb.xlen:.0f} tall)")

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

out.append(f"\n{len(out) - fails} PASS, {fails} FAIL")
open("VERIFICATION_dock.txt", "w").write("NIIMBOT B1 face-out dock — 10-inch 3U — geometric checks\n\n" + "\n".join(out) + "\n")
print("\n".join(out))
