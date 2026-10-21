from pathlib import Path
import re

sch = Path("pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_sch").read_text(encoding="utf-8")

# Extract all symbol instances that are NOT J1, TP*, H*
# We want U1, U2, JP1, R1, R2, R3, R4, C1, C2, C3, C4, C5
s_idx = 0
symbols = []
while True:
    pos = sch.find("(symbol\n", s_idx)
    if pos == -1: break
    # check if this is inside lib_symbols
    if pos < sch.find(")\n\t(symbol\n") and pos < 2000: # inside lib_symbols
        pass
    count, end = 0, pos
    while end < len(sch):
        if sch[end] == '(': count += 1
        elif sch[end] == ')':
            count -= 1
            if count == 0: break
        end += 1
    blk = sch[pos:end+1]
    s_idx = end + 1

    m_ref = re.search(r'\(property\s+\"Reference\"\s+\"([^\"]+)\"', blk)
    ref = m_ref.group(1) if m_ref else ""
    m_val = re.search(r'\(property\s+\"Value\"\s+\"([^\"]+)\"', blk)
    val = m_val.group(1) if m_val else ""
    m_at = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)(?:\s+([\d\.\-]+))?\)', blk)
    at = (m_at.group(1), m_at.group(2)) if m_at else ("", "")
    
    if ref in ['U1', 'U2', 'JP1', 'R1', 'R2', 'R3', 'R4', 'C1', 'C2', 'C3', 'C4', 'C5']:
        symbols.append((ref, val, at, blk))

print(f"Extracted {len(symbols)} symbols:")
for ref, val, at, blk in symbols:
    print(f"  [{ref}] {val} at {at}")

# Also extract all wires and labels in curcur40-pmw3360.kicad_sch
wires = re.findall(r'\(wire\s+\(pts\s+\(xy\s+[\d\.\-]+\s+[\d\.\-]+\)\s+\(xy\s+[\d\.\-]+\s+[\d\.\-]+\)\)\s+\(stroke[^)]*\)\s+\(uuid\s+\"[^\"]+\"\)\)', sch)
labels = re.findall(r'\((?:global_label|hierarchical_label|label)\s+\"[^\"]+\"[^)]*\(at\s+[\d\.\-]+\s+[\d\.\-]+[^)]*\)[^)]*\)', sch)
print(f"Total wires: {len(wires)}, Total labels: {len(labels)}")
