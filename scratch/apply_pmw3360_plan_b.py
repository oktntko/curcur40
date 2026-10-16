import pcbnew
import math

PCB_PATH = r"pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pcb"

def apply_plan_b():
    board = pcbnew.LoadBoard(PCB_PATH)
    netinfo = board.GetNetInfo()

    net_gnd = netinfo.GetNetItem("GND")
    net_vin = netinfo.GetNetItem("V_{IN}")
    net_vdd = netinfo.GetNetItem("VDD")
    net_vio = netinfo.GetNetItem("V_{IO}")
    net_led_p = netinfo.GetNetItem("Net-(U1-LED_P)")
    net_u2_nc = netinfo.GetNetItem("Net-(U2-NC)")

    # 1. Update Edge.Cuts
    # Dimensions: width 21.75 mm, height 26.50 mm, r = 2.50 mm
    # X range: [134.389, 156.139], center = 145.264
    # Y range: [79.2758, 105.7758], center = 92.5258
    xL = 134.389
    xR = 156.139
    yT = 79.2758
    yB = 105.7758
    rC = 2.5000
    s2 = rC * (1.0 - 0.70710678)

    # Remove existing board Edge.Cuts (drawings on Edge.Cuts, not footprint graphics)
    for d in list(board.GetDrawings()):
        if d.GetLayerName() == "Edge.Cuts":
            board.Delete(d)

    def add_edge_line(x1, y1, x2, y2):
        sh = pcbnew.PCB_SHAPE(board)
        sh.SetShape(pcbnew.SHAPE_T_SEGMENT)
        sh.SetLayer(pcbnew.Edge_Cuts)
        sh.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
        sh.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
        sh.SetWidth(pcbnew.FromMM(0.15))
        board.Add(sh)

    def add_edge_arc(x1, y1, xm, ym, x2, y2):
        sh = pcbnew.PCB_SHAPE(board)
        sh.SetShape(pcbnew.SHAPE_T_ARC)
        sh.SetLayer(pcbnew.Edge_Cuts)
        sh.SetArcGeometry(
            pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)),
            pcbnew.VECTOR2I(pcbnew.FromMM(xm), pcbnew.FromMM(ym)),
            pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)),
        )
        sh.SetWidth(pcbnew.FromMM(0.15))
        board.Add(sh)

    # Rounded rectangle outline
    add_edge_line(xL + rC, yT, xR - rC, yT)
    add_edge_arc(xR - rC, yT, xR - s2, yT + s2, xR, yT + rC)
    add_edge_line(xR, yT + rC, xR, yB - rC)
    add_edge_arc(xR, yB - rC, xR - s2, yB - s2, xR - rC, yB)
    add_edge_line(xR - rC, yB, xL + rC, yB)
    add_edge_arc(xL + rC, yB, xL + s2, yB - s2, xL, yB - rC)
    add_edge_line(xL, yB - rC, xL, yT + rC)
    add_edge_arc(xL, yT + rC, xL + s2, yT + s2, xL + rC, yT)

    # 2. Update Mounting Holes H1, H2, H3, H4
    # Coordinates:
    # H1 (Top-Left):     (141.139, 82.9258)
    # H2 (Top-Right):    (150.139, 82.9258)
    # H3 (Bottom-Left):  (141.139, 102.1258)
    # H4 (Bottom-Right): (150.139, 102.1258)
    hole_coords = {
        "H1": (141.139, 82.9258),
        "H2": (150.139, 82.9258),
        "H3": (141.139, 102.1258),
        "H4": (150.139, 102.1258),
    }

    for ref, (hx, hy) in hole_coords.items():
        fp = board.FindFootprintByReference(ref)
        if fp:
            fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(hx), pcbnew.FromMM(hy)))
            # Ensure M2 hole size (2.2mm drill, 2.2mm pad)
            for pad in fp.Pads():
                pad.SetDrillSize(pcbnew.VECTOR2I(pcbnew.FromMM(2.2), pcbnew.FromMM(2.2)))
                pad.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(2.2), pcbnew.FromMM(2.2)))

    # 3. Relocate Test Points TP1, TP2, TP3 in top area between top M2 holes
    # TP1 (GND), TP2 (VDD), TP3 (VIO)
    tp_coords = {
        "TP3": (143.639, 81.200),
        "TP1": (145.639, 81.200),
        "TP2": (147.639, 81.200),
    }
    for ref, (tx, ty) in tp_coords.items():
        fp = board.FindFootprintByReference(ref)
        if fp:
            fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(tx), pcbnew.FromMM(ty)))

    # 4. Relocate bottom LDO circuit: U2, C3, C4, C5, R3, R4
    # U2 (SOT-23-5): centered at (145.639, 103.200) rot=0
    # C3 (VIN 1uF): at (143.100, 103.200) rot=-90
    # C4 (VDD 1uF): at (148.178, 103.200) rot=-90
    # R3 (LED_P 39R): at (145.639, 98.700) rot=0
    # R4 (28k): at (148.178, 98.700) rot=0
    # C5 (22nF): at (148.178, 100.700) rot=0
    comp_locs = {
        "U2": ((145.639, 103.200), 0.0),
        "C3": ((143.100, 103.200), -90.0),
        "C4": ((148.178, 103.200), -90.0),
        "R3": ((145.639, 98.700), 0.0),
        "R4": ((148.178, 98.700), 0.0),
        "C5": ((148.178, 100.700), 0.0),
    }
    for ref, ((cx, cy), rot) in comp_locs.items():
        fp = board.FindFootprintByReference(ref)
        if fp:
            fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(cx), pcbnew.FromMM(cy)))
            fp.SetOrientationDegrees(rot)

    # 5. Remove existing tracks in bottom area (y > 97.0) and near top holes
    for t in list(board.GetTracks()):
        if t.GetClass() != "PCB_VIA":
            y1 = pcbnew.ToMM(t.GetStart().y)
            y2 = pcbnew.ToMM(t.GetEnd().y)
            x1 = pcbnew.ToMM(t.GetStart().x)
            x2 = pcbnew.ToMM(t.GetEnd().x)
            # Delete tracks in bottom relocated circuit area
            if max(y1, y2) > 97.0:
                board.Delete(t)
            # Delete tracks near top holes (H1, H2) or top test points (y < 83.5)
            elif min(y1, y2) < 83.5 and (x1 > 140.0 or x2 > 140.0):
                board.Delete(t)

    # Delete vias in bottom area (y > 97.0)
    for v in list(board.GetTracks()):
        if v.GetClass() == "PCB_VIA":
            vy = pcbnew.ToMM(v.GetPosition().y)
            if vy > 97.0:
                board.Delete(v)

    # Helper to add track
    def add_track(net, x1, y1, x2, y2, layer=pcbnew.F_Cu, width=0.25):
        trk = pcbnew.PCB_TRACK(board)
        trk.SetLayer(layer)
        trk.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
        trk.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
        trk.SetWidth(pcbnew.FromMM(width))
        trk.SetNet(net)
        board.Add(trk)

    def add_poly_track(net, pts, layer=pcbnew.F_Cu, width=0.25):
        for i in range(len(pts) - 1):
            add_track(net, pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], layer, width)

    def add_via(net, x, y, drill=0.3, size=0.6):
        via = pcbnew.PCB_VIA(board)
        via.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
        via.SetDrill(pcbnew.FromMM(drill))
        via.SetWidth(pcbnew.FromMM(size))
        via.SetNet(net)
        board.Add(via)

    # 6. Re-route bottom circuitry
    # 6.1 VIN: J1 pad 2 (135.389, 99.369) -> C3 pad 1 (143.100, 102.338) -> U2 pad 1 & 3 (144.501, 102.250 & 104.150)
    add_poly_track(net_vin, [
        (135.389, 99.369),
        (138.000, 99.369),
        (138.000, 101.500),
        (142.000, 101.500),
        (143.100, 102.338),
    ], width=0.30)
    # C3 pad 1 to U2 pad 1
    add_poly_track(net_vin, [
        (143.100, 102.338),
        (144.501, 102.250),
    ], width=0.30)
    # U2 pad 1 to pad 3 (bridge EN to VIN)
    add_poly_track(net_vin, [
        (144.501, 102.250),
        (144.000, 102.750),
        (144.000, 103.650),
        (144.501, 104.150),
    ], width=0.25)

    # 6.2 VDD: U2 pad 5 (146.777, 102.250) -> C4 pad 1 (148.178, 102.338)
    add_track(net_vdd, 146.777, 102.250, 148.178, 102.338, width=0.30)
    # VDD from C4 to R3 pad 1 (146.552, 98.700) and R4 pad 1 (147.265, 98.700)
    add_poly_track(net_vdd, [
        (148.178, 102.338),
        (148.178, 100.500),
        (147.265, 99.587),
        (147.265, 98.700),
    ], width=0.25)
    add_track(net_vdd, 147.265, 98.700, 146.552, 98.700, width=0.25)
    # VDD to JP1 pad 3 (153.889, 91.584)
    add_poly_track(net_vdd, [
        (148.178, 102.338),
        (152.000, 102.338),
        (153.000, 101.338),
        (153.000, 93.000),
        (153.889, 92.111),
        (153.889, 91.584),
    ], layer=pcbnew.B_Cu, width=0.30)
    # Via from C4 VDD to B_Cu
    add_via(net_vdd, 148.178, 102.338)

    # 6.3 LED_P: U1 pad 9 (143.031, 95.826) to R3 pad 2 (144.726, 98.700)
    add_poly_track(net_led_p, [
        (143.031, 95.826),
        (143.031, 97.005),
        (144.726, 98.700),
    ], width=0.25)

    # 6.4 Net-(U2-NC): U2 pad 4 (146.777, 104.150) -> C5 pad 1 (149.040, 100.700) & R4 pad 2 (149.091, 98.700)
    add_poly_track(net_u2_nc, [
        (146.777, 104.150),
        (147.500, 104.150),
        (149.500, 102.150),
        (149.500, 100.700),
        (149.040, 100.700),
    ], width=0.20)
    add_track(net_u2_nc, 149.040, 100.700, 149.091, 98.700, width=0.20)

    # 6.5 GND connections for bottom circuit
    # U2 pad 2 (144.501, 103.200) -> Via to GND
    add_via(net_gnd, 144.501, 103.200)
    # C3 pad 2 (143.100, 104.062) -> Via to GND
    add_via(net_gnd, 143.100, 104.062)
    # C4 pad 2 (148.178, 104.062) -> Via to GND
    add_via(net_gnd, 148.178, 104.062)
    # C5 pad 2 (147.316, 100.700) -> Via to GND
    add_via(net_gnd, 147.316, 100.700)

    # 7. Re-route top circuitry around H1, H2
    # TP1 (GND at 145.639, 81.200) -> Via to GND
    add_via(net_gnd, 145.639, 81.200)
    # TP2 (VDD at 147.639, 81.200) -> route to VDD at (154.139, 85.284)
    add_poly_track(net_vdd, [
        (147.639, 81.200),
        (147.639, 80.200),
        (153.500, 80.200),
        (154.500, 81.200),
        (154.500, 84.000),
        (154.139, 84.361),
    ], layer=pcbnew.F_Cu, width=0.25)

    # TP3 (VIO at 143.639, 81.200) -> route to JP1 pad 2 / VIO net
    add_poly_track(net_vio, [
        (143.639, 81.200),
        (143.639, 80.000),
        (138.000, 80.000),
        (138.000, 84.000),
    ], layer=pcbnew.B_Cu, width=0.25)
    add_via(net_vio, 143.639, 81.200)

    # 8. Update GND Zone Outline to match new compact board
    for z in board.Zones():
        if z.GetNetname() == "GND":
            outline = z.Outline()
            outline.RemoveAllContours()
            # Inset polygon by 0.3mm from Edge.Cuts
            zi = 0.30
            pts = [
                (xL + rC, yT + zi),
                (xR - rC, yT + zi),
                (xR - zi, yT + rC),
                (xR - zi, yB - rC),
                (xR - rC, yB - zi),
                (xL + rC, yB - zi),
                (xL + zi, yB - rC),
                (xL + zi, yT + rC),
            ]
            outline.NewOutline()
            for px, py in pts:
                outline.Append(pcbnew.FromMM(px), pcbnew.FromMM(py))

    # Refill zones
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())

    # Save board
    board.Save(PCB_PATH)
    print("Plan B applied and board saved successfully!")

if __name__ == "__main__":
    apply_plan_b()
