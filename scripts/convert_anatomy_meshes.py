"""
CoroVista — Anatomical Mesh Conversion Pipeline
Converts selected BodyParts3D OBJ assets into standardized, coordinate-aligned GLB files.
Preserves all source assets in 'OBJ Files/' without modification.
"""

import os
import glob
import json
import shutil
import trimesh
import numpy as np

# Verified anatomical mapping for coronary artery branches and heart structures
LOCKED_SELECTION = {
    "vessels": {
        "vessel_lad": {
            "name": "Left Anterior Descending Artery (LAD)",
            "clinical_target": "LAD Stenosis",
            "segments": [
                {"id": "MM420", "role": "Proximal segment", "bp": "BP51969", "fma": "FMA74912"},
                {"id": "MM424", "role": "Mid segment", "bp": "BP51969", "fma": "FMA74912"},
                {"id": "MM425", "role": "Distal segment", "bp": "BP51969", "fma": "FMA74912"},
            ]
        },
        "vessel_lcx": {
            "name": "Left Circumflex Artery (LCX)",
            "clinical_target": "LCX Stenosis",
            "segments": [
                {"id": "MM426", "role": "Proximal segment", "bp": "BP51973", "fma": "FMA74923"},
                {"id": "MM635", "role": "Distal segment", "bp": "BP51973", "fma": "FMA74923"},
            ]
        },
        "vessel_rca": {
            "name": "Right Coronary Artery (RCA)",
            "clinical_target": "RCA Stenosis",
            "segments": [
                {"id": "MM556", "role": "Proximal segment", "bp": "BP51977", "fma": "FMA3802"},
                {"id": "MM436", "role": "Mid segment", "bp": "BP51977", "fma": "FMA3802"},
                {"id": "MM439", "role": "Distal segment", "bp": "BP51977", "fma": "FMA3802"},
            ]
        }
    },
    "supporting": {
        "struct_left_main": {
            "id": "MM557",
            "name": "Left Main Coronary Artery",
            "bp": "BP58405",
            "fma": "FMA4685",
            "role": "Root connecting aortic bulb to LAD/LCX bifurcation"
        },
        "struct_aorta_bulb": {
            "id": "MM558",
            "name": "Aortic Bulb (Root)",
            "bp": "BP51975",
            "fma": "FMA15098",
            "role": "Origin of coronary arteries"
        },
        "struct_aorta_ascending": {
            "id": "MM506",
            "name": "Ascending Aorta Proper",
            "bp": "BP51985",
            "fma": "FMA23733",
            "role": "Superior anatomical landmark"
        },
        "struct_lv_wall": {
            "id": "MM631",
            "name": "Left Ventricular Free Wall",
            "bp": "BP51876",
            "fma": "FMA84850",
            "role": "Myocardial background silhouette"
        },
        "struct_septum": {
            "id": "MM600",
            "name": "Muscular Interventricular Septum",
            "bp": "BP51936",
            "fma": "FMA7134",
            "role": "Septal myocardial background"
        },
        "struct_pulmonary_trunk": {
            "id": "MM607",
            "name": "Pulmonary Trunk",
            "bp": "BP58392",
            "fma": "FMA15086",
            "role": "Anterior outflow context landmark"
        }
    }
}

OUTPUT_DIR = os.path.join("assets", "anatomy", "bodyparts3d", "processed")
FRONTEND_MODELS_DIR = os.path.join("frontend", "public", "models")


def find_obj_file(prefix: str, obj_dir: str = "OBJ Files") -> str:
    matches = glob.glob(os.path.join(obj_dir, f"{prefix}_*.obj"))
    if not matches:
        raise FileNotFoundError(f"Source OBJ file matching prefix '{prefix}' not found in {obj_dir}")
    return matches[0]


def convert_assets():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(FRONTEND_MODELS_DIR, exist_ok=True)

    print("=== CoroVista: Converting BodyParts3D Meshes ===")

    manifest = {
        "metadata": {
            "source_repo": "BodyParts3D",
            "license": "CC BY-SA 2.1 Japan",
            "units": "millimeters",
            "coordinate_system": "Pre-aligned BodyParts3D / DICOM Space",
            "total_selected_source_objs": 14,
        },
        "groups": {},
        "global_bounds": {}
    }

    master_scene = trimesh.Scene()
    all_vertices = []

    # Process primary coronary vessel groups
    for group_key, group_data in LOCKED_SELECTION["vessels"].items():
        segment_meshes = []
        seg_meta_list = []

        for seg in group_data["segments"]:
            fpath = find_obj_file(seg["id"])
            mesh = trimesh.load(fpath, process=False)
            segment_meshes.append(mesh)
            all_vertices.append(mesh.vertices)

            seg_meta_list.append({
                "id": seg["id"],
                "role": seg["role"],
                "bp_id": seg["bp"],
                "fma_id": seg["fma"],
                "source_file": os.path.basename(fpath),
                "vertices": len(mesh.vertices),
                "faces": len(mesh.faces),
                "bounds_min": [float(x) for x in np.round(mesh.bounds[0], 3)],
                "bounds_max": [float(x) for x in np.round(mesh.bounds[1], 3)]
            })

        # Concatenate segments into unified continuous vessel
        merged_mesh = trimesh.util.concatenate(segment_meshes)
        # Ensure vertex normals are computed
        _ = merged_mesh.vertex_normals

        # Export individual vessel GLB
        vessel_glb_path = os.path.join(OUTPUT_DIR, f"{group_key}.glb")
        with open(vessel_glb_path, "wb") as f:
            f.write(merged_mesh.export(file_type="glb"))

        # Add to master scene
        master_scene.add_geometry(merged_mesh, node_name=group_key, geom_name=group_key)

        manifest["groups"][group_key] = {
            "name": group_data["name"],
            "clinical_target": group_data["clinical_target"],
            "total_vertices": len(merged_mesh.vertices),
            "total_faces": len(merged_mesh.faces),
            "bounds_min": [float(x) for x in np.round(merged_mesh.bounds[0], 3)],
            "bounds_max": [float(x) for x in np.round(merged_mesh.bounds[1], 3)],
            "dimensions_mm": [float(x) for x in np.round(merged_mesh.extents, 3)],
            "segments": seg_meta_list
        }
        print(f"-> Processed {group_key}: {len(merged_mesh.vertices)} verts, {len(merged_mesh.faces)} faces")

    # Process supporting structures
    for group_key, struct_data in LOCKED_SELECTION["supporting"].items():
        fpath = find_obj_file(struct_data["id"])
        mesh = trimesh.load(fpath, process=False)
        all_vertices.append(mesh.vertices)
        _ = mesh.vertex_normals

        # Export individual structure GLB
        struct_glb_path = os.path.join(OUTPUT_DIR, f"{group_key}.glb")
        with open(struct_glb_path, "wb") as f:
            f.write(mesh.export(file_type="glb"))

        # Add to master scene
        master_scene.add_geometry(mesh, node_name=group_key, geom_name=group_key)

        manifest["groups"][group_key] = {
            "id": struct_data["id"],
            "name": struct_data["name"],
            "role": struct_data["role"],
            "bp_id": struct_data["bp"],
            "fma_id": struct_data["fma"],
            "source_file": os.path.basename(fpath),
            "total_vertices": len(mesh.vertices),
            "total_faces": len(mesh.faces),
            "bounds_min": [float(x) for x in np.round(mesh.bounds[0], 3)],
            "bounds_max": [float(x) for x in np.round(mesh.bounds[1], 3)],
            "dimensions_mm": [float(x) for x in np.round(mesh.extents, 3)]
        }
        print(f"-> Processed {group_key}: {len(mesh.vertices)} verts, {len(mesh.faces)} faces")

    # Global bounding statistics
    all_v_stack = np.vstack(all_vertices)
    global_min = all_v_stack.min(axis=0)
    global_max = all_v_stack.max(axis=0)
    global_center = (global_min + global_max) / 2.0
    global_extents = global_max - global_min

    manifest["global_bounds"] = {
        "min": [float(x) for x in np.round(global_min, 3)],
        "max": [float(x) for x in np.round(global_max, 3)],
        "center": [float(x) for x in np.round(global_center, 3)],
        "dimensions_mm": [float(x) for x in np.round(global_extents, 3)]
    }

    # Export master scene GLB
    master_glb_path = os.path.join(OUTPUT_DIR, "corovista_heart.glb")
    master_glb_bytes = master_scene.export(file_type="glb")
    with open(master_glb_path, "wb") as f:
        f.write(master_glb_bytes)
    print(f"-> Exported master scene {master_glb_path} ({len(master_glb_bytes)} bytes)")

    # Save manifest
    manifest_path = os.path.join(OUTPUT_DIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"-> Saved manifest to {manifest_path}")

    # Copy to frontend/public/models
    for fname in os.listdir(OUTPUT_DIR):
        src_f = os.path.join(OUTPUT_DIR, fname)
        if os.path.isfile(src_f):
            dst_f = os.path.join(FRONTEND_MODELS_DIR, fname)
            shutil.copy2(src_f, dst_f)
    print(f"-> Synchronized processed models to {FRONTEND_MODELS_DIR}")

    # Write attribution file
    attribution_text = """# BodyParts3D Asset Attribution & Licensing

## Data Source
The 3D anatomical models in this directory originate from **BodyParts3D**, developed and maintained by **The Database Center for Life Science (DBCLS)**, Japan.

* **Repository**: [BodyParts3D](https://lifesciencedb.jp/bp3d/)
* **License**: [Creative Commons Attribution-ShareAlike 2.1 Japan (CC BY-SA 2.1 JP)](https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en)
* **Ontology Standard**: Foundational Model of Anatomy (FMA)

## Selected Assets & Attribution Table

| Structure Key | Anatomical Structure | FMA ID | BodyParts3D ID | Source File(s) | Role in CoroVista |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `vessel_lad` | Left anterior descending branch | FMA74912 | BP51969 | MM420, MM424, MM425 | Primary target for LAD stenosis probability visualization |
| `vessel_lcx` | Circumflex branch of LCA | FMA74923 | BP51973 | MM426, MM635 | Primary target for LCX stenosis probability visualization |
| `vessel_rca` | Right coronary artery trunk | FMA3802 | BP51977 | MM556, MM436, MM439 | Primary target for RCA stenosis probability visualization |
| `struct_left_main` | Stem of left coronary artery | FMA4685 | BP58405 | MM557 | Root connecting aortic bulb to LAD/LCX bifurcation |
| `struct_aorta_bulb` | Wall of bulb of aorta | FMA15098 | BP51975 | MM558 | Coronary sinus take-off anchor |
| `struct_aorta_ascending` | Ascending aorta proper | FMA23733 | BP51985 | MM506 | Superior aortic orientation context |
| `struct_lv_wall` | Left ventricle, free wall | FMA84850 | BP51876 | MM631 | Semi-transparent background myocardial silhouette |
| `struct_septum` | Muscular interventricular septum | FMA7134 | BP51936 | MM600 | Septal background myocardial silhouette |
| `struct_pulmonary_trunk` | Pulmonary trunk | FMA15086 | BP58392 | MM607 | Anterior outflow tract context |

## Transformation and Derivation Notice
* All 14 original meshes remain unmodified in `OBJ Files/`.
* The converted GLB assets preserve the exact, unified DICOM/BodyParts3D coordinate space and millimeter scale.
* Sub-segments of vessel trunks (MM420/424/425, MM426/635, MM556/436/439) were combined into continuous vascular meshes for unified shader rendering.
"""
    with open(os.path.join(OUTPUT_DIR, "LICENSE_ATTRIBUTION.md"), "w", encoding="utf-8") as f:
        f.write(attribution_text)
    print("-> Wrote LICENSE_ATTRIBUTION.md")
    print("=== Conversion Completed Successfully ===")


if __name__ == "__main__":
    convert_assets()
