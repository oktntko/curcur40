import re

with open(r"pcbs/curcur40/right/curcur40-right.kicad_pcb", "r", encoding="utf-8") as f:
    text = f.read()

# KiCad 8/9/10 format: (property "Reference" "REF" (at X Y rot) ...)
# or (fp_text reference "REF" (at X Y rot) ...)
props = re.findall(r'\(property\s+"Reference"\s+"([^"]+)"[\s\S]*?\(at\s+([-\d.]+)\s+([-\d.]+)', text)
print(f"Properties found: {len(props)}")
for ref, x, y in props[:15]:
    print(f"Prop: {ref:<10} at ({x}, {y})")

# Also look for footprints directly
footprints = re.findall(r'\(footprint\s+"([^"]+)"[\s\S]*?\(at\s+([-\d.]+)\s+([-\d.]+)', text)
print(f"Footprints found: {len(footprints)}")
for fp, x, y in footprints[:15]:
    print(f"FP: {fp:<35} at ({x}, {y})")
