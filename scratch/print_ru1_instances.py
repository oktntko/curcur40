import re
from pathlib import Path

sch = Path("pcbs/curcur40/right/curcur40-right.kicad_sch").read_text(encoding="utf-8")
pos = sch.find('"rU1"')
s_start = sch.rfind('(symbol', 0, pos)
count, s_end = 0, s_start
while s_end < len(sch):
    if sch[s_end] == '(': count += 1
    elif sch[s_end] == ')':
        count -= 1
        if count == 0: break
    s_end += 1

print(sch[s_start:s_end+1][-500:])
