from pathlib import Path
import re

text = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")

# Parse all segments
idx = 0
segments = []
while True:
    pos = text.find("(segment", idx)
    if pos == -1: break
    count, end = 0, pos
    while end < len(text):
        if text[end] == '(': count += 1
        elif text[end] == ')':
            count -= 1
            if count == 0: break
        end += 1
    blk = text[pos:end+1]
    idx = end + 1

    m_start = re.search(r'\(start\s+([\d\.\-]+)\s+([\d\.\-]+)\)', blk)
    m_end = re.search(r'\(end\s+([\d\.\-]+)\s+([\d\.\-]+)\)', blk)
    m_layer = re.search(r'\(layer\s+\"([^\"]+)\"\)', blk)
    m_net = re.search(r'\(net\s+\"([^\"]+)\"\)', blk)
    if m_start and m_end and m_layer and m_net:
        sx, sy = float(m_start.group(1)), float(m_start.group(2))
        ex, ey = float(m_end.group(1)), float(m_end.group(2))
        layer = m_layer.group(1)
        net = m_net.group(1)
        if -5 <= sx <= 25 and 40 <= sy <= 68:
            segments.append((sx, sy, ex, ey, layer, net))

print(f"Total PMW area segments: {len(segments)}")
for s in segments:
    print(f"  {s[4]:6}: ({s[0]:7.2f}, {s[1]:7.2f}) -> ({s[2]:7.2f}, {s[3]:7.2f}) | {s[5]}")

# Also check pads of U1
print("\n=== U1 pad details ===")
pos = text.find('(property "Reference" "U1"')
start = text.rfind('(footprint', 0, pos)
count, end = 0, start
while end < len(text):
    if text[end] == '(': count += 1
    elif text[end] == ')':
        count -= 1
        if count == 0: break
    end += 1
blk = text[start:end+1]
# find pads
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
