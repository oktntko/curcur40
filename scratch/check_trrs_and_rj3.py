import re

with open(r"pcbs/curcur40/right/curcur40-right.kicad_pcb", "r", encoding="utf-8") as f:
    text = f.read()

# find rJ3
m = re.search(r'\(footprint\s+"([^"]+)"[\s\S]*?\(fp_text\s+reference\s+"rJ3"[\s\S]*?\n\s*\)', text)
if m:
    print("rJ3 in right PCB:")
    print(m.group(0)[:500])

# check TRRS jack
m_trrs = re.search(r'\(footprint\s+"([^"]+)"[\s\S]*?\(fp_text\s+reference\s+"rJ2"[\s\S]*?\n\s*\)', text)
if m_trrs:
    print("rJ2 (TRRS) in right PCB:")
    print(m_trrs.group(0)[:500])

# check TRRS other refs
for m in re.finditer(r'\(footprint\s+"([^"]+)"[\s\S]*?\(fp_text\s+reference\s+"([^"]+)"', text):
    fp, ref = m.groups()
    if any(k in ref.lower() for k in ["trrs", "pj", "jack", "j2"]):
        print(f"TRRS candidate: Ref={ref} FP={fp}")
