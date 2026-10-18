import pcbnew

b = pcbnew.LoadBoard('scratch/test_left_orig.kicad_pcb')

print("=== Items between X in [-102, -88] and Y in [33, 37] ===")
for t in b.GetTracks():
    if t.GetClass() == "PCB_TRACK":
        s, e = t.GetStart(), t.GetEnd()
        sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
        ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)
        if -102 <= min(sx, ex) and max(sx, ex) <= -88 and 33 <= min(sy, ey) and max(sy, ey) <= 37:
            print(f"Track [{t.GetNetname()}] on {t.GetLayerName()}: ({sx:.3f}, {sy:.3f}) -> ({ex:.3f}, {ey:.3f})")
