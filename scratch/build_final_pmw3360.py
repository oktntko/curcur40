import pcbnew
import math
import subprocess
import json

SRC_PCB = r"scratch/pmw3360_head.kicad_pcb"
OUT_PCB = r"pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pcb"
KICAD_CLI = r"C:\Users\oktnt\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe"

def build():
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

    # Adjust U1 keepout zone: allow footprints, keep tight boundary around aperture
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

    # 4. Position bottom components
    comp_locs = {
        "C3": ((137.500, 103.500), 0.0),
        "U2": ((144.500, 103.800), 0.0),
        "C4": ((147.200, 103.800), -90.0),
        "R3": ((144.500, 101.800), 180.0),
        "R4": ((153.500, 102.500), 0.0),
        "C5": ((153.500, 104.200), 180.0),
    }
    for ref, ((cx, cy), rot) in comp_locs.items():
        fp = board.FindFootprintByReference(ref)
        if fp:
            fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(cx), pcbnew.FromMM(cy)))
            fp.SetOrientationDegrees(rot)

    # 5. Position top test points:
    tp_locs = {
        "TP3": (143.639, 80.800), # GND
        "TP1": (146.000, 80.800), # VIO
        "TP2": (148.500, 80.800), # VDD
    }
    for ref, (tx, ty) in tp_locs.items():
        fp = board.FindFootprintByReference(ref)
        if fp:
            fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(tx), pcbnew.FromMM(ty)))

    # 6. Delete tracks & vias in top (y < 85.0) and bottom (y > 97.0)
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

    # Routing helpers
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

    # 7. Route Bottom Area:
    # 7.1 Net-(U1-LED_P): U1 pin 15 (140.289, 96.024) to R3 pad 2 (143.588, 101.800)
    # Avoid U1 pin 16 at (140.289, 97.804) by stepping left to X=138.80
    add_via(net_led_p, 138.800, 96.024)
    add_track(net_led_p, 140.289, 96.024, 138.800, 96.024, layer=pcbnew.F_Cu, width=0.25)
    # On B.Cu, route below Y=101.00 so it doesn't touch U1 keepout
    add_poly_track(net_led_p, [
        (138.800, 96.024),
        (138.800, 101.200),
        (143.588, 101.200),
        (143.588, 101.800),
    ], layer=pcbnew.B_Cu, width=0.25)
    add_via(net_led_p, 143.588, 101.800)

    # 7.2 VIN: J1 pin 2 (135.389, 99.369) -> C3 pad 1 (136.637, 103.500) -> U2 pin 1,3
    # U2 is at (144.500, 103.800). Pin 1: (143.363, 102.850), Pin 3: (143.363, 104.750)
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
        (142.500, 105.200),
        (142.500, 104.750),
    ], layer=pcbnew.B_Cu, width=0.30)
    add_via(net_vin, 142.500, 104.750)
    add_track(net_vin, 142.500, 104.750, 143.363, 104.750, layer=pcbnew.F_Cu, width=0.30)
    add_poly_track(net_vin, [
        (143.363, 104.750),
        (142.600, 104.750),
        (142.600, 102.850),
        (143.363, 102.850),
    ], layer=pcbnew.F_Cu, width=0.25)
    # Also connect VIN to right side JP1 pin 1 (153.889, 88.984) via existing track at (155.039, 88.984)
    # In HEAD, VIN ran to JP1 from bottom. Let's connect VIN on B.Cu to JP1 via:
    add_poly_track(net_vin, [
        (142.500, 105.200),
        (155.200, 105.200),
        (155.200, 89.145),
        (153.889, 88.984),
    ], layer=pcbnew.B_Cu, width=0.25)

    # 7.3 VDD on bottom:
    # U2 pin 5: (145.637, 102.850)
    # R3 pad 1: (145.412, 101.800)
    # C4 pad 1: (147.200, 102.937)
    # R4 pad 1: (152.588, 102.500)
    add_poly_track(net_vdd, [
        (145.637, 102.850),
        (145.637, 101.800),
        (145.412, 101.800),
    ], layer=pcbnew.F_Cu, width=0.30)
    add_poly_track(net_vdd, [
        (145.637, 102.850),
        (147.200, 102.850),
        (147.200, 102.937),
    ], layer=pcbnew.F_Cu, width=0.30)
    # Route to R4 pad 1 on B.Cu well below H4 (H4 bottom is 103.626)
    add_via(net_vdd, 147.200, 102.000)
    add_track(net_vdd, 147.200, 102.850, 147.200, 102.000, layer=pcbnew.F_Cu, width=0.25)
    add_poly_track(net_vdd, [
        (147.200, 102.000),
        (147.200, 104.700),
        (152.588, 104.700),
        (152.588, 102.500),
    ], layer=pcbnew.B_Cu, width=0.25)
    add_via(net_vdd, 152.588, 102.500)
    # Connect VDD to U1 pin 4 (150.989, 93.354) on B.Cu along right edge
    add_poly_track(net_vdd, [
        (152.588, 102.500),
        (154.500, 102.500),
        (154.500, 93.354),
        (150.989, 93.354),
    ], layer=pcbnew.B_Cu, width=0.25)

    # 7.4 Net-(U2-NC):
    # U2 pin 4: (145.637, 104.750)
    # C5 pad 1: (154.363, 104.200)
    # R4 pad 2: (154.412, 102.500)
    add_via(net_u2_nc, 145.637, 104.750)
    add_poly_track(net_u2_nc, [
        (145.637, 104.750),
        (146.500, 105.350),
        (154.000, 105.350),
        (154.363, 104.987),
        (154.363, 104.200),
    ], layer=pcbnew.B_Cu, width=0.20)
    add_via(net_u2_nc, 154.363, 104.200)
    add_track(net_u2_nc, 154.363, 104.200, 154.412, 102.500, layer=pcbnew.F_Cu, width=0.20)

    # 7.5 GND on bottom:
    # C3 pad 2: (138.363, 103.500) -> via
    add_via(net_gnd, 138.363, 104.500)
    add_track(net_gnd, 138.363, 103.500, 138.363, 104.500, layer=pcbnew.F_Cu, width=0.30)
    # U2 pin 2: (143.363, 103.800) -> via
    add_via(net_gnd, 142.400, 103.800)
    add_track(net_gnd, 143.363, 103.800, 142.400, 103.800, layer=pcbnew.F_Cu, width=0.30)
    # C4 pad 2: (147.200, 104.663) -> via
    add_via(net_gnd, 147.200, 104.700)
    # C5 pad 2: (152.637, 104.200) -> via
    add_via(net_gnd, 152.637, 104.200)

    # 8. Route Top Area:
    # 8.1 TP3: (143.639, 80.800) GND -> via
    add_via(net_gnd, 143.639, 80.800)
    # U1 pin 8 GND: (150.989, 86.234) -> via to plane
    add_via(net_gnd, 152.000, 86.234)
    add_track(net_gnd, 150.989, 86.234, 152.000, 86.234, layer=pcbnew.F_Cu, width=0.30)

    # 8.2 TP1: (146.000, 80.800) VIO -> R2 pad 1 (155.052, 83.534), R1 pad 1 (155.052, 85.284)
    # Route on F.Cu at Y = 80.200
    add_poly_track(net_vio, [
        (146.000, 80.800),
        (146.000, 80.200),
        (154.200, 80.200),
        (155.052, 81.052),
        (155.052, 83.534),
        (155.052, 85.284),
    ], layer=pcbnew.F_Cu, width=0.25)
    # Connect VIO from TP1 to JP1 pin 2 (153.889, 90.284) on B.Cu
    add_via(net_vio, 146.000, 80.800)
    add_poly_track(net_vio, [
        (146.000, 80.800),
        (146.000, 80.400),
        (138.000, 80.400),
        (138.000, 87.000),
        (137.000, 88.000),
        (137.000, 90.284),
        (138.000, 90.284),
    ], layer=pcbnew.B_Cu, width=0.25)

    # 8.3 TP2: (148.500, 80.800) VDD -> connect to VDD bus at (154.139, 85.284)
    # Route on B.Cu at Y = 79.600
    add_via(net_vdd, 148.500, 80.800)
    add_poly_track(net_vdd, [
        (148.500, 80.800),
        (148.500, 79.600),
        (153.500, 79.600),
        (154.200, 80.300),
        (154.200, 84.500),
        (154.139, 84.861),
        (154.139, 85.284),
    ], layer=pcbnew.B_Cu, width=0.25)

    # 8.4 /RESET: J1 pin 8 (135.389, 84.129) to R1 pad 2 (153.226, 85.284)
    # Route on F.Cu at Y = 79.800 (above VIO at 80.200)
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

    # 8.5 /MISO: J1 pin 4 (135.389, 94.289) to R2 pad 2 (153.226, 83.534)
    # Route on B.Cu at Y = 80.000
    add_poly_track(net_miso, [
        (138.639, 89.7838),
        (138.639, 80.000),
        (151.000, 80.000),
        (152.500, 81.500),
        (152.500, 82.808),
        (153.226, 83.534),
    ], layer=pcbnew.B_Cu, width=0.20)
    add_via(net_miso, 153.226, 83.534)

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
    print("Clean PCB built and saved successfully.")

if __name__ == "__main__":
    build()
