import pcbnew

board = pcbnew.LoadBoard('pcbs/curcur40/right/curcur40-right.kicad_pcb')
for t in board.GetTracks():
    name = t.GetNetname()
    if name in ('/KEY16', '/KEY17', '/KEY18'):
        sp, ep = t.GetStart(), t.GetEnd()
        sx, sy = sp.x / 1e6, sp.y / 1e6
        ex, ey = ep.x / 1e6, ep.y / 1e6
        is_via = t.GetClass() == 'PCB_VIA'
        print(f"{name}: ({sx:.3f}, {sy:.3f}) -> ({ex:.3f}, {ey:.3f}) layer={t.GetLayerName()} via={is_via}")
