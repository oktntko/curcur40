from pathlib import Path
import re

pcb = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")
fps = ["U1", "U2", "JP1", "R1", "R2", "R3", "R4", "C1", "C2", "C3", "C4", "C5"]
for ref in fps:
    pos = pcb.find(f'"{ref}"')
    f_start = pcb.rfind('(footprint', 0, pos)
    m = re.search(r'\(layer\s+"([^"]+)"\)', pcb[f_start:pos+50])
    m_at = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)(?:\s+([\d\.\-]+))?\)', pcb[f_start:pos+50])
    print(f"{ref:4}: layer={m.group(1) if m else '?'} at={m_at.groups() if m_at else '?'}")
