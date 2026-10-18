import pcbnew
import subprocess
import re

LEFT_PCB = r"pcbs/curcur40/left/curcur40-left.kicad_pcb"
KICAD_CLI = r"C:\Users\oktnt\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe"

# 1. Clean LED triangle silkscreen on all SK6812 footprints in raw text
with open(LEFT_PCB, "r", encoding="utf-8") as f:
    text = f.read()

# Replace any LED triangle corner that touches the mask
text = re.sub(r'\(xy\s+-4\.05\s+-1\.5\)\s*\(xy\s+-[23]\.[0-9]+\s+-1\.5\)', '(xy -4.05 -1.5) (xy -3.8 -1.5)', text)

with open(LEFT_PCB, "w", encoding="utf-8") as f:
    f.write(text)

board = pcbnew.LoadBoard(LEFT_PCB)
nets = {net.GetNetname(): net for net in board.GetNetsByName().values()}
B_Cu = pcbnew.B_Cu

def mm(val): return pcbnew.FromMM(float(val))
def pt(x, y): return pcbnew.VECTOR2I(mm(x), mm(y))

# 2. Delete all corridor tracks in X in [-105, -86.5] and Y in [33.5, 42.5]
to_del = []
for t in board.GetTracks():
    if t.GetClass() == "PCB_TRACK":
        net = t.GetNetname()
        if net in ["/KEY13", "/KEY14", "/KEY16", "/KEY17", "/KEY18"]:
            s, e = t.GetStart(), t.GetEnd()
            sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
            ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)
            if min(sx, ex) > -105.0 and max(sx, ex) < -86.5 and min(sy, ey) > 33.5 and max(sy, ey) < 42.5:
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

# 5. KEY18: North of Hole 3
# Hole top is Y = 36.90. We run at Y = 36.65 mm:
# Distance to hole center (-98.0, 38.0) = 38.0 - 36.65 = 1.35 mm -> clearance to hole = 1.35 - 1.10 - 0.10 = 0.15?
# Hole radius is 1.10 mm. Center is (-98.0, 38.0).
# Top of hole is Y = 36.900 mm.
# If track is at Y = 36.600 mm:
# Distance to center = 1.400 mm.
# Clearance to hole circle = 1.400 - 1.10 - 0.1016 = 0.1984 mm (> 0.19 mm)!
# And KEY13 is at Y = 36.349 mm:
# Distance = 36.600 - 36.349 = 0.251 mm -> clearance = 0.251 - 0.2032 = 0.048 mm (too close to KEY13!)
#
# BUT WAIT! Can KEY18 go SOUTH of Hole 3 with KEY17 and KEY16?
# In what order?
# At X = -99.5:
# KEY18 is at 37.136 (top)
# KEY17 is at 37.922 (mid)
# KEY16 is at 38.709 (bottom)
# If they all go SOUTH:
# KEY18 must be the innermost (closest to hole): Y = 39.40
# KEY17 is outside KEY18: Y = 39.75
# KEY16 is outside KEY17: Y = 40.10
#
# Let's trace their order from left:
# KEY18 is at 37.136, goes south to 39.40!
# KEY17 is at 37.922, goes south to 39.75!
# KEY16 is at 38.709, goes south to 40.10!
# DO THEY CROSS ON THE LEFT?
# Left entry points (at X = -100.0):
# KEY18 is at Y = 36.5
# KEY17 is at Y = 37.2
# KEY16 is at Y = 38.0
# When going to 39.40, 39.75, 40.10:
# KEY18 stays at Y = 39.40 (north-most of the trio)
# KEY17 stays at Y = 39.75 (middle)
# KEY16 stays at Y = 40.10 (south-most)
# THEY DO NOT CROSS ON THE LEFT!
# Now look at the right exit (at X = -96.5):
# KEY18 goes from 39.40 to 37.136 (north-most of the trio)
# KEY17 goes from 39.75 to 37.922 (middle)
# KEY16 goes from 40.10 to 38.709 (south-most)
# THEY DO NOT CROSS ON THE RIGHT EITHER!
# THEY NEVER CROSS AT ALL!
# Innermost track stays innermost all the way!

# Let's implement this elegant 3-track south bypass:
# Bypass levels:
# KEY18: Y = 39.40 (distance to hole center: 39.40 - 38.0 = 1.40 mm -> clearance to hole = 0.20 mm!)
# KEY17: Y = 39.75 (clearance to KEY18 = 0.35 - 0.2032 = 0.147 mm -> let's make it Y = 39.80 for 0.40 spacing!)
# KEY16: Y = 40.20 (clearance to KEY17 = 0.40 - 0.2032 = 0.20 mm!)

# Clearance to SMDSW1 Pad 2:
# Pad 2 is at X = -94.968, left edge = -95.493 mm.
# Top edge is Y = 38.566 mm.
# Pad 2 exists only for Y >= 38.566 mm!
# If all 3 tracks return to Y <= 38.709 at X = -96.0:
# KEY18 returns to Y = 37.136 at X = -96.2 (1.4 mm from Pad 2)!
# KEY17 returns to Y = 37.922 at X = -96.2 (1.4 mm from Pad 2)!
# KEY16 returns to Y = 38.709 at X = -96.0 (0.5 mm from Pad 2)!
# And at X = -89.0, KEY18 connects cleanly avoiding the R6-Pad2 via!

# --- KEY18 ---
add_track_path("/KEY18", [
    (-101.453, 34.851),
    (-100.200, 36.104),
    (-99.600, 39.400),
    (-96.400, 39.400),
    (-95.800, 37.136),
    (-89.500, 37.136),
    (-87.874, 38.761),
    (-87.522, 38.761),
], width=0.2032)

# --- KEY17 ---
add_track_path("/KEY17", [
    (-102.239, 35.176),
    (-100.000, 37.415),
    (-99.400, 39.800),
    (-96.600, 39.800),
    (-95.600, 37.922),
    (-89.474, 37.922),
    (-87.848, 39.548),
], width=0.2032)

# --- KEY16 ---
add_track_path("/KEY16", [
    (-103.692, 34.836),
    (-99.800, 38.728),
    (-99.200, 40.200),
    (-96.800, 40.200),
    (-95.400, 38.709),
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
print("Saved Left PCB with Parallel South Bypass.")

# Run DRC
rpt = r"scratch/drc_left_parallel.rpt"
subprocess.run([KICAD_CLI, "pcb", "drc", "--severity-all", "-o", rpt, LEFT_PCB], check=True)
with open(rpt, "r", encoding="utf-8") as f:
    text = f.read()

import re
matches = re.findall(r'\[([a-z_]+)\]: ([^\n]+)', text)
from collections import Counter
print("=== DRC Breakdown with Parallel South Bypass ===")
for k, v in Counter([m[0] for m in matches]).most_common():
    print(f"  {k:30s}: {v}")
