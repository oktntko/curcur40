import pcbnew
import subprocess
import re
from collections import Counter

RIGHT_PCB = r"pcbs/curcur40/right/curcur40-right.kicad_pcb"
KICAD_CLI = r"C:\Users\oktnt\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe"

# First, restore clean right PCB
subprocess.run(["git", "checkout", RIGHT_PCB], check=True)

# 1. Clean LED triangle silkscreen in text
with open(RIGHT_PCB, "r", encoding="utf-8") as f:
    text = f.read()

text = re.sub(r'\(xy\s+-4\.05\s+-1\.5\)\s*\(xy\s+-[23]\.[0-9]+\s+-1\.5\)', '(xy -4.05 -1.5) (xy -3.8 -1.5)', text)
with open(RIGHT_PCB, "w", encoding="utf-8") as f:
    f.write(text)

board = pcbnew.LoadBoard(RIGHT_PCB)
nets = {net.GetNetname(): net for net in board.GetNetsByName().values()}
B_Cu = pcbnew.B_Cu
F_Cu = pcbnew.F_Cu

def mm(val): return pcbnew.FromMM(float(val))
def pt(x, y): return pcbnew.VECTOR2I(mm(x), mm(y))

def add_track_path(netname, pts, layer=B_Cu, width=0.2032):
    net_obj = nets[netname]
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        t = pcbnew.PCB_TRACK(board)
        t.SetLayer(layer)
        t.SetNet(net_obj)
        t.SetStart(pt(x1, y1))
        t.SetEnd(pt(x2, y2))
        t.SetWidth(mm(width))
        board.Add(t)

# 2. Fix +5VR clearance to /TX and board edge:
to_del_5v = []
for t in board.GetTracks():
    if t.GetNetname() == '+5VR' and t.GetLayerName() == 'B.Cu' and t.GetClass() == 'PCB_TRACK':
        sp, ep = t.GetStart(), t.GetEnd()
        sx, sy = pcbnew.ToMM(sp.x), pcbnew.ToMM(sp.y)
        ex, ey = pcbnew.ToMM(ep.x), pcbnew.ToMM(ep.y)
        if min(sx, ex) > 6.0 and max(sx, ex) < 19.0 and min(sy, ey) > 38.0 and max(sy, ey) < 39.0:
            to_del_5v.append(t)

for t in to_del_5v:
    board.Delete(t)

add_track_path('+5VR', [
    (6.543, 38.546),
    (7.600, 38.546),
    (8.000, 38.146),
    (17.402, 38.146),
    (18.598, 38.696),
], layer=B_Cu, width=0.400)

# 3. Clean KEY16, KEY17, KEY18 in corridor [86.8, 102.0]
to_del_keys = []
for t in board.GetTracks():
    net = t.GetNetname()
    if net in ['/KEY16', '/KEY17', '/KEY18']:
        sp, ep = t.GetStart(), t.GetEnd()
        sx, sy = pcbnew.ToMM(sp.x), pcbnew.ToMM(sp.y)
        ex, ey = pcbnew.ToMM(ep.x), pcbnew.ToMM(ep.y)
        if min(sx, ex) >= 86.8 and max(sx, ex) <= 102.0 and min(sy, ey) > 34.0 and max(sy, ey) < 42.0:
            if t.GetClass() == 'PCB_TRACK' and t.GetLayerName() == 'B.Cu':
                to_del_keys.append(t)

for t in to_del_keys:
    board.Delete(t)

# Route /KEY18 (North-most on B.Cu):
add_track_path('/KEY18', [
    (87.002, 39.268),
    (89.697, 36.573),
    (95.800, 36.573),
    (96.859, 35.514),
    (98.221, 35.514),
], layer=B_Cu, width=0.2032)

# Route /KEY17 (Middle on B.Cu):
add_track_path('/KEY17', [
    (87.328, 40.054),
    (90.132, 37.250),
    (96.800, 37.250),
    (98.050, 36.000),
    (99.010, 36.000),
    (99.010, 35.860),
], layer=B_Cu, width=0.2032)

# Route /KEY16 (South on B.Cu):
add_track_path('/KEY16', [
    (88.737, 40.426),
    (90.100, 37.850),
    (96.000, 37.850),
    (96.700, 40.100),
    (99.800, 40.100),
    (101.320, 34.660),
], layer=B_Cu, width=0.2032)

# 4. Hide reference silks for overlapping components
for ref in ['rZD1', 'rC9', 'rSMDSW1', 'rSMDSW2']:
    fp = board.FindFootprintByReference(ref)
    if fp:
        fp.Reference().SetVisible(False)

zf = pcbnew.ZONE_FILLER(board)
zf.Fill(board.Zones())
board.Save(RIGHT_PCB)
print("Right PCB updated and saved.")
