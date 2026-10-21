import re
from pathlib import Path

sch = Path("pcbs/curcur40/right/curcur40-right.kicad_sch").read_text(encoding="utf-8")

# find rJ3
pos = sch.find('"rJ3"')
start = sch.rfind('(symbol', 0, pos)
count, end = 0, start
while end < len(sch):
    if sch[end] == '(': count += 1
    elif sch[end] == ')':
        count -= 1
        if count == 0: break
    end += 1

print(sch[start:end+1])
