import pcbnew
b = pcbnew.LoadBoard('pcbs/curcur40/right/curcur40-right.kicad_pcb')
print("=== Right PCB tracks around Hole 3 (X in [85, 105], Y in [33, 42]) ===")
for t in b.GetTracks():
    if t.GetNetname() in ['/KEY16', '/KEY17', '/KEY18']:
        s, e = t.GetStart(), t.GetEnd()
        sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
        ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)
        if 85 <= min(sx, ex) and max(sx, ex) <= 105 and 33 <= min(sy, ey) and max(sy, ey) <= 42:
            print(f"Track [{t.GetNetname()}] on {t.GetLayerName()}: ({sx:.3f}, {sy:.3f}) -> ({ex:.3f}, {ey:.3f})")
