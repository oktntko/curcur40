import pcbnew

board = pcbnew.LoadBoard("pcbs/curcur40/right/curcur40-right.kicad_pcb")

pmw_refs = ["U1", "U2", "JP1", "R1", "R2", "R3", "R4", "C1", "C2", "C3", "C4", "C5"]

net_pads = {}
for ref in pmw_refs:
    fp = board.FindFootprintByReference(ref)
    for pad in fp.Pads():
        net = pad.GetNetname()
        pos = pad.GetPosition()
        x, y = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
        net_pads.setdefault(net, []).append((ref, pad.GetNumber(), x, y))

for net, pads in sorted(net_pads.items()):
    print(f"=== Net: {net} ({len(pads)} pads) ===")
    for ref, num, x, y in sorted(pads, key=lambda p: (p[0], p[1])):
        print(f"  {ref:4} Pin {num:>2}: ({x:8.4f}, {y:8.4f})")
