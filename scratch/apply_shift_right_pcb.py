# -*- coding: utf-8 -*-
import pcbnew
import math
from pathlib import Path

PCB_PATH = Path(r"pcbs/curcur40/right/curcur40-right.kicad_pcb")
board = pcbnew.LoadBoard(str(PCB_PATH))

edge_layer = board.GetLayerID("Edge.Cuts")
b_cu = board.GetLayerID("B.Cu")
f_cu = board.GetLayerID("F.Cu")

# Shift trackball center by +2.0 mm: from 7.525 to 9.525
cx_old, cy = 7.525, 52.3875
dx = 2.000
cx_new = cx_old + dx  # 9.525

print(f"Shifting trackball center from {cx_old:.3f} to {cx_new:.3f}")

# 1. Update central cutout circle on Edge.Cuts
for dr in board.GetDrawings():
    if dr.GetLayer() == edge_layer and dr.GetShapeStr() == "Circle":
        c = dr.GetCenter()
        if abs(pcbnew.ToMM(c.x) - cx_old) < 0.2 and abs(pcbnew.ToMM(c.y) - cy) < 0.2:
            dr.SetCenter(pcbnew.VECTOR2I(pcbnew.FromMM(cx_new), pcbnew.FromMM(cy)))
            dr.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(cx_new + 5.0), pcbnew.FromMM(cy)))
            print("Shifted central circle cutout")

# 2. Update 4x M2 mounting holes
hole_defs = [
    ("rH1", cx_new - 4.5, cy - 10.0), # (5.025, 42.3875)
    ("rH2", cx_new + 4.5, cy - 10.0), # (14.025, 42.3875)
    ("rH3", cx_new - 4.5, cy + 10.0), # (5.025, 62.3875)
    ("rH4", cx_new + 4.5, cy + 10.0), # (14.025, 62.3875)
]

for ref, hx, hy in hole_defs:
    fp = board.FindFootprintByReference(ref)
    if fp:
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(hx), pcbnew.FromMM(hy)))
        for pad in fp.Pads():
            pad.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(hx), pcbnew.FromMM(hy)))
        print(f"Shifted mounting hole {ref} to ({hx:.3f}, {hy:.3f})")

# 3. Update Edge.Cuts tab:
# Old tab:
# - Bottom line: (-4.263, 67.500) -> (18.500, 67.500)
# - Chamfer line: (18.500, 67.500) -> (22.8375, 63.1625)
# - Bottom line: (22.8375, 63.1625) -> (81.463, 63.1625)
# With +2mm shift:
# - Bottom line: (-4.263, 67.500) -> (20.500, 67.500)
# - Chamfer line: (20.500, 67.500) -> (24.8375, 63.1625)
# - Bottom line: (24.8375, 63.1625) -> (81.463, 63.1625)

to_remove_draw = []
for dr in board.GetDrawings():
    if dr.GetLayer() == edge_layer and dr.GetShapeStr() in ["Line", "Segment"]:
        s, e = dr.GetStart(), dr.GetEnd()
        sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
        ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)
        # Tab bottom line
        if abs(sy - 67.500) < 0.1 and abs(ey - 67.500) < 0.1:
            to_remove_draw.append(dr)
        # Chamfer line
        elif (abs(sy - 67.500) < 0.1 or abs(ey - 67.500) < 0.1) and (abs(sy - 63.1625) < 0.1 or abs(ey - 63.1625) < 0.1):
            to_remove_draw.append(dr)
        # Bottom line
        elif abs(sy - 63.1625) < 0.1 and abs(ey - 63.1625) < 0.1 and (min(sx, ex) < 30.0):
            to_remove_draw.append(dr)

for dr in to_remove_draw:
    board.Remove(dr)

def add_edge_line(x1, y1, x2, y2, width=0.15):
    line = pcbnew.PCB_SHAPE(board)
    line.SetShape(pcbnew.SHAPE_T_SEGMENT)
    line.SetLayer(edge_layer)
    line.SetWidth(pcbnew.FromMM(width))
    line.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
    line.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
    board.Add(line)
    return line

add_edge_line(-4.263, 67.500, 20.500, 67.500)
add_edge_line(20.500, 67.500, 24.8375, 63.1625)
add_edge_line(24.8375, 63.1625, 81.463, 63.1625)
print("Updated Edge.Cuts tab (+2mm shift)")

# 4. Update /TX trace near rH2 (14.025, 42.3875)
# Shift the 45 deg turn point to X=17.500
tracks_to_remove = []
for tr in board.GetTracks():
    if tr.GetClass() != "PCB_TRACK":
        continue
    net = tr.GetNetname()
    layer = tr.GetLayer()
    s, e = tr.GetStart(), tr.GetEnd()
    sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
    ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)
    
    if net == "/TX" and layer == b_cu:
        if (38.0 <= sy <= 43.0 and 38.0 <= ey <= 43.0) and (min(sx, ex) < 18.0):
            tracks_to_remove.append(tr)
            
    if net in ["+3V3R", "/SCLK", "/MOSI", "/MISO"] and layer == b_cu:
        # Remove east slanted and tab horizontal segments to shift east bend by +2mm
        if (sy > 60.0 or ey > 60.0) and (min(sx, ex) < 25.0):
            tracks_to_remove.append(tr)

for tr in tracks_to_remove:
    board.Remove(tr)

def add_track(netname, layer_id, x1, y1, x2, y2, width=0.2):
    t = pcbnew.PCB_TRACK(board)
    t.SetLayer(layer_id)
    t.SetWidth(pcbnew.FromMM(width))
    t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
    t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
    netinfo = board.FindNet(netname)
    if netinfo:
        t.SetNet(netinfo)
    board.Add(t)
    return t

# Reroute /TX on B.Cu:
# (23.575, 42.416) -> (17.500, 42.416) -> 45 deg to (13.630, 38.546) -> horiz to (10.268, 38.546)
add_track("/TX", b_cu, 23.575, 42.416, 17.500, 42.416, width=0.2)
add_track("/TX", b_cu, 17.500, 42.416, 13.630, 38.546, width=0.2)
add_track("/TX", b_cu, 13.630, 38.546, 10.268, 38.546, width=0.2)

# Reroute 4 SPI lines on B.Cu with east bend shifted right by +2.0 mm:
y_tabs = {
    "+3V3R": 64.200,
    "/SCLK": 64.800,
    "/MOSI": 65.400,
    "/MISO": 66.000
}

x_bend_east = {
    "+3V3R": 20.000,
    "/SCLK": 20.000 + (64.800 - 64.200),  # 20.600
    "/MOSI": 20.000 + (65.400 - 64.200),  # 21.200
    "/MISO": 20.000 + (66.000 - 64.200)   # 21.800
}

# +3V3R:
add_track("+3V3R", b_cu, 63.800, 60.712, x_bend_east["+3V3R"], 60.712, width=0.2)
corner_x_3v3 = x_bend_east["+3V3R"] - (y_tabs["+3V3R"] - 60.712)
add_track("+3V3R", b_cu, x_bend_east["+3V3R"], 60.712, corner_x_3v3, y_tabs["+3V3R"], width=0.2)
add_track("+3V3R", b_cu, corner_x_3v3, y_tabs["+3V3R"], 1.200, y_tabs["+3V3R"], width=0.2)
add_track("+3V3R", b_cu, 1.200, y_tabs["+3V3R"], 1.200, 60.712, width=0.2)

# /SCLK:
add_track("/SCLK", b_cu, 78.300, 61.263, x_bend_east["/SCLK"], 61.263, width=0.2)
corner_x_sclk = x_bend_east["/SCLK"] - (y_tabs["/SCLK"] - 61.263)
add_track("/SCLK", b_cu, x_bend_east["/SCLK"], 61.263, corner_x_sclk, y_tabs["/SCLK"], width=0.2)
add_track("/SCLK", b_cu, corner_x_sclk, y_tabs["/SCLK"], 0.000, y_tabs["/SCLK"], width=0.2)
add_track("/SCLK", b_cu, 0.000, y_tabs["/SCLK"], 0.000, 49.071, width=0.2)
add_track("/SCLK", b_cu, 0.000, 49.071, -2.725, 49.071, width=0.2)

# /MOSI:
add_track("/MOSI", b_cu, 78.950, 61.812, x_bend_east["/MOSI"], 61.812, width=0.2)
corner_x_mosi = x_bend_east["/MOSI"] - (y_tabs["/MOSI"] - 61.812)
add_track("/MOSI", b_cu, x_bend_east["/MOSI"], 61.812, corner_x_mosi, y_tabs["/MOSI"], width=0.2)
add_track("/MOSI", b_cu, corner_x_mosi, y_tabs["/MOSI"], -0.500, y_tabs["/MOSI"], width=0.2)
add_track("/MOSI", b_cu, -0.500, y_tabs["/MOSI"], -0.500, 51.611, width=0.2)
add_track("/MOSI", b_cu, -0.500, 51.611, -2.725, 51.611, width=0.2)

# /MISO:
add_track("/MISO", b_cu, 79.600, 62.362, x_bend_east["/MISO"], 62.362, width=0.2)
corner_x_miso = x_bend_east["/MISO"] - (y_tabs["/MISO"] - 62.362)
add_track("/MISO", b_cu, x_bend_east["/MISO"], 62.362, corner_x_miso, y_tabs["/MISO"], width=0.2)
add_track("/MISO", b_cu, corner_x_miso, y_tabs["/MISO"], -1.000, y_tabs["/MISO"], width=0.2)
add_track("/MISO", b_cu, -1.000, y_tabs["/MISO"], -1.000, 54.151, width=0.2)
add_track("/MISO", b_cu, -1.000, 54.151, -2.725, 54.151, width=0.2)

print("Tracks rerouted")

# Refill zones
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())
print("Zones refilled")

board.Save(str(PCB_PATH))
print(f"Saved: {PCB_PATH}")
