"""
CoroVista — Script to render high-resolution Anterior, Posterior, and Lateral anatomical views
from the production corovista_heart.glb asset.
"""

import os
from pathlib import Path
import trimesh
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

OUTPUT_DIR = Path("docs/screenshots")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

GLB_PATH = Path("frontend/public/models/corovista_heart.glb")

# Anatomical color hierarchy for rich PBR rendering
COLOR_MAP = {
    # Cohesive Myocardium (Warm natural anatomical burgundy / deep terracotta red)
    "struct_myocardium": (0.53, 0.13, 0.18, 1.0),
    # Auricles (Atrial appendages capping the base)
    "struct_auricles": (0.49, 0.11, 0.16, 1.0),
    # Internal context (subtle septum)
    "struct_septum": (0.43, 0.10, 0.15, 0.45),
    # Great Vessels (Aorta: warm arterial ivory / rose; Pulmonary: venous slate-blue)
    "struct_aorta_bulb": (0.85, 0.55, 0.51, 1.0),
    "struct_aorta_ascending": (0.89, 0.61, 0.58, 1.0),
    "struct_pulmonary_trunk": (0.33, 0.49, 0.59, 1.0),
    # Coronary Arteries (Continuous model-probability risk shaders)
    "struct_left_main": (0.99, 0.65, 0.65, 1.0),
    "vessel_lad": (0.94, 0.62, 0.05, 1.0),        # Amber / Orange (prob = 0.53, Stenotic)
    "vessel_lcx": (0.09, 0.71, 0.63, 1.0),        # Teal / Cyan-green (prob = 0.13, Normal)
    "vessel_rca": (0.73, 0.72, 0.11, 1.0),        # Warm gold / Yellow (prob = 0.4005, Stenotic)
}

# True anatomical assembly center
CENTER_X = 23.09
CENTER_Y = -128.55
CENTER_Z = 1233.94

def transform_to_viewer_coords(verts):
    """
    Centers the mesh around anatomical heart centroid:
    X: Left-Right (Positive X = Patient Left, Negative X = Patient Right)
    Y: Anterior-Posterior (Negative Y = Anterior, Positive Y = Posterior)
    Z: Superior-Inferior (Positive Z = Superior / Base, Negative Z = Inferior / Apex)
    """
    v = verts.copy()
    v[:, 0] -= CENTER_X
    v[:, 1] -= CENTER_Y
    v[:, 2] -= CENTER_Z
    return v

def render_view(scene, elev, azim, title, filename):
    fig = plt.figure(figsize=(10, 10), facecolor="#090d16")
    ax = fig.add_subplot(111, projection="3d", facecolor="#090d16")
    
    # Hide axes background and grid for clean cinematic presentation
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    ax.axis("off")

    # Render background walls first, then great vessels, then coronaries on top
    render_order = [
        "struct_septum",
        "struct_myocardium",
        "struct_auricles",
        "struct_aorta_ascending",
        "struct_aorta_bulb",
        "struct_pulmonary_trunk",
        "struct_left_main",
        "vessel_lcx",
        "vessel_rca",
        "vessel_lad",
    ]

    for name in render_order:
        if name not in scene.geometry:
            continue
        mesh = scene.geometry[name]
        verts = transform_to_viewer_coords(mesh.vertices)
        faces = mesh.faces
        
        # Subsample faces if dense for faster plotting
        if len(faces) > 2500:
            step = max(1, len(faces) // 2500)
            faces = faces[::step]
            
        triangles = verts[faces]
        color = COLOR_MAP.get(name, (0.7, 0.7, 0.7, 0.5))
        
        poly = Poly3DCollection(
            triangles,
            facecolors=color,
            edgecolors=(color[0]*0.8, color[1]*0.8, color[2]*0.8, color[3]*0.3),
            linewidths=0.15,
            alpha=color[3]
        )
        ax.add_collection3d(poly)

    # Set coordinate limits centered around heart origin
    limit = 65
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_zlim(-limit, limit)
    
    # Set camera elevation and azimuth
    ax.view_init(elev=elev, azim=azim)

    # Add clinical title and annotations
    fig.text(0.5, 0.94, f"CoroVista — {title}", ha="center", va="top", color="#f8fafc", fontsize=15, weight="bold")
    fig.text(0.5, 0.90, "Reconstructed BodyParts3D Complete Heart Assembly", ha="center", va="top", color="#94a3b8", fontsize=11)
    
    # Legend
    legend_text = (
        "LAD (Anterior): 53.0% (Stenotic) [Amber]  |  "
        "LCX (Circumflex): 13.0% (Normal) [Teal]  |  "
        "RCA (Right Coronary): 40.1% (Stenotic, θ=0.38) [Gold]"
    )
    fig.text(0.5, 0.05, legend_text, ha="center", va="bottom", color="#cbd5e1", fontsize=9, fontfamily="monospace")

    out_path = OUTPUT_DIR / filename
    plt.tight_layout()
    plt.savefig(out_path, dpi=180, facecolor=fig.get_facecolor(), edgecolor="none", bbox_inches="tight")
    plt.close(fig)
    print(f"Rendered {out_path} (elev={elev}, azim={azim})")

def main():
    print(f"Loading {GLB_PATH}...")
    scene = trimesh.load(GLB_PATH, process=False)
    
    # In matplotlib with Z upright:
    # azim=-90 looks from -Y (Anterior) towards +Y (Posterior)
    # azim=90 looks from +Y (Posterior) towards -Y (Anterior)
    print("Rendering Anterior (AP) View...")
    render_view(scene, elev=15, azim=-90, title="Anterior (AP) View", filename="anterior_view.png")

    print("Rendering Posterior View...")
    render_view(scene, elev=15, azim=90, title="Posterior View", filename="posterior_view.png")

    print("Rendering Lateral (LAO) View...")
    render_view(scene, elev=15, azim=-45, title="Lateral (LAO) View", filename="lateral_view.png")

    print("Rendering Right Anterior Oblique (RAO) View...")
    render_view(scene, elev=15, azim=-135, title="Right Anterior Oblique (RAO) View", filename="rao_view.png")

    print("All anatomical views successfully rendered to docs/screenshots/")

if __name__ == "__main__":
    main()
