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
F_Cu = pcbnew.F_Cu
B_Cu = pcbnew.B_Cu

def mm(val): return pcbnew.FromMM(float(val))
def pt(x, y): return pcbnew.VECTOR2I(mm(x), mm(y))

def add_track_path(board, net_item, layer, pts, width=0.25):
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        t = pcbnew.PCB_TRACK(board)
        t.SetLayer(layer)
        t.SetStart(pt(x1, y1))
        t.SetEnd(pt(x2, y2))
        t.SetWidth(mm(width))
        board.Add(t)
        t.SetNet(net_item)

def add_via(board, net_item, x, y, drill=0.30, size=0.50):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pt(x, y))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetDrill(mm(drill))
    v.SetWidth(mm(size))
    board.Add(v)
    v.SetNet(net_item)

# 2. Clean corridor tracks in X in [-105, -87] and Y in [33.5, 42.5]
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

# 3. Route KEY13 & KEY14 (Original untouched paths on B.Cu)
add_track_path(board, nets["/KEY13"], B_Cu, [
    (-100.666, 34.501),
    (-98.818, 36.349),
    (-88.824, 36.349),
    (-87.839, 35.364),
], width=0.2032)

add_track_path(board, nets["/KEY14"], B_Cu, [
    (-100.273, 34.204),
    (-98.521, 35.956),
    (-88.987, 35.956),
    (-88.002, 34.971),
], width=0.2032)

# 4. Route KEY18 on B.Cu:
# Passes north of Hole 3 at Y = 36.55 mm (between KEY13 at 36.35 and Hole 3 top keepout at 36.70)
# Or pass KEY18 via F.Cu!
# Let's route KEY17 and KEY18 on B.Cu, or use F.Cu for KEY16!
# With F.Cu:
# KEY16:
# B.Cu: (-103.692, 34.836) -> via at (-102.500, 35.000)
# F.Cu: (-102.500, 35.000) -> (-99.500, 35.000) -> (-97.500, 36.400) -> (-88.500, 36.400) -> (-88.500, 39.000) -> via at (-88.500, 39.000)
# B.Cu: via (-88.500, 39.000) -> (-88.367, 40.334)
add_track_path(board, nets["/KEY16"], B_Cu, [
    (-103.692, 34.836),
    (-102.500, 35.000),
], width=0.2032)
add_via(board, nets["/KEY16"], -102.500, 35.000, drill=0.30, size=0.50)
add_track_path(board, nets["/KEY16"], F_Cu, [
    (-102.500, 35.000),
    (-100.000, 35.000),
    (-97.000, 36.400),
    (-88.500, 36.400),
    (-88.500, 39.000),
], width=0.2032)
add_via(board, nets["/KEY16"], -88.500, 39.000, drill=0.30, size=0.50)
add_track_path(board, nets["/KEY16"], B_Cu, [
    (-88.500, 39.000),
    (-88.367, 40.334),
], width=0.2032)

# KEY17 on F.Cu:
# Left: (-102.239, 35.176)
# Via at (-101.500, 35.500)
# F.Cu: (-101.500, 35.500) -> (-100.000, 35.500) -> (-97.000, 36.900) -> (-87.848, 36.900) -> (-87.848, 38.500) -> via at (-87.848, 38.500)
# B.Cu: (-87.848, 38.500) -> (-87.848, 39.548)
add_track_path(board, nets["/KEY17"], B_Cu, [
    (-102.239, 35.176),
    (-101.500, 35.500),
], width=0.2032)
add_via(board, nets["/KEY17"], -101.500, 35.500, drill=0.30, size=0.50)
add_track_path(board, nets["/KEY17"], F_Cu, [
    (-101.500, 35.500),
    (-100.000, 35.500),
    (-97.000, 37.000),
    (-87.848, 37.000),
    (-87.848, 38.200),
], width=0.2032)
add_via(board, nets["/KEY17"], -87.848, 38.200, drill=0.30, size=0.50)
add_track_path(board, nets["/KEY17"], B_Cu, [
    (-87.848, 38.200),
    (-87.848, 39.548),
], width=0.2032)

# KEY18 on B.Cu:
# Now with KEY16 & KEY17 on F.Cu, B.Cu has ONLY KEY18!
# KEY18 can easily bypass north of Hole 3 at Y = 36.65, or south at Y = 39.50!
# At Y = 36.60 mm:
# KEY13 is at 36.349 -> distance = 0.251 mm (clearance > 0.19 mm!)
# Hole 3 top is at 36.90 -> distance = 0.30 mm (clearance > 0.19 mm!)
add_track_path(board, nets["/KEY18"], B_Cu, [
    (-101.453, 34.851),
    (-99.600, 36.600),
    (-96.400, 36.600),
    (-89.148, 37.136),
    (-87.522, 38.761),
], width=0.2032)

# 5. Hide overlapping silkscreen texts
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
print("Saved left PCB.")

# Run DRC
rpt = r"scratch/drc_left_vias_test.rpt"
subprocess.run([KICAD_CLI, "pcb", "drc", "--severity-all", "-o", rpt, LEFT_PCB], check=True)
with open(rpt, "r", encoding="utf-8") as f:
    text = f.read()

import re
matches = re.findall(r'\[([a-z_]+)\]: ([^\n]+)', text)
from collections import Counter
print("=== DRC Breakdown with 2-Layer Clean Routing ===")
for k, v in Counter([m[0] for m in matches]).most_common():
    print(f"  {k:30s}: {v}")
