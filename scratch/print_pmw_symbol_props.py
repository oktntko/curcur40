from pathlib import Path
import re

sch = Path("pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_sch").read_text(encoding="utf-8")

s_idx = 0
while True:
    pos = sch.find("(symbol\n", s_idx)
    if pos == -1: break
    count, end = 0, pos
    while end < len(sch):
        if sch[end] == '(': count += 1
        elif sch[end] == ')':
            count -= 1
            if count == 0: break
        end += 1
    blk = sch[pos:end+1]
    s_idx = end + 1

    m_ref = re.search(r'\(property\s+\"Reference\"\s+\"([^\"]+)\"', blk)
    ref = m_ref.group(1) if m_ref else ""
    if ref in ['U1', 'U2', 'JP1', 'R1', 'R2', 'R3', 'R4', 'C1', 'C2', 'C3', 'C4', 'C5']:
        print(f"=== Symbol [{ref}] ===")
        # print all properties
        for m_prop in re.finditer(r'\(property\s+\"([^\"]+)\"\s+\"([^\"]*)\"', blk):
            print(f"  {m_prop.group(1):15}: {m_prop.group(2)}")
