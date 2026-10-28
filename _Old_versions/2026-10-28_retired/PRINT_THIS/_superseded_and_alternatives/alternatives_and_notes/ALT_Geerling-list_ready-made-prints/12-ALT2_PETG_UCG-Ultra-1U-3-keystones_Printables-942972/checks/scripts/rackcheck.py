"""Rack fit of the Printables 942972 UCG-Ultra mount (cleaned mesh) in the T0-look 9U rack.
Usage: python -I rackcheck.py <rack source dir> <clean_local.stl> <out txt> <render dir>"""
import sys, os
SRC, MOUNT, OUTTXT, RDIR = sys.argv[1:5]
sys.path.insert(0, SRC)
import numpy as np, trimesh, cadquery as cq
import rack_t0 as r
import units as un

YB3 = r.module_bottoms()[3]
lines, fails = [], 0
def check(name, ok, detail=""):
    global fails
    lines.append(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}"); fails += (not ok)
def warn(name, detail): lines.append(f"WARN  {name}  {detail}")
def info(name, detail): lines.append(f"INFO  {name}  {detail}")

def to_mesh(wp, tol=0.05):
    vs, fs = [], []
    for s in wp.solids().vals():
        v, f = s.tessellate(tol, 0.2)
        off = sum(len(x) for x in vs)
        vs.append(np.array([(p.x, p.y, p.z) for p in v])); fs.append(np.array(f) + off)
    m = trimesh.Trimesh(np.vstack(vs), np.vstack(fs), process=True)
    trimesh.repair.fix_normals(m)
    return m

def inter(a, b):
    A, B = a.bounds, b.bounds
    if np.any(A[1] < B[0]) or np.any(B[1] < A[0]):
        return 0.0
    try:
        i = trimesh.boolean.intersection([a, b], engine="manifold")
        return float(i.volume) if len(i.faces) else 0.0
    except Exception as e:
        return -1.0

# mount: local (x across, y up, z 0 = tray back .. 136 = panel front) -> rack (turn 180 deg about y)
local = trimesh.load(MOUNT, force="mesh")
M = np.eye(4); M[0, 0] = -1; M[2, 2] = -1; M[:3, 3] = (127.0, YB3, 133.0)
mount = local.copy().apply_transform(M)
b = mount.bounds
info("mount placed", f"x {b[0][0]:.1f}..{b[1][0]:.1f}, y {b[0][1]:.2f}..{b[1][1]:.2f}, z {b[0][2]:.1f}..{b[1][2]:.1f} "
     f"(1U slot {YB3:.2f}..{YB3 + r.U:.2f}; panel 3 mm in front of the rails, tray {b[1][2]:.0f} mm deep)")
check("cleaned mount is one watertight solid (keystone receptacles fused into the panel)", local.is_watertight and len(local.split()) == 1,
      f"(volume {local.volume / 1000:.1f} cm3)")

# ear slots vs the rail inserts (from the panel section 1.5 mm behind the front face)
sec = local.section(plane_origin=[0, 0, 134.5], plane_normal=[0, 0, 1])
p, _ = sec.to_2D(to_2D=np.eye(4))
slots = []
for poly in p.polygons_full:
    for h in poly.interiors:
        x, y = np.array(h.xy)
        w, hh = x.max() - x.min(), y.max() - y.min()
        if 10 < w < 14 and 6 < hh < 8:
            slots.append((127.0 - (x.min() + x.max()) / 2, YB3 + (y.min() + y.max()) / 2, w, hh))
want = [(sx * r.HOLE_X, YB3 + e) for sx in (1, -1) for e in (6.35, 38.1)]
ok = len(slots) == 4
worst = 0.0
for wx, wy in want:
    s = min(slots, key=lambda s: abs(s[0] - wx) + abs(s[1] - wy))
    dx, dy = abs(s[0] - wx), abs(s[1] - wy)
    worst = max(worst, dx, dy)
    ok &= dx <= s[2] / 2 - 2.75 and dy <= s[3] / 2 - 2.75       # an M5 (5.5 clearance) still passes
check("4 ear slots sit on the rail inserts (EIA 6.35 / 38.1, 236.525 apart) and pass an M5", ok,
      f"(slots {slots[0][2]:.1f} x {slots[0][3]:.1f}; worst offset {worst:.2f} mm)")

# rack and neighbours
P = {k: to_mesh(v) for k, v in r.assembly().items()}
D = {k: to_mesh(v) for k, v in un.display_parts().items()}
hits = sorted(((inter(mount, m), k) for k, m in {**P, **D}.items()), reverse=True)
check("no collision with the rack parts or the screen module below", hits[0][0] < 0.01 and hits[0][0] >= 0,
      f"(worst {hits[0][0]:.3f} mm3 with {hits[0][1]})")

def gap(direction, parts):
    """how far the mount can move (mm, +1 up / -1 down) before touching any of parts"""
    lo, hi = 0.0, 3.0
    if any(inter(mount, m) > 0.001 for m in parts.values()):
        return 0.0
    for _ in range(12):
        mid = (lo + hi) / 2
        t = mount.copy(); t.apply_translation((0, direction * mid, 0))
        if any(inter(t, m) > 0.001 for m in parts.values()):
            hi = mid
        else:
            lo = mid
    return lo
caps = {k: v for k, v in P.items() if "cap" in k.lower()}
g_up = gap(+1, caps)
g_dn = gap(-1, D)
g_up_any = gap(+1, P)
msg = (f"{g_up:.2f} mm to the cap, {g_up_any:.2f} mm to any rack part above (the downloaded panel is a full 44.45 mm; "
       f"1U panels are normally 43.65 so they don't rub)")
if g_up >= 0.3:
    check("air between the mount's top and the cap", True, f"({msg})")
else:
    warn("air between the mount's top and the cap", msg)
check("air between the mount's floor and the screen module below", g_dn >= 0.2, f"({g_dn:.2f} mm)")

# UCG-Ultra in the tray: front face against the panel back (z = 0), on the 3 mm floor, centred between the walls
GW = (141.8, 127.6, 30.0)
# tray inner walls from a section across the tray
loc, ri, _ = local.ray.intersects_location(np.array([[140.0, 20.0, 60.0]] * 2), np.array([[-1.0, 0, 0], [1.0, 0, 0]]))
inner_l, inner_r = loc[ri == 0][:, 0].max(), loc[ri == 1][:, 0].min()   # local x of the two inner wall faces
xc_local = (inner_l + inner_r) / 2
xc = 127.0 - xc_local
floor_top = YB3 + 3.0
gw = (cq.Workplane("XY").box(GW[0], GW[2], GW[1], centered=(True, False, False))
      .edges("|Y").fillet(8.0).edges(">Y").fillet(4.0).edges("<Y").fillet(2.0).translate((xc, floor_top + 0.02, 0.02)))
gwm = to_mesh(gw)
info("tray", f"inner width {inner_r - inner_l:.1f} mm for the 141.8 mm gateway ({(inner_r - inner_l - GW[0]) / 2:.2f} mm each side), "
     f"gateway centre {xc:+.1f} mm from the rack centre line")
check("UCG-Ultra (141.8 x 127.6 x 30) fits: no collision with the mount", inter(gwm, mount) < 0.01)
held = []
for nm, d in (("side walls", (1.0, 0, 0)), ("side walls", (-1.0, 0, 0)), ("floor", (0, -0.1, 0)), ("panel / frame", (0, 0, -0.1))):
    t = gwm.copy(); t.apply_translation(d); held.append(inter(t, mount) > 0.05)
rear = None
for dz in np.arange(0.2, 6.01, 0.2):
    t = gwm.copy(); t.apply_translation((0, 0, dz))
    if inter(t, mount) > 0.05:
        rear = dz; break
check("gateway is located: floor, panel, both side walls, rear stop", all(held) and rear is not None,
      f"(slides back {rear - 0.2 if rear else float('nan'):.1f} mm to the rear stop)")
# display window vs the gateway's face
win = [h for poly in p.polygons_full for h in poly.interiors]
wb = None
for h in win:
    x, y = np.array(h.xy)
    if 20 < x.max() - x.min() < 30 and 10 < y.max() - y.min() < 15:
        wb = (127.0 - x.max(), 127.0 - x.min(), YB3 + y.min(), YB3 + y.max())
if wb:
    info("display window", f"{wb[1] - wb[0]:.1f} x {wb[3] - wb[2]:.1f} mm, centre {((wb[0] + wb[1]) / 2 - xc):+.1f} mm across and "
         f"{((wb[2] + wb[3]) / 2 - (floor_top + GW[2] / 2)):+.1f} mm up from the centre of the gateway's front face")
# rear ports: open space behind the gateway's back face (RJ45 jacks sit roughly mid-height; USB-C at one end)
zb = GW[1] + 0.02
hit, _, _ = local.ray.intersects_location(np.array([[xc_local, 50.0, 1.5]]), np.array([[0, -1.0, 0]]))
lip_top = hit[:, 1].max() - 3.0                                   # lip height above the floor top
hl, ri, _ = local.ray.intersects_location(np.array([[xc_local, 25.0, 1.5]] * 2), np.array([[-1.0, 0, 0], [1.0, 0, 0]]))
post_l, post_r = hl[ri == 0][:, 0].max(), hl[ri == 1][:, 0].min()  # inner edges of the rear corner posts (local x)
cover_r = (xc_local + GW[0] / 2) - post_r                           # local +x = right as seen from the front
cover_l = post_l - (xc_local - GW[0] / 2)
zone_full = trimesh.creation.box(extents=(GW[0] - 8, GW[2] - 8, 40)); zone_full.apply_translation((xc, floor_top + GW[2] / 2, zb + 20.5))
v = inter(zone_full, mount)
warn("rear ports", f"a 3 mm lip runs across the back, {lip_top:.1f} mm above the floor and {rear - 0.2 if rear else 0:.1f} mm behind "
     f"the gateway, and two full-height corner posts cover the last {cover_r:.1f} mm (right, seen from the front) and {cover_l:.1f} mm "
     f"(left) of its back. Check with the real gateway that the RJ45 and USB-C plugs clear them (the asymmetry and the "
     f"raised display window suggest the designer modelled the real ports)") if v > 0.01 else \
    check("rear ports: nothing behind the gateway's back face", True)
check("rack depth: tray ends well before the rear posts, cables have room", b[1][2] < 188 - 40, f"(tray ends {b[1][2]:.0f} mm behind the rails; rear posts at 188)")
lines.append("")
lines.append(f"{sum(l.startswith('PASS') for l in lines)} PASS, {fails} FAIL, {sum(l.startswith('WARN') for l in lines)} WARN")
os.makedirs(os.path.dirname(OUTTXT), exist_ok=True)
head = ["Printables 942972 UCG-Ultra 10-inch 1U mount (3 keystones) in the T0-look 9U rack: checks (27 Oct 2026)",
        "Calculations on the downloaded mesh and the rack CAD, not a physical test. Rack frame: x across, y up, z back from the rails.", ""]
open(OUTTXT, "w").write("\n".join(head + lines) + "\n")
print("\n".join(head + lines))
mount.export(os.path.join(RDIR, "ucg_option2_rack.stl"))
gwm.export(os.path.join(RDIR, "ucg_ultra_in_option2_rack.stl"))
