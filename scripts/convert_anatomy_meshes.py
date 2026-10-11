"""
CoroVista — Anatomical Mesh Conversion Pipeline
Converts validated BodyParts3D OBJ assets into standardized, coordinate-aligned GLB files.
Reconstructs a clean, cohesive, rounded 3D human heart with smooth silhouette,
clearly integrated great vessels, and prominently visible coronary arteries.
Preserves all source assets in 'OBJ Files/' without modification.
"""

import os
import glob
import json
import shutil
import trimesh
import numpy as np

# Refined anatomical selection: 18 licensed BodyParts3D source assets
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
            "name": "Left Main Coronary Artery",
            "role": "Root arterial trunk connecting aortic bulb to LAD/LCX bifurcation",
            "segments": [
                {"id": "MM557", "role": "Left main trunk", "bp": "BP58405", "fma": "FMA4685"}
            ]
        },
        "struct_aorta_bulb": {
            "name": "Aortic Bulb (Root)",
            "role": "Origin of coronary arteries and aortic root anchor",
            "segments": [
                {"id": "MM558", "role": "Wall of bulb of aorta", "bp": "BP51975", "fma": "FMA15098"}
            ]
        },
        "struct_aorta_ascending": {
            "name": "Ascending Aorta Proper",
            "role": "Superior aortic outflow tract orientation landmark",
            "segments": [
                {"id": "MM506", "role": "Ascending aorta proper", "bp": "BP51985", "fma": "FMA23733"}
            ]
        },
        "struct_pulmonary_trunk": {
            "name": "Pulmonary Trunk",
            "role": "Anterior outflow tract context landmark",
            "segments": [
                {"id": "MM607", "role": "Pulmonary trunk proper", "bp": "BP58392", "fma": "FMA15086"}
            ]
        },
        "struct_myocardium": {
            "name": "Ventricular Myocardium",
            "role": "Unified rounded ventricular myocardial cone (LV free wall, RV inflow, and RV outflow)",
            "segments": [
                {"id": "MM474", "role": "Free wall of left ventricle", "bp": "BP51876", "fma": "FMA84850"},
                {"id": "MM598", "role": "Wall of inflow part of right ventricle", "bp": "BP51897", "fma": "FMA84851"},
                {"id": "MM538", "role": "Wall of outflow part of right ventricle", "bp": "BP51893", "fma": "FMA84853"},
            ]
        },
        "struct_auricles": {
            "name": "Atrial Auricular Appendages",
            "role": "Rounded right and left auricles framing cardiac base and AV groove",
            "segments": [
                {"id": "MM461", "role": "Wall of right auricle proper", "bp": "BP51915", "fma": "FMA84093"},
                {"id": "MM459", "role": "Wall of left auricle", "bp": "BP51910", "fma": "FMA84087"},
            ]
        },
        "struct_septum": {
            "name": "Muscular Interventricular Septum",
            "role": "Internal muscular septal partition separating ventricles",
            "segments": [
                {"id": "MM600", "role": "Muscular part of interventricular septum", "bp": "BP51936", "fma": "FMA7134"}
            ]
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


def load_clean_component(prefix: str, min_faces: int = 15) -> trimesh.Trimesh:
    """Loads OBJ and removes disconnected orphan shards (<15 faces) while preserving genuine anatomical geometry."""
    fpath = find_obj_file(prefix)
    m = trimesh.load(fpath, process=False)
    comps = m.split(only_watertight=False)
    valid_comps = [c for c in comps if len(c.faces) >= min_faces]
    if not valid_comps:
        valid_comps = [max(comps, key=lambda c: len(c.faces))]
    if len(valid_comps) > 1:
        res = trimesh.util.concatenate(valid_comps)
    else:
        res = valid_comps[0].copy()
    return res


def convert_assets():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(FRONTEND_MODELS_DIR, exist_ok=True)

    print("=== CoroVista: Refining Cohesive 3D Heart Assembly ===")

    all_source_ids = []
    for gdata in LOCKED_SELECTION["vessels"].values():
        all_source_ids.extend([s["id"] for s in gdata["segments"]])
    for gdata in LOCKED_SELECTION["supporting"].values():
        all_source_ids.extend([s["id"] for s in gdata["segments"]])

    unique_sources = sorted(list(set(all_source_ids)))
    print(f"Total unique source OBJ assets: {len(unique_sources)} ({unique_sources})")
    assert len(all_source_ids) == len(unique_sources), f"Duplicate sources detected: {all_source_ids}"

    manifest = {
        "metadata": {
            "source_repo": "BodyParts3D",
            "license": "CC BY-SA 2.1 Japan",
            "units": "millimeters",
            "coordinate_system": "Pre-aligned BodyParts3D / DICOM Space",
            "total_selected_source_objs": len(unique_sources),
            "reconstruction_version": "2.1-cohesive-heart",
        },
        "groups": {},
        "global_bounds": {}
    }

    master_scene = trimesh.Scene()
    all_vertices = []

    def process_group(group_key: str, group_data: dict, is_vessel: bool):
        segment_meshes = []
        seg_meta_list = []

        for seg in group_data["segments"]:
            fpath = find_obj_file(seg["id"])
            # Load cleaned mesh (removes tiny floating noise fragments)
            mesh = load_clean_component(seg["id"], min_faces=15)
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

        # Concatenate and weld coincident boundary vertices for smooth silhouette
        if len(segment_meshes) > 1:
            merged_mesh = trimesh.util.concatenate(segment_meshes)
        else:
            merged_mesh = segment_meshes[0].copy()

        merged_mesh.merge_vertices(merge_tex=True, merge_norm=True)
        # Compute smooth vertex normals
        _ = merged_mesh.vertex_normals

        # Export individual GLB
        glb_path = os.path.join(OUTPUT_DIR, f"{group_key}.glb")
        with open(glb_path, "wb") as f:
            f.write(merged_mesh.export(file_type="glb"))

        # Add to master scene
        master_scene.add_geometry(merged_mesh, node_name=group_key, geom_name=group_key)

        group_meta = {
            "name": group_data["name"],
            "role": group_data.get("role", group_data.get("clinical_target", "")),
            "total_vertices": len(merged_mesh.vertices),
            "total_faces": len(merged_mesh.faces),
            "bounds_min": [float(x) for x in np.round(merged_mesh.bounds[0], 3)],
            "bounds_max": [float(x) for x in np.round(merged_mesh.bounds[1], 3)],
            "dimensions_mm": [float(x) for x in np.round(merged_mesh.extents, 3)],
            "segments": seg_meta_list
        }
        if is_vessel:
            group_meta["clinical_target"] = group_data["clinical_target"]

        manifest["groups"][group_key] = group_meta
        print(f"-> Processed {group_key:<24s}: {len(merged_mesh.vertices):5d} verts, {len(merged_mesh.faces):5d} faces ({len(segment_meshes)} segment(s))")

    # Process vessels
    for gkey, gdata in LOCKED_SELECTION["vessels"].items():
        process_group(gkey, gdata, is_vessel=True)

    # Process supporting structures
    for gkey, gdata in LOCKED_SELECTION["supporting"].items():
        process_group(gkey, gdata, is_vessel=False)

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
    print(f"\n-> Exported master scene {master_glb_path} ({len(master_glb_bytes)} bytes)")

    # Save manifest
    manifest_path = os.path.join(OUTPUT_DIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"-> Saved manifest to {manifest_path}")

    # Copy all processed models to frontend/public/models
    for fname in os.listdir(OUTPUT_DIR):
        src_f = os.path.join(OUTPUT_DIR, fname)
        if os.path.isfile(src_f):
            dst_f = os.path.join(FRONTEND_MODELS_DIR, fname)
            shutil.copy2(src_f, dst_f)
    print(f"-> Synchronized processed models to {FRONTEND_MODELS_DIR}")

    write_attribution_file(unique_sources)
    print("=== Refined Conversion Completed Successfully ===")


def write_attribution_file(unique_sources):
    rows = []
    all_structures = {}
    for gkey, gdata in LOCKED_SELECTION["vessels"].items():
        for s in gdata["segments"]:
            all_structures[s["id"]] = (gkey, gdata["name"], s["role"], s["bp"], s["fma"])
    for gkey, gdata in LOCKED_SELECTION["supporting"].items():
        for s in gdata["segments"]:
            all_structures[s["id"]] = (gkey, gdata["name"], s["role"], s["bp"], s["fma"])

    for sid in sorted(unique_sources):
        info = all_structures.get(sid, ("", sid, "", "", ""))
        rows.append(f"| `{info[0]}` | {info[1]} | {info[2]} | {info[4]} | {info[3]} | {sid} |")

    table_content = "\n".join(rows)

    attribution_text = f"""# BodyParts3D Asset Attribution & Licensing

## Data Source
The 3D anatomical models in this directory originate from **BodyParts3D**, developed and maintained by **The Database Center for Life Science (DBCLS)**, Japan.

* **Repository**: [BodyParts3D](https://lifesciencedb.jp/bp3d/)
* **License**: [Creative Commons Attribution-ShareAlike 2.1 Japan (CC BY-SA 2.1 JP)](https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en)
* **Ontology Standard**: Foundational Model of Anatomy (FMA)
* **Total Licensed Assets**: {len(unique_sources)} source OBJ meshes

## Selected Assets & Attribution Table

| Structure Group | Logical Name | Specific Segment Role | FMA ID | BodyParts3D ID | Source File Prefix |
| :--- | :--- | :--- | :--- | :--- | :--- |
{table_content}

## Transformation and Derivation Notice
* All 18 original meshes remain unmodified in `OBJ Files/`.
* The converted GLB assets strictly preserve the unified BodyParts3D millimeter coordinate space ($X, Y, Z$).
* Fragment cleaning removes disconnected orphan shards (<15 faces) while preserving all authentic anatomical openings and ostia.
* Unified ventricular myocardium (`struct_myocardium`) welds LV free wall (MM474), RV inflow (MM598), and RV outflow (MM538) into a cohesive, rounded organ silhouette with continuous surface normals.
"""
    with open(os.path.join(OUTPUT_DIR, "LICENSE_ATTRIBUTION.md"), "w", encoding="utf-8") as f:
        f.write(attribution_text)
    print("-> Wrote LICENSE_ATTRIBUTION.md")


if __name__ == "__main__":
    convert_assets()
