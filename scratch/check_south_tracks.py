import pcbnew
b = pcbnew.LoadBoard('scratch/test_left_orig.kicad_pcb')
print("=== Tracks between y=40.0 and 50.0 in x in [-105, -85] ===")
for t in b.GetTracks():
    if t.GetClass() == 'PCB_TRACK':
        s, e = t.GetStart(), t.GetEnd()
        sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
        ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)
        if -105 <= min(sx, ex) and max(sx, ex) <= -85 and min(sy, ey) >= 40.0 and max(sy, ey) <= 50.0:
            print(f"Track [{t.GetNetname()}] on {t.GetLayerName()}: ({sx:.3f}, {sy:.3f}) -> ({ex:.3f}, {ey:.3f})")

print("=== Footprints between y=40.0 and 50.0 in x in [-105, -85] ===")
for fp in b.GetFootprints():
    pos = fp.GetPosition()
    px, py = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
    if -105 <= px <= -85 and 39.0 <= py <= 52.0:
        print(f"FP {fp.GetReference()} at ({px:.3f}, {py:.3f})")
