import re
from pathlib import Path

pcb = Path("scratch/pmw3360_pcb_b9043a22.kicad_pcb").read_text(encoding="utf-8")
pos = pcb.find('"J1"')
f_start = pcb.rfind('(footprint', 0, pos)
m_at = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)(?:\s+([\d\.\-]+))?\)', pcb[f_start:pos+50])
print("J1 in PMW PCB:", m_at.groups() if m_at else "?")
