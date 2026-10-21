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

pos_lib = sch.find("(lib_symbols")
count, end_lib = 0, pos_lib
while end_lib < len(sch):
    if sch[end_lib] == '(': count += 1
    elif sch[end_lib] == ')':
        count -= 1
        if count == 0: break
    end_lib += 1
body = sch[end_lib+1:]

symbols = parse_blocks(body, "symbol")
wires = parse_blocks(body, "wire")

all_x, all_y = [], []
for s in symbols:
    m_ref = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', s)
    ref = m_ref.group(1) if m_ref else ""
    if ref in ['U1', 'U2', 'JP1', 'R1', 'R2', 'R3', 'R4', 'C1', 'C2', 'C3', 'C4', 'C5'] or (ref.startswith('#PWR') and 'Conn' not in s):
        m_at = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', s)
        if m_at:
            x, y = float(m_at.group(1)), float(m_at.group(2))
            if x < 210:
                all_x.append(x)
                all_y.append(y)

print(f"X range: {min(all_x)} to {max(all_x)} (span = {max(all_x) - min(all_x)})")
print(f"Y range: {min(all_y)} to {max(all_y)} (span = {max(all_y) - min(all_y)})")
