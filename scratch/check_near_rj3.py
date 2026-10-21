from pathlib import Path
import re

sch = Path("pcbs/curcur40/right/curcur40-right.kicad_sch").read_text(encoding="utf-8")

# find all symbols
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

    m_at = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', blk)
    m_ref = re.search(r'\(property\s+\"Reference\"\s+\"([^\"]+)\"', blk)
    if m_at and m_ref:
        x, y = float(m_at.group(1)), float(m_at.group(2))
        dist = ((x - 303.53)**2 + (y - 44.45)**2)**0.5
        if dist < 80:
            print(f"  [{m_ref.group(1)}] at ({x}, {y}), dist={dist:.1f}mm")
