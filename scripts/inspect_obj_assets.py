"""
CoroVista - Stage 5B.1: BodyParts3D OBJ Asset Inventory Script
Parses all OBJ assets in 'OBJ Files', extracting geometric bounds, vertex/face counts,
anatomical taxonomy, and segment relationships.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, Any, List

OBJ_DIR = Path("OBJ Files")

def parse_filename(filename: str) -> Dict[str, str]:
    # e.g., MM420_BP51969_FMA74912_Trunk of anterior interventricular branch of left coronary artery.obj
    stem = filename[:-4] if filename.endswith(".obj") else filename
    match = re.match(r"^(MM\d+)_(BP\d+)_(FMA\d+)_(.+)$", stem)
    if match:
        return {
            "mm_id": match.group(1),
            "bp_id": match.group(2),
            "fma_id": match.group(3),
            "anatomical_name": match.group(4).strip()
        }
    return {
        "mm_id": "UNKNOWN",
        "bp_id": "UNKNOWN",
        "fma_id": "UNKNOWN",
        "anatomical_name": stem
    }

def analyze_obj_file(filepath: Path) -> Dict[str, Any]:
    meta = parse_filename(filepath.name)
    file_size = filepath.stat().st_size
    
    vertices = []
    face_count = 0
    mtllib_refs = []
    usemtl_refs = []
    has_normals = False
    has_texcoords = False
    
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("v "):
                parts = line.split()
                if len(parts) >= 4:
                    vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
            elif line.startswith("f "):
                face_count += 1
            elif line.startswith("vn "):
                has_normals = True
            elif line.startswith("vt "):
                has_texcoords = True
            elif line.startswith("mtllib "):
                mtllib_refs.append(line[7:].strip())
            elif line.startswith("usemtl "):
                usemtl_refs.append(line[7:].strip())
                
    v_count = len(vertices)
    
    if v_count > 0:
        xs = [v[0] for v in vertices]
        ys = [v[1] for v in vertices]
        zs = [v[2] for v in vertices]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        min_z, max_z = min(zs), max(zs)
        dx = max_x - min_x
        dy = max_y - min_y
        dz = max_z - min_z
        center = [round((min_x + max_x) / 2, 2), round((min_y + max_y) / 2, 2), round((min_z + max_z) / 2, 2)]
        bounds = {
            "min": [round(min_x, 2), round(min_y, 2), round(min_z, 2)],
            "max": [round(max_x, 2), round(max_y, 2), round(max_z, 2)],
            "dimensions": [round(dx, 2), round(dy, 2), round(dz, 2)],
            "center": center
        }
    else:
        bounds = None

    # Check if any mtl file exists
    mtl_exists = False
    mtl_name = filepath.with_suffix(".mtl")
    if mtl_name.exists():
        mtl_exists = True
    elif mtllib_refs:
        for m in mtllib_refs:
            if (filepath.parent / m).exists():
                mtl_exists = True
                break

    return {
        "filename": filepath.name,
        "mm_id": meta["mm_id"],
        "bp_id": meta["bp_id"],
        "fma_id": meta["fma_id"],
        "anatomical_name": meta["anatomical_name"],
        "file_size_bytes": file_size,
        "file_size_kb": round(file_size / 1024, 1),
        "vertex_count": v_count,
        "face_count": face_count,
        "has_normals": has_normals,
        "has_texcoords": has_texcoords,
        "mtllib_references": mtllib_refs,
        "has_material_file": mtl_exists,
        "bounds": bounds
    }

def main():
    files = sorted(list(OBJ_DIR.glob("*.obj")))
    print(f"Analyzing {len(files)} OBJ files...")
    
    inventory = []
    for f in files:
        data = analyze_obj_file(f)
        inventory.append(data)
        
    print("Done parsing files.")
    
    # Save raw json analysis
    out_json = Path("scripts/obj_inventory_raw.json")
    with open(out_json, "w", encoding="utf-8") as out:
        json.dump(inventory, out, indent=2)
    print(f"Saved to {out_json}")

if __name__ == "__main__":
    main()
