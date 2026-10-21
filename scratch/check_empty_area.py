import re
from pathlib import Path

sch = Path("pcbs/curcur40/right/curcur40-right.kicad_sch").read_text(encoding="utf-8")

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
found = []
for s in symbols:
    m_at = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', s)
    if m_at:
        x, y = float(m_at.group(1)), float(m_at.group(2))
        if x >= 250 and y >= 55:
            m_ref = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', s)
            ref = m_ref.group(1) if m_ref else ""
            found.append((ref, x, y))

print(f"Symbols in X >= 250, Y >= 55: {len(found)}")
for f in found[:20]:
    print(f)
