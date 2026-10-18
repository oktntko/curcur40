import pcbnew

board = pcbnew.LoadBoard('pcbs/curcur40/right/curcur40-right.kicad_pcb')

# Let's inspect all tracks in X in [85, 102], Y in [33, 42]
print("All tracks in corridor [85, 102] x [33, 42]:")
for t in board.GetTracks():
    sp, ep = t.GetStart(), t.GetEnd()
    sx, sy = sp.x / 1e6, sp.y / 1e6
    ex, ey = ep.x / 1e6, ep.y / 1e6
    if max(sx, ex) > 85 and min(sx, ex) < 102 and max(sy, ey) > 33 and min(sy, ey) < 42:
        is_via = t.GetClass() == 'PCB_VIA'
        print(f"  {t.GetNetname():15s} {t.GetLayerName():6s} ({sx:7.3f}, {sy:7.3f}) -> ({ex:7.3f}, {ey:7.3f}) via={is_via}")
