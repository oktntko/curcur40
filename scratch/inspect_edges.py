import pcbnew

b_plate = pcbnew.LoadBoard('plates/curcur40/pcb/plate-top-left.kicad_pcb')
print("=== Plate-top-left Edge.Cuts around pinky ===")
for d in b_plate.GetDrawings():
    if d.GetLayerName() == "Edge.Cuts":
        s, e = d.GetStart(), d.GetEnd()
        sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
        ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)
        if -110 <= min(sx, ex) and max(sx, ex) <= -80 and min(sy, ey) >= 35.0:
            print(f"Edge {d.GetShapeStr()}: ({sx:.3f}, {sy:.3f}) -> ({ex:.3f}, {ey:.3f})")

b_pcb = pcbnew.LoadBoard('pcbs/curcur40/left/curcur40-left.kicad_pcb')
print("\n=== PCB Edge.Cuts around pinky ===")
for d in b_pcb.GetDrawings():
    if d.GetLayerName() == "Edge.Cuts":
        s, e = d.GetStart(), d.GetEnd()
        sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
        ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)
        if -110 <= min(sx, ex) and max(sx, ex) <= -80 and min(sy, ey) >= 35.0:
            print(f"Edge {d.GetShapeStr()}: ({sx:.3f}, {sy:.3f}) -> ({ex:.3f}, {ey:.3f})")
