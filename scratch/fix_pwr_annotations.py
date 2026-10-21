import re
from pathlib import Path

sch_path = Path("pcbs/curcur40/right/curcur40-right.kicad_sch")
sch = sch_path.read_text(encoding="utf-8")

# Find all #PWR symbols that contain hex letters a-f
hex_pwr_refs = list(set(re.findall(r'#PWR0[0-9a-fA-F]*[a-fA-F][0-9a-fA-F]*', sch)))
print(f"Hex #PWR references found: {hex_pwr_refs}")

start_num = 201
for old_ref in hex_pwr_refs:
    new_ref = f"#PWR0{start_num}"
    start_num += 1
    print(f"Replacing {old_ref} with {new_ref}")
    sch = sch.replace(f'"{old_ref}"', f'"{new_ref}"')

sch_path.write_text(sch, encoding="utf-8")
print("Updated schematic.")
