"""Filament estimate, close to what a slicer reports: slice each print-oriented STL into 0.2 mm layers, rasterise
the layers, count the shells (perimeters in plane, top/bottom skins) as solid and the rest at the infill fraction.
Needs trimesh, scipy and pillow. Usage: python estimate_filament.py [STL_for_printing folder]"""
import os
import sys
import numpy as np
import trimesh
from scipy import ndimage

RHO = 1.24  # PLA g/cm3 (PETG 1.27)


def grams(path, walls=3, infill=0.15, line=0.45, skin=1.0, px=0.2, layer=0.2):
    m = trimesh.load(path, force="mesh")
    lo, hi = m.bounds
    zs = np.arange(lo[2] + layer / 2, hi[2], layer)
    res = np.ceil((hi[:2] - lo[:2]) / px).astype(int) + 4
    origin = lo[:2] - 2 * px
    grid = np.zeros((len(zs), res[1], res[0]), bool)
    for i, s in enumerate(m.section_multiplane(plane_origin=[0, 0, 0], plane_normal=[0, 0, 1], heights=list(zs))):
        if s is not None:
            grid[i] = np.array(s.rasterize(pitch=px, origin=origin, resolution=res, fill=True), dtype=bool)
    pad = np.pad(grid, 1)
    d_xy = ndimage.distance_transform_edt(pad, sampling=(1e6, px, px))
    d_z = ndimage.distance_transform_edt(pad, sampling=(layer, 1e6, 1e6))
    shell = pad & ((d_xy <= walls * line) | (d_z <= skin))
    return (shell.sum() + infill * (pad & ~shell).sum()) * px * px * layer / 1000 * RHO


PARTS = [  # file, qty, walls, infill
    ("Rack_SideModule_2U_Base_x2.stl", 2, 3, 0.15),
    ("Rack_SideModule_3U_x4.stl", 4, 3, 0.15),
    ("Rack_CapHalf_x2.stl", 2, 3, 0.15),
    ("Rack_Handle_x2.stl", 2, 4, 0.20),
    ("Rack_BaseBar_x3.stl", 3, 3, 0.15),
]
if __name__ == "__main__":
    d = sys.argv[1] if len(sys.argv) > 1 else "STL_for_printing"
    tot = 0
    for f, q, w, inf in PARTS:
        g = grams(os.path.join(d, f), w, inf)
        tot += g * q
        print(f"{f:34s} x{q}  {g:5.0f} g each  {g * q:5.0f} g  ({w} walls, {inf:.0%})")
    print(f"rack total {tot:.0f} g")
