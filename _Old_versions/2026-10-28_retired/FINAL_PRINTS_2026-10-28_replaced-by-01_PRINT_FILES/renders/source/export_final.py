"""
FINAL BUILD (28 Oct 2026, FINAL_PRINTS_2026-10-28): v7.2 rack + B1 dock v5 + ready-made UCG-Ultra mount (Printables 942972)
+ Pi unit = shelf + UPS tray + Argon Poly+ 5 tray (W1) + Waveshare adapter (F) holder (W3/W4) + DC-notch faceplate
+ 12 V brick in the plate 13 cradle (8 mm spacer), with the brick lead into the UPS DC-IN and the right-angle UPS OUT
lead to the adapter's screw terminal (the route checked in verify_pi_power_path.py).
Colours as ordered: every PLA part silver, every PETG part black.
Export the rack, units and parts as meshes + a scene description for Blender (build_final.py).
Positions and explode offsets follow the option-2 pipeline. Rack frame: x across, y up, z back, mm.
Usage: python export_final.py <rack source dir> <Pi unit folder> <out dir> <UCG mesh dir> <Argon folder> <brick_cradle.py dir> <DC-notch faceplate STEP>
"""
import json
import math
import os
import sys
import numpy as np
import trimesh
import cadquery as cq

SRC, PI_DIR, OUT, UCG2, ARGON, BRICK_SRC, FP_NOTCH = sys.argv[1:8]
sys.path.insert(0, SRC)
sys.path.insert(0, os.path.join(ARGON, "source"))
sys.path.insert(0, BRICK_SRC)
import rack_t0 as r              # noqa: E402
import b1_dock as dk             # noqa: E402
import display as dp             # noqa: E402
import units as un               # noqa: E402
import argon_tray as AT          # noqa: E402
import waveshare_f_holder as WH  # noqa: E402
import brick_cradle as BC        # noqa: E402

PI_STEP = os.path.join(PI_DIR, "STEP_for_Onshape")
PI_COMP = os.path.join(PI_DIR, "Component_Models")
AR_STEP = os.path.join(ARGON, "STEP_for_Onshape")
os.makedirs(os.path.join(OUT, "meshes"), exist_ok=True)


def T(x=0, y=0, z=0):
    m = np.eye(4); m[:3, 3] = (x, y, z); return m


def Rx(deg):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    m = np.eye(4); m[1, 1], m[1, 2], m[2, 1], m[2, 2] = c, -s, s, c; return m


def Ry(deg):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    m = np.eye(4); m[0, 0], m[0, 2], m[2, 0], m[2, 2] = c, s, -s, c; return m


def Rz(deg):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    m = np.eye(4); m[0, 0], m[0, 1], m[1, 0], m[1, 1] = c, -s, s, c; return m


ML = T(0, 0, r.D) @ Ry(180)                                        # right -> left
PI_M = T(-un.PI_CX, -un.PI_Z0, un.PI_PY0) @ Rx(-90)                # Pi v3 frame -> rack


def tess(shape, tol=0.08):
    s = shape.val() if hasattr(shape, "val") else shape
    vs, ts = s.tessellate(tol, 0.2)
    return trimesh.Trimesh(np.array([(p.x, p.y, p.z) for p in vs]), np.array(ts), process=True)


def step(path):
    return cq.Workplane().add(cq.importers.importStep(path).val())


def b(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def cyl(x, y, z0, z1, d):
    return cq.Workplane("XY").circle(d / 2).extrude(z1 - z0).translate((x, y, z0))


def fuse(parts):
    out = parts[0]
    for p in parts[1:]:
        out = out.union(p)
    return out


M = {}


def add(key, shape_or_mesh, mat, label, module, file=None, qty=None, grams=None, note="", pre=None, bevel=0.0):
    mesh = shape_or_mesh if isinstance(shape_or_mesh, trimesh.Trimesh) else tess(shape_or_mesh)
    if pre is not None:
        mesh = mesh.copy(); mesh.apply_transform(pre)
    M[key] = dict(mesh=mesh, mat=mat, label=label, module=module, file=file, qty=qty, grams=grams, note=note, bevel=bevel)


# ---------------- rack, dock, screen: all PLA silver as ordered ----------------
add("side2U", r.side_module(2, True), "pla_silver", "Side module, 2U base", "Rack", "Rack_SideModule_2U_Base_x2.stl", 2, 93)
add("side3U", r.side_module(3), "pla_silver", "Side module, 3U", "Rack", "Rack_SideModule_3U_x4.stl", 4, 104)
add("side1U", r.side_module(1), "pla_silver", "Side module, 1U top", "Rack", "Rack_SideModule_1U_Top_x2.stl", 2, 50)
add("cap", r.cap_half(), "pla_silver", "Cap half", "Rack", "Rack_CapHalf_x2.stl", 2, 96)
add("handle", r.handle(), "pla_silver", "Handle", "Rack", "Rack_Handle_x2.stl", 2, 36)
add("bar", r.base_bar(*r.BAR_Z[0]), "pla_silver", "Base bar", "Rack", "Rack_BaseBar_x3.stl", 3, 21)
add("dock", dk.body(), "pla_silver", "B1 dock body", "B1 dock", "B1_Dock_3U_Body.stl", 1, 125)
add("ear", dk.ear(1), "pla_silver", "Rack ear (dock and screen)", "B1 dock", "B1_Dock_3U_Ear_x2.stl", 4, 10)
B1P = dk.b1_parts()
for k, mat in (("body", "dev_b1_body"), ("lid", "dev_b1_lid"), ("slide", "dev_white"), ("led", "dev_led"), ("button", "dev_b1_button")):
    add(f"b1_{k}", B1P[k], mat, f"NIIMBOT B1 {k}" if k != "body" else "NIIMBOT B1 (132 x 91 x 62)", "B1 dock")
add("b1_lid_open", dk.lid_open(80), "dev_b1_lid", "NIIMBOT B1 lid, open 80 deg", "B1 dock")
add("disp", dp.body(), "pla_silver", "Screen module body (C type)", "Screen", "Display7C_3U_Body.stl", 1, 71,
    "not in the order yet: prints after the screen arrives (4 Nov)")
clips = dp.clips()
add("clip0", clips[0], "pla_silver", "Screen clip", "Screen", "Display7C_Clip_x4.stl", 4, 0.6)
for i in (1, 2, 3):
    add(f"clip{i}", clips[i], "pla_silver", "Screen clip", "Screen")
add("glass", dp.glass_dummy(), "dev_screen", "7-inch screen (Waveshare C type)", "Screen")

# ---------------- UCG-Ultra: the ready-made ALT2 mount, PETG black ----------------
add("ucg", trimesh.load(os.path.join(UCG2, "ucg_option2_rack.stl"), force="mesh"), "petg_black",
    "UCG-Ultra mount, 3 keystones (Printables 942972)", "UCG 1U", "UCG-Ultra_1U_3-keystones_Printables-942972.stl", 1, None)
add("ucg_gw", trimesh.load(os.path.join(UCG2, "ucg_ultra_in_option2_rack.stl"), force="mesh"), "dev_ucg", "UniFi UCG-Ultra", "UCG 1U", bevel=4.0)

# ---------------- Pi unit (Argon Poly+ 5 build), PETG black ----------------
add("pi_shelf", step(os.path.join(PI_STEP, "Rack_Shelf_pinned.step")), "petg_black", "Pi shelf (pinned)", "Pi unit", "Rack_Shelf_pinned.stl", 1, 96)
add("pi_face", step(FP_NOTCH), "petg_black", "Pi faceplate (DC-notch)", "Pi unit", "12_Pi_Faceplate_2U_DC-notch__x1__PETG.stl", 1, 64)
add("pi_ups", step(os.path.join(PI_STEP, "Pi5_UPS_v3_ups_tray_pinned.step")), "petg_black", "Pi UPS tray (pinned)", "Pi unit", "Pi5_UPS_v3_ups_tray_pinned.stl", 1, 62)
add("pi_argon", step(os.path.join(AR_STEP, "Pi5_ArgonPoly5_tray.step")), "petg_black", "Argon Poly+ 5 tray (plate 11B)", "Pi unit", "Pi5_ArgonPoly5_tray.stl", 1, None)
add("pi_hbase", step(os.path.join(AR_STEP, "Waveshare_F_holder_base.step")), "petg_black", "Adapter (F) holder, base", "Pi unit", "W3_Waveshare_F_Holder_Base__x1__PETG__WAIT-test-fit.stl", 1, 35)
add("pi_hlid", step(os.path.join(AR_STEP, "Waveshare_F_holder_lid.step")), "petg_black", "Adapter (F) holder, lid", "Pi unit", "W4_Waveshare_F_Holder_Lid__x1__PETG__WAIT-test-fit.stl", 1, 17)
add("c_ups", step(os.path.join(PI_COMP, "Cuzor_MiniUPS_Pro_12V3A.step")), "dev_ups", "Cuzor Mini UPS Pro", "Pi unit",
    pre=T(50.6, 40.6, 1.0))                                        # UPS_X 0.6..100.6, UPS_Y 0.6..80.6, on the 1 mm ribs


def argon_poly5():
    """stand-in for the Argon Poly+ 5 (seller size 93.5 x 64 x 30; no official drawing): black shell, grooved top with a
    round louvred window over the THRML 30 mm fan, Pi 5 ports where the board puts them. In the tray's datum corner,
    on 1 mm foam tape, USB/Ethernet end to the rack rear, HDMI/USB-C side to the left (towards the holder)."""
    L, Wc, Hc = AT.CASES["POLY5"]["nominal"]
    x0, x1, y0, y1 = AT.X_DATUM - Wc, AT.X_DATUM, AT.Y_DATUM, AT.Y_DATUM + L
    z0 = AT.ZS + 1.0
    z1 = z0 + Hc
    zt = z1 - 4.0                                                  # top cover split
    bx0 = x0 + (Wc - 56.0) / 2                                     # board edge (HDMI side)
    by1 = y0 + 87.0                                                # board far end (ports overhang the rear by ~2)
    zp = z0 + 5.5                                                  # PCB top
    shell = b(x0, x1, y0, y1, z0, zt).edges("|Z").fillet(5.0)
    try:
        shell = shell.faces("<Z").edges().fillet(1.5)
    except Exception:                                              # noqa: BLE001
        pass
    top = b(x0, x1, y0, y1, zt + 0.25, z1).edges("|Z").fillet(5.0)
    try:
        top = top.faces(">Z").edges().fillet(1.2)
    except Exception:                                              # noqa: BLE001
        pass
    # fan window and pocket
    fx, fy, fr = x0 + Wc * 0.47, y0 + L * 0.58, 14.0
    shell = shell.cut(cyl(fx, fy, zt - 7.0, zt + 1, 2 * fr + 1.0))
    reach = 200.0
    keep = cyl(fx, fy, z1 - 1.5, z1 + 1, 2 * fr + 8.0)
    zone = b(x0 + 3, x1 - 3, y0 + 3, y1 - 3, z1 - 0.8, z1 + 1).cut(keep)
    grooves = fuse([cq.Workplane("XY").rect(reach * 2, 1.4).extrude(2).translate((0, i * 7.0, z1 - 0.8))
                    .rotate((0, 0, 0), (0, 0, 1), 60.0).translate(((x0 + x1) / 2, (y0 + y1) / 2, 0)) for i in range(-16, 17)])
    top = top.cut(grooves.intersect(zone))
    disc = cyl(fx, fy, zt - 1, z1 + 1, 2 * fr)
    slats = fuse([cq.Workplane("XY").rect(reach, 2.0).extrude(Hc).translate((0, i * 3.6, zt - 1))
                  .rotate((0, 0, 0), (0, 0, 1), 60.0).translate((fx, fy, 0)) for i in range(-5, 6)])
    top = top.cut(slats.intersect(disc))
    fan = cyl(fx, fy, zt - 6.0, zt - 3.5, 12.0)
    for k in range(7):
        bl = b(6.0, 13.6, -1.6, 1.6, zt - 5.8, zt - 4.6).rotate((0, 0, 0), (1, 0, 0), 18).rotate((0, 0, 0), (0, 0, 1), k * 360 / 7)
        fan = fan.union(bl.translate((fx, fy, 0)))
    # ports: openings in the shell, metal shells set just behind the face
    metal, blue, dark = [], [], []
    rj = (bx0 + 10.25, 16.0, 13.5)                                 # Pi 5: RJ45 by the HDMI side, then two USB stacks
    usb = [(bx0 + 29.1, "usb3"), (bx0 + 47.0, "usb2")]
    shell = shell.cut(b(rj[0] - 8.6, rj[0] + 8.6, y0 - 1, y0 + 2.4, zp - 0.4, zp + rj[2] + 0.5))
    m = b(rj[0] - 8.0, rj[0] + 8.0, y0 + 1.2, y0 + 20, zp, zp + rj[2])
    m = m.cut(b(rj[0] - 5.9, rj[0] + 5.9, y0 + 1.0, y0 + 14, zp + 1.5, zp + 10.0))
    m = m.cut(b(rj[0] - 3.0, rj[0] + 3.0, y0 + 1.0, y0 + 14, zp + 9.9, zp + 11.6))
    metal.append(m)
    for ux, kind in usb:
        shell = shell.cut(b(ux - 7.4, ux + 7.4, y0 - 1, y0 + 2.4, zp - 0.4, zp + 16.0))
        m = b(ux - 6.6, ux + 6.6, y0 + 1.2, y0 + 18, zp, zp + 15.6)
        for zc in (zp + 4.0, zp + 11.6):
            m = m.cut(b(ux - 6.0, ux + 6.0, y0 + 1.0, y0 + 14, zc - 2.7, zc + 2.7))
            tongue = b(ux - 5.6, ux + 5.6, y0 + 3.5, y0 + 14, zc - 2.7, zc - 0.9)
            (blue if kind == "usb3" else dark).append(tongue)
        metal.append(m)
    side = [(by1 - 11.2, 9.6, 3.6), (by1 - 25.8, 7.0, 3.4), (by1 - 39.2, 7.0, 3.4)]   # USB-C, HDMI0, HDMI1 centres
    for cy_, w, h in side:
        zc = zp + h / 2 + 0.2
        shell = shell.cut(b(x0 - 1, x0 + 2.4, cy_ - w / 2 - 1.2, cy_ + w / 2 + 1.2, zc - h / 2 - 1.2, zc + h / 2 + 1.2)
                          .edges("|X").fillet(1.0))
        m = b(x0 + 1.2, x0 + 9.0, cy_ - w / 2, cy_ + w / 2, zc - h / 2, zc + h / 2)
        m = m.cut(b(x0 + 1.0, x0 + 8.0, cy_ - w / 2 + 0.5, cy_ + w / 2 - 0.5, zc - h / 2 + 0.5, zc + h / 2 - 0.5))
        metal.append(m)
    shell = shell.cut(b((x0 + x1) / 2 - 7, (x0 + x1) / 2 + 7, y1 - 2.4, y1 + 1, z0 + 1.2, z0 + 3.4))   # microSD slot
    return shell, top, fan, fuse(metal), fuse(blue), fuse(dark)


AR = argon_poly5()
add("ar_shell", AR[0], "dev_case_black", "Argon Poly+ 5 (stand-in, 93.5 x 64 x 30)", "Pi unit")
add("ar_top", AR[1], "dev_alu_black", "Argon Poly+ 5 top", "Pi unit")
add("ar_fan", AR[2], "dev_fan", "THRML 30 mm fan", "Pi unit")
add("ar_ports", AR[3], "dev_alu_silver", "Pi 5 port shells", "Pi unit")
add("ar_usb3", AR[4], "dev_usb3", "USB 3 tongues", "Pi unit")
add("ar_usb2", AR[5], "dev_fan", "USB 2 tongues", "Pi unit")


def adapter_f():
    """the adapter (F) in the holder, as verify_waveshare_f_holder.py models it: PCB, hole pattern and RJ45/HDMI from
    Waveshare's drawing; everything else (SSD, terminal, plugs, parts) is an estimate for the picture"""
    def comp(xd0, xd1, yd0, yd1, z0, z1):
        (xa, ya), (xb, yb) = WH.d2v(xd0, yd0), WH.d2v(xd1, yd1)
        return b(min(xa, xb), max(xa, xb), min(ya, yb), max(ya, yb), WH.PCB_TOP + z0, WH.PCB_TOP + z1)
    pcb = b(WH.PCB_X0, WH.XP, WH.PCB_Y0, WH.PCB_Y0 + WH.PCB_L, WH.ZB, WH.PCB_TOP)
    for hx, hy in WH.HOLES_V:
        pcb = pcb.cut(cyl(hx, hy, WH.ZB - 1, WH.PCB_TOP + 1, 2.7))
    rj = comp(-1.0, 20.0, 30.7 - 8.0, 30.7 + 8.0, 0, 13.5)
    rj = rj.cut(comp(-1.2, 12.0, 30.7 - 5.9, 30.7 + 5.9, 1.5, 10.0))
    hd = comp(-1.0, 13.0, 10.05 - 7.6, 10.05 + 7.6, 0, 6.0)
    hd = hd.cut(comp(-1.2, 9.0, 10.05 - 7.0, 10.05 + 7.0, 0.8, 5.2))
    metal = rj.union(hd)
    term = comp(79.0, 97.0, 0.8, 16.0, 0, 10.0)
    for yd in (4.6, 12.0):
        term = term.cut(cyl(*WH.d2v(90.0, yd), WH.PCB_TOP + 8.0, WH.PCB_TOP + 11, 3.4))
    ssd = comp(40.0, 70.0, 15.0, 37.0, 1.6, 3.0)
    sock = comp(35.5, 40.0, 14.0, 38.0, 0, 4.2)
    parts = [sock]
    for xd, yd in ((32.0, 45.5), (44.0, 45.5), (56.0, 45.5)):
        parts.append(comp(xd - 3.5, xd + 3.5, yd - 3.5, yd + 3.5, 0, 4.5))   # inductors
    caps = [cyl(*WH.d2v(xd, 47.0), WH.PCB_TOP, WH.PCB_TOP + 8.0, 6.3) for xd in (66.0, 74.0)]
    plugs = []
    for xd, hw, ln, hh in ((34.4, 3.4, 4.0, 4.5), (59.2, 3.4, 5.0, 2.8), (73.6, 4.6, 5.5, 3.3)):
        cy_ = WH.PCB_Y0 + xd
        plugs.append(b(WH.XP - 3.0, WH.XP + ln, cy_ - hw, cy_ + hw, WH.PCB_TOP - 0.5, WH.PCB_TOP - 0.5 + hh))
    return pcb, metal, term, ssd, fuse(parts), fuse(caps), fuse(plugs)


AF = adapter_f()
add("af_pcb", AF[0], "dev_pcb_black", "Waveshare adapter (F) PCB", "Pi unit")
add("af_metal", AF[1], "dev_alu_silver", "Adapter RJ45 (2.5G) + HDMI-A", "Pi unit")
add("af_term", AF[2], "dev_terminal", "Adapter 12 V screw terminal", "Pi unit")
add("af_ssd", AF[3], "dev_ssd", "EVM 512 GB 2230 NVMe", "Pi unit")
add("af_parts", AF[4], "dev_fan", "Adapter socket + inductors", "Pi unit")
add("af_caps", AF[5], "dev_alu_silver", "Adapter capacitors", "Pi unit")
add("af_plugs", AF[6], "dev_fan", "Adapter plugs (SH1.0, micro-HDMI, USB-C)", "Pi unit")


# ---------------- 28 Oct: the 12 V brick in its cradle, and the two 12 V leads ----------------
def tube_mesh(pts, d, sections=20):
    """a cable along a polyline: cylinders + spheres at the bends (render only, no booleans)"""
    r_ = d / 2
    ms = [trimesh.creation.icosphere(subdivisions=2, radius=r_).apply_translation(p) for p in pts]
    for a_, b_ in zip(pts, pts[1:]):
        if np.linalg.norm(np.subtract(b_, a_)) > 1e-6:
            ms.append(trimesh.creation.cylinder(radius=r_, segment=[a_, b_], sections=sections))
    return trimesh.util.concatenate(ms)


add("cradle", BC.brick_cradle(), "petg_black", "12 V brick cradle (plate 13)", "Pi unit", "13_Brick_Cradle_12V__x1__PETG.stl", 1, 63)
add("spacer8", BC.spacer(8.0), "petg_black", "Brick spacer, 8 mm", "Pi unit", "14_Brick_Spacer_8mm__x1__PETG.stl", 1, 17)
BR = BC.brick_dummy(110.0, 50.0, 30.0, 8.0).val().BoundingBox()
add("brick", b(BR.xmin, BR.xmax, BR.ymin, BR.ymax, BR.zmin, BR.zmax).edges().fillet(3.0), "dev_brick", "12 V 5 A brick (Robu, 110 x 50 x 30)", "Pi unit")
bxc, byc = (BR.xmin + BR.xmax) / 2, (BR.ymin + BR.ymax) / 2
add("c13", b(bxc - 16.75, bxc + 16.75, byc - 12.0, byc + 12.0, BR.zmax, BR.zmax + 38.0).edges("|Z").fillet(4.0), "dev_fan", "Mains plug (C13)", "Pi unit")
add("mains", tube_mesh([(bxc, byc, BR.zmax + 38.0), (bxc, byc - 2.0, BR.zmax + 46.0), (bxc, byc - 12.0, BR.zmax + 52.0),
                        (bxc, byc - 28.0, BR.zmax + 56.0), (bxc, -r.PLINTH + 3.5, BR.zmax + 60.0), (bxc, -r.PLINTH + 3.5, BR.zmax + 75.0)], 7.0),
    "dev_cable", "Mains cord", "Pi unit")
# brick lead (rack frame): the route verify_brick.py checks, out through the faceplate notch, then into the DC-IN window
NX = BC.NOTCH_X
jack_x, jack_y = 96.0 - un.PI_CX, 17.0 - un.PI_Z0                # DC-IN plug at the window centre (as the windows intend)
jack_z = un.PI_PY0 - 80.6                                          # the UPS's front face
add("dcin_plug", cq.Workplane("XY").circle(5.25).extrude(jack_z + 6.0).translate((jack_x, jack_y, -6.0))
    .union(cq.Workplane("XY").circle(3.2).extrude(9.0).translate((jack_x, jack_y, -15.0))), "dev_fan", "Brick DC plug in the UPS DC-IN", "Pi unit")
add("brick_lead", tube_mesh([(bxc, byc, BR.zmin), (bxc, byc, 40.0), (NX, 9.0, 22.0), (NX, 3.4, 8.0), (NX, 3.4, -9.0),
                             (NX - 6.0, 5.0, -12.0), (52.0, 15.0, -16.5), (jack_x + 3.0, jack_y - 1.0, -17.5), (jack_x, jack_y, -15.0)], 4.0),
    "dev_cable", "Brick 12 V lead", "Pi unit")
# UPS OUT right-angle plug + lead to the adapter's screw terminal (v3 frame, route from verify_pi_power_path.py)
OX, OY, OZ = 86.6, 0.6, 11.5
YE = OY - 16.0 + 5.5
add("out_plug", b(OX - 5.5, OX + 5.5, OY - 16.0, OY, OZ - 6.0, OZ + 6.0).edges("|Y").fillet(2.5)
    .union(cq.Workplane("YZ").circle(3.25).extrude(10.0).translate((OX + 5.5, YE, OZ))), "dev_fan", "Right-angle DC plug in the UPS OUT", "Pi unit")
TX = sum(WH.TERM_X) / 2
TZ = WH.PCB_TOP + 5.0
TY = WH.PCB_Y0 + 97.0
cx_, cy_, w_, h_ = AT.LEAD_HOLE
OUT_PATH = [(OX + 15.5, YE, OZ), (104.5, YE + 2.0, OZ), (106.3, -3.5, OZ), (106.3, 4.0, OZ), (106.5, 22.0, 14.0),
            (102.0, 33.0, 31.6), (102.0, 47.0, 31.6), (107.0, 58.0, 16.0), (107.0, 84.0, 14.0), (107.0, 95.0, 14.0),
            (100.0, 101.0, 27.0), (cx_ + 2.0, 101.0, 29.0), (cx_, cy_, 33.0), (cx_, cy_, AT.ZS + 4.0),
            (TX, WH.OY1 + 4.0, TZ + 3.0), (TX, WH.OY1 + 0.5, TZ)]
add("out_lead", tube_mesh(OUT_PATH, 4.0), "dev_cable", "UPS OUT lead to the adapter terminal", "Pi unit")
WX = [WH.d2v(90.0, yd)[0] for yd in (4.6, 12.0)]
add("wire_red", tube_mesh([(TX + 0.9, WH.OY1 + 0.5, TZ), (WX[0], TY - 3.0, TZ - 1.0)], 1.6), "dev_wire_red", "+12 V wire", "Pi unit")
add("wire_blk", tube_mesh([(TX - 0.9, WH.OY1 + 0.5, TZ), (WX[1], TY - 3.0, TZ - 1.0)], 1.6), "dev_cable", "0 V wire", "Pi unit")

# ---------------- assembly nodes ----------------
YB = r.module_bottoms()
nodes = []


def node(key, mat, group, explode, name=None):
    nodes.append(dict(mesh=key, matrix=np.asarray(mat).ravel().tolist(), group=group, explode=list(map(float, explode)),
                      name=name or M[key]["label"]))


for i, (n, yb) in enumerate(zip(r.MODULES, YB)):
    key = "side2U" if i == 0 else ("side3U" if n == 3 else "side1U")
    node(key, T(0, yb, 0), "rack", (115, 70 * i, 0), f"{M[key]['label']} (right)")
    node(key, ML @ T(0, yb, 0), "rack", (-115, 70 * i, 0), f"{M[key]['label']} (left)")
for (z0, _), nm in zip(r.BAR_Z, ("front", "middle", "rear")):
    node("bar", T(0, 0, z0 - r.BAR_Z[0][0]), "rack", (0, -75, 0), f"Base bar ({nm})")
node("cap", np.eye(4), "rack", (75, 320, 0), "Cap half (right)")
node("cap", ML, "rack", (-75, 320, 0), "Cap half (left)")
node("handle", np.eye(4), "rack", (75, 400, 0), "Handle (right)")
node("handle", ML, "rack", (-75, 400, 0), "Handle (left)")
Dd = T(0, un.YC_DOCK, -dk.EAR_T)
node("dock", Dd, "dock", (0, 70, -230))
node("ear", Dd, "dock", (40, 70, -280), "Dock ear (right)")
node("ear", Dd @ Rz(180), "dock", (-40, 70, -280), "Dock ear (left)")
for k in ("body", "lid", "slide", "led", "button"):
    node(f"b1_{k}", Dd, "dock", (0, 110, -360))
node("dock", Dd, "dock_open", (0, 0, 0))
node("ear", Dd, "dock_open", (0, 0, 0), "Dock ear (right)")
node("ear", Dd @ Rz(180), "dock_open", (0, 0, 0), "Dock ear (left)")
for k in ("body", "slide", "led", "button"):
    node(f"b1_{k}", Dd, "dock_open", (0, 0, 0))
node("b1_lid_open", Dd, "dock_open", (0, 0, 0))
Ds = T(0, un.YC_DISP, -dp.Z0)
node("disp", Ds, "screen", (0, 140, -210))
node("glass", Ds, "screen", (0, 140, -290))
for i in range(4):
    node(f"clip{i}", Ds, "screen", (0, 140, -170), "Screen clip")
node("ear", Ds, "screen", (40, 140, -270), "Screen ear (right)")
node("ear", Ds @ Rz(180), "screen", (-40, 140, -270), "Screen ear (left)")
node("ucg", np.eye(4), "ucg", (0, 210, -220))
node("ucg_gw", np.eye(4), "ucg", (0, 250, -300))
node("pi_shelf", PI_M, "pi", (0, 0, -240))
node("pi_ups", PI_M, "pi", (0, 35, -240))
node("c_ups", PI_M, "pi", (0, 55, -240))
node("pi_argon", PI_M, "pi", (0, 80, -240))
for k in ("ar_shell", "ar_fan", "ar_ports", "ar_usb3", "ar_usb2"):
    node(k, PI_M, "pi", (0, 112, -240))
node("ar_top", PI_M, "pi", (0, 132, -240))
node("pi_hbase", PI_M, "pi", (0, 104, -240))
for k in ("af_pcb", "af_metal", "af_term", "af_ssd", "af_parts", "af_caps", "af_plugs"):
    node(k, PI_M, "pi", (0, 126, -240))
node("pi_hlid", PI_M, "pi", (0, 152, -240))
node("pi_face", PI_M, "pi", (0, 0, -330))
node("cradle", np.eye(4), "pi", (160, 0, 0))
node("spacer8", np.eye(4), "pi", (160, 40, 0))
node("brick", np.eye(4), "pi", (160, 80, 0))
for k in ("c13", "mains", "dcin_plug", "brick_lead"):
    node(k, np.eye(4), "pi_cables", (0, 0, 0))
for k in ("out_plug", "out_lead", "wire_red", "wire_blk"):
    node(k, PI_M, "pi_cables", (0, 0, 0))


# ---------------- emissive panels: the screen's active area and the gateway's status display ----------------
def placed_bounds(key, mat):
    return trimesh.transform_points(M[key]["mesh"].vertices, np.asarray(mat))


v = placed_bounds("glass", Ds)
zf = v[:, 2].min()
front = v[v[:, 2] < zf + 0.3]
cx, cy = (front[:, 0].min() + front[:, 0].max()) / 2, (front[:, 1].min() + front[:, 1].max()) / 2
v = placed_bounds("ucg_gw", np.eye(4))
gz = v[:, 2].min()
gcy = (v[:, 1].min() + v[:, 1].max()) / 2
gcx = (v[:, 0].min() + v[:, 0].max()) / 2
panels = [dict(name="Screen image", group="screen", explode=[0, 140, -290], center=[float(cx), float(cy), float(zf - 0.05)],
               size=[154.2, 85.9], image="screen_ui.png", strength=2.2),
          dict(name="UCG status display", group="ucg", explode=[0, 250, -300], center=[float(gcx), float(gcy), float(gz - 0.05)],
               size=[24.0, 12.0], image="ucg_ui.png", strength=2.0)]

# ---------------- clearance sanity: nothing new pokes into the shelf/tray/holder it sits on ----------------
def placed(key):
    mm = M[key]["mesh"].copy(); mm.apply_transform(PI_M); return mm


for a_, b_ in (("ar_shell", "pi_argon"), ("ar_shell", "pi_hbase"), ("af_pcb", "pi_hbase"), ("af_plugs", "ar_shell")):
    A, B = placed(a_), placed(b_)
    print(f"bbox {a_} vs {b_}: A z {A.bounds[0][1]:.1f}..{A.bounds[1][1]:.1f}  B z {B.bounds[0][1]:.1f}..{B.bounds[1][1]:.1f}")
ab = placed("ar_top").bounds
db = trimesh.transform_points(M["dock"]["mesh"].vertices, Dd)
print(f"Argon top y_rack {ab[1][1]:.1f}  dock underside y_rack {db[:, 1].min():.1f}")

# ---------------- write ----------------
meshes = {}
tris = 0
for key, info in M.items():
    m = info["mesh"]
    if not info["bevel"]:
        m = trimesh.graph.smooth_shade(m, angle=math.radians(30))   # split at creases: smooth curves, crisp edges
    np.savez_compressed(os.path.join(OUT, "meshes", f"{key}.npz"), v=np.asarray(m.vertices, np.float32),
                        f=np.asarray(m.faces, np.int32))
    meshes[key] = dict(mat=info["mat"], label=info["label"], module=info["module"], file=info["file"],
                       qty=info["qty"], grams=info["grams"], bevel=info["bevel"])
    tris += len(m.faces)
    print(f"{key:9s} {len(m.faces):8d} tris")
json.dump(dict(meshes=meshes, nodes=nodes, parts=[], panels=panels, desk=-r.PLINTH),
          open(os.path.join(OUT, "scene.json"), "w"), indent=1)
print("total tris", tris)
