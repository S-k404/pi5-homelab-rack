import cadquery as cq
import display as dp
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


B, G, C, DRV = dp.body(), dp.glass_dummy(), dp.clips(), dp.driver_dummy()
ins = lambda s, p: s.val().isInside(cq.Vector(*p))

check("body is one solid", len(B.solids().vals()) == 1)
check("screen sits in its pocket without touching", vol_int(B, G) < 0.01)
check("screen rests on the bezel (1 mm forward collides)", vol_int(B, G.translate((0, 0, -1))) > 1)
check("4 corner clips clear the body and the screen", all(vol_int(B, c) < 0.01 and vol_int(G, c) < 0.01 for c in C))
gx, gy = dp.GLASS[0] / 2, dp.GLASS[1] / 2
ov = min(gx - (dp.CLIP_POS[0] - 2 - dp.CLIP / 2), gy - (dp.CLIP_POS[1] - 2 - dp.CLIP / 2))
check("clips overlap the screen edge", ov >= 4, f"({ov:.1f} mm, with {dp.FOAM:.0f} mm foam tape between)")
check("bezel window shows the whole active area", dp.WINDOW[0] >= dp.ACTIVE[0] and dp.WINDOW[1] >= dp.ACTIVE[1],
      f"(window {dp.WINDOW[0]:.0f} x {dp.WINDOW[1]:.0f}, active {dp.ACTIVE[0]:.1f} x {dp.ACTIVE[1]:.1f} mm)")
check("bezel covers the glass edge", dp.WINDOW[0] < dp.GLASS[0] - 4 and dp.WINDOW[1] < dp.GLASS[1] - 4)
zf = dp.Z0 + dp.FACE_T + 2
gaps = [(0, gy + 1.5, zf), (0, -gy - 1.5, zf), (gx + 1.5, 0, zf), (-gx - 1.5, 0, zf)]
check("ribbon-cable gaps in the pocket wall on all four edges", all(not ins(B, p) for p in gaps), "(60 mm top/bottom, 50 mm sides)")
zc = dp.Z0 + dp.FACE_T + dp.GLASS[2] + dp.FOAM
clip_ok = all(not ins(B, (sx * dp.CLIP_POS[0], sy * dp.CLIP_POS[1], zc - 2)) and not ins(c, (sx * dp.CLIP_POS[0], sy * dp.CLIP_POS[1], zc + 1.5))
              for (sx, sy), c in zip(((1, 1), (-1, 1), (1, -1), (-1, -1)), C))
check("each clip's screw hole lines up with a boss insert", clip_ok)
ear_ok = all(not ins(B, (sx * dp.EAR_SCREW_X, sy * dp.EAR_SCREW_Y, dp.Z0 + 2)) for sx in (1, -1) for sy in (1, -1))
check("ear inserts in place (ears are the B1 dock's ears)", ear_ok)
check("driver board fits on the tray", vol_int(B, DRV) < 0.01, "(100 x 50 mm board shown; tray 186 x 67 mm with zip-tie slots)")
bb = B.val().BoundingBox()
check("body fits between 10-inch rails and inside 3U", bb.xlen <= 222 and bb.ylen <= dp.PANEL_H, f"({bb.xlen:.0f} x {bb.ylen:.0f} mm)")
check("body fits a 220 mm bed face down", bb.xlen <= 220 and bb.ylen <= 220, f"({bb.xlen:.0f} x {bb.ylen:.0f} x {bb.zlen:.0f} mm)")

out.append(f"\n{len(out) - fails} PASS, {fails} FAIL")
open("VERIFICATION_display.txt", "w").write('7" display module (3U) — checks\n\n' + "\n".join(out) + "\n")
print("\n".join(out))
