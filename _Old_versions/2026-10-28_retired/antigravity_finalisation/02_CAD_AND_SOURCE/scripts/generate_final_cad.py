import os
import sys
import math
import zipfile
import xml.etree.ElementTree as ET
from xml.sax.saxutils import quoteattr
import numpy as np
import trimesh
import cadquery as cq

BASE = os.path.dirname(os.path.abspath(__file__))
BUNDLE_DIR = os.path.join(BASE, "rework-01", "Pi5-MiniRack_v7.2_ALL-FILES_2026-10-27")
PI_DIR = os.path.join(BUNDLE_DIR, "4_Pi_Unit_2U")
PI_STEP = os.path.join(PI_DIR, "STEP_for_Onshape")

FINAL_DIR = os.path.join(BASE, "antigravity_finalisation")
CAD_OUT = os.path.join(FINAL_DIR, "02_CAD_AND_SOURCE")
PLATES_OUT = os.path.join(FINAL_DIR, "01_PRINT_READY_PLATES")

os.makedirs(CAD_OUT, exist_ok=True)
os.makedirs(PLATES_OUT, exist_ok=True)

# Geometry constants (v3 coordinates)
W, IW = 2.2, 113.9
CASE_X0, CASE_X1 = -W, IW + W          # -2.2 .. 116.1
CASE_Y1 = 110.0 + W                    # 112.2
GAP = 0.3
PY0 = CASE_Y1 + GAP                    # 112.5 (faceplate back face)
PY1 = PY0 + 4.0                        # 116.5 (faceplate front face)
Z0 = -8.0
U = 44.45
PANEL_W, PANEL_H = 254.0, 2 * U - 0.8  # 254 x 88.1
CX = (CASE_X0 + CASE_X1) / 2           # 56.95
PX0, PX1 = CX - PANEL_W / 2, CX + PANEL_W / 2

def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))

def rounded_slot_y(xc, zc, w, h, y0, y1, r=None):
    r = (min(w, h) / 2 - 0.01) if r is None else r
    return (cq.Workplane("XZ").center(xc, zc).rect(w, h).extrude(-(y1 - y0))
            .edges("|Y").fillet(r).translate((0, y0, 0)))

def make_faceplate_final():
    # Load original faceplate
    orig_step = os.path.join(PI_STEP, "Rack_Faceplate_2U_10in.step")
    fp = cq.importers.importStep(orig_step)
    
    # 1. UPS ON/OFF Switch opening:
    # Switch is at x=62.6, z=13.0
    sw_x, sw_z = 62.6, 13.0
    sw_slot = rounded_slot_y(sw_x, sw_z, 16.0, 11.0, PY0 - 1.0, PY1 + 1.0, r=2.5)
    sw_dish = rounded_slot_y(sw_x, sw_z, 20.0, 14.5, PY1 - 1.2, PY1 + 1.0, r=3.5)
    fp = fp.cut(sw_slot).cut(sw_dish)
    
    # 2. Hidden cable slit on the rear (inside) face of faceplate:
    # Runs vertically from UPS level (z=4) to board tray level (z=38)
    # x = 97.0 .. 106.0, depth 2.5 mm into faceplate rear (PY0 to PY0 + 2.5), leaving front 1.5 mm solid!
    cable_slit = box(97.0, 106.0, PY0 - 0.5, PY0 + 2.5, 4.0, 38.0).edges("|Y").fillet(1.5)
    fp = fp.cut(cable_slit)
    
    # Also connect cable slit horizontally into the DC-IN / OUT window so cable can slip seamlessly into the slit
    transit_notch = box(95.0, 102.0, PY0 - 0.5, PY0 + 2.5, 10.0, 20.0).edges("|Y").fillet(1.5)
    fp = fp.cut(transit_notch)
    
    return fp

def make_switch_extender():
    """Tactile switch extender print that snaps onto the Cuzor UPS switch nub
    and provides a front-panel sliding toggle button.
    Laid flat on bed for printing:
    X: width across faceplate
    Y: length through faceplate (from switch face to front knob)
    Z: thickness / height
    """
    # Main sliding shank (length ~34 mm, width 5.4 mm, height 4.0 mm)
    body = cq.Workplane("XY").box(5.4, 34.0, 4.0, centered=True)
    
    # Rear socket for switch nub (at y = -17.0)
    # Cuzor switch nub is approx 3.2 x 2.8 x 2.5 mm
    pocket = cq.Workplane("XY").box(3.8, 3.2, 3.2, centered=True).translate((0, -15.4, 0))
    body = body.cut(pocket)
    
    # Front button cap (at y = +17.0)
    cap = cq.Workplane("XY").box(14.0, 3.8, 9.2, centered=True).translate((0, 17.0 + 1.9, 0)).edges("|Y").fillet(1.2)
    
    # Tactile grip ribs on the front face of the cap
    for oz in [-2.5, 0.0, 2.5]:
        rib = cq.Workplane("XY").box(10.0, 0.8, 0.8, centered=True).translate((0, 17.0 + 3.8 + 0.2, oz))
        cap = cap.union(rib)
        
    # Internal retention / guide wing (slides behind the inside face of the faceplate)
    wing = cq.Workplane("XY").box(11.0, 2.0, 6.8, centered=True).translate((0, 17.0 - 4.5, 0)).edges("|Y").fillet(0.8)
    
    extender = body.union(cap).union(wing)
    return extender

def to_bed(shape, rots=()):
    s = shape
    for axis, ang in rots:
        s = s.rotate((0, 0, 0), axis, ang)
    bb = s.val().BoundingBox()
    return s.translate((-bb.xmin, -bb.ymin, -bb.zmin))

print("Generating final faceplate...")
fp_final = make_faceplate_final()
assert len(fp_final.solids().vals()) == 1, "Faceplate solid check failed"
print("  Faceplate valid:", fp_final.val().isValid())

print("Generating UPS switch extender...")
sw_ext = make_switch_extender()
assert len(sw_ext.solids().vals()) == 1, "Switch extender solid check failed"
print("  Switch extender valid:", sw_ext.val().isValid())

# Two-half faceplates for 220mm beds
print("Generating split faceplates for 220mm beds...")
fp_left = fp_final.intersect(box(PX0, CX, PY0 - 1, PY1 + 1, Z0 - 1, Z0 + PANEL_H + 1))
fp_right = fp_final.intersect(box(CX, PX1, PY0 - 1, PY1 + 1, Z0 - 1, Z0 + PANEL_H + 1))

# Export STEPs
print("Exporting STEP files to", CAD_OUT)
cq.exporters.export(fp_final, os.path.join(CAD_OUT, "Rack_Faceplate_2U_10in_final.step"))
cq.exporters.export(sw_ext, os.path.join(CAD_OUT, "UPS_Switch_Extender.step"))
cq.exporters.export(fp_left, os.path.join(CAD_OUT, "Rack_Faceplate_Left_final.step"))
cq.exporters.export(fp_right, os.path.join(CAD_OUT, "Rack_Faceplate_Right_final.step"))

# Export STLs
print("Exporting STLs to", CAD_OUT)
# Bed orientation: faceplate front face down on bed (rotate (1,0,0) by -90)
fp_bed = to_bed(fp_final, [((1, 0, 0), -90)])
sw_bed = to_bed(sw_ext, [])  # already flat on bed
fl_bed = to_bed(fp_left, [((1, 0, 0), -90)])
fr_bed = to_bed(fp_right, [((1, 0, 0), -90)])

cq.exporters.export(fp_bed, os.path.join(CAD_OUT, "Rack_Faceplate_2U_10in_final.stl"), tolerance=0.02, angularTolerance=0.1)
cq.exporters.export(sw_bed, os.path.join(CAD_OUT, "UPS_Switch_Extender.stl"), tolerance=0.02, angularTolerance=0.1)
cq.exporters.export(fl_bed, os.path.join(CAD_OUT, "Rack_Faceplate_Left_final.stl"), tolerance=0.02, angularTolerance=0.1)
cq.exporters.export(fr_bed, os.path.join(CAD_OUT, "Rack_Faceplate_Right_final.stl"), tolerance=0.02, angularTolerance=0.1)

print("Export completed successfully!")
