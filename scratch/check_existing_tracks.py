import pcbnew

b = pcbnew.LoadBoard('scratch/backup_before_sync/curcur40-right.kicad_pcb')
print("Tracks in PMW area in backup:")
for t in b.GetTracks():
    sp = t.GetStart()
    ep = t.GetEnd()
    sx, sy = pcbnew.ToMM(sp.x), pcbnew.ToMM(sp.y)
    ex, ey = pcbnew.ToMM(ep.x), pcbnew.ToMM(ep.y)
    if (-5 <= sx <= 25 and 38 <= sy <= 70) or (-5 <= ex <= 25 and 38 <= ey <= 70):
        print(f"{t.GetNetname()}: ({sx:.2f},{sy:.2f}) -> ({ex:.2f},{ey:.2f}) on {b.GetLayerName(t.GetLayer())} is_via={isinstance(t, pcbnew.PCB_VIA)}")
