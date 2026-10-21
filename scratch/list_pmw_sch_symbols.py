import re
from pathlib import Path

sch = Path("pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_sch").read_text(encoding="utf-8")

def parse_blocks(b_text, tag):
    blocks = []
    idx = 0
    tag_prefix = f"({tag}"
    while True:
        pos = b_text.find(tag_prefix, idx)
        if pos == -1: break
        count, end = 0, pos
        while end < len(b_text):
            if b_text[end] == '(': count += 1
            elif b_text[end] == ')':
                count -= 1
                if count == 0: break
            end += 1
        blocks.append(b_text[pos:end+1])
        idx = end + 1
    return blocks

symbols = parse_blocks(sch, "symbol")
for s in symbols:
    m_ref = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', s)
    ref = m_ref.group(1) if m_ref else ""
    m_at = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', s)
    if m_at:
        x, y = float(m_at.group(1)), float(m_at.group(2))
        print(f"{ref:8} at ({x:6.2f}, {y:6.2f})")
