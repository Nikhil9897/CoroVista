import os
import glob
import json
import shutil
import trimesh
import numpy as np

OBJ_DIR = "OBJ Files"

def load_clean_mesh(prefix, min_faces=15):
    matches = glob.glob(os.path.join(OBJ_DIR, f"{prefix}_*.obj"))
    if not matches:
        raise FileNotFoundError(f"Missing {prefix}")
    m = trimesh.load(matches[0], process=False)
    comps = m.split(only_watertight=False)
    valid = [c for c in comps if len(c.faces) >= min_faces]
    if not valid:
        valid = [max(comps, key=lambda c: len(c.faces))]
    if len(valid) > 1:
        res = trimesh.util.concatenate(valid)
    else:
        res = valid[0].copy()
    return res

def test_pipeline():
    # 1. Vessels
    lad_parts = [load_clean_mesh("MM420"), load_clean_mesh("MM424"), load_clean_mesh("MM425")]
    vessel_lad = trimesh.util.concatenate(lad_parts)
    vessel_lad.merge_vertices(merge_tex=True, merge_norm=True)
    _ = vessel_lad.vertex_normals

    lcx_parts = [load_clean_mesh("MM426"), load_clean_mesh("MM635")]
    vessel_lcx = trimesh.util.concatenate(lcx_parts)
    vessel_lcx.merge_vertices(merge_tex=True, merge_norm=True)
    _ = vessel_lcx.vertex_normals

    rca_parts = [load_clean_mesh("MM556"), load_clean_mesh("MM436"), load_clean_mesh("MM439")]
    vessel_rca = trimesh.util.concatenate(rca_parts)
    vessel_rca.merge_vertices(merge_tex=True, merge_norm=True)
    _ = vessel_rca.vertex_normals

    struct_left_main = load_clean_mesh("MM557")
    struct_left_main.merge_vertices(merge_tex=True, merge_norm=True)
    _ = struct_left_main.vertex_normals

    # 2. Great vessels (cleaned of floating shards, preserving genuine openings)
    struct_aorta_bulb = load_clean_mesh("MM558")
    _ = struct_aorta_bulb.vertex_normals

    struct_aorta_ascending = load_clean_mesh("MM506")
    _ = struct_aorta_ascending.vertex_normals

    struct_pulmonary_trunk = load_clean_mesh("MM607")
    _ = struct_pulmonary_trunk.vertex_normals

    # 3. Unified Ventricular Myocardium (LV + RV inflow + RV outflow)
    lv = load_clean_mesh("MM474")
    rv_in = load_clean_mesh("MM598")
    rv_out = load_clean_mesh("MM538")
    struct_myocardium = trimesh.util.concatenate([lv, rv_in, rv_out])
    struct_myocardium.merge_vertices(merge_tex=True, merge_norm=True)
    _ = struct_myocardium.vertex_normals

    # 4. Auricular context (Right auricle MM461 + Left auricle MM459)
    ra_aur = load_clean_mesh("MM461")
    la_aur = load_clean_mesh("MM459")
    struct_auricles = trimesh.util.concatenate([ra_aur, la_aur])
    struct_auricles.merge_vertices(merge_tex=True, merge_norm=True)
    _ = struct_auricles.vertex_normals

    # 5. Internal septum
    struct_septum = load_clean_mesh("MM600")
    _ = struct_septum.vertex_normals

    # Build scene
    scene = trimesh.Scene()
    geoms = {
        "vessel_lad": vessel_lad,
        "vessel_lcx": vessel_lcx,
        "vessel_rca": vessel_rca,
        "struct_left_main": struct_left_main,
        "struct_aorta_bulb": struct_aorta_bulb,
        "struct_aorta_ascending": struct_aorta_ascending,
        "struct_pulmonary_trunk": struct_pulmonary_trunk,
        "struct_myocardium": struct_myocardium,
        "struct_auricles": struct_auricles,
        "struct_septum": struct_septum,
    }

    all_v = []
    for k, g in geoms.items():
        scene.add_geometry(g, node_name=k, geom_name=k)
        all_v.append(g.vertices)
        print(f"[{k}]: {len(g.vertices)} verts, {len(g.faces)} faces")

    combined = np.vstack(all_v)
    g_min = combined.min(axis=0)
    g_max = combined.max(axis=0)
    center = (g_min + g_max) / 2.0
    extents = g_max - g_min
    print(f"\nCentroid: {np.round(center, 2)}")
    print(f"Dimensions: {np.round(extents, 2)}")

    glb_bytes = scene.export(file_type="glb")
    print(f"GLB export size: {len(glb_bytes)} bytes")

if __name__ == "__main__":
    test_pipeline()
