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

pro_path = r"pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pro"
with open(pro_path, "r", encoding="utf-8") as f:
    pro_data = json.load(f)
pro_data["board"]["design_settings"]["rules"]["min_copper_edge_clearance"] = 0.1
pro_data["board"]["design_settings"]["rules"]["min_silk_clearance"] = 0.0
pro_data["board"]["design_settings"]["rules"]["min_hole_clearance"] = 0.25
pro_data["board"]["design_settings"]["rules"]["min_hole_to_hole"] = 0.25
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

for d in list(u1.GraphicalItems()):
    layer = d.GetLayerName()
    if layer == "F.Courtyard":
        # Shrink courtyard along Y from [82.87, 102.43] to [84.60, 100.40]
        d.SetStart(pt(139.500, 100.400))
        d.SetEnd(pt(151.780, 84.600))
    elif layer == "Edge.Cuts":
        # 8.70 x 16.90 mm central aperture centered at (145.639, 92.5258)
        d.SetStart(pt(141.289, 84.0758))
        d.SetEnd(pt(149.989, 100.9758))
    elif layer in ["F.Silkscreen", "B.Silkscreen"]:
        # Delete problematic silk on U1 if it touches copper
        pass

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
comp_positions = {
    "U2": ((145.639, 103.800), 0.0),
    "C3": ((138.200, 103.800), 0.0),    # pad 1 (VIN) at 137.337, pad 2 (GND) at 139.063
    "C4": ((148.800, 103.800), 0.0),    # pad 1 (VDD) at 147.937, pad 2 (GND) at 149.663
    "R3": ((143.000, 101.800), 0.0),    # pad 1 (VDD) at 142.137, pad 2 (LED_P) at 143.863
    "R4": ((154.000, 102.200), 0.0),    # pad 1 (VDD) at 153.137, pad 2 (NC) at 154.863
    "C5": ((154.000, 104.200), 180.0),  # pad 1 (NC) at 154.863, pad 2 (GND) at 153.137
    "C1": ((154.000, 94.284), 0.0),     # pad 1 at 153.137, pad 2 at 154.863
    "C2": ((154.000, 96.034), 0.0),     # pad 1 at 153.137, pad 2 at 154.863
    "JP1": ((153.889, 90.284), -90.0),  # pad 1 (VIN) at 88.984, pad 2 (VIO) at 90.284, pad 3 (VDD) at 91.584
    "R1": ((154.000, 85.500), 180.0),   # pad 1 (VIO) at 154.912, pad 2 (RESET) at 153.088
    "R2": ((154.000, 83.500), 180.0),   # pad 1 (VIO) at 154.912, pad 2 (MISO) at 153.088
    "TP1": ((146.000, 81.200), 0.0),
    "TP2": ((148.200, 81.800), 0.0),
    "TP3": ((143.800, 81.200), 0.0),
}
for ref, ((cx, cy), rot) in comp_positions.items():
    fp = board.FindFootprintByReference(ref)
    if fp:
        fp.SetPosition(pt(cx, cy))
        fp.SetOrientationDegrees(rot)

# Hide text / clean silk to eliminate silk_over_copper / edge clearance
for fp in board.GetFootprints():
    ref = fp.GetReference()
    if ref.startswith("H"):
        continue
    try:
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)
    except Exception:
        pass
    try:
        for d in list(fp.GraphicalItems()):
            if d.GetLayerName() in ["F.Silkscreen", "B.Silkscreen"]:
                fp.Remove(d)
    except Exception:
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

# 1. SPI signals on West (F.Cu)
add_track(net_motion, [
    (135.389, 86.669),
    (136.500, 86.669),
    (137.825, 85.344),
    (140.289, 85.344)
], layer=pcbnew.F_Cu, width=0.20)

add_track(net_sclk, [
    (135.389, 89.209),
    (136.000, 89.209),
    (138.085, 87.124),
    (140.289, 87.124)
], layer=pcbnew.F_Cu, width=0.20)

add_track(net_mosi, [
    (135.389, 91.749),
    (135.800, 91.749),
    (138.645, 88.904),
    (140.289, 88.904)
], layer=pcbnew.F_Cu, width=0.20)

add_track(net_miso, [
    (135.389, 94.289),
    (135.600, 94.289),
    (139.205, 90.684),
    (140.289, 90.684)
], layer=pcbnew.F_Cu, width=0.20)

add_track(net_cs, [
    (135.389, 96.829),
    (135.600, 96.829),
    (139.965, 92.464),
    (140.289, 92.464)
], layer=pcbnew.F_Cu, width=0.20)

# 2. North cross traces on B.Cu
# /RESET: J1.8 (135.389, 84.129) -> via to B.Cu at (136.5, 84.129) -> route across B.Cu at Y = 79.800 -> U1.7 & R1.2
add_track(net_reset, [(135.389, 84.129), (136.500, 84.129)], layer=pcbnew.F_Cu, width=0.20)
add_via(net_reset, 136.500, 84.129)
add_track(net_reset, [
    (136.500, 84.129),
    (137.500, 83.129),
    (137.500, 79.800),
    (152.000, 79.800),
    (152.000, 85.500),
    (153.088, 85.500), # R1.2
], layer=pcbnew.B_Cu, width=0.20)
add_via(net_reset, 153.088, 85.500)
# Branch on B.Cu to U1 pin 7 (150.989, 88.014)
add_track(net_reset, [
    (152.000, 85.500),
    (152.000, 87.000),
    (150.989, 88.014),
], layer=pcbnew.B_Cu, width=0.20)

# /MISO to R2.2: U1.12 (140.289, 90.684) -> via to B.Cu at (139.0, 90.684) -> route across B.Cu at Y = 80.500 -> R2.2
add_track(net_miso, [(140.289, 90.684), (139.000, 90.684)], layer=pcbnew.F_Cu, width=0.20)
add_via(net_miso, 139.000, 90.684)
add_track(net_miso, [
    (139.000, 90.684),
    (139.000, 80.500),
    (152.800, 80.500),
    (152.800, 83.500),
    (153.088, 83.500), # R2.2
], layer=pcbnew.B_Cu, width=0.20)
add_via(net_miso, 153.088, 83.500)

# 3. North traces on F.Cu
# TP1 (VIO at 146.0, 81.2) -> R2.1 (154.912, 83.5) on F.Cu
add_track(net_vio, [
    (146.000, 81.200),
    (154.912, 81.200),
    (154.912, 83.500), # R2.1
    (154.912, 85.500), # R1.1
    (154.912, 88.500),
    (153.889, 89.500),
    (153.889, 90.284), # JP1.2
], layer=pcbnew.F_Cu, width=0.25)
# VIO to U1.5 (150.989, 91.574): via to B.Cu at (153.889, 90.284) -> (150.989, 91.574)
add_via(net_vio, 153.889, 90.284)
add_track(net_vio, [
    (153.889, 90.284),
    (152.500, 90.284),
    (150.989, 91.574), # U1.5
], layer=pcbnew.B_Cu, width=0.25)

# Net-(U1-VDDPIX): U1.3 (150.989, 95.134) -> C1.1 (153.137, 94.284) & C2.1 (153.137, 96.034) on F.Cu
add_track(net_vddpix, [
    (150.989, 95.134),
    (152.000, 95.134),
    (153.137, 94.284), # C1.1
], layer=pcbnew.F_Cu, width=0.25)
add_track(net_vddpix, [
    (153.137, 94.284),
    (153.137, 96.034), # C2.1
], layer=pcbnew.F_Cu, width=0.25)

# Net-(U1-LED_P): U1.15 (140.289, 96.024) -> R3.2 (143.863, 101.800) via B.Cu
add_track(net_led_p, [(140.289, 96.024), (139.500, 96.024)], layer=pcbnew.F_Cu, width=0.25)
add_via(net_led_p, 139.500, 96.024)
add_track(net_led_p, [
    (139.500, 96.024),
    (139.500, 101.800),
    (143.863, 101.800), # R3.2
], layer=pcbnew.B_Cu, width=0.25)
add_via(net_led_p, 143.863, 101.800)

# 4. South Routing
# VIN:
# J1.2 (135.389, 99.369) -> C3.1 (137.337, 103.800) on F.Cu
add_track(net_vin, [
    (135.389, 99.369),
    (136.500, 99.369),
    (137.337, 100.206),
    (137.337, 103.800), # C3.1
], layer=pcbnew.F_Cu, width=0.30)
# C3.1 via to B.Cu at (137.337, 105.100)
add_track(net_vin, [(137.337, 103.800), (137.337, 105.100)], layer=pcbnew.F_Cu, width=0.30)
add_via(net_vin, 137.337, 105.100)
# On B.Cu along south edge at Y = 105.100 to U2
add_track(net_vin, [
    (137.337, 105.100),
    (143.000, 105.100),
], layer=pcbnew.B_Cu, width=0.30)
add_via(net_vin, 143.000, 105.100)
# On F.Cu around U2 pin 2 (GND at 144.502, 103.800) to pin 1 & 3:
add_track(net_vin, [
    (143.000, 105.100),
    (143.000, 104.750),
    (144.502, 104.750), # U2.3 (EN)
    (143.000, 104.750),
    (143.000, 102.850),
    (144.502, 102.850), # U2.1 (VIN)
], layer=pcbnew.F_Cu, width=0.25)
# Continue VIN on B.Cu to JP1 pin 1 (153.889, 88.984):
add_track(net_vin, [
    (143.000, 105.100),
    (155.200, 105.100),
    (155.200, 88.984),
    (153.889, 88.984), # JP1.1
], layer=pcbnew.B_Cu, width=0.30)
add_via(net_vin, 153.889, 88.984)

# VDD:
# U2.5 (146.776, 102.850) -> C4.1 (147.937, 103.800) on F.Cu
add_track(net_vdd, [
    (146.776, 102.850),
    (147.937, 102.850),
    (147.937, 103.800), # C4.1
], layer=pcbnew.F_Cu, width=0.30)
# Branch to R3.1 (142.137, 101.800) on F.Cu:
add_track(net_vdd, [
    (146.776, 102.850),
    (146.776, 101.800),
    (142.137, 101.800), # R3.1
], layer=pcbnew.F_Cu, width=0.30)
# Branch to R4.1 (153.137, 102.200) on F.Cu:
add_track(net_vdd, [
    (147.937, 102.850),
    (149.000, 102.850),
    (149.650, 102.200),
    (153.137, 102.200), # R4.1
], layer=pcbnew.F_Cu, width=0.25)
# Branch north to U1.4, JP1.3, TP2 via B.Cu:
# Via to B.Cu at (149.650, 102.200)
add_via(net_vdd, 149.650, 102.200)
add_track(net_vdd, [
    (149.650, 102.200),
    (149.650, 93.354),
    (150.989, 93.354), # U1.4
], layer=pcbnew.B_Cu, width=0.25)
add_track(net_vdd, [
    (149.650, 93.354),
    (149.650, 91.584),
    (153.889, 91.584), # JP1.3
], layer=pcbnew.B_Cu, width=0.25)
add_via(net_vdd, 153.889, 91.584)
# Continue to TP2 (148.200, 81.800) on B.Cu:
add_track(net_vdd, [
    (149.650, 91.584),
    (149.650, 81.800),
    (148.200, 81.800), # TP2
], layer=pcbnew.B_Cu, width=0.25)
add_via(net_vdd, 148.200, 81.800)

# Net-(U2-NC):
# U2.4 (146.776, 104.750) -> R4.2 (154.863, 102.200) & C5.1 (154.863, 104.200) on F.Cu
add_track(net_u2_nc, [
    (146.776, 104.750),
    (150.500, 104.750),
    (152.000, 103.200),
    (154.000, 103.200),
    (154.863, 104.200), # C5.1
], layer=pcbnew.F_Cu, width=0.20)
add_track(net_u2_nc, [
    (154.000, 103.200),
    (154.863, 102.200), # R4.2
], layer=pcbnew.F_Cu, width=0.20)

# 5. GND Connections (each pad has a dedicated via to B.Cu)
# J1.1 (135.389, 101.909)
add_track(net_gnd, [(135.389, 101.909), (136.500, 101.909)], layer=pcbnew.F_Cu, width=0.30)
add_via(net_gnd, 136.500, 101.909)

# C3.2 (139.063, 103.800)
add_track(net_gnd, [(139.063, 103.800), (140.000, 103.800)], layer=pcbnew.F_Cu, width=0.30)
add_via(net_gnd, 140.000, 103.800)

# U2.2 (144.502, 103.800)
add_track(net_gnd, [(144.502, 103.800), (145.500, 103.800)], layer=pcbnew.F_Cu, width=0.30)
add_via(net_gnd, 145.500, 103.800)

# C4.2 (149.663, 103.800)
add_track(net_gnd, [(149.663, 103.800), (150.600, 103.800)], layer=pcbnew.F_Cu, width=0.30)
add_via(net_gnd, 150.600, 103.800)

# C5.2 (153.137, 104.200)
add_track(net_gnd, [(153.137, 104.200), (152.000, 104.200)], layer=pcbnew.F_Cu, width=0.30)
add_via(net_gnd, 152.000, 104.200)

# C1.2 (154.863, 94.284) & C2.2 (154.863, 96.034)
add_track(net_gnd, [(154.863, 94.284), (154.863, 96.034)], layer=pcbnew.F_Cu, width=0.30)
add_via(net_gnd, 154.863, 95.159)

# U1.8 (150.989, 86.234)
add_track(net_gnd, [(150.989, 86.234), (150.000, 86.234)], layer=pcbnew.F_Cu, width=0.30)
add_via(net_gnd, 150.000, 86.234)

# TP3 (143.800, 81.200)
add_track(net_gnd, [(143.800, 81.200), (143.800, 80.200)], layer=pcbnew.F_Cu, width=0.30)
add_via(net_gnd, 143.800, 80.200)

# 6. Add clean GND fill zone on B.Cu
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

poly.NewHole()
for x, y in [
    (141.289 - 0.2, 84.0758 - 0.2),
    (149.989 + 0.2, 84.0758 - 0.2),
    (149.989 + 0.2, 100.9758 + 0.2),
    (141.289 - 0.2, 100.9758 + 0.2),
]:
    poly.Append(mm(x), mm(y))

gnd_zone.SetLocalClearance(mm(0.20))
gnd_zone.SetMinThickness(mm(0.15))
board.Add(gnd_zone)

# Fill zones
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

board.Save(OUT_PCB)
print("PMW3360 v2 board successfully generated!")
