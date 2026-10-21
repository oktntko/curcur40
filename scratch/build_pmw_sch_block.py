import re
from pathlib import Path

WORKSPACE = Path(r"c:\Users\oktnt\workspace\curcur40")
SCH_PMW_PATH = WORKSPACE / "pcbs" / "curcur40" / "pmw3360" / "curcur40-pmw3360.kicad_sch"
text = SCH_PMW_PATH.read_text(encoding="utf-8")

def parse_blocks(b_text, tag):
    blocks = []
    idx = 0
    tag_prefix = f"({tag}"
    while True:
        pos = b_text.find(tag_prefix, idx)
        if pos == -1: break
        count, end = 0, pos
        while end < len(b_text):
            if b_text[end] == '(': count += 1
            elif b_text[end] == ')':
                count -= 1
                if count == 0: break
            end += 1
        blocks.append(b_text[pos:end+1])
        idx = end + 1
    return blocks

# Extract lib_symbols end
pos_lib = text.find("(lib_symbols")
count, end_lib = 0, pos_lib
while end_lib < len(text):
    if text[end_lib] == '(': count += 1
    elif text[end_lib] == ')':
        count -= 1
        if count == 0: break
    end_lib += 1

body = text[end_lib+1:]

# Parse all symbols in body
symbols = parse_blocks(body, "symbol")
wires = parse_blocks(body, "wire")
junctions = parse_blocks(body, "junction")
labels = parse_blocks(body, "label")
glabels = parse_blocks(body, "global_label")

print(f"Extracted: symbols={len(symbols)}, wires={len(wires)}, junctions={len(junctions)}, labels={len(labels)}, glabels={len(glabels)}")

# Filter symbols to keep:
# U1, U2, JP1, R1, R2, R3, R4, C1, C2, C3, C4, C5
# And power symbols (#PWR*) that are not on J1
pmw_syms_to_keep = []
for s in symbols:
    m_ref = re.search(r'\(property\s+\"Reference\"\s+\"([^\"]+)\"', s)
    ref = m_ref.group(1) if m_ref else ""
    if ref in ['U1', 'U2', 'JP1', 'R1', 'R2', 'R3', 'R4', 'C1', 'C2', 'C3', 'C4', 'C5']:
        pmw_syms_to_keep.append(s)
    elif ref.startswith('#PWR'):
        # check location
        m_at = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', s)
        if m_at:
            x, y = float(m_at.group(1)), float(m_at.group(2))
            if x < 210: # not on J1
                pmw_syms_to_keep.append(s)

print(f"Filtered symbols to keep: {len(pmw_syms_to_keep)}")

# Filter wires: keep wires with coordinates x < 210
pmw_wires_to_keep = []
for w in wires:
    pts = re.findall(r'\(xy\s+([\d\.\-]+)\s+([\d\.\-]+)\)', w)
    if pts:
        (x1, y1), (x2, y2) = (float(pts[0][0]), float(pts[0][1])), (float(pts[1][0]), float(pts[1][1]))
        if x1 < 215 and x2 < 215:
            pmw_wires_to_keep.append(w)

print(f"Filtered wires to keep: {len(pmw_wires_to_keep)}")

# Filter junctions: keep junctions with x < 210
pmw_juncs_to_keep = []
for j in junctions:
    m_at = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', j)
    if m_at and float(m_at.group(1)) < 215:
        pmw_juncs_to_keep.append(j)

print(f"Filtered junctions to keep: {len(pmw_juncs_to_keep)}")

# Filter labels: keep labels with x < 215
pmw_labels_to_keep = []
for l in labels + glabels:
    m_at = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', l)
    if m_at and float(m_at.group(1)) < 215:
        pmw_labels_to_keep.append(l)

print(f"Filtered labels to keep: {len(pmw_labels_to_keep)}")
for l in pmw_labels_to_keep:
    m_name = re.search(r'\((?:label|global_label)\s+\"([^\"]+)\"', l)
    m_at = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', l)
    print(f"  {m_name.group(1) if m_name else '?'} at {m_at.group(1) if m_at else '?'}, {m_at.group(2) if m_at else '?'}")
