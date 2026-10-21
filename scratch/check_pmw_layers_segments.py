import re
from pathlib import Path

pcb = Path("scratch/pmw3360_pcb_b9043a22.kicad_pcb").read_text(encoding="utf-8")

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

segments = parse_blocks(pcb, "segment")
layers = {}
for s in segments:
    m = re.search(r'\(layer\s+"([^"]+)"\)', s)
    l = m.group(1) if m else "?"
    layers[l] = layers.get(l, 0) + 1

print("Segment layers in PMW PCB:")
for l, cnt in layers.items():
    print(f"  {l}: {cnt}")
