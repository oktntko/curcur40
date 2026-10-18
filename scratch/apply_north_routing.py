import pcbnew
import subprocess
import re

LEFT_PCB = r"pcbs/curcur40/left/curcur40-left.kicad_pcb"
KICAD_CLI = r"C:\Users\oktnt\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe"

# 1. Clean LED triangle silkscreen on all SK6812 footprints
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

# 2. Delete all tracks of KEY13, KEY14, KEY16, KEY17, KEY18 in x in [-104, -87] and y in [33.5, 42.5]
to_del = []
for t in board.GetTracks():
    if t.GetClass() == "PCB_TRACK" and t.GetLayerName() == "B.Cu":
        net = t.GetNetname()
        if net in ["/KEY13", "/KEY14", "/KEY16", "/KEY17", "/KEY18"]:
            s, e = t.GetStart(), t.GetEnd()
            sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
            ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)
            if min(sx, ex) > -105.0 and max(sx, ex) < -87.0 and min(sy, ey) > 33.5 and max(sy, ey) < 42.5:
                to_del.append(t)

print(f"Deleting {len(to_del)} existing corridor tracks...")
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

# Order from North (top) to South (bottom), all strictly NORTH of Hole 3 (top keepout Y = 36.60):
# Hole 3 is at (-98.0, 38.0). Keepout radius = 1.40 mm -> top keepout Y = 36.60 mm.
#
# Available Y tracks (spacing 0.35 mm):
# Y1 = 34.60 mm -> KEY13
# Y2 = 35.00 mm -> KEY14
# Y3 = 35.45 mm -> KEY18
# Y4 = 35.90 mm -> KEY17
# Y5 = 36.35 mm -> KEY16
# Notice: Y5 = 36.35 mm is 38.0 - 36.35 = 1.65 mm away from (-98.0, 38.0)!
# sqrt(dx^2 + 1.65^2) >= 1.65 mm > 1.40 mm -> ZERO COPPER EDGE VIOLATION to Hole 3!

# --- KEY13 ---
# Left: (-100.666, 34.501)
# Right: (-88.824, 36.349) -> connects to (-87.839, 35.364)
add_track_path("/KEY13", [
    (-100.666, 34.501),
    (-100.567, 34.600),
    (-90.575, 34.600),
    (-88.824, 36.349),
])

# --- KEY14 ---
# Left: (-100.273, 34.204)
# Right: (-88.987, 35.956) -> connects to (-88.002, 34.971)
add_track_path("/KEY14", [
    (-100.273, 34.204),
    (-99.477, 35.000),
    (-89.943, 35.000),
    (-88.987, 35.956),
])

# --- KEY18 ---
# Left: (-101.453, 34.851)
# Right: (-87.522, 38.761)
add_track_path("/KEY18", [
    (-101.453, 34.851),
    (-100.854, 35.450),
    (-90.833, 35.450),
    (-87.522, 38.761),
])

# --- KEY17 ---
# Left: (-102.239, 35.176)
# Right: (-87.848, 39.548)
add_track_path("/KEY17", [
    (-102.239, 35.176),
    (-101.515, 35.900),
    (-91.496, 35.900),
    (-87.848, 39.548),
])

# --- KEY16 ---
# Left: (-103.692, 34.836)
# Right: (-88.367, 40.334)
add_track_path("/KEY16", [
    (-103.692, 34.836),
    (-102.178, 36.350),
    (-92.351, 36.350),
    (-88.367, 40.334),
])

print("Rerouted all 5 tracks cleanly north of Hole 3.")

# 3. Clean references
for ref in ["C7", "R3", "ZD1", "SW15", "SMDSW1", "SMDSW2"]:
    fp = board.FindFootprintByReference(ref)
    if fp:
        fp.Reference().SetVisible(False)

y1 = board.FindFootprintByReference("Y1")
if y1:
    for g in y1.GraphicalItems():
        if g.GetLayerName() == "B.SilkS":
            g.SetLayer(board.GetLayerID("B.Fab"))

# Refill zones and save
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())
board.Save(LEFT_PCB)
print("Saved left PCB.")

# Run DRC
rpt = r"scratch/drc_left_clean_routed.rpt"
subprocess.run([KICAD_CLI, "pcb", "drc", "--severity-all", "-o", rpt, LEFT_PCB], check=True)
with open(rpt, "r", encoding="utf-8") as f:
    text = f.read()

import re
matches = re.findall(r'\[([a-z_]+)\]: ([^\n]+)', text)
from collections import Counter
print("=== DRC Breakdown with North Routing ===")
for k, v in Counter([m[0] for m in matches]).most_common():
    print(f"  {k:30s}: {v}")
