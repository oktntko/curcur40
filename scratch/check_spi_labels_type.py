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

labels = parse_blocks(sch, "label")
glabels = parse_blocks(sch, "global_label")

for name in ["SCLK", "MOSI", "MISO", "NCS", "CS"]:
    for l in labels:
        if f'"{name}"' in l:
            print(f"Local label {name}: {l.strip().replace(chr(10), ' ')}")
    for g in glabels:
        if f'"{name}"' in g:
            print(f"Global label {name}: {g.strip().replace(chr(10), ' ')}")
