from pathlib import Path
import re

sch = Path("pcbs/curcur40/right/curcur40-right.kicad_sch").read_text(encoding="utf-8")

# Let's find all symbols in curcur40-right.kicad_sch with X > 250 and Y < 100
for m in re.finditer(r'\(symbol\s+[^)]*\(at\s+([\d\.\-]+)\s+([\d\.\-]+)[^)]*\)[^)]*\(property\s+\"Reference\"\s+\"([^\"]+)\"', sch):
    x, y, ref = float(m.group(1)), float(m.group(2)), m.group(3)
    if x > 250 and y < 100:
        print(f"  [{ref:10}] at ({x}, {y})")

# Also check paper size of curcur40-right.kicad_sch
m_paper = re.search(r'\(paper\s+\"([^\"]+)\"\)', sch)
print("Paper size:", m_paper.group(1) if m_paper else "unknown")
