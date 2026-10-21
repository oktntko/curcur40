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

wires = parse_blocks(body, "wire")
labels = parse_blocks(body, "label") + parse_blocks(body, "global_label")

print("PMW schematic labels (X < 215):")
for l in labels:
    m_at = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', l)
    m_txt = re.search(r'\((?:label|global_label)\s+"([^"]+)"', l)
    if m_at and float(m_at.group(1)) < 215:
        print(f"  {m_txt.group(1) if m_txt else '?'} at ({m_at.group(1)}, {m_at.group(2)})")

print("\nPMW schematic wires (X < 215):")
for w in wires:
    pts = re.findall(r'\(xy\s+([\d\.\-]+)\s+([\d\.\-]+)\)', w)
    if pts:
        x1, y1 = float(pts[0][0]), float(pts[0][1])
        x2, y2 = float(pts[1][0]), float(pts[1][1])
        if x1 < 215 and x2 < 215:
            print(f"  ({x1:6.2f}, {y1:6.2f}) -> ({x2:6.2f}, {y2:6.2f})")
