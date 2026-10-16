import pcbnew

def fix_connections():
    board = pcbnew.LoadBoard(r"pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pcb")
    netinfo = board.GetNetInfo()
    net_gnd = netinfo.GetNetItem("GND")
    net_miso = netinfo.GetNetItem("/MISO")
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

    # 1. /MISO: R2 pad 2 is at (153.226, 83.534) on F.Cu. Add via to B.Cu at (152.000, 83.534)
    add_track(net_miso, 153.226, 83.534, 152.000, 83.534, layer=pcbnew.F_Cu, width=0.20)
    add_via(net_miso, 152.000, 83.534)

    # 2. V_{IN}: ensure continuous track from J1 pin 2 to U2
    # J1 pin 2 at (135.389, 99.369), C3 pad 1 at (136.637, 103.600)
    add_track(net_vin, 135.389, 99.369, 136.637, 99.369, layer=pcbnew.F_Cu, width=0.30)
    add_track(net_vin, 136.637, 99.369, 136.637, 103.600, layer=pcbnew.F_Cu, width=0.30)

    # 3. VDD: ensure continuous connection between U2 pad 5 (145.637, 102.650) and TP2 / B.Cu bus
    add_track(net_vdd, 147.200, 102.737, 147.200, 101.700, layer=pcbnew.F_Cu, width=0.30)
    # Connect C4 VDD to TP2 VDD via B.Cu
    add_track(net_vdd, 154.500, 84.500, 153.889, 91.584, layer=pcbnew.B_Cu, width=0.30)

    # 4. GND stitching vias across board to eliminate isolated GND islands
    # Top left, top right, bottom left, bottom right, center
    stitching_pts = [
        (136.5, 82.0),
        (148.5, 82.0),
        (136.5, 96.0),
        (154.5, 98.0),
        (149.0, 104.5),
        (140.0, 104.5),
        (145.639, 86.0),
    ]
    for sx, sy in stitching_pts:
        add_via(net_gnd, sx, sy)

    # Refill zones
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())

    board.Save(r"pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pcb")
    print("Fixes applied successfully.")

if __name__ == "__main__":
    fix_connections()
