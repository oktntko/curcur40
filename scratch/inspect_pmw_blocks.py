from pathlib import Path
import re

text = Path("pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_sch").read_text(encoding="utf-8")

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

pos_lib = text.find("(lib_symbols")
count, end_lib = 0, pos_lib
while end_lib < len(text):
    if text[end_lib] == '(': count += 1
    elif text[end_lib] == ')':
        count -= 1
        if count == 0: break
    end_lib += 1

body = text[end_lib+1:]

symbols = parse_blocks(body, "symbol")
wires = parse_blocks(body, "wire")
junctions = parse_blocks(body, "junction")
labels = parse_blocks(body, "label")

# Sub-block 1: LDO & Power (U2, C3, C4, C5, R4, and JP1)
# Sub-block 2: Sensor & Passives (U1, R1, R2, R3, C1, C2)
print("=== SYMBOLS ===")
for s in symbols:
    m_ref = re.search(r'\(property\s+\"Reference\"\s+\"([^\"]+)\"', s)
    m_val = re.search(r'\(property\s+\"Value\"\s+\"([^\"]+)\"', s)
    m_at = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', s)
    if m_ref and m_at:
        x, y = float(m_at.group(1)), float(m_at.group(2))
        ref = m_ref.group(1)
        val = m_val.group(1) if m_val else ""
        if ref in ['U1', 'U2', 'JP1', 'R1', 'R2', 'R3', 'R4', 'C1', 'C2', 'C3', 'C4', 'C5'] or ref.startswith('#PWR'):
            if x < 210:
                print(f"  {ref:10} {val:15} at ({x:6.2f}, {y:6.2f})")
