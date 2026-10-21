from pathlib import Path
import re

pcb = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")

# Let's find all tracks connecting to the PMW components!
pmw_nets = ['+1V8_PMW', '/CS', '/MISO', '/MOSI', '/MOTION', '/RESET', '/SCLK', 'Net-(U1-LED_P)', 'Net-(U2-NC)', 'V_{IN}', 'V_{IO}', '/NCS', '+3V3R']

print("=== ALL SEGMENTS WITH PMW NETS ===")
for m in re.finditer(r'\(segment\s+\(start\s+([\d\.\-]+)\s+([\d\.\-]+)\)\s+\(end\s+([\d\.\-]+)\s+([\d\.\-]+)\)\s+\(width[^)]*\)\s+\(layer\s+\"([^\"]+)\"\)\s+\(net\s+\"([^\"]+)\"\)', pcb):
    sx, sy, ex, ey, layer, net = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), m.group(5), m.group(6)
    if net in pmw_nets:
        print(f"  {net:16} | {layer:5}: ({sx:7.3f}, {sy:7.3f}) -> ({ex:7.3f}, {ey:7.3f})")

# Also check vias with pmw_nets
print("\n=== ALL VIAS WITH PMW NETS ===")
for m in re.finditer(r'\(via\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)\)[^)]*\(net\s+\"([^\"]+)\"\)', pcb):
    vx, vy, net = float(m.group(1)), float(m.group(2)), m.group(3)
    if net in pmw_nets:
        print(f"  via {net:16} at ({vx:7.3f}, {vy:7.3f})")
