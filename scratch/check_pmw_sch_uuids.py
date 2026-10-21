from pathlib import Path
import re

sch_text = Path("pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_sch").read_text(encoding="utf-8")

# find symbols and their uuids and references
for m in re.finditer(r'\(symbol\s+[^)]*\(uuid\s+\"([^\"]+)\"\)[^)]*\(property\s+\"Reference\"\s+\"([^\"]+)\"', sch_text):
    print(m.group(2), m.group(1))

# Also search directly
for ref in ['U1', 'U2', 'R1', 'R2', 'R3', 'R4', 'C1', 'C2', 'C3', 'C4', 'C5', 'JP1', 'J1', 'H1']:
    pos = sch_text.find(f'"{ref}"')
    if pos != -1:
        s_start = sch_text.rfind('(symbol', 0, pos)
        count, s_end = 0, s_start
        while s_end < len(sch_text):
            if sch_text[s_end] == '(': count += 1
            elif sch_text[s_end] == ')':
                count -= 1
                if count == 0: break
            s_end += 1
        blk = sch_text[s_start:s_end+1]
        uuid_m = re.search(r'\(uuid\s+\"([^\"]+)\"\)', blk)
        u = uuid_m.group(1) if uuid_m else ""
        print(f"SCH [{ref}] uuid: {u}")
