import re
from pathlib import Path

sch = Path("pcbs/curcur40/right/curcur40-right.kicad_sch").read_text(encoding="utf-8")
pcb = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")

print("In SCH:")
for sig in ["RESET", "MOTION", "NCS", "CS", "SCLK", "MOSI", "MISO"]:
    count_sch = len(re.findall(rf'\b{sig}\b', sch))
    count_pcb = len(re.findall(rf'\b{sig}\b', pcb))
    print(f"  {sig:10}: sch={count_sch}, pcb={count_pcb}")
