import re
from pathlib import Path

pcb = Path("pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pcb").read_text(encoding="utf-8")

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
nets = {}
for s in segments:
    m = re.search(r'\(net\s+(?:\d+\s+)?"([^"]+)"\)', s)
    n = m.group(1) if m else "?"
    nets[n] = nets.get(n, 0) + 1

for n, count in sorted(nets.items()):
    print(f"{n}: {count}")
