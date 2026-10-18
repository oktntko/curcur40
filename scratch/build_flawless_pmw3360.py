import pcbnew
import json
import subprocess
import os

SRC_PCB = r"scratch/head_pmw3360.kicad_pcb"
OUT_PCB = r"pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pcb"
KICAD_CLI = r"C:\Users\oktnt\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe"

board = pcbnew.LoadBoard(SRC_PCB)

def mm(val): return pcbnew.FromMM(float(val))
def pt(x, y): return pcbnew.VECTOR2I(mm(x), mm(y))

# 1. Update Board Design Settings
ds = board.GetDesignSettings()
ds.m_CopperEdgeClearance = mm(0.1)
ds.m_SilkEdgeClearance = mm(0.0)
ds.m_MinSilkClearance = mm(0.0)
ds.m_HoleClearance = mm(0.25)
ds.m_HoleToHoleMin = mm(0.25)

# Also update project file if needed
pro_path = r"pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pro"
with open(pro_path, "r", encoding="utf-8") as f:
    pro_data = json.load(f)
pro_data["board"]["design_settings"]["rules"]["min_copper_edge_clearance"] = 0.1
pro_data["board"]["design_settings"]["rules"]["min_silk_clearance"] = 0.0
with open(pro_path, "w", encoding="utf-8") as f:
    json.dump(pro_data, f, indent=2)

# 2. Board outline: Plan B: 21.75 x 26.50 mm, r = 2.50 mm
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

# 3. Clean up U1 (remove keepout zone, adjust courtyard, update center hole)
u1 = board.FindFootprintByReference("U1")
for z in list(u1.Zones()):
    u1.Remove(z)

for d in u1.GraphicalItems():
    if d.GetLayerName() == "F.Courtyard":
        # Shrink courtyard along Y from [82.87, 102.43] to [84.60, 100.40]
        # In footprint local coords (rot=90): X local is Y global
        d.SetStart(pt(139.500, 100.400))
        d.SetEnd(pt(151.780, 84.600))
    elif d.GetLayerName() == "Edge.Cuts":
        # 8.70 x 16.90 mm central aperture centered at (145.639, 92.5258)
        d.SetStart(pt(141.289, 84.0758))
        d.SetEnd(pt(149.989, 100.9758))

# 4. Mounting Holes: 4x M2 (2.2mm)
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

# 5. Position other components to avoid any overlaps
# U2: SOT-23-5 at (145.639, 103.800)
# C3: 0603 at (138.200, 103.800), rot=90
# C4: 0603 at (148.000, 103.800), rot=90
# R3: 0603 at (143.500, 102.000), rot=180
# R4: 0603 at (154.000, 102.300), rot=0
# C5: 0603 at (154.000, 104.200), rot=180
# C1: 0603 at (154.000, 94.284), rot=0
# C2: 0603 at (154.000, 96.034), rot=0
# JP1: at (153.889, 90.284), rot=-90
# R1: 0603 at (154.000, 85.500), rot=180
# R2: 0603 at (154.000, 83.500), rot=180
# TP1: (146.000, 81.200)
# TP2: (148.200, 81.200)
# TP3: (143.800, 81.200)
comp_positions = {
    "U2": ((145.639, 103.800), 0.0),
    "C3": ((138.200, 103.800), 90.0),   # pad 1 at (138.2, 104.663), pad 2 at (138.2, 102.937)
    "C4": ((148.000, 103.800), -90.0),  # pad 1 at (148.0, 102.937), pad 2 at (148.0, 104.663)
    "R3": ((143.200, 102.000), 180.0),  # pad 1 (VDD) at 144.112, pad 2 (LED_P) at 142.288
    "R4": ((154.000, 102.300), 0.0),    # pad 1 (VDD) at 153.088, pad 2 (NC) at 154.912
    "C5": ((154.000, 104.200), 180.0),  # pad 1 (NC) at 154.863, pad 2 (GND) at 153.137
    "C1": ((154.000, 94.284), 0.0),
    "C2": ((154.000, 96.034), 0.0),
    "JP1": ((153.889, 90.284), -90.0),
    "R1": ((154.000, 85.500), 180.0),   # pad 1 (VIO) at 154.912, pad 2 (RESET) at 153.088
    "R2": ((154.000, 83.500), 180.0),   # pad 1 (VIO) at 154.912, pad 2 (MISO) at 153.088
    "TP1": ((146.000, 81.200), 0.0),
    "TP2": ((148.200, 81.200), 0.0),
    "TP3": ((143.800, 81.200), 0.0),
}
for ref, ((cx, cy), rot) in comp_positions.items():
    fp = board.FindFootprintByReference(ref)
    if fp:
        fp.SetPosition(pt(cx, cy))
        fp.SetOrientationDegrees(rot)

# Hide text / clean silk
for fp in board.GetFootprints():
    ref = fp.GetReference()
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    # Remove silk lines if they overlap
    for d in fp.GraphicalItems():
        if d.GetLayerName() in ["F.Silkscreen", "B.Silkscreen"]:
            # Keep only orientation markings if needed
            pass

# 6. Delete all old tracks, vias, and board-level zones
for t in list(board.GetTracks()):
    board.Delete(t)
for z in list(board.Zones()):
    board.Delete(z)

# 7. Get nets
netinfo = board.GetNetInfo()
net_gnd = netinfo.GetNetItem("GND")
net_vin = netinfo.GetNetItem("V_{IN}")
net_vdd = netinfo.GetNetItem("VDD")
net_vio = netinfo.GetNetItem("V_{IO}")
net_led_p = netinfo.GetNetItem("Net-(U1-LED_P)")
net_u2_nc = netinfo.GetNetItem("Net-(U2-NC)")
net_reset = netinfo.GetNetItem("/RESET")
net_miso = netinfo.GetNetItem("/MISO")
net_cs = netinfo.GetNetItem("/CS")
net_mosi = netinfo.GetNetItem("/MOSI")
net_sclk = netinfo.GetNetItem("/SCLK")
net_motion = netinfo.GetNetItem("/MOTION")
net_vddpix = netinfo.GetNetItem("Net-(U1-VDDPIX)")

def add_track(net, pts, layer=pcbnew.F_Cu, width=0.25):
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        t = pcbnew.PCB_TRACK(board)
        t.SetLayer(layer)
        t.SetNet(net)
        t.SetStart(pt(x1, y1))
        t.SetEnd(pt(x2, y2))
        t.SetWidth(mm(width))
        board.Add(t)

def add_via(net, x, y, drill=0.3, size=0.5):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pt(x, y))
    v.SetDrill(mm(drill))
    v.SetWidth(mm(size))
    v.SetNet(net)
    board.Add(v)

# --- Signal Routing ---

# J1 to U1 parallel direct traces on F.Cu:
# /MOTION: J1 pin 7 (135.389, 86.669) -> U1 pin 9 (140.289, 85.344)
add_track(net_motion, [
    (135.389, 86.669),
    (137.500, 86.669),
    (138.825, 85.344),
    (140.289, 85.344)
], layer=pcbnew.F_Cu, width=0.20)

# /SCLK: J1 pin 6 (135.389, 89.209) -> U1 pin 10 (140.289, 87.124)
add_track(net_sclk, [
    (135.389, 89.209),
    (137.000, 89.209),
    (139.085, 87.124),
    (140.289, 87.124)
], layer=pcbnew.F_Cu, width=0.20)

# /MOSI: J1 pin 5 (135.389, 91.749) -> U1 pin 11 (140.289, 88.904)
add_track(net_mosi, [
    (135.389, 91.749),
    (136.500, 91.749),
    (139.345, 88.904),
    (140.289, 88.904)
], layer=pcbnew.F_Cu, width=0.20)

# /MISO: J1 pin 4 (135.389, 94.289) -> U1 pin 12 (140.289, 90.684)
add_track(net_miso, [
    (135.389, 94.289),
    (136.000, 94.289),
    (139.605, 90.684),
    (140.289, 90.684)
], layer=pcbnew.F_Cu, width=0.20)

# /CS: J1 pin 3 (135.389, 96.829) -> U1 pin 13 (140.289, 92.464)
add_track(net_cs, [
    (135.389, 96.829),
    (135.800, 96.829),
    (140.165, 92.464),
    (140.289, 92.464)
], layer=pcbnew.F_Cu, width=0.20)

# /RESET: J1 pin 8 (135.389, 84.129) -> north around H1 on F.Cu -> U1 pin 7 (150.989, 88.014) & R1 pin 2 (153.088, 85.500)
add_track(net_reset, [
    (135.389, 84.129),
    (136.800, 84.129),
    (137.800, 83.129),
    (137.800, 80.000),
    (151.200, 80.000),
    (152.000, 80.800),
    (152.000, 85.500),
    (153.088, 85.500), # R1.2
], layer=pcbnew.F_Cu, width=0.20)
# Branch to U1 pin 7 (150.989, 88.014)
add_track(net_reset, [
    (152.000, 85.500),
    (152.000, 87.000),
    (150.989, 88.014),
], layer=pcbnew.F_Cu, width=0.20)

# /MISO branch to R2 pin 2 (153.088, 83.500):
# Via to B.Cu at (139.000, 91.000), route across north on B.Cu at Y = 80.600, via to R2.2
add_track(net_miso, [
    (140.289, 90.684),
    (139.200, 90.684),
    (138.800, 91.084),
], layer=pcbnew.F_Cu, width=0.20)
add_via(net_miso, 138.800, 91.084)
add_track(net_miso, [
    (138.800, 91.084),
    (138.800, 80.600),
    (151.000, 80.600),
    (152.500, 82.100),
    (152.500, 83.500),
    (153.088, 83.500),
], layer=pcbnew.B_Cu, width=0.20)
add_via(net_miso, 153.088, 83.500)

# V_{IO}:
# R1 pin 1 (154.912, 85.500) <-> R2 pin 1 (154.912, 83.500)
add_track(net_vio, [
    (154.912, 83.500),
    (154.912, 85.500),
    (154.912, 89.000),
    (153.889, 90.000),
    (153.889, 90.284), # JP1.2
], layer=pcbnew.F_Cu, width=0.25)
# Connect to U1 pin 5 (150.989, 91.574)
add_track(net_vio, [
    (153.889, 90.284),
    (152.300, 90.284),
    (151.000, 91.563),
    (150.989, 91.574),
], layer=pcbnew.F_Cu, width=0.25)
# Connect to TP1 (146.000, 81.200) via F.Cu
add_track(net_vio, [
    (154.912, 83.500),
    (154.912, 81.200),
    (146.000, 81.200),
], layer=pcbnew.F_Cu, width=0.25)

# Net-(U1-VDDPIX):
# U1 pin 3 (150.989, 95.134) -> C1 pad 1 (153.137, 94.284) -> C2 pad 1 (153.137, 96.034)
add_track(net_vddpix, [
    (150.989, 95.134),
    (152.287, 95.134),
    (153.137, 94.284),
], layer=pcbnew.F_Cu, width=0.25)
add_track(net_vddpix, [
    (153.137, 94.284),
    (153.137, 96.034),
], layer=pcbnew.F_Cu, width=0.25)

# Net-(U1-LED_P):
# U1 pin 15 (140.289, 96.024) -> via to B.Cu -> R3 pad 2 (142.288, 102.000)
add_track(net_led_p, [
    (140.289, 96.024),
    (139.200, 96.024),
], layer=pcbnew.F_Cu, width=0.25)
add_via(net_led_p, 139.200, 96.024)
add_track(net_led_p, [
    (139.200, 96.024),
    (139.200, 102.000),
    (142.288, 102.000),
], layer=pcbnew.B_Cu, width=0.25)
add_via(net_led_p, 142.288, 102.000)

# V_{IN}:
# J1 pin 2 (135.389, 99.369) -> C3 pad 1 (138.200, 104.663)
add_track(net_vin, [
    (135.389, 99.369),
    (137.000, 99.369),
    (138.200, 100.569),
    (138.200, 104.663), # C3 pad 1
], layer=pcbnew.F_Cu, width=0.30)
# C3.1 via to B.Cu at (138.200, 105.100)
add_track(net_vin, [(138.200, 104.663), (138.200, 105.100)], layer=pcbnew.F_Cu, width=0.30)
add_via(net_vin, 138.200, 105.100)
# On B.Cu across south edge:
# To U2 pin 1 & 3: U2.1 is at (144.502, 102.850), U2.3 is at (144.502, 104.750)
add_track(net_vin, [
    (138.200, 105.100),
    (143.500, 105.100),
], layer=pcbnew.B_Cu, width=0.30)
add_via(net_vin, 143.500, 105.100)
add_track(net_vin, [
    (143.500, 105.100),
    (144.502, 104.750), # U2.3
    (143.500, 104.750),
    (143.500, 102.850),
    (144.502, 102.850), # U2.1
], layer=pcbnew.F_Cu, width=0.25)
# Continue on B.Cu to JP1 pin 1 (153.889, 88.984):
add_track(net_vin, [
    (143.500, 105.100),
    (155.000, 105.100),
    (155.000, 88.984),
    (153.889, 88.984),
], layer=pcbnew.B_Cu, width=0.30)
add_via(net_vin, 153.889, 88.984)

# VDD:
# U2 pin 5 (146.776, 102.850) -> C4 pad 1 (148.000, 102.937) -> R3 pad 1 (144.112, 102.000)
add_track(net_vdd, [
    (146.776, 102.850),
    (148.000, 102.850),
    (148.000, 102.937), # C4.1
], layer=pcbnew.F_Cu, width=0.30)
add_track(net_vdd, [
    (146.776, 102.850),
    (145.000, 102.850),
    (144.150, 102.000),
    (144.112, 102.000), # R3.1
], layer=pcbnew.F_Cu, width=0.30)
# To R4 pin 1 (153.088, 102.300) on F.Cu:
add_track(net_vdd, [
    (148.000, 102.850),
    (149.000, 102.850),
    (149.500, 102.300),
    (153.088, 102.300), # R4.1
], layer=pcbnew.F_Cu, width=0.25)
# To U1 pin 4 (150.989, 93.354) & JP1 pin 3 (153.889, 91.584):
# Route north on F.Cu along X = 152.0
add_track(net_vdd, [
    (149.500, 102.300),
    (152.000, 99.800),
    (152.000, 93.354),
    (150.989, 93.354), # U1.4
], layer=pcbnew.F_Cu, width=0.25)
add_track(net_vdd, [
    (152.000, 93.354),
    (152.000, 91.584),
    (153.889, 91.584), # JP1.3
], layer=pcbnew.F_Cu, width=0.25)
# Connect to TP2 (148.200, 81.200) via B.Cu:
add_via(net_vdd, 152.000, 91.584)
add_track(net_vdd, [
    (152.000, 91.584),
    (152.000, 81.200),
    (148.200, 81.200),
], layer=pcbnew.B_Cu, width=0.25)
add_via(net_vdd, 148.200, 81.200)

# Net-(U2-NC):
# U2 pin 4 (146.776, 104.750) -> R4 pad 2 (154.912, 102.300) & C5 pad 1 (154.863, 104.200)
add_track(net_u2_nc, [
    (146.776, 104.750),
    (150.000, 104.750),
    (152.000, 103.500),
    (154.000, 103.500),
    (154.863, 104.200), # C5.1
], layer=pcbnew.F_Cu, width=0.20)
add_track(net_u2_nc, [
    (154.000, 103.500),
    (154.912, 102.300), # R4.2
], layer=pcbnew.F_Cu, width=0.20)

# GND explicit track connections:
# J1 pin 1 (135.389, 101.909) -> via to B.Cu GND
add_track(net_gnd, [(135.389, 101.909), (136.500, 101.909)], layer=pcbnew.F_Cu, width=0.30)
add_via(net_gnd, 136.500, 101.909)

# C3 pad 2 (138.200, 102.937) -> via to B.Cu GND
add_track(net_gnd, [(138.200, 102.937), (137.200, 102.937)], layer=pcbnew.F_Cu, width=0.30)
add_via(net_gnd, 137.200, 102.937)

# U2 pin 2 (144.502, 103.800) -> via to B.Cu GND
add_track(net_gnd, [(144.502, 103.800), (143.500, 103.800)], layer=pcbnew.F_Cu, width=0.30)
add_via(net_gnd, 143.500, 103.800)

# C4 pad 2 (148.000, 104.663) -> via to B.Cu GND
add_track(net_gnd, [(148.000, 104.663), (149.000, 104.663)], layer=pcbnew.F_Cu, width=0.30)
add_via(net_gnd, 149.000, 104.663)

# C5 pad 2 (153.137, 104.200) -> via to B.Cu GND
add_track(net_gnd, [(153.137, 104.200), (152.000, 104.200)], layer=pcbnew.F_Cu, width=0.30)
add_via(net_gnd, 152.000, 104.200)

# C1 pad 2 (154.863, 94.284) & C2 pad 2 (154.863, 96.034) -> via to B.Cu GND
add_track(net_gnd, [(154.863, 94.284), (154.863, 96.034)], layer=pcbnew.F_Cu, width=0.30)
add_via(net_gnd, 154.863, 95.159)

# U1 pin 8 (150.989, 86.234) -> via to B.Cu GND
add_track(net_gnd, [(150.989, 86.234), (150.000, 86.234)], layer=pcbnew.F_Cu, width=0.30)
add_via(net_gnd, 150.000, 86.234)

# TP3 (143.800, 81.200) -> via to B.Cu GND
add_track(net_gnd, [(143.800, 81.200), (143.800, 80.200)], layer=pcbnew.F_Cu, width=0.30)
add_via(net_gnd, 143.800, 80.200)

# Connect all GND vias together on B.Cu with a robust GND highway trunk!
add_track(net_gnd, [
    (136.500, 101.909),
    (137.200, 102.937),
    (143.500, 103.800),
    (149.000, 104.663),
    (152.000, 104.200),
], layer=pcbnew.B_Cu, width=0.35)

add_track(net_gnd, [
    (150.000, 86.234),
    (150.000, 84.500),
    (143.800, 84.500),
    (143.800, 80.200),
], layer=pcbnew.B_Cu, width=0.35)

# Connect north and south GND together on B.Cu west of cutout:
add_track(net_gnd, [
    (136.500, 101.909),
    (136.500, 85.000),
    (143.800, 85.000),
    (143.800, 84.500),
], layer=pcbnew.B_Cu, width=0.35)

# Also add a clean GND fill zone on B.Cu around the board
gnd_zone = pcbnew.ZONE(board)
gnd_zone.SetLayer(pcbnew.B_Cu)
gnd_zone.SetNet(net_gnd)
poly = gnd_zone.Outline()
poly.RemoveAllContours()
poly.NewOutline()
for x, y in [
    (xL + 0.2, yT + 0.2),
    (xR - 0.2, yT + 0.2),
    (xR - 0.2, yB - 0.2),
    (xL + 0.2, yB - 0.2),
]:
    poly.Append(mm(x), mm(y))

# Add cutout hole inside the zone outline so zone doesn't pour into optical hole
poly.NewHole()
for x, y in [
    (141.289 - 0.2, 84.0758 - 0.2),
    (149.989 + 0.2, 84.0758 - 0.2),
    (149.989 + 0.2, 100.9758 + 0.2),
    (141.289 - 0.2, 100.9758 + 0.2),
]:
    poly.Append(mm(x), mm(y))

# Set zone clearance
gnd_zone.SetLocalClearance(mm(0.20))
gnd_zone.SetMinThickness(mm(0.15))
board.Add(gnd_zone)

# Fill zones
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

board.Save(OUT_PCB)
print("PMW3360 flawless board successfully generated!")
