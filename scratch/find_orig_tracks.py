with open('scratch/test_left_orig.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# find all segments
pattern = r'\(segment\s*\(start\s+([-\d.]+)\s+([-\d.]+)\)\s*\(end\s+([-\d.]+)\s+([-\d.]+)\)\s*\(width\s+([-\d.]+)\)\s*\(layer\s+\"([^\"]+)\"\)\s*\(net\s+(\d+)\)\s*(?:\(tstamp\s+([^\)]+)\)\s*)?\)'

for m in re.finditer(pattern, text):
    sx, sy, ex, ey, w, layer, net = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), float(m.group(5)), m.group(6), m.group(7)
    if -104 <= min(sx, ex) and max(sx, ex) <= -92 and 34 <= min(sy, ey) and max(sy, ey) <= 42:
        print(f"Segment: ({sx:.3f}, {sy:.3f}) -> ({ex:.3f}, {ey:.3f}) w={w} layer={layer} net={net}")
