import pcbnew

board = pcbnew.LoadBoard("pcbs/curcur40/right/curcur40-right.kicad_pcb")

print("=== Items in East corridor: X in [18.0, 25.0], Y in [38.0, 68.0] ===")
for t in board.GetTracks():
    if t.GetClass() == "PCB_VIA":
        p = t.GetPosition()
        x, y = pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)
        if 18.0 <= x <= 25.0 and 38.0 <= y <= 68.0:
            print(f"Via: net={t.GetNetname()} at ({x:.3f}, {y:.3f})")
    else:
        p1, p2 = t.GetStart(), t.GetEnd()
        x1, y1 = pcbnew.ToMM(p1.x), pcbnew.ToMM(p1.y)
        x2, y2 = pcbnew.ToMM(p2.x), pcbnew.ToMM(p2.y)
        if (18.0 <= x1 <= 25.0 and 38.0 <= y1 <= 68.0) or (18.0 <= x2 <= 25.0 and 38.0 <= y2 <= 68.0):
            print(f"Track: net={t.GetNetname()}, layer={t.GetLayerName()} from ({x1:.3f}, {y1:.3f}) to ({x2:.3f}, {y2:.3f})")

for fp in board.GetFootprints():
    p = fp.GetPosition()
    x, y = pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)
    if 18.0 <= x <= 25.0 and 38.0 <= y <= 68.0:
        print(f"Footprint {fp.GetReference()} at ({x:.3f}, {y:.3f})")
