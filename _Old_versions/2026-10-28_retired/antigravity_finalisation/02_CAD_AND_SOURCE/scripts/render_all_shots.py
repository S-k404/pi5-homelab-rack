import os
import math
import sys
import bpy
from mathutils import Matrix, Vector

BASE = os.path.expanduser("~/Downloads/Pi 5 HomeLab 1")
BLEND_FILE = os.path.join(BASE, "antigravity_finalisation", "03_BLENDER_RENDERS", "Pi5_MiniRack_antigravity_studio.blend")
OUT_DIR = os.path.join(BASE, "antigravity_finalisation", "03_BLENDER_RENDERS")
os.makedirs(OUT_DIR, exist_ok=True)

print("Opening blend file...")
bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)
scene = bpy.context.scene

# Configure Cycles Metal GPU
scene.render.engine = "CYCLES"
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "METAL"
    if hasattr(prefs, "kernel_optimization_level"):
        prefs.kernel_optimization_level = "OFF"
    (prefs.refresh_devices if hasattr(prefs, "refresh_devices") else prefs.get_devices)()
    for dv in prefs.devices:
        dv.use = True
    scene.cycles.device = "GPU"
    print("Cycles on Metal GPU initialized.")
except Exception as e:
    print("Metal fallback:", e)

scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.015
scene.cycles.use_denoising = True
scene.cycles.samples = 96
scene.view_settings.view_transform = "AgX"

cyc = bpy.data.objects.get("Backdrop")
LIGHTS = {nm: bpy.data.objects.get(nm) for nm in ("Key", "Fill", "Rim")}
studio = bpy.data.collections.get("Studio")
cams = bpy.data.collections.get("Cameras")

def place_studio(az, el, radius):
    s = max(radius / 0.33, 0.06)
    azr = math.radians(az)
    away = Vector((-math.sin(azr), math.cos(azr), 0))
    if cyc:
        cyc.matrix_world = Matrix.Translation(away * 0.75 * s) @ Matrix.Rotation(math.atan2(-away.x, away.y), 4, "Z") @ Matrix.Scale(s, 4)
    target = Vector((0, 0, radius * 0.55))
    for nm, (daz, del_, dist, size, power) in {"Key": (-55, 42, 1.7, 1.1, 80), "Fill": (70, 18, 2.0, 1.6, 26),
                                               "Rim": (175, 55, 1.6, 0.9, 55)}.items():
        lo = LIGHTS.get(nm)
        if not lo:
            continue
        a, e = math.radians(az + daz), math.radians(del_)
        pos = target + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist * s
        lo.location = pos
        lo.rotation_euler = (target - pos).to_track_quat("-Z", "Y").to_euler()
        lo.data.size = size * s
        if lo.data.shape == "RECTANGLE":
            lo.data.size_y = size * s * 0.7
        lo.data.energy = power * s * s

def show_only(col_name):
    target_col = bpy.data.collections.get(col_name)
    keep = (target_col, studio, cams)
    for lc in scene.view_layers[0].layer_collection.children:
        lc.exclude = lc.collection not in keep

# Define render shots: (output_name, camera_name, set_collection, res_x, res_y)
SHOTS = [
    ("01_rack_loaded_front.png", "01_rack_loaded_front", "Rack, loaded", 1600, 2000),
    ("02_rack_loaded_back.png", "02_rack_loaded_back", "Rack, loaded", 1600, 2000),
    ("03_rack_front_straight.png", "03_rack_front_straight", "Rack, loaded", 1400, 2000),
    ("04_rack_exploded.png", "04_rack_exploded", "Rack, exploded", 1800, 2200),
    ("05_pi_unit_faceplate_switch_cableslit.png", "06_pi_unit", "Pi unit", 1600, 1100),
    ("06_pi_unit_exploded.png", "08_pi_unit_exploded", "Pi unit, exploded", 1600, 1500),
    ("07_pi_unit_lid_off.png", "15_pi_unit_lid_off_active_cooler", "Pi unit, lid off", 1600, 1100),
    ("08_b1_dock.png", "09_b1_dock", "B1 dock", 1600, 1200),
    ("09_screen_module.png", "10_screen_module", "Screen module", 1600, 1200),
    ("10_ucg_mount.png", "12_ucg_mount_option2", "UCG-Ultra shelf", 1600, 1000),
]

# Create close-up camera for switch & hidden slit
cd_detail = bpy.data.cameras.new("11_pi_unit_switch_detail")
cam_detail = bpy.data.objects.new("11_pi_unit_switch_detail", cd_detail)
cams.objects.link(cam_detail)
# Focus closely on the switch opening and cable slit of Pi unit
cam_detail.location = Vector((-0.03, -0.26, 0.035))
cam_detail.rotation_euler = (math.radians(82), 0, math.radians(-8))
cam_detail["set"] = "Pi unit"
cam_detail["az"] = -10
cam_detail["el"] = 10
cam_detail["radius"] = 0.08
SHOTS.append(("11_pi_unit_switch_detail.png", "11_pi_unit_switch_detail", "Pi unit", 1600, 1100))

for out_name, cam_name, set_name, rx, ry in SHOTS:
    cam_obj = bpy.data.objects.get(cam_name)
    if not cam_obj:
        print(f"Skipping {out_name}: camera {cam_name} not found")
        continue
    
    print(f"Rendering {out_name} with camera {cam_name} ({rx}x{ry})...", flush=True)
    show_only(set_name)
    az = cam_obj.get("az", 0)
    el = cam_obj.get("el", 15)
    radius = cam_obj.get("radius", 0.3)
    place_studio(az, el, radius)
    
    scene.camera = cam_obj
    scene.render.resolution_x = rx
    scene.render.resolution_y = ry
    scene.render.resolution_percentage = 100
    scene.render.filepath = os.path.join(OUT_DIR, out_name)
    
    bpy.ops.render.render(write_still=True)
    print(f"Saved: {out_name}", flush=True)

# Also copy top renders to root "Pi 5 Mini Rack Renders" for immediate visibility
RACK_RENDERS_ROOT = os.path.join(BASE, "Pi 5 Mini Rack Renders")
os.makedirs(RACK_RENDERS_ROOT, exist_ok=True)
for out_name, _, _, _, _ in SHOTS:
    src_f = os.path.join(OUT_DIR, out_name)
    if os.path.exists(src_f):
        import shutil
        shutil.copy2(src_f, os.path.join(RACK_RENDERS_ROOT, out_name))

print("All renders completed successfully!")
