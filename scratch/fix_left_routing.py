import pcbnew
import subprocess

LEFT_PCB = r"pcbs/curcur40/left/curcur40-left.kicad_pcb"
KICAD_CLI = r"C:\Users\oktnt\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe"

board = pcbnew.LoadBoard(LEFT_PCB)
nets = {net.GetNetname(): net for net in board.GetNetsByName().values()}
B_Cu = pcbnew.B_Cu

def mm(val): return pcbnew.FromMM(float(val))
def pt(x, y): return pcbnew.VECTOR2I(mm(x), mm(y))

# 1. Fix /KEY16, /KEY17, /KEY18 tracks around (-98.0, 38.0)
# Delete all tracks of KEY16, KEY17, KEY18 in x in [-104, -88], y in [34, 41]
to_delete = []
for t in board.GetTracks():
    if t.GetClass() == "PCB_TRACK":
        net = t.GetNetname()
        if net in ["/KEY16", "/KEY17", "/KEY18"]:
            s, e = t.GetStart(), t.GetEnd()
            sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
            ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)
            if min(sx, ex) > -104.0 and max(sx, ex) < -88.0 and min(sy, ey) > 34.0 and max(sy, ey) < 41.5:
                to_delete.append(t)

print(f"Deleting {len(to_delete)} buggy tracks around hole 3...")
for t in to_delete:
    board.Delete(t)

# Restore original clean tracks of KEY16, KEY17, KEY18 (from test_left_orig before any hole addition)
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

# Original KEY16
add_track_path("/KEY16", [
    (-103.69159, 34.83625),
    (-99.81919, 38.70865),
    (-89.99190, 38.70865),
    (-88.36650, 40.33405),
])

# Original KEY17
add_track_path("/KEY17", [
    (-102.239, 35.176),
    (-99.493, 37.922),
    (-89.474, 37.922),
    (-87.848, 39.548),
])

# Original KEY18
add_track_path("/KEY18", [
    (-101.453, 34.851),
    (-99.168, 37.136),
    (-89.148, 37.136),
    (-87.522, 38.761),
])

print("Restored original KEY16/17/18 tracks.")

# 2. Check hole 3 circle at (-98.0, 38.0)
# Let's see all circles on Edge.Cuts
circles = []
for d in board.GetDrawings():
    if d.GetLayerName() == "Edge.Cuts" and d.GetShapeStr() == "Circle":
        pos = d.GetPosition()
        circles.append((d, pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)))

print(f"Edge.Cuts circles on Left PCB: {[(round(x, 2), round(y, 2)) for _, x, y in circles]}")

# 3. Refill zones
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())
board.Save(LEFT_PCB)
print("Saved left PCB.")

# Run DRC
rpt = r"scratch/drc_left_test_route.rpt"
subprocess.run([KICAD_CLI, "pcb", "drc", "--severity-all", "-o", rpt, LEFT_PCB], check=True)
with open(rpt, "r", encoding="utf-8") as f:
    text = f.read()

import re
matches = re.findall(r'\[([a-z_]+)\]: ([^\n]+)', text)
from collections import Counter
print("=== DRC Breakdown after route restore ===")
for k, v in Counter([m[0] for m in matches]).most_common():
    print(f"  {k:30s}: {v}")
