"""
CoroVista - Detailed Mesh Connectivity, Overlap & Continuity Analysis
"""

import json
from pathlib import Path
import numpy as np

def load_vertices(filepath: Path):
    verts = []
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("v "):
                parts = line.split()
                if len(parts) >= 4:
                    verts.append([float(parts[1]), float(parts[2]), float(parts[3])])
    return np.array(verts)

def min_distance_between_meshes(v1, v2):
    # Sample down if too large
    if len(v1) > 1000:
        idx1 = np.random.choice(len(v1), 1000, replace=False)
        s1 = v1[idx1]
    else:
        s1 = v1
    if len(v2) > 1000:
        idx2 = np.random.choice(len(v2), 1000, replace=False)
        s2 = v2[idx2]
    else:
        s2 = v2
    
    # Compute pairwise min distance
    from scipy.spatial.distance import cdist
    dists = cdist(s1, s2)
    return float(np.min(dists))

def main():
    obj_dir = Path("OBJ Files")
    
    # LAD analysis
    print("=== LAD SEGMENT CONTINUITY ===")
    v_lm = load_vertices(obj_dir / "MM557_BP58405_FMA4685_Stem of left coronary artery.obj")
    v_lad1 = load_vertices(obj_dir / "MM420_BP51969_FMA74912_Trunk of anterior interventricular branch of left coronary artery.obj")
    v_lad2 = load_vertices(obj_dir / "MM424_BP51969_FMA74912_Trunk of anterior interventricular branch of left coronary artery.obj")
    v_lad3 = load_vertices(obj_dir / "MM425_BP51969_FMA74912_Trunk of anterior interventricular branch of left coronary artery.obj")
    
    print(f"Left Main (MM557) <-> LAD Proximal (MM420) min dist: {min_distance_between_meshes(v_lm, v_lad1):.3f} mm")
    print(f"LAD Proximal (MM420) <-> LAD Mid (MM424) min dist:    {min_distance_between_meshes(v_lad1, v_lad2):.3f} mm")
    print(f"LAD Mid (MM424) <-> LAD Distal (MM425) min dist:      {min_distance_between_meshes(v_lad2, v_lad3):.3f} mm")
    
    # RCA analysis
    print("\n=== RCA SEGMENT CONTINUITY ===")
    v_rca1 = load_vertices(obj_dir / "MM556_BP51977_FMA3802_Trunk of right coronary artery.obj") # proximal
    v_rca2 = load_vertices(obj_dir / "MM436_BP51977_FMA3802_Trunk of right coronary artery.obj") # mid
    v_rca3 = load_vertices(obj_dir / "MM439_BP51977_FMA3802_Trunk of right coronary artery.obj") # distal
    
    print(f"RCA Proximal (MM556) <-> RCA Mid (MM436) min dist:    {min_distance_between_meshes(v_rca1, v_rca2):.3f} mm")
    print(f"RCA Mid (MM436) <-> RCA Distal (MM439) min dist:      {min_distance_between_meshes(v_rca2, v_rca3):.3f} mm")

    # LCX analysis
    print("\n=== LCX SEGMENT CONTINUITY ===")
    v_lcx1 = load_vertices(obj_dir / "MM426_BP51973_FMA74923_Trunk of circumflex branch of left coronary artery.obj")
    v_lcx2 = load_vertices(obj_dir / "MM635_BP51973_FMA74923_Trunk of circumflex branch of left coronary artery.obj")
    
    print(f"Left Main (MM557) <-> LCX Proximal (MM426) min dist: {min_distance_between_meshes(v_lm, v_lcx1):.3f} mm")
    print(f"LCX Proximal (MM426) <-> LCX Distal (MM635) min dist: {min_distance_between_meshes(v_lcx1, v_lcx2):.3f} mm")
    
    # LCX Branches
    v_om = load_vertices(obj_dir / "MM610_BP51926_FMA3902_Left marginal artery.obj")
    v_plv = load_vertices(obj_dir / "MM428_BP51937_FMA3914_First posterior ventricular branch of circumflex coronary artery.obj")
    print(f"LCX Proximal (MM426) <-> Left Marginal (MM610) min dist: {min_distance_between_meshes(v_lcx1, v_om):.3f} mm")
    print(f"LCX Distal (MM635) <-> First Post. Vent. (MM428) min dist: {min_distance_between_meshes(v_lcx2, v_plv):.3f} mm")

    # Aorta ostia
    print("\n=== AORTA AND CORONARY OSTIA ===")
    v_aorta = load_vertices(obj_dir / "MM558_BP51975_FMA15098_Wall of bulb of aorta.obj")
    print(f"Aorta Bulb (MM558) <-> Left Main (MM557) min dist: {min_distance_between_meshes(v_aorta, v_lm):.3f} mm")
    print(f"Aorta Bulb (MM558) <-> RCA Proximal (MM556) min dist: {min_distance_between_meshes(v_aorta, v_rca1):.3f} mm")

if __name__ == "__main__":
    main()
