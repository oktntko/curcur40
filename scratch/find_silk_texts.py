import re

with open('pcbs/curcur40/left/curcur40-left.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's find all (gr_text ...) on any layer
for m in re.finditer(r'\(gr_text\s+\"([^\"]+)\"\s*\(at\s+([-\d.]+)\s+([-\d.]+)[^)]*\)\s*\(layer\s+\"([^\"]+)\"\)', text):
    content, x, y, layer = m.group(1), float(m.group(2)), float(m.group(3)), m.group(4)
    print(f"gr_text '{content}' at ({x:.3f}, {y:.3f}) on {layer}")

print("\n--- Footprint silkscreen texts ---")
# Check all text items on F.SilkS and B.SilkS
for m in re.finditer(r'\((?:fp_text|property\s+\"Reference\"|property\s+\"Value\")\s+(?:\"([^\"]+)\"|(\w+))\s*\(at\s+([-\d.]+)\s+([-\d.]+)[^)]*\)\s*\(layer\s+\"([^\"]+)\"\)', text):
    t1, t2, x, y, layer = m.group(1), m.group(2), float(m.group(3)), float(m.group(4)), m.group(5)
    t = t1 if t1 else t2
    if 'Silk' in layer:
        # Check if in target area or near board edge
        if -105 <= x <= -85 and 30 <= y <= 45:
            print(f"Silk text '{t}' at ({x:.3f}, {y:.3f}) on {layer}")
