import re

with open('scratch/test_left_orig.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

for m in re.finditer(r'\(via\s*\(at\s+([-\d.]+)\s+([-\d.]+)\)[^\)]*\(net\s+\"([^\"]+)\"\)', text):
    x, y, net = float(m.group(1)), float(m.group(2)), m.group(3)
    if -105 <= x <= -85 and 33 <= y <= 43:
        print(f"Via {net} at ({x:.3f}, {y:.3f})")

print("\n--- Footprints in area ---")
for m in re.finditer(r'\(footprint\s+\"([^\"]+)\"[^)]*\(at\s+([-\d.]+)\s+([-\d.]+)[^)]*\)[^)]*\(property\s+\"Reference\"\s+\"([^\"]+)\"', text):
    fp_name, x, y, ref = m.group(1), float(m.group(2)), float(m.group(3)), m.group(4)
    if -105 <= x <= -85 and 33 <= y <= 43:
        print(f"FP {ref} ({fp_name}) at ({x:.3f}, {y:.3f})")
