import pcbnew

b_orig = pcbnew.LoadBoard('scratch/pmw3360_pcb_b9043a22.kicad_pcb')

# Let's inspect all tracks in b_orig
print("Total tracks/vias in b_orig:", len(b_orig.GetTracks()))
for t in b_orig.GetTracks():
    net = t.GetNetname()
    if t.GetClass() == 'PCB_TRACK':
        layer = t.GetLayerName()
        s = (t.GetStart().x/1e6, t.GetStart().y/1e6)
        e = (t.GetEnd().x/1e6, t.GetEnd().y/1e6)
        w = t.GetWidth()/1e6
        print(f"TRACK: {net:15} {layer:5} {s} -> {e} (w={w:.2f})")
    elif t.GetClass() == 'PCB_VIA':
        pos = (t.GetPosition().x/1e6, t.GetPosition().y/1e6)
        print(f"VIA:   {net:15} pos={pos}")
