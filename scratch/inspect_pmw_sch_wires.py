from pathlib import Path
import re

sch = Path("pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_sch").read_text(encoding="utf-8")

# Let's inspect J1 connections and nets in curcur40-pmw3360.kicad_sch
# Find wires, labels, etc.
print("=== Labels in curcur40-pmw3360.kicad_sch ===")
labels = re.findall(r'\((?:global_label|hierarchical_label|label)\s+\"([^\"]+)\"', sch)
print(set(labels))

print("\n=== Check how J1 is wired ===")
pos = sch.find('"J1"')
if pos != -1:
    s_start = sch.rfind('(symbol', 0, pos)
    count, s_end = 0, s_start
    while s_end < len(sch):
        if sch[s_end] == '(': count += 1
        elif sch[s_end] == ')':
            count -= 1
            if count == 0: break
        s_end += 1
    print(sch[s_start:s_end+1])
