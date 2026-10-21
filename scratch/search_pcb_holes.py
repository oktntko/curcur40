import re
from pathlib import Path

pcb = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")
for line in pcb.splitlines():
    if "2.2" in line or "drill" in line or "circle" in line:
        if "pad" in line or "fp_circle" in line or "gr_circle" in line:
            print(line.strip())
