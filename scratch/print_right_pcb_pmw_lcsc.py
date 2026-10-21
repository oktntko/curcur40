import re
from pathlib import Path

pcb = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")
fps = ["U1", "U2", "JP1", "R1", "R2", "R3", "R4", "C1", "C2", "C3", "C4", "C5"]

for ref in fps:
    pattern = rf'\(property\s+"Reference"\s+"{ref}"\s+'
    m = re.search(pattern, pcb)
    pos = m.start()
    f_start = pcb.rfind("(footprint", 0, pos)
    count, f_end = 0, f_start
    while f_end < len(pcb):
        if pcb[f_end] == '(': count += 1
        elif pcb[f_end] == ')':
            count -= 1
            if count == 0: break
        f_end += 1
    fp = pcb[f_start:f_end+1]
    m_val = re.search(r'\(property\s+"Value"\s+"([^"]+)"', fp)
    m_lcsc = re.search(r'\(property\s+"JLCPCB Part #"\s+"([^"]+)"', fp)
    print(f"{ref:4}: val={m_val.group(1) if m_val else ''} | LCSC={m_lcsc.group(1) if m_lcsc else 'None'}")
