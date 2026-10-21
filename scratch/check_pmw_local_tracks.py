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
for net in ["+1V8_PMW", "V_{IO}", "V_{IN}", "/RESET", "/MOTION", "/CS", "Net-(U1-LED_P)", "Net-(U2-NC)"]:
    segs = [s for s in segments if f'"{net}"' in s]
    print(f"Net {net}: {len(segs)} segments")
