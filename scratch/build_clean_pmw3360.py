import pcbnew
import math

SRC_PCB = r"scratch/pmw3360_clean_base.kicad_pcb"
OUT_PCB = r"pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pcb"

def run():
    board = pcbnew.LoadBoard(SRC_PCB)
    netinfo = board.GetNetInfo()

    net_gnd = netinfo.GetNetItem("GND")
    net_vin = netinfo.GetNetItem("V_{IN}")
    net_vdd = netinfo.GetNetItem("VDD")
    net_vio = netinfo.GetNetItem("V_{IO}")
    net_led_p = netinfo.GetNetItem("Net-(U1-LED_P)")
    net_u2_nc = netinfo.GetNetItem("Net-(U2-NC)")
    net_reset = netinfo.GetNetItem("/RESET")
    net_miso = netinfo.GetNetItem("/MISO")

    # 1. Update Edge.Cuts (21.75 x 26.50 mm, r=2.50 mm)
    xL, xR = 134.389, 156.139
    yT, yB = 79.2758, 105.7758
    rC = 2.5000
    s2 = rC * (1.0 - 0.70710678)

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

    add_edge_line(xL + rC, yT, xR - rC, yT)
    add_edge_arc(xR - rC, yT, xR - s2, yT + s2, xR, yT + rC)
    add_edge_line(xR, yT + rC, xR, yB - rC)
    add_edge_arc(xR, yB - rC, xR - s2, yB - s2, xR - rC, yB)
    add_edge_line(xR - rC, yB, xL + rC, yB)
    add_edge_arc(xL + rC, yB, xL + s2, yB - s2, xL, yB - rC)
    add_edge_line(xL, yB - rC, xL, yT + rC)
    add_edge_arc(xL, yT + rC, xL + s2, yT + s2, xL + rC, yT)

    # 2. Mounting holes (M2 2.2mm)
    m2_lib = r"C:\Users\oktnt\AppData\Local\Programs\KiCad\10.0\share\kicad\footprints\MountingHole.pretty"
    m2_coords = {
        "H1": (141.139, 82.9258),
        "H2": (150.139, 82.9258),
        "H3": (141.139, 102.1258),
        "H4": (150.139, 102.1258),
    }
    for ref, (hx, hy) in m2_coords.items():
        fp = board.FindFootprintByReference(ref)
        if fp:
            board.Delete(fp)
        new_fp = pcbnew.FootprintLoad(m2_lib, "MountingHole_2.2mm_M2")
        new_fp.SetReference(ref)
        new_fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(hx), pcbnew.FromMM(hy)))
        board.Add(new_fp)

    # 3. Shrink U1 internal keepout zone so it doesn't overlap holes
    u1 = board.FindFootprintByReference("U1")
    for z in u1.Zones():
        poly = z.Outline()
        poly.RemoveAllContours()
        poly.NewOutline()
        for kx, ky in [
            (141.80, 85.00),
            (149.48, 85.00),
            (149.48, 100.00),
            (141.80, 100.00),
        ]:
            poly.Append(pcbnew.FromMM(kx), pcbnew.FromMM(ky))

    # 4. Relocate Test Points TP1, TP2, TP3
    tp_locs = {
        "TP3": (143.639, 81.200),
        "TP1": (145.639, 81.200),
        "TP2": (147.639, 81.200),
    }
    for ref, (tx, ty) in tp_locs.items():
        fp = board.FindFootprintByReference(ref)
        if fp:
            fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(tx), pcbnew.FromMM(ty)))

    # 5. Relocate bottom circuit components
    comp_locs = {
        "C3": ((137.500, 103.600), 0.0),
        "U2": ((144.500, 103.600), 0.0),
        "C4": ((147.200, 103.600), -90.0),
        "R3": ((144.500, 101.600), 180.0),
        "R4": ((153.500, 102.600), 0.0),
        "C5": ((153.500, 104.400), 0.0),
    }
    for ref, ((cx, cy), rot) in comp_locs.items():
        fp = board.FindFootprintByReference(ref)
        if fp:
            fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(cx), pcbnew.FromMM(cy)))
            fp.SetOrientationDegrees(rot)

    # 6. Delete old tracks in bottom (y > 97.0) and top (y < 84.0) areas
    for t in list(board.GetTracks()):
        if t.GetClass() != "PCB_VIA":
            y1 = pcbnew.ToMM(t.GetStart().y)
            y2 = pcbnew.ToMM(t.GetEnd().y)
            if max(y1, y2) > 97.0 or min(y1, y2) < 84.0:
                board.Delete(t)
        else:
            vy = pcbnew.ToMM(t.GetPosition().y)
            if vy > 97.0 or vy < 84.0:
                board.Delete(t)

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

    # 7. Wiring:
    # 7.1 VIN: J1 pin 2 (135.389, 99.369) -> C3 pad 1 (136.637, 103.600) -> U2 pad 1 & 3
    add_poly_track(net_vin, [
        (135.389, 99.369),
        (136.637, 100.617),
        (136.637, 103.600),
    ], width=0.30)
    add_track(net_vin, 136.637, 103.600, 136.637, 104.500, width=0.30)
    add_via(net_vin, 136.637, 104.500)
    add_poly_track(net_vin, [
        (136.637, 104.500),
        (136.637, 105.100),
        (142.000, 105.100),
        (142.500, 104.550),
    ], layer=pcbnew.B_Cu, width=0.30)
    add_via(net_vin, 142.500, 104.550)
    add_track(net_vin, 142.500, 104.550, 143.363, 104.550, width=0.25)
    add_poly_track(net_vin, [
        (143.363, 104.550),
        (142.600, 103.787),
        (142.600, 103.413),
        (143.363, 102.650),
    ], width=0.25)

    # 7.2 VDD:
    # U2 pad 5: (145.637, 102.650)
    # C4 pad 1: (147.200, 102.737)
    # R3 pad 1: (145.412, 101.600)
    # R4 pad 1: (152.588, 102.600)
    add_track(net_vdd, 145.637, 102.650, 147.200, 102.650, width=0.30)
    add_track(net_vdd, 147.200, 102.650, 147.200, 102.737, width=0.30)
    add_poly_track(net_vdd, [
        (145.637, 102.650),
        (145.637, 101.825),
        (145.412, 101.600),
    ], width=0.25)
    add_via(net_vdd, 147.200, 101.700)
    add_poly_track(net_vdd, [
        (147.200, 101.700),
        (147.200, 101.000),
        (151.500, 101.000),
        (152.588, 102.088),
        (152.588, 102.600),
    ], layer=pcbnew.B_Cu, width=0.25)
    add_via(net_vdd, 152.588, 102.600)
    add_poly_track(net_vdd, [
        (152.588, 102.088),
        (154.500, 102.088),
        (154.500, 93.000),
        (153.889, 92.389),
        (153.889, 91.584),
    ], layer=pcbnew.B_Cu, width=0.30)
    # Connect VDD to U1 pin 4 (150.989, 93.354)
    add_poly_track(net_vdd, [
        (153.889, 92.389),
        (152.000, 92.389),
        (150.989, 93.354),
    ], layer=pcbnew.B_Cu, width=0.25)

    # 7.3 Net-(U1-LED_P):
    # U1 pad 15: (140.289, 96.024)
    # R3 pad 2: (143.588, 101.600)
    add_poly_track(net_led_p, [
        (140.289, 96.024),
        (140.289, 98.301),
        (143.588, 101.600),
    ], width=0.25)

    # 7.4 Net-(U2-NC):
    # U2 pad 4: (145.637, 104.550)
    # C5 pad 1: (152.637, 104.400)
    # R4 pad 2: (154.412, 102.600)
    add_via(net_u2_nc, 145.637, 104.550)
    add_poly_track(net_u2_nc, [
        (145.637, 104.550),
        (146.500, 105.413),
        (151.500, 105.413),
        (152.637, 104.400),
    ], layer=pcbnew.B_Cu, width=0.20)
    add_via(net_u2_nc, 152.637, 104.400)
    add_poly_track(net_u2_nc, [
        (152.637, 104.400),
        (154.412, 104.400),
        (154.412, 102.600),
    ], width=0.20)

    # 7.5 GND connections:
    add_track(net_gnd, 138.363, 103.600, 138.363, 104.400)
    add_via(net_gnd, 138.363, 104.400)
    add_track(net_gnd, 143.363, 103.600, 142.400, 103.600)
    add_via(net_gnd, 142.400, 103.600)
    add_via(net_gnd, 147.200, 104.463)
    add_track(net_gnd, 154.363, 104.400, 154.363, 105.100)
    add_via(net_gnd, 154.363, 105.100)
    # U1 pad 8 GND: (150.989, 86.234)
    add_via(net_gnd, 152.000, 86.234)
    add_track(net_gnd, 150.989, 86.234, 152.000, 86.234)

    # 7.6 Top area:
    # TP3 (GND at 143.639, 81.200)
    add_via(net_gnd, 143.639, 81.200)
    # TP1 (VIO at 145.639, 81.200)
    add_via(net_vio, 145.639, 81.200)
    add_poly_track(net_vio, [
        (145.639, 81.200),
        (145.639, 80.200),
        (138.000, 80.200),
        (138.000, 87.000),
        (137.000, 88.000),
        (137.000, 90.284),
        (138.000, 90.284),
    ], layer=pcbnew.B_Cu, width=0.25)
    # Connect VIO to R2 pad 1 (155.052, 83.534) and R1 pad 1 (155.052, 85.284)
    add_poly_track(net_vio, [
        (145.639, 81.200),
        (145.639, 80.800),
        (154.000, 80.800),
        (155.052, 81.852),
        (155.052, 83.534),
        (155.052, 85.284),
    ], width=0.25)

    # TP2 (VDD at 147.639, 81.200) -> connect to VDD bus at (154.139, 85.284)
    add_poly_track(net_vdd, [
        (147.639, 81.200),
        (147.639, 80.200),
        (153.500, 80.200),
        (154.500, 81.200),
        (154.500, 84.500),
        (154.139, 84.861),
        (154.139, 85.284),
    ], width=0.25)

    # /RESET track from J1 pin 8 (135.389, 84.129) to R1 pad 2 (153.226, 85.284)
    add_poly_track(net_reset, [
        (135.389, 84.129),
        (137.500, 84.129),
        (139.000, 85.629),
        (143.000, 85.629),
        (145.000, 83.629),
        (147.000, 83.629),
        (148.500, 85.129),
        (152.000, 85.129),
        (152.155, 85.284),
        (153.226, 85.284),
    ], width=0.20)

    # /MISO track from J1 pin 4 to R2 pad 2 (153.226, 83.534)
    add_poly_track(net_miso, [
        (138.639, 89.7838),
        (138.639, 84.000),
        (140.000, 82.639),
        (151.000, 82.639),
        (152.000, 83.534),
        (153.226, 83.534),
    ], layer=pcbnew.B_Cu, width=0.20)

    # 8. Update GND Zone Outline to match new compact board
    for z in board.Zones():
        if z.GetNetname() == "GND":
            outline = z.Outline()
            outline.RemoveAllContours()
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

    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())

    board.Save(OUT_PCB)
    print("Clean PCB built and saved successfully.")

if __name__ == "__main__":
    run()
