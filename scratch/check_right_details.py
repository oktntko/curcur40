import re
from pathlib import Path

sch = Path("pcbs/curcur40/right/curcur40-right.kicad_sch").read_text(encoding="utf-8")
print("=== Symbols in curcur40-right.kicad_sch ===")
# find all (symbol ... (property "Reference" "XYZ")
symbols = re.findall(r'\(property\s+\"Reference\"\s+\"([^\"]+)\"', sch)
for ref in set(symbols):
    if any(k in ref.lower() for k in ['u', 'j', 'exsw', 'r1', 'r2', 'r3', 'r4', 'c1', 'c2', 'c3', 'c4', 'c5']):
        print(f"  Ref: {ref}")

print("\n=== Check if rJ3 is in schematic ===")
print("rJ3 in sch:", "rJ3" in sch)

print("\n=== Check footprints on curcur40-right.kicad_pcb ===")
pcb = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")
print("rJ3 in pcb:", "rJ3" in pcb)
print("PMW3360 in pcb:", "PMW3360" in pcb)
