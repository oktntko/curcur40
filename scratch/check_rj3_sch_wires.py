from pathlib import Path
import re

sch = Path("pcbs/curcur40/right/curcur40-right.kicad_sch").read_text(encoding="utf-8")

# Find rJ3 position
pos = sch.find('"rJ3"')
start = sch.rfind('(symbol', 0, pos)
count, end = 0, start
while end < len(sch):
    if sch[end] == '(': count += 1
    elif sch[end] == ')':
        count -= 1
        if count == 0: break
    end += 1

rj3_block = sch[start:end+1]
print("=== rJ3 block in right sch ===")
print(rj3_block)

# Look at wires near rJ3 at (at 303.53 44.45 180)
print("\n=== Wires and labels near (303.53, 44.45) ===")
for m in re.finditer(r'\(wire\s+\(pts\s+\(xy\s+([\d\.\-]+)\s+([\d\.\-]+)\)\s+\(xy\s+([\d\.\-]+)\s+([\d\.\-]+)\)\)\s+\(stroke[^)]*\)\s+\(uuid\s+\"([^\"]+)\"\)\)', sch):
    x1, y1, x2, y2 = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
    if 290 <= x1 <= 320 and 30 <= y1 <= 60:
        print(f"  wire ({x1}, {y1}) -> ({x2}, {y2})")

for m in re.finditer(r'\((?:global_label|hierarchical_label|label)\s+\"([^\"]+)\"[^)]*\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', sch):
    name, lx, ly = m.group(1), float(m.group(2)), float(m.group(3))
    if 290 <= lx <= 320 and 30 <= ly <= 60:
        print(f"  label '{name}' at ({lx}, {ly})")
