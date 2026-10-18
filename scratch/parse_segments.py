with open('scratch/test_left_orig.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# split by '(segment'
blocks = text.split('(segment')
print(f"Total segment blocks: {len(blocks)-1}")

for b in blocks[1:]:
    # get text up to matching closing parens
    header = b[:200]
    m_start = re.search(r'\(start\s+([-\d.]+)\s+([-\d.]+)\)', header)
    m_end = re.search(r'\(end\s+([-\d.]+)\s+([-\d.]+)\)', header)
    m_layer = re.search(r'\(layer\s+\"([^\"]+)\"\)', header)
    m_net = re.search(r'\(net\s+(\d+)\)', header)
    if m_start and m_end:
        sx, sy = float(m_start.group(1)), float(m_start.group(2))
        ex, ey = float(m_end.group(1)), float(m_end.group(2))
        if -105 <= min(sx, ex) and max(sx, ex) <= -90 and 34 <= min(sy, ey) and max(sy, ey) <= 42:
            layer = m_layer.group(1) if m_layer else "?"
            net = m_net.group(1) if m_net else "?"
            print(f"Orig: ({sx:.3f}, {sy:.3f}) -> ({ex:.3f}, {ey:.3f}) on {layer} net={net}")
