import pcbnew

b = pcbnew.LoadBoard('pcbs/curcur40/left/curcur40-left.kicad_pcb')

print("=== Footprints in target area ===")
for fp in b.GetFootprints():
    pos = fp.GetPosition()
    px, py = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
    if -105 <= px <= -85 and 35 <= py <= 42:
        print(f"FP {fp.GetReference()} at ({px:.3f}, {py:.3f})")
        for p in fp.Pads():
            ppos = p.GetPosition()
            print(f"   Pad {p.GetName()} [{p.GetNetname()}] at ({pcbnew.ToMM(ppos.x):.3f}, {pcbnew.ToMM(ppos.y):.3f})")

print("\n=== Tracks in target area ===")
for t in b.GetTracks():
    if t.GetClass() == "PCB_TRACK":
        s, e = t.GetStart(), t.GetEnd()
        sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
        ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)
        if (-105 <= sx <= -85 or -105 <= ex <= -85) and (34 <= sy <= 42 or 34 <= ey <= 42):
            print(f"Track [{t.GetNetname()}] on {t.GetLayerName()}: ({sx:.3f}, {sy:.3f}) -> ({ex:.3f}, {ey:.3f}) len={pcbnew.ToMM(t.GetLength()):.3f}")
