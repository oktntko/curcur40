import re
from pathlib import Path

pcb = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")
fps = ["U1", "U2", "JP1", "R1", "R2", "R3", "R4", "C1", "C2", "C3", "C4", "C5"]

for ref in fps:
    pattern = rf'\(property\s+"Reference"\s+"{ref}"\s+'
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
    paths = re.findall(r'\(path\s+"([^"]*)"\)', fp_text)
    sheets = re.findall(r'\(sheetfile\s+"([^"]*)"\)', fp_text)
    print(f"{ref:4}: path={paths}, sheetfile={sheets}")
