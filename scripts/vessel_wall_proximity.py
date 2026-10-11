import os
import glob
import trimesh
import numpy as np
from scipy.spatial import cKDTree

OBJ_DIR = "OBJ Files"

def load_mesh(prefix):
    matches = glob.glob(os.path.join(OBJ_DIR, f"{prefix}_*.obj"))
    return trimesh.load(matches[0], process=False)

def check_vessel_distances():
    # Vessels
    lad = trimesh.util.concatenate([load_mesh("MM420"), load_mesh("MM424"), load_mesh("MM425")])
    lcx = trimesh.util.concatenate([load_mesh("MM426"), load_mesh("MM635")])
    rca = trimesh.util.concatenate([load_mesh("MM556"), load_mesh("MM436"), load_mesh("MM439")])
    lm = load_mesh("MM557")

    # Walls
    lv_474 = load_mesh("MM474")
    rv_inflow = load_mesh("MM598")
    rv_outflow = load_mesh("MM538")
    ra_ant = load_mesh("MM559")
    ra_lat = load_mesh("MM560")
    ra_aur = load_mesh("MM461")
    la_ant = load_mesh("MM632")
    la_post = load_mesh("MM633")
    la_aur = load_mesh("MM459")
    septum = load_mesh("MM600")

    walls = {
        "LV Free Wall (MM474)": lv_474,
        "RV Inflow (MM598)": rv_inflow,
        "RV Outflow (MM538)": rv_outflow,
        "RA Anterior (MM559)": ra_ant,
        "RA Lateral (MM560)": ra_lat,
        "RA Auricle (MM461)": ra_aur,
        "LA Anterior (MM632)": la_ant,
        "LA Posterior (MM633)": la_post,
        "LA Auricle (MM459)": la_aur,
        "Septum (MM600)": septum,
    }

    print("=== VESSEL-TO-WALL PROXIMITY ANALYSIS ===")
    for vname, vmesh in [("LAD", lad), ("LCX", lcx), ("RCA", rca), ("Left Main", lm)]:
        print(f"\n[{vname}]:")
        for wname, wmesh in walls.items():
            tree = cKDTree(wmesh.vertices)
            dists, _ = tree.query(vmesh.vertices)
            min_d = dists.min()
            pct_under_2mm = (dists < 2.0).mean() * 100
            pct_under_5mm = (dists < 5.0).mean() * 100
            if min_d < 3.0:
                print(f"  -> Contact with {wname}: min={min_d:.3f} mm, {pct_under_2mm:.1f}% verts < 2mm, {pct_under_5mm:.1f}% verts < 5mm")

if __name__ == "__main__":
    check_vessel_distances()
