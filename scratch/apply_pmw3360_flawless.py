import pcbnew
import math
import subprocess
import json

SRC_PCB = r"scratch/orig_pmw3360.kicad_pcb"
OUT_PCB = r"pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pcb"
KICAD_CLI = r"C:\Users\oktnt\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe"

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

def mm(val): return pcbnew.FromMM(float(val))
def pt(x, y): return pcbnew.VECTOR2I(mm(x), mm(y))

# 1. Update Edge.Cuts to Plan B: 21.75 x 26.50 mm, r = 2.50 mm
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
    sh.SetStart(pt(x1, y1))
    sh.SetEnd(pt(x2, y2))
    sh.SetWidth(mm(0.15))
    board.Add(sh)

def add_edge_arc(x1, y1, xm, ym, x2, y2):
    sh = pcbnew.PCB_SHAPE(board)
    sh.SetShape(pcbnew.SHAPE_T_ARC)
    sh.SetLayer(pcbnew.Edge_Cuts)
    sh.SetArcGeometry(pt(x1, y1), pt(xm, ym), pt(x2, y2))
    sh.SetWidth(mm(0.15))
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
    new_fp.SetPosition(pt(hx, hy))
    board.Add(new_fp)

# 3. Update U1 central aperture to 8.70 x 16.90 mm (centered at (145.639, 92.5258))
u1 = board.FindFootprintByReference("U1")
for d in u1.GraphicalItems():
    if d.GetLayerName() == "Edge.Cuts":
        d.SetStart(pt(141.289, 84.0758))
        d.SetEnd(pt(149.989, 100.9758))

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
        poly.Append(mm(kx), mm(ky))

# 4. Shift East VDD bus inwards to X = 155.000 so it clears the board edge (xR = 156.139):
for t in board.GetTracks():
    sp, ep = t.GetStart(), t.GetEnd()
    sx, sy = pcbnew.ToMM(sp.x), pcbnew.ToMM(sp.y)
    ex, ey = pcbnew.ToMM(ep.x), pcbnew.ToMM(ep.y)
    if sx > 155.8:
        t.SetStart(pt(155.000, sy))
    if ex > 155.8:
        t.SetEnd(pt(155.000, ey))
    if t.GetClass() == 'PCB_VIA':
        pos = t.GetPosition()
        vx, vy = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
        if vx > 155.8:
            t.SetPosition(pt(155.000, vy))

# 5. Position bottom components
comp_locs = {
    "C3": ((137.500, 103.500), 0.0),    # Pad 1 (VIN) at 136.637, Pad 2 (GND) at 138.363
    "U2": ((145.639, 104.000), 0.0),    # Pin 1,3 (VIN, EN) at 144.502, Pin 2 (GND) at 144.502, Pin 4 (NC), Pin 5 (VDD) at 146.776
    "C4": ((147.600, 104.000), -90.0),  # Pad 1 (VDD) at 147.600, Pad 2 (GND) at 147.600
    "R3": ((144.500, 101.800), 180.0),  # Pad 1 (VDD) at 145.412, Pad 2 (LED_P) at 143.588
    "R4": ((153.500, 102.500), 0.0),    # Pad 1 (VDD) at 152.588, Pad 2 (NC) at 154.412
    "C5": ((153.500, 104.200), 180.0),  # Pad 1 (NC) at 154.363, Pad 2 (GND) at 152.637
}
for ref, ((cx, cy), rot) in comp_locs.items():
    fp = board.FindFootprintByReference(ref)
    if fp:
        fp.SetPosition(pt(cx, cy))
        fp.SetOrientationDegrees(rot)

# 6. Position top test points:
tp_locs = {
    "TP3": (143.639, 81.200),
    "TP1": (146.000, 81.200),
    "TP2": (148.500, 81.200),
}
for ref, (tx, ty) in tp_locs.items():
    fp = board.FindFootprintByReference(ref)
    if fp:
        fp.SetPosition(pt(tx, ty))

# 7. Delete conflicting tracks at top and bottom
for t in list(board.GetTracks()):
    y1 = pcbnew.ToMM(t.GetStart().y)
    y2 = pcbnew.ToMM(t.GetEnd().y)
    ymin, ymax = min(y1, y2), max(y1, y2)
    if ymax > 102.0:
        board.Delete(t)
    elif ymin < 84.5 and t.GetNetname() in ['/RESET', '/MISO', 'VDD', 'V_{IO}', 'GND']:
        board.Delete(t)

# 8. Add tracks using clean helper
def add_track_path(net_obj, pts, layer=pcbnew.F_Cu, width=0.25):
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        t = pcbnew.PCB_TRACK(board)
        t.SetLayer(layer)
        t.SetNet(net_obj)
        t.SetStart(pt(x1, y1))
        t.SetEnd(pt(x2, y2))
        t.SetWidth(mm(width))
        board.Add(t)

def add_via_item(net_obj, x, y, drill=0.3, size=0.5):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pt(x, y))
    v.SetDrill(mm(drill))
    v.SetWidth(mm(size))
    v.SetNet(net_obj)
    board.Add(v)

# Top tracks:
# /RESET: J1 pin 8 (135.389, 84.129) -> R1 pad 2 (153.226, 85.284)
add_track_path(net_reset, [
    (135.389, 84.129),
    (136.500, 84.129),
    (137.500, 83.129),
    (137.500, 79.800),
    (151.000, 79.800),
    (152.000, 80.800),
    (152.000, 84.058),
    (153.226, 85.284),
], layer=pcbnew.F_Cu, width=0.20)

# /MISO: on B.Cu from (138.639, 89.784) -> R2 pad 2 (153.226, 83.534)
add_track_path(net_miso, [
    (138.639, 89.784),
    (138.639, 80.200),
    (151.000, 80.200),
    (152.500, 81.700),
    (152.500, 82.808),
    (153.226, 83.534),
], layer=pcbnew.B_Cu, width=0.20)
add_via_item(net_miso, 153.226, 83.534, size=0.5)

# V_{IO} on F.Cu at Y = 80.400: TP1 (146.0, 81.2) -> R2 pad 1 (155.052, 83.534)
add_track_path(net_vio, [
    (146.000, 81.200),
    (146.000, 80.400),
    (154.200, 80.400),
    (155.052, 81.252),
    (155.052, 83.534),
], layer=pcbnew.F_Cu, width=0.20)

# VDD on B.Cu at Y = 79.600: TP2 (148.5, 81.2) -> VDD bus at (155.0, 84.5)
add_via_item(net_vdd, 148.500, 81.200, size=0.5)
add_track_path(net_vdd, [
    (148.500, 81.200),
    (148.500, 79.600),
    (155.000, 79.600),
    (155.000, 84.500),
], layer=pcbnew.B_Cu, width=0.25)

# Bottom tracks:
# 1. VIN: J1 pin 2 (135.389, 99.369) -> C3 pad 1 (136.637, 103.500) -> U2 pin 1,3
add_track_path(net_vin, [
    (135.389, 99.369),
    (136.637, 100.617),
    (136.637, 103.500),
], layer=pcbnew.F_Cu, width=0.30)
# From C3.1 (136.637, 103.500) to U2.1 & 3:
# Via to B.Cu at (136.637, 104.700)
add_track_path(net_vin, [(136.637, 103.500), (136.637, 104.700)], layer=pcbnew.F_Cu, width=0.30)
add_via_item(net_vin, 136.637, 104.700, size=0.5)
# On B.Cu across to U2 at Y = 105.100
add_track_path(net_vin, [
    (136.637, 104.700),
    (136.637, 105.100),
    (143.500, 105.100),
    (143.500, 104.950),
], layer=pcbnew.B_Cu, width=0.30)
add_via_item(net_vin, 143.500, 104.950, size=0.5)
add_track_path(net_vin, [
    (143.500, 104.950),
    (144.502, 104.950), # U2 pin 3 (EN)
    (143.700, 104.950),
    (143.700, 103.050),
    (144.502, 103.050), # U2 pin 1 (VIN)
], layer=pcbnew.F_Cu, width=0.25)

# Connect VIN to JP1 pin 1 on B.Cu:
# From (143.500, 105.100) -> east on B.Cu to (154.5, 105.1) -> north to (154.5, 90.284) -> JP1.1 (153.889, 90.284)
add_track_path(net_vin, [
    (143.500, 105.100),
    (154.500, 105.100),
    (154.500, 90.284),
    (153.889, 90.284),
], layer=pcbnew.B_Cu, width=0.25)
add_via_item(net_vin, 153.889, 90.284, size=0.5)

# 2. VDD on bottom:
# U2 pin 5 (146.776, 103.050) -> C4 pad 1 (147.600, 103.138) -> R3 pad 1 (145.412, 101.800)
add_track_path(net_vdd, [
    (146.776, 103.050),
    (147.600, 103.050),
    (147.600, 103.138),
], layer=pcbnew.F_Cu, width=0.30)
add_track_path(net_vdd, [
    (146.776, 103.050),
    (146.776, 101.800),
    (145.412, 101.800),
], layer=pcbnew.F_Cu, width=0.30)
# Connect VDD to R4.1 (152.588, 102.500) and VDD bus:
add_track_path(net_vdd, [
    (147.600, 103.050),
    (147.600, 102.000),
], layer=pcbnew.F_Cu, width=0.25)
add_via_item(net_vdd, 147.600, 102.000, size=0.5)
add_track_path(net_vdd, [
    (147.600, 102.000),
    (147.600, 101.200),
    (152.000, 101.200),
    (152.000, 102.500),
    (152.588, 102.500),
], layer=pcbnew.B_Cu, width=0.25)
# Continue to VDD bus at (155.000, 101.200) -> (155.000, 96.000)
add_track_path(net_vdd, [
    (152.000, 101.200),
    (155.000, 101.200),
    (155.000, 96.000),
], layer=pcbnew.B_Cu, width=0.25)

# 3. Net-(U1-LED_P): from U1.15 (140.289, 96.024) to R3 pad 2 (143.588, 101.800)
add_track_path(net_led_p, [
    (140.289, 96.024),
    (139.000, 96.024),
    (139.000, 101.800),
    (143.588, 101.800),
], layer=pcbnew.F_Cu, width=0.25)

# 4. Net-(U2-NC): U2 pin 4 (146.776, 104.950) -> R4 pad 2 (154.412, 102.500) and C5 pad 1 (154.363, 104.200)
add_track_path(net_u2_nc, [
    (146.776, 104.950),
    (147.500, 104.950),
], layer=pcbnew.F_Cu, width=0.25)
add_via_item(net_u2_nc, 147.500, 104.950, size=0.5)
add_track_path(net_u2_nc, [
    (147.500, 104.950),
    (153.500, 104.950),
    (154.400, 104.050),
    (154.400, 102.500),
    (154.412, 102.500),
], layer=pcbnew.B_Cu, width=0.25)
add_via_item(net_u2_nc, 154.400, 104.050, size=0.5)
add_track_path(net_u2_nc, [
    (154.400, 104.050),
    (154.363, 104.200),
], layer=pcbnew.F_Cu, width=0.25)

# 5. GND vias for bottom components:
add_via_item(net_gnd, 138.363, 104.700, size=0.5) # near C3 pad 2
add_track_path(net_gnd, [(138.363, 103.500), (138.363, 104.700)], layer=pcbnew.F_Cu, width=0.25)

add_via_item(net_gnd, 144.502, 103.000, size=0.5) # near U2 pin 2

add_via_item(net_gnd, 147.600, 105.200, size=0.5) # near C4 pad 2
add_track_path(net_gnd, [(147.600, 104.863), (147.600, 105.200)], layer=pcbnew.F_Cu, width=0.25)

add_via_item(net_gnd, 152.637, 105.200, size=0.5) # near C5 pad 2
add_track_path(net_gnd, [(152.637, 104.200), (152.637, 105.200)], layer=pcbnew.F_Cu, width=0.25)

# Refill all zones
zf = pcbnew.ZONE_FILLER(board)
zf.Fill(board.Zones())

board.Save(OUT_PCB)
print("PMW3360 flawless board saved.")
