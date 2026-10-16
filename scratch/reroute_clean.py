import pcbnew
import math

SRC_PCB = r"scratch/pmw3360_head.kicad_pcb"
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

    # 1. Update Edge.Cuts to Plan B (21.75 x 26.50 mm, r = 2.50 mm)
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

    # 2. Update Mounting Holes: M2 2.2mm at (X = +-4.50, Y = +-10.00 mm from (145.639, 92.5258))
    m2_coords = {
        "H1": (141.139, 82.5258),
        "H2": (150.139, 82.5258),
        "H3": (141.139, 102.5258),
        "H4": (150.139, 102.5258),
    }
    m2_lib = r"C:\Users\oktnt\AppData\Local\Programs\KiCad\10.0\share\kicad\footprints\MountingHole.pretty"
    for ref, (hx, hy) in m2_coords.items():
        fp = board.FindFootprintByReference(ref)
        if fp:
            board.Delete(fp)
        new_fp = pcbnew.FootprintLoad(m2_lib, "MountingHole_2.2mm_M2")
        new_fp.SetReference(ref)
        new_fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(hx), pcbnew.FromMM(hy)))
        board.Add(new_fp)

    # 3. Update U1 central aperture to 8.70 x 16.90 mm (centered at (145.639, 92.5258))
    u1 = board.FindFootprintByReference("U1")
    for d in u1.GraphicalItems():
        if d.GetLayerName() == "Edge.Cuts":
            d.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(141.289), pcbnew.FromMM(84.0758)))
            d.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(149.989), pcbnew.FromMM(100.9758)))

    # Adjust U1 keepout zone
    for z in u1.Zones():
        z.SetDoNotAllowFootprints(False)
        poly = z.Outline()
        poly.RemoveAllContours()
        poly.NewOutline()
        for kx, ky in [
            (141.50, 84.10),
            (149.78, 84.10),
            (149.78, 100.95),
            (141.50, 100.95),
        ]:
            poly.Append(pcbnew.FromMM(kx), pcbnew.FromMM(ky))

    # Helper functions
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

    # 4. Remove ONLY conflicting tracks in HEAD:
    # 4.1 /MISO: track from (139.32, 82.98) to (152.67, 82.98) and its ends
    for t in list(board.GetTracks()):
        if t.GetNetname() == "/MISO":
            y1 = pcbnew.ToMM(t.GetStart().y)
            y2 = pcbnew.ToMM(t.GetEnd().y)
            if min(y1, y2) < 84.0:
                board.Delete(t)

    # 4.2 /RESET: track from (151.48, 83.53) to (140.29, 83.53) and its ends
    for t in list(board.GetTracks()):
        if t.GetNetname() == "/RESET":
            y1 = pcbnew.ToMM(t.GetStart().y)
            y2 = pcbnew.ToMM(t.GetEnd().y)
            if min(y1, y2) < 84.5 and max(y1, y2) < 86.0:
                board.Delete(t)

    # 4.3 All bottom tracks (y > 103.0) and bottom components
    for t in list(board.GetTracks()):
        y1 = pcbnew.ToMM(t.GetStart().y)
        y2 = pcbnew.ToMM(t.GetEnd().y)
        if max(y1, y2) > 102.5:
            board.Delete(t)

    # 5. Position bottom components compactly:
    # U2: SOT-23-5 at (145.639, 104.000)
    # C3: (137.500, 103.500)
    # C4: (148.500, 103.500) rot -90
    # R3: (144.500, 101.800) rot 180
    # R4: (153.500, 102.500)
    # C5: (153.500, 104.200) rot 180
    comp_locs = {
        "C3": ((137.500, 103.500), 0.0),
        "U2": ((145.639, 104.000), 0.0),
        "C4": ((148.500, 103.500), -90.0),
        "R3": ((144.500, 101.800), 180.0),
        "R4": ((153.500, 102.500), 0.0),
        "C5": ((153.500, 104.200), 180.0),
    }
    for ref, ((cx, cy), rot) in comp_locs.items():
        fp = board.FindFootprintByReference(ref)
        if fp:
            fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(cx), pcbnew.FromMM(cy)))
            fp.SetOrientationDegrees(rot)

    # 6. Re-route /RESET at top:
    # From J1 pin 8 (135.389, 84.129) -> R1 pad 2 (153.226, 85.284)
    # Route on F.Cu above H1/H2 at Y = 79.800
    add_poly_track(net_reset, [
        (135.389, 84.129),
        (136.500, 84.129),
        (137.500, 83.129),
        (137.500, 79.800),
        (151.000, 79.800),
        (152.000, 80.800),
        (152.000, 84.058),
        (153.226, 85.284),
    ], layer=pcbnew.F_Cu, width=0.20)

    # 7. Re-route /MISO at top:
    # From (138.639, 89.7838) on B.Cu -> R2 pad 2 (153.226, 83.534) on F.Cu
    # Route on B.Cu above H1/H2 at Y = 80.200
    add_poly_track(net_miso, [
        (138.639, 89.7838),
        (138.639, 80.200),
        (151.000, 80.200),
        (152.500, 81.700),
        (152.500, 82.808),
        (153.226, 83.534),
    ], layer=pcbnew.B_Cu, width=0.20)
    add_via(net_miso, 153.226, 83.534)

    # 8. Re-route Bottom components:
    # 8.1 Net-(U1-LED_P): from (138.89, 97.42) on F.Cu to R3 pad 2 (143.588, 101.800)
    add_poly_track(net_led_p, [
        (138.890, 97.420),
        (138.890, 101.800),
        (143.588, 101.800),
    ], layer=pcbnew.F_Cu, width=0.25)

    # 8.2 VIN: J1 pin 2 (135.389, 99.369) -> C3 pad 1 (136.637, 103.500) -> U2 pin 1,3
    add_poly_track(net_vin, [
        (135.389, 99.369),
        (136.637, 100.617),
        (136.637, 103.500),
    ], layer=pcbnew.F_Cu, width=0.30)
    add_via(net_vin, 136.637, 104.700)
    add_track(net_vin, 136.637, 103.500, 136.637, 104.700, layer=pcbnew.F_Cu, width=0.30)
    add_poly_track(net_vin, [
        (136.637, 104.700),
        (136.637, 105.200),
        (143.500, 105.200),
        (143.500, 104.950),
    ], layer=pcbnew.B_Cu, width=0.30)
    add_via(net_vin, 143.500, 104.950)
    add_track(net_vin, 143.500, 104.950, 144.502, 104.950, layer=pcbnew.F_Cu, width=0.30)
    add_poly_track(net_vin, [
        (144.502, 104.950),
        (143.800, 104.950),
        (143.800, 103.050),
        (144.502, 103.050),
    ], layer=pcbnew.F_Cu, width=0.25)
    # Connect VIN from U2 to JP1 pin 1 on B.Cu
    add_poly_track(net_vin, [
        (143.500, 105.200),
        (155.000, 105.200),
        (155.000, 99.530),
        (156.640, 99.530),
        (156.640, 90.580),
        (155.040, 88.980),
        (153.889, 88.984),
    ], layer=pcbnew.F_Cu, width=0.25)

    # 8.3 VDD on bottom:
    # U2 pin 5: (146.776, 103.050)
    # R3 pad 1: (145.412, 101.800)
    # C4 pad 1: (148.500, 102.637)
    # R4 pad 1: (152.588, 102.500)
    add_poly_track(net_vdd, [
        (146.776, 103.050),
        (146.776, 101.800),
        (145.412, 101.800),
    ], layer=pcbnew.F_Cu, width=0.30)
    add_poly_track(net_vdd, [
        (146.776, 103.050),
        (148.500, 103.050),
        (148.500, 102.637),
    ], layer=pcbnew.F_Cu, width=0.30)
    add_via(net_vdd, 148.500, 101.800)
    add_track(net_vdd, 148.500, 102.637, 148.500, 101.800, layer=pcbnew.F_Cu, width=0.25)
    add_poly_track(net_vdd, [
        (148.500, 101.800),
        (148.500, 104.700),
        (152.588, 104.700),
        (152.588, 102.500),
    ], layer=pcbnew.B_Cu, width=0.25)
    add_via(net_vdd, 152.588, 102.500)
    # Connect VDD to right side VDD bus at (156.14, 98.53)
    add_poly_track(net_vdd, [
        (152.588, 102.500),
        (154.500, 102.500),
        (154.500, 98.530),
        (156.140, 98.530),
    ], layer=pcbnew.B_Cu, width=0.25)

    # 8.4 Net-(U2-NC):
    add_via(net_u2_nc, 146.776, 104.950)
    add_poly_track(net_u2_nc, [
        (146.776, 104.950),
        (147.500, 105.400),
        (154.000, 105.400),
        (154.363, 105.037),
        (154.363, 104.200),
    ], layer=pcbnew.B_Cu, width=0.20)
    add_via(net_u2_nc, 154.363, 104.200)
    add_track(net_u2_nc, 154.363, 104.200, 154.412, 102.500, layer=pcbnew.F_Cu, width=0.20)

    # 8.5 GND connections on bottom:
    # C3 pad 2: (138.363, 103.500)
    add_via(net_gnd, 138.363, 104.500)
    add_track(net_gnd, 138.363, 103.500, 138.363, 104.500, layer=pcbnew.F_Cu, width=0.30)
    # Connect C3 GND to J1 GND track at (139.64, 104.78)
    add_track(net_gnd, 138.363, 104.500, 139.640, 104.780, layer=pcbnew.F_Cu, width=0.30)
    # U2 pin 2: (144.502, 104.000)
    add_via(net_gnd, 143.500, 104.000)
    add_track(net_gnd, 144.502, 104.000, 143.500, 104.000, layer=pcbnew.F_Cu, width=0.30)
    # C4 pad 2: (148.500, 104.363)
    add_via(net_gnd, 148.500, 104.500)
    # C5 pad 2: (152.637, 104.200)
    add_via(net_gnd, 152.637, 104.200)

    # 9. Update GND Zone Outline to match compact board
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
    print("Surgical reroute completed successfully.")

if __name__ == "__main__":
    run()
