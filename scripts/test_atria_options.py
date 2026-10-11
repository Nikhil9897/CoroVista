import os
import glob
import trimesh
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from pathlib import Path

OBJ_DIR = "OBJ Files"
OUTPUT_DIR = Path("docs/screenshots/silhouette_tests")

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

def test_atria_options():
    lv = load_clean("MM474")
    rv_in = load_clean("MM598")
    rv_out = load_clean("MM538")
    myo = trimesh.util.concatenate([lv, rv_in, rv_out])
    myo.merge_vertices(merge_tex=True, merge_norm=True)

    aorta = trimesh.util.concatenate([load_clean("MM558"), load_clean("MM506")])
    aorta.merge_vertices(merge_tex=True, merge_norm=True)
    pulm = load_clean("MM607")
    pulm.merge_vertices(merge_tex=True, merge_norm=True)

    lad = trimesh.util.concatenate([load_clean("MM420"), load_clean("MM424"), load_clean("MM425")])
    lcx = trimesh.util.concatenate([load_clean("MM426"), load_clean("MM635")])
    rca = trimesh.util.concatenate([load_clean("MM556"), load_clean("MM436"), load_clean("MM439")])

    ra_ant = load_clean("MM559")
    ra_aur = load_clean("MM461")
    la_ant = load_clean("MM632")
    la_aur = load_clean("MM459")

    # Option 1: Myocardium + Auricles only (Right auricle MM461, Left auricle MM459)
    # Option 2: Myocardium + Anterior RA (MM559) + Auricles (MM461, MM459)
    # Option 3: Full Myocardium alone (Ventricles + Aorta + Pulm)

    options = [
        ("opt1_ventricles_only", []),
        ("opt2_with_auricles", [ra_aur, la_aur]),
        ("opt3_with_ant_atria_auricles", [ra_ant, ra_aur, la_ant, la_aur]),
    ]

    center = np.array([21.51, -122.85, 1233.94])

    for name, atria_meshes in options:
        fig = plt.figure(figsize=(10, 10), facecolor="#090d16")
        ax = fig.add_subplot(111, projection="3d", facecolor="#090d16")
        ax.axis("off")

        # Myocardium
        tri_myo = (myo.vertices - center)[myo.faces[::2]]
        ax.add_collection3d(Poly3DCollection(tri_myo, facecolors=(0.65, 0.15, 0.20, 0.95), edgecolors="none"))

        # Atria
        for am in atria_meshes:
            tri_a = (am.vertices - center)[am.faces[::2]]
            ax.add_collection3d(Poly3DCollection(tri_a, facecolors=(0.60, 0.20, 0.25, 0.90), edgecolors="none"))

        # Aorta
        tri_ao = (aorta.vertices - center)[aorta.faces[::2]]
        ax.add_collection3d(Poly3DCollection(tri_ao, facecolors=(0.85, 0.45, 0.45, 0.95), edgecolors="none"))

        # Pulm
        tri_p = (pulm.vertices - center)[pulm.faces[::2]]
        ax.add_collection3d(Poly3DCollection(tri_p, facecolors=(0.35, 0.55, 0.75, 0.95), edgecolors="none"))

        # LAD
        ax.add_collection3d(Poly3DCollection((lad.vertices - center)[lad.faces], facecolors=(0.95, 0.60, 0.05, 1.0), edgecolors="none"))
        # RCA
        ax.add_collection3d(Poly3DCollection((rca.vertices - center)[rca.faces], facecolors=(0.75, 0.72, 0.10, 1.0), edgecolors="none"))
        # LCX
        ax.add_collection3d(Poly3DCollection((lcx.vertices - center)[lcx.faces], facecolors=(0.09, 0.71, 0.63, 1.0), edgecolors="none"))

        limit = 65
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        ax.set_zlim(-limit, limit)
        ax.view_init(elev=15, azim=-90)

        out_p = OUTPUT_DIR / f"{name}.png"
        plt.tight_layout()
        plt.savefig(out_p, dpi=160, facecolor=fig.get_facecolor(), edgecolor="none")
        plt.close(fig)
        print(f"Rendered {out_p}")

if __name__ == "__main__":
    test_atria_options()
