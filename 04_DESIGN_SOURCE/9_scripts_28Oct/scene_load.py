"""load the exported FINAL scene (export_final.py) as world-frame trimesh objects. Rack frame: x across (+x = viewer's LEFT
seen from the front), y up from the base-bar tops, z back from the front rails, mm."""
import json, os
import numpy as np
import trimesh

ASSEMBLY = ("rack", "dock", "screen", "ucg", "pi", "pi_cables")


def load(scene_dir, groups=ASSEMBLY):
    d = json.load(open(os.path.join(scene_dir, "scene.json")))
    cache, out = {}, []
    for n in d["nodes"]:
        if n["group"] not in groups:
            continue
        k = n["mesh"]
        if k not in cache:
            z = np.load(os.path.join(scene_dir, "meshes", f"{k}.npz"))
            cache[k] = trimesh.Trimesh(z[z.files[0]], z[z.files[1]], process=True) if len(z.files) >= 2 else None
        m = cache[k].copy()
        m.apply_transform(np.array(n["matrix"]).reshape(4, 4))
        out.append(dict(name=n["name"], mesh_key=k, group=n["group"], mesh=m, mat=d["meshes"][k]["mat"]))
    return out
