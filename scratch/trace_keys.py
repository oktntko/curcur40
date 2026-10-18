import re

with open('scratch/test_left_orig.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

for net in ["/KEY16", "/KEY17", "/KEY18"]:
    print(f"=== Segments for {net} ===")
    pattern = r'\(segment\s*\(start\s+([-\d.]+)\s+([-\d.]+)\)\s*\(end\s+([-\d.]+)\s+([-\d.]+)\)[^\)]*\(net\s+\"' + re.escape(net) + r'\"'
    for m in re.finditer(pattern, text):
        sx, sy, ex, ey = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
        print(f"  ({sx:8.3f}, {sy:8.3f}) -> ({ex:8.3f}, {ey:8.3f})")
