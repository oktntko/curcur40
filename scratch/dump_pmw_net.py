import pcbnew

b = pcbnew.LoadBoard('scratch/head_pmw3360.kicad_pcb')
for code, n in b.GetNetInfo().NetsByNetcode().items():
    netname = n.GetNetname()
    if not netname or 'unconnected' in netname:
        continue
    pads = [f"{p.GetParentFootprint().GetReference()}.{p.GetName()}" for p in b.GetPads() if p.GetNetname() == netname]
    print(f"{netname}: {pads}")
