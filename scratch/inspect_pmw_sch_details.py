from pathlib import Path
import re

sch = Path("pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_sch").read_text(encoding="utf-8")

# Let's extract all labels and their locations
print("=== LABELS IN PMW SCH ===")
for m in re.finditer(r'\((?:global_label|hierarchical_label|label)\s+\"([^\"]+)\"[^)]*\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', sch):
    print(f"  Label '{m.group(1)}' at ({m.group(2)}, {m.group(3)})")

# Let's extract all power symbols (GND, VDD, etc.)
print("\n=== POWER SYMBOLS IN PMW SCH ===")
s_idx = 0
while True:
    pos = sch.find("(symbol\n", s_idx)
    if pos == -1: break
    count, end = 0, pos
    while end < len(sch):
        if sch[end] == '(': count += 1
        elif sch[end] == ')':
            count -= 1
            if count == 0: break
        end += 1
    blk = sch[pos:end+1]
    s_idx = end + 1
    m_ref = re.search(r'\(property\s+\"Reference\"\s+\"([^\"]+)\"', blk)
    m_val = re.search(r'\(property\s+\"Value\"\s+\"([^\"]+)\"', blk)
    m_at = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', blk)
    ref = m_ref.group(1) if m_ref else ""
    val = m_val.group(1) if m_val else ""
    at = (m_at.group(1), m_at.group(2)) if m_at else ("", "")
    if ref.startswith('#PWR'):
        print(f"  Power {ref}: {val} at {at}")
