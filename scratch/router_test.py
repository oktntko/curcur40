import pcbnew
import json
import subprocess

PCB_PATH = r"pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pcb"
KICAD_CLI = r"C:\Users\oktnt\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe"

def build_pcb():
    board = pcbnew.LoadBoard(PCB_PATH)
    netinfo = board.GetNetInfo()

    net_gnd = netinfo.GetNetItem("GND")
    net_vin = netinfo.GetNetItem("V_{IN}")
    net_vdd = netinfo.GetNetItem("VDD")
    net_vio = netinfo.GetNetItem("V_{IO}")
    net_led_p = netinfo.GetNetItem("Net-(U1-LED_P)")
    net_u2_nc = netinfo.GetNetItem("Net-(U2-NC)")
    net_reset = netinfo.GetNetItem("/RESET")
    net_miso = netinfo.GetNetItem("/MISO")

    # 1. Update Edge.Cuts (21.75 x 26.5 mm, r=2.5 mm)
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

    # 2. Replace Mounting Holes with standard M2 footprints
    m2_lib = r"C:\Users\oktnt\AppData\Local\Programs\KiCad\10.0\share\kicad\footprints\MountingHole.pretty"
    m2_coords = {
        "H1": (141.139, 82.9258),
        "H2": (150.139, 82.9258),
        "H3": (141.139, 102.1258),
        "H4": (150.139, 102.1258),
    }

    for ref, (hx, hy) in m2_coords.items():
        old_fp = board.FindFootprintByReference(ref)
        if old_fp:
            board.Delete(old_fp)
        new_fp = pcbnew.FootprintLoad(m2_lib, "MountingHole_2.2mm_M2")
        new_fp.SetReference(ref)
        new_fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(hx), pcbnew.FromMM(hy)))
        board.Add(new_fp)

    # 3. Relocate Test Points TP1, TP2, TP3 in top area between top M2 holes
    # TP3 (VIO), TP1 (GND), TP2 (VDD)
    tp_locs = {
        "TP3": (143.639, 81.200),
        "TP1": (145.639, 81.200),
        "TP2": (147.639, 81.200),
    }
    for ref, (tx, ty) in tp_locs.items():
        fp = board.FindFootprintByReference(ref)
        if fp:
            fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(tx), pcbnew.FromMM(ty)))

    # 4. Relocate components: C3 on left, U2 & C4 & R3 center, R4 & C5 on right
    comp_locs = {
        "C3": ((137.500, 103.600), 0.0),    # left of H3
        "U2": ((144.500, 103.600), 0.0),    # center
        "C4": ((147.200, 103.600), -90.0),  # center right of U2
        "R3": ((144.500, 101.600), 180.0),  # above U2
        "R4": ((153.500, 102.600), 0.0),    # right of H4
        "C5": ((153.500, 104.400), 0.0),    # right of H4, below R4
    }
    for ref, ((cx, cy), rot) in comp_locs.items():
        fp = board.FindFootprintByReference(ref)
        if fp:
            fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(cx), pcbnew.FromMM(cy)))
            fp.SetOrientationDegrees(rot)

    # 5. Remove existing tracks in bottom area (y > 97.0) and top area (y < 84.0)
    for t in list(board.GetTracks()):
        if t.GetClass() != "PCB_VIA":
            y1 = pcbnew.ToMM(t.GetStart().y)
            y2 = pcbnew.ToMM(t.GetEnd().y)
            if max(y1, y2) > 97.0:
                board.Delete(t)
            elif min(y1, y2) < 84.0:
                board.Delete(t)

    # Remove vias in bottom area (y > 97.0) and top area (y < 84.0)
    for v in list(board.GetTracks()):
        if v.GetClass() == "PCB_VIA":
            vy = pcbnew.ToMM(v.GetPosition().y)
            if vy > 97.0 or vy < 84.0:
                board.Delete(v)

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
    # 6.1 VIN:
    # J1 pin 2 at (135.389, 99.369)
    # C3 pad 1 at (136.638, 103.600)
    # U2 pad 1 at (143.363, 102.650)
    # U2 pad 3 at (143.363, 104.550)
    add_poly_track(net_vin, [
        (135.389, 99.369),
        (136.638, 100.618),
        (136.638, 103.600),
    ], width=0.30)
    # C3 pad 1 to U2 pad 1 & 3 via B.Cu under H3
    add_via(net_vin, 136.638, 104.500)
    add_poly_track(net_vin, [
        (136.638, 104.500),
        (136.638, 105.000),
        (142.500, 105.000),
        (142.500, 104.550),
        (143.363, 104.550),
    ], layer=pcbnew.B_Cu, width=0.30)
    add_via(net_vin, 143.363, 104.550)
    # Connect U2 pad 3 to pad 1 on F.Cu
    add_poly_track(net_vin, [
        (143.363, 104.550),
        (142.700, 103.890),
        (142.700, 103.310),
        (143.363, 102.650),
    ], width=0.25)

    # 6.2 VDD:
    # U2 pad 5 at (145.637, 102.650)
    # C4 pad 1 at (147.200, 102.738)
    # R3 pad 1 at (145.413, 101.600)
    add_track(net_vdd, 145.637, 102.650, 147.200, 102.650, width=0.30)
    add_track(net_vdd, 147.200, 102.650, 147.200, 102.738, width=0.30)
    add_poly_track(net_vdd, [
        (145.637, 102.650),
        (145.637, 101.824),
        (145.413, 101.600),
    ], width=0.25)
    # VDD to R4 pad 1 at (152.638, 102.600) via B.Cu under H4
    add_via(net_vdd, 147.200, 101.800)
    add_poly_track(net_vdd, [
        (147.200, 101.800),
        (147.200, 101.200),
        (152.000, 101.200),
        (152.638, 101.838),
        (152.638, 102.600),
    ], layer=pcbnew.B_Cu, width=0.25)
    add_via(net_vdd, 152.638, 102.600)

    # Connect VDD to existing main VDD bus at (153.889, 91.584)
    add_poly_track(net_vdd, [
        (152.638, 101.838),
        (154.500, 101.838),
        (154.500, 93.000),
        (153.889, 92.389),
        (153.889, 91.584),
    ], layer=pcbnew.B_Cu, width=0.30)

    # 6.3 LED_P:
    # U1 pin 9 (LED_P) at (141.270, 95.826)
    # R3 pad 2 at (143.587, 101.600)
    add_poly_track(net_led_p, [
        (141.270, 95.826),
        (141.270, 99.283),
        (143.587, 101.600),
    ], width=0.25)

    # 6.4 Net-(U2-NC):
    # U2 pad 4 at (145.637, 104.550)
    # C5 pad 1 at (152.638, 104.400)
    # R4 pad 2 at (154.362, 102.600)
    add_via(net_u2_nc, 145.637, 104.550)
    add_poly_track(net_u2_nc, [
        (145.637, 104.550),
        (146.500, 105.413),
        (151.500, 105.413),
        (152.638, 104.400),
    ], layer=pcbnew.B_Cu, width=0.20)
    add_via(net_u2_nc, 152.638, 104.400)
    add_poly_track(net_u2_nc, [
        (152.638, 104.400),
        (154.362, 104.400),
        (154.362, 102.600),
    ], width=0.20)

    # 6.5 GND Vias for bottom components:
    # C3 pad 2 at (138.362, 103.600)
    add_via(net_gnd, 138.362, 104.400)
    add_track(net_gnd, 138.362, 103.600, 138.362, 104.400)
    # U2 pad 2 at (143.363, 103.600)
    add_via(net_gnd, 142.400, 103.600)
    add_track(net_gnd, 143.363, 103.600, 142.400, 103.600)
    # C4 pad 2 at (147.200, 104.462)
    add_via(net_gnd, 147.200, 104.462)
    # C5 pad 2 at (154.362, 104.400)
    add_via(net_gnd, 154.362, 105.100)
    add_track(net_gnd, 154.362, 104.400, 154.362, 105.100)

    # 7. Top Area Re-routing:
    # TP1 (GND at 145.639, 81.200)
    add_via(net_gnd, 145.639, 81.200)
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
    # TP3 (VIO at 143.639, 81.200) -> connect to VIO net at JP1 pad 2
    add_via(net_vio, 143.639, 81.200)
    add_poly_track(net_vio, [
        (143.639, 81.200),
        (143.639, 80.200),
        (139.000, 80.200),
        (138.000, 81.200),
        (138.000, 87.000),
        (137.000, 88.000),
        (137.000, 90.000),
    ], layer=pcbnew.B_Cu, width=0.25)

    # /RESET track from J1 pin 8 (135.389, 84.129) to R1 pad 2 (153.226, 85.284)
    # Bypass H1 (141.139, 82.9258) by routing above it or below it
    add_poly_track(net_reset, [
        (135.389, 84.129),
        (138.000, 84.129),
        (139.000, 85.129),
        (143.000, 85.129),
        (145.000, 83.129),
        (145.000, 84.500),
        (152.000, 84.500),
        (152.784, 85.284),
        (153.226, 85.284),
    ], width=0.20)

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

    board.Save(PCB_PATH)
    print("PCB built successfully.")

if __name__ == "__main__":
    build_pcb()
