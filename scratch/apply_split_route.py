import pcbnew
import subprocess
import re

LEFT_PCB = r"pcbs/curcur40/left/curcur40-left.kicad_pcb"
KICAD_CLI = r"C:\Users\oktnt\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe"

# 1. Clean LED triangle silkscreen on all SK6812 footprints in raw text
with open(LEFT_PCB, "r", encoding="utf-8") as f:
    text = f.read()

text = re.sub(r'\(xy\s+-4\.05\s+-1\.5\)\s*\(xy\s+-[23]\.[0-9]+\s+-1\.5\)', '(xy -4.05 -1.5) (xy -3.8 -1.5)', text)

# Also fix curcur40 text position if it touches any trace
with open(LEFT_PCB, "w", encoding="utf-8") as f:
    f.write(text)

board = pcbnew.LoadBoard(LEFT_PCB)
nets = {net.GetNetname(): net for net in board.GetNetsByName().values()}
B_Cu = pcbnew.B_Cu

def mm(val): return pcbnew.FromMM(float(val))
def pt(x, y): return pcbnew.VECTOR2I(mm(x), mm(y))

# 2. Delete all corridor tracks in X in [-105, -87] and Y in [33.5, 42.5]
to_del = []
for t in board.GetTracks():
    if t.GetClass() == "PCB_TRACK":
        net = t.GetNetname()
        if net in ["/KEY13", "/KEY14", "/KEY16", "/KEY17", "/KEY18"]:
            s, e = t.GetStart(), t.GetEnd()
            sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
            ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)
            if min(sx, ex) > -105.0 and max(sx, ex) < -87.0 and min(sy, ey) > 33.5 and max(sy, ey) < 42.5:
                to_del.append(t)
    elif t.GetClass() == "PCB_VIA":
        pos = t.GetPosition()
        vx, vy = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
        if -105.0 < vx < -87.0 and 33.5 < vy < 42.5 and t.GetNetname() in ["/KEY16", "/KEY17", "/KEY18"]:
            to_del.append(t)

for t in to_del:
    board.Delete(t)

def add_track_path(net_name, pts, width=0.2032):
    net_item = nets[net_name]
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        t = pcbnew.PCB_TRACK(board)
        t.SetLayer(B_Cu)
        t.SetStart(pt(x1, y1))
        t.SetEnd(pt(x2, y2))
        t.SetWidth(mm(width))
        board.Add(t)
        t.SetNet(net_item)

# 3. KEY13: Original clean path
add_track_path("/KEY13", [
    (-100.666, 34.501),
    (-98.818, 36.349),
    (-88.824, 36.349),
    (-87.839, 35.364),
], width=0.2032)

# 4. KEY14: Original clean path
add_track_path("/KEY14", [
    (-100.273, 34.204),
    (-98.521, 35.956),
    (-88.987, 35.956),
    (-88.002, 34.971),
], width=0.2032)

# 5. KEY18: North bypass around Hole 3
# Hole top is Y = 36.90. We run at Y = 36.56 mm (dy to center = 1.44 mm -> clearance = 0.24 mm to hole edge).
# KEY13 is at Y = 36.349 -> clearance to KEY13 = 36.560 - 36.349 - 0.2032 = 0.0078?
# Wait! Let's give KEY13 and KEY18 0.22 mm track-to-track clearance!
# KEY13 can be shifted NORTH by 0.15 mm:
# KEY13 at Y = 36.200:
#   KEY14 is at Y = 35.956 -> 36.200 - 35.956 = 0.244 mm spacing (> 0.20 mm)!
# Then KEY18 can be at Y = 36.560:
#   36.560 - 36.200 = 0.360 mm spacing (> 0.20 mm)!
#   Hole top is 36.900 -> 38.000 - 36.560 = 1.440 mm from center -> 1.440 - 1.10 = 0.340 mm (> 0.20 mm)!
# PERFECT!
# Let's adjust KEY13 between X = -99.0 and X = -89.0:
add_track_path("/KEY13", [
    (-100.666, 34.501),
    (-98.967, 36.200),
    (-88.973, 36.200),
    (-87.839, 35.364),
], width=0.2032)

# Now KEY18:
add_track_path("/KEY18", [
    (-101.453, 34.851),
    (-99.400, 36.560),
    (-96.600, 36.560),
    (-89.148, 37.136),
    (-87.522, 38.761),
], width=0.2032)

# 6. KEY17: South bypass around Hole 3
# Passes at Y = 39.45 mm between X = -99.40 and X = -96.60:
# (38.0 - 39.45 = 1.45 mm from center -> clearance = 0.25 mm to hole edge)
# SMDSW1 starts at X = -95.50. So at X = -96.60, it turns NE to (-95.80, 37.922),
# then runs along original Y = 37.922 through the SMDSW1/2 corridor!
add_track_path("/KEY17", [
    (-102.239, 35.176),
    (-99.800, 37.615),
    (-99.400, 39.450),
    (-96.600, 39.450),
    (-95.800, 37.922),
    (-89.474, 37.922),
    (-87.848, 39.548),
], width=0.2032)

# 7. KEY16: South bypass around KEY17
# Passes at Y = 39.80 mm between X = -99.40 and X = -96.60:
# Clearance to KEY17 = 39.80 - 39.45 = 0.35 mm!
# Clearance to board edge (40.981) = 40.981 - 39.80 = 1.18 mm!
# At X = -96.60, turns NE to (-95.60, 38.709), then original Y = 38.709!
add_track_path("/KEY16", [
    (-103.692, 34.836),
    (-100.100, 38.428),
    (-99.400, 39.800),
    (-96.600, 39.800),
    (-95.600, 38.709),
    (-89.992, 38.709),
    (-88.367, 40.334),
], width=0.2032)

# 8. Clean all overlapping references
for ref in ["C7", "R3", "ZD1", "SW15", "SMDSW1", "SMDSW2"]:
    fp = board.FindFootprintByReference(ref)
    if fp:
        fp.Reference().SetVisible(False)

y1 = board.FindFootprintByReference("Y1")
if y1:
    for g in y1.GraphicalItems():
        if g.GetLayerName() == "B.SilkS":
            g.SetLayer(board.GetLayerID("B.Fab"))

filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())
board.Save(LEFT_PCB)
print("Saved Left PCB with Split Route.")

# Run DRC
rpt = r"scratch/drc_left_split_route.rpt"
subprocess.run([KICAD_CLI, "pcb", "drc", "--severity-all", "-o", rpt, LEFT_PCB], check=True)
with open(rpt, "r", encoding="utf-8") as f:
    text = f.read()

import re
matches = re.findall(r'\[([a-z_]+)\]: ([^\n]+)', text)
from collections import Counter
print("=== DRC Breakdown with Split Route ===")
for k, v in Counter([m[0] for m in matches]).most_common():
    print(f"  {k:30s}: {v}")
