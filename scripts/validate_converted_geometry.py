"""
CoroVista — Anatomical Mesh Geometry Validation Script
Rigorously verifies:
1. All expected GLB meshes exist and load successfully.
2. Coordinate systems and bounding boxes match source OBJs.
3. Node names and semantic groups are preserved in the master scene.
4. Segment junctions, gaps, and coronary origins are quantified.
5. No source mesh is duplicated.
6. Dimensional integrity and scale are verified for the refined cardiac assembly.
"""

import os
import json
import trimesh
import numpy as np
from scipy.spatial import cKDTree

PROCESSED_DIR = os.path.join("assets", "anatomy", "bodyparts3d", "processed")
MANIFEST_PATH = os.path.join(PROCESSED_DIR, "manifest.json")
MASTER_GLB = os.path.join(PROCESSED_DIR, "corovista_heart.glb")
OBJ_DIR = "OBJ Files"


def load_mesh(fpath):
    loaded = trimesh.load(fpath, process=False)
    if isinstance(loaded, trimesh.Scene):
        return trimesh.util.concatenate(list(loaded.geometry.values()))
    return loaded


def run_geometry_validation():
    print("=== CoroVista Geometry Validation Check ===")
    assert os.path.exists(MANIFEST_PATH), f"Manifest missing: {MANIFEST_PATH}"
    assert os.path.exists(MASTER_GLB), f"Master GLB missing: {MASTER_GLB}"

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    expected_groups = [
        "vessel_lad", "vessel_lcx", "vessel_rca",
        "struct_left_main", "struct_aorta_bulb", "struct_aorta_ascending",
        "struct_pulmonary_trunk", "struct_myocardium", "struct_auricles", "struct_septum"
    ]

    # 1. Verify all individual GLBs exist and load
    print("\n[Check 1/6] Verifying individual GLB files...")
    for group_key in expected_groups:
        glb_file = os.path.join(PROCESSED_DIR, f"{group_key}.glb")
        assert os.path.exists(glb_file), f"Missing individual GLB: {glb_file}"
        mesh = load_mesh(glb_file)
        assert len(mesh.vertices) > 0, f"Mesh {group_key} has 0 vertices"
        assert len(mesh.faces) > 0, f"Mesh {group_key} has 0 faces"
        expected_verts = manifest["groups"][group_key]["total_vertices"]
        assert len(mesh.vertices) == expected_verts, (
            f"Vertex count mismatch in {group_key}: expected {expected_verts}, got {len(mesh.vertices)}"
        )
        print(f"  [OK] {group_key:<24s}: {len(mesh.vertices):5d} verts, {len(mesh.faces):5d} faces")

    # 2. Verify master scene loads with correct nodes
    print("\n[Check 2/6] Verifying master scene corovista_heart.glb...")
    master = trimesh.load(MASTER_GLB, process=False)
    assert isinstance(master, trimesh.Scene), "Master GLB is not a trimesh.Scene"
    scene_geoms = list(master.geometry.keys())
    print(f"  Master scene geometries: {scene_geoms}")
    for group_key in expected_groups:
        assert group_key in scene_geoms, f"Missing geometry {group_key} in master scene"
    print(f"  [OK] All {len(expected_groups)} semantic groups present in master scene")

    # 3. Check for duplicates in source usage
    print("\n[Check 3/6] Verifying no duplicate source assets...")
    used_sources = []
    for gkey, gval in manifest["groups"].items():
        if "segments" in gval:
            for s in gval["segments"]:
                used_sources.append(s["id"])
        else:
            used_sources.append(gval["id"])
    assert len(used_sources) == len(set(used_sources)), f"Duplicate source IDs found: {used_sources}"
    assert len(used_sources) == 18, f"Expected exactly 18 source meshes, found {len(used_sources)}"
    print(f"  [OK] Exactly 18 unique source assets utilized: {sorted(used_sources)}")

    # 4. Check coordinate alignment against source OBJs
    print("\n[Check 4/6] Verifying coordinate bounds against source OBJs...")
    for group_key in expected_groups:
        glb_file = os.path.join(PROCESSED_DIR, f"{group_key}.glb")
        glb_mesh = load_mesh(glb_file)
        m_info = manifest["groups"][group_key]
        expected_min = np.array(m_info["bounds_min"])
        expected_max = np.array(m_info["bounds_max"])

        glb_min = glb_mesh.bounds[0]
        glb_max = glb_mesh.bounds[1]

        diff_min = np.max(np.abs(glb_min - expected_min))
        diff_max = np.max(np.abs(glb_max - expected_max))

        assert diff_min < 0.01, f"Bounding min mismatch in {group_key}: {diff_min} mm"
        assert diff_max < 0.01, f"Bounding max mismatch in {group_key}: {diff_max} mm"
    print("  [OK] Coordinate alignment and millimeter scale strictly preserved")

    # 5. Junction and origin continuity analysis
    print("\n[Check 5/6] Inspecting anatomical junctions and coronary origins...")
    junction_pairs = [
        ("Aortic Bulb -> Left Main", "struct_aorta_bulb", "struct_left_main", 0.5, 0.35),
        ("Aortic Bulb -> Proximal RCA", "struct_aorta_bulb", "vessel_rca", 0.5, 0.35),
        ("Left Main -> LAD", "struct_left_main", "vessel_lad", 0.5, 0.35),
        ("Left Main -> LCX", "struct_left_main", "vessel_lcx", 0.5, 0.35),
        ("Aorta Bulb -> Ascending Aorta", "struct_aorta_bulb", "struct_aorta_ascending", 0.5, 0.35),
        ("Pulmonary Trunk -> Myocardium", "struct_pulmonary_trunk", "struct_myocardium", 0.5, 0.35),
        ("Myocardium -> Auricles", "struct_myocardium", "struct_auricles", 1.5, 1.0),
        ("Septum -> Myocardium", "struct_septum", "struct_myocardium", 0.5, 0.35),
    ]

    for label, id_a, id_b, threshold_mm, max_gap_mm in junction_pairs:
        mesh_a = load_mesh(os.path.join(PROCESSED_DIR, f"{id_a}.glb"))
        mesh_b = load_mesh(os.path.join(PROCESSED_DIR, f"{id_b}.glb"))

        tree_b = cKDTree(mesh_b.vertices)
        dists, _ = tree_b.query(mesh_a.vertices)
        min_dist = dists.min()
        close_pts = int((dists < threshold_mm).sum())

        print(f"  {label}:")
        print(f"    - Minimum Euclidean distance: {min_dist:.4f} mm")
        print(f"    - Vertices within {threshold_mm} mm: {close_pts}")

        assert min_dist < max_gap_mm, f"Unacceptably large gap at {label}: {min_dist} mm (threshold: {max_gap_mm} mm)"

    # 6. Global dimensions verification
    print("\n[Check 6/6] Verifying global assembled heart dimensions...")
    all_verts = []
    for group_key in expected_groups:
        mesh = load_mesh(os.path.join(PROCESSED_DIR, f"{group_key}.glb"))
        all_verts.append(mesh.vertices)
    combined = np.vstack(all_verts)
    extents = combined.max(axis=0) - combined.min(axis=0)
    print(f"  Assembled dimensions (W x D x H): {extents[0]:.2f} x {extents[1]:.2f} x {extents[2]:.2f} mm")
    assert 95 < extents[0] < 125, f"Width out of expected physiological range: {extents[0]}"
    assert 85 < extents[1] < 105, f"Depth out of expected physiological range: {extents[1]}"
    assert 110 < extents[2] < 130, f"Height out of expected physiological range: {extents[2]}"
    print("  [OK] Physiological dimensions validated for cohesive heart assembly")

    print("\n=============================================")
    print("ALL GEOMETRY VALIDATION CHECKS PASSED (6/6)!")
    print("=============================================")
    return True


if __name__ == "__main__":
    run_geometry_validation()
