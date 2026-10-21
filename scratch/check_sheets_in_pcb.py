import re
from pathlib import Path

pcb = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")

sheets = set()
for m in re.finditer(r'\(sheetname\s+"([^"]*)"\)\s+\(sheetfile\s+"([^"]*)"\)', pcb):
    sheets.add((m.group(1), m.group(2)))

print("Sheetnames and sheetfiles in curcur40-right.kicad_pcb:")
for s in sorted(sheets):
    print(s)

# Also check any (sheetfile ...) without sheetname
sheetfiles_only = set(re.findall(r'\(sheetfile\s+"([^"]*)"\)', pcb))
print("\nAll sheetfiles:")
for sf in sorted(sheetfiles_only):
    print(sf)
