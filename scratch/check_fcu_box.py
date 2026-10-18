import pcbnew
b = pcbnew.LoadBoard('scratch/test_left_orig.kicad_pcb')
print("=== F.Cu items in box X in [-104, -88], Y in [34, 41] ===")
for t in b.GetTracks():
    if t.GetClass() == 'PCB_TRACK' and t.GetLayerName() == 'F.Cu':
        s, e = t.GetStart(), t.GetEnd()
        sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
        ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)
        if -104 <= min(sx, ex) and max(sx, ex) <= -88 and 34 <= min(sy, ey) and max(sy, ey) <= 41:
            print(f"F.Cu Track [{t.GetNetname()}]: ({sx:.3f}, {sy:.3f}) -> ({ex:.3f}, {ey:.3f})")
for v in b.GetTracks():
    if v.GetClass() == 'PCB_VIA':
        pos = v.GetPosition()
        vx, vy = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
        if -104 <= vx <= -88 and 34 <= vy <= 41:
            print(f"Via [{v.GetNetname()}] at ({vx:.3f}, {vy:.3f})")
