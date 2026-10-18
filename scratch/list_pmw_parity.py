import json

with open('scratch/pmw_parity_drc.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

for v in d.get('violations', []):
    print(v.get('type'), ':', v.get('description'), '-->', [it.get('description') for it in v.get('items', [])])
