import os
import glob
import trimesh
import numpy as np

OBJ_DIR = "OBJ Files"

def load_mesh(prefix):
    matches = glob.glob(os.path.join(OBJ_DIR, f"{prefix}_*.obj"))
    return trimesh.load(matches[0], process=False)

def inspect_each_structure():
    prefixes = [
        "MM474", # LV
        "MM598", # RV inflow
        "MM538", # RV outflow
        "MM559", # RA ant
        "MM560", # RA lat
        "MM461", # RA auricle
        "MM632", # LA ant
        "MM633", # LA post
        "MM456", # LA lat
        "MM459", # LA auricle
        "MM460", # LA sup
        "MM558", # Aorta bulb
        "MM506", # Asc aorta
        "MM607", # Pulm trunk
        "MM600", # Septum
    ]
    for p in prefixes:
        m = load_mesh(p)
        print(f"[{p}] {m.metadata.get('name', p)}:")
        print(f"  Verts: {len(m.vertices)}, Faces: {len(m.faces)}, Bounds: X[{m.bounds[0][0]:.1f}, {m.bounds[1][0]:.1f}], Y[{m.bounds[0][1]:.1f}, {m.bounds[1][1]:.1f}], Z[{m.bounds[0][2]:.1f}, {m.bounds[1][2]:.1f}]")
        print(f"  Extents: {np.round(m.extents, 1)}")

if __name__ == "__main__":
    inspect_each_structure()
