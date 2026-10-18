import pcbnew
import json
import subprocess

# Let's inspect all dangling tracks reported by DRC
cmd = [
    r'C:\Users\oktnt\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe',
    'pcb', 'drc',
    '--severity-all',
    '--format', 'json',
    '-o', 'scratch/dangling_test.json',
    'pcbs/curcur40/left/curcur40-left.kicad_pcb'
]
subprocess.run(cmd, check=True)

with open('scratch/dangling_test.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

dangling = [v for v in d.get('violations', []) if v.get('type') == 'track_dangling']
print(f"Found {len(dangling)} dangling track violations on Left PCB:")
for v in dangling:
    for it in v.get('items', []):
        print(" ", it.get('uuid'), it.get('description'), it.get('pos'))
