import re

with open('scratch/test_left_orig.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

blocks = text.split('(footprint')
for b in blocks[1:]:
    header = b[:400]
    m_ref = re.search(r'\(property\s+\"Reference\"\s+\"([^\"]+)\"', header)
    m_at = re.search(r'\(at\s+([-\d.]+)\s+([-\d.]+)', header)
    if m_ref and m_at:
        x, y = float(m_at.group(1)), float(m_at.group(2))
        if -119 <= x <= -85 and 25 <= y <= 66:
            print(f"FP {m_ref.group(1):10s} at ({x:8.3f}, {y:8.3f})")
