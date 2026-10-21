import re
from pathlib import Path

pcb = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")
pattern = r'\(property\s+"Reference"\s+"rU1"\s+'
m = re.search(pattern, pcb)
pos = m.start()
f_start = pcb.rfind("(footprint", 0, pos)
c, f_end = 0, f_start
while f_end < len(pcb):
    if pcb[f_end] == '(': c += 1
    elif pcb[f_end] == ')':
        c -= 1
        if c == 0: break
    f_end += 1

fp_text = pcb[f_start:f_end+1]
for line in fp_text.splitlines():
    if "path" in line or "sheet" in line:
        print(line.strip())
