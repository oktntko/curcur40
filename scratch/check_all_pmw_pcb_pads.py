import re
from pathlib import Path

pcb = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")
fps = ["U1", "U2", "JP1", "R1", "R2", "R3", "R4", "C1", "C2", "C3", "C4", "C5"]

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

for ref in fps:
    pattern = rf'\(property\s+"Reference"\s+"{ref}"\s+'
    m = re.search(pattern, pcb)
    if not m:
        print(f"{ref}: NOT FOUND")
        continue
    pos = m.start()
    f_start = pcb.rfind("(footprint", 0, pos)
    c, f_end = 0, f_start
    while f_end < len(pcb):
        if pcb[f_end] == '(': c += 1
        elif pcb[f_end] == ')':
            c -= 1
            if c == 0: break
        f_end += 1
    fp_text = pcb[f_start:f_end+1]
    pads = parse_blocks(fp_text, "pad")
    print(f"=== {ref} ===")
    for p in pads:
        m_num = re.search(r'\(pad\s+"?([^"\s]+)"?', p)
        num = m_num.group(1) if m_num else "?"
        m_net = re.search(r'\(net\s+(?:\d+\s+)?"([^"]+)"\)', p)
        net_name = m_net.group(1) if m_net else "-"
        print(f"  pad {num:>2}: {net_name}")
