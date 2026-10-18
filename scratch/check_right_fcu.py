import pcbnew

board = pcbnew.LoadBoard('pcbs/curcur40/right/curcur40-right.kicad_pcb')
for t in board.GetTracks():
    sp, ep = t.GetStart(), t.GetEnd()
    sx, sy = sp.x / 1e6, sp.y / 1e6
    ex, ey = ep.x / 1e6, ep.y / 1e6
    if min(sx, ex) > 85 and max(sx, ex) < 105 and min(sy, ey) > 33 and max(sy, ey) < 42:
        if t.GetLayerName() == 'F.Cu':
            is_via = t.GetClass() == 'PCB_VIA'
            print(f"{t.GetNetname()}: ({sx:.3f}, {sy:.3f}) -> ({ex:.3f}, {ey:.3f}) via={is_via}")
