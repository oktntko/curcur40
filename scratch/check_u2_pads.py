import pcbnew

pcb_pmw = pcbnew.LoadBoard("scratch/pmw3360_pcb_b9043a22.kicad_pcb")
pcb_right = pcbnew.LoadBoard("pcbs/curcur40/right/curcur40-right.kicad_pcb")

u2_p = pcb_pmw.FindFootprintByReference("U2")
u2_r = pcb_right.FindFootprintByReference("U2")

print("U2 PMW pads:")
for pad in u2_p.Pads():
    pos = pad.GetPosition()
    print(f"  Pad {pad.GetNumber()}: ({pcbnew.ToMM(pos.x):.4f}, {pcbnew.ToMM(pos.y):.4f}) net={pad.GetNetname()}")

print("\nU2 Right pads:")
for pad in u2_r.Pads():
    pos = pad.GetPosition()
    print(f"  Pad {pad.GetNumber()}: ({pcbnew.ToMM(pos.x):.4f}, {pcbnew.ToMM(pos.y):.4f}) net={pad.GetNetname()}")
