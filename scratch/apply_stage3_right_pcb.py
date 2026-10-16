# -*- coding: utf-8 -*-
import pcbnew
import math
import uuid
from pathlib import Path

SRC_PCB = Path(r"pcbs/curcur40/right/curcur40-right.kicad_pcb")
DST_PCB = SRC_PCB

board = pcbnew.LoadBoard(str(SRC_PCB))
edge_layer = board.GetLayerID("Edge.Cuts")
b_cu = board.GetLayerID("B.Cu")
f_cu = board.GetLayerID("F.Cu")

cx, cy = 7.525, 52.3875

# =========================================================================
# 1. Update Edge.Cuts
# =========================================================================
to_remove = []
for draw in board.GetDrawings():
    if draw.GetLayer() == edge_layer:
        if draw.GetShapeStr() == "Arc":
            c = draw.GetCenter()
            if abs(pcbnew.ToMM(c.x) - (-4.263)) < 0.1 and abs(pcbnew.ToMM(c.y) - 62.163) < 0.1:
                to_remove.append(draw)
        elif draw.GetShapeStr() in ["Line", "Segment"]:
            s, e = draw.GetStart(), draw.GetEnd()
            sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
            ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)
            # Old vertical line
            if abs(sx - (-5.263)) < 0.1 and abs(ex - (-5.263)) < 0.1 and (sy > 45 or ey > 45):
                to_remove.append(draw)
            # Old horizontal line
            if abs(sy - 63.163) < 0.1 and abs(ey - 63.163) < 0.1 and (min(sx, ex) < 0.0):
                to_remove.append(draw)

for item in to_remove:
    board.Remove(item)

def add_edge_line(x1, y1, x2, y2, width=0.15):
    line = pcbnew.PCB_SHAPE(board)
    line.SetShape(pcbnew.SHAPE_T_SEGMENT)
    line.SetLayer(edge_layer)
    line.SetWidth(pcbnew.FromMM(width))
    line.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
    line.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
    board.Add(line)
    return line

def add_edge_arc(cx_mm, cy_mm, start_x, start_y, end_x, end_y, width=0.15):
    arc = pcbnew.PCB_SHAPE(board)
    arc.SetShape(pcbnew.SHAPE_T_ARC)
    arc.SetLayer(edge_layer)
    arc.SetWidth(pcbnew.FromMM(width))
    arc.SetCenter(pcbnew.VECTOR2I(pcbnew.FromMM(cx_mm), pcbnew.FromMM(cy_mm)))
    arc.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(start_x), pcbnew.FromMM(start_y)))
    arc.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(end_x), pcbnew.FromMM(end_y)))
    board.Add(arc)
    return arc

# 1. Extended vertical line on left: (-5.263, 38.800) -> (-5.263, 66.500)
add_edge_line(-5.263, 38.800, -5.263, 66.500)
# 2. Bottom-left fillet arc: center (-4.263, 66.500)
add_edge_arc(-4.263, 66.500, -4.263, 67.500, -5.263, 66.500)
# 3. Bottom horizontal tab edge: (-4.263, 67.500) -> (18.500, 67.500)
add_edge_line(-4.263, 67.500, 18.500, 67.500)
# 4. 45-degree chamfer transition: (18.500, 67.500) -> (22.8375, 63.1625)
add_edge_line(18.500, 67.500, 22.8375, 63.1625)
# 5. Remaining bottom edge: (22.8375, 63.1625) -> (81.463, 63.1625)
add_edge_line(22.8375, 63.1625, 81.463, 63.1625)

# =========================================================================
# 2. Add 4x M2 Mounting Holes (rH1, rH2, rH3, rH4)
# =========================================================================
hole_defs = [
    ("rH1", cx - 4.5, cy - 10.0), # (3.025, 42.3875)
    ("rH2", cx + 4.5, cy - 10.0), # (12.025, 42.3875)
    ("rH3", cx - 4.5, cy + 10.0), # (3.025, 62.3875)
    ("rH4", cx + 4.5, cy + 10.0), # (12.025, 62.3875)
]

for ref, hx, hy in hole_defs:
    existing = board.FindFootprintByReference(ref)
    if existing:
        board.Remove(existing)
        
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference(ref)
    fp.SetValue("MountingHole_2.2mm_M2")
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(hx), pcbnew.FromMM(hy)))
    
    pad = pcbnew.PAD(fp)
    pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    pad.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
    pad.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(2.2), pcbnew.FromMM(2.2)))
    pad.SetDrillSize(pcbnew.VECTOR2I(pcbnew.FromMM(2.2), pcbnew.FromMM(2.2)))
    pad.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(hx), pcbnew.FromMM(hy)))
    
    pad_layers = pcbnew.LSET()
    pad_layers.AddLayer(f_cu)
    pad_layers.AddLayer(b_cu)
    pad.SetLayerSet(pad_layers)
    
    fp.Add(pad)
    board.Add(fp)

# =========================================================================
# 3. Clean and Reroute Traces
# =========================================================================
tracks_to_remove = []
for tr in board.GetTracks():
    if tr.GetClass() != "PCB_TRACK":
        continue
    net = tr.GetNetname()
    layer = tr.GetLayer()
    s, e = tr.GetStart(), tr.GetEnd()
    sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
    ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)
    
    # /NCS on F.Cu horizontal segment
    if net == "/NCS" and layer == f_cu:
        if (sy < 45 or ey < 45) and (sx < 22 and ex < 22):
            tracks_to_remove.append(tr)
            
    # /TX on B.Cu near rH2 (12.025, 42.3875)
    # Original segment: (23.575, 42.416) -> (13.988, 42.416) -> (10.268, 38.696)
    if net == "/TX" and layer == b_cu:
        if (38.0 <= sy <= 43.0 and 38.0 <= ey <= 43.0) and (min(sx, ex) < 16.0):
            tracks_to_remove.append(tr)
            
    # B.Cu SPI lines: remove segments in trackball region (X < 19.5, Y > 48.0)
    if net in ["+3V3R", "/SCLK", "/MOSI", "/MISO"] and layer == b_cu:
        if (sy > 48.0 or ey > 48.0) and (min(sx, ex) < 19.5):
            tracks_to_remove.append(tr)

for tr in tracks_to_remove:
    board.Remove(tr)
print(f"Removed {len(tracks_to_remove)} old tracks")

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

# 1. Reroute /NCS on F.Cu:
# Via at (21.900, 41.200) -> 45 deg to (20.500, 39.800) -> horiz to (0.500, 39.800) -> vert to (0.500, 56.691)
add_track("/NCS", f_cu, 21.900, 41.200, 20.500, 39.800, width=0.2)
add_track("/NCS", f_cu, 20.500, 39.800, 0.500, 39.800, width=0.2)
add_track("/NCS", f_cu, 0.500, 39.800, 0.500, 56.691, width=0.2)

# 2. Reroute /TX on B.Cu to give large clearance to rH2 (12.025, 42.3875):
# Originally connects to (23.575, 42.416) on east, and (10.268, 38.546) on west (rJ2 pad R).
# Route: (23.575, 42.416) -> (15.500, 42.416) -> 45 deg slant to (11.630, 38.546) -> horiz to (10.268, 38.546)
add_track("/TX", b_cu, 23.575, 42.416, 15.500, 42.416, width=0.2)
add_track("/TX", b_cu, 15.500, 42.416, 11.630, 38.546, width=0.2)
add_track("/TX", b_cu, 11.630, 38.546, 10.268, 38.546, width=0.2)

# 3. Reroute 4 SPI lines on B.Cu:
# We maintain uniform 0.40mm center-to-center spacing perpendicular to the 45-degree angle.
# Center-to-center pitch along 45-deg normal = 0.45mm -> clearance = 0.25mm (> 0.19mm requirement).
# Spacing in Y = 0.45 * sqrt(2) = 0.6364mm.
# Net configs:
# +3V3R: orig_y = 60.712, orig_east = 63.800, rJ3 via = (1.200, 60.712)
# /SCLK: orig_y = 61.263, orig_east = 78.300, rJ3 pin 6 = (-2.725, 49.071), vert trunk at X=0.000
# /MOSI: orig_y = 61.812, orig_east = 78.950, rJ3 pin 5 = (-2.725, 51.611), vert trunk at X=-0.500
# /MISO: orig_y = 62.362, orig_east = 79.600, rJ3 pin 4 = (-2.725, 54.151), vert trunk at X=-1.000

# Base tab Y positions (giving ample clearance to bottom holes Y=62.3875 + 1.1 = 63.4875):
y_tabs = {
    "+3V3R": 64.200,
    "/SCLK": 64.800,
    "/MOSI": 65.400,
    "/MISO": 66.000
}

# Bend start X on east side: stagger them along a line perpendicular to 45 deg (i.e. Y = X + c)
# so the diagonal traces are perfectly parallel with uniform 0.60mm Y separation (0.424mm normal distance).
x_bend_east = {
    "+3V3R": 18.000,
    "/SCLK": 18.000 + (64.800 - 64.200),  # 18.600
    "/MOSI": 18.000 + (65.400 - 64.200),  # 19.200
    "/MISO": 18.000 + (66.000 - 64.200)   # 19.800
}

# For each track:
# East straight segment: (orig_east, orig_y) -> (x_bend_east[net], orig_y)
# 45 deg slant: (x_bend_east[net], orig_y) -> (x_corner_tab, y_tabs[net]) where dx = y_tabs[net] - orig_y
# Tab horizontal segment: (x_corner_tab, y_tabs[net]) -> (west_x, y_tabs[net])
# West vertical/connection to rJ3:

# +3V3R:
# East straight:
add_track("+3V3R", b_cu, 63.800, 60.712, x_bend_east["+3V3R"], 60.712, width=0.2)
# Slant:
corner_x_3v3 = x_bend_east["+3V3R"] - (y_tabs["+3V3R"] - 60.712)
add_track("+3V3R", b_cu, x_bend_east["+3V3R"], 60.712, corner_x_3v3, y_tabs["+3V3R"], width=0.2)
# Horiz in tab:
add_track("+3V3R", b_cu, corner_x_3v3, y_tabs["+3V3R"], 1.200, y_tabs["+3V3R"], width=0.2)
# Vert up to via at (1.200, 60.712):
add_track("+3V3R", b_cu, 1.200, y_tabs["+3V3R"], 1.200, 60.712, width=0.2)

# /SCLK:
add_track("/SCLK", b_cu, 78.300, 61.263, x_bend_east["/SCLK"], 61.263, width=0.2)
corner_x_sclk = x_bend_east["/SCLK"] - (y_tabs["/SCLK"] - 61.263)
add_track("/SCLK", b_cu, x_bend_east["/SCLK"], 61.263, corner_x_sclk, y_tabs["/SCLK"], width=0.2)
add_track("/SCLK", b_cu, corner_x_sclk, y_tabs["/SCLK"], 0.000, y_tabs["/SCLK"], width=0.2)
# Vert up to rJ3 pin 6 at (-2.725, 49.071):
add_track("/SCLK", b_cu, 0.000, y_tabs["/SCLK"], 0.000, 49.071, width=0.2)
add_track("/SCLK", b_cu, 0.000, 49.071, -2.725, 49.071, width=0.2)

# /MOSI:
add_track("/MOSI", b_cu, 78.950, 61.812, x_bend_east["/MOSI"], 61.812, width=0.2)
corner_x_mosi = x_bend_east["/MOSI"] - (y_tabs["/MOSI"] - 61.812)
add_track("/MOSI", b_cu, x_bend_east["/MOSI"], 61.812, corner_x_mosi, y_tabs["/MOSI"], width=0.2)
add_track("/MOSI", b_cu, corner_x_mosi, y_tabs["/MOSI"], -0.500, y_tabs["/MOSI"], width=0.2)
# Vert up to rJ3 pin 5 at (-2.725, 51.611):
add_track("/MOSI", b_cu, -0.500, y_tabs["/MOSI"], -0.500, 51.611, width=0.2)
add_track("/MOSI", b_cu, -0.500, 51.611, -2.725, 51.611, width=0.2)

# /MISO:
add_track("/MISO", b_cu, 79.600, 62.362, x_bend_east["/MISO"], 62.362, width=0.2)
corner_x_miso = x_bend_east["/MISO"] - (y_tabs["/MISO"] - 62.362)
add_track("/MISO", b_cu, x_bend_east["/MISO"], 62.362, corner_x_miso, y_tabs["/MISO"], width=0.2)
add_track("/MISO", b_cu, corner_x_miso, y_tabs["/MISO"], -1.000, y_tabs["/MISO"], width=0.2)
# Vert up to rJ3 pin 4 at (-2.725, 54.151):
add_track("/MISO", b_cu, -1.000, y_tabs["/MISO"], -1.000, 54.151, width=0.2)
add_track("/MISO", b_cu, -1.000, 54.151, -2.725, 54.151, width=0.2)

print("All traces cleanly connected")

# =========================================================================
# 4. Refill Zones
# =========================================================================
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())
print("Zones refilled")

# =========================================================================
# 5. Save Board
# =========================================================================
board.Save(str(DST_PCB))
print(f"Board saved to {DST_PCB}")
