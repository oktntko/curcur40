import json

with open('scratch/Left_full_audit.json', 'r', encoding='utf-8') as f:
    d_left = json.load(f)

print("=== Left text_height items ===")
for v in d_left.get('violations', []):
    if v.get('type') == 'text_height':
        for it in v.get('items', []):
            print(" ", it.get('description'))
