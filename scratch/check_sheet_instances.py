import re
from pathlib import Path

sch = Path("pcbs/curcur40/right/curcur40-right.kicad_sch").read_text(encoding="utf-8")
pos = sch.find("sheet_instances")
if pos != -1:
    print(sch[pos-50:pos+200])
else:
    print("sheet_instances not found")
