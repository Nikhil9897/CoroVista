import os
import json
import re
from pathlib import Path
import numpy as np

# Load raw inventory
with open("scripts/obj_inventory_raw.json", "r", encoding="utf-8") as f:
    inventory = json.load(f)

by_mm = {item["mm_id"]: item for item in inventory}

# Filter by anatomical keywords
keywords = ["wall", "ventricle", "atrium", "auricle", "septum", "myocardium", "aorta", "pulmonary"]

print(f"Total inventory items: {len(inventory)}")

wall_items = []
for item in inventory:
    name = item["anatomical_name"].lower()
    if any(k in name for k in ["wall", "auricle", "ventricle", "atrium", "septum"]):
        # exclude valves/muscles/vessels if needed or keep for inspection
        wall_items.append(item)

print(f"\nDiscovered {len(wall_items)} chamber wall / myocardial / septal candidates:")
for item in sorted(wall_items, key=lambda x: x["mm_id"]):
    b = item["bounds"]
    dims = b["dimensions"] if b else [0,0,0]
    center = b["center"] if b else [0,0,0]
    print(f"[{item['mm_id']}] {item['anatomical_name']} | verts: {item['vertex_count']}, faces: {item['face_count']} | size: {item['file_size_kb']}KB | dims: {dims} | center: {center}")

# Specific candidate analysis
candidates = [
    "MM474", "MM631", "MM614", "MM615", "MM616", "MM620", "MM624", # LV
    "MM538", "MM598", # RV
    "MM559", "MM560", "MM461", # RA
    "MM456", "MM458", "MM459", "MM460", "MM632", "MM633", # LA
    "MM600", "MM594", "MM613", "MM618", "MM619", "MM625", "MM629", # Septum
    "MM558", "MM506", "MM607", # Great vessels
    "MM557", # Left main
]

print("\n--- DETAILED CANDIDATE INSPECTION ---")
for cid in candidates:
    if cid in by_mm:
        c = by_mm[cid]
        b = c["bounds"]
        print(f"{cid:6s} | {c['bp_id']} | {c['fma_id']} | verts: {c['vertex_count']:5d} | {c['anatomical_name']}")
        if b:
            print(f"       Bounds: X[{b['min'][0]:.1f}, {b['max'][0]:.1f}] Y[{b['min'][1]:.1f}, {b['max'][1]:.1f}] Z[{b['min'][2]:.1f}, {b['max'][2]:.1f}] Dims: {b['dimensions']}")
