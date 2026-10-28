import os
import math
import bpy
import bmesh
from mathutils import Matrix, Vector, Euler

BASE = "~/Downloads/Pi 5 HomeLab 1"
ORIG_BLEND = os.path.join(BASE, "_Old_versions", "rework-01", "Pi5-MiniRack_v7.2_ALL-FILES_2026-10-27", "VISUALS", "blender_option2", "Pi5_MiniRack_option2_studio.blend")
RENDERS_DIR = os.path.join(BASE, "antigravity_finalisation", "03_BLENDER_RENDERS")
RACK_RENDERS_ROOT = os.path.join(BASE, "Pi 5 Mini Rack Renders")
os.makedirs(RENDERS_DIR, exist_ok=True)
os.makedirs(RACK_RENDERS_ROOT, exist_ok=True)

print("Opening clean base blend file...")
bpy.ops.wm.open_mainfile(filepath=ORIG_BLEND)
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
    print("Metal GPU fallback:", e)

scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.015
scene.cycles.use_denoising = True
scene.cycles.samples = 96
scene.view_settings.view_transform = "AgX"

# Load the updated faceplate mesh
ply_fp = os.path.join(RENDERS_DIR, "pi_face_final_v3.ply")
bpy.ops.wm.ply_import(filepath=ply_fp)
new_fp_obj = bpy.context.selected_objects[0]
new_fp_mesh = new_fp_obj.data
new_fp_mesh.name = "Mesh_Pi_Faceplate_Final"
bpy.data.objects.remove(new_fp_obj, do_unlink=True)

# -------------------------------------------------------------------------
# Materials
# -------------------------------------------------------------------------
petg_dark_grey = bpy.data.materials.get("PETG dark grey")

# Create vibrant PLA Orange (Prusa/Bambu style accent)
pla_orange = bpy.data.materials.new("PLA_Orange_Accent")
pla_orange.use_nodes = True
nodes = pla_orange.node_tree.nodes
nodes.clear()
bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
bsdf.inputs["Base Color"].default_value = (0.88, 0.22, 0.04, 1.0)
bsdf.inputs["Roughness"].default_value = 0.32
node_out = nodes.new(type="ShaderNodeOutputMaterial")
pla_orange.node_tree.links.new(bsdf.outputs["BSDF"], node_out.inputs["Surface"])

# Create Matte Black Rubber for cables and DC plug
cable_black = bpy.data.materials.new("Matte_Black_Rubber")
cable_black.use_nodes = True
nodes = cable_black.node_tree.nodes
nodes.clear()
bsdf_cb = nodes.new(type="ShaderNodeBsdfPrincipled")
bsdf_cb.inputs["Base Color"].default_value = (0.035, 0.035, 0.035, 1.0)
bsdf_cb.inputs["Roughness"].default_value = 0.45
node_out_cb = nodes.new(type="ShaderNodeOutputMaterial")
cable_black.node_tree.links.new(bsdf_cb.outputs["BSDF"], node_out_cb.inputs["Surface"])

# Create Nickel Metal for barrel jack
nickel_metal = bpy.data.materials.new("Nickel_Metal")
nickel_metal.use_nodes = True
nodes = nickel_metal.node_tree.nodes
nodes.clear()
bsdf_nm = nodes.new(type="ShaderNodeBsdfPrincipled")
bsdf_nm.inputs["Base Color"].default_value = (0.75, 0.76, 0.78, 1.0)
bsdf_nm.inputs["Metallic"].default_value = 0.95
bsdf_nm.inputs["Roughness"].default_value = 0.2
node_out_nm = nodes.new(type="ShaderNodeOutputMaterial")
nickel_metal.node_tree.links.new(bsdf_nm.outputs["BSDF"], node_out_nm.inputs["Surface"])

# Create Vibrant Green Status LED
led_mat = bpy.data.materials.new("UPS_LED_Green")
led_mat.use_nodes = True
nodes = led_mat.node_tree.nodes
nodes.clear()
node_emit = nodes.new(type="ShaderNodeEmission")
node_emit.inputs["Color"].default_value = (0.05, 0.95, 0.25, 1.0)
node_emit.inputs["Strength"].default_value = 14.0
node_out_led = nodes.new(type="ShaderNodeOutputMaterial")
led_mat.node_tree.links.new(node_emit.outputs["Emission"], node_out_led.inputs["Surface"])

# 1. Update Faceplate objects to new mesh
for o in list(bpy.data.objects):
    if "Pi faceplate" in o.name:
        o.data = new_fp_mesh
        if petg_dark_grey and not o.data.materials:
            o.data.materials.append(petg_dark_grey)

# 2. Properly seat Cuzor UPS mesh forward:
# Move mesh vertices along +Y by +29.9 mm so front face is at Y = 110.5 mm
# (sits 2 mm behind faceplate at 112.5 mm, perfectly seated inside lower chamber)
ups_mesh = bpy.data.meshes.get("Cuzor Mini UPS Pro")
if ups_mesh:
    for v in ups_mesh.vertices:
        v.co.y += 29.9
    ups_mesh.update()
    print("Seated UPS mesh forward by +29.9 mm! New Y bounds:",
          min(v.co.y for v in ups_mesh.vertices), "..", max(v.co.y for v in ups_mesh.vertices))

# 3. Create Switch Extender Slider Button (Orange PLA):
# Sits in faceplate switch bezel at X = 62.6, Z = 13.0, Y = [112.5, 116.5]
# Cap: X = [57.0, 68.2], Z = [9.8, 16.2], Y = [114.5, 116.8] (0.3mm proud for tactile actuation)
# Shank: connects to UPS switch nub at Y = 110.0
bm_sw = bmesh.new()
# Cap body
v1 = bm_sw.verts.new((57.0, 114.5, 9.8))
v2 = bm_sw.verts.new((68.2, 114.5, 9.8))
v3 = bm_sw.verts.new((68.2, 116.8, 9.8))
v4 = bm_sw.verts.new((57.0, 116.8, 9.8))
v5 = bm_sw.verts.new((57.0, 114.5, 16.2))
v6 = bm_sw.verts.new((68.2, 114.5, 16.2))
v7 = bm_sw.verts.new((68.2, 116.8, 16.2))
v8 = bm_sw.verts.new((57.0, 116.8, 16.2))
bm_sw.faces.new((v1, v2, v3, v4))
bm_sw.faces.new((v5, v8, v7, v6))
bm_sw.faces.new((v1, v5, v6, v2))
bm_sw.faces.new((v2, v6, v7, v3))
bm_sw.faces.new((v3, v7, v8, v4))
bm_sw.faces.new((v4, v8, v5, v1))

# Tactile grip ribs on front face
for rz in [11.2, 13.0, 14.8]:
    rv1 = bm_sw.verts.new((59.0, 116.8, rz - 0.35))
    rv2 = bm_sw.verts.new((66.2, 116.8, rz - 0.35))
    rv3 = bm_sw.verts.new((66.2, 117.25, rz - 0.35))
    rv4 = bm_sw.verts.new((59.0, 117.25, rz - 0.35))
    rv5 = bm_sw.verts.new((59.0, 116.8, rz + 0.35))
    rv6 = bm_sw.verts.new((66.2, 116.8, rz + 0.35))
    rv7 = bm_sw.verts.new((66.2, 117.25, rz + 0.35))
    rv8 = bm_sw.verts.new((59.0, 117.25, rz + 0.35))
    bm_sw.faces.new((rv1, rv2, rv3, rv4))
    bm_sw.faces.new((rv5, rv8, rv7, rv6))
    bm_sw.faces.new((rv1, rv5, rv6, rv2))
    bm_sw.faces.new((rv2, rv6, rv7, rv3))
    bm_sw.faces.new((rv3, rv7, rv8, rv4))
    bm_sw.faces.new((rv4, rv8, rv5, rv1))

# Shank connecting to UPS switch nub at Y = 110.0
sv1 = bm_sw.verts.new((60.0, 110.0, 11.5))
sv2 = bm_sw.verts.new((65.2, 110.0, 11.5))
sv3 = bm_sw.verts.new((65.2, 114.5, 11.5))
sv4 = bm_sw.verts.new((60.0, 114.5, 11.5))
sv5 = bm_sw.verts.new((60.0, 110.0, 14.5))
sv6 = bm_sw.verts.new((65.2, 110.0, 14.5))
sv7 = bm_sw.verts.new((65.2, 114.5, 14.5))
sv8 = bm_sw.verts.new((60.0, 114.5, 14.5))
bm_sw.faces.new((sv1, sv2, sv3, sv4))
bm_sw.faces.new((sv5, sv8, sv7, sv6))
bm_sw.faces.new((sv1, sv5, sv6, sv2))
bm_sw.faces.new((sv2, sv6, sv7, sv3))
bm_sw.faces.new((sv3, sv7, sv8, sv4))
bm_sw.faces.new((sv4, sv8, sv5, sv1))

me_sw = bpy.data.meshes.new("Mesh_UPS_Switch_Extender_Flush")
bm_sw.to_mesh(me_sw)
bm_sw.free()
me_sw.materials.append(pla_orange)

# 4. Status LED at X = 73.0, Y = 110.6, Z = 13.0
me_led = bpy.data.meshes.new("Mesh_UPS_LED")
bm_led = bmesh.new()
bmesh.ops.create_circle(bm_led, cap_ends=True, radius=1.6, segments=16)
bm_led.to_mesh(me_led)
bm_led.free()
for v in me_led.vertices:
    v.co = Vector((v.co.x + 73.0, 110.6, v.co.y + 13.0))
me_led.update()
me_led.materials.append(led_mat)

# 5. Right-angle DC Barrel Plug:
# Plug collar at jack X = 86.6, Y = 110.5, Z = 13.0
bm_plug = bmesh.new()
# Circular collar flush on jack
bmesh.ops.create_circle(bm_plug, cap_ends=True, radius=4.5, segments=16)
for v in bm_plug.verts:
    v.co = Vector((v.co.x + 86.6, 110.6, v.co.y + 13.0))
# Extrude plug body back along -Y to 107.0 (recessed behind faceplate)
ret = bmesh.ops.extrude_face_region(bm_plug, geom=bm_plug.faces[:])
for v in [ele for ele in ret['geom'] if isinstance(ele, bmesh.types.BMVert)]:
    v.co.y = 107.0

# 90-degree molded rubber elbow turning towards +X (side channel)
bmesh.ops.create_cube(bm_plug, size=9.0)
for v in bm_plug.verts[-8:]:
    v.co = Vector((v.co.x * 0.8 + 89.0, v.co.y * 0.8 + 107.0, v.co.z * 0.8 + 13.0))

me_plug = bpy.data.meshes.new("Mesh_UPS_DC_Plug")
bm_plug.to_mesh(me_plug)
bm_plug.free()
me_plug.materials.append(cable_black)

# 6. Hidden Cable Spline: Strictly Y <= 107.0 .. 109.5 behind faceplate
# Enters side channel at X = 103.5, rises to Z = 36.5, enters board tray floor cutout
cable_pts = [
    Vector((89.0, 107.0, 13.0)),
    Vector((96.0, 108.5, 13.0)),
    Vector((103.5, 109.0, 14.0)),
    Vector((103.5, 109.0, 36.5)),
    Vector((101.0, 98.0, 37.0)),
    Vector((96.0, 94.0, 42.0))
]

curve_data = bpy.data.curves.new("Hidden_Cable_Curve", type="CURVE")
curve_data.dimensions = "3D"
curve_data.bevel_depth = 1.6
curve_data.bevel_resolution = 4
polyline = curve_data.splines.new("POLY")
polyline.points.add(len(cable_pts) - 1)
for i, pt in enumerate(cable_pts):
    polyline.points[i].co = (pt.x, pt.y, pt.z, 1.0)

temp_obj = bpy.data.objects.new("TempCable", curve_data)
scene.collection.objects.link(temp_obj)
bpy.context.view_layer.objects.active = temp_obj
temp_obj.select_set(True)
bpy.ops.object.convert(target="MESH")
cable_mesh = temp_obj.data
cable_mesh.name = "Mesh_UPS_Hidden_Cable"
bpy.data.objects.remove(temp_obj, do_unlink=True)
cable_mesh.materials.append(cable_black)

# Function to add component linked to collection with reference transform
def add_component(col_name, mesh, name, mat, ref_name):
    col = bpy.data.collections.get(col_name)
    ref = bpy.data.objects.get(ref_name)
    if not col or not ref:
        return None
    obj = bpy.data.objects.new(name, mesh)
    obj.location = ref.location.copy()
    obj.rotation_euler = ref.rotation_euler.copy()
    obj.scale = ref.scale.copy()
    if mat:
        obj.active_material = mat
        if not obj.data.materials:
            obj.data.materials.append(mat)
    col.objects.link(obj)
    return obj

# Link to Pi unit
add_component("Pi unit", me_sw, "UPS Switch Extender (Pi unit)", pla_orange, "Pi faceplate (one piece).002")
add_component("Pi unit", me_led, "UPS Status LED (Pi unit)", led_mat, "Pi faceplate (one piece).002")
add_component("Pi unit", me_plug, "UPS DC Plug (Pi unit)", cable_black, "Pi faceplate (one piece).002")
add_component("Pi unit", cable_mesh, "UPS Hidden Cable (Pi unit)", cable_black, "Pi faceplate (one piece).002")

# Link to Rack loaded
add_component("Rack, loaded", me_sw, "UPS Switch Extender", pla_orange, "Pi faceplate (one piece)")
add_component("Rack, loaded", me_led, "UPS Status LED", led_mat, "Pi faceplate (one piece)")
add_component("Rack, loaded", me_plug, "UPS DC Plug", cable_black, "Pi faceplate (one piece)")
add_component("Rack, loaded", cable_mesh, "UPS Hidden Cable", cable_black, "Pi faceplate (one piece)")

# Studio lighting setup
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

# Create close-up camera for switch & hidden slit
cd_detail = bpy.data.cameras.new("11_pi_unit_switch_detail")
cam_detail = bpy.data.objects.new("11_pi_unit_switch_detail", cd_detail)
cams.objects.link(cam_detail)
cam_detail.location = Vector((-0.03, -0.26, 0.035))
cam_detail.rotation_euler = (math.radians(82), 0, math.radians(-8))
cam_detail["set"] = "Pi unit"
cam_detail["az"] = -10
cam_detail["el"] = 10
cam_detail["radius"] = 0.08

# Save the blend file
out_blend = os.path.join(RENDERS_DIR, "Pi5_MiniRack_antigravity_studio.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend, compress=True)
print("Saved blend file to:", out_blend)

# List of shots to re-render with the properly seated UPS and hidden cable:
SHOTS_TO_RENDER = [
    ("05_pi_unit_faceplate_switch_cableslit.png", "06_pi_unit", "Pi unit", 1600, 1100),
    ("11_pi_unit_switch_detail.png", "11_pi_unit_switch_detail", "Pi unit", 1600, 1100),
    ("01_rack_loaded_front.png", "01_rack_loaded_front", "Rack, loaded", 1600, 2000),
    ("03_rack_front_straight.png", "03_rack_front_straight", "Rack, loaded", 1400, 2000),
]

for out_name, cam_name, set_name, rx, ry in SHOTS_TO_RENDER:
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
    out_target = os.path.join(RENDERS_DIR, out_name)
    scene.render.filepath = out_target
    
    bpy.ops.render.render(write_still=True)
    print(f"Saved: {out_name}", flush=True)
    
    # Also copy to root "Pi 5 Mini Rack Renders"
    import shutil
    shutil.copy2(out_target, os.path.join(RACK_RENDERS_ROOT, out_name))

print("All targeted renders finished successfully!")
