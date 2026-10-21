import re
from pathlib import Path
import pcbnew

pcb_pmw = pcbnew.LoadBoard("scratch/pmw3360_pcb_b9043a22.kicad_pcb")
pcb_right = pcbnew.LoadBoard("pcbs/curcur40/right/curcur40-right.kicad_pcb")

fps = ["U1", "U2", "JP1", "R1", "R2", "R3", "R4", "C1", "C2", "C3", "C4", "C5"]

u1_pmw = pcb_pmw.FindFootprintByReference("U1").GetPosition()
u1_right = pcb_right.FindFootprintByReference("U1").GetPosition()

print(f"U1 PMW pos: {pcbnew.ToMM(u1_pmw.x)}, {pcbnew.ToMM(u1_pmw.y)}")
print(f"U1 Right pos: {pcbnew.ToMM(u1_right.x)}, {pcbnew.ToMM(u1_right.y)}")

# Check pad 1 of U1
p1_pmw = pcb_pmw.FindFootprintByReference("U1").FindPadByNumber("1").GetPosition()
p1_right = pcb_right.FindFootprintByReference("U1").FindPadByNumber("1").GetPosition()
print(f"Pad 1 U1 PMW: {pcbnew.ToMM(p1_pmw.x)}, {pcbnew.ToMM(p1_pmw.y)}")
print(f"Pad 1 U1 Right: {pcbnew.ToMM(p1_right.x)}, {pcbnew.ToMM(p1_right.y)}")

# Check pad 1 of U2
p1_u2_pmw = pcb_pmw.FindFootprintByReference("U2").FindPadByNumber("1").GetPosition()
p1_u2_right = pcb_right.FindFootprintByReference("U2").FindPadByNumber("1").GetPosition()
print(f"Pad 1 U2 PMW: {pcbnew.ToMM(p1_u2_pmw.x)}, {pcbnew.ToMM(p1_u2_pmw.y)}")
print(f"Pad 1 U2 Right: {pcbnew.ToMM(p1_u2_right.x)}, {pcbnew.ToMM(p1_u2_right.y)}")
