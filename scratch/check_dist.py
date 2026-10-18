import json

with open('scratch/Left_tnc.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

for v in d.get('violations', []):
    if v.get('type') == 'track_not_centered_on_via':
        items = v.get('items', [])
        p1 = items[0].get('pos', {})
        p2 = items[1].get('pos', {})
        dx = (p1['x'] - p2['x']) * 1000
        dy = (p1['y'] - p2['y']) * 1000
        dist_um = (dx**2 + dy**2)**0.5
        print(f"{dist_um:.3f} um: {items[0].get('description')}")
