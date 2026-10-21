import re
from pathlib import Path

sch = Path("pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_sch").read_text(encoding="utf-8")
fps = ["U1", "U2", "JP1", "R1", "R2", "R3", "R4", "C1", "C2", "C3", "C4", "C5"]

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
    m_val = re.search(r'\(property\s+"Value"\s+"([^"]+)"', sym)
    m_fp = re.search(r'\(property\s+"Footprint"\s+"([^"]+)"', sym)
    m_lcsc = re.search(r'\(property\s+"JLCPCB Part #"\s+"([^"]+)"', sym)
    m_lib = re.search(r'\(lib_id\s+"([^"]+)"', sym)
    m_u = re.search(r'\(uuid\s+"([^"]+)"\)', sym)
    print(f"{ref:4}: {m_val.group(1) if m_val else ''} | {m_fp.group(1) if m_fp else ''} | LCSC={m_lcsc.group(1) if m_lcsc else 'None'} | lib={m_lib.group(1) if m_lib else ''} | uuid={m_u.group(1) if m_u else ''}")
