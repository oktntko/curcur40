import pcbnew
import json
import subprocess

with open('pcbs/curcur40/left/curcur40-left.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

def remove_item_by_uuid(content, u, item_type):
    target = f'(uuid "{u}")'
    idx = content.find(target)
    if idx == -1:
        print(f"UUID {u} not found")
        return content
    start = content.rfind(f'({item_type}', 0, idx)
    end = content.find('\n\t)', idx)
    end_pos = end + len('\n\t)')
    if end_pos < len(content) and content[end_pos] == '\n':
        end_pos += 1
    start_pos = content.rfind('\n', 0, start)
    start_pos = start if start_pos == -1 else start_pos + 1
    print(f"Removed {item_type} {u}")
    return content[:start_pos] + content[end_pos:]

# The 3 dangling vias:
# 78642824-387a-4796-926d-26f2361673d6
# e6f812af-7c59-4069-beac-2f3c6a0bc235
# 21d205c0-7f25-4551-8c7a-9f73393b24ab

for u in ['78642824-387a-4796-926d-26f2361673d6', 'e6f812af-7c59-4069-beac-2f3c6a0bc235', '21d205c0-7f25-4551-8c7a-9f73393b24ab']:
    text = remove_item_by_uuid(text, u, 'via')

# And their dead-end segments:
# 224b0f51-69f5-447d-ac50-598520467bed
# 77903f55-007d-4359-bb3a-7b8aa84bc347
for u in ['224b0f51-69f5-447d-ac50-598520467bed', '77903f55-007d-4359-bb3a-7b8aa84bc347']:
    text = remove_item_by_uuid(text, u, 'segment')

with open('pcbs/curcur40/left/curcur40-left.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(text)

cmd = [
    r'C:\Users\oktnt\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe',
    'pcb', 'drc',
    '--severity-all',
    '--format', 'json',
    '-o', 'scratch/left_drc_clean2.json',
    'pcbs/curcur40/left/curcur40-left.kicad_pcb'
]
subprocess.run(cmd, check=True)

with open('scratch/left_drc_clean2.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print("=== DRC RESULT AFTER CLEANING VIAS ===")
print("Unconnected items:", len(d.get('unconnected_items', [])))
print("Violations:", len(d.get('violations', [])))
for v in d.get('violations', []):
    print(" ", v.get('type'), ":", v.get('description'))
