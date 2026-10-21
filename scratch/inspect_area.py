import pcbnew

board = pcbnew.LoadBoard("pcbs/curcur40/right/curcur40-right.kicad_pcb")

print("=== Footprints near PMW3360 ===")
for fp in board.GetFootprints():
    ref = fp.GetReference()
    pos = fp.GetPosition()
    px, py = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
    if px < 30 and py > 35:
        print(f"Footprint {ref} at ({px:.3f}, {py:.3f}), layer={fp.GetLayerName()}, rot={fp.GetOrientationDegrees()}")
        for pad in fp.Pads():
            pp = pad.GetPosition()
            print(f"  Pad {pad.GetNumber()}: net={pad.GetNetname()}, at ({pcbnew.ToMM(pp.x):.3f}, {pcbnew.ToMM(pp.y):.3f})")

print("\n=== Edge.Cuts Segments in the area ===")
for drawing in board.GetDrawings():
    if drawing.GetLayerName() == "Edge.Cuts":
        if hasattr(drawing, 'GetStart') and hasattr(drawing, 'GetEnd'):
            p1 = drawing.GetStart()
            p2 = drawing.GetEnd()
            x1, y1 = pcbnew.ToMM(p1.x), pcbnew.ToMM(p1.y)
            x2, y2 = pcbnew.ToMM(p2.x), pcbnew.ToMM(p2.y)
            if (x1 < 25 or x2 < 25) and (y1 > 35 or y2 > 35):
                print(f"  Edge.Cuts from ({x1:.3f}, {y1:.3f}) to ({x2:.3f}, {y2:.3f})")
