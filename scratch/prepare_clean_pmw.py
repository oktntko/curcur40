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

# 1. Update Edge.Cuts to Plan B: 21.75 x 26.50 mm, r = 2.50 mm
# Center: X0 = 145.264, Y0 = 92.5258
xL, xR = 134.389, 156.139
yT, yB = 79.2758, 105.7758
rC = 2.5000
s2 = rC * (1.0 - 0.70710678)

for d in list(board.GetDrawings()):
    if d.GetLayerName() == "Edge.Cuts":
        board.Delete(d)

def mm(val): return pcbnew.FromMM(float(val))
def pt(x, y): return pcbnew.VECTOR2I(mm(x), mm(y))

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

# 4. Remove conflicting tracks at top and bottom:
for t in list(board.GetTracks()):
    y1 = pcbnew.ToMM(t.GetStart().y)
    y2 = pcbnew.ToMM(t.GetEnd().y)
    ymin, ymax = min(y1, y2), max(y1, y2)
    # Delete bottom tracks where components are moved
    if ymax > 102.0:
        board.Delete(t)
    # Delete top tracks where H1/H2 and TP1/2/3 are moved
    elif ymin < 84.5 and t.GetNetname() in ['/RESET', '/MISO', 'VDD', 'V_{IO}', 'GND']:
        board.Delete(t)

# 5. Position bottom components
comp_locs = {
    "C3": ((137.500, 103.500), 0.0),    # Pad 1 (VIN) at 136.637, Pad 2 (GND) at 138.363
    "U2": ((145.639, 104.000), 0.0),    # Pin 1,3 (VIN, EN) at 144.502, Pin 2 (GND) at 144.502, Pin 4 (NC), Pin 5 (VDD) at 146.776
    "C4": ((148.500, 103.500), -90.0),  # Pad 1 (VDD) at 148.500, Pad 2 (GND) at 148.500
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

board.Save(OUT_PCB)
print("Base board prepared and saved.")
