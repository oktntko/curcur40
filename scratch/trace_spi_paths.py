import pcbnew

b = pcbnew.LoadBoard("scratch/backup_before_sync/curcur40-right.kicad_pcb")

nets_to_check = ["/SCLK", "/MOSI", "/MISO", "/NCS", "+3V3R", "GNDR", "/TX"]

print("=== Tracks of interest ===")
for t in b.GetTracks():
    net_name = t.GetNetname()
    if net_name in nets_to_check:
        sp = t.GetStart()
        ep = t.GetEnd()
        sx, sy = pcbnew.ToMM(sp.x), pcbnew.ToMM(sp.y)
        ex, ey = pcbnew.ToMM(ep.x), pcbnew.ToMM(ep.y)
        # only print if in PMW region or near it (X <= 30)
        if sx <= 35 or ex <= 35:
            is_via = isinstance(t, pcbnew.PCB_VIA)
            print(f"[{net_name:10}] {b.GetLayerName(t.GetLayer()):5} : ({sx:.3f}, {sy:.3f}) -> ({ex:.3f}, {ey:.3f}) (via={is_via})")
