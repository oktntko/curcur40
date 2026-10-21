import pcbnew

pcb_pmw = pcbnew.LoadBoard("scratch/pmw3360_pcb_b9043a22.kicad_pcb")
pcb_right = pcbnew.LoadBoard("pcbs/curcur40/right/curcur40-right.kicad_pcb")

fps = ["U1", "U2", "JP1", "R1", "R2", "R3", "R4", "C1", "C2", "C3", "C4", "C5"]

u1_p = pcb_pmw.FindFootprintByReference("U1").GetPosition()
u1_r = pcb_right.FindFootprintByReference("U1").GetPosition()

print(f"{'Ref':4} | {'PMW center':20} | {'Right center':20} | {'Rel PMW (dx, dy)':22} | {'Rel Right (dx, dy)':22}")
for ref in fps:
    fp_p = pcb_pmw.FindFootprintByReference(ref).GetPosition()
    fp_r = pcb_right.FindFootprintByReference(ref).GetPosition()
    dx_p = round(pcbnew.ToMM(fp_p.x - u1_p.x), 4)
    dy_p = round(pcbnew.ToMM(fp_p.y - u1_p.y), 4)
    dx_r = round(pcbnew.ToMM(fp_r.x - u1_r.x), 4)
    dy_r = round(pcbnew.ToMM(fp_r.y - u1_r.y), 4)
    print(f"{ref:4} | ({pcbnew.ToMM(fp_p.x):8.3f}, {pcbnew.ToMM(fp_p.y):8.3f}) | ({pcbnew.ToMM(fp_r.x):8.3f}, {pcbnew.ToMM(fp_r.y):8.3f}) | ({dx_p:8.3f}, {dy_p:8.3f}) | ({dx_r:8.3f}, {dy_r:8.3f})")
