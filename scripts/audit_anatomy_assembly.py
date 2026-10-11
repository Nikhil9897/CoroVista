import os
import glob
import json
import trimesh
import numpy as np

OBJ_DIR = "OBJ Files"

def analyze_all_candidates():
    files = glob.glob(os.path.join(OBJ_DIR, "*.obj"))
    print(f"Total OBJ files in '{OBJ_DIR}': {len(files)}")

    inventory = []
    for fpath in sorted(files):
        fname = os.path.basename(fpath)
        parts = fname.replace(".obj", "").split("_", 3)
        mm_id = parts[0]
        bp_id = parts[1] if len(parts) > 1 else ""
        fma_id = parts[2] if len(parts) > 2 else ""
        anat_name = parts[3] if len(parts) > 3 else ""
        
        # Fast load with trimesh
        mesh = trimesh.load(fpath, process=False)
        b_min = mesh.bounds[0].tolist()
        b_max = mesh.bounds[1].tolist()
        dims = mesh.extents.tolist()
        center = mesh.centroid.tolist()
        is_watertight = mesh.is_watertight
        euler = mesh.euler_number

        inventory.append({
            "mm_id": mm_id,
            "bp_id": bp_id,
            "fma_id": fma_id,
            "name": anat_name,
            "filename": fname,
            "verts": len(mesh.vertices),
            "faces": len(mesh.faces),
            "bounds_min": b_min,
            "bounds_max": b_max,
            "dims": dims,
            "center": center,
            "watertight": is_watertight,
            "euler": euler,
        })

    # Group by anatomical category
    print("\n=== MYOCARDIAL / CHAMBER WALL / AURICLE / SEPTUM INVENTORY ===")
    search_keys = ["wall", "ventric", "atri", "auric", "sept", "myocard", "trunk", "aorta"]
    matching = [item for item in inventory if any(k in item['name'].lower() for k in search_keys)]
    for m in matching:
        print(f"[{m['mm_id']}] {m['name']} (verts: {m['verts']}, faces: {m['faces']}, watertight: {m['watertight']})")
        print(f"     bounds X: [{m['bounds_min'][0]:.1f}, {m['bounds_max'][0]:.1f}], Y: [{m['bounds_min'][1]:.1f}, {m['bounds_max'][1]:.1f}], Z: [{m['bounds_min'][2]:.1f}, {m['bounds_max'][2]:.1f}]")

    with open("scripts/detailed_anatomy_audit.json", "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2)

if __name__ == "__main__":
    analyze_all_candidates()
