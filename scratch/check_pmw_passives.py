from pathlib import Path
import re

text = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")

for ref in ['R1', 'R2', 'R3', 'R4', 'C1', 'C2', 'C3', 'C4', 'C5']:
    pos = text.find(f'(property "Reference" "{ref}"')
    if pos == -1: continue
    start = text.rfind('(footprint', 0, pos)
    count, end = 0, start
    while end < len(text):
        if text[end] == '(': count += 1
        elif text[end] == ')':
            count -= 1
            if count == 0: break
        end += 1
    blk = text[start:end+1]
    val_m = re.search(r'\(property "Value" "([^"]+)"', blk)
    val = val_m.group(1) if val_m else ""
    print(f"\n=== [{ref}] {val} ===")
    p_idx = 0
    while True:
        pos_p = blk.find("(pad ", p_idx)
        if pos_p == -1: break
        c, end_p = 0, pos_p
        while end_p < len(blk):
            if blk[end_p] == '(': c += 1
            elif blk[end_p] == ')':
                c -= 1
                if c == 0: break
            end_p += 1
        pad_blk = blk[pos_p:end_p+1]
        p_idx = end_p + 1
        m_p = re.match(r'\(pad\s+\"([^\"]+)\"', pad_blk)
        m_net = re.search(r'\(net\s+\"([^\"]+)\"\)', pad_blk)
        p_num = m_p.group(1) if m_p else "?"
        net_str = m_net.group(1) if m_net else "(NO NET)"
        print(f"  Pad {p_num:4} -> {net_str}")
