import os
import glob
import trimesh
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from pathlib import Path

OBJ_DIR = "OBJ Files"
OUTPUT_DIR = Path("docs/screenshots/silhouette_tests")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_clean(prefix):
    matches = glob.glob(os.path.join(OBJ_DIR, f"{prefix}_*.obj"))
    m = trimesh.load(matches[0], process=False)
    comps = m.split(only_watertight=False)
    valid = [c for c in comps if len(c.faces) >= 15]
    if not valid:
        valid = [max(comps, key=lambda c: len(c.faces))]
    if len(valid) > 1:
        res = trimesh.util.concatenate(valid)
    else:
        res = valid[0].copy()
    return res

def test_configurations():
    # Ventricular myocardium
    lv = load_clean("MM474")
    rv_in = load_clean("MM598")
    rv_out = load_clean("MM538")
    
    # Atria
    ra_ant = load_clean("MM559")
    ra_lat = load_clean("MM560")
    ra_aur = load_clean("MM461")
    la_ant = load_clean("MM632")
    la_post = load_clean("MM633")
    la_lat = load_clean("MM456")
    la_aur = load_clean("MM459")
    la_sup = load_clean("MM460")

    # Vessels
    lad = trimesh.util.concatenate([load_clean("MM420"), load_clean("MM424"), load_clean("MM425")])
    lcx = trimesh.util.concatenate([load_clean("MM426"), load_clean("MM635")])
    rca = trimesh.util.concatenate([load_clean("MM556"), load_clean("MM436"), load_clean("MM439")])
    lm = load_clean("MM557")
    aorta = trimesh.util.concatenate([load_clean("MM558"), load_clean("MM506")])
    pulm = load_clean("MM607")

    # Test Config A: Unified Ventricles (LV + RV), RA (ant + auricle only, without the flat lateral MM560 plate), LA (ant + auricle + post)
    # Test Config B: Merged Myocardium as a single welded mesh!
    
    # Let's inspect Config A
    myo_parts = [lv, rv_in, rv_out]
    # Weld nearby vertices of ventricles
    myo_unified = trimesh.util.concatenate(myo_parts)
    # Merge coincident vertices with tolerance 0.25mm
    # In trimesh, we can merge vertices
    myo_unified.merge_vertices(merge_tex=True, merge_norm=True)
    _ = myo_unified.vertex_normals

    print(f"Unified Ventricular Myocardium: {len(myo_unified.vertices)} verts, {len(myo_unified.faces)} faces")

    # Center
    center = np.array([21.51, -122.85, 1233.94])

    # Plot
    fig = plt.figure(figsize=(10, 10), facecolor="#090d16")
    ax = fig.add_subplot(111, projection="3d", facecolor="#090d16")
    ax.axis("off")

    # Add unified myocardium
    tri = (myo_unified.vertices - center)[myo_unified.faces[::2]]
    p1 = Poly3DCollection(tri, facecolors=(0.65, 0.15, 0.20, 0.95), edgecolors="none")
    ax.add_collection3d(p1)

    # Add aorta
    tri_ao = (aorta.vertices - center)[aorta.faces[::2]]
    p2 = Poly3DCollection(tri_ao, facecolors=(0.85, 0.45, 0.45, 0.95), edgecolors="none")
    ax.add_collection3d(p2)

    # Add pulm
    tri_p = (pulm.vertices - center)[pulm.faces[::2]]
    p3 = Poly3DCollection(tri_p, facecolors=(0.35, 0.55, 0.75, 0.95), edgecolors="none")
    ax.add_collection3d(p3)

    # Add LAD
    tri_lad = (lad.vertices - center)[lad.faces]
    p_lad = Poly3DCollection(tri_lad, facecolors=(0.95, 0.60, 0.05, 1.0), edgecolors="none")
    ax.add_collection3d(p_lad)

    # Add RCA
    tri_rca = (rca.vertices - center)[rca.faces]
    p_rca = Poly3DCollection(tri_rca, facecolors=(0.75, 0.72, 0.10, 1.0), edgecolors="none")
    ax.add_collection3d(p_rca)

    limit = 65
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_zlim(-limit, limit)
    ax.view_init(elev=15, azim=-90)

    out_p = OUTPUT_DIR / "ventricles_only.png"
    plt.tight_layout()
    plt.savefig(out_p, dpi=160, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    print(f"Saved {out_p}")

if __name__ == "__main__":
    test_configurations()
