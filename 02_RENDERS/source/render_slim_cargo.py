"""
Build and Render the 10-inch 9U Slim Cargo Mini Rack (140 mm Depth).
Loads all 4 homelab subsystems (Pi 5, B1 dock, 7" screen, UCG-Ultra, 12V brick)
directly into the 140 mm Slim Cargo frame.
"""
import math
import os
import shutil
import sys
import bpy
from mathutils import Matrix, Vector
from bpy_extras.object_utils import world_to_camera_view
import numpy as np

STUDIO_BLEND = os.path.abspath("02_RENDERS/Pi5_MiniRack_FINAL_studio.blend")
OUT_DIR = os.path.abspath("02_RENDERS/SLIM_CARGO_PROTOTYPE")
PARTS_DIR = os.path.abspath("04_DESIGN_SOURCE/10_Slim_Cargo_Rack_140mm/STL_for_printing/in_rack_coords")
os.makedirs(OUT_DIR, exist_ok=True)

# Open master studio scene
bpy.ops.wm.open_mainfile(filepath=STUDIO_BLEND)
scene = bpy.context.scene

# Metal GPU setup
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'
    if hasattr(prefs, 'kernel_optimization_level'):
        prefs.kernel_optimization_level = 'OFF'
    (prefs.refresh_devices if hasattr(prefs, 'refresh_devices') else prefs.get_devices)()
    for dv in prefs.devices:
        dv.use = True
    scene.cycles.device = 'GPU'
except Exception as e:
    print('GPU notice:', e)

scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.015
scene.cycles.use_denoising = True
scene.view_settings.view_transform = 'AgX'

studio = bpy.data.collections.get("Studio")
cyc = bpy.data.objects.get("Backdrop")
cams = bpy.data.collections.get("Cameras")
old_rack = bpy.data.collections.get("Rack, loaded")

# Collections for Slim Cargo
slim_loaded = bpy.data.collections.new("Slim Cargo, loaded")
scene.collection.children.link(slim_loaded)
slim_empty = bpy.data.collections.new("Slim Cargo, empty")
scene.collection.children.link(slim_empty)

# Materials from master studio scene
mat_silver = bpy.data.materials.get("PLA silver")
mat_black = bpy.data.materials.get("PETG black")

if not mat_silver:
    mat_silver = bpy.data.materials.new("Slim_Silver")
    mat_silver.use_nodes = True
    p = next(n for n in mat_silver.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value = (0.76, 0.78, 0.81, 1.0)
    p.inputs['Roughness'].default_value = 0.35
    p.inputs['Metallic'].default_value = 0.80

if not mat_black:
    mat_black = bpy.data.materials.new("Slim_Black")
    mat_black.use_nodes = True
    p = next(n for n in mat_black.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value = (0.04, 0.04, 0.05, 1.0)
    p.inputs['Roughness'].default_value = 0.45
    p.inputs['Metallic'].default_value = 0.20

# Transform matrix for Slim Cargo Rack parts:
# Maps rack coordinates (mm, x across, y up, z depth) into the master Blender frame
M_SLIM = Matrix((
    (-0.001, 0, 0, 0),
    (0, 0, 0.001, -0.1287),
    (0, 0.001, 0, 0.0200),
    (0, 0, 0, 1)
))

slim_frame_objs = []
for f in sorted(os.listdir(PARTS_DIR)):
    if not f.endswith(".stl"):
        continue
    filepath = os.path.join(PARTS_DIR, f)
    name = f[:-4]
    bpy.ops.wm.stl_import(filepath=filepath)
    obj = bpy.context.selected_objects[0]
    obj.name = f"Slim_{name}"
    
    # Assign material: black cap, handles, and base bars; silver side modules
    if "cap" in name or "handle" in name or "bar" in name:
        obj.data.materials.append(mat_black)
    else:
        obj.data.materials.append(mat_silver)
        
    obj.matrix_world = M_SLIM
    
    # Relink
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    slim_loaded.objects.link(obj)
    slim_empty.objects.link(obj)
    slim_frame_objs.append(obj)

# Add unit objects from old_rack into slim_loaded.
# Skip 200 mm rack frame parts and 200 mm rack cables (which float in air behind 140 mm frame)
EXCLUDE_PREFIXES = (
    "Side module", "Cap half", "Handle", "Base bar",
    "HDMI (adapter", "USB-A -> micro-USB", "slim Cat6", "USB-A -> USB-C", "UCG-Ultra USB-C"
)
for o in old_rack.objects:
    if any(o.name.startswith(p) for p in EXCLUDE_PREFIXES):
        continue
    if o.name not in slim_loaded.objects:
        slim_loaded.objects.link(o)

print("Linked unit objects into slim_loaded:", len(slim_loaded.objects))

def show_only(col):
    keep = (col, studio, cams)
    for lc in scene.view_layers[0].layer_collection.children:
        lc.exclude = lc.collection not in keep

def place_studio(az, el, radius):
    s = max(radius / 0.33, 0.06)
    azr = math.radians(az)
    away = Vector((-math.sin(azr), math.cos(azr), 0))
    cyc.matrix_world = Matrix.Translation(away * 0.75 * s) @ Matrix.Rotation(math.atan2(-away.x, away.y), 4, "Z") @ Matrix.Scale(s, 4)
    target = Vector((0, 0, radius * 0.55))
    LIGHTS = {o.name: o for o in studio.objects if o.type == "LIGHT"}
    for nm, (daz, del_, dist, size, power) in {"Key": (-55, 42, 1.7, 1.1, 80), "Fill": (70, 18, 2.0, 1.6, 26),
                                               "Rim": (175, 55, 1.6, 0.9, 55)}.items():
        a, e = math.radians(az + daz), math.radians(del_)
        pos = target + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist * s
        if nm in LIGHTS:
            lo = LIGHTS[nm]
            lo.location = pos
            lo.rotation_euler = (target - pos).to_track_quat("-Z", "Y").to_euler()
            lo.data.size = size * s
            if lo.data.shape == "RECTANGLE":
                lo.data.size_y = size * s * 0.7
            lo.data.energy = power * s * s

def frame(cam, col, az, el, lens, fill=0.84):
    pts = [o.matrix_world @ Vector(c) for o in col.objects for c in o.bound_box]
    arr = np.array([list(p) for p in pts])
    lo, hi = arr.min(0), arr.max(0)
    ctr, radius = Vector((lo + hi) / 2), float(np.linalg.norm(hi - lo) / 2)
    azr, elr = math.radians(az), math.radians(el)
    dirv = Vector((math.sin(azr) * math.cos(elr), -math.cos(azr) * math.cos(elr), math.sin(elr)))
    cam.data.lens = lens
    cam.data.clip_start, cam.data.clip_end = radius * 0.02, radius * 60
    d = radius * 4
    rx, ry = scene.render.resolution_x, scene.render.resolution_y
    for _ in range(8):
        d = max(d, radius * 1.3)
        cam.location = ctr + dirv * d
        cam.rotation_euler = (-dirv).to_track_quat("-Z", "Y").to_euler()
        bpy.context.view_layer.update()
        try:
            co = [world_to_camera_view(scene, cam, p) for p in pts]
        except ZeroDivisionError:
            d *= 1.5
            continue
        xs, ys = [c.x for c in co], [c.y for c in co]
        span = max(max(xs) - min(xs), max(ys) - min(ys))
        cam.data.shift_x += ((min(xs) + max(xs)) / 2 - 0.5) * rx / max(rx, ry)
        cam.data.shift_y += ((min(ys) + max(ys)) / 2 - 0.5) * ry / max(rx, ry)
        d *= span / fill
    return radius

SLIM_SHOTS = [
    ("01_slim_cargo_rack_loaded_front", slim_loaded, -32, 14, 60, (1600, 2000), 192),
    ("02_slim_cargo_rack_loaded_rear", slim_loaded, 212, 16, 60, (1600, 2000), 192),
    ("03_slim_cargo_rack_side_profile", slim_loaded, -90, 0, 85, (1400, 1800), 192),
    ("04_slim_cargo_rack_empty_isometric", slim_empty, -34, 18, 60, (1600, 1800), 192),
]

for sname, col, az, el, lens, res, spp in SLIM_SHOTS:
    show_only(col)
    bpy.context.view_layer.update()
    
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    scene.cycles.samples = spp
    
    cd = bpy.data.cameras.new(sname)
    cam = bpy.data.objects.new(sname, cd)
    cams.objects.link(cam)
    scene.camera = cam
    
    radius = frame(cam, col, az, el, lens, 0.84)
    place_studio(az, el, radius)
    
    out_file = os.path.join(OUT_DIR, f"{sname}.png")
    scene.render.filepath = out_file
    print(f"Rendering Slim Cargo Shot: {sname} -> {out_file}...", flush=True)
    bpy.ops.render.render(write_still=True)
    print(f"Done {sname}!", flush=True)

# Copy 01 as primary isometric
shutil.copy2(os.path.join(OUT_DIR, "01_slim_cargo_rack_loaded_front.png"),
             os.path.join(OUT_DIR, "01_slim_cargo_rack_isometric.png"))

# Save master studio blend for Slim Cargo
show_only(slim_loaded)
bpy.context.view_layer.update()
blend_out = os.path.join(OUT_DIR, "Slim_Cargo_Rack_studio.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_out)
print("Saved Slim Cargo studio blend ->", blend_out)
print("All Slim Cargo renders finished successfully!")
