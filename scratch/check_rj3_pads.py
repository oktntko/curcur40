import re

with open(r"pcbs/curcur40/right/curcur40-right.kicad_pcb", "r", encoding="utf-8") as f:
    text = f.read()

# find footprint blocks
fps = re.findall(r'(\(footprint\s+"[^"]+"[\s\S]*?\n  \))', text)
print(f"Total footprints: {len(fps)}")

for fp in fps:
    m_ref = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', fp)
    if m_ref:
        ref = m_ref.group(1)
        if ref in ["rJ3", "rJ2", "rJ1"] or "PJ-398" in fp or "PinHeader" in fp:
            m_at = re.search(r'\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\)', fp)
            at = m_at.groups() if m_at else ()
            print(f"Ref: {ref:<10} at {at}")
            # print pads
            pads = re.findall(r'\(pad\s+"([^"]+)"\s+(\w+)\s+\w+\s+\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\)', fp)
            print(f"  Pads ({len(pads)}):")
            for p in pads[:8]:
                print(f"    pad {p[0]} at ({p[2]}, {p[3]})")
