import re
from pathlib import Path

sch = Path("pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_sch").read_text(encoding="utf-8")
fps = ["U1", "U2", "JP1", "R1"]
for ref in fps:
    pos = sch.find(f'"{ref}"')
    s_start = sch.rfind('(symbol', 0, pos)
    c, s_end = 0, s_start
    while s_end < len(sch):
        if sch[s_end] == '(': c += 1
        elif sch[s_end] == ')':
            c -= 1
            if c == 0: break
        s_end += 1
    sym = sch[s_start:s_end+1]
    m_inst = re.search(r'\(instances.*?\n\t\)', sym, re.DOTALL)
    print(f"=== {ref} ===")
    if m_inst:
        print(m_inst.group(0))
    else:
        print("No instances found")
