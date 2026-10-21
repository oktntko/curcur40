import re
from pathlib import Path

pcb_pmw = Path("scratch/pmw3360_pcb_b9043a22.kicad_pcb").read_text(encoding="utf-8")
pcb_right = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")

fps = ["U1", "U2", "JP1", "R1", "R2", "R3", "R4", "C1", "C2", "C3", "C4", "C5"]

def get_positions(pcb_text):
    res = {}
    for ref in fps:
        pos = pcb_text.find(f'"{ref}"')
        f_start = pcb_text.rfind('(footprint', 0, pos)
        m = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)(?:\s+([\d\.\-]+))?\)', pcb_text[f_start:pos+50])
        if m:
            x, y = float(m.group(1)), float(m.group(2))
            rot = float(m.group(3)) if m.group(3) else 0.0
            res[ref] = (x, y, rot)
    return res

pos_pmw = get_positions(pcb_pmw)
pos_right = get_positions(pcb_right)

u1_pmw = pos_pmw["U1"]
u1_right = pos_right["U1"]
print(f"U1 in PMW PCB: {u1_pmw}")
print(f"U1 in Right PCB: {u1_right}")
print(f"Delta U1: ({u1_right[0] - u1_pmw[0]}, {u1_right[1] - u1_pmw[1]}), Rot diff: {u1_right[2] - u1_pmw[2]}")

print("\nComparing relative positions to U1:")
all_match = True
for ref in fps:
    dp = (pos_pmw[ref][0] - u1_pmw[0], pos_pmw[ref][1] - u1_pmw[1], pos_pmw[ref][2] - u1_pmw[2])
    dr = (pos_right[ref][0] - u1_right[0], pos_right[ref][1] - u1_right[1], pos_right[ref][2] - u1_right[2])
    diff = (round(dr[0] - dp[0], 4), round(dr[1] - dp[1], 4), round(dr[2] - dp[2], 4))
    if diff != (0, 0, 0):
        all_match = False
        print(f"  {ref:4}: diff={diff}")
    else:
        print(f"  {ref:4}: PERFECT RELATIVE MATCH")

print(f"\nAll match: {all_match}")
