import os
import glob
import trimesh
import numpy as np

OBJ_DIR = "OBJ Files"

def load_clean_mesh(prefix, min_faces=20):
    matches = glob.glob(os.path.join(OBJ_DIR, f"{prefix}_*.obj"))
    m = trimesh.load(matches[0], process=False)
    # Split into connected components and remove tiny orphan shards
    comps = m.split(only_watertight=False)
    valid_comps = [c for c in comps if len(c.faces) >= min_faces]
    if len(valid_comps) == 0:
        valid_comps = [max(comps, key=lambda c: len(c.faces))]
    
    if len(valid_comps) > 1:
        cleaned = trimesh.util.concatenate(valid_comps)
    else:
        cleaned = valid_comps[0].copy()
    
    print(f"[{prefix}]: reduced from {len(m.faces)} faces ({len(comps)} comps) to {len(cleaned.faces)} faces ({len(valid_comps)} comps)")
    return cleaned

def test_clean_assembly():
    prefixes = ["MM474", "MM598", "MM538", "MM559", "MM560", "MM461", "MM632", "MM633", "MM456", "MM459", "MM460", "MM558", "MM506", "MM607", "MM557", "MM600"]
    for p in prefixes:
        load_clean_mesh(p, min_faces=15)

if __name__ == "__main__":
    test_clean_assembly()
