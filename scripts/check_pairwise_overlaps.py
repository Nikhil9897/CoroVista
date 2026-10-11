import os
import glob
import trimesh
import numpy as np
from scipy.spatial import cKDTree

OBJ_DIR = "OBJ Files"

def load_mesh(prefix):
    matches = glob.glob(os.path.join(OBJ_DIR, f"{prefix}_*.obj"))
    return trimesh.load(matches[0], process=False)

def check_pairwise_overlaps():
    candidates = {
        # Ventricles
        "MM474": ("LV Free Wall", load_mesh("MM474")),
        "MM631": ("LV subsegment (old)", load_mesh("MM631")),
        "MM598": ("RV Inflow", load_mesh("MM598")),
        "MM538": ("RV Outflow", load_mesh("MM538")),
        
        # RA
        "MM559": ("RA Anterior", load_mesh("MM559")),
        "MM560": ("RA Lateral", load_mesh("MM560")),
        "MM461": ("RA Auricle", load_mesh("MM461")),
        "MM590": ("RA Septal", load_mesh("MM590")),
        
        # LA
        "MM632": ("LA Anterior", load_mesh("MM632")),
        "MM633": ("LA Posterior", load_mesh("MM633")),
        "MM456": ("LA Lateral", load_mesh("MM456")),
        "MM458": ("LA Septal", load_mesh("MM458")),
        "MM459": ("LA Auricle", load_mesh("MM459")),
        "MM460": ("LA Superior", load_mesh("MM460")),
        
        # Septum
        "MM600": ("IV Septum", load_mesh("MM600")),
        "MM594": ("IV Septum sub", load_mesh("MM594")),
        "MM618": ("LV Septal", load_mesh("MM618")),
        "MM625": ("LV Septal", load_mesh("MM625")),
        "MM629": ("LV Septal", load_mesh("MM629")),

        # Great Vessels
        "MM558": ("Aortic Bulb", load_mesh("MM558")),
        "MM506": ("Ascending Aorta", load_mesh("MM506")),
        "MM607": ("Pulmonary Trunk", load_mesh("MM607")),
    }

    # Analyze LA parts
    la_keys = ["MM632", "MM633", "MM456", "MM458", "MM459", "MM460"]
    print("=== LA PARTS OVERLAP / DISTANCE MATRIX ===")
    for i, k1 in enumerate(la_keys):
        for k2 in la_keys[i+1:]:
            m1 = candidates[k1][1]
            m2 = candidates[k2][1]
            tree = cKDTree(m2.vertices)
            dists, _ = tree.query(m1.vertices)
            close = (dists < 0.1).sum()
            overlap_verts = (dists < 0.01).sum()
            print(f"{k1} ({candidates[k1][0]}) vs {k2} ({candidates[k2][0]}): min={dists.min():.4f} mm, <0.1mm: {close}, <0.01mm: {overlap_verts}")

    # Analyze RA parts
    ra_keys = ["MM559", "MM560", "MM461", "MM590"]
    print("\n=== RA PARTS OVERLAP / DISTANCE MATRIX ===")
    for i, k1 in enumerate(ra_keys):
        for k2 in ra_keys[i+1:]:
            m1 = candidates[k1][1]
            m2 = candidates[k2][1]
            tree = cKDTree(m2.vertices)
            dists, _ = tree.query(m1.vertices)
            close = (dists < 0.1).sum()
            overlap_verts = (dists < 0.01).sum()
            print(f"{k1} ({candidates[k1][0]}) vs {k2} ({candidates[k2][0]}): min={dists.min():.4f} mm, <0.1mm: {close}, <0.01mm: {overlap_verts}")

    # Analyze Ventricle parts
    v_keys = ["MM474", "MM598", "MM538", "MM600"]
    print("\n=== VENTRICLE & SEPTUM OVERLAP / DISTANCE MATRIX ===")
    for i, k1 in enumerate(v_keys):
        for k2 in v_keys[i+1:]:
            m1 = candidates[k1][1]
            m2 = candidates[k2][1]
            tree = cKDTree(m2.vertices)
            dists, _ = tree.query(m1.vertices)
            close = (dists < 0.1).sum()
            print(f"{k1} ({candidates[k1][0]}) vs {k2} ({candidates[k2][0]}): min={dists.min():.4f} mm, <0.1mm: {close}")

if __name__ == "__main__":
    check_pairwise_overlaps()
