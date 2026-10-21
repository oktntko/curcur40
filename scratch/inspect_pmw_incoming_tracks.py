import re
from pathlib import Path

pcb = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")

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

print(f"Total segments: {len(segments)}, vias: {len(vias)}")

# Find track endpoints near X in [-5, 5], Y in [40, 65]
dangling_ends = []
for s in segments:
    m_start = re.search(r'\(start\s+([\d\.\-]+)\s+([\d\.\-]+)\)', s)
    m_end = re.search(r'\(end\s+([\d\.\-]+)\s+([\d\.\-]+)\)', s)
    m_net = re.search(r'\(net\s+(?:\d+\s+)?"([^"]+)"\)', s)
    m_layer = re.search(r'\(layer\s+"([^"]+)"\)', s)
    if m_start and m_end:
        x1, y1 = float(m_start.group(1)), float(m_start.group(2))
        x2, y2 = float(m_end.group(1)), float(m_end.group(2))
        net = m_net.group(1) if m_net else "?"
        layer = m_layer.group(1) if m_layer else "?"
        if (-5 <= x1 <= 5 and 40 <= y1 <= 65) or (-5 <= x2 <= 5 and 40 <= y2 <= 65):
            print(f"Track: ({x1}, {y1}) -> ({x2}, {y2}) | net={net} | layer={layer}")
