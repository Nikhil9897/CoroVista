import os
import glob
import trimesh
import numpy as np

OBJ_DIR = "OBJ Files"

def load_clean_component(prefix, min_faces=15):
    matches = glob.glob(os.path.join(OBJ_DIR, f"{prefix}_*.obj"))
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

def test_refined_heart():
    # 1. Unified Myocardium: LV (MM474) + RV inflow (MM598) + RV outflow (MM538)
    lv = load_clean_component("MM474")
    rv_in = load_clean_component("MM598")
    rv_out = load_clean_component("MM538")
    myo = trimesh.util.concatenate([lv, rv_in, rv_out])
    # Weld coincident vertices along shared seams
    myo.merge_vertices(merge_tex=True, merge_norm=True)
    _ = myo.vertex_normals
    print(f"Refined Myocardium: {len(myo.vertices)} verts, {len(myo.faces)} faces, bounds={np.round(myo.bounds, 1).tolist()}")

    # 2. Auricles: RA auricle (MM461) + LA auricle (MM459)
    ra_aur = load_clean_component("MM461")
    la_aur = load_clean_component("MM459")
    auricles = trimesh.util.concatenate([ra_aur, la_aur])
    auricles.merge_vertices(merge_tex=True, merge_norm=True)
    _ = auricles.vertex_normals
    print(f"Refined Auricles: {len(auricles.vertices)} verts, {len(auricles.faces)} faces")

    # 3. Great vessels: Aorta bulb (MM558), Ascending aorta (MM506), Pulmonary trunk (MM607)
    aorta_bulb = load_clean_component("MM558")
    aorta_asc = load_clean_component("MM506")
    pulm = load_clean_component("MM607")
    _ = aorta_bulb.vertex_normals
    _ = aorta_asc.vertex_normals
    _ = pulm.vertex_normals
    print(f"Aorta Bulb: {len(aorta_bulb.vertices)} verts, Ascending Aorta: {len(aorta_asc.vertices)} verts, Pulmonary Trunk: {len(pulm.vertices)} verts")

    # 4. Vessels: LAD (MM420, 424, 425), LCX (MM426, 635), RCA (MM556, 436, 439), Left Main (MM557)
    lad = trimesh.util.concatenate([load_clean_component("MM420"), load_clean_component("MM424"), load_clean_component("MM425")])
    lcx = trimesh.util.concatenate([load_clean_component("MM426"), load_clean_component("MM635")])
    rca = trimesh.util.concatenate([load_clean_component("MM556"), load_clean_component("MM436"), load_clean_component("MM439")])
    lm = load_clean_component("MM557")
    lad.merge_vertices(merge_tex=True, merge_norm=True)
    lcx.merge_vertices(merge_tex=True, merge_norm=True)
    rca.merge_vertices(merge_tex=True, merge_norm=True)
    lm.merge_vertices(merge_tex=True, merge_norm=True)
    _ = lad.vertex_normals
    _ = lcx.vertex_normals
    _ = rca.vertex_normals
    _ = lm.vertex_normals
    print(f"LAD: {len(lad.vertices)} verts, LCX: {len(lcx.vertices)} verts, RCA: {len(rca.vertices)} verts, Left Main: {len(lm.vertices)} verts")

    all_v = np.vstack([myo.vertices, auricles.vertices, aorta_bulb.vertices, aorta_asc.vertices, pulm.vertices, lad.vertices, lcx.vertices, rca.vertices, lm.vertices])
    g_min = all_v.min(axis=0)
    g_max = all_v.max(axis=0)
    center = (g_min + g_max) / 2.0
    extents = g_max - g_min
    print(f"\nGlobal Centroid: {np.round(center, 2)}")
    print(f"Global Extents: {np.round(extents, 1)}")

if __name__ == "__main__":
    test_refined_heart()
