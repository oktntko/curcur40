with open('pcbs/curcur40/right/curcur40-right.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's check what is at U1 pin 32 (GPIO21) on Right schematic
# U1 on right:
import re
u1_idx = text.find('(property "Reference" "U1"')
u1_start = text.rfind('(symbol', 0, u1_idx)
print(text[u1_start:u1_start+300])

for line in text.splitlines():
    if '111.76' in line and '181.61' in line:
        print(line)
