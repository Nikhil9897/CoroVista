import os
import glob
import trimesh
import numpy as np

OBJ_DIR = "OBJ Files"

def load_mesh(prefix):
    matches = glob.glob(os.path.join(OBJ_DIR, f"{prefix}_*.obj"))
    return trimesh.load(matches[0], process=False)

def inspect_mesh_structure(prefix, name):
    m = load_mesh(prefix)
    print(f"\n--- {prefix}: {name} ---")
    print(f"Verts: {len(m.vertices)}, Faces: {len(m.faces)}")
    print(f"Bounds: min={np.round(m.bounds[0], 2)}, max={np.round(m.bounds[1], 2)}")
    print(f"Extents: {np.round(m.extents, 2)}")
    print(f"Watertight: {m.is_watertight}")
    # Boundary edges
    edges = m.edges_sorted
    unique_edges, counts = np.unique(edges, axis=0, return_counts=True)
    boundary_edges = unique_edges[counts == 1]
    manifold_edges = unique_edges[counts == 2]
    nonmanifold_edges = unique_edges[counts > 2]
    print(f"Edges: total={len(edges)}, boundary (open)={len(boundary_edges)}, manifold={len(manifold_edges)}, non-manifold={len(nonmanifold_edges)}")
    
    # Check if closed or has volume
    if m.is_watertight:
        print(f"Volume: {m.volume:.2f} mm^3")
    else:
        # Check if it is a single open shell or has thickness (inner + outer surface)
        # We can check vertex normals
        v_norms = m.vertex_normals
        print(f"Vertex normals computed, shape={v_norms.shape}")

inspect_mesh_structure("MM474", "Free wall of left ventricle")
inspect_mesh_structure("MM631", "Free wall of left ventricle (subsegment)")
inspect_mesh_structure("MM598", "Wall of inflow part of RV")
inspect_mesh_structure("MM538", "Wall of outflow part of RV")
inspect_mesh_structure("MM559", "Anterior wall proper of RA")
inspect_mesh_structure("MM560", "Lateral wall proper of RA")
inspect_mesh_structure("MM461", "Wall of right auricle proper")
inspect_mesh_structure("MM632", "Anterior wall proper of LA")
inspect_mesh_structure("MM633", "Posterior wall of LA")
inspect_mesh_structure("MM459", "Wall of left auricle")
inspect_mesh_structure("MM600", "Muscular part of IV septum")
inspect_mesh_structure("MM558", "Wall of bulb of aorta")
inspect_mesh_structure("MM506", "Ascending aorta proper")
inspect_mesh_structure("MM607", "Pulmonary trunk proper")
