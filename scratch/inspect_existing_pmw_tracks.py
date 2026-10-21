import pcbnew

board = pcbnew.LoadBoard("pcbs/curcur40/right/curcur40-right.kicad_pcb")

pmw_nets = {"/SCLK", "/MOSI", "/MISO", "/NCS", "/CS", "/RESET", "/MOTION", "+3V3R", "GNDR", "+1V8_PMW", "V_{IO}", "Net-(U1-LED_P)", "Net-(U2-NC)"}

for track in board.GetTracks():
    netname = track.GetNetname()
    if netname in pmw_nets:
        if track.GetClass() == "PCB_VIA":
            pos = track.GetPosition()
            px, py = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
            if px < 35 and py > 35:
                print(f"Via: net={netname}, at ({px:.3f}, {py:.3f}), layers={track.GetLayerName()}")
        else:
            sp = track.GetStart()
            ep = track.GetEnd()
            sx, sy = pcbnew.ToMM(sp.x), pcbnew.ToMM(sp.y)
            ex, ey = pcbnew.ToMM(ep.x), pcbnew.ToMM(ep.y)
            if (sx < 35 and sy > 35) or (ex < 35 and ey > 35):
                print(f"Track: net={netname}, layer={track.GetLayerName()}, from ({sx:.3f}, {sy:.3f}) to ({ex:.3f}, {ey:.3f})")
