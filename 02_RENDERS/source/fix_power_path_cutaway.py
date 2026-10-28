"""
Fix Power Path in Pi unit and re-render 16_pi_power_path_cutaway.png:
1. Adds Brick 12 V lead connecting front of 12V brick to UPS DC-IN.
2. Ensures right-angle DC-IN plug is visible on UPS front face.
3. Links the Argon Poly+ 5 case base + Pi ports so the Pi unit is visible.
4. Adds the 12V -> 5V 5A Buck Converter module on the front-left tray anchors.
5. Adds the 5V USB-C lead connecting the Buck Converter to the Pi 5's USB-C port.
6. Re-renders 16_pi_power_path_cutaway.png with Cycles Metal GPU.
"""
import math
import os
import sys
import bpy
from mathutils import Matrix, Vector
import numpy as np

STUDIO_BLEND = "02_RENDERS/Pi5_MiniRack_FINAL_studio.blend"
bpy.ops.wm.open_mainfile(filepath=os.path.abspath(STUDIO_BLEND))
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

col_power = bpy.data.collections.get("Pi unit, power path")
col_loaded = bpy.data.collections.get("Rack, loaded")
col_pi = bpy.data.collections.get("Pi unit")

# 1. Delta matrix for brick/lead objects into power path
cradle_loaded = bpy.data.objects.get("12 V brick cradle (plate 13)")
cradle_power = bpy.data.objects.get("12 V brick cradle (plate 13).006")
dM = cradle_power.matrix_world @ cradle_loaded.matrix_world.inverted()

# Remove any old Brick 12 V lead in power path
for o in list(col_power.objects):
    if "brick 12 v lead" in o.name.lower():
        col_power.objects.unlink(o)

# Duplicate lead from loaded and apply dM
lead_loaded = bpy.data.objects.get("Brick 12 V lead")
lead_p = lead_loaded.copy()
lead_p.name = "Brick 12 V lead.power"
lead_p.data = lead_loaded.data.copy()
lead_p.matrix_world = dM @ lead_loaded.matrix_world
col_power.objects.link(lead_p)
print("Added Brick 12 V lead to power path!")

# 2. Fix DC-IN plug on UPS front face:
# The right-angle plug into UPS DC-IN on front face (Y=80.6, X=50.05, Z=28.9)
dcin = bpy.data.objects.get("Brick DC plug in the UPS DC-IN.004")
if dcin:
    # Ensure it is visible and has Fan black material
    dcin.hide_viewport = False
    dcin.hide_render = False

# 3. Add Pi 5 / Poly+ 5 case base & port shells to show Pi 5 location
for obj_name in ["Argon Poly+ 5 (stand-in, 93.5 x 64 x 30).002", "Pi 5 port shells.002", "THRML 30 mm fan.002"]:
    src = bpy.data.objects.get(obj_name)
    if src and src.name not in col_power.objects:
        col_power.objects.link(src)
        print(f"Linked {src.name} to power path!")

# 4. Helper function to create tube mesh
def make_tube(name, pts, d, mat):
    me = bpy.data.meshes.new(name)
    r = d / 2.0
    # Create simple line curve or mesh
    curve = bpy.data.curves.new(name, type='CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = r
    curve.bevel_resolution = 4
    polyline = curve.splines.new('POLY')
    polyline.points.add(len(pts) - 1)
    for i, pt in enumerate(pts):
        polyline.points[i].co = (pt[0], pt[1], pt[2], 1.0)
    ob = bpy.data.objects.new(name, curve)
    if mat:
        ob.data.materials.append(mat)
    col_power.objects.link(ob)
    return ob

# 5. Create 12V -> 5V Buck Converter module on front-left tray anchors:
# Anchors are at X = (8, 32), Y = 104, ZS = 36.9
mat_case = bpy.data.materials.get("Anodised black") or bpy.data.materials.get("Fan black")
mat_cable = bpy.data.materials.get("Cable black") or bpy.data.materials.get("Fan black")
mat_red = bpy.data.materials.get("Wire red") or bpy.data.materials.get("Fan black")
mat_usb = bpy.data.materials.get("USB 3 blue") or bpy.data.materials.get("Fan black")

# Buck converter body (aluminum extrusion enclosure: 35 x 22 x 12 mm)
bpy.ops.mesh.primitive_cube_add(size=1.0)
buck = bpy.context.active_object
buck.name = "12V-to-5V Buck Converter (5A)"
buck.scale = (26.0, 16.0, 11.0)
buck.location = (20.0, 104.0, 36.9 + 5.5)
if mat_case:
    buck.data.materials.append(mat_case)
col_power.objects.link(buck)
bpy.context.scene.collection.objects.unlink(buck)

# 12V input leads from terminal block to buck converter
make_tube("Buck_12V_IN_red", [(28.0, 96.0, 52.0), (24.0, 99.0, 48.0), (20.0, 100.0, 40.0)], 1.4, mat_red)
make_tube("Buck_12V_IN_blk", [(30.0, 96.0, 52.0), (26.0, 99.0, 48.0), (22.0, 100.0, 40.0)], 1.4, mat_cable)

# 5V USB-C output lead from buck converter to Pi 5 USB-C port:
# Pi 5 USB-C is at X ~ 32.0 (case side cutout), Y ~ 76.3, Z ~ 42.0
usbc_pts = [
    (18.0, 107.0, 40.0),
    (15.0, 108.0, 40.0),
    (10.0, 100.0, 41.0),
    (10.0, 85.0, 42.0),
    (15.0, 76.5, 42.5),
    (29.0, 76.5, 42.5),
]
make_tube("Pi5_USBC_Power_Cable", usbc_pts, 3.2, mat_cable)

# USB-C Right Angle Plug body at Pi 5 port
bpy.ops.mesh.primitive_cube_add(size=1.0)
usbc_plug = bpy.context.active_object
usbc_plug.name = "Pi5_USBC_RightAngle_Plug"
usbc_plug.scale = (6.0, 10.0, 5.0)
usbc_plug.location = (29.5, 76.5, 42.5)
if mat_case:
    usbc_plug.data.materials.append(mat_case)
col_power.objects.link(usbc_plug)
bpy.context.scene.collection.objects.unlink(usbc_plug)

print("Created 12V->5V Buck Converter, 12V tap, and Pi 5 USB-C power lead!")

# Save blend
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(STUDIO_BLEND))
print("Saved blend file!")

# Re-render 16_pi_power_path_cutaway
def show_only(target_col):
    studio = bpy.data.collections.get("Studio")
    cams = bpy.data.collections.get("Cameras")
    keep = (target_col, studio, cams)
    for lc in scene.view_layers[0].layer_collection.children:
        lc.exclude = lc.collection not in keep

show_only(col_power)
cam = bpy.data.objects.get("16_pi_power_path_cutaway")
scene.camera = cam
scene.render.resolution_x, scene.render.resolution_y = 1600, 1300
scene.render.resolution_percentage = 100
scene.cycles.samples = 192

out_path = os.path.abspath("02_RENDERS/16_pi_power_path_cutaway.png")
scene.render.filepath = out_path
print(f"Rendering 16_pi_power_path_cutaway -> {out_path}...")
bpy.ops.render.render(write_still=True)
print("Done rendering 16_pi_power_path_cutaway!")

