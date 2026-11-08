"""
Blender render of the adapter (F) wall frame, hung on a wall, with the adapter modelled part by part.
Run: Blender -b -P render_wall_frame.py -- <out folder>
Reads <out>/render_meshes/*.stl (export_render_meshes.py); writes <out>/renders/*.png and <out>/WallFrame_F_scene.blend.
The adapter is simple shapes at the drawing's positions, not Waveshare's real model.
"""
import os
import sys
import math
import bpy
from mathutils import Vector

OUT = sys.argv[sys.argv.index("--") + 1]
MESH = os.path.join(OUT, "render_meshes")
REN = os.path.join(OUT, "renders")
os.makedirs(REN, exist_ok=True)
MM = 0.001

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene


def mat(name, rgb, rough=0.5, metal=0.0, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*rgb, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if coat:
        p.inputs["Coat Weight"].default_value = coat
    return m


MATS = {
    "petg": mat("PETG black", (0.018, 0.018, 0.02), 0.42),
    "pcb": mat("solder mask", (0.008, 0.008, 0.009), 0.3, coat=0.3),
    "steel": mat("steel", (0.78, 0.78, 0.78), 0.28, 1.0),
    "gold": mat("gold", (1.0, 0.74, 0.32), 0.25, 1.0),
    "green": mat("terminal green", (0.10, 0.55, 0.22), 0.5),
    "white": mat("connector cream", (0.86, 0.82, 0.72), 0.6),
    "ferrite": mat("ferrite black", (0.03, 0.03, 0.03), 0.6),
    "alu": mat("capacitor can", (0.72, 0.72, 0.75), 0.35, 0.8),
    "ssd": mat("SSD", (0.015, 0.02, 0.018), 0.45),
    "wall": mat("wall paint", (0.80, 0.78, 0.74), 0.9),
}

# everything is modelled with z out of the wall; this empty stands the frame up (frame y -> up, frame z -> towards us)
root = bpy.data.objects.new("frame (frame coords, mm)", None)
sc.collection.objects.link(root)
root.rotation_euler = (math.radians(90), 0, 0)
root.scale = (MM, MM, MM)


def load(fname, m):
    bpy.ops.wm.stl_import(filepath=os.path.join(MESH, fname))
    o = bpy.context.selected_objects[0]
    o.data.materials.append(m)
    bpy.ops.object.shade_auto_smooth(angle=math.radians(30))
    o.parent = root
    return o


box = load("frame_box.stl", MATS["petg"])
front = load("frame_front.stl", MATS["petg"])
board = [load(f, MATS[f[len("board_"):-4]]) for f in sorted(os.listdir(MESH)) if f.startswith("board_")]

# the wall: frame z = 0 is the wall face -> Blender y = 0
bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0.05, 0.0002, 0.03), rotation=(math.radians(90), 0, 0))
wall = bpy.context.object
wall.data.materials.append(MATS["wall"])

target = bpy.data.objects.new("target", None)
sc.collection.objects.link(target)


def area(name, loc_mm, energy, size):
    bpy.ops.object.light_add(type="AREA", location=Vector(loc_mm) * MM)
    l = bpy.context.object
    l.name = name
    l.data.energy, l.data.size = energy, size
    c = l.constraints.new("TRACK_TO")
    c.target = target
    return l


area("key", (-180, -380, 320), 9, 0.30)
area("fill", (320, -260, 40), 3, 0.40)
area("rim", (60, -60, 420), 2, 0.25)
back = area("back (back view only)", (-120, 320, 260), 9, 0.4)
back.hide_render = True
sc.world = bpy.data.worlds.new("w")
sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.08

cam_data = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_data)
sc.collection.objects.link(cam)
sc.camera = cam
track = cam.constraints.new("TRACK_TO")
track.target = target

sc.render.engine = "CYCLES"
sc.cycles.samples = 128
sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1600, 1100
sc.view_settings.view_transform = "AgX"

CENTRE = (49.4, -14.0, 26.25)       # Blender mm: frame centre x, out of the wall, up


def shot(name, cam_mm, tgt_mm=CENTRE, lens=60, explode=0.0, show_wall=True):
    cam.location = Vector(cam_mm) * MM
    target.location = Vector(tgt_mm) * MM
    cam_data.lens = lens
    for o in board:
        o.location = (0, 0, explode * 0.45)
    front.location = (0, 0, explode)
    wall.hide_render = not show_wall
    back.hide_render = show_wall
    sc.render.filepath = os.path.join(REN, name + ".png")
    bpy.ops.render.render(write_still=True)


shot("1_on_the_wall", (49.4, -420, 26.25), lens=50)
shot("2_ports_side_from_below", (-150, -250, -70), lens=55)
shot("3_terminal_side_from_above", (230, -240, 150), lens=55)
shot("4_exploded", (-110, -330, 200), (49.4, -40, 26.25), lens=50, explode=60.0)
shot("5_back_keyholes", (49.4, 330, 60), (49.4, -10, 26.25), lens=50, show_wall=False)

# leave the scene assembled and save it so it can be opened and turned round in Blender
for o in board:
    o.location = (0, 0, 0)
front.location = (0, 0, 0)
wall.hide_render = False
cam.location = Vector((-150, -250, -70)) * MM
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "WallFrame_F_scene.blend"))
