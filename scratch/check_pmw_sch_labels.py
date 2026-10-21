import re
from pathlib import Path

sch = Path("pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_sch").read_text(encoding="utf-8")

# Let's inspect the labels and wires in pmw sch
for line in sch.splitlines():
    if "label" in line:
        print(line.strip())
