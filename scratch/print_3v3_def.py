import re
from pathlib import Path

sch = Path("pcbs/curcur40/right/curcur40-right.kicad_sch").read_text(encoding="utf-8")
pos = sch.find('(symbol "kbd:+3V3R"')
if pos != -1:
    c, end = 0, pos
    while end < len(sch):
        if sch[end] == '(': c += 1
        elif sch[end] == ')':
            count = c - 1
            c = count
            if c == 0: break
        end += 1
    print(sch[pos:end+1])
