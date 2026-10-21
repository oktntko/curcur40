import re
from pathlib import Path

sch = Path("pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_sch").read_text(encoding="utf-8")
pcb = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")

fps = ["U1", "U2", "JP1", "R1", "R2", "R3", "R4", "C1", "C2", "C3", "C4", "C5"]

for ref in fps:
    # sch uuid
    m_s = re.search(rf'\(symbol[^\)]+?\(uuid\s+"([^"]+)"\)\s+\(property\s+"Reference"\s+"{ref}"', sch, re.DOTALL)
    if not m_s:
        # try matching Reference first
        pos = sch.find(f'"{ref}"')
        s_start = sch.rfind('(symbol', 0, pos)
        m_u = re.search(r'\(uuid\s+"([^"]+)"\)', sch[s_start:pos])
        sch_uuid = m_u.group(1) if m_u else "?"
    else:
        sch_uuid = m_s.group(1)

    # pcb uuid
    pos_p = pcb.find(f'"{ref}"')
    p_start = pcb.rfind('(footprint', 0, pos_p)
    m_pu = re.search(r'\(uuid\s+"([^"]+)"\)', pcb[p_start:pos_p])
    pcb_uuid = m_pu.group(1) if m_pu else "?"

    # path property or sheetfile in pcb
    p_end = pcb.find(')', pos_p + 200)
    path_m = re.search(r'\(path\s+"([^"]+)"\)', pcb[pos_p:pos_p+300])
    pcb_path = path_m.group(1) if path_m else "?"

    print(f"{ref:5}: SCH={sch_uuid} | PCB={pcb_uuid} | Match={sch_uuid == pcb_uuid} | PCB_path={pcb_path}")
