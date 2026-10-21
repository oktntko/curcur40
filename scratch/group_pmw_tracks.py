import pcbnew

pcb_pmw = pcbnew.LoadBoard("scratch/pmw3360_pcb_b9043a22.kicad_pcb")

# Group tracks by net
nets = {}
for t in pcb_pmw.GetTracks():
    net = t.GetNetname()
    nets.setdefault(net, []).append(t)

for net, items in sorted(nets.items()):
    vias = [x for x in items if isinstance(x, pcbnew.PCB_VIA)]
    tracks = [x for x in items if not isinstance(x, pcbnew.PCB_VIA)]
    print(f"Net {net:15}: {len(tracks):2} tracks, {len(vias):2} vias")
