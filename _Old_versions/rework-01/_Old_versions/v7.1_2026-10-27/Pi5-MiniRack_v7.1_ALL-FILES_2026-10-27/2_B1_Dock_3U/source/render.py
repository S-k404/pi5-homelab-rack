"""Shaded preview renders with matplotlib (no CAD viewer needed). x across, y up, z back (front faces the camera)."""
import numpy as np
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def mesh(shape, tol=0.4, max_edge=8.0):
    s = shape.val() if hasattr(shape, "val") else shape
    vs, ts = s.tessellate(tol, 0.3)
    v, t = np.array([(p.x, p.y, p.z) for p in vs]), np.array(ts)
    v, t = trimesh.remesh.subdivide_to_size(v, t, max_edge=max_edge)   # small faces sort better
    return v, t


def render(parts, path, elev, azim, title, lims):
    fig = plt.figure(figsize=(9, 9), dpi=130)
    ax = fig.add_subplot(111, projection="3d")
    tris, cols = [], []
    light = np.array([0.45, 0.55, 0.7]); light /= np.linalg.norm(light)
    for shp, color in parts:
        v, t = mesh(shp)
        P = v[:, [0, 2, 1]].copy()
        P[:, 1] = -P[:, 1]                       # rack front faces the camera
        tri = P[t]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        n /= (np.linalg.norm(n, axis=1, keepdims=True) + 1e-9)
        shade = 0.45 + 0.55 * np.clip(np.abs(n @ light), 0, 1)
        base = np.array(matplotlib.colors.to_rgb(color))
        tris.append(tri)
        cols.append(np.clip(base[None, :] * shade[:, None], 0, 1))
    pc = Poly3DCollection(np.concatenate(tris), facecolors=np.concatenate(cols), edgecolors="none")
    ax.add_collection3d(pc)
    (x0, x1), (z0, z1), (y0, y1) = lims
    ax.set_xlim(x0, x1); ax.set_ylim(-z1, -z0); ax.set_zlim(y0, y1)
    ax.set_box_aspect([x1 - x0, z1 - z0, y1 - y0])
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_title(title, fontsize=12)
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close(fig)
