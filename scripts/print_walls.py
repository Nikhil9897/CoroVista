import json

with open('scripts/detailed_anatomy_audit.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

print("=== ALL WALL, ATRIUM, AURICLE, VENTRICLE MESHES ===")
for it in items:
    name = it['name'].lower()
    if any(k in name for k in ['wall', 'atrium', 'auricle', 'ventricle']):
        bmin = [round(x, 1) for x in it['bounds_min']]
        bmax = [round(x, 1) for x in it['bounds_max']]
        dims = [round(x, 1) for x in it['dims']]
        print(f"[{it['mm_id']:6s}] {it['name']:<50s} | {it['verts']:5d}v {it['faces']:5d}f | X:{bmin}..{bmax} | dims:{dims}")
