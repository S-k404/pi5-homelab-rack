import bpy
import math
import os
import sys
from mathutils import Matrix, Vector

OUT_DIR = os.path.abspath("02_RENDERS/SLIM_CARGO_PROTOTYPE")
os.makedirs(OUT_DIR, exist_ok=True)
PARTS_DIR = os.path.abspath("04_DESIGN_SOURCE/10_Slim_Cargo_Rack_140mm/STL_for_printing/in_rack_coords")

bpy.ops.wm.read_factory_settings(use_empty=True)
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
for look in ('AgX - Medium High Contrast', 'Medium High Contrast'):
    try:
        scene.view_settings.look = look
        break
    except TypeError:
        pass

# Studio collection
studio = bpy.data.collections.new("Studio")
scene.collection.children.link(studio)
rack_col = bpy.data.collections.new("Slim_Rack")
scene.collection.children.link(rack_col)

# Materials
def principled(name, color, rough=0.35, metal=0.85):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value = (*color, 1.0)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    return m

mat_silver = principled("Anodized_Silver", (0.76, 0.78, 0.81), rough=0.32, metal=0.80)
mat_black = principled("Satin_Black", (0.04, 0.04, 0.05), rough=0.45, metal=0.20)

# Coordinate transform: rack (x across, y up, z depth) -> Blender (X across, Y depth, Z up)
# In rack: x = -140..140, y = -18..440, z = 0..140
# Scale 0.001 (mm to m)
T_RACK = Matrix((
    (-0.001, 0, 0, 0),
    (0, 0, 0.001, 0),
    (0, 0.001, 0, 0),
    (0, 0, 0, 1)
))

# Import STLs
for f in sorted(os.listdir(PARTS_DIR)):
    if not f.endswith(".stl"):
        continue
    filepath = os.path.join(PARTS_DIR, f)
    name = f[:-4]
    bpy.ops.wm.stl_import(filepath=filepath)
    obj = bpy.context.selected_objects[0]
    obj.name = name
    # Move to rack collection
    for c in obj.users_collection:
        c.objects.unlink(obj)
    rack_col.objects.link(obj)
    
    # Assign material
    if "cap" in name or "handle" in name or "bar" in name:
        obj.data.materials.append(mat_black)
    else:
        obj.data.materials.append(mat_silver)
        
    # Apply transform: rack -> blender
    # Note: STL coordinates are in mm: rack X (-X in blender), rack Y (+Z in blender), rack Z (+Y in blender)
    # Let's adjust rotation: -90 about X to orient Y up -> Z up
    obj.rotation_euler = (math.radians(-90), 0, math.radians(180))
    obj.scale = (0.001, 0.001, 0.001)

# Backdrop
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, -0.02))
bg = bpy.context.active_object
bg.name = "Backdrop"
studio.objects.link(bg)
scene.collection.objects.unlink(bg)
bg_mat = bpy.data.materials.new("Backdrop_Mat")
bg_mat.use_nodes = True
bg_p = next(n for n in bg_mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bg_p.inputs['Base Color'].default_value = (0.92, 0.93, 0.95, 1.0)
bg_p.inputs['Roughness'].default_value = 0.8
bg.data.materials.append(bg_mat)

# Studio Lights
lights = [
    ("Key", Vector((-1.2, -1.8, 1.6)), 280, 1.2),
    ("Fill", Vector((1.8, -1.2, 1.0)), 120, 1.8),
    ("Rim", Vector((0.2, 1.6, 1.8)), 220, 1.0),
    ("Top", Vector((0.0, -0.2, 2.2)), 160, 2.0)
]
target = Vector((0, 0, 0.21))
for lname, pos, power, size in lights:
    ld = bpy.data.lights.new(lname, 'AREA')
    ld.energy = power
    ld.size = size
    lo = bpy.data.objects.new(lname, ld)
    lo.location = pos
    lo.rotation_euler = (target - pos).to_track_quat('-Z', 'Y').to_euler()
    studio.objects.link(lo)

# Camera shots
cam_data = bpy.data.cameras.new("SlimCam")
cam_data.lens = 65
cam_obj = bpy.data.objects.new("SlimCam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

SHOTS = [
    ("01_slim_cargo_rack_isometric", Vector((-0.75, -1.25, 0.65)), target, (1600, 1800), 192),
    ("02_slim_cargo_rack_front_elevation", Vector((0.0, -1.45, 0.21)), target, (1400, 1800), 192),
    ("03_slim_cargo_rack_side_profile", Vector((-1.45, 0.0, 0.21)), target, (1400, 1800), 192),
]

for sname, cpos, ctarget, res, spp in SHOTS:
    cam_obj.location = cpos
    cam_obj.rotation_euler = (ctarget - cpos).to_track_quat('-Z', 'Y').to_euler()
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    scene.cycles.samples = spp
    out_file = os.path.join(OUT_DIR, f"{sname}.png")
    scene.render.filepath = out_file
    print(f"Rendering Slim Cargo Shot: {sname} -> {out_file}...")
    bpy.ops.render.render(write_still=True)
    print(f"Done {sname}!")

blend_out = os.path.join(OUT_DIR, "Slim_Cargo_Rack_studio.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_out)
print(f"Saved Studio Blend file -> {blend_out}")
