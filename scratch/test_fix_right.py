import pcbnew
import subprocess
import re
from collections import Counter

RIGHT_PCB = r"pcbs/curcur40/right/curcur40-right.kicad_pcb"
KICAD_CLI = r"C:\Users\oktnt\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe"

# 1. Clean LED silkscreen triangle on SK6812 footprints
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

# 2. Fix /TX vs +5VR clearance:
# Move /TX via from (8.773, 39.200) to (8.773, 40.500)
for t in list(board.GetTracks()):
    if t.GetNetname() == '/TX':
        sp, ep = t.GetStart(), t.GetEnd()
        sx, sy = pcbnew.ToMM(sp.x), pcbnew.ToMM(sp.y)
        ex, ey = pcbnew.ToMM(ep.x), pcbnew.ToMM(ep.y)
        if t.GetClass() == 'PCB_VIA' and abs(sx - 8.773) < 0.1 and abs(sy - 39.200) < 0.1:
            t.SetPosition(pt(8.773, 40.500))
        elif t.GetClass() == 'PCB_TRACK':
            if abs(sx - 8.773) < 0.1 and abs(ex - 8.773) < 0.1:
                if abs(max(sy, ey) - 39.200) < 0.1: # track ending at old via pos
                    if sy > ey: t.SetStart(pt(8.773, 40.500))
                    else: t.SetEnd(pt(8.773, 40.500))
                elif abs(min(sy, ey) - 39.200) < 0.1: # track starting at old via pos
                    if sy < ey: t.SetStart(pt(8.773, 40.500))
                    else: t.SetEnd(pt(8.773, 40.500))

# 3. Clean up bad /KEY16 and /KEY17 tracks in corridor [87, 102] x [34, 42]
to_del = []
for t in board.GetTracks():
    net = t.GetNetname()
    if net in ['/KEY16', '/KEY17', '/KEY18']:
        sp, ep = t.GetStart(), t.GetEnd()
        sx, sy = pcbnew.ToMM(sp.x), pcbnew.ToMM(sp.y)
        ex, ey = pcbnew.ToMM(ep.x), pcbnew.ToMM(ep.y)
        if max(sx, ex) > 87.0 and min(sx, ex) < 101.5 and max(sy, ey) > 34.0 and min(sy, ey) < 42.0:
            if t.GetClass() == 'PCB_TRACK' and t.GetLayerName() == 'B.Cu':
                to_del.append(t)

for t in to_del:
    board.Delete(t)

def add_track(netname, p1, p2, layer=B_Cu, width=0.2032):
    tr = pcbnew.PCB_TRACK(board)
    tr.SetLayer(layer)
    tr.SetStart(pt(p1[0], p1[1]))
    tr.SetEnd(pt(p2[0], p2[1]))
    tr.SetWidth(mm(width))
    tr.SetNet(nets[netname])
    board.Add(tr)

# Route /KEY18 (North of Hole 3):
# Connect (87.002, 39.268) -> (89.697, 36.573) -> (97.162, 36.573) -> (98.221, 35.514)
add_track('/KEY18', (87.002, 39.268), (89.697, 36.573))
add_track('/KEY18', (89.697, 36.573), (97.162, 36.573))
add_track('/KEY18', (97.162, 36.573), (98.221, 35.514))

# Route /KEY17:
# Connect (87.328, 40.054) to (99.010, 35.860)
# Let's run at Y = 37.150:
add_track('/KEY17', (87.328, 40.054), (90.232, 37.150))
add_track('/KEY17', (90.232, 37.150), (96.500, 37.150))
add_track('/KEY17', (96.500, 37.150), (97.790, 35.860))
add_track('/KEY17', (97.790, 35.860), (99.010, 35.860))

# Route /KEY16:
# South of SMDSW1 & SMDSW2 at Y = 40.500:
# From via (88.737, 40.426) -> (88.737, 40.500) -> (99.800, 40.500) -> (101.320, 34.660)
add_track('/KEY16', (88.737, 40.426), (88.737, 40.500))
add_track('/KEY16', (88.737, 40.500), (99.800, 40.500))
add_track('/KEY16', (99.800, 40.500), (101.320, 34.660))

# Hide reference silks for overlapping components
for ref in ['rZD1', 'rC9', 'rSMDSW1', 'rSMDSW2']:
    fp = board.FindFootprintByReference(ref)
    if fp:
        fp.Reference().SetVisible(False)

zf = pcbnew.ZONE_FILLER(board)
zf.Fill(board.Zones())
board.Save(RIGHT_PCB)
print("Right PCB saved, running strict DRC...")
