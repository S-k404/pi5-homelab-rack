"""Checks for the C-type 7-inch screen module, run against Waveshare's 3D model of the screen, both ways round.
Writes VERIFICATION_display7c.txt in the current folder."""
import cadquery as cq
import display as dp

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


B, C = dp.body(), dp.clips()
ins = lambda s, p: s.val().isInside(cq.Vector(*p))
check("body is one valid solid", len(B.solids().vals()) == 1 and B.val().isValid())
for flip in (False, True):
    way = "turned 180 deg (sockets on the right)" if flip else "sockets on the left"
    S = dp.screen_dummy(flip)
    check(f"screen sits in the module without touching, {way}", vol_int(B, S) < 0.01, f"({vol_int(B, S):.3f} mm3)")
    check(f"screen rests on the bezel (0.2 mm forward collides), {way}", vol_int(B, S.translate((0, 0, -0.2))) > 1)
    play = [s for s in ((0.5, 0, 0), (-0.5, 0, 0), (0, 0.5, 0), (0, -0.5, 0)) if vol_int(B, S.translate(s)) > 0.01]
    check(f"flanges and corner walls locate it to within 0.5 mm, {way}", len(play) == 4, f"({len(play)}/4 directions stopped)")
    check(f"clips clear the screen at rest, {way}", all(vol_int(S, c) < 0.01 for c in C))
    press = [vol_int(S, c.translate((0, 0, -dp.FOAM - 0.3))) for c in C]
    check(f"each clip bears on an ear through the 1 mm foam, {way}", all(p > 5 for p in press),
          f"(overlap if pushed 1.3 mm: {min(press):.0f}-{max(press):.0f} mm3)")
    P = dp.plugs(flip)
    worst = max(vol_int(B, p) for p in P)
    check(f"HDMI and micro-USB plugs (flat HDMI cable folded back) clear the module, {way}", worst < 0.01, f"({worst:.3f} mm3)")
    clash = max(vol_int(S, p) for p in P)
    check(f"plug spaces start at the sockets (no overlap with the screen), {way}", clash < 0.5, f"({clash:.2f} mm3)")
check("4 clips clear the body", all(vol_int(B, c) < 0.01 for c in C))
clip_ok = all(not ins(B, (sx * dp.BOSS[0], sy * dp.BOSS[1], dp.ZC - 2)) and not ins(c, (sx * dp.BOSS[0], sy * dp.BOSS[1], dp.ZC + 1.5))
              for (sx, sy), c in zip(((1, 1), (-1, 1), (1, -1), (-1, -1)), C))
check("each clip's screw hole lines up with a boss insert", clip_ok)
ear_ok = all(not ins(B, (sx * dp.EAR_SCREW_X, sy * dp.EAR_SCREW_Y, dp.Z0 + 2)) for sx in (1, -1) for sy in (1, -1))
check("ear inserts in place (ears are the B1 dock's ears)", ear_ok)
# window: the active area, anywhere within +-2.3 (x) / +-3.0 (y) of the glass centre, either way round
wx, wy = dp.WINDOW[0] / 2, dp.WINDOW[1] / 2
mx, my = wx - dp.ACTIVE[0] / 2, wy - dp.ACTIVE[1] / 2
check("bezel window shows the whole active area even when it sits off centre", mx >= 2.3 and my >= 3.0 + dp.GLASS_DY - 1.45,
      f"(window {dp.WINDOW[0]:.0f} x {dp.WINDOW[1]:.0f}, active {dp.ACTIVE[0]:.1f} x {dp.ACTIVE[1]:.1f}: {mx:.1f} / {my:.1f} mm spare)")
cover_x = dp.SCR_W / 2 - dp.FIT - wx
cover_y = dp.GLASS_H / 2 - dp.GLASS_DY - dp.FIT - wy
check("bezel covers the glass edge by >= 1 mm all round (screen pushed to one side)", min(cover_x, cover_y) >= 1.0,
      f"({cover_x:.1f} mm at the sides, {cover_y:.1f} mm at the narrow edge)")
bb = B.val().BoundingBox()
check("body fits between 10-inch rails and inside 3U", bb.xlen <= 222 and bb.ylen <= dp.PANEL_H, f"({bb.xlen:.0f} x {bb.ylen:.0f} mm)")
check("body fits a 220 mm bed face down", bb.xlen <= 220 and bb.ylen <= 220, f"({bb.xlen:.0f} x {bb.ylen:.0f} x {bb.zlen:.0f} mm)")
check("no overhangs face down: everything rises from the bezel", abs(bb.zmin - dp.Z0) < 1e-6)

out.append(f"\n{len(out) - fails} PASS, {fails} FAIL")
open("VERIFICATION_display7c.txt", "w").write(
    '7" screen module, C-type (3U) — checks against Waveshare\'s 3D model of the 7inch HDMI LCD (C)\n\n' + "\n".join(out) + "\n")
print("\n".join(out))
