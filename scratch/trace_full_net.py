import pcbnew

b = pcbnew.LoadBoard("scratch/backup_before_sync/curcur40-right.kicad_pcb")

def trace_net(net_name):
    print(f"\n================ Net {net_name} ================")
    pads = []
    tracks = []
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname() == net_name:
                pos = p.GetPosition()
                pads.append((f"{fp.GetReference()} Pad {p.GetNumber()}", pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)))
    
    for t in b.GetTracks():
        if t.GetNetname() == net_name:
            sp = t.GetStart()
            ep = t.GetEnd()
            sx, sy = pcbnew.ToMM(sp.x), pcbnew.ToMM(sp.y)
            ex, ey = pcbnew.ToMM(ep.x), pcbnew.ToMM(ep.y)
            layer = b.GetLayerName(t.GetLayer())
            is_via = isinstance(t, pcbnew.PCB_VIA)
            tracks.append((layer, (sx, sy), (ex, ey), is_via))
            
    print("Pads:")
    for p in pads:
        print(f"  {p[0]}: ({p[1]:.3f}, {p[2]:.3f})")
    print(f"Tracks ({len(tracks)}):")
    for tr in tracks:
        print(f"  {tr[0]:5} : {tr[1]} -> {tr[2]} (via={tr[3]})")

for n in ["/SCLK", "/MOSI", "/MISO", "/NCS", "+3V3R"]:
    trace_net(n)
