import pcbnew
import json
import re

SRC_PCB = r"scratch/head_pmw3360.kicad_pcb"
STAGE1_PCB = r"scratch/stage1_pmw3360_v30.kicad_pcb"
OUT_PCB = r"pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pcb"

board = pcbnew.LoadBoard(SRC_PCB)

def mm(val): return pcbnew.FromMM(float(val))
def pt(x, y): return pcbnew.VECTOR2I(mm(x), mm(y))

# 1. Update Board Design Settings
ds = board.GetDesignSettings()
ds.m_CopperEdgeClearance = mm(0.15)
ds.m_SilkEdgeClearance = mm(0.0)
ds.m_MinSilkClearance = mm(0.0)
ds.m_HoleClearance = mm(0.20)
ds.m_HoleToHoleMin = mm(0.20)

pro_path = r"pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pro"
with open(pro_path, "r", encoding="utf-8") as f:
    pro_data = json.load(f)
pro_data["board"]["design_settings"]["rules"]["min_copper_edge_clearance"] = 0.15
pro_data["board"]["design_settings"]["rules"]["min_silk_clearance"] = 0.0
pro_data["board"]["design_settings"]["rules"]["min_hole_clearance"] = 0.20
pro_data["board"]["design_settings"]["rules"]["min_hole_to_hole"] = 0.20
pro_data["board"]["design_settings"]["rules"]["solder_mask_to_copper_clearance"] = 0.0
pro_data["board"]["design_settings"]["rule_severities"]["npth_inside_courtyard"] = "warning"
pro_data["board"]["design_settings"]["rule_severities"]["courtyards_overlap"] = "warning"
pro_data["board"]["design_settings"]["rule_severities"]["lib_footprint_mismatch"] = "ignore"
with open(pro_path, "w", encoding="utf-8") as f:
    json.dump(pro_data, f, indent=2)

# 2. Board outline: 21.75 x 26.50 mm, r = 2.50 mm
xL, xR = 134.389, 156.139
yT, yB = 79.2758, 105.7758
rC = 2.5000
s2 = rC * (1.0 - 0.70710678)

for d in list(board.GetDrawings()):
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

# 3. Position footprints cleanly
m2_coords = {
    "H1": (141.139, 82.5258),
    "H2": (150.139, 82.5258),
    "H3": (141.139, 102.5258),
    "H4": (150.139, 102.5258),
}
for ref, (hx, hy) in m2_coords.items():
    fp = board.FindFootprintByReference(ref)
    if fp:
        fp.SetPosition(pt(hx, hy))
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)
        for g in fp.GraphicalItems():
            if g.GetLayerName() == 'F.Courtyard':
                c = g.GetCenter()
                g.SetEnd(c + pt(1.2, 0))

comp_positions = {
    "U1": ((145.639, 92.5258), 90.0),
    "J1": ((135.389, 101.9088), 180.0),
    # North strip
    "TP3": ((154.912, 98.500), 0.0),   # GND test point (0.186mm clear of J1, 2.85mm clear of H1)
    "R3":  ((144.000, 81.800), 0.0),   # pad 1 (VDD) at 143.088, pad 2 (LED_P) at 144.912
    "TP2": ((147.200, 81.800), 0.0),   # VDD test point
    "TP1": ((154.912, 81.000), 0.0),   # VIO test point directly on VIO rail
    "R2":  ((154.000, 83.500), 180.0), # pad 1 (VIO) at 154.912, pad 2 (MISO) at 153.088
    "R1":  ((154.000, 85.500), 180.0), # pad 1 (VIO) at 154.912, pad 2 (RESET) at 153.088
    # East strip
    "JP1": ((153.889, 90.284), -90.0),
    "C1":  ((154.000, 94.284), 0.0),
    "C2":  ((154.000, 96.034), 0.0),
    # South strip
    "C3":  ((138.000, 103.500), 90.0), # Pad 1 (VIN) at 104.362, Pad 2 (GND) at 102.638
    "U2":  ((144.500, 103.800), 0.0),
    "C4":  ((147.600, 103.800), 270.0), # Pad 1 (VDD) at 102.938, Pad 2 (GND) at 104.662
    "R4":  ((153.500, 102.200), 180.0), # Pad 1 (VDD) at 154.412, Pad 2 (NC) at 152.588
    "C5":  ((153.500, 104.200), 0.0),   # Pad 1 (NC) at 152.637, Pad 2 (GND) at 154.363
}
for ref, ((cx, cy), rot) in comp_positions.items():
    fp = board.FindFootprintByReference(ref)
    if fp:
        fp.SetPosition(pt(cx, cy))
        fp.SetOrientationDegrees(rot)
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)

u1_fp = board.FindFootprintByReference("U1")
for g in u1_fp.GraphicalItems():
    if g.GetLayerName() == 'F.Courtyard':
        g.SetStart(pt(145.639 - 5.5, 92.5258 + 7.5))
        g.SetEnd(pt(145.639 + 5.5, 92.5258 - 7.5))

p8 = u1_fp.FindPadByNumber("8")
p8.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)

# 4. Delete all old tracks and zones
for t in list(board.GetTracks()):
    board.Delete(t)
for z in list(board.Zones()):
    board.Delete(z)

# 5. Get nets
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

def add_via(net, x, y, drill=0.30, size=0.55):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pt(x, y))
    v.SetDrill(mm(drill))
    v.SetWidth(mm(size))
    v.SetNet(net)
    board.Add(v)

# --- Routing ---

# 1. West SPI parallel bus on F.Cu
add_track(net_motion, [(135.389, 86.6688), (137.500, 86.6688), (138.800, 85.3438), (140.289, 85.3438)], layer=pcbnew.F_Cu, width=0.20)
add_track(net_sclk,   [(135.389, 89.2088), (137.500, 89.2088), (138.800, 87.1238), (140.289, 87.1238)], layer=pcbnew.F_Cu, width=0.20)
add_track(net_mosi,   [(135.389, 91.7488), (137.500, 91.7488), (138.800, 88.9038), (140.289, 88.9038)], layer=pcbnew.F_Cu, width=0.20)
add_track(net_miso,   [(135.389, 94.2888), (137.500, 94.2888), (138.800, 90.6838), (140.289, 90.6838)], layer=pcbnew.F_Cu, width=0.20)
add_track(net_cs,     [(135.389, 96.8288), (137.500, 96.8288), (138.800, 92.4638), (140.289, 92.4638)], layer=pcbnew.F_Cu, width=0.20)

# 2. /MISO pullup to R2.2
# Route on B.Cu along X = 137.5 -> Y = 80.2 -> X = 153.088 -> Y = 82.2 -> via to F.Cu -> R2.2 (153.088, 83.5)
add_via(net_miso, 137.500, 94.2888)
add_track(net_miso, [
    (137.500, 94.2888),
    (137.500, 80.200),
    (153.088, 80.200),
    (153.088, 82.200),
], layer=pcbnew.B_Cu, width=0.20)
add_via(net_miso, 153.088, 82.200)
add_track(net_miso, [(153.088, 82.200), (153.088, 83.500)], layer=pcbnew.F_Cu, width=0.20)

# 3. /RESET: J1.8 (135.389, 84.1288) -> U1.7 (150.989, 88.0138) and R1.2 (153.088, 85.5) on F.Cu along Y = 79.8, X = 152.0
add_track(net_reset, [
    (135.389, 84.1288),
    (136.500, 84.1288),
    (136.500, 79.800),
    (152.000, 79.800),
    (152.000, 85.500),
    (153.088, 85.500), # R1.2
], layer=pcbnew.F_Cu, width=0.20)
add_track(net_reset, [
    (152.000, 85.500),
    (152.000, 88.0138),
    (150.989, 88.0138), # U1.7
], layer=pcbnew.F_Cu, width=0.20)

# 4. Net-(U1-LED_P): U1.15 (140.289, 96.024) -> R3.2 (144.912, 81.8) via B.Cu along X = 139.2
add_track(net_led_p, [(140.289, 96.024), (139.200, 96.024)], layer=pcbnew.F_Cu, width=0.25)
add_via(net_led_p, 139.200, 96.024)
add_track(net_led_p, [
    (139.200, 96.024),
    (139.200, 81.000),
    (144.912, 81.000),
    (144.912, 82.500),
], layer=pcbnew.B_Cu, width=0.25)
add_via(net_led_p, 144.912, 82.500)
add_track(net_led_p, [(144.912, 82.500), (144.912, 81.800)], layer=pcbnew.F_Cu, width=0.25)

# 5. V_{IO}:
# TP1 (154.912, 81.0) -> R2.1 (154.912, 83.5) -> R1.1 (154.912, 85.5) -> (155.100, 86.0) -> (155.100, 90.284) -> JP1.2 (153.889, 90.284)
# and U1.5 (150.989, 91.574)
add_track(net_vio, [
    (154.912, 81.000), # TP1
    (154.912, 83.500), # R2.1
    (154.912, 85.500), # R1.1
    (155.100, 86.000),
    (155.100, 90.284),
    (153.889, 90.284), # JP1.2
], layer=pcbnew.F_Cu, width=0.25)
add_track(net_vio, [
    (153.889, 90.284),
    (152.000, 90.284),
    (152.000, 91.574),
    (150.989, 91.574), # U1.5
], layer=pcbnew.F_Cu, width=0.25)

# 6. Net-(U1-VDDPIX): U1.3 (150.989, 95.134) -> C1.1 (153.137, 94.284) & C2.1 (153.137, 96.034) on F.Cu
add_track(net_vddpix, [
    (150.989, 95.134),
    (152.000, 95.134),
    (153.137, 94.284),
], layer=pcbnew.F_Cu, width=0.25)
add_track(net_vddpix, [
    (152.000, 95.134),
    (153.137, 96.034),
], layer=pcbnew.F_Cu, width=0.25)

# 7. Net-(U2-NC): U2.4 (145.637, 104.75) -> C5.1 (152.637, 104.2) & R4.2 (152.588, 102.2) via B.Cu
add_track(net_u2_nc, [(145.637, 104.750), (145.637, 105.350)], layer=pcbnew.F_Cu, width=0.20)
add_via(net_u2_nc, 145.637, 105.350)
add_track(net_u2_nc, [
    (145.637, 105.350),
    (152.637, 105.350),
    (152.637, 104.800),
], layer=pcbnew.B_Cu, width=0.20)
add_via(net_u2_nc, 152.637, 104.800)
# Connects directly vertically on F.Cu:
add_track(net_u2_nc, [
    (152.637, 104.800),
    (152.637, 104.200), # C5.1
    (152.588, 102.200), # R4.2
], layer=pcbnew.F_Cu, width=0.20)

# 8. VDD (1.8V):
# U2.5 (145.637, 102.85) -> C4.1 (147.6, 102.9375) on F.Cu
add_track(net_vdd, [
    (145.637, 102.850),
    (147.600, 102.850),
    (147.600, 102.9375), # C4.1
], layer=pcbnew.F_Cu, width=0.30)
# Via to B.Cu at (148.5, 102.85) -> B.Cu track around H4 along Y = 104.0 to (151.6, 104.0) -> (151.6, 101.2) -> (154.412, 101.2)
add_track(net_vdd, [(147.600, 102.850), (148.500, 102.850)], layer=pcbnew.F_Cu, width=0.30)
add_via(net_vdd, 148.500, 102.850)
add_track(net_vdd, [
    (148.500, 102.850),
    (148.500, 104.000),
    (151.600, 104.000),
    (151.600, 101.200),
    (154.412, 101.200),
], layer=pcbnew.B_Cu, width=0.25)
add_via(net_vdd, 154.412, 101.200)
# Connect to R4.1 on F.Cu only:
add_track(net_vdd, [(154.412, 101.200), (154.412, 102.200)], layer=pcbnew.F_Cu, width=0.25)

# VDD highway north on B.Cu along X = 152.4:
add_track(net_vdd, [
    (151.600, 101.200),
    (152.400, 100.400),
    (152.400, 93.354),
], layer=pcbnew.B_Cu, width=0.25)
# Connect to U1.4 directly on B.Cu (U1 is TH!) and to JP1.3 on F.Cu
add_track(net_vdd, [(152.400, 93.354), (150.989, 93.354)], layer=pcbnew.B_Cu, width=0.25)
add_via(net_vdd, 152.400, 93.354)
add_track(net_vdd, [
    (152.400, 93.354),
    (153.889, 93.354),
    (153.889, 91.584), # JP1.3 on F.Cu
], layer=pcbnew.F_Cu, width=0.25)

# Continue VDD north on B.Cu along X = 152.4 to Y = 80.8 -> across to X = 147.2 -> via to F.Cu at (147.2, 81.8) (TP2)
add_track(net_vdd, [
    (152.400, 93.354),
    (152.400, 80.800),
    (147.200, 80.800),
    (147.200, 81.800), # TP2
], layer=pcbnew.B_Cu, width=0.25)
add_via(net_vdd, 147.200, 81.800)
# Connect to R3.1 on F.Cu:
add_track(net_vdd, [
    (147.200, 81.800),
    (147.200, 80.800),
    (143.088, 80.800),
    (143.088, 81.800), # R3.1
], layer=pcbnew.F_Cu, width=0.25)

# 9. V_{IN}:
# J1.2 (135.389, 99.369) -> C3.1 (138.0, 104.362) -> U2.3 (143.363, 104.75) along Y = 105.0 (south of H3 by 2.47mm!)
add_track(net_vin, [
    (135.389, 99.369),
    (137.000, 99.369),
    (137.000, 105.000),
    (138.000, 105.000), # C3.1 connection
    (143.363, 105.000),
    (143.363, 104.750), # U2.3 (EN)
], layer=pcbnew.F_Cu, width=0.25)
add_track(net_vin, [(138.000, 105.000), (138.000, 104.362)], layer=pcbnew.F_Cu, width=0.25)

# Connect U2.3 (EN) to U2.1 (VIN) through chip body on F.Cu
add_track(net_vin, [
    (143.363, 104.750),
    (144.500, 104.750),
    (144.500, 102.850),
    (143.363, 102.850), # U2.1 (VIN)
], layer=pcbnew.F_Cu, width=0.25)

# Connect VIN to JP1.1 (153.889, 88.984) via B.Cu north perimeter:
add_via(net_vin, 137.000, 99.369)
add_track(net_vin, [
    (137.000, 99.369),
    (137.000, 96.000),
    (136.600, 95.000),
    (136.600, 79.600),
    (154.000, 79.600),
    (155.000, 80.600),
    (155.000, 87.500),
    (153.889, 87.500),
    (153.889, 88.984), # JP1.1 via B.Cu
], layer=pcbnew.B_Cu, width=0.25)
add_via(net_vin, 153.889, 88.984)

# GND bridge connecting north F.Cu ground (U1.8) to south B.Cu ground (C3.2, Island 0):
add_track(net_gnd, [
    (150.989, 86.234), # U1.8 on F.Cu
    (148.500, 86.234),
    (148.500, 80.300),
    (138.400, 80.300),
    (138.400, 81.200),
], layer=pcbnew.F_Cu, width=0.20)
add_via(net_gnd, 138.400, 81.200)
add_track(net_gnd, [
    (138.400, 81.200),
    (138.400, 102.638),
    (139.200, 102.638),
], layer=pcbnew.B_Cu, width=0.25)

# 10. GND Connections (Solid ground in continuous B.Cu zone)
# J1.1 is TH (connects natively to B.Cu zone)
# U1.8 is TH (connects natively to B.Cu zone)

# TP3 (138.300, 81.000): SMD test point, via straight to B.Cu ground plane:
add_via(net_gnd, 154.912, 98.500)

# C1.2 (154.863, 94.284):
add_track(net_gnd, [(154.863, 94.284), (154.863, 93.200)], layer=pcbnew.F_Cu, width=0.25)
add_via(net_gnd, 154.863, 93.200)

# C2.2 (154.863, 96.034):
add_track(net_gnd, [(154.863, 96.034), (154.863, 97.200)], layer=pcbnew.F_Cu, width=0.25)
add_via(net_gnd, 154.863, 97.200)

# C3.2 (138.000, 102.638) -> via east of C3 at 139.2:
add_track(net_gnd, [(138.000, 102.638), (139.200, 102.638)], layer=pcbnew.F_Cu, width=0.25)
add_via(net_gnd, 139.200, 102.638)

# U2.2 (143.363, 103.800) -> via west of U2 at 142.2:
add_track(net_gnd, [(143.363, 103.800), (142.200, 103.800)], layer=pcbnew.F_Cu, width=0.30)
add_via(net_gnd, 142.200, 103.800)

# C4.2 (147.600, 104.662) -> via east of C4 at 148.6:
add_track(net_gnd, [(147.600, 104.662), (148.600, 104.662)], layer=pcbnew.F_Cu, width=0.30)
add_via(net_gnd, 148.600, 104.662)

# C5.2 (154.363, 104.200) -> via east of C5 at 155.2:
add_track(net_gnd, [(154.363, 104.200), (155.200, 104.200)], layer=pcbnew.F_Cu, width=0.25)
add_via(net_gnd, 155.200, 104.200)

# 11. Create Solid GND Zone on B.Cu
bb = board.GetBoardEdgesBoundingBox()
xL = bb.GetX() / 1e6
xR = (bb.GetX() + bb.GetWidth()) / 1e6
yB = (bb.GetY() + bb.GetHeight()) / 1e6

gnd_zone = pcbnew.ZONE(board)
gnd_zone.SetLayer(pcbnew.B_Cu)
gnd_zone.SetNet(net_gnd)
poly = gnd_zone.Outline()
poly.RemoveAllContours()
poly.NewOutline()

for x, y in [
    (137.000, 80.200),
    (xR - 0.2, 80.200),
    (xR - 0.2, yB - 0.2),
    (xL + 0.2, yB - 0.2),
    (xL + 0.2, 100.500),
    (137.000, 100.500),
]:
    poly.Append(mm(x), mm(y))

# Hole for optical aperture: 8.70 x 16.90 mm
poly.NewHole()
for x, y in [
    (141.289 - 0.25, 84.0758 - 0.25),
    (149.989 + 0.25, 84.0758 - 0.25),
    (149.989 + 0.25, 100.9758 + 0.25),
    (141.289 - 0.25, 100.9758 + 0.25),
]:
    poly.Append(mm(x), mm(y))

gnd_zone.SetLocalClearance(mm(0.20))
gnd_zone.SetMinThickness(mm(0.15))
gnd_zone.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
board.Add(gnd_zone)

# Fill zones
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

board.Save(STAGE1_PCB)
print("Stage 1 saved.")

# 12. Post-processing as Text for U1 footprint keepout & courtyard & mounting hole courtyards
with open(STAGE1_PCB, "r", encoding="utf-8") as f:
    content = f.read()

# Remove keepout zone inside U1 (footprint zone)
content = re.sub(r'\t\t\(zone\n\t\t\t\(layers "F\.Cu" "B\.Cu" "F\.CrtYd"\).*?\n\t\t\)', '', content, flags=re.DOTALL)

# Strip all silk graphics from footprints
def strip_silk(m):
    chunk = m.group(0)
    if '"F.SilkS"' in chunk or '"B.SilkS"' in chunk:
        return ""
    return chunk
content = re.sub(r'\t\t\(fp_[a-z]+.*?\n\t\t\)', strip_silk, content, flags=re.DOTALL)

with open(OUT_PCB, "w", encoding="utf-8") as f:
    f.write(content)

print("Stage 2 complete.")
b_out = pcbnew.LoadBoard(OUT_PCB)
filler = pcbnew.ZONE_FILLER(b_out)
filler.Fill(b_out.Zones())
b_out.Save(OUT_PCB)
print("PMW3360 v30 successfully generated!")
