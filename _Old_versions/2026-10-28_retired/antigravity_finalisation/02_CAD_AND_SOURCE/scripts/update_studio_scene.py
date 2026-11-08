import os
import sys
import bpy
from mathutils import Matrix, Vector

BASE = os.path.expanduser("~/Downloads/Pi 5 HomeLab 1")
BLEND_IN = os.path.join(BASE, "rework-01", "Pi5-MiniRack_v7.2_ALL-FILES_2026-10-27", "VISUALS", "blender_option2", "Pi5_MiniRack_option2_studio.blend")
RENDERS_DIR = os.path.join(BASE, "antigravity_finalisation", "03_BLENDER_RENDERS")
os.makedirs(RENDERS_DIR, exist_ok=True)

print("Opening base studio blend file...")
bpy.ops.wm.open_mainfile(filepath=BLEND_IN)
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
    print("Cycles configured on Metal GPU.")
except Exception as e:
    print("GPU setup fallback:", e)

scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.015
scene.cycles.use_denoising = True
scene.cycles.samples = 96

# Import updated PLY meshes
ply_fp = os.path.join(RENDERS_DIR, "pi_face_final_v3.ply")
ply_sw = os.path.join(RENDERS_DIR, "ups_switch_extender_v3.ply")
ply_cable = os.path.join(RENDERS_DIR, "ups_cable_hidden_v3.ply")

print("Importing updated faceplate mesh...")
bpy.ops.wm.ply_import(filepath=ply_fp)
new_fp_obj = bpy.context.selected_objects[0]
new_fp_mesh = new_fp_obj.data
new_fp_mesh.name = "Mesh_Pi_Faceplate_Final"
bpy.data.objects.remove(new_fp_obj, do_unlink=True)

print("Importing switch extender mesh...")
bpy.ops.wm.ply_import(filepath=ply_sw)
new_sw_obj = bpy.context.selected_objects[0]
new_sw_mesh = new_sw_obj.data
new_sw_mesh.name = "Mesh_UPS_Switch_Extender"
bpy.data.objects.remove(new_sw_obj, do_unlink=True)

print("Importing hidden cable mesh...")
bpy.ops.wm.ply_import(filepath=ply_cable)
new_cable_obj = bpy.context.selected_objects[0]
new_cable_mesh = new_cable_obj.data
new_cable_mesh.name = "Mesh_UPS_Hidden_Cable"
bpy.data.objects.remove(new_cable_obj, do_unlink=True)

# Replace faceplate mesh data across all instances
petg_mat = bpy.data.materials.get("PETG dark grey")
orange_mat = bpy.data.materials.get("PLA orange")
cable_mat = bpy.data.materials.get("PLA black")

for o in list(bpy.data.objects):
    if "Pi faceplate" in o.name:
        o.data = new_fp_mesh
        if petg_mat and not o.data.materials:
            o.data.materials.append(petg_mat)
        print("Updated faceplate mesh on:", o.name)

# Helper to add object to collection
def add_to_col(col_name, mesh, name, mat, transform=None):
    col = bpy.data.collections.get(col_name)
    if not col:
        return None
    obj = bpy.data.objects.new(name, mesh)
    if mat:
        obj.data.materials.append(mat)
    if transform:
        obj.matrix_world = transform
    col.objects.link(obj)
    return obj

# Base transform of Pi unit faceplate in Rack, loaded:
base_fp = bpy.data.objects.get("Pi faceplate (one piece)")
T_base = base_fp.matrix_world.copy() if base_fp else Matrix.Identity(4)

# Add Switch Extender to collections
sw_loaded = add_to_col("Rack, loaded", new_sw_mesh, "UPS switch extender", orange_mat, T_base)
sw_pi = add_to_col("Pi unit", new_sw_mesh, "UPS switch extender (Pi unit)", orange_mat, T_base)

# In exploded views, explode forward with faceplate
T_exp = bpy.data.objects.get("Pi faceplate (one piece).001").matrix_world.copy() if bpy.data.objects.get("Pi faceplate (one piece).001") else T_base
sw_exp = add_to_col("Rack, exploded", new_sw_mesh, "UPS switch extender (exploded)", orange_mat, T_exp)

T_pi_exp = bpy.data.objects.get("Pi faceplate (one piece).003").matrix_world.copy() if bpy.data.objects.get("Pi faceplate (one piece).003") else T_base
sw_pi_exp = add_to_col("Pi unit, exploded", new_sw_mesh, "UPS switch extender (Pi exploded)", orange_mat, T_pi_exp)

# Add Cable to collections
cable_loaded = add_to_col("Rack, loaded", new_cable_mesh, "UPS hidden 12V cable", cable_mat, T_base)
cable_pi = add_to_col("Pi unit", new_cable_mesh, "UPS hidden 12V cable (Pi unit)", cable_mat, T_base)
cable_pi_exp = add_to_col("Pi unit, exploded", new_cable_mesh, "UPS hidden 12V cable (Pi exploded)", cable_mat, T_pi_exp)

# Save updated blend file
out_blend = os.path.join(RENDERS_DIR, "Pi5_MiniRack_antigravity_studio.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend, compress=True)
print("Updated blend saved to:", out_blend)
