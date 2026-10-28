"""
Render 360-degree rotating turntable animation of the 140 mm Slim Cargo Rack.
Outputs MP4 video (H.264) and animated GIF in 02_RENDERS/SLIM_CARGO_PROTOTYPE/
"""
import math
import os
import subprocess
import sys
import bpy
from mathutils import Matrix, Vector
import numpy as np

STUDIO_BLEND = os.path.abspath("02_RENDERS/SLIM_CARGO_PROTOTYPE/Slim_Cargo_Rack_studio.blend")
OUT_DIR = os.path.abspath("02_RENDERS/SLIM_CARGO_PROTOTYPE")
FRAMES_DIR = "/tmp/slim_turntable_frames"
os.makedirs(FRAMES_DIR, exist_ok=True)
for f in os.listdir(FRAMES_DIR):
    if f.endswith(".png"):
        os.remove(os.path.join(FRAMES_DIR, f))

bpy.ops.wm.open_mainfile(filepath=STUDIO_BLEND)
scene = bpy.context.scene

scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1080
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100

target_col = bpy.data.collections.get("Slim Cargo, loaded")
studio = bpy.data.collections.get("Studio")
cams = bpy.data.collections.get("Cameras")
cyc = bpy.data.objects.get("Backdrop")

def show_only(col):
    keep = (col, studio, cams)
    for lc in scene.view_layers[0].layer_collection.children:
        lc.exclude = lc.collection not in keep

show_only(target_col)
bpy.context.view_layer.update()

# Find bounding box and center of target collection
pts = [o.matrix_world @ Vector(c) for o in target_col.objects for c in o.bound_box]
arr = np.array([list(p) for p in pts])
lo, hi = arr.min(0), arr.max(0)
ctr = Vector((lo + hi) / 2)
radius = float(np.linalg.norm(hi - lo) / 2)

cam_data = bpy.data.cameras.new("Slim_Turntable_Cam")
cam_data.lens = 65
cam_data.clip_start = 0.05
cam_data.clip_end = 50.0
cam_obj = bpy.data.objects.new("Slim_Turntable_Cam", cam_data)
cams.objects.link(cam_obj)
scene.camera = cam_obj

elevation_deg = 15.0
el_rad = math.radians(elevation_deg)
dist = radius * 2.85

def place_studio(az, el, radius):
    s = max(radius / 0.33, 0.06)
    azr = math.radians(az)
    away = Vector((-math.sin(azr), math.cos(azr), 0))
    if cyc:
        cyc.matrix_world = Matrix.Translation(away * 0.75 * s) @ Matrix.Rotation(math.atan2(-away.x, away.y), 4, "Z") @ Matrix.Scale(s, 4)
    target = Vector((0, 0, radius * 0.55))
    LIGHTS = {o.name: o for o in studio.objects if o.type == "LIGHT"}
    for nm, (daz, del_, dist_mul, size, power) in {"Key": (-55, 42, 1.7, 1.1, 80), "Fill": (70, 18, 2.0, 1.6, 26),
                                                   "Rim": (175, 55, 1.6, 0.9, 55)}.items():
        a, e = math.radians(az + daz), math.radians(del_)
        pos = target + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist_mul * s
        if nm in LIGHTS:
            lo = LIGHTS[nm]
            lo.location = pos
            lo.rotation_euler = (target - pos).to_track_quat("-Z", "Y").to_euler()
            lo.data.size = size * s
            if lo.data.shape == "RECTANGLE":
                lo.data.size_y = size * s * 0.7
            lo.data.energy = power * s * s

TOTAL_FRAMES = 90
scene.frame_start = 1
scene.frame_end = TOTAL_FRAMES

print(f"Starting Slim Cargo 360 turntable render: {TOTAL_FRAMES} frames...")
for f in range(1, TOTAL_FRAMES + 1):
    angle_deg = -35.0 + (f - 1) * (360.0 / TOTAL_FRAMES)
    az_rad = math.radians(angle_deg)
    
    cam_x = ctr.x + dist * math.sin(az_rad) * math.cos(el_rad)
    cam_y = ctr.y - dist * math.cos(az_rad) * math.cos(el_rad)
    cam_z = ctr.z + dist * math.sin(el_rad)
    cam_obj.location = Vector((cam_x, cam_y, cam_z))
    
    direction = ctr - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    
    place_studio(angle_deg, elevation_deg, radius)
    
    frame_path = os.path.join(FRAMES_DIR, f"frame_{f:04d}.png")
    scene.render.filepath = frame_path
    bpy.ops.render.render(write_still=True)
    if f % 15 == 0 or f == TOTAL_FRAMES:
        print(f"Rendered frame {f}/{TOTAL_FRAMES} ({f/TOTAL_FRAMES*100:.0f}%)", flush=True)

print("All Slim Cargo turntable frames rendered!")

# Encode MP4
mp4_out = os.path.join(OUT_DIR, "SlimCargo_Rack_360_Turntable.mp4")
cmd_mp4 = [
    "/opt/homebrew/bin/ffmpeg", "-y",
    "-r", "30",
    "-i", os.path.join(FRAMES_DIR, "frame_%04d.png"),
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-crf", "18",
    "-movflags", "+faststart",
    mp4_out
]
subprocess.run(cmd_mp4, check=True)
print(f"Encoded MP4: {mp4_out}")

# Encode GIF
gif_out = os.path.join(OUT_DIR, "SlimCargo_Rack_360_Turntable.gif")
cmd_gif = [
    "/opt/homebrew/bin/ffmpeg", "-y",
    "-r", "30",
    "-i", os.path.join(FRAMES_DIR, "frame_%04d.png"),
    "-vf", "fps=20,scale=540:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
    gif_out
]
subprocess.run(cmd_gif, check=True)
print(f"Encoded GIF: {gif_out}")
