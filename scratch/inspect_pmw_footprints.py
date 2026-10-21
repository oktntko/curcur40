import pcbnew

board = pcbnew.LoadBoard("pcbs/curcur40/right/curcur40-right.kicad_pcb")

print("Mounting holes in PMW region:")
for fp in board.GetFootprints():
    ref = fp.GetReference()
    pos = fp.GetPosition()
    x = pcbnew.ToMM(pos.x)
    y = pcbnew.ToMM(pos.y)
    if -5 <= x <= 25 and 35 <= y <= 75:
        print(f"  {ref:10} at ({x:8.3f}, {y:8.3f}) val={fp.GetValue()} fp={fp.GetFPID().GetLibItemName()}")
