import pcbnew
b = pcbnew.LoadBoard('scratch/test_left_orig.kicad_pcb')
print("=== Items between Y=28.0 and Y=34.5 in X in [-105, -88] ===")
for t in b.GetTracks():
    if t.GetClass() == 'PCB_TRACK':
        s, e = t.GetStart(), t.GetEnd()
        sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
        ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)
        if -105 <= min(sx, ex) and max(sx, ex) <= -88 and min(sy, ey) >= 28.0 and max(sy, ey) <= 34.5:
            print(f"Track [{t.GetNetname()}] on {t.GetLayerName()}: ({sx:.3f}, {sy:.3f}) -> ({ex:.3f}, {ey:.3f})")

for fp in b.GetFootprints():
    pos = fp.GetPosition()
    px, py = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
    if -105 <= px <= -88 and 25.0 <= py <= 35.0:
        print(f"FP {fp.GetReference()} at ({px:.3f}, {py:.3f})")
