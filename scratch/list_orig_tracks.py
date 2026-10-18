import re

with open('scratch/test_left_orig.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

pattern = r'\(segment\s*\(start\s+([-\d.]+)\s+([-\d.]+)\)\s*\(end\s+([-\d.]+)\s+([-\d.]+)\)\s*\(width\s+([-\d.]+)\)\s*\(layer\s+\"([^\"]+)\"\)\s*\(net\s+\"([^\"]+)\"\)'

for m in re.finditer(pattern, text):
    sx, sy, ex, ey = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
    layer = m.group(6)
    net = m.group(7)
    if -105 <= min(sx, ex) and max(sx, ex) <= -85 and 33 <= min(sy, ey) and max(sy, ey) <= 43:
        print(f"{net:20s} on {layer:6s}: ({sx:8.3f}, {sy:8.3f}) -> ({ex:8.3f}, {ey:8.3f})")
