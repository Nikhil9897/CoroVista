import os
import glob
import trimesh
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

OBJ_DIR = "OBJ Files"

def load_mesh(prefix):
    matches = glob.glob(os.path.join(OBJ_DIR, f"{prefix}_*.obj"))
    return trimesh.load(matches[0], process=False)

def test_complete_assembly():
    structures = {
        # Vessels
        "vessel_lad": trimesh.util.concatenate([load_mesh("MM420"), load_mesh("MM424"), load_mesh("MM425")]),
        "vessel_lcx": trimesh.util.concatenate([load_mesh("MM426"), load_mesh("MM635")]),
        "vessel_rca": trimesh.util.concatenate([load_mesh("MM556"), load_mesh("MM436"), load_mesh("MM439")]),
        "struct_left_main": load_mesh("MM557"),
        
        # Great Vessels
        "struct_aorta_bulb": load_mesh("MM558"),
        "struct_aorta_ascending": load_mesh("MM506"),
        "struct_pulmonary_trunk": load_mesh("MM607"),
        
        # Ventricular Myocardium
        "struct_lv_wall": load_mesh("MM474"),
        "struct_rv_inflow": load_mesh("MM598"),
        "struct_rv_outflow": load_mesh("MM538"),
        
        # Atria & Auricles
        "struct_ra_anterior": load_mesh("MM559"),
        "struct_ra_lateral": load_mesh("MM560"),
        "struct_ra_auricle": load_mesh("MM461"),
        "struct_la_anterior": load_mesh("MM632"),
        "struct_la_posterior": load_mesh("MM633"),
        "struct_la_lateral": load_mesh("MM456"),
        "struct_la_auricle": load_mesh("MM459"),
        "struct_la_superior": load_mesh("MM460"),
        
        # Internal Context
        "struct_septum": load_mesh("MM600"),
    }

    print("=== PROPOSED FULL CARDIAC ASSEMBLY ===")
    total_verts = 0
    total_faces = 0
    all_verts = []

    for name, m in structures.items():
        nv = len(m.vertices)
        nf = len(m.faces)
        total_verts += nv
        total_faces += nf
        all_verts.append(m.vertices)
        print(f"[{name:<24s}]: {nv:5d} verts, {nf:5d} faces | bounds X:[{m.bounds[0][0]:.1f}, {m.bounds[1][0]:.1f}], Y:[{m.bounds[0][1]:.1f}, {m.bounds[1][1]:.1f}], Z:[{m.bounds[0][2]:.1f}, {m.bounds[1][2]:.1f}]")

    combined_verts = np.vstack(all_verts)
    g_min = combined_verts.min(axis=0)
    g_max = combined_verts.max(axis=0)
    g_center = (g_min + g_max) / 2.0
    g_extents = g_max - g_min

    print(f"\nTOTAL: {len(structures)} structures, {total_verts} vertices, {total_faces} faces")
    print(f"Global Bounds: min={np.round(g_min, 2)}, max={np.round(g_max, 2)}")
    print(f"Global Center: {np.round(g_center, 2)}")
    print(f"Dimensions (W x D x H): {g_extents[0]:.1f} x {g_extents[1]:.1f} x {g_extents[2]:.1f} mm")

    return structures, g_center

if __name__ == "__main__":
    test_complete_assembly()
