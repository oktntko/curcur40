import re
from pathlib import Path

pcb = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")
for ref in ["rR1", "rC1", "rD1"]:
    pattern = rf'\(property\s+"Reference"\s+"{ref}"\s+'
    m = re.search(pattern, pcb)
    if not m: continue
    pos = m.start()
    f_start = pcb.rfind("(footprint", 0, pos)
    c, f_end = 0, f_start
    while f_end < len(pcb):
        if pcb[f_end] == '(': c += 1
        elif pcb[f_end] == ')':
            c -= 1
            if c == 0: break
        f_end += 1
    fp = pcb[f_start:f_end+1]
    for line in fp.splitlines():
        if "sheet" in line or "path" in line:
            print(f"{ref}: {line.strip()}")
