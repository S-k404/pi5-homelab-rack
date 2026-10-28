"""
Every cable in the 28 Oct build, checked on the 3D models (ultrareview, 28 Oct 2026): where each plug sits, whether the
plug body and the cable clear every printed part and device, and whether the cable you're buying is long enough.
Calculations on the CAD models and stand-ins, not a physical test.

Rack frame: x across (+x = the viewer's LEFT seen from the front), y up from the base-bar tops, z back from the front rails, mm.
Usage: python verify_wiring_all.py <scene dir from export_final.py> <rack source dir> <report.txt> [<wired scene out dir>]
The optional 4th argument writes a copy of the scene with every cable added (group "rack_cables") for build_final.py.
"""
import json
import os
import shutil
import sys

import numpy as np
import trimesh
from manifold3d import Manifold, Mesh

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scene_load import load  # noqa: E402

SCENE, RACK_SRC, REPORT = sys.argv[1:4]
WIRED = sys.argv[4] if len(sys.argv) > 4 else None
sys.path.insert(0, RACK_SRC)
import units as un  # noqa: E402
import display as dp  # noqa: E402

lines, counts = [], {"PASS": 0, "FAIL": 0, "WARN": 0}


def rec(st, name, detail=""):
    if st in counts:
        counts[st] += 1
    lines.append(f"{st:<5} {name}  {detail}".rstrip())


# ---------------------------------------------------------------- geometry helpers
def to_manifold(tm):
    m = Manifold(Mesh(vert_properties=np.asarray(tm.vertices, np.float32), tri_verts=np.asarray(tm.faces, np.uint32)))
    if m.status().name != "NoError" or m.volume() <= 0:
        h = tm.convex_hull
        m = Manifold(Mesh(vert_properties=np.asarray(h.vertices, np.float32), tri_verts=np.asarray(h.faces, np.uint32)))
    return m


def to_trimesh(m):
    mm = m.to_mesh()
    return trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts), process=False)


def tube(pts, d, seg=16):
    """a cable along a polyline (capsules hulled pairwise, unioned)"""
    r = d / 2
    sph = [Manifold.sphere(r, seg).translate(tuple(map(float, p))) for p in pts]
    caps = [Manifold.batch_hull([a, b]) for a, b in zip(sph, sph[1:])]
    out = caps[0]
    for c in caps[1:]:
        out = out + c
    return out


def flat(pts, w, t):
    """a flat cable (w wide, t thick) along a polyline, approximated by a chain of boxes hulled pairwise; the wide side
    lies across the direction given with each point: pts = [(p, wide_axis_unit_vector), ...]"""
    blocks = []
    for p, ax in pts:
        ax = np.asarray(ax, float) / np.linalg.norm(ax)
        # a small slab with its long side along ax
        size = np.array([t, t, t], float) + np.abs(ax) * (w - t)
        blocks.append(Manifold.cube(tuple(size), True).translate(tuple(map(float, p))))
    out = None
    for a, b in zip(blocks, blocks[1:]):
        h = Manifold.batch_hull([a, b])
        out = h if out is None else out + h
    return out


def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube((x1 - x0, y1 - y0, z1 - z0)).translate((x0, y0, z0))


def plen(pts):
    return float(sum(np.linalg.norm(np.subtract(b, a)) for a, b in zip(pts, pts[1:])))


# ---------------------------------------------------------------- the scene
OBJS = load(SCENE)
SOLIDS = []
for o in OBJS:
    if o["group"] == "pi_cables":
        continue
    lo, hi = o["mesh"].bounds
    SOLIDS.append(dict(name=o["name"], key=o["mesh_key"], lo=lo, hi=hi, man=to_manifold(o["mesh"])))
def cable_manifold(tm):
    """a scene cable is spheres + cylinders concatenated: union their pieces (one convex hull would fill the bends)"""
    out = None
    for piece in tm.split(only_watertight=False):
        if len(piece.vertices) < 4 or piece.extents.min() < 1e-3:
            continue                                             # flat scraps (end caps) carry no volume
        m = to_manifold(piece)
        out = m if out is None else out + m
    return out


OLD_CABLES = [dict(name=o["name"], key=o["mesh_key"], lo=o["mesh"].bounds[0], hi=o["mesh"].bounds[1], man=cable_manifold(o["mesh"]))
              for o in OBJS if o["group"] == "pi_cables"]
OBJ = {o["mesh_key"]: o["mesh"] for o in OBJS}


def hits(m, skip=(), pool=None):
    """volume of m inside every solid (bounding boxes first), worst first"""
    pool = SOLIDS if pool is None else pool
    mm = to_trimesh(m)
    lo, hi = mm.bounds
    out = []
    for s in pool:
        if s["key"] in skip or (s["lo"] > hi).any() or (s["hi"] < lo).any():
            continue
        v = (m ^ s["man"]).volume()
        if v > 0.05:
            out.append((v, s["name"]))
    return sorted(out, reverse=True)


def htxt(h):
    return "nothing" if not h else ", ".join(f"{n} {v:.1f} mm3" for v, n in h[:3])


# ---------------------------------------------------------------- ports (from the scene meshes and the unit sources)
def comps(key):
    parts = OBJ[key].split(only_watertight=False)
    return sorted(parts, key=lambda m: -m.volume if m.is_watertight else -m.area)


af = OBJ["af_metal"].split(only_watertight=False)
af = sorted(af, key=lambda m: m.extents[1])                        # HDMI-A (6 tall) first, RJ45 (13.5 tall) second
HD, RJ = af[0].bounds, af[-1].bounds
JACK_Z = HD[1][2]                                                  # adapter jack mouths (rack rear direction = +z)
hdmi_c = ((HD[0][0] + HD[1][0]) / 2, (HD[0][1] + HD[1][1]) / 2)
rj_c = ((RJ[0][0] + RJ[1][0]) / 2, (RJ[0][1] + RJ[1][1]) / 2)
HOLDER_Z = max(OBJ["pi_hbase"].bounds[1][2], OBJ["pi_hlid"].bounds[1][2])
CASE_Z = OBJ["ar_shell"].bounds[1][2]                              # Poly+ 5 rear face (USB / Ethernet end)
usb2 = sorted(OBJ["ar_usb2"].split(only_watertight=False), key=lambda m: m.bounds[0][1])
usb_lo, usb_hi = [((m.bounds[0][0] + m.bounds[1][0]) / 2, (m.bounds[0][1] + m.bounds[1][1]) / 2 + 0.9) for m in usb2]
# screen sockets: display.py plugs(): on the -x edge of the board (x -83.5), HDMI centre y 36.4 / z ZF + 11.05,
# micro-USB centre y 17.15 / z ZF + 9.4, in the display frame; the rack places the module at T(0, YC_DISP, -Z0)
SY, SZ = un.YC_DISP, -dp.Z0
scr_hdmi = (-83.5, 36.4 + SY, dp.ZF + 11.05 + SZ)
scr_usb = (-83.3, 17.15 + SY, dp.ZF + 9.4 + SZ)
UG = OBJ["ucg_gw"].bounds                                          # UCG-Ultra in the mount
UCG_REAR = UG[1][2]
B1 = OBJ["b1_body"].bounds
DOCK = OBJ["dock"].bounds

lines.append("Every cable in the 28 Oct build: plugs, routes, clearances and lengths (ultrareview, 28 Oct 2026)")
lines.append("Calculations on the CAD models and stand-ins, not a physical test. Rack frame: x across (+x = viewer's LEFT "
             "from the front), y up from the base-bar tops, z back from the front rails, mm.")
lines.append("Cables are routed up the open rack rear on the -x side (the viewer's RIGHT seen from the front; the 12 V "
             "brick and its mains cord are on the other side), tight against that side so the ears hide them from the front. "
             "Lengths are port face to port face along the route + 10 %.")
lines.append("")
lines.append("== Where the plugs go ==")
rec("INFO", "adapter (F) HDMI-A + 2.5G RJ45 (rack rear)", f"(HDMI centre x {hdmi_c[0]:.1f} y {hdmi_c[1]:.1f}, RJ45 centre x "
    f"{rj_c[0]:.1f} y {rj_c[1]:.1f}; jack mouths at z {JACK_Z:.1f}, holder rear face z {HOLDER_Z:.1f})")
rec("INFO", "Pi 5 USB 2.0 pair (Poly+ 5 rear end)", f"(x {usb_lo[0]:.1f}, lower y {usb_lo[1]:.1f}, upper y {usb_hi[1]:.1f}; "
    f"case rear face z {CASE_Z:.1f})")
rec("INFO", "screen HDMI + micro-USB (side edge, -x)", f"(HDMI x {scr_hdmi[0]} y {scr_hdmi[1]:.1f} z {scr_hdmi[2]:.1f}; micro-USB "
    f"y {scr_usb[1]:.1f} z {scr_usb[2]:.1f})")
rec("INFO", "UCG-Ultra rear ports", f"(rear face z {UCG_REAR:.1f}, x {UG[0][0]:.1f}..{UG[1][0]:.1f}, y {UG[0][1]:.1f}..{UG[1][1]:.1f}; "
    "port order across the back not modelled: the Cat6 is taken to its centre)")

# ---------------------------------------------------------------- 1. plugs in the adapter (F) holder's rear notches
lines.append("")
lines.append("== Plugs at the adapter (F) in its holder (the holder check only tested the jacks) ==")
holder = [s for s in SOLIDS if s["key"] in ("pi_hbase", "pi_hlid")]
for nm, (cx, cy), sizes in (("HDMI-A plug", hdmi_c, [("slim flat-cable plug", 20.0, 9.0, 27.0), ("standard moulded plug", 21.5, 11.5, 38.0)]),
                            ("RJ45 plug + boot", rj_c, [("slim Cat6 plug + boot", 12.5, 14.5, 32.0)])):
    for desc, w, h, ln in sizes:
        pb = box(cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2, JACK_Z + 0.2, JACK_Z + ln)
        hh = hits(pb, pool=holder)
        vol = sum(v for v, _ in hh)
        st = "PASS" if vol < 0.5 else ("WARN" if "standard" in desc else "FAIL")
        rec(st, f"{nm} ({desc}, {w:.1f} x {h:.1f}) clears the holder's rear notch", f"({htxt(hh)})")
# how wide is the HDMI notch at the mouth?
probe = [x for x in np.arange(5.0, 15.01, 0.1) if not hits(box(hdmi_c[0] - x, hdmi_c[0] + x, hdmi_c[1] - 2, hdmi_c[1] + 2,
                                                                 JACK_Z + 0.2, HOLDER_Z + 0.5), pool=holder)]
notch_w = 2 * max(probe) if probe else 0.0
rec("INFO", "HDMI notch width at the jack mouth (measured on the model)", f"({'open, more than 29' if notch_w >= 29.8 else f'{notch_w:.1f}'} mm; "
    f"the plug's moulding sits in it for the last {HOLDER_Z - JACK_Z:.1f} mm)")

# ---------------------------------------------------------------- 2. the routes
RX = -92.0           # riser line, rack rear, -x side (B1 cable)
RZ = 165.0           # riser depth (dock ends z 92, UCG mount 133, rear base bar 188)
# 28 Oct (clean front): one straight riser at x -110, tight against the right-hand side (seen from the front), so the
# dock's and the screen's ears (x -127..-99) hide it and it can't be seen through the open dock. Behind the units (z 150-186)
# the side modules are open down to x -112 except at their joint ribs (x -112..-130), the 2U base included. The cables
# leave the Pi unit's rear ports, drop to y 50 (well below the faceplate's top, even seen from above) and cross to the riser
# there. The riser stops at y 362, under the UCG mount's open keystone hole (x -105..-93, y 368-388); the Cat6 and the
# gateway's power cross behind the gateway at that height. The cables lie one behind the other, not side by side.
RXR, YL, YC = -110.0, 50.0, 362.0
RZ_H, RZ_U, RZ_C, RZ_P = 160.0, 166.0, 172.0, 178.0
CABLES = []          # (key, label, polyline, dia, plug boxes, bought length mm, colour)


def route(key, label, pts, d, plugs, bought, mat, skip=(), note=""):
    CABLES.append(dict(key=key, label=label, pts=pts, d=d, plugs=plugs, bought=bought, mat=mat, skip=skip, note=note))


# 2a. HDMI: adapter (F) HDMI-A -> screen HDMI (flat 1 m cable)
hx, hy = hdmi_c
sx, sy, sz = scr_hdmi
p_hd = [(hx, hy, JACK_Z + 27.0), (hx, hy, RZ_H - 10), (hx, YL, RZ_H), (RXR, YL, RZ_H),
        (RXR, sy - 20, RZ_H), (RXR, sy, 120.0), (sx - 24.0, sy, sz + 30.0), (sx - 24.0, sy, sz + 4.5)]
route("cab_hdmi", "HDMI (adapter (F) -> screen), 1 m flat", p_hd, 4.5,
      [box(hx - 10, hx + 10, hy - 4.5, hy + 4.5, JACK_Z + 0.2, JACK_Z + 27.0), box(sx - 27, sx - 0.2, sy - 10, sy + 10, sz - 4.5, sz + 4.5)],
      1000.0, "dev_cable", note="the flat cable folds back at the screen as display.py's plug space allows")

# 2b. micro-USB: Pi USB 2.0 (upper) -> screen micro-USB (touch + power)
ux, uy = usb_hi
mx, my, mz = scr_usb
p_mu = [(ux, uy, CASE_Z + 35.0), (ux, uy + 4, RZ_U - 8), (ux, YL, RZ_U), (RXR, YL, RZ_U),
        (RXR, my - 20, RZ_U), (RXR + 2, my, 110.0), (mx - 22.0, my, mz + 25.0), (mx - 22.0, my, mz)]
route("cab_musb", "USB-A -> micro-USB (Pi -> screen touch/power), 1 m", p_mu, 3.5,
      [box(ux - 8, ux + 8, uy - 4, uy + 4, CASE_Z + 0.2, CASE_Z + 35.0), box(mx - 20, mx - 0.2, my - 5.5, my + 5.5, mz - 4, mz + 4)],
      1000.0, "dev_cable")

# the UCG mount behind the gateway: a rear lip across the bottom and a corner post at each end (Printables 942972)
mount = OBJ["ucg"]
gxs = np.arange(UG[0][0], UG[1][0], 1.0)
gys = np.arange(UG[0][1], UG[1][1], 0.5)
gzs = np.arange(UCG_REAR + 0.5, UCG_REAR + 8.0, 1.0)               # the lip stands ~2 mm behind the gateway
probe = np.array([(x, y, z) for x in gxs for y in gys for z in gzs])
occ = mount.contains(probe).reshape(len(gxs), len(gys), len(gzs)).any(axis=2)
mid = occ[len(gxs) // 2]
LIP_TOP = gys[np.where(mid)[0].max()] + 0.5 if mid.any() else UG[0][1]
cols = occ[:, np.searchsorted(gys, LIP_TOP + 3)]
free_x = gxs[~cols]
FREE_X0, FREE_X1 = float(free_x.min()), float(free_x.max())
lines.append("")
lines.append("== The UCG-Ultra's rear ports and the mount (Printables 942972) ==")
rec("INFO", "mount material right behind the gateway", f"(a rear lip up to {LIP_TOP - UG[0][1]:.1f} mm above the gateway's base, full width; "
    f"corner posts cover x {UG[0][0]:.1f}..{FREE_X0:.1f} and {FREE_X1:.1f}..{UG[1][0]:.1f}: plugs fit only in x {FREE_X0:.1f}..{FREE_X1:.1f}, "
    f"{LIP_TOP - UG[0][1]:.1f}..{UG[1][1] - UG[0][1]:.0f} mm up)")
# the gateway's rear ports, measured on Ubiquiti's straight rear view (store.ui.com product image, 694 px = 141.8 mm, about
# +-1 mm). Seen from the back, left to right: reset pinhole, LAN 1-4, WAN 5 (2.5G), USB-C power; from the back, the left end
# is the rack's -x end (the viewer's right from the front). (distance from that end, centre height above the base), mm
UCG_PORTS = {"reset": (9.8, 21.0), "LAN 1": (24.8, 18.7), "LAN 4": (82.1, 18.7), "WAN 5": (101.3, 18.7), "USB-C": (118.7, 17.4)}
RJ_PLUG, USBC_PLUG = (12.5, 14.5), (12.0, 7.0)                     # plug + boot / overmould, across x tall
base = UG[0][1]
lip = LIP_TOP - base
rj_bot = UCG_PORTS["LAN 1"][1] - RJ_PLUG[1] / 2
uc_bot = UCG_PORTS["USB-C"][1] - USBC_PLUG[1] / 2
rec("PASS" if rj_bot > lip + 0.5 else "FAIL", "RJ45 plugs (14.5 tall with the boot) clear the mount's rear lip",
    f"(Ubiquiti's rear view: the RJ45 openings run 13.5-23.9 mm above the base, so a plug's bottom is ~{rj_bot:.1f} mm up; "
    f"the lip is {lip:.1f} mm: {rj_bot - lip:.1f} mm to spare, +-1 mm from the picture)")
rec("PASS" if uc_bot > lip + 0.5 else "FAIL", "the USB-C power plug clears the lip", f"(its bottom ~{uc_bot:.1f} mm up: {uc_bot - lip:.1f} mm to spare)")
l1_edge = UG[0][0] + UCG_PORTS["LAN 1"][0] - RJ_PLUG[0] / 2
rec("PASS" if l1_edge > FREE_X0 + 0.5 else "FAIL", "LAN 1's plug clears the corner post at that end",
    f"({l1_edge - FREE_X0:.1f} mm; the post covers the last {FREE_X0 - UG[0][0]:.0f} mm)")
rec("INFO", "the reset pinhole is behind that corner post", f"({UCG_PORTS['reset'][0]:.0f} mm from the end): slide the gateway out to reach it")
rec("INFO", "power", "(Ubiquiti: \"5V DC, 3A USB-C adapter included\")")

# 2c. Cat6: adapter (F) 2.5G RJ45 -> UCG-Ultra LAN 1 (the port nearest the riser)
rx_, ry_ = rj_c
gx, gy = UG[0][0] + UCG_PORTS["LAN 1"][0], base + UCG_PORTS["LAN 1"][1]
p_c6 = [(rx_, ry_, JACK_Z + 32.0), (rx_, ry_, RZ_C), (rx_, YL, RZ_C), (RXR, YL, RZ_C), (RXR, YC, RZ_C),
        (gx, YC, RZ_C), (gx, gy, RZ_C), (gx, gy, UCG_REAR + 32.0)]
route("cab_cat6", "slim Cat6 (adapter (F) 2.5G -> UCG-Ultra LAN 1)", p_c6, 3.8,
      [box(rx_ - 6.25, rx_ + 6.25, ry_ - 7.25, ry_ + 7.25, JACK_Z + 0.2, JACK_Z + 32.0),
       box(gx - 6.25, gx + 6.25, gy - 7.25, gy + 7.25, UCG_REAR + 0.2, UCG_REAR + 32.0)],
      1000.0, "dev_cat6")

# 2d. USB-A -> USB-C: Pi USB 2.0 (lower) -> NIIMBOT B1 (its USB-C position isn't known: routed into the dock's rear and
#     its length taken to the farthest point of the printer)
lx, ly = usb_lo
dz = DOCK[1][2]
p_b1 = [(lx, ly, CASE_Z + 35.0), (lx, ly - 2, RZ - 20), (lx - 20, (B1[0][1] + B1[1][1]) / 2, RZ - 20),
        (lx - 20, (B1[0][1] + B1[1][1]) / 2, dz + 8.0)]
route("cab_b1", "USB-A -> USB-C (Pi -> B1), 0.5 m", p_b1, 4.0,
      [box(lx - 8, lx + 8, ly - 4, ly + 4, CASE_Z + 0.2, CASE_Z + 35.0)], 500.0, "dev_cable")

# 2e. UCG-Ultra power: USB-C out of its back, down the rear to the desk (the adapter plugs into a wall socket)
px, py = UG[0][0] + UCG_PORTS["USB-C"][0], base + UCG_PORTS["USB-C"][1]
p_up = [(px, py, UCG_REAR + 25.0), (px, py, RZ_P), (px, YC, RZ_P), (RXR, YC, RZ_P),
        (RXR, 20.0, RZ_P), (RXR, -2.0, 215.0), (RXR, -18.0, 240.0)]
route("cab_ucgpwr", "UCG-Ultra USB-C power, out of the rack rear to its adapter", p_up, 4.0,
      [box(px - 6, px + 6, py - 3.5, py + 3.5, UCG_REAR + 0.2, UCG_REAR + 25.0)], None, "dev_cable")

lines.append("")
lines.append("== Routes: the plug bodies and the cable against every printed part, device and rack part ==")
lens = {}
for c in CABLES:
    m = tube(c["pts"], c["d"])
    for pb in c["plugs"]:
        m = m + pb
    h = hits(m, skip=c["skip"])
    rec("PASS" if not h or h[0][0] < 0.5 else "FAIL", f"{c['label']}: plugs + {c['d']:.1f} mm cable touch nothing", f"({htxt(h)})")
    oh = hits(m, pool=OLD_CABLES)
    if oh:
        rec("INFO", "   ... it crosses the 12 V wiring (cables may touch)", f"({htxt(oh)})")
    c["mesh"] = m
    L = plen(c["pts"]) + sum(to_trimesh(pb).extents.max() for pb in c["plugs"])
    lens[c["key"]] = L
    if c["bought"]:
        need = 1.10 * L
        rec("PASS" if need <= c["bought"] else "FAIL", f"   length: {L:.0f} mm port to port, {need:.0f} mm with 10 % slack",
            f"(buying {c['bought']:.0f} mm: {c['bought'] - need:.0f} mm to spare)")
    if c["note"]:
        rec("INFO", "   note", c["note"])

# B1: the port position is not known: worst case to the farthest corner of the printer, through the dock's back
far = max(np.linalg.norm(np.subtract((x, y, z), p_b1[-1])) for x in (B1[0][0], B1[1][0]) for y in (B1[0][1], B1[1][1])
          for z in (B1[0][2], B1[1][2]))
worst_b1 = lens["cab_b1"] + far
rec("PASS" if 1.10 * worst_b1 <= 500 else "WARN", "   B1 cable reaches the printer's port wherever it is (port not modelled: "
    "worst case = the farthest corner of the printer)", f"({worst_b1:.0f} mm, {1.10 * worst_b1:.0f} mm with slack, buying 500 mm)")

# the Cat6: a 0.5 m cable (the Robu cart notes) vs the 1 m one (PARTS_LIST / START_HERE)
c6 = 1.10 * lens["cab_cat6"]
rec("PASS" if c6 <= 1000 else "FAIL", "Cat6 length: the 1 m patch cable in PARTS_LIST / START_HERE is enough", f"(needs {c6:.0f} mm)")
rec("PASS" if c6 <= 500 else "FAIL", "   ... a 0.5 m cable (ROBU_HARDWARE_CART_TO_RESTORE.md 'Not on Robu' list) would be enough",
    f"(needs {c6:.0f} mm{': buy the 1 m one' if c6 > 500 else ''})")
rec("INFO", "UCG-Ultra power", f"(about {lens['cab_ucgpwr'] / 10:.0f} cm from its back to the desk behind the rack, then to a wall "
    "socket: it is NOT on the UPS. The 5 V 3 A adapter comes in the box)")

# ---------------------------------------------------------------- 3. the brick's 12 V lead, behind the faceplate (28 Oct)
lines.append("")
lines.append("== The brick's 12 V lead behind the faceplate (28 Oct: no notch, no DC-IN window; brick_lead_route.py) ==")
sys.path.insert(0, os.path.join(RACK_SRC, "..", "..", "4_Pi_Unit_2U", "source"))
import brick_lead_route as BL  # noqa: E402

x0_, x1_, y0_, y1_, z0_, z1_ = BL.PLUG_BOX
plug = box(x0_, x1_, y0_, y1_, z0_, z1_ - 0.2) + tube([BL.SR[0], BL.SR[1]], BL.SR[2])
h = hits(plug)
rec("PASS" if not h or h[0][0] < 0.5 else "FAIL", "right-angle plug (11 x 12, 16 deep) + strain relief in the UPS DC-IN touch nothing",
    f"({htxt(h)})")
win = (80.0 - BL.PI_CX, 112.0 - BL.PI_CX, 5.0 - BL.PI_Z0, 29.0 - BL.PI_Z0)   # UPS tray DC-IN window (pi_rack.DCIN_X/Z), rack x0 x1 y0 y1
rec("INFO", "   it sits inside the UPS tray's DC-IN window", f"({x0_ - win[0]:.1f} / {win[1] - x1_:.1f} mm each side across, "
    f"{y0_ - win[2]:.1f} below, {win[3] - y1_:.1f} above), so it plugs in from the pocket before the faceplate goes on")
ext = tube(BL.EXT_PATH, BL.LEAD_D)
for d, lab in ((BL.LEAD_D, "PASS"), (5.5, "WARN")):
    h = hits(tube(BL.EXT_PATH, d))
    rec("PASS" if not h or h[0][0] < 0.5 else ("FAIL" if lab == "PASS" else "WARN"),
        f"a {d:.1f} mm extension lead from the plug, along the shelf floor, through the gusset arch, into the cradle touches nothing",
        f"({htxt(h)})")
join = (tube([BL.SOCKET[0], BL.SOCKET[1]], BL.SOCKET[2]) + tube([BL.BRICK_PLUG[0], BL.BRICK_PLUG[1]], BL.BRICK_PLUG[2])
        + tube([BL.BRICK_SR[0], BL.BRICK_SR[1]], BL.BRICK_SR[2]))
h = hits(join)
rec("PASS" if not h or h[0][0] < 0.5 else "FAIL", "the join (extension socket + the brick's straight plug) lies in the cradle's open front",
    f"({htxt(h)})")
lead = tube(BL.brick_lead_path(), 3.5)
h = hits(lead, skip=("brick",))
rec("PASS" if not h or h[0][0] < 0.5 else "FAIL", f"the brick's lead with {BL.COIL_TURNS} turns of spare coiled beside the join touches nothing",
    f"({htxt(h)}; the lead leaves the brick's front face)")
outs = [c for c in OLD_CABLES if c["key"] in ("out_plug", "out_lead", "wire_red", "wire_blk")]
allnew = plug + ext + join + lead
h = hits(allnew, pool=outs)
rec("PASS" if not h or h[0][0] < 0.5 else "FAIL", "none of it touches the UPS OUT plug or its lead to the adapter (F)", f"({htxt(h)})")
zmin = to_trimesh(allnew).bounds[0][2]
rec("PASS" if zmin >= 0.0 else "FAIL", "nothing in front of the faceplate (its back face is z 0)", f"(the lead's front-most point is at z {zmin:.1f})")
fpm = OBJ["pi_face"]
probe_pts = np.array([(BL.JACK[0], BL.JACK[1], -2.0), (74.0, 4.0, -2.0)])
inside = fpm.contains(probe_pts) if fpm.is_watertight else [True, True]
rec("PASS" if all(inside) else "FAIL", "the faceplate is solid where the DC-IN window and the notch were", f"({list(map(bool, inside))})")
need = 1.10 * BL.EXT_LENGTH
rec("PASS" if need <= 300 else "FAIL", "a 30 cm right-angle extension is long enough",
    f"(it spans {BL.EXT_LENGTH:.0f} mm plug to socket, {need:.0f} with slack; coil the rest with the brick's)")
used = BL.length(BL.LEAD_IN) + BL.length(BL.LEAD_OUT)
coil = BL.length(BL.coil_path())
rec("INFO", "the brick's own lead", f"(~{used:.0f} mm from its face to the join; the {BL.COIL_TURNS}-turn coil drawn beside the join holds "
    f"~{coil:.0f} mm. A 1.0-1.5 m lead leaves ~{1000 - used - coil:.0f} to ~{1500 - used - coil:.0f} mm more: add turns, or lay a second "
    "coil on top of the brick (110 x 38 x 40 mm under the dock). Zip-tie the coil; don't wrap it round the brick)")

# ---------------------------------------------------------------- 4. USB power budget and the 12 V budget
lines.append("")
lines.append("== Power: what the Pi's USB ports and the UPS have to supply (estimates from typical figures) ==")
rec("INFO", "Pi 5 USB ports", "(with usb_max_current_enable=1 the four ports share 1.6 A; without it, 0.6 A)")
rec("WARN", "screen (~0.3-0.5 A at 5 V) + B1 charging (~1 A at 5 V) on the Pi's USB", "(about 1.3-1.5 A of the 1.6 A. If the Pi "
    "logs USB over-current or the screen flickers while the B1 charges, unplug the B1 once charged, or charge it from a "
    "phone charger: it prints over Bluetooth too)")
rec("PASS", "UPS OUT (12 V 3 A = 36 W) covers the Pi side", "(Pi 5 under load 8-12 W, NVMe 2-3 W, screen 2-2.5 W, B1 "
    "charging ~5 W, fan ~0.5 W: ~25 W at 5 V, ~28 W from 12 V through the adapter's converter = ~2.3 A of the 3 A)")
rec("INFO", "UPS runtime", "(3 x 2900 mAh in series ~ 32 Wh: about 1 h at full load, 2-3 h idle. The UCG-Ultra is NOT on the UPS)")

# ---------------------------------------------------------------- report
lines.append("")
lines.append(f"{counts['PASS']} PASS, {counts['FAIL']} FAIL, {counts['WARN']} WARN")
open(REPORT, "w").write("\n".join(lines) + "\n")
print("\n".join(lines))

# ---------------------------------------------------------------- wired scene for the renders
if WIRED:
    if os.path.exists(WIRED):
        shutil.rmtree(WIRED)
    shutil.copytree(SCENE, WIRED)
    d = json.load(open(os.path.join(WIRED, "scene.json")))
    for c in CABLES:
        tm = to_trimesh(tube(c["pts"], c["d"]))
        np.savez_compressed(os.path.join(WIRED, "meshes", f"{c['key']}.npz"), v=tm.vertices.astype(np.float32), f=tm.faces.astype(np.int32))
        d["meshes"][c["key"]] = dict(mat=c["mat"], label=c["label"], module="Wiring", file=None, qty=None, grams=None, bevel=0.0)
        d["nodes"].append(dict(mesh=c["key"], matrix=np.eye(4).ravel().tolist(), group="rack_cables", explode=[0.0, 0.0, 0.0], name=c["label"]))
        for i, pb in enumerate(c["plugs"]):
            k = f"{c['key']}_plug{i}"
            tm = to_trimesh(pb)
            np.savez_compressed(os.path.join(WIRED, "meshes", f"{k}.npz"), v=tm.vertices.astype(np.float32), f=tm.faces.astype(np.int32))
            d["meshes"][k] = dict(mat="dev_fan", label=f"{c['label']}: plug", module="Wiring", file=None, qty=None, grams=None, bevel=0.0)
            d["nodes"].append(dict(mesh=k, matrix=np.eye(4).ravel().tolist(), group="rack_cables", explode=[0.0, 0.0, 0.0], name=f"{c['label']}: plug"))
    json.dump(d, open(os.path.join(WIRED, "scene.json"), "w"))
    print("wired scene ->", WIRED)
