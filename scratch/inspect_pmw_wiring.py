from pathlib import Path
import re

pmw_sch_path = Path("pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_sch")
text = pmw_sch_path.read_text(encoding="utf-8")

def parse_blocks(text, tag):
    blocks = []
    idx = 0
    tag_prefix = f"({tag}"
    while True:
        pos = text.find(tag_prefix, idx)
        if pos == -1: break
        count, end = 0, pos
        while end < len(text):
            if text[end] == '(': count += 1
            elif text[end] == ')':
                count -= 1
                if count == 0: break
            end += 1
        blocks.append(text[pos:end+1])
        idx = end + 1
    return blocks

wires = parse_blocks(text, "wire")
junctions = parse_blocks(text, "junction")
no_connects = parse_blocks(text, "no_connect")
labels = parse_blocks(text, "label")

print(f"Wires: {len(wires)}")
print(f"Junctions: {len(junctions)}")
print(f"No_connects: {len(no_connects)}")
print(f"Labels: {len(labels)}")

for l in labels:
    m = re.search(r'\(label\s+\"([^\"]+)\"\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', l)
    if m:
        print(f"  Label '{m.group(1)}' at ({m.group(2)}, {m.group(3)})")
