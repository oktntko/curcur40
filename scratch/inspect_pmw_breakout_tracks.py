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
vias = parse_blocks(pcb, "via")

print(f"PMW PCB has {len(segments)} segments and {len(vias)} vias.")

# Check net names
nets = set()
for s in segments + vias:
    m = re.search(r'\(net\s+(?:\d+\s+)?"([^"]+)"\)', s)
    if m: nets.add(m.group(1))

print("Nets on tracks/vias in PMW PCB:")
for n in sorted(nets):
    cnt = sum(1 for x in segments + vias if f'"{n}"' in x)
    print(f"  {n:15}: {cnt}")
