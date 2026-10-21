from pathlib import Path
import re

pcb = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")
for ref in ['rU1', 'rSW1', 'rEXSW1', 'U1', 'R1']:
    pos = pcb.find(f'(property "Reference" "{ref}"')
    if pos == -1: continue
    start = pcb.rfind('(footprint', 0, pos)
    count, end = 0, start
    while end < len(pcb):
        if pcb[end] == '(': count += 1
        elif pcb[end] == ')':
            count -= 1
            if count == 0: break
        end += 1
    blk = pcb[start:end+1]
    path_m = re.search(r'\(path\s+"([^"]+)"\)', blk)
    sheet_m = re.search(r'\(sheetfile\s+"([^"]+)"\)', blk)
    p = path_m.group(1) if path_m else ""
    s = sheet_m.group(1) if sheet_m else ""
    print(f"[{ref}] path: {p} | sheet: {s}")
