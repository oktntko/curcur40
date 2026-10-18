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

# 2. Delete all tracks of KEY13, KEY14, KEY16, KEY17, KEY18 in corridor x in [-105, -87] and y in [33.5, 42.5]
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

# 1. KEY13: Original clean path (does not hit Hole 3)
# (-100.666, 34.501) -> (-98.818, 36.349) -> (-88.824, 36.349) -> (-87.839, 35.364)
add_track_path("/KEY13", [
    (-100.666, 34.501),
    (-98.818, 36.349),
    (-88.824, 36.349),
    (-87.839, 35.364),
])

# 2. KEY14: Original clean path (does not hit Hole 3)
# (-100.273, 34.204) -> (-98.521, 35.956) -> (-88.987, 35.956) -> (-88.002, 34.971)
add_track_path("/KEY14", [
    (-100.273, 34.204),
    (-98.521, 35.956),
    (-88.987, 35.956),
    (-88.002, 34.971),
])

# Hole 3 is at (-98.0, 38.0), radius = 1.10 mm.
# Edge of hole is at X in [-99.10, -96.90], Y in [36.90, 39.10].
# Bottom of hole keepout is Y = 39.40.
# Local south bypass between X = -99.8 and X = -96.2:
# (At X = -96.2, we are 0.70 mm WEST of SMDSW1 left edge (-95.493), ZERO INTERFERENCE!)
# At X >= -96.0, tracks return to original corridor Y = [37.136, 37.922, 38.709]!

# 3. KEY18:
# Original: (-101.453, 34.851) -> (-99.168, 37.136) -> (-89.148, 37.136) -> (-87.522, 38.761)
# With local bypass:
add_track_path("/KEY18", [
    (-101.453, 34.851),
    (-99.168, 37.136),
    (-99.400, 37.136),
    (-98.000, 36.550), # Pass north of hole at Y = 36.550!
    (-96.600, 37.136),
    (-89.148, 37.136),
    (-87.522, 38.761),
])
# Wait, north of hole: Hole top is 36.90! Y = 36.550 is 38.0 - 36.550 = 1.45 mm from center!
# 1.45 - 1.10 = 0.35 mm clearance! And KEY13 is at Y = 36.349 -> 36.550 - 36.349 = 0.201 mm clearance!
# Or pass SOUTH of hole:
# Let's check south bypass for all 3:
# Y_bypass:
# KEY18: Y = 39.50
# KEY17: Y = 39.85
# KEY16: Y = 40.20
# X_in = -99.60, X_out = -96.40:
# (x - (-98))^2 + (39.5 - 38)^2 = dx^2 + 2.25 >= 2.25 -> dist >= 1.50 mm (clearance = 0.40 mm!)
# At X = -96.40, turn back to original Y:
# KEY18: from (-96.40, 39.50) -> (-94.036, 37.136) -> wait! At X = -94.0, that is SMDSW1!
# That's why! At X in [-95.5, -90.5], Y in [39.0, 40.5] is where SMDSW1/2 Pad 2 is!
# BUT inside SMDSW1/2, Y = 37.136, 37.922, 38.709 ARE ALREADY IN THE MIDDLE between Pad 1 and Pad 2!
# So the tracks must enter the middle corridor BEFORE X = -95.5!
# Can a track go from Y = 39.5 to Y = 37.136 between X = -96.4 and X = -95.5?
# dx = 0.9 mm, dy = 2.364 mm -> angle is steep, but it's just a segment!
# Even better: what if KEY18 passes NORTH of the hole (Y = 36.65, 0.25mm clear to hole),
# and KEY17 & KEY16 pass between hole and SMDSW1?
# Let's test the north route for KEY18 and check clearance!
