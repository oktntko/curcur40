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
for s in segments:
    if '"+3V3R"' in s:
        m_start = re.search(r'\(start\s+([\d\.\-]+)\s+([\d\.\-]+)\)', s)
        m_end = re.search(r'\(end\s+([\d\.\-]+)\s+([\d\.\-]+)\)', s)
        if m_start and m_end:
            x1, y1 = float(m_start.group(1)), float(m_start.group(2))
            x2, y2 = float(m_end.group(1)), float(m_end.group(2))
            if (x1 < 25 and 35 < y1 < 70) or (x2 < 25 and 35 < y2 < 70):
                print(f"+3V3R segment: ({x1}, {y1}) -> ({x2}, {y2})")
