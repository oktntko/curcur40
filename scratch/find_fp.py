with open("pcbs/curcur40/right/curcur40-right.kicad_pcb", encoding="utf-8") as f:
    txt = f.read()

import re

for ref in ["rU1", "U2", "JP1"]:
    m = re.search(r'\(footprint [^\n]+\n[^\)]+\(property "Reference" "' + ref + r'"[^\)]+\)', txt)
    if not m:
        # KiCad 8/9/10 property syntax:
        m = re.search(r'\(property "Reference" "' + ref + r'"[^\n]+\n', txt)
        if m:
            start = txt.rfind('(footprint', 0, m.start())
            end = txt.find('(pad "1"', start)
            p1_end = txt.find(')', end)
            print(f"=== {ref} ===")
            print(txt[start:p1_end+1])
    else:
        print(f"=== {ref} ===")
        print(m.group(0))
