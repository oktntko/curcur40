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
pwr_vals = set()
for s in symbols:
    m_ref = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', s)
    if m_ref and m_ref.group(1).startswith('#PWR'):
        m_val = re.search(r'\(property\s+"Value"\s+"([^"]+)"', s)
        m_lib = re.search(r'\(lib_id\s+"([^"]+)"', s)
        if m_val:
            pwr_vals.add((m_val.group(1), m_lib.group(1) if m_lib else ""))

for v in sorted(pwr_vals):
    print(v)
