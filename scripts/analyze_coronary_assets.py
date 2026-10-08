"""
CoroVista - In-depth Analysis of Coronary Arteries and Context Structures
"""

import json
from pathlib import Path

def main():
    with open("scripts/obj_inventory_raw.json", "r", encoding="utf-8") as f:
        items = json.load(f)

    print(f"Total items: {len(items)}")

    # 1. Global coordinate bounds
    all_min_x = min(item["bounds"]["min"][0] for item in items if item["bounds"])
    all_max_x = max(item["bounds"]["max"][0] for item in items if item["bounds"])
    all_min_y = min(item["bounds"]["min"][1] for item in items if item["bounds"])
    all_max_y = max(item["bounds"]["max"][1] for item in items if item["bounds"])
    all_min_z = min(item["bounds"]["min"][2] for item in items if item["bounds"])
    all_max_z = max(item["bounds"]["max"][2] for item in items if item["bounds"])

    print(f"Global Bounding Box: X=[{all_min_x}, {all_max_x}], Y=[{all_min_y}, {all_max_y}], Z=[{all_min_z}, {all_max_z}]")
    print(f"Global Dimensions: dX={all_max_x - all_min_x:.1f}, dY={all_max_y - all_min_y:.1f}, dZ={all_max_z - all_min_z:.1f} mm")

    # 2. Coronary artery assets
    print("\n" + "="*80)
    print("CORONARY ARTERY ASSETS")
    print("="*80)
    coronary_arteries = []
    for item in items:
        name_l = item["anatomical_name"].lower()
        if any(k in name_l for k in ["coronary", "interventricular", "circumflex", "diagonal", "septal branch", "marginal artery"]):
            # Filter out veins
            if "vein" not in name_l and "sinus" not in name_l:
                coronary_arteries.append(item)
                b = item["bounds"]
                print(f"{item['mm_id']} | {item['bp_id']} | {item['fma_id']} | verts: {item['vertex_count']:5d} | faces: {item['face_count']:5d} | size: {item['file_size_kb']:6.1f}KB")
                print(f"    Name:   {item['anatomical_name']}")
                print(f"    Bounds: X=[{b['min'][0]}, {b['max'][0]}], Y=[{b['min'][1]}, {b['max'][1]}], Z=[{b['min'][2]}, {b['max'][2]}]")
                print(f"    Center: {b['center']}, Dims: {b['dimensions']}")
                print("-" * 60)

    # 3. LAD trunk comparison
    print("\n" + "="*80)
    print("LAD TRUNK COMPARISON (MM420, MM424, MM425)")
    print("="*80)
    lad_trunks = [it for it in items if it["mm_id"] in ["MM420", "MM424", "MM425"]]
    for item in lad_trunks:
        b = item["bounds"]
        print(f"{item['mm_id']} | verts: {item['vertex_count']} | faces: {item['face_count']} | size: {item['file_size_kb']}KB")
        print(f"    X: {b['min'][0]} to {b['max'][0]} (dX={b['dimensions'][0]})")
        print(f"    Y: {b['min'][1]} to {b['max'][1]} (dY={b['dimensions'][1]})")
        print(f"    Z: {b['min'][2]} to {b['max'][2]} (dZ={b['dimensions'][2]})")
        print(f"    Center: {b['center']}")

    # 4. RCA trunk comparison
    print("\n" + "="*80)
    print("RCA TRUNK COMPARISON (MM436, MM439, MM556)")
    print("="*80)
    rca_trunks = [it for it in items if it["mm_id"] in ["MM436", "MM439", "MM556"]]
    for item in rca_trunks:
        b = item["bounds"]
        print(f"{item['mm_id']} | verts: {item['vertex_count']} | faces: {item['face_count']} | size: {item['file_size_kb']}KB")
        print(f"    X: {b['min'][0]} to {b['max'][0]} (dX={b['dimensions'][0]})")
        print(f"    Y: {b['min'][1]} to {b['max'][1]} (dY={b['dimensions'][1]})")
        print(f"    Z: {b['min'][2]} to {b['max'][2]} (dZ={b['dimensions'][2]})")
        print(f"    Center: {b['center']}")

    # 5. LCX trunk comparison
    print("\n" + "="*80)
    print("LCX TRUNK COMPARISON (MM426 vs MM635)")
    print("="*80)
    lcx_trunks = [it for it in items if it["mm_id"] in ["MM426", "MM635"]]
    for item in lcx_trunks:
        b = item["bounds"]
        print(f"{item['mm_id']} | verts: {item['vertex_count']} | faces: {item['face_count']} | size: {item['file_size_kb']}KB")
        print(f"    X: {b['min'][0]} to {b['max'][0]} (dX={b['dimensions'][0]})")
        print(f"    Y: {b['min'][1]} to {b['max'][1]} (dY={b['dimensions'][1]})")
        print(f"    Z: {b['min'][2]} to {b['max'][2]} (dZ={b['dimensions'][2]})")
        print(f"    Center: {b['center']}")

    # 6. Aorta & Context Structures
    print("\n" + "="*80)
    print("AORTA & HEART CONTEXT STRUCTURES")
    print("="*80)
    context_keywords = ["aorta", "pulmonary trunk", "ventricle", "atrium", "septum"]
    for item in items:
        name_l = item["anatomical_name"].lower()
        if any(k in name_l for k in ["aorta", "pulmonary trunk"]):
            b = item["bounds"]
            print(f"{item['mm_id']} | {item['anatomical_name']} | verts: {item['vertex_count']} | bounds: {b['min']} to {b['max']}")

if __name__ == "__main__":
    main()
