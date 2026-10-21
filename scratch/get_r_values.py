import re

with open('pcbs/curcur40/right/curcur40-right.kicad_sch', encoding='utf-8') as f:
    text = f.read()

for r in ['R1', 'R2', 'R3', 'R4']:
    m = re.search(r'\(property "Reference" "' + r + r'".*?\(property "Value" "(.*?)"', text, re.DOTALL)
    if m:
        print(f'{r}: {m.group(1)}')
