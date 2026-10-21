import re
from pathlib import Path

pcb = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")
pos_p = pcb.find('"rU1"')
p_start = pcb.rfind("(footprint", 0, pos_p)
print(pcb[p_start+1000:p_start+1500])
