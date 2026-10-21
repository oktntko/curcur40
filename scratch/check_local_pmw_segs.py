from pathlib import Path
import re

pcb = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")

# Let's find ALL segments where sx or ex is between 0 and 20, and sy or ey is between 40 and 65
all_local_segs = []
for m in re.finditer(r'\(segment\s+\(start\s+([\d\.\-]+)\s+([\d\.\-]+)\)\s+\(end\s+([\d\.\-]+)\s+([\d\.\-]+)\)\s+\(width[^)]*\)\s+\(layer\s+\"([^\"]+)\"\)\s+\(net\s+\"([^\"]+)\"\)', pcb):
    sx, sy, ex, ey, layer, net = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), m.group(5), m.group(6)
    if (0 <= sx <= 20 and 40 <= sy <= 65) or (0 <= ex <= 20 and 40 <= ey <= 65):
        all_local_segs.append((net, layer, sx, sy, ex, ey))

print(f"Total local segments found: {len(all_local_segs)}")
for s in all_local_segs:
    print(f"  {s[0]:15} | {s[1]:5}: ({s[2]:7.3f}, {s[3]:7.3f}) -> ({s[4]:7.3f}, {s[5]:7.3f})")
