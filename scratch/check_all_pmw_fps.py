from pathlib import Path
import re

text = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")

# find all footprints: (footprint "name" ... (property "Reference" "REF" ...) ...)
idx = 0
fps = []
while True:
    pos = text.find("(footprint ", idx)
    if pos == -1: break
    count, end = 0, pos
    while end < len(text):
        if text[end] == '(': count += 1
        elif text[end] == ')':
            count -= 1
            if count == 0: break
        end += 1
    blk = text[pos:end+1]
    idx = end + 1

    m_ref = re.search(r'\(property\s+\"Reference\"\s+\"([^\"]+)\"', blk)
    m_val = re.search(r'\(property\s+\"Value\"\s+\"([^\"]+)\"', blk)
    m_fp = re.match(r'\(footprint\s+\"([^\"]+)\"', blk)
    m_sheet = re.search(r'\(sheetfile\s+\"([^\"]+)\"\)', blk)
    m_path = re.search(r'\(path\s+\"([^\"]+)\"\)', blk)
    ref = m_ref.group(1) if m_ref else ""
    val = m_val.group(1) if m_val else ""
    fp = m_fp.group(1) if m_fp else ""
    sheet = m_sheet.group(1) if m_sheet else ""
    path_s = m_path.group(1) if m_path else ""

    fps.append((ref, val, fp, sheet, path_s))

print(f"Total footprints in right PCB: {len(fps)}")
print("\nFootprints with sheet curcur40-pmw3360.kicad_sch or without 'r' prefix:")
for ref, val, fp, sheet, path_s in fps:
    if "pmw" in sheet or not ref.startswith("r"):
        print(f"  [{ref:6}] {val:20} | fp: {fp:40} | sheet: {sheet:25} | path: {path_s}")
