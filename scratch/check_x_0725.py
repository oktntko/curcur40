from pathlib import Path
import re

pcb = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")

# Let's find what is at (-0.72, 46.05), (-0.72, 51.13), (-0.72, 48.59), (-0.72, 53.67), (-0.72, 43.51), (-0.72, 65.50)
print("=== Segments ending at X = -0.72 ===")
for m in re.finditer(r'\(segment\s+\(start\s+([\d\.\-]+)\s+([\d\.\-]+)\)\s+\(end\s+([\d\.\-]+)\s+([\d\.\-]+)\)\s+\(width[^)]*\)\s+\(layer\s+\"([^\"]+)\"\)\s+\(net\s+\"([^\"]+)\"\)', pcb):
    sx, sy, ex, ey, layer, net = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), m.group(5), m.group(6)
    if abs(sx - -0.725) < 0.1 or abs(ex - -0.725) < 0.1:
        print(f"  {layer:5}: ({sx:7.3f}, {sy:7.3f}) -> ({ex:7.3f}, {ey:7.3f}) | {net}")

# Also check vias at X = -0.725 or pads near there
print("\n=== Vias near X = -0.725 ===")
for m in re.finditer(r'\(via\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)\)[^)]*\(net\s+\"([^\"]+)\"\)', pcb):
    vx, vy, net = float(m.group(1)), float(m.group(2)), m.group(3)
    if abs(vx - -0.725) < 0.5:
        print(f"  via at ({vx:7.3f}, {vy:7.3f}) | {net}")
