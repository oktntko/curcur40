import pcbnew

board = pcbnew.LoadBoard('pcbs/curcur40/right/curcur40-right.kicad_pcb')
for netname in ['/KEY13', '/KEY14', '/KEY16', '/KEY17', '/KEY18']:
    pads = [p for p in board.GetPads() if p.GetNetname() == netname]
    pad_strs = [f"{p.GetParentFootprint().GetReference()}.{p.GetNumber()} at ({p.GetPosition().x/1e6:.2f}, {p.GetPosition().y/1e6:.2f})" for p in pads]
    print(f"{netname}: {pad_strs}")
