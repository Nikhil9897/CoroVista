import os
import glob
import trimesh
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from pathlib import Path

OBJ_DIR = "OBJ Files"
OUTPUT_DIR = Path("docs/screenshots/test_renders")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_mesh(prefix):
    matches = glob.glob(os.path.join(OBJ_DIR, f"{prefix}_*.obj"))
    return trimesh.load(matches[0], process=False)

def assemble_heart():
    # Assemblies
    lad = trimesh.util.concatenate([load_mesh("MM420"), load_mesh("MM424"), load_mesh("MM425")])
    lcx = trimesh.util.concatenate([load_mesh("MM426"), load_mesh("MM635")])
    rca = trimesh.util.concatenate([load_mesh("MM556"), load_mesh("MM436"), load_mesh("MM439")])
    lm = load_mesh("MM557")
    aorta_bulb = load_mesh("MM558")
    aorta_asc = load_mesh("MM506")
    pulm = load_mesh("MM607")
    lv = load_mesh("MM474")
    rv = trimesh.util.concatenate([load_mesh("MM598"), load_mesh("MM538")])
    ra = trimesh.util.concatenate([load_mesh("MM559"), load_mesh("MM560"), load_mesh("MM461")])
    la = trimesh.util.concatenate([load_mesh("MM632"), load_mesh("MM633"), load_mesh("MM456"), load_mesh("MM459"), load_mesh("MM460")])
    septum = load_mesh("MM600")

    parts = {
        "lv": lv,
        "rv": rv,
        "ra": ra,
        "la": la,
        "septum": septum,
        "aorta_bulb": aorta_bulb,
        "aorta_asc": aorta_asc,
        "pulm": pulm,
        "lm": lm,
        "lcx": lcx,
        "rca": rca,
        "lad": lad,
    }
    return parts

def render_assembled_views():
    parts = assemble_heart()
    # Centroid across all parts
    all_verts = np.vstack([p.vertices for p in parts.values()])
    center = (all_verts.min(axis=0) + all_verts.max(axis=0)) / 2.0
    print(f"Calculated assembly center: {np.round(center, 2)}")

    # Natural anatomical color scheme
    # Myocardium: Warm natural crimson / deep coral
    # Great vessels: Soft anatomical pearl / warm ivory aorta, cyan-tinged pulmonary
    # Coronary vessels: Diagnostic risk colors
    colors = {
        "lv": (0.75, 0.22, 0.24, 0.95),        # Deep natural warm crimson
        "rv": (0.78, 0.26, 0.26, 0.95),        # Warm natural myocardial tissue
        "ra": (0.72, 0.28, 0.30, 0.95),        # Atrial wall
        "la": (0.70, 0.25, 0.28, 0.95),        # Atrial wall
        "septum": (0.65, 0.20, 0.25, 0.40),    # Internal septum (subtle)
        "aorta_bulb": (0.88, 0.42, 0.40, 0.90),# Aortic bulb
        "aorta_asc": (0.90, 0.45, 0.42, 0.90), # Ascending aorta
        "pulm": (0.35, 0.55, 0.75, 0.88),      # Pulmonary trunk
        "lm": (0.95, 0.30, 0.30, 1.0),         # Left main
        "lad": (0.94, 0.62, 0.05, 1.0),        # LAD prob ~0.53 Stenotic (Amber)
        "lcx": (0.09, 0.71, 0.63, 1.0),        # LCX prob ~0.13 Normal (Teal)
        "rca": (0.73, 0.72, 0.11, 1.0),        # RCA prob ~0.40 Stenotic (Gold)
    }

    views = [
        ("anterior", 15, -90, "Anterior (AP) View"),
        ("posterior", 15, 90, "Posterior View"),
        ("lao", 15, -45, "Left Anterior Oblique (LAO) View"),
        ("rao", 15, -135, "Right Anterior Oblique (RAO) View"),
    ]

    for vname, elev, azim, title in views:
        fig = plt.figure(figsize=(10, 10), facecolor="#090d16")
        ax = fig.add_subplot(111, projection="3d", facecolor="#090d16")
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
        ax.grid(False)
        ax.axis("off")

        for name, mesh in parts.items():
            verts = mesh.vertices - center
            faces = mesh.faces
            if len(faces) > 2500:
                step = max(1, len(faces) // 2500)
                faces = faces[::step]
            triangles = verts[faces]
            c = colors[name]
            poly = Poly3DCollection(
                triangles,
                facecolors=c,
                edgecolors=(c[0]*0.8, c[1]*0.8, c[2]*0.8, c[3]*0.3),
                linewidths=0.15,
                alpha=c[3]
            )
            ax.add_collection3d(poly)

        limit = 65
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        ax.set_zlim(-limit, limit)
        ax.view_init(elev=elev, azim=azim)

        fig.text(0.5, 0.94, f"CoroVista — {title}", ha="center", va="top", color="#f8fafc", fontsize=15, weight="bold")
        fig.text(0.5, 0.90, "Reconstructed BodyParts3D Complete Heart Assembly", ha="center", va="top", color="#94a3b8", fontsize=11)
        
        out_path = OUTPUT_DIR / f"{vname}_assembly.png"
        plt.tight_layout()
        plt.savefig(out_path, dpi=160, facecolor=fig.get_facecolor(), edgecolor="none", bbox_inches="tight")
        plt.close(fig)
        print(f"Rendered {out_path}")

if __name__ == "__main__":
    render_assembled_views()
