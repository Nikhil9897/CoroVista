import os
import glob
import trimesh
import numpy as np

OBJ_DIR = "OBJ Files"

def load_mesh(prefix):
    matches = glob.glob(os.path.join(OBJ_DIR, f"{prefix}_*.obj"))
    return trimesh.load(matches[0], process=False)

def check_normals_orientation():
    # Heart center approx [20, -124, 1236]
    heart_center = np.array([20.10, -124.14, 1236.43])
    
    mesh_keys = [
        ("MM474", "LV Free Wall"),
        ("MM598", "RV Inflow"),
        ("MM538", "RV Outflow"),
        ("MM559", "RA Anterior"),
        ("MM560", "RA Lateral"),
        ("MM461", "RA Auricle"),
        ("MM632", "LA Anterior"),
        ("MM633", "LA Posterior"),
        ("MM456", "LA Lateral"),
        ("MM459", "LA Auricle"),
        ("MM460", "LA Superior"),
        ("MM600", "IV Septum"),
        ("MM558", "Aortic Bulb"),
        ("MM506", "Ascending Aorta"),
        ("MM607", "Pulmonary Trunk"),
    ]

    print("=== NORMAL ORIENTATION CHECK ===")
    for prefix, name in mesh_keys:
        m = load_mesh(prefix)
        # For each face, vector from heart center to face center
        face_centers = m.triangles_center
        face_normals = m.face_normals
        
        # Vector from heart center to face center
        v_out = face_centers - heart_center
        # Dot product with normal
        dots = np.sum(v_out * face_normals, axis=1)
        outward_ratio = (dots > 0).mean()
        
        # Also check winding consistency
        # In trimesh, m.is_winding_consistent
        winding_ok = m.is_winding_consistent
        
        print(f"[{prefix:6s}] {name:<22s}: faces={len(m.faces):5d}, winding_consistent={winding_ok}, outward_facing_ratio={outward_ratio*100:.1f}%")

if __name__ == "__main__":
    check_normals_orientation()
