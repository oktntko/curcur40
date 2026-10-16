import re

with open(r"pcbs/curcur40/right/curcur40-right.kicad_pcb", "r", encoding="utf-8") as f:
    text = f.read()

print("Footprints near trackball on right PCB:")
matches = re.finditer(r'\(footprint\s+"([^"]+)"[\s\S]*?\(fp_text\s+reference\s+"([^"]+)"[\s\S]*?\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\)', text)
for m in matches:
    name, ref, x, y, rot = m.groups()
    if any(k in ref.lower() for k in ["pmw", "tb", "sensor", "j3", "rj3"]) or any(k in name.lower() for k in ["pmw", "trackball"]):
        print(f"Ref: {ref:<10} Name: {name:<40} at ({x}, {y}) rot={rot}")

# Check circles or cuts near trackball (around X=148, Y=93 or similar)
print("\nEdge.Cuts on right PCB:")
cuts = re.findall(r'\((?:gr_line|gr_arc|gr_circle)[\s\S]*?\(layer\s+"Edge\.Cuts"\)[\s\S]*?\)', text)
for c in cuts:
    if "gr_circle" in c:
        print("Circle cut:", c.strip())
