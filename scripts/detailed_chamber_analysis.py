import os
import glob
import json
import trimesh
import numpy as np
from scipy.spatial import cKDTree

OBJ_DIR = "OBJ Files"

def load_mesh(prefix):
    matches = glob.glob(os.path.join(OBJ_DIR, f"{prefix}_*.obj"))
    if not matches:
        raise FileNotFoundError(f"Prefix {prefix} not found")
    return trimesh.load(matches[0], process=False)

def analyze_lv():
    print("=== 1. LV FREE WALL INVESTIGATION ===")
    m474 = load_mesh("MM474")
    m631 = load_mesh("MM631")
    print(f"MM474: {len(m474.vertices)} verts, {len(m474.faces)} faces, bounds min={np.round(m474.bounds[0],1)}, max={np.round(m474.bounds[1],1)}, dims={np.round(m474.extents,1)}")
    print(f"MM631: {len(m631.vertices)} verts, {len(m631.faces)} faces, bounds min={np.round(m631.bounds[0],1)}, max={np.round(m631.bounds[1],1)}, dims={np.round(m631.extents,1)}")

    # Check if MM631 vertices are a subset of or close to MM474
    tree474 = cKDTree(m474.vertices)
    dists, _ = tree474.query(m631.vertices)
    print(f"Min dist MM631 -> MM474: {dists.min():.4f} mm, mean={dists.mean():.4f} mm, max={dists.max():.4f} mm")
    print(f"Fraction of MM631 within 0.1mm of MM474: {(dists < 0.1).mean()*100:.1f}%")
    print(f"Fraction of MM631 within 1.0mm of MM474: {(dists < 1.0).mean()*100:.1f}%")

    # Let's check subsegments MM614..MM631
    lv_subsegments = ["MM614", "MM615", "MM616", "MM620", "MM621", "MM622", "MM623", "MM624", "MM626", "MM627", "MM628", "MM631"]
    print(f"\nChecking 12 LV subsegments {lv_subsegments} vs MM474:")
    sub_meshes = [load_mesh(p) for p in lv_subsegments]
    concat_sub = trimesh.util.concatenate(sub_meshes)
    print(f"Combined subsegments: {len(concat_sub.vertices)} verts, bounds min={np.round(concat_sub.bounds[0],1)}, max={np.round(concat_sub.bounds[1],1)}, dims={np.round(concat_sub.extents,1)}")
    tree_concat = cKDTree(concat_sub.vertices)
    dists_sub_to_474, _ = tree_concat.query(m474.vertices)
    print(f"MM474 to concatenated subsegments: mean dist = {dists_sub_to_474.mean():.4f} mm, max = {dists_sub_to_474.max():.4f} mm")
    dists_474_to_sub, _ = tree474.query(concat_sub.vertices)
    print(f"Concatenated subsegments to MM474: mean dist = {dists_474_to_sub.mean():.4f} mm, max = {dists_474_to_sub.max():.4f} mm")

def analyze_rv():
    print("\n=== 2. RV WALL INVESTIGATION ===")
    m598 = load_mesh("MM598") # inflow
    m538 = load_mesh("MM538") # outflow
    print(f"MM598 (inflow): {len(m598.vertices)} verts, dims={np.round(m598.extents,1)}, bounds={np.round(m598.bounds,1).tolist()}")
    print(f"MM538 (outflow): {len(m538.vertices)} verts, dims={np.round(m538.extents,1)}, bounds={np.round(m538.bounds,1).tolist()}")
    tree538 = cKDTree(m538.vertices)
    dists, _ = tree538.query(m598.vertices)
    print(f"Junction between MM598 and MM538: min dist = {dists.min():.4f} mm")

def analyze_atria():
    print("\n=== 3. ATRIAL WALL INVESTIGATION ===")
    # RA: MM559 (ant), MM560 (lat), MM461 (auricle)
    ra_ant = load_mesh("MM559")
    ra_lat = load_mesh("MM560")
    ra_aur = load_mesh("MM461")
    print(f"RA Anterior (MM559): {len(ra_ant.vertices)} verts, bounds={np.round(ra_ant.bounds,1).tolist()}")
    print(f"RA Lateral (MM560): {len(ra_lat.vertices)} verts, bounds={np.round(ra_lat.bounds,1).tolist()}")
    print(f"RA Auricle (MM461): {len(ra_aur.vertices)} verts, bounds={np.round(ra_aur.bounds,1).tolist()}")
    tree_lat = cKDTree(ra_lat.vertices)
    d1, _ = tree_lat.query(ra_ant.vertices)
    print(f"Min dist RA ant (MM559) <-> RA lat (MM560): {d1.min():.4f} mm")
    tree_aur = cKDTree(ra_aur.vertices)
    d2, _ = tree_aur.query(ra_ant.vertices)
    print(f"Min dist RA ant (MM559) <-> RA auricle (MM461): {d2.min():.4f} mm")

    # LA: MM632 (ant), MM633 (post), MM456 (lat), MM458 (sept), MM459 (auricle), MM460 (sup)
    la_ant = load_mesh("MM632")
    la_post = load_mesh("MM633")
    la_lat = load_mesh("MM456")
    la_sept = load_mesh("MM458")
    la_aur = load_mesh("MM459")
    la_sup = load_mesh("MM460")
    print(f"\nLA Anterior (MM632): {len(la_ant.vertices)} verts, bounds={np.round(la_ant.bounds,1).tolist()}")
    print(f"LA Posterior (MM633): {len(la_post.vertices)} verts, bounds={np.round(la_post.bounds,1).tolist()}")
    print(f"LA Lateral (MM456): {len(la_lat.vertices)} verts, bounds={np.round(la_lat.bounds,1).tolist()}")
    print(f"LA Septal (MM458): {len(la_sept.vertices)} verts, bounds={np.round(la_sept.bounds,1).tolist()}")
    print(f"LA Auricle (MM459): {len(la_aur.vertices)} verts, bounds={np.round(la_aur.bounds,1).tolist()}")
    print(f"LA Superior (MM460): {len(la_sup.vertices)} verts, bounds={np.round(la_sup.bounds,1).tolist()}")

if __name__ == "__main__":
    analyze_lv()
    analyze_rv()
    analyze_atria()
