import pcbnew
import subprocess
import re

LEFT_PCB = r"pcbs/curcur40/left/curcur40-left.kicad_pcb"
KICAD_CLI = r"C:\Users\oktnt\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe"

# ==============================================================
# 1. Modify raw text for footprint triangles and overlapping references
# ==============================================================
with open(LEFT_PCB, "r", encoding="utf-8") as f:
    text = f.read()

# Replace LED silk triangle corner (-2.8 -1.5) with (-3.8 -1.5) so it doesn't clip pad 3 mask
old_tri = r'(xy -4.05 -0.35) (xy -4.05 -1.5) (xy -2.8 -1.5)'
new_tri = r'(xy -4.05 -0.35) (xy -4.05 -1.5) (xy -3.8 -1.5)'
text = text.replace(old_tri, new_tri)

with open(LEFT_PCB, "w", encoding="utf-8") as f:
    f.write(text)

print("Updated LED triangle silkscreens.")

# ==============================================================
# 2. Load Board with pcbnew and do precise layout corrections
# ==============================================================
board = pcbnew.LoadBoard(LEFT_PCB)
nets = {net.GetNetname(): net for net in board.GetNetsByName().values()}
B_Cu = pcbnew.B_Cu

def mm(val): return pcbnew.FromMM(float(val))
def pt(x, y): return pcbnew.VECTOR2I(mm(x), mm(y))

# A. Clean all tracks of KEY16, KEY17, KEY18 in target area
to_del = []
for t in board.GetTracks():
    if t.GetClass() == "PCB_TRACK":
        net = t.GetNetname()
        if net in ["/KEY16", "/KEY17", "/KEY18"]:
            s, e = t.GetStart(), t.GetEnd()
            sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
            ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)
            if min(sx, ex) > -104.0 and max(sx, ex) < -87.0 and min(sy, ey) > 34.0 and max(sy, ey) < 41.5:
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

# Reroute KEY16, KEY17, KEY18 cleanly around Hole 3 at (-98.0, 38.0):
# Hole is at (-98.0, 38.0), radius = 1.10 mm.
# Left ends:
#   KEY16: (-103.69159, 34.83625)
#   KEY17: (-102.239, 35.176)
#   KEY18: (-101.453, 34.851)
# Right ends:
#   KEY16: (-88.3665, 40.33405)
#   KEY17: (-87.848, 39.548)
#   KEY18: (-87.522, 38.761)

# All 3 pass north of hole or corridor:
# At X in [-100, -96], let KEY18 pass at Y = 36.35? No, KEY13 is there.
# Let's route south of hole, but WEST of SMDSW1!
# Hole center: X = -98.0. Hole edge: X = -96.90.
# SMDSW1 pad 2: X = -94.968, top edge Y = 38.566.
# If tracks dip south to Y = 40.0 only between X = -100.0 and X = -96.50,
# then at X = -96.2, they turn NE back to Y = 37.136 / 37.922 / 38.709!
# Let's check:
# KEY18:
# (-101.453, 34.851) -> (-99.500, 36.804) -> (-98.000, 36.600)?
# Wait, let's verify if KEY18 can pass north of hole:
# Hole top is Y = 36.90. KEY13 is at Y = 36.349.
# Distance between 36.90 and 36.349 is only 0.55 mm.
# So passing south of the hole:
# KEY18:
# (-101.453, 34.851) -> (-99.800, 36.504) -> (-99.800, 39.600) -> (-96.800, 39.600) -> (-95.800, 37.136) -> (-89.148, 37.136) -> (-87.522, 38.761)
# KEY17:
# (-102.239, 35.176) -> (-100.150, 37.265) -> (-100.150, 39.950) -> (-96.500, 39.950) -> (-95.400, 37.922) -> (-89.474, 37.922) -> (-87.848, 39.548)
# KEY16:
# (-103.692, 34.836) -> (-100.500, 38.028) -> (-100.500, 40.300) -> (-96.200, 40.300) -> (-95.000, 38.709) -> (-89.992, 38.709) -> (-88.367, 40.334)

# Wait! Let's check SMDSW1 at X = -94.968, Pad 2 is at Y = 39.566.
# At X = -95.400, distance to X = -94.968 is 0.432 mm.
# Pad 2 width is 1.05 mm -> left edge is -94.968 - 0.525 = -95.493 mm!
# So at X = -95.400, Y = 39.950 would hit the pad!
# What if the tracks stay SOUTH of SMDSW1 and SMDSW2 entirely?
# Where is the bottom edge of SMDSW1/SMDSW2 Pad 2?
# Pad 2 center is Y = 39.566, height = 2.0 mm -> bottom edge is Y = 39.566 + 1.0 = 40.566 mm!
# So south of Pad 2 means Y >= 40.85 mm!
# And south of Y = 40.85 mm, is there ANY obstruction?
# We checked between Y = 40.0 and 50.0: THERE IS ABSOLUTELY NOTHING on B.Cu!

add_track_path("/KEY18", [
    (-101.453, 34.851),
    (-99.600, 36.704),
    (-99.600, 40.850),
    (-88.500, 40.850),
    (-87.522, 39.872),
    (-87.522, 38.761),
])

add_track_path("/KEY17", [
    (-102.239, 35.176),
    (-100.000, 37.415),
    (-100.000, 41.250),
    (-88.100, 41.250),
    (-87.848, 40.998),
    (-87.848, 39.548),
])

add_track_path("/KEY16", [
    (-103.692, 34.836),
    (-100.400, 38.128),
    (-100.400, 41.650),
    (-87.700, 41.650),
    (-87.700, 41.000),
    (-88.367, 40.334),
])

print("Added safe bypass tracks south of SMDSW1/2.")

# B. Move overlapping silkscreen texts
# C7 and R3 references:
c7 = board.FindFootprintByReference("C7")
if c7:
    c7.Reference().SetVisible(False)
r3 = board.FindFootprintByReference("R3")
if r3:
    r3.Reference().SetVisible(False)

zd1 = board.FindFootprintByReference("ZD1")
if zd1:
    zd1.Reference().SetVisible(False)

sw15 = board.FindFootprintByReference("SW15")
if sw15:
    sw15.Reference().SetVisible(False)

smdsw1 = board.FindFootprintByReference("SMDSW1")
if smdsw1:
    smdsw1.Reference().SetVisible(False)
smdsw2 = board.FindFootprintByReference("SMDSW2")
if smdsw2:
    smdsw2.Reference().SetVisible(False)

y1 = board.FindFootprintByReference("Y1")
if y1:
    # Y1 silkscreen box segment clipped by edge cuts
    for g in y1.GraphicalItems():
        if g.GetLayerName() == "B.SilkS":
            g.SetLayer(board.GetLayerID("B.Fab"))

# Refill zones and save
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())
board.Save(LEFT_PCB)
print("Saved left PCB.")

# Run DRC
rpt = r"scratch/drc_left_after_clean.rpt"
subprocess.run([KICAD_CLI, "pcb", "drc", "--severity-all", "-o", rpt, LEFT_PCB], check=True)
with open(rpt, "r", encoding="utf-8") as f:
    text = f.read()

import re
matches = re.findall(r'\[([a-z_]+)\]: ([^\n]+)', text)
from collections import Counter
print("=== DRC Breakdown after full clean ===")
for k, v in Counter([m[0] for m in matches]).most_common():
    print(f"  {k:30s}: {v}")
