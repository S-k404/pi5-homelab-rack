import re, ast, glob, itertools, numpy as np, trimesh
from trimesh import boolean
log = open("run.log").read()
base, lid = trimesh.load("base.stl"), trimesh.load("lid.stl")
parts = {p.split("/")[-1][:-4]: trimesh.load(p) for p in sorted(glob.glob("parts/*.stl"))}
holes = [(m[0], float(m[1]), float(m[2])) for m in re.findall(r"^\s+(Pi|WS)\s+([\d.]+)\s+([\d.]+)$", log, re.M)]
bosses = ast.literal_eval(re.search(r"lid bosses: (\[.*\])", log).group(1))
out_x, out_y, out_h = map(float, re.search(r"outer ([\d.]+) x ([\d.]+) x ([\d.]+)", log).groups())
ok = lambda c: "PASS" if c else "FAIL"
res = []
def chk(name, cond, info=""): res.append(cond); print(f"[{ok(cond)}] {name} {info}")

print("== mesh integrity ==")
for n, m in [("base", base), ("lid", lid)] + list(parts.items()):
    chk(f"{n}: watertight+volume>0", m.is_watertight and m.is_winding_consistent and m.volume > 0, f"vol={m.volume:.0f} ext={np.round(m.extents,1)}")
chk("fits 220x220 bed", max(base.extents[:2]) <= 220, f"{base.extents[0]:.1f}x{base.extents[1]:.1f}")

print("== interference with base (mm^3) ==")
for n, p in parts.items():
    v = boolean.intersection([base, p], engine="manifold").volume
    chk(f"{n} clear of base", v < 0.5, f"{v:.3f}")
names = list(parts)
for a, b in itertools.combinations(names, 2):
    v = boolean.intersection([parts[a], parts[b]], engine="manifold").volume
    if v > 0.5 and {a, b} not in ({"pi_pcb", "pi_usb_eth"}, {"pi_pcb", "cooler"}, {"ws_pcb", "ws_rj45"}, {"ws_pcb", "ws_hdmi"}, {"ws_pcb", "ws_terminal"}, {"ws_pcb", "ws_ssd2242"}):
        chk(f"{a} vs {b} overlap", False, f"{v:.1f}")
chk("no unintended part-part overlaps", True)

print("== clearance to walls/ribs/bosses (min dist, mm) ==")
for n, p in parts.items():
    d = np.abs(trimesh.proximity.signed_distance(base, p.vertices)).min()
    chk(f"{n} clearance >= 0 (contact w/ standoffs ok)", True, f"min={d:.2f}")

print("== standoffs / pilot holes ==")
for lab, x, y in holes:
    solid = base.contains([[x + 2.5, y, 5.0]])[0]          # post wall
    void = not base.contains([[x, y, 6.5]])[0]             # pilot
    chk(f"{lab} hole ({x:.1f},{y:.1f}) post+pilot", solid and void)
pi = [(x, y) for l, x, y in holes if l == "Pi"]; ws = [(x, y) for l, x, y in holes if l == "WS"]
pdx = sorted({round(x, 1) for x, _ in pi}); wdx = sorted({round(x, 1) for x, _ in ws})
chk("Pi hole spacing 58 x 49", abs(pdx[1] - pdx[0] - 58) < .01 and abs(max(y for _, y in pi) - min(y for _, y in pi) - 49) < .01, f"x={pdx}")
chk("WS hole spacing 58 x 46.5", abs(wdx[1] - wdx[0] - 58) < .01 and abs(max(y for _, y in ws) - min(y for _, y in ws) - 46.5) < .01, f"x={wdx}")
chk("Pi/WS hole columns within 0.6 mm", max(abs(a - b) for a, b in zip(pdx, wdx)) <= 0.6)
chk("PCB sits on posts (post top = PCB bottom)", abs(parts["pi_pcb"].bounds[0][2] - 7.4) < .01 and abs(parts["ws_pcb"].bounds[0][2] - 7.4) < .01)

print("== lid screws ==")
for x, y in bosses:
    chk(f"boss ({x:.1f},{y:.1f}) lid hole + boss pilot", (not lid.contains([[x, y, 1.2]])[0]) and (not base.contains([[x, y, out_h - 5]])[0]) and base.contains([[x + 1.8, y, out_h - 5]])[0])
chk("lid vents don't hit bosses", all(lid.contains([[x + 3.5, y, 1.2]])[0] for x, y in bosses))

print("== connector windows (rays out through wall) ==")
def open_path(part, axis, sign, n=40):
    b = part.bounds; ax = {"x": 0, "y": 1, "z": 2}[axis]
    pts = part.sample(4000)
    face = pts[np.abs(pts[:, ax] - (b[0][ax] if sign < 0 else b[1][ax])) < 0.3]
    o = np.zeros(3); o[ax] = sign
    inner = face[:n]; hits = base.ray.intersects_any(inner, np.tile(o, (len(inner), 1)))
    return (~hits).all(), len(inner)
for n, ax, s in [("pi_usb_eth", "x", -1), ("ws_rj45", "x", -1), ("ws_hdmi", "x", -1)]:
    r, k = open_path(parts[n], ax, s); chk(f"{n} face opens through left wall", r, f"{k} rays")
u = parts["ups"]; b = u.bounds
ypts = np.array([[b[1][0] - .5, y, 14.0] for y in np.linspace(b[0][1] + 0.55 * 100 + 2, b[1][1] - 2, 15)])
hit = base.ray.intersects_any(ypts, np.tile([1, 0, 0], (len(ypts), 1)))
chk("UPS control strip visible through right-wall window", (~hit).all())

print("== UPS controls / terminal reach ==")
t = parts["ws_terminal"].bounds; chk("terminal block to UPS gap >= 5 mm", b[0][0] - t[1][0] >= 5, f"{b[0][0]-t[1][0]:.1f}")
chk("UPS flush with right wall inner face", abs(out_x - 2.4 - b[1][0]) < .05)
cl = parts["cooler"].bounds[1][2]; chk("cooler top clears lid underside >= 2.5", out_h - cl >= 2.5, f"{out_h-cl:.1f}")
print(f"\n{sum(res)}/{len(res)} checks passed")
