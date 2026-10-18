import re

with open('pcbs/curcur40/left/curcur40-left.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

for u in ['7948b160-acc5-4b1d-9d8b-e5b1c2f6d66b', '0861c061-bd36-48be-8fe3-08e9fcb91427']:
    p = re.compile(rf'\t\(segment\b.*?\buuid \"{u}\"\)\n\t\)\n', re.DOTALL)
    text = p.sub('', text)
    print(f'Removed {u}')

with open('pcbs/curcur40/left/curcur40-left.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved left PCB.")
