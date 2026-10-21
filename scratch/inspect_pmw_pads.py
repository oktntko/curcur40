from pathlib import Path
import re

text = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")
for ref in ['U1', 'R1', 'R2', 'R3', 'R4', 'C1', 'C2', 'C3', 'C4', 'C5']:
    pos = text.find(f'(property "Reference" "{ref}"')
    if pos == -1:
        print(f"[{ref}] NOT FOUND")
        continue
    start = text.rfind('(footprint', 0, pos)
    count, end = 0, start
    while end < len(text):
        if text[end] == '(': count += 1
        elif text[end] == ')':
            count -= 1
            if count == 0: break
        end += 1
    blk = text[start:end+1]
    
    val_m = re.search(r'\(property "Value" "([^"]+)"', blk)
    val = val_m.group(1) if val_m else ""
    lcsc_m = re.search(r'\(property "LCSC" "([^"]+)"', blk)
    lcsc = lcsc_m.group(1) if lcsc_m else ""
    path_m = re.search(r'\(path\s+"([^"]+)"\)', blk)
    path_s = path_m.group(1) if path_m else ""
    sheet_m = re.search(r'\(sheetfile\s+"([^"]+)"\)', blk)
    sheet = sheet_m.group(1) if sheet_m else ""

    print(f"\n=================== [{ref}] {val} (LCSC: {lcsc}) ===================")
    print(f"  path: {path_s}, sheet: {sheet}")
    # find pads: in KiCad, (pad "1" smd roundrect ... (net 14 "/SCLK") ...)
    # pad regex across multiple lines
    for p_m in re.finditer(r'\(pad\s+"([^"]+)"\s+([^\s\)]+)\s+([^\s\)]+)', blk):
        p_num = p_m.group(1)
        # find matching paren for this pad
        p_start = p_m.start()
        p_count, p_end = 0, p_start
        while p_end < len(blk):
            if blk[p_end] == '(': p_count += 1
            elif blk[p_end] == ')':
                p_count -= 1
                if p_count == 0: break
            p_end += 1
        pad_str = blk[p_start:p_end+1]
        net_m = re.search(r'\(net\s+\d+\s+"([^"]+)"\)', pad_str)
        net_name = net_m.group(1) if net_m else "(no net)"
        print(f"  Pad {p_num:4} -> {net_name}")
