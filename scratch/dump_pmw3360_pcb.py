import re

with open(r"pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pcb", "r", encoding="utf-8") as f:
    text = f.read()

# Footprints
print("=== FOOTPRINTS ===")
matches = re.finditer(r'\(footprint\s+"([^"]+)"[\s\S]*?\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\)[\s\S]*?\(fp_text\s+reference\s+"([^"]+)"', text)
for m in matches:
    name, x, y, rot, ref = m.groups()
    print(f"Ref: {ref:<10} Name: {name:<40} at ({x}, {y}) rot={rot}")

# Edge cuts lines
print("\n=== EDGE CUTS ===")
edge_lines = re.findall(r'\(gr_line\s+\(start\s+([-\d.]+)\s+([-\d.]+)\)\s+\(end\s+([-\d.]+)\s+([-\d.]+)\)[\s\S]*?\(layer\s+"Edge\.Cuts"\)', text)
for l in edge_lines:
    print(f"Line: ({float(l[0]):.2f}, {float(l[1]):.2f}) -> ({float(l[2]):.2f}, {float(l[3]):.2f})")

edge_arcs = re.findall(r'\(gr_arc\s+\(start\s+([-\d.]+)\s+([-\d.]+)\)\s+\(mid\s+([-\d.]+)\s+([-\d.]+)\)\s+\(end\s+([-\d.]+)\s+([-\d.]+)\)[\s\S]*?\(layer\s+"Edge\.Cuts"\)', text)
for a in edge_arcs:
    print(f"Arc: ({float(a[0]):.2f}, {float(a[1]):.2f}) -> ({float(a[4]):.2f}, {float(a[5]):.2f})")
