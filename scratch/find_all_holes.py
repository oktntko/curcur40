import pcbnew

board = pcbnew.LoadBoard("pcbs/curcur40/right/curcur40-right.kicad_pcb")

print("All mounting holes in right pcb:")
for fp in board.GetFootprints():
    fp_id = str(fp.GetFPID().GetLibItemName())
    ref = fp.GetReference()
    if "hole" in fp_id.lower() or "mounting" in fp_id.lower() or ref.startswith("H"):
        pos = fp.GetPosition()
        print(f"  {ref:10} at ({pcbnew.ToMM(pos.x):8.3f}, {pcbnew.ToMM(pos.y):8.3f}) val={fp.GetValue()} fp={fp_id}")
