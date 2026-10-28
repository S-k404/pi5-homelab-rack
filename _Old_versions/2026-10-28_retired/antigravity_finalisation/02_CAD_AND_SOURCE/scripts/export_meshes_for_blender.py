import os
import sys
import numpy as np
import trimesh
import cadquery as cq

BASE = os.path.dirname(os.path.abspath(__file__))
CAD_DIR = os.path.join(BASE, "antigravity_finalisation", "02_CAD_AND_SOURCE")
RENDERS_DIR = os.path.join(BASE, "antigravity_finalisation", "03_BLENDER_RENDERS")
os.makedirs(RENDERS_DIR, exist_ok=True)

def tess(shape, tol=0.08):
    s = shape.val() if hasattr(shape, "val") else shape
    vs, ts = s.tessellate(tol, 0.2)
    return trimesh.Trimesh(np.array([(p.x, p.y, p.z) for p in vs]), np.array(ts), process=True)

# 1. Faceplate
fp_step = os.path.join(CAD_DIR, "Rack_Faceplate_2U_10in_final.step")
fp_solid = cq.importers.importStep(fp_step)
fp_mesh = tess(fp_solid)
fp_mesh_path = os.path.join(RENDERS_DIR, "pi_face_final_v3.ply")
fp_mesh.export(fp_mesh_path)
print("Faceplate mesh exported to", fp_mesh_path, "bounds:", fp_mesh.bounds)

# 2. Switch extender in assembled v3 coordinates:
# Switch nub is at x=62.6, y=80.6, z=13.0
# Faceplate front face is at y=116.5
# Knob front should be at y=117.5
sw_step = os.path.join(CAD_DIR, "UPS_Switch_Extender.step")
sw_solid = cq.importers.importStep(sw_step)
sw_mesh_bed = tess(sw_solid)

# Switch extender was built centered at (0,0,0) in XY, with Y along length (-17 to +17)
# Let's orient it into v3 assembled position:
# In v3:
# X centered at 62.6
# Y runs from ~80 to ~117 (center = (80.6 + 116.5)/2 = 98.55)
# Z centered at 13.0
sw_mesh_assembled = sw_mesh_bed.copy()
# Bounding box of sw_mesh_bed:
bb = sw_mesh_bed.bounds
print("Switch extender bed bounds:", bb)
# Center x at 0, center z at 0, rear at y=80.0
# Bed bounds: x: [-7, 7], y: [-17, 21], z: [-2, 2]
cx = (bb[0][0] + bb[1][0]) / 2
cz = (bb[0][2] + bb[1][2]) / 2
# In bed coords: pocket is at min Y (-17), knob is at max Y (+21)
# In v3 coords: pocket goes to y=80.6, knob goes to y=117.5
# So shift x by 62.6 - cx, z by 13.0 - cz, y so that rear aligns with y=80.0
rear_y = bb[0][1]
front_y = bb[1][1]
dy = 80.0 - rear_y
dx = 62.6 - cx
dz = 13.0 - cz
sw_mesh_assembled.apply_translation([dx, dy, dz])

sw_mesh_path = os.path.join(RENDERS_DIR, "ups_switch_extender_v3.ply")
sw_mesh_assembled.export(sw_mesh_path)
print("Switch extender mesh exported to", sw_mesh_path, "assembled bounds:", sw_mesh_assembled.bounds)

# 3. Model the 12V DC cable running through the hidden slit
# UPS OUT: (86.6, 80.6, 13.0)
# Barrel plug extends to y = 98.0
# Cable bends right to enter hidden slit: (101.5, 113.5, 13.0)
# Cable rises vertically in slit behind solid faceplate: (101.5, 113.5, 36.9)
# Cable turns into board tray floor hole: (101.0, 98.0, 36.9)
# Cable turns towards screw terminal: (96.0, 94.0, 42.0)
cable_pts = [
    (86.6, 80.6, 13.0),
    (86.6, 96.0, 13.0),
    (100.5, 113.5, 13.0),
    (100.5, 113.5, 36.5),
    (101.0, 98.0, 37.0),
    (96.0, 94.0, 42.0)
]
cable_wire = cq.Workplane("XY").polyline(cable_pts)
# Create a circular cross-section tube
cable_path = cq.Workplane("XY").spline(cable_pts)
cable_solid = (cq.Workplane("YZ", origin=cable_pts[0])
               .circle(2.1)
               .sweep(cable_path))
cable_mesh = tess(cable_solid)
cable_mesh_path = os.path.join(RENDERS_DIR, "ups_cable_hidden_v3.ply")
cable_mesh.export(cable_mesh_path)
print("Cable mesh exported to", cable_mesh_path, "bounds:", cable_mesh.bounds)
