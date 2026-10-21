import re
from pathlib import Path

pmw_pcb = Path("pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pcb").read_text(encoding="utf-8")
fps = ["U1", "U2", "JP1"]
for ref in fps:
    pos = pmw_pcb.find(f'"{ref}"')
    f_start = pmw_pcb.rfind("(footprint", 0, pos)
    c, f_end = 0, f_start
    while f_end < len(pmw_pcb):
        if pmw_pcb[f_end] == '(': c += 1
        elif pmw_pcb[f_end] == ')':
            c -= 1
            if c == 0: break
        f_end += 1
    fp = pmw_pcb[f_start:f_end+1]
    for line in fp.splitlines():
        if "sheet" in line or "path" in line:
            print(f"{ref}: {line.strip()}")
