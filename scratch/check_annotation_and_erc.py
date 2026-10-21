import re
from pathlib import Path

sch = Path("pcbs/curcur40/right/curcur40-right.kicad_sch").read_text(encoding="utf-8")

# Let's check references
# Note: exclude (lib_symbols ...)
pos_lib = sch.find("(lib_symbols")
c, end_lib = 0, pos_lib
while end_lib < len(sch):
    if sch[end_lib] == '(': c += 1
    elif sch[end_lib] == ')':
        c -= 1
        if c == 0: break
    end_lib += 1

body = sch[end_lib+1:]
all_refs = re.findall(r'\(property\s+"Reference"\s+"([^"]+)"', body)
print(f"Total symbol references in body: {len(all_refs)}")

unannotated = [r for r in all_refs if '?' in r or not re.search(r'\d', r)]
print("Unannotated or suspicious references in body:")
for u in unannotated:
    print(" ", u)

# Check hex in #PWR
hex_pwr = [r for r in all_refs if r.startswith("#PWR") and any(c in 'abcdef' for c in r.lower())]
print(f"Hex in #PWR: {len(hex_pwr)} items: {hex_pwr}")
