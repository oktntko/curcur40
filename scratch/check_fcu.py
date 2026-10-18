import pcbnew
b = pcbnew.LoadBoard('scratch/test_left_orig.kicad_pcb')
for t in b.GetTracks():
    if t.GetClass() == 'PCB_TRACK' and t.GetLayerName() == 'F.Cu':
        s, e = t.GetStart(), t.GetEnd()
        sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
        ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)
        if -104 <= min(sx, ex) and max(sx, ex) <= -86 and 34 <= min(sy, ey) and max(sy, ey) <= 42:
            print(f"F.Cu {t.GetNetname()}: ({sx:.3f}, {sy:.3f}) -> ({ex:.3f}, {ey:.3f})")
