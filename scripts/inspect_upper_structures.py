import os
import glob
import trimesh
import numpy as np

OBJ_DIR = "OBJ Files"

def load_mesh(prefix):
    matches = glob.glob(os.path.join(OBJ_DIR, f"{prefix}_*.obj"))
    return trimesh.load(matches[0], process=False)

def inspect_upper_structures():
    aorta_bulb = load_mesh("MM558")
    aorta_asc = load_mesh("MM506")
    pulm = load_mesh("MM607")
    lm = load_mesh("MM557")

    print("=== UPPER STRUCTURES INSPECTION ===")
    for name, m in [("Aorta Bulb MM558", aorta_bulb), ("Ascending Aorta MM506", aorta_asc), ("Pulmonary Trunk MM607", pulm), ("Left Main MM557", lm)]:
        print(f"\n[{name}]:")
        print(f"  Verts: {len(m.vertices)}, Faces: {len(m.faces)}")
        print(f"  Connected components: {len(m.split(only_watertight=False))}")
        comps = m.split(only_watertight=False)
        for i, c in enumerate(comps):
            print(f"    Comp {i}: {len(c.vertices)} verts, {len(c.faces)} faces, bounds={np.round(c.bounds, 1).tolist()}")

    # Check relationship between Aorta Bulb MM558 and Ascending Aorta MM506
    # Do they overlap or have a seam?
    from scipy.spatial import cKDTree
    tree_asc = cKDTree(aorta_asc.vertices)
    dists_bulb_to_asc, _ = tree_asc.query(aorta_bulb.vertices)
    print(f"\nAorta Bulb MM558 -> Ascending Aorta MM506 min dist: {dists_bulb_to_asc.min():.4f} mm")
    print(f"Aorta Bulb vertices within 0.1mm of Ascending Aorta: {(dists_bulb_to_asc < 0.1).sum()} / {len(aorta_bulb.vertices)}")

    # What about Pulmonary Trunk MM607? Does it have multiple components or floating fragments?
    # What about around the valve?
    print(f"\nPulmonary Trunk components: {len(pulm.split(only_watertight=False))}")

if __name__ == "__main__":
    inspect_upper_structures()
