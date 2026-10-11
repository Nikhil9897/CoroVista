import os
import glob
import trimesh
import numpy as np

OBJ_DIR = "OBJ Files"

def load_mesh(prefix):
    matches = glob.glob(os.path.join(OBJ_DIR, f"{prefix}_*.obj"))
    return trimesh.load(matches[0], process=False)

def test_wall_thickness(prefix, name):
    m = load_mesh(prefix)
    # Check distances between opposite faces or vertices
    # If a mesh has thickness, a vertex on the outer wall has a nearby vertex on the inner wall
    from scipy.spatial import cKDTree
    tree = cKDTree(m.vertices)
    # Distance to second nearest neighbor (first is self)
    dists, _ = tree.query(m.vertices, k=15)
    # Let's inspect ray casting or face normals
    # If there are opposite normals:
    # Check if for faces, there are pairs with dot product < -0.8
    f_centers = m.triangles_center
    f_norms = m.face_normals
    tree_fc = cKDTree(f_centers)
    # Query nearest faces
    dists_f, idxs_f = tree_fc.query(f_centers, k=50)
    
    # Look for faces with normal pointing roughly opposite
    opp_dists = []
    for i in range(len(f_centers)):
        for k in range(1, 50):
            dot = np.dot(f_norms[i], f_norms[idxs_f[i, k]])
            if dot < -0.7:
                opp_dists.append(dists_f[i, k])
                break
    opp_dists = np.array(opp_dists)
    print(f"[{prefix}] {name}:")
    print(f"  Faces with opposing surface: {len(opp_dists)} / {len(f_centers)} ({len(opp_dists)/len(f_centers)*100:.1f}%)")
    if len(opp_dists) > 0:
        print(f"  Wall thickness: median = {np.median(opp_dists):.2f} mm, 10th pct = {np.percentile(opp_dists, 10):.2f} mm, 90th pct = {np.percentile(opp_dists, 90):.2f} mm")

test_wall_thickness("MM474", "LV Free Wall")
test_wall_thickness("MM598", "RV Inflow")
test_wall_thickness("MM538", "RV Outflow")
test_wall_thickness("MM559", "RA Anterior")
test_wall_thickness("MM632", "LA Anterior")
test_wall_thickness("MM558", "Aortic Bulb")
test_wall_thickness("MM607", "Pulmonary Trunk")
