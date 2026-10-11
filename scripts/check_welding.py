import os
import glob
import trimesh
import numpy as np

OBJ_DIR = "OBJ Files"

def load_mesh(prefix):
    matches = glob.glob(os.path.join(OBJ_DIR, f"{prefix}_*.obj"))
    return trimesh.load(matches[0], process=False)

def check_welding_and_normals():
    # Ventricles: LV (MM474) + RV (MM598 + MM538)
    lv = load_mesh("MM474")
    rv_inflow = load_mesh("MM598")
    rv_outflow = load_mesh("MM538")

    print(f"LV MM474: {len(lv.vertices)} verts, {len(lv.faces)} faces")
    print(f"RV Inflow MM598: {len(rv_inflow.vertices)} verts, {len(rv_inflow.faces)} faces")
    print(f"RV Outflow MM538: {len(rv_outflow.vertices)} verts, {len(rv_outflow.faces)} faces")

    # When concatenated in trimesh:
    v_concat = trimesh.util.concatenate([lv, rv_inflow, rv_outflow])
    print(f"Concatenated ventricles: {len(v_concat.vertices)} verts, {len(v_concat.faces)} faces")
    
    # Check duplicate or coincident vertices
    # If we merge close vertices (within 0.3mm):
    v_merged = v_concat.copy()
    v_merged.merge_vertices(merge_tex=True, merge_norm=True)
    print(f"Merged exact duplicate vertices: {len(v_merged.vertices)} verts")

    # Now let's test trimesh grouping or welding nearby boundary vertices
    # How many boundary edges does v_concat have?
    edges = v_concat.edges_sorted
    unique_edges, counts = np.unique(edges, axis=0, return_counts=True)
    boundary_edges = unique_edges[counts == 1]
    print(f"Boundary edges in concatenated: {len(boundary_edges)}")

    # Check the distances between boundary vertices of LV and RV:
    from scipy.spatial import cKDTree
    tree_rv = cKDTree(rv_inflow.vertices)
    dists_lv_to_rv, _ = tree_rv.query(lv.vertices)
    close_mask = dists_lv_to_rv < 0.3
    print(f"LV vertices within 0.3mm of RV inflow: {close_mask.sum()} / {len(lv.vertices)}")
    print(f"Min dist LV to RV inflow: {dists_lv_to_rv.min():.4f} mm")

    # What about RA meshes: MM559, MM560, MM461?
    ra_ant = load_mesh("MM559")
    ra_lat = load_mesh("MM560")
    ra_aur = load_mesh("MM461")
    print(f"\nRA Ant MM559: {len(ra_ant.vertices)} verts, faces: {len(ra_ant.faces)}")
    print(f"RA Lat MM560: {len(ra_lat.vertices)} verts, faces: {len(ra_lat.faces)}")
    print(f"RA Aur MM461: {len(ra_aur.vertices)} verts, faces: {len(ra_aur.faces)}")

    # Let's inspect MM560: why does it look like a plate?
    # MM560 bounds:
    print(f"MM560 bounds: X[{ra_lat.bounds[0][0]:.1f}, {ra_lat.bounds[1][0]:.1f}], Y[{ra_lat.bounds[0][1]:.1f}, {ra_lat.bounds[1][1]:.1f}], Z[{ra_lat.bounds[0][2]:.1f}, {ra_lat.bounds[1][2]:.1f}]")
    print(f"MM559 bounds: X[{ra_ant.bounds[0][0]:.1f}, {ra_ant.bounds[1][0]:.1f}], Y[{ra_ant.bounds[0][1]:.1f}, {ra_ant.bounds[1][1]:.1f}], Z[{ra_ant.bounds[0][2]:.1f}, {ra_ant.bounds[1][2]:.1f}]")

if __name__ == "__main__":
    check_welding_and_normals()
