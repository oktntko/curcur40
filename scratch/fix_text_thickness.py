import re

# Fix Left R4 text thickness: change (thickness 0.05) to (thickness 0.1) in R4
with open('pcbs/curcur40/left/curcur40-left.kicad_pcb', 'r', encoding='utf-8') as f:
    left = f.read()

# Find R4 reference property
r4_match = re.search(r'\(property \"Reference\" \"R4\".*?\(effects.*?\)', left, re.DOTALL)
if r4_match:
    old_r4 = r4_match.group(0)
    new_r4 = old_r4.replace('(thickness 0.05)', '(thickness 0.1)')
    left = left.replace(old_r4, new_r4)
    print("Fixed Left R4 text thickness")

with open('pcbs/curcur40/left/curcur40-left.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(left)

# Fix Right rC8, rC15, rC5, rR5, rC13, rR4, rC12 text thickness
with open('pcbs/curcur40/right/curcur40-right.kicad_pcb', 'r', encoding='utf-8') as f:
    right = f.read()

right_refs = ['rC8', 'rC15', 'rC5', 'rR5', 'rC13', 'rR4', 'rC12']
for r in right_refs:
    m = re.search(rf'\(property \"Reference\" \"{r}\".*?\(effects.*?\)', right, re.DOTALL)
    if m:
        old_txt = m.group(0)
        new_txt = old_txt.replace('(thickness 0.05)', '(thickness 0.1)')
        right = right.replace(old_txt, new_txt)
        print(f"Fixed Right {r} text thickness")

with open('pcbs/curcur40/right/curcur40-right.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(right)

print("Updated text thickness on both PCBs successfully.")
