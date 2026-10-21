import pcbnew

board = pcbnew.LoadBoard("pcbs/curcur40/right/curcur40-right.kicad_pcb")
u1 = board.FindFootprintByReference("U1")

print("U1 pads:")
for pad in sorted(u1.Pads(), key=lambda p: int(p.GetNumber())):
    pos = pad.GetPosition()
    print(f"  Pin {pad.GetNumber():>2}: ({pcbnew.ToMM(pos.x):8.4f}, {pcbnew.ToMM(pos.y):8.4f}) net={pad.GetNetname()}")
