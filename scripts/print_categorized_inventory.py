import json

with open("scripts/detailed_anatomy_audit.json", "r", encoding="utf-8") as f:
    items = json.load(f)

print(f"Total items: {len(items)}\n")

categories = {
    "Vessels & Arteries": [],
    "Chamber Walls & Free Walls": [],
    "Atrial Structures & Auricles": [],
    "Septal Structures": [],
    "Great Vessels": [],
    "Internal Structures (Papillary/Trabeculae/Valves/Nodes)": [],
    "Other": []
}

for item in items:
    name = item["name"].lower()
    mid = item["mm_id"]
    if any(k in name for k in ["artery", "branch", "coronary", "trunk of anterior", "trunk of circumflex", "trunk of right", "vein", "sinus"]):
        categories["Vessels & Arteries"].append(item)
    elif "aorta" in name or "pulmonary" in name:
        categories["Great Vessels"].append(item)
    elif "auricle" in name or "atrium" in name:
        categories["Atrial Structures & Auricles"].append(item)
    elif "septum" in name or "septal" in name:
        categories["Septal Structures"].append(item)
    elif "free wall" in name or "wall of" in name or "ventricle" in name:
        categories["Chamber Walls & Free Walls"].append(item)
    elif any(k in name for k in ["papillary", "trabecula", "valve", "cusp", "leaflet", "node", "bundle", "crest", "trigone"]):
        categories["Internal Structures (Papillary/Trabeculae/Valves/Nodes)"].append(item)
    else:
        categories["Other"].append(item)

for cat, list_items in categories.items():
    print(f"=== {cat} ({len(list_items)} assets) ===")
    for it in list_items:
        bmin = [round(x, 1) for x in it["bounds_min"]]
        bmax = [round(x, 1) for x in it["bounds_max"]]
        dims = [round(x, 1) for x in it["dims"]]
        print(f"  [{it['mm_id']:6s}] {it['name']:<50s} | {it['verts']:5d}v {it['faces']:5d}f | X:[{bmin[0]},{bmax[0]}] Y:[{bmin[1]},{bmax[1]}] Z:[{bmin[2]},{bmax[2]}] | dims:{dims}")
    print()
