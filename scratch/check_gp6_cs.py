from pathlib import Path
import re

pcb = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")
sch = Path("pcbs/curcur40/right/curcur40-right.kicad_sch").read_text(encoding="utf-8")

# Check RP2040 GP6 / SPI CS in schematic
print("=== GP6 in right schematic ===")
for line in sch.splitlines():
    if "GP6" in line or "/CS" in line or "/NCS" in line or "NCS" in line:
        print("  ", line.strip())

# Check all occurrences of /CS and /NCS in PCB
print("\n=== In right PCB: nets containing CS ===")
all_nets = set(re.findall(r'\(net\s+\"([^\"]*CS[^\"]*)\"\)', pcb))
print("  Nets found:", all_nets)

# Check segments of /CS vs /NCS
for net in all_nets:
    segs = len(re.findall(rf'\(net\s+\"{re.escape(net)}\"\)', pcb))
    print(f"  Net '{net}' has {segs} occurrences in PCB")
