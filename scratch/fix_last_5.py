import pcbnew

def fix_last_5():
    board = pcbnew.LoadBoard(r"pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pcb")
    netinfo = board.GetNetInfo()
    net_gnd = netinfo.GetNetItem("GND")
    net_vin = netinfo.GetNetItem("V_{IN}")
    net_vdd = netinfo.GetNetItem("VDD")

    def add_track(net, x1, y1, x2, y2, layer=pcbnew.F_Cu, width=0.25):
        trk = pcbnew.PCB_TRACK(board)
        trk.SetLayer(layer)
        trk.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
        trk.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
        trk.SetWidth(pcbnew.FromMM(width))
        trk.SetNet(net)
        board.Add(trk)

    def add_via(net, x, y, drill=0.3, size=0.6):
        via = pcbnew.PCB_VIA(board)
        via.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
        via.SetDrill(pcbnew.FromMM(drill))
        via.SetWidth(pcbnew.FromMM(size))
        via.SetNet(net)
        board.Add(via)

    # 1. C5 pad 2 (154.363, 104.400) directly connect to GND zone and C4 pad 2 / ground plane
    add_track(net_gnd, 154.363, 104.400, 154.363, 105.100, layer=pcbnew.F_Cu, width=0.30)
    add_via(net_gnd, 154.363, 105.100)
    # Bridge to bottom copper track to ensure robust return path
    add_track(net_gnd, 154.363, 105.100, 149.000, 105.100, layer=pcbnew.B_Cu, width=0.30)
    add_track(net_gnd, 149.000, 105.100, 147.200, 104.463, layer=pcbnew.B_Cu, width=0.30)

    # 2. V_{IN}: connect C3 pad 1 (136.637, 103.600) to U2 pad 1 (143.363, 102.650) directly on F.Cu
    add_track(net_vin, 136.637, 103.600, 138.000, 103.600, layer=pcbnew.F_Cu, width=0.30)
    add_track(net_vin, 138.000, 103.600, 139.500, 105.100, layer=pcbnew.F_Cu, width=0.30)
    add_track(net_vin, 139.500, 105.100, 142.000, 105.100, layer=pcbnew.F_Cu, width=0.30)
    add_track(net_vin, 142.000, 105.100, 143.363, 104.550, layer=pcbnew.F_Cu, width=0.30)

    # 3. VDD: connect C4 pad 1 (147.200, 102.737) to B.Cu track at (154.500, 102.088)
    add_via(net_vdd, 147.200, 102.737)
    add_track(net_vdd, 147.200, 102.737, 154.500, 102.088, layer=pcbnew.B_Cu, width=0.30)

    # 4. GND stitching on right edge to tie isolated zones
    add_via(net_gnd, 154.500, 88.000)
    add_via(net_gnd, 154.500, 91.000)

    # Refill zones
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())

    board.Save(r"pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pcb")
    print("Fixed last 5 items.")

if __name__ == "__main__":
    fix_last_5()
