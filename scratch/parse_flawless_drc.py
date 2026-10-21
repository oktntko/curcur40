import json

with open('scratch/drc_flawless.json', encoding='utf-8') as f:
    d = json.load(f)

unconnected = d.get('unconnected_items', [])
print(f'Unconnected items: {len(unconnected)}')
for u in unconnected:
    print(f"  - {u.get('description')}")
    for it in u.get('items', []):
        print(f"      {it.get('description')} at {it.get('pos')}")

violations = d.get('violations', [])
print(f'\nTotal violations: {len(violations)}')
type_counts = {}
for v in violations:
    t = v.get('type', 'unknown')
    type_counts[t] = type_counts.get(t, 0) + 1

for t, count in sorted(type_counts.items()):
    print(f'  {t}: {count}')

print('\nElectrical / Clearance / Short violations:')
copper_types = {'clearance', 'shorting_items', 'tracks_crossing', 'hole_clearance', 'copper_edge_clearance', 'via_dangling'}
found_copper = 0
for i, v in enumerate(violations):
    t = v.get('type')
    if t in copper_types or 'clearance' in t or 'short' in t or 'crossing' in t:
        found_copper += 1
        print(f"[{i+1}] [{v.get('type')}] {v.get('description')}")
        for item in v.get('items', []):
            print(f"     - {item.get('description')} at {item.get('pos')}")

print(f'\nTotal copper/electrical issues found: {found_copper}')
