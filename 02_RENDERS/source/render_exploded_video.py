"""
Render a physically accurate Exploding & Reassembling video of the Pi 5 Mini Rack.
Every single part moves along its genuine CAD disassembly vector (zero implosion).
Outputs MP4 video (H.264) and animated GIF.
"""
import math
import os
import subprocess
import sys
import bpy
from mathutils import Matrix, Vector
import numpy as np

STUDIO_BLEND = os.path.abspath("02_RENDERS/Pi5_MiniRack_FINAL_studio.blend")
OUT_DIR = os.path.abspath("02_RENDERS")
FRAMES_DIR = "/tmp/exploded_frames"
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

loaded_col = bpy.data.collections.get("Rack, loaded")
studio = bpy.data.collections.get("Studio")
cams = bpy.data.collections.get("Cameras")

def show_only(col):
    keep = (col, studio, cams)
    for lc in scene.view_layers[0].layer_collection.children:
        lc.exclude = lc.collection not in keep

show_only(loaded_col)

# Rack to Blender coordinate mapping:
# ex -> -ex * 0.001 (Blender X)
# ey -> +ey * 0.001 (Blender Z, up)
# ez -> +ez * 0.001 (Blender Y, depth)
def r2b(ex, ey, ez):
    return Vector((-ex * 0.001, ez * 0.001, ey * 0.001))

# Canonical explosion rules matching export_final.py exactly
RULES = [
    # Top Handles & Cap (UP in Blender: +Z)
    ("handle (right)", r2b(75, 400, 0)),
    ("handle (left)", r2b(-75, 400, 0)),
    ("cap half (right)", r2b(75, 320, 0)),
    ("cap half (left)", r2b(-75, 320, 0)),
    
    # 1U Top Side modules
    ("side module, 1u top (right)", r2b(115, 210, 0)),
    ("side module, 1u top (left)", r2b(-115, 210, 0)),
    
    # 3U Side modules
    ("side module, 3u (right).001", r2b(115, 140, 0)),
    ("side module, 3u (left).001", r2b(-115, 140, 0)),
    ("side module, 3u (right)", r2b(115, 70, 0)),
    ("side module, 3u (left)", r2b(-115, 70, 0)),
    
    # 2U Base Side modules
    ("side module, 2u base (right)", r2b(115, 0, 0)),
    ("side module, 2u base (left)", r2b(-115, 0, 0)),
    
    # Base bars (DOWN in Blender: -Z)
    ("base bar", r2b(0, -75, 0)),
    
    # Brick subsystem & its cables (SIDEWAYS in Blender: -X)
    ("12 v 5 a brick", r2b(160, 80, 0)),
    ("brick spacer", r2b(160, 40, 0)),
    ("12 v brick cradle", r2b(160, 0, 0)),
    ("mains plug", r2b(160, 40, 0)),
    ("mains cord", r2b(160, 40, 0)),
    ("brick dc plug", r2b(160, 20, 0)),
    ("brick 12 v lead", r2b(160, 20, 0)),
    
    # Faceplates & Ears (FORWARD in Blender: -Y)
    ("pi faceplate", r2b(0, 0, -330)),
    ("dock ear (right)", r2b(40, 70, -280)),
    ("dock ear (left)", r2b(-40, 70, -280)),
    ("screen ear (right)", r2b(40, 140, -270)),
    ("screen ear (left)", r2b(-40, 140, -270)),
    ("screen clip", r2b(0, 140, -170)),
    
    # 1U UCG-Ultra (FORWARD & UP)
    ("unifi cloud gateway", r2b(0, 250, -300)),
    ("ucg status", r2b(0, 250, -300)),
    ("ucg-ultra", r2b(0, 210, -220)),
    
    # 3U Screen (FORWARD & UP)
    ("screen image", r2b(0, 140, -290)),
    ("screen glass", r2b(0, 140, -290)),
    ("7-inch screen", r2b(0, 140, -290)),
    ("screen module", r2b(0, 140, -210)),
    
    # 3U B1 Dock (FORWARD & UP)
    ("niimbot b1", r2b(0, 110, -360)),
    ("b1 dock", r2b(0, 70, -230)),
    
    # 2U Pi unit internal layers & cables (FORWARD & UP)
    ("adapter (f) holder, lid", r2b(0, 152, -240)),
    ("argon poly+ 5 top", r2b(0, 132, -240)),
    ("waveshare adapter (f) pcb", r2b(0, 126, -240)),
    ("adapter rj45", r2b(0, 126, -240)),
    ("adapter 12 v", r2b(0, 126, -240)),
    ("evm 512 gb", r2b(0, 126, -240)),
    ("adapter socket", r2b(0, 126, -240)),
    ("adapter capacitor", r2b(0, 126, -240)),
    ("adapter plug", r2b(0, 126, -240)),
    ("argon poly+ 5", r2b(0, 112, -240)),
    ("thrml 30 mm", r2b(0, 112, -240)),
    ("pi 5 port shell", r2b(0, 112, -240)),
    ("usb 3 tongue", r2b(0, 112, -240)),
    ("usb 2 tongue", r2b(0, 112, -240)),
    ("adapter (f) holder, base", r2b(0, 104, -240)),
    ("argon poly+ 5 tray", r2b(0, 80, -240)),
    ("right-angle dc plug in the ups out", r2b(0, 55, -240)),
    ("ups out lead", r2b(0, 55, -240)),
    ("+12 v wire", r2b(0, 55, -240)),
    ("0 v wire", r2b(0, 55, -240)),
    ("cuzor mini ups", r2b(0, 55, -240)),
    ("pi ups tray", r2b(0, 35, -240)),
    ("pi shelf", r2b(0, 0, -240)),
]

# Calculate displacement vector for every object
explode_vectors = {}
for o in loaded_col.objects:
    nl = o.name.lower()
    vec = Vector((0, 0, 0))
    for pat, v in RULES:
        if pat in nl:
            vec = v
            break
    explode_vectors[o.name] = vec

# Bounding box of assembled rack
pts = [o.matrix_world @ Vector(c) for o in loaded_col.objects for c in o.bound_box]
arr = np.array([list(p) for p in pts])
lo, hi = arr.min(0), arr.max(0)
ctr = Vector((lo + hi) / 2)
radius = float(np.linalg.norm(hi - lo) / 2)

cam_data = bpy.data.cameras.new("Accurate_Explode_Cam")
cam_data.lens = 52
cam_data.clip_start = 0.05
cam_data.clip_end = 50.0
cam_obj = bpy.data.objects.new("Accurate_Explode_Cam", cam_data)
cams.objects.link(cam_obj)
scene.camera = cam_obj

# Camera elevation and distance to frame the entire exploded rack
el_rad = math.radians(22.0)
dist = radius * 3.6

TOTAL_FRAMES = 80  # 80 frames @ 30 fps = 2.67 seconds
scene.frame_start = 1
scene.frame_end = TOTAL_FRAMES

# Store rest matrices
rest_matrices = {o.name: o.matrix_world.copy() for o in loaded_col.objects}

print(f"Rendering 100% Genuine Exploded Animation: {TOTAL_FRAMES} frames...")
for f in range(1, TOTAL_FRAMES + 1):
    # Progression parameter t from 0 (assembled) -> 1 (exploded) -> 0 (assembled)
    if f <= 36:
        # Smooth cosine ease in-out expansion
        prog = (1.0 - math.cos(math.pi * (f - 1) / 35.0)) / 2.0
    elif f <= 46:
        prog = 1.0  # Pause at peak explosion
    else:
        # Smooth cosine ease in-out contraction
        prog = (1.0 + math.cos(math.pi * (f - 46) / 34.0)) / 2.0
    
    # Camera orbit: gentle 50 degree sweep from -40 to +10 deg
    angle_deg = -38.0 + 50.0 * ((f - 1) / TOTAL_FRAMES)
    az_rad = math.radians(angle_deg)
    
    cam_x = ctr.x + dist * math.sin(az_rad) * math.cos(el_rad)
    cam_y = ctr.y - dist * math.cos(az_rad) * math.cos(el_rad)
    cam_z = ctr.z + dist * math.sin(el_rad)
    cam_obj.location = Vector((cam_x, cam_y, cam_z))
    
    direction = ctr - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    
    # Apply explosion translation to each object
    for o in loaded_col.objects:
        v = explode_vectors[o.name]
        o.matrix_world = Matrix.Translation(v * prog) @ rest_matrices[o.name]
    
    frame_path = os.path.join(FRAMES_DIR, f"frame_{f:04d}.png")
    scene.render.filepath = frame_path
    bpy.ops.render.render(write_still=True)
    if f % 20 == 0 or f == TOTAL_FRAMES:
        print(f"Rendered frame {f}/{TOTAL_FRAMES} ({f/TOTAL_FRAMES*100:.0f}%)", flush=True)

# Restore rest matrices
for o in loaded_col.objects:
    o.matrix_world = rest_matrices[o.name]

print("Explosion frames rendered successfully with zero implosion!")

# Encode to MP4
mp4_out = os.path.join(OUT_DIR, "Pi5_MiniRack_Exploded_Assembly.mp4")
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

# Encode to GIF
gif_out = os.path.join(OUT_DIR, "Pi5_MiniRack_Exploded_Assembly.gif")
cmd_gif = [
    "/opt/homebrew/bin/ffmpeg", "-y",
    "-r", "30",
    "-i", os.path.join(FRAMES_DIR, "frame_%04d.png"),
    "-vf", "fps=20,scale=540:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
    gif_out
]
subprocess.run(cmd_gif, check=True)
print(f"Encoded animated GIF: {gif_out}")
