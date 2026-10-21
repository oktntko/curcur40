from pathlib import Path
import re

sch = Path("pcbs/curcur40/right/curcur40-right.kicad_sch").read_text(encoding="utf-8")

s_idx = 0
found = {}
while True:
    pos = sch.find("(symbol\n", s_idx)
    if pos == -1: break
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
    m_val = re.search(r'\(property\s+\"Value\"\s+\"([^\"]+)\"', blk)
    m_lib = re.search(r'\(lib_id\s+\"([^\"]+)\"\)', blk)
    if m_ref and m_ref.group(1).startswith('#PWR'):
        val = m_val.group(1) if m_val else ""
        lib = m_lib.group(1) if m_lib else ""
        found[val] = lib

print("Power symbols in right sch:")
for v, l in found.items():
    print(f"  {v:15}: {l}")
