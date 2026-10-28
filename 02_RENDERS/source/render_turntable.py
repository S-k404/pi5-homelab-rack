"""
Render 360-degree rotating turntable animation of the Pi 5 Mini Rack.
Outputs both an MP4 video (H.264) and an animated GIF for instant preview.
"""
import math
import os
import shutil
import subprocess
import sys
import bpy
from mathutils import Matrix, Vector
import numpy as np

STUDIO_BLEND = os.path.abspath("02_RENDERS/Pi5_MiniRack_FINAL_studio.blend")
OUT_DIR = os.path.abspath("02_RENDERS")
FRAMES_DIR = "/tmp/turntable_frames"
os.makedirs(FRAMES_DIR, exist_ok=True)
for f in os.listdir(FRAMES_DIR):
    if f.endswith(".png"):
        os.remove(os.path.join(FRAMES_DIR, f))

bpy.ops.wm.open_mainfile(filepath=STUDIO_BLEND)
scene = bpy.context.scene

# Set renderer to EEVEE
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1080
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100

target_col = bpy.data.collections.get("Rack, loaded")
studio = bpy.data.collections.get("Studio")
cams = bpy.data.collections.get("Cameras")

def show_only(col):
    keep = (col, studio, cams)
    for lc in scene.view_layers[0].layer_collection.children:
        lc.exclude = lc.collection not in keep

show_only(target_col)

# Find bounding box and center of target collection
pts = [o.matrix_world @ Vector(c) for o in target_col.objects for c in o.bound_box]
arr = np.array([list(p) for p in pts])
lo, hi = arr.min(0), arr.max(0)
ctr = Vector((lo + hi) / 2)
radius = float(np.linalg.norm(hi - lo) / 2)

# Create turntable camera
cam_data = bpy.data.cameras.new("Turntable_Cam")
cam_data.lens = 65
cam_data.clip_start = 0.05
cam_data.clip_end = 50.0
cam_obj = bpy.data.objects.new("Turntable_Cam", cam_data)
cams.objects.link(cam_obj)
scene.camera = cam_obj

# Camera distance & elevation
elevation_deg = 15.0
el_rad = math.radians(elevation_deg)
dist = radius * 2.85

TOTAL_FRAMES = 90  # 90 frames @ 30 fps = 3.0 seconds full 360 loop (4 deg/frame)
scene.frame_start = 1
scene.frame_end = TOTAL_FRAMES

print(f"Starting 360 turntable render: {TOTAL_FRAMES} frames...")
for f in range(1, TOTAL_FRAMES + 1):
    angle_deg = -35.0 + (f - 1) * (360.0 / TOTAL_FRAMES)
    az_rad = math.radians(angle_deg)
    
    # Position camera in orbit around ctr
    cam_x = ctr.x + dist * math.sin(az_rad) * math.cos(el_rad)
    cam_y = ctr.y - dist * math.cos(az_rad) * math.cos(el_rad)
    cam_z = ctr.z + dist * math.sin(el_rad)
    cam_obj.location = Vector((cam_x, cam_y, cam_z))
    
    # Aim camera at center
    direction = ctr - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    
    # Adjust backdrop and lights to follow camera smoothly
    cyc = bpy.data.objects.get("Backdrop")
    if cyc:
        cyc.location = ctr - Vector((math.sin(az_rad), -math.cos(az_rad), 0)) * (radius * 1.5)
        cyc.rotation_euler = (0, 0, az_rad)
    
    frame_path = os.path.join(FRAMES_DIR, f"frame_{f:04d}.png")
    scene.render.filepath = frame_path
    bpy.ops.render.render(write_still=True)
    if f % 15 == 0 or f == TOTAL_FRAMES:
        print(f"Rendered frame {f}/{TOTAL_FRAMES} ({f/TOTAL_FRAMES*100:.0f}%)", flush=True)

print("All frames rendered successfully!")

# Encode to MP4 with ffmpeg
mp4_out = os.path.join(OUT_DIR, "Pi5_MiniRack_360_Turntable.mp4")
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
print(f"Encoded MP4 video: {mp4_out}")

# Encode to GIF with palettegen for high quality
gif_out = os.path.join(OUT_DIR, "Pi5_MiniRack_360_Turntable.gif")
cmd_gif = [
    "/opt/homebrew/bin/ffmpeg", "-y",
    "-r", "30",
    "-i", os.path.join(FRAMES_DIR, "frame_%04d.png"),
    "-vf", "fps=20,scale=540:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
    gif_out
]
subprocess.run(cmd_gif, check=True)
print(f"Encoded animated GIF: {gif_out}")

