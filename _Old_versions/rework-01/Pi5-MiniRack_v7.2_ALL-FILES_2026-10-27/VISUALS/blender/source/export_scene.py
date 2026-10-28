"""
Export the v7.2 rack, units and parts as meshes + a scene description for Blender (build_scene.py).
Positions and explode offsets are the same as the 3D page (make_visuals72.py). Rack frame: x across, y up, z back, mm.
Usage: python export_scene.py <rack source dir> <Pi unit folder> <out dir>
"""
import json
import math
import os
import sys
import numpy as np
import trimesh
import cadquery as cq

SRC, PI_DIR, OUT = sys.argv[1:4]
sys.path.insert(0, SRC)
import rack_t0 as r          # noqa: E402
import b1_dock as dk         # noqa: E402
import display as dp         # noqa: E402
import units as un           # noqa: E402
import ucg_shelf as ug       # noqa: E402

PI_STEP = os.path.join(PI_DIR, "STEP_for_Onshape")
PI_COMP = os.path.join(PI_DIR, "Component_Models")
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
PI_M = T(-un.PI_CX, -un.PI_Z0, un.PI_PY0) @ Rx(-90)                # Pi v3 case frame -> rack


def tess(shape, tol=0.08):
    s = shape.val() if hasattr(shape, "val") else shape
    vs, ts = s.tessellate(tol, 0.2)
    return trimesh.Trimesh(np.array([(p.x, p.y, p.z) for p in vs]), np.array(ts), process=True)


def step(path):
    return cq.Workplane().add(cq.importers.importStep(path).val())


M = {}


def add(key, shape_or_mesh, mat, label, module, file=None, qty=None, grams=None, note="", pre=None, bevel=0.0):
    mesh = shape_or_mesh if isinstance(shape_or_mesh, trimesh.Trimesh) else tess(shape_or_mesh)
    if pre is not None:
        mesh = mesh.copy(); mesh.apply_transform(pre)
    M[key] = dict(mesh=mesh, mat=mat, label=label, module=module, file=file, qty=qty, grams=grams, note=note, bevel=bevel)


add("side2U", r.side_module(2, True), "pla_silver", "Side module, 2U base", "Rack", "Rack_SideModule_2U_Base_x2.stl", 2, 93)
add("side3U", r.side_module(3), "pla_silver", "Side module, 3U", "Rack", "Rack_SideModule_3U_x4.stl", 4, 104)
add("side1U", r.side_module(1), "pla_silver", "Side module, 1U top", "Rack", "Rack_SideModule_1U_Top_x2.stl", 2, 50)
add("cap", r.cap_half(), "pla_black", "Cap half", "Rack", "Rack_CapHalf_x2.stl", 2, 96)
add("handle", r.handle(), "pla_silver", "Handle", "Rack", "Rack_Handle_x2.stl", 2, 36)
add("bar", r.base_bar(*r.BAR_Z[0]), "pla_grey", "Base bar", "Rack", "Rack_BaseBar_x3.stl", 3, 21)
add("dock", dk.body(), "pla_dark", "B1 dock body", "B1 dock", "B1_Dock_3U_Body.stl", 1, 125)
add("ear", dk.ear(1), "pla_darker", "Rack ear (dock and screen)", "B1 dock", "B1_Dock_3U_Ear_x2.stl", 4, 10)
add("spacer", dk.spacer(1, local=True), "pla_orange", "B1 spacer, 5 mm", "B1 dock", "B1_Spacer_5mm_x2.stl", 2, 9, "only for a 62 mm B1")
add("b1", dk.b1_dummy(), "dev_b1", "NIIMBOT B1 (67 mm)", "B1 dock", bevel=5.0)
add("disp", dp.body(), "pla_dark", "Screen module body (C type)", "Screen", "Display7C_3U_Body.stl", 1, 71)
clips = dp.clips()
add("clip0", clips[0], "pla_darker", "Screen clip", "Screen", "Display7C_Clip_x4.stl", 4, 0.6)
for i in (1, 2, 3):
    add(f"clip{i}", clips[i], "pla_darker", "Screen clip", "Screen")
add("glass", dp.glass_dummy(), "dev_screen", "7-inch screen (Waveshare C type)", "Screen")
add("pi_shelf", step(os.path.join(PI_STEP, "Rack_Shelf_pinned.step")), "petg_dark", "Pi shelf (pinned)", "Pi unit", "Rack_Shelf_pinned.stl", 1, 96)
add("pi_face", step(os.path.join(PI_STEP, "Rack_Faceplate_2U_10in.step")), "petg_dark", "Pi faceplate (one piece)", "Pi unit", "Rack_Faceplate_2U_10in.stl", 1, 64)
add("pi_faceL", step(os.path.join(PI_STEP, "Rack_Faceplate_Left.step")), "petg_dark", "Pi faceplate, left half", "Pi unit", "Rack_Faceplate_Left.stl", 1, 34, "only for 220 mm beds")
add("pi_faceR", step(os.path.join(PI_STEP, "Rack_Faceplate_Right.step")), "petg_dark", "Pi faceplate, right half", "Pi unit", "Rack_Faceplate_Right.stl", 1, 31, "only for 220 mm beds")
add("pi_ups", step(os.path.join(PI_STEP, "Pi5_UPS_v3_ups_tray_pinned.step")), "petg_darker", "Pi UPS tray (pinned)", "Pi unit", "Pi5_UPS_v3_ups_tray_pinned.stl", 1, 62)
add("pi_board", step(os.path.join(PI_STEP, "Pi5_UPS_v3_board_tray_HDMIexit.step")), "petg_darker", "Pi board tray", "Pi unit", "Pi5_UPS_v3_board_tray_HDMIexit.stl", 1, 65)
add("pi_lid", step(os.path.join(PI_STEP, "Pi5_UPS_v3_lid.step")), "petg_lid", "Pi case lid", "Pi unit", "Pi5_UPS_v3_lid.stl", 1, 28)
add("ucg", ug.body(), "petg_dark", "UCG-Ultra shelf (1U)", "UCG 1U", "UCG_Ultra_1U_Shelf.stl", 1, 95)
add("ucg_gw", ug.gateway_dummy(), "dev_ucg", "UniFi UCG-Ultra", "UCG 1U", bevel=4.0)
add("pi_shims", trimesh.load(os.path.join(PI_DIR, "STL_for_printing", "Pi5_UPS_v3_shims.stl"), force="mesh"),
    "petg_darker", "Adapter shims", "Pi unit", "Pi5_UPS_v3_shims.stl", 1, 1, pre=Rx(-90))

# Pi unit components, placed in the v3 case frame as case_v3.py does
PI_PLACE = T(56.9, 90.0, 41.9) @ Rz(-90)                           # Pi 5: pi_xy(mx, my) = (X_PI + my, Y0 + 85 - mx), PCB on the bosses
add("c_pi5", step(os.path.join(PI_COMP, "RaspberryPi5_8GB.step")), "dev_pcb_green", "Raspberry Pi 5", "Pi unit", pre=PI_PLACE)
add("c_cool", step(os.path.join(PI_COMP, "GeeekPi_ArmorLite_V5.step")), "dev_alu_black", "Armor Lite V5 cooler", "Pi unit",
    pre=PI_PLACE @ T(32.5, 28.0, 3.9))                             # over the SoC, fan under the lid grill (x 84.9, y 58)
add("c_ups", step(os.path.join(PI_COMP, "Cuzor_MiniUPS_Pro_12V3A.step")), "dev_ups", "Cuzor Mini UPS Pro", "Pi unit",
    pre=T(50.6, 40.6, 1.0))                                        # UPS_X 0.6..100.6, UPS_Y 0.6..80.6, on the 1 mm ribs
add("c_adapt", step(os.path.join(PI_COMP, "Waveshare_Adapter_F_v3position.step")), "dev_pcb_black", "Waveshare adapter (F)", "Pi unit")

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
node("b1", Dd, "dock", (0, 110, -360))
Ds = T(0, un.YC_DISP, -dp.Z0)
node("disp", Ds, "screen", (0, 140, -210))
node("glass", Ds, "screen", (0, 140, -290))
for i in range(4):
    node(f"clip{i}", Ds, "screen", (0, 140, -170), "Screen clip")
node("ear", Ds, "screen", (40, 140, -270), "Screen ear (right)")
node("ear", Ds @ Rz(180), "screen", (-40, 140, -270), "Screen ear (left)")
Du = T(0, un.YC_UCG, -ug.PANEL_T)
node("ucg", Du, "ucg", (0, 210, -220))
node("ucg_gw", Du, "ucg", (0, 250, -300))
node("pi_shelf", PI_M, "pi", (0, 0, -240))
node("pi_ups", PI_M, "pi", (0, 35, -240))
node("c_ups", PI_M, "pi", (0, 55, -240))
node("pi_board", PI_M, "pi", (0, 75, -240))
node("c_pi5", PI_M, "pi", (0, 95, -240))
node("c_cool", PI_M, "pi", (0, 95, -240))
node("c_adapt", PI_M, "pi", (0, 95, -240))
node("pi_lid", PI_M, "pi", (0, 120, -240))
node("pi_face", PI_M, "pi", (0, 0, -330))

# ---------------- emissive panels: the screen's active area and the gateway's status display ----------------
def placed_bounds(key, mat):
    v = trimesh.transform_points(M[key]["mesh"].vertices, np.asarray(mat))
    return v


v = placed_bounds("glass", Ds)
zf = v[:, 2].min()
front = v[v[:, 2] < zf + 0.3]
cx, cy = (front[:, 0].min() + front[:, 0].max()) / 2, (front[:, 1].min() + front[:, 1].max()) / 2
v = placed_bounds("ucg_gw", Du)
gz = v[:, 2].min()
gcy = (v[:, 1].min() + v[:, 1].max()) / 2
panels = [dict(name="Screen image", group="screen", explode=[0, 140, -290], center=[float(cx), float(cy), float(zf - 0.05)],
               size=[154.2, 85.9], image="screen_ui.png", strength=2.2),
          dict(name="UCG status display", group="ucg", explode=[0, 250, -300], center=[0.0, float(gcy), float(gz - 0.05)],
               size=[24.0, 12.0], image="ucg_ui.png", strength=2.0)]
print("screen front", round(zf, 2), "centre", round(cx, 2), round(cy, 2), "glass front span",
      round(front[:, 0].max() - front[:, 0].min(), 1), "x", round(front[:, 1].max() - front[:, 1].min(), 1))

# ---------------- parts to show one by one (in-use orientation) ----------------
print_keys = ["side2U", "side3U", "side1U", "cap", "handle", "bar", "dock", "ear", "spacer", "disp", "clip0",
              "pi_shelf", "pi_ups", "pi_board", "pi_lid", "pi_face", "pi_faceL", "pi_faceR", "pi_shims", "ucg"]
parts = []
for key in print_keys:
    info = M[key]
    mat = PI_M if key.startswith("pi_") and key != "pi_shims" else np.eye(4)
    parts.append(dict(key=key, label=info["label"], file=info["file"], qty=info["qty"], grams=info["grams"],
                      note=info["note"], matrix=np.asarray(mat).ravel().tolist()))

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
json.dump(dict(meshes=meshes, nodes=nodes, parts=parts, panels=panels, desk=-r.PLINTH),
          open(os.path.join(OUT, "scene.json"), "w"), indent=1)
print("total tris", tris)
