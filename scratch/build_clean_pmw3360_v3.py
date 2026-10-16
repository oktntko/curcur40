import pcbnew
import math
import subprocess
import json

SRC_PCB = r"scratch/pmw3360_clean_base.kicad_pcb"
OUT_PCB = r"pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pcb"
KICAD_CLI = r"C:\Users\oktnt\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe"

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

    # 1. Update Edge.Cuts (21.75 x 26.50 mm, r = 2.50 mm)
    # Center: X0 = 145.264, Y0 = 92.5258
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

    # 2. Update Mounting Holes to (X = +-4.50, Y = +-10.00 mm from optical center (145.639, 92.5258))
    m2_lib = r"C:\Users\oktnt\AppData\Local\Programs\KiCad\10.0\share\kicad\footprints\MountingHole.pretty"
    m2_coords = {
        "H1": (141.139, 82.5258),
        "H2": (150.139, 82.5258),
        "H3": (141.139, 102.5258),
        "H4": (150.139, 102.5258),
    }
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
            # Start: (141.289, 84.0758), End: (149.989, 100.9758)
            d.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(141.289), pcbnew.FromMM(84.0758)))
            d.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(149.989), pcbnew.FromMM(100.9758)))

    # 4. Update U1 keepout zone so it doesn't touch mounting holes or tracks outside aperture
    for z in u1.Zones():
        poly = z.Outline()
        poly.RemoveAllContours()
        poly.NewOutline()
        for kx, ky in [
            (141.80, 84.30),
            (149.48, 84.30),
            (149.48, 100.75),
            (141.80, 100.75),
        ]:
            poly.Append(pcbnew.FromMM(kx), pcbnew.FromMM(ky))

    # 5. Position bottom components cleanly inside y <= 104.5 mm
    comp_locs = {
        "C3": ((137.500, 103.600), 0.0),     # Pad 1 (VIN) at 136.637, Pad 2 (GND) at 138.363
        "U2": ((144.500, 103.600), 0.0),     # Pin 1,3 at 143.363, Pin 2 at 143.363, Pin 4,5 at 145.637
        "C4": ((147.200, 103.600), -90.0),   # Pad 1 (VDD) at 102.737, Pad 2 (GND) at 104.463
        "R3": ((144.500, 101.600), 180.0),   # Pad 1 (VDD) at 145.412, Pad 2 (LED_P) at 143.588
        "R4": ((153.500, 102.600), 0.0),     # Pad 1 (VDD) at 152.588, Pad 2 (U2-NC) at 154.412
        "C5": ((153.500, 104.400), 180.0),   # Pad 1 (U2-NC) at 154.363, Pad 2 (GND) at 152.637
    }
    for ref, ((cx, cy), rot) in comp_locs.items():
        fp = board.FindFootprintByReference(ref)
        if fp:
            fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(cx), pcbnew.FromMM(cy)))
            fp.SetOrientationDegrees(rot)

    # 6. Position top test points TP1, TP2, TP3
    tp_locs = {
        "TP3": (143.639, 80.500), # GND
        "TP1": (145.639, 80.500), # VIO
        "TP2": (147.639, 80.500), # VDD
    }
    for ref, (tx, ty) in tp_locs.items():
        fp = board.FindFootprintByReference(ref)
        if fp:
            fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(tx), pcbnew.FromMM(ty)))

    # 7. Delete all existing tracks and vias in top (y < 85.0) and bottom (y > 97.0) areas
    for t in list(board.GetTracks()):
        if t.GetClass() != "PCB_VIA":
            y1 = pcbnew.ToMM(t.GetStart().y)
            y2 = pcbnew.ToMM(t.GetEnd().y)
            if max(y1, y2) > 97.0 or min(y1, y2) < 85.0:
                board.Delete(t)
        else:
            vy = pcbnew.ToMM(t.GetPosition().y)
            if vy > 97.0 or vy < 85.0:
                board.Delete(t)

    # Helper functions for routing
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

    # 8. Bottom Routing:
    # 8.1 Net-(U1-LED_P): U1 pad 15 (140.289, 96.024) to R3 pad 2 (143.588, 101.600)
    # Avoid U1 pin 16 at (140.289, 97.804) by stepping left to X=138.80
    add_poly_track(net_led_p, [
        (140.289, 96.024),
        (138.800, 96.024),
        (138.800, 100.000),
        (140.400, 101.600),
        (143.588, 101.600),
    ], layer=pcbnew.F_Cu, width=0.25)

    # 8.2 VIN: J1 pin 2 (135.389, 99.369) to C3 pad 1 (136.637, 103.600) to U2 pin 1,3 (143.363, 102.650 / 104.550)
    add_poly_track(net_vin, [
        (135.389, 99.369),
        (136.637, 100.617),
        (136.637, 103.600),
    ], layer=pcbnew.F_Cu, width=0.30)
    add_via(net_vin, 136.637, 104.600)
    add_track(net_vin, 136.637, 103.600, 136.637, 104.600, layer=pcbnew.F_Cu, width=0.30)
    add_poly_track(net_vin, [
        (136.637, 104.600),
        (136.637, 105.100),
        (142.200, 105.100),
        (142.200, 104.550),
    ], layer=pcbnew.B_Cu, width=0.30)
    add_via(net_vin, 142.200, 104.550)
    add_track(net_vin, 142.200, 104.550, 143.363, 104.550, layer=pcbnew.F_Cu, width=0.30)
    # Connect U2 pin 1 and 3 on F.Cu
    add_poly_track(net_vin, [
        (143.363, 104.550),
        (142.600, 104.550),
        (142.600, 102.650),
        (143.363, 102.650),
    ], layer=pcbnew.F_Cu, width=0.25)

    # 8.3 VDD on bottom:
    # U2 pad 5: (145.637, 102.650)
    # C4 pad 1: (147.200, 102.737)
    # R3 pad 1: (145.412, 101.600)
    # R4 pad 1: (152.588, 102.600)
    add_poly_track(net_vdd, [
        (145.637, 102.650),
        (147.200, 102.650),
        (147.200, 102.737),
    ], layer=pcbnew.F_Cu, width=0.30)
    add_poly_track(net_vdd, [
        (145.637, 102.650),
        (145.637, 101.600),
        (145.412, 101.600),
    ], layer=pcbnew.F_Cu, width=0.25)
    # Bridge VDD to right side R4 pad 1 via B.Cu
    add_via(net_vdd, 147.200, 101.600)
    add_track(net_vdd, 147.200, 102.650, 147.200, 101.600, layer=pcbnew.F_Cu, width=0.25)
    add_poly_track(net_vdd, [
        (147.200, 101.600),
        (147.200, 101.000),
        (151.500, 101.000),
        (152.588, 102.088),
        (152.588, 102.600),
    ], layer=pcbnew.B_Cu, width=0.25)
    add_via(net_vdd, 152.588, 102.600)
    # Continue VDD up B.Cu along right edge (X=154.80) to U1 pin 4 (150.989, 93.354)
    add_poly_track(net_vdd, [
        (152.588, 102.600),
        (154.800, 102.600),
        (154.800, 93.354),
        (150.989, 93.354),
    ], layer=pcbnew.B_Cu, width=0.25)

    # 8.4 Net-(U2-NC):
    # U2 pad 4: (145.637, 104.550)
    # C5 pad 1: (154.363, 104.400) (since rotated 180)
    # R4 pad 2: (154.412, 102.600)
    add_via(net_u2_nc, 145.637, 104.550)
    add_poly_track(net_u2_nc, [
        (145.637, 104.550),
        (146.500, 105.400),
        (153.500, 105.400),
        (154.363, 104.537),
        (154.363, 104.400),
    ], layer=pcbnew.B_Cu, width=0.20)
    add_track(net_u2_nc, 154.363, 104.400, 154.412, 102.600, layer=pcbnew.F_Cu, width=0.20)

    # 8.5 GND connections on bottom:
    add_track(net_gnd, 138.363, 103.600, 138.363, 104.400, layer=pcbnew.F_Cu, width=0.30)
    add_via(net_gnd, 138.363, 104.400)
    add_track(net_gnd, 143.363, 103.600, 142.400, 103.600, layer=pcbnew.F_Cu, width=0.30)
    add_via(net_gnd, 142.400, 103.600)
    add_via(net_gnd, 147.200, 104.463)
    add_via(net_gnd, 152.637, 104.400)

    # 9. Top Routing:
    # 9.1 TP3 (GND at 143.639, 80.500)
    add_via(net_gnd, 143.639, 80.500)

    # 9.2 TP1 (VIO at 145.639, 80.500) -> R2 pad 1 (155.052, 83.534), R1 pad 1 (155.052, 85.284)
    # Route on F.Cu at Y = 80.500 above H2 (H2 is at 150.139, 82.526)
    add_poly_track(net_vio, [
        (145.639, 80.500),
        (154.200, 80.500),
        (155.052, 81.352),
        (155.052, 83.534),
        (155.052, 85.284),
    ], layer=pcbnew.F_Cu, width=0.25)
    # Also connect VIO from TP1 to JP1 pin 2 (153.889, 90.284) on B.Cu
    add_via(net_vio, 145.639, 80.500)
    add_poly_track(net_vio, [
        (145.639, 80.500),
        (138.000, 80.500),
        (138.000, 87.000),
        (137.000, 88.000),
        (137.000, 90.284),
        (138.000, 90.284),
    ], layer=pcbnew.B_Cu, width=0.25)

    # 9.3 TP2 (VDD at 147.639, 80.500) -> connect to VDD bus at (154.139, 85.284)
    # Route on B.Cu at Y = 79.900
    add_via(net_vdd, 147.639, 80.500)
    add_poly_track(net_vdd, [
        (147.639, 80.500),
        (147.639, 79.900),
        (153.500, 79.900),
        (154.500, 80.900),
        (154.500, 84.500),
        (154.139, 84.861),
        (154.139, 85.284),
    ], layer=pcbnew.B_Cu, width=0.25)

    # 9.4 /RESET: J1 pin 8 (135.389, 84.129) to R1 pad 2 (153.226, 85.284)
    # Route on F.Cu: goes around H1 and H2 above them at Y = 81.000!
    add_poly_track(net_reset, [
        (135.389, 84.129),
        (137.000, 84.129),
        (139.000, 82.129),
        (139.000, 81.000),
        (144.500, 81.000),
        (144.500, 81.100),
        (152.000, 81.100),
        (153.226, 82.326),
        (153.226, 85.284),
    ], layer=pcbnew.F_Cu, width=0.20)

    # 9.5 /MISO: J1 pin 4 (135.389, 94.289) to R2 pad 2 (153.226, 83.534)
    # In HEAD, /MISO came up to (138.639, 89.7838) on B.Cu.
    # Route on B.Cu above H1/H2 at Y = 80.500!
    add_poly_track(net_miso, [
        (138.639, 89.7838),
        (138.639, 81.200),
        (139.500, 80.500),
        (143.000, 80.500),
        (144.000, 81.500),
        (150.000, 81.500),
        (152.000, 82.308),
        (153.226, 83.534),
    ], layer=pcbnew.B_Cu, width=0.20)

    # 10. Update GND Zone Outline to match compact board
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
    print("V3 clean PCB saved successfully.")

if __name__ == "__main__":
    run()
