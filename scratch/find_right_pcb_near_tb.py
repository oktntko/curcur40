import re

with open(r"pcbs/curcur40/right/curcur40-right.kicad_pcb", "r", encoding="utf-8") as f:
    text = f.read()

fps = re.findall(r'\(fp_text\s+reference\s+"([^"]+)"[\s\S]*?\(at\s+([-\d.]+)\s+([-\d.]+)', text)
for ref, x, y in fps:
    fx, fy = float(x), float(y)
    d = ((fx - 7.525)**2 + (fy - 52.3875)**2)**0.5
    if d < 30.0:
        print(f"Near trackball: {ref:<10} at ({fx:.2f}, {fy:.2f}) dist={d:.2f}")
