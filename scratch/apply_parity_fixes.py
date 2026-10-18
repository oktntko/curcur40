import re
import json

# 1. Update U4 footprint from Package_SO:SOIC-8_5.23x5.23mm_P1.27mm to Package_SO:SOIC-8_5.3x5.3mm_P1.27mm
files_to_update_u4 = [
    'pcbs/curcur40/left/curcur40-left.kicad_sch',
    'pcbs/curcur40/left/curcur40-left.kicad_pcb',
    'pcbs/curcur40/right/curcur40-right.kicad_sch',
    'pcbs/curcur40/right/curcur40-right.kicad_pcb'
]

for path in files_to_update_u4:
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    c_new = c.replace('SOIC-8_5.23x5.23mm_P1.27mm', 'SOIC-8_5.3x5.3mm_P1.27mm')
    if c != c_new:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(c_new)
        print(f"Updated SOIC-8 footprint name in {path}")

# 2. Update curcur40-pmw3360.kicad_sch:
# - H1~H4: footprint MountingHole_2.2mm_M2, value H1/H2/H3/H4
with open('pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_sch', 'r', encoding='utf-8') as f:
    sch = f.read()

# Replace MountingHole_3.2mm_M3_ISO14580 with MountingHole_2.2mm_M2
sch = sch.replace('MountingHole:MountingHole_3.2mm_M3_ISO14580', 'MountingHole:MountingHole_2.2mm_M2')
sch = sch.replace('MountingHole_Pad', 'MountingHole_2.2mm_M2')

with open('pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_sch', 'w', encoding='utf-8') as f:
    f.write(sch)
print("Updated PMW3360 schematic mounting holes")

# 3. Update curcur40-pmw3360.kicad_pcb:
# - C5, R1, R4: set dnp yes to match schematic
with open('pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pcb', 'r', encoding='utf-8') as f:
    pmw_pcb = f.read()

# For C5, R1, R4 footprints, add (dnp yes) if (attr smd)
for ref in ['C5', 'R1', 'R4']:
    idx = pmw_pcb.find(f'property "Reference" "{ref}"')
    if idx != -1:
        fp_start = pmw_pcb.rfind('(footprint', 0, idx)
        fp_end = pmw_pcb.find('\n\t)', idx)
        fp_text = pmw_pcb[fp_start:fp_end]
        if '(attr smd)' in fp_text and '(attr smd dnp)' not in fp_text:
            new_fp = fp_text.replace('(attr smd)', '(attr smd dnp)')
            pmw_pcb = pmw_pcb[:fp_start] + new_fp + pmw_pcb[fp_end:]
            print(f"Set dnp on PMW3360 PCB {ref}")

with open('pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pmw_pcb)

print("Fixes applied successfully.")
