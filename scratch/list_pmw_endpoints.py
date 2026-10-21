import pcbnew

board = pcbnew.LoadBoard("pcbs/curcur40/right/curcur40-right.kicad_pcb")

pmw_nets = [
    "/SCLK", "/MOSI", "/MISO", "/NCS", "/CS", "/RESET", 
    "+3V3R", "GNDR", "+1V8_PMW", "V_{IO}", "Net-(U1-LED_P)", "Net-(U2-NC)"
]

print("=== PADS PER NET ===")
for netname in pmw_nets:
    pads = [p for p in board.GetPads() if p.GetNetname() == netname and (pcbnew.ToMM(p.GetPosition().x) < 30 and pcbnew.ToMM(p.GetPosition().y) > 35)]
    print(f"Net: {netname} ({len(pads)} local pads):")
    for p in pads:
        ref = p.GetParentFootprint().GetReference()
        pos = p.GetPosition()
        print(f"  {ref} pin {p.GetNumber()} at ({pcbnew.ToMM(pos.x):.3f}, {pcbnew.ToMM(pos.y):.3f})")

print("\n=== EXTERNAL ARRIVAL VIAS/TRACKS (connections coming from keyboard) ===")
# Where does each net cross X=30 or connect to the rest of the board?
for netname in ["/SCLK", "/MOSI", "/MISO", "/NCS", "+3V3R", "GNDR"]:
    tracks = [t for t in board.GetTracks() if t.GetNetname() == netname]
    print(f"\nNet: {netname}")
    for t in tracks:
        if t.GetClass() == "PCB_VIA":
            pos = t.GetPosition()
            px, py = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
            if px < 25 and py > 35:
                print(f"  Via at ({px:.3f}, {py:.3f})")
        else:
            sp, ep = t.GetStart(), t.GetEnd()
            sx, sy = pcbnew.ToMM(sp.x), pcbnew.ToMM(sp.y)
            ex, ey = pcbnew.ToMM(ep.x), pcbnew.ToMM(ep.y)
            if (sx > 25 and ex <= 25) or (ex > 25 and sx <= 25):
                print(f"  Cross-boundary track: ({sx:.3f}, {sy:.3f}) -> ({ex:.3f}, {ey:.3f}) on {t.GetLayerName()}")
