import json

with open('scratch/drc_perfect.json', encoding='utf-8') as f:
    d = json.load(f)

violations = d.get('violations', [])

for i, v in enumerate(violations):
    t = v.get('type')
    # only electrical/copper
    if t in ['shorting_items', 'tracks_crossing', 'clearance', 'copper_edge_clearance', 'track_dangling', 'via_dangling']:
        print(f"=== [{i+1}] {t} ===")
        print(f"Desc: {v.get('description')}")
        for it in v.get('items', []):
            print(f"  - {it.get('description')} (pos: {it.get('pos')})")
