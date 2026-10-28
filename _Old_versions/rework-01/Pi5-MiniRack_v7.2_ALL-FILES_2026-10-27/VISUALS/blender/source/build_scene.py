"""
Build the Pi 5 Mini Rack v7.2 studio scene in Blender from export_scene.py's output and render it with Cycles.
Usage: blender -b -P build_scene.py -- <scene dir> <out dir> [final|preview] [shot,shot,...]
Writes <out dir>/*.png (whole rack and units), <out dir>/parts/*.png (one per printed part) and
<out dir>/Pi5_MiniRack_v7.2_studio.blend (every set as a collection, one camera per shot).
"""
import json
import math
import os
import sys
import bpy
import numpy as np
from mathutils import Matrix, Vector
from bpy_extras.object_utils import world_to_camera_view

argv = sys.argv[sys.argv.index("--") + 1:]
SCENE_DIR, OUT = argv[0], argv[1]
PREVIEW = len(argv) > 2 and argv[2] == "preview"
ONLY = set(argv[3].split(",")) if len(argv) > 3 and argv[3] else None
os.makedirs(os.path.join(OUT, "parts"), exist_ok=True)
data = json.load(open(os.path.join(SCENE_DIR, "scene.json")))

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
C = Matrix(((-1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))   # rack (x across, y up, z back) -> Blender, front faces -Y
S = Matrix.Scale(0.001, 4)                                             # mm -> m


def mat4(flat):
    return Matrix([flat[0:4], flat[4:8], flat[8:12], flat[12:16]])


def srgb(hexstr):
    c = [int(hexstr[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)


# ---------------- materials ----------------
def principled(name, color, rough=0.5, metal=0.0, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*color, 1.0)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if coat:
        p.inputs["Coat Weight"].default_value = coat
    return m


MATS = {
    "pla_silver": principled("PLA silver", srgb("#aab0b8"), 0.3, 0.72),
    "pla_grey": principled("PLA grey", srgb("#9ba1aa"), 0.42, 0.45),
    "pla_black": principled("PLA black", srgb("#111214"), 0.58),
    "pla_dark": principled("PLA dark grey", srgb("#43474e"), 0.55),
    "pla_darker": principled("PLA charcoal", srgb("#303338"), 0.55),
    "pla_orange": principled("PLA orange", srgb("#e8833a"), 0.5),
    "petg_dark": principled("PETG dark grey", srgb("#3b3f46"), 0.3),
    "petg_darker": principled("PETG charcoal", srgb("#2c2f34"), 0.3),
    "petg_lid": principled("PETG lid", srgb("#34373d"), 0.3),
    "dev_b1": principled("NIIMBOT B1", srgb("#e7e9ec"), 0.4),
    "dev_screen": principled("Screen glass", srgb("#08090b"), 0.08, coat=1.0),
    "dev_ucg": principled("UCG-Ultra white", srgb("#eef0f2"), 0.42),
    "dev_pcb_green": principled("PCB green", srgb("#1f6b3a"), 0.35),
    "dev_pcb_black": principled("PCB black", srgb("#17191c"), 0.35),
    "dev_alu_black": principled("Anodised black", srgb("#1b1d20"), 0.32, 0.85),
    "dev_ups": principled("UPS body", srgb("#1f2a38"), 0.45),
}


def pi_board_material():
    """the Pi 5 model is one solid: green below the top of the PCB, metal-grey for everything mounted on it"""
    m = principled("Pi 5 board", srgb("#1f6b3a"), 0.35)
    nt = m.node_tree
    pcb = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    metal = nt.nodes.new("ShaderNodeBsdfPrincipled")
    metal.inputs["Base Color"].default_value = (*srgb("#b8bcc2"), 1.0)
    metal.inputs["Metallic"].default_value = 0.9
    metal.inputs["Roughness"].default_value = 0.32
    tc, sep, gt, mix = (nt.nodes.new(t) for t in ("ShaderNodeTexCoord", "ShaderNodeSeparateXYZ", "ShaderNodeMath", "ShaderNodeMixShader"))
    gt.operation, gt.inputs[1].default_value = "GREATER_THAN", 43.7      # PCB top: 41.9 (bosses) + 1.6 mm, case frame
    nt.links.new(tc.outputs["Object"], sep.inputs["Vector"])
    nt.links.new(sep.outputs["Z"], gt.inputs[0])
    nt.links.new(gt.outputs["Value"], mix.inputs["Fac"])
    nt.links.new(pcb.outputs["BSDF"], mix.inputs[1])
    nt.links.new(metal.outputs["BSDF"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
    return m


MATS["dev_pcb_green"] = pi_board_material()


def emission(name, image_path, strength):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(image_path)
    tex.image.pack()
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = strength
    nt.links.new(tex.outputs["Color"], em.inputs["Color"])
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    return m


# ---------------- meshes ----------------
MESHES = {}


def mesh_data(key):
    if key in MESHES:
        return MESHES[key]
    z = np.load(os.path.join(SCENE_DIR, "meshes", f"{key}.npz"))
    v, f = z["v"].astype(np.float32), z["f"].astype(np.int32)
    me = bpy.data.meshes.new(data["meshes"][key]["label"])
    me.vertices.add(len(v))
    me.vertices.foreach_set("co", v.ravel())
    me.loops.add(f.size)
    me.loops.foreach_set("vertex_index", f.ravel())
    me.polygons.add(len(f))
    me.polygons.foreach_set("loop_start", np.arange(0, f.size, 3, dtype=np.int32))
    me.update(calc_edges=True)
    me.validate()
    if not data["meshes"][key]["bevel"]:
        me.shade_smooth()                       # creases were split on export, so smooth shading keeps them crisp
    me.materials.append(MATS[data["meshes"][key]["mat"]])
    MESHES[key] = me
    return me


def new_collection(name):
    col = bpy.data.collections.new(name)
    scene.collection.children.link(col)
    return col


def add_object(col, key, name, world):
    ob = bpy.data.objects.new(name, mesh_data(key))
    ob.matrix_world = world
    bev = data["meshes"][key]["bevel"]
    if bev:
        md = ob.modifiers.new("Rounded edges", "BEVEL")
        md.width, md.segments, md.limit_method = bev, 5, "ANGLE"
    col.objects.link(ob)
    return ob


def add_panel(col, p, explode_t):
    w, h = p["size"]
    me = bpy.data.meshes.new(p["name"])
    me.from_pydata([(-w / 2, -h / 2, 0), (w / 2, -h / 2, 0), (w / 2, h / 2, 0), (-w / 2, h / 2, 0)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for li, (u, vv) in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[li].uv = (u, vv)
    me.materials.append(emission(p["name"], os.path.join(SCENE_DIR, p["image"]), p["strength"]))
    ob = bpy.data.objects.new(p["name"], me)
    cx, cy, cz = p["center"]
    ex = Vector(p["explode"]) * explode_t
    # the panel faces -z in the rack frame (out of the front); its local +x must read left-to-right from the front
    face = Matrix(((-1, 0, 0, 0), (0, 1, 0, 0), (0, 0, -1, 0), (0, 0, 0, 1)))
    ob.matrix_world = S @ C @ Matrix.Translation(Vector((cx, cy, cz)) + ex) @ face
    col.objects.link(ob)
    return ob


def ground(col):
    """move a set so it's centred on the origin and stands on z = 0"""
    obs = list(col.objects)
    pts = np.array([list(o.matrix_world @ Vector(c)) for o in obs for c in o.bound_box])
    lo, hi = pts.min(0), pts.max(0)
    off = Matrix.Translation(Vector((-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2])))
    for o in obs:
        o.matrix_world = off @ o.matrix_world


SETS = {}


def make_set(name, groups, t=0.0, pi_components=True):
    col = new_collection(name)
    for n in data["nodes"]:
        if n["group"] not in groups or (not pi_components and n["mesh"].startswith("c_")):
            continue
        world = S @ C @ Matrix.Translation(Vector(n["explode"]) * t) @ mat4(n["matrix"])
        add_object(col, n["mesh"], n["name"], world)
    for p in data["panels"]:
        if p["group"] in groups:
            add_panel(col, p, t)
    ground(col)
    SETS[name] = col
    return col


ALL = ("rack", "dock", "screen", "ucg", "pi")
make_set("Rack, loaded", ALL)
make_set("Rack, exploded", ALL, 1.0)
make_set("Rack, empty", ("rack",))
make_set("Pi unit", ("pi",))
make_set("Pi unit, exploded", ("pi",), 1.0)
make_set("B1 dock", ("dock",))
make_set("Screen module", ("screen",))
make_set("UCG-Ultra shelf", ("ucg",))
for p in data["parts"]:
    col = new_collection(f"Part · {p['label']}")
    add_object(col, p["key"], p["label"], S @ C @ mat4(p["matrix"]))
    ground(col)
    SETS[f"part:{p['key']}"] = col

# ---------------- studio: cyclorama, three soft lights, dim grey world ----------------
studio = new_collection("Studio")
prof = [(-4.0, 0.0), (0.0, 0.0)] + [(1.2 * math.sin(a), 1.2 - 1.2 * math.cos(a)) for a in np.linspace(0.08, math.pi / 2, 14)] + [(1.2, 4.0)]
Wc = 8.0
verts = [(x, y, z) for y, z in prof for x in (-Wc / 2, Wc / 2)]
faces = [(2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2) for i in range(len(prof) - 1)]
me = bpy.data.meshes.new("Backdrop")
me.from_pydata(verts, [], faces)
me.shade_smooth()
me.materials.append(principled("Backdrop", srgb("#a7abb1"), 0.85))
cyc = bpy.data.objects.new("Backdrop", me)
studio.objects.link(cyc)
LIGHTS = {}
for nm, shape in (("Key", "RECTANGLE"), ("Fill", "RECTANGLE"), ("Rim", "DISK")):
    ld = bpy.data.lights.new(nm, "AREA")
    ld.shape = shape
    lo = bpy.data.objects.new(nm, ld)
    studio.objects.link(lo)
    LIGHTS[nm] = lo
world = bpy.data.worlds.new("Studio grey")
world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
hdri = os.path.join(os.path.dirname(bpy.app.binary_path), "..", "Resources", bpy.app.version_string[:3], "datafiles",
                    "studiolights", "world", "studio.exr")
if os.path.exists(hdri):                     # Blender's own studio HDRI: soft reflections on the silver and the glass
    env = world.node_tree.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(hdri)
    env.image.pack()
    world.node_tree.links.new(env.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 0.22
else:
    bg.inputs["Color"].default_value = (*srgb("#9aa0a8"), 1.0)
    bg.inputs["Strength"].default_value = 0.08
scene.world = world

# ---------------- render settings ----------------
scene.render.engine = "CYCLES"
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "METAL"
    if hasattr(prefs, "kernel_optimization_level"):
        prefs.kernel_optimization_level = "OFF"    # background kernel specialisation crashed the Metal driver (5.2.3)
    (prefs.refresh_devices if hasattr(prefs, "refresh_devices") else prefs.get_devices)()
    for dv in prefs.devices:
        dv.use = True
    scene.cycles.device = "GPU"
except Exception as e:                       # noqa: BLE001
    print("GPU setup failed, using CPU:", e)
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.015
scene.cycles.use_denoising = True
scene.view_settings.view_transform = "AgX"
for look in ("AgX - Medium High Contrast", "Medium High Contrast"):
    try:
        scene.view_settings.look = look
        break
    except TypeError:
        pass
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"


def show_only(col):
    keep = (col, studio, bpy.data.collections.get("Cameras"))   # cameras must stay in the view layer to be evaluated
    for lc in scene.view_layers[0].layer_collection.children:
        lc.exclude = lc.collection not in keep


def place_studio(az, el, radius):
    """scale the backdrop and lights to the subject, and turn them with the camera"""
    s = max(radius / 0.33, 0.06)
    azr = math.radians(az)
    away = Vector((-math.sin(azr), math.cos(azr), 0))           # from the subject, away from the camera
    cyc.matrix_world = Matrix.Translation(away * 0.75 * s) @ Matrix.Rotation(math.atan2(-away.x, away.y), 4, "Z") @ Matrix.Scale(s, 4)
    target = Vector((0, 0, radius * 0.55))
    for nm, (daz, del_, dist, size, power) in {"Key": (-55, 42, 1.7, 1.1, 80), "Fill": (70, 18, 2.0, 1.6, 26),
                                               "Rim": (175, 55, 1.6, 0.9, 55)}.items():
        a, e = math.radians(az + daz), math.radians(del_)
        pos = target + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist * s
        lo = LIGHTS[nm]
        lo.location = pos
        lo.rotation_euler = (target - pos).to_track_quat("-Z", "Y").to_euler()
        lo.data.size = size * s
        if lo.data.shape == "RECTANGLE":
            lo.data.size_y = size * s * 0.7
        lo.data.energy = power * s * s


def frame(cam, col, az, el, lens, fill):
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
        d = max(d, radius * 1.3)                    # keep the camera outside the subject's bounding sphere
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


SHOTS = [  # name, set, azimuth (0 = front, + = to the right), elevation, lens mm, resolution, samples
    ("01_rack_loaded_front", "Rack, loaded", -32, 14, 60, (1600, 2000), 256),
    ("02_rack_loaded_back", "Rack, loaded", 212, 16, 60, (1600, 2000), 256),
    ("03_rack_front_straight", "Rack, loaded", 0, 5, 85, (1400, 2000), 192),
    ("04_rack_exploded", "Rack, exploded", -36, 17, 55, (1800, 2200), 256),
    ("05_rack_empty", "Rack, empty", -30, 18, 60, (1500, 1900), 192),
    ("06_pi_unit", "Pi unit", -32, 24, 70, (1600, 1100), 192),
    ("07_pi_unit_back_ports", "Pi unit", 205, 20, 70, (1600, 1100), 192),
    ("08_pi_unit_exploded", "Pi unit, exploded", -34, 22, 60, (1600, 1500), 192),
    ("09_b1_dock", "B1 dock", -28, 18, 70, (1600, 1200), 192),
    ("10_screen_module", "Screen module", -24, 12, 70, (1600, 1200), 192),
    ("11_screen_module_back", "Screen module", 200, 22, 70, (1600, 1200), 192),
    ("12_ucg_shelf", "UCG-Ultra shelf", -30, 24, 70, (1600, 1000), 192),
    ("13_ucg_shelf_back", "UCG-Ultra shelf", 210, 28, 70, (1600, 1000), 192),
] + [(f"part_{p['key']}", f"part:{p['key']}", 35 if p["key"].startswith("side") else -35, 24, 70, (1000, 1000), 128)
     for p in data["parts"]]                 # side modules from the inside, so the ribs, posts and inserts show

cams = new_collection("Cameras")
for name, set_name, az, el, lens, res, spp in SHOTS:
    col = SETS[set_name]
    show_only(col)
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.resolution_percentage = 30 if PREVIEW else 100
    scene.cycles.samples = 24 if PREVIEW else spp
    cd = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, cd)
    cams.objects.link(cam)
    print("framing", name, flush=True)
    radius = frame(cam, col, az, el, lens, 0.84)
    place_studio(az, el, radius)
    cam["set"], cam["az"], cam["el"], cam["radius"] = set_name, az, el, radius
    if ONLY and name not in ONLY:
        continue
    scene.camera = cam
    sub = "parts" if name.startswith("part_") else ""
    scene.render.filepath = os.path.join(OUT, sub, name.replace("part_", "") + ".png")
    if not PREVIEW and os.path.exists(scene.render.filepath):
        print("kept", name, flush=True)          # already rendered: lets a crashed run resume
        continue
    bpy.ops.render.render(write_still=True)
    print("rendered", name, flush=True)

# leave the .blend on the hero shot, with the other sets switched off in the outliner
hero = bpy.data.objects["01_rack_loaded_front"]
show_only(SETS["Rack, loaded"])
for lc in scene.view_layers[0].layer_collection.children:
    if lc.collection is cams:
        lc.exclude = False
place_studio(hero["az"], hero["el"], hero["radius"])
scene.camera = hero
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 1600, 2000, 100
scene.cycles.samples = 256
if not PREVIEW:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Pi5_MiniRack_v7.2_studio.blend"), compress=True)
    print("saved .blend")
