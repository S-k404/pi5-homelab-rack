import os, sys
import cadquery as cq

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)
import slim_rack as sr

OUT_STL = os.path.abspath(os.path.join(DIR, "..", "STL_for_printing"))
P = sr.assembly()

# Export each assembled part in rack coordinates for 1:1 loading into Blender
os.makedirs(os.path.join(OUT_STL, "in_rack_coords"), exist_ok=True)
for name, part in P.items():
    cq.exporters.export(part, os.path.join(OUT_STL, "in_rack_coords", f"{name}.stl"), tolerance=0.05, angularTolerance=0.1)
print("Exported all assembled parts in rack coordinates!")

