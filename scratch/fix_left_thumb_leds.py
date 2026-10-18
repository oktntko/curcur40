import pcbnew
import json

LEFT_PCB = r"pcbs/curcur40/left/curcur40-left.kicad_pcb"
TEST_PCB = r"scratch/perfect_left_thumb_leds.kicad_pcb"

b = pcbnew.LoadBoard(LEFT_PCB)

def mm(v): return pcbnew.FromMM(float(v))
def pt(x, y): return pcbnew.VECTOR2I(mm(x), mm(y))

# Target Y for all thumb LEDs
TARGET_Y = 47.6500

# 1. Update LED8 and LED9 positions
led8 = b.FindFootprintByReference("LED8")
led9 = b.FindFootprintByReference("LED9")

# Remove old tracks connected to LED8 and LED9 pads
pads_to_clear = list(led8.Pads()) + list(led9.Pads())
pad_positions_old = [p.GetPosition() for p in pads_to_clear]

# Delete old tracks in the LED8/LED9 immediate area
tracks_to_delete = []
for t in b.GetTracks():
    p1, p2 = t.GetStart(), t.GetEnd()
    x1, y1 = p1.x/1e6, p1.y/1e6
    x2, y2 = p2.x/1e6, p2.y/1e6
    # Delete Net-(D1-K) tracks/vias near LED8/LED9
    if t.GetNetname() == "Net-(D1-K)":
        if (-75 <= x1 <= -48 or -75 <= x2 <= -48) and (45.5 <= y1 <= 49.5 or 45.5 <= y2 <= 49.5):
            tracks_to_delete.append(t)
    # Delete Net-(LED8-DOUT) tracks/vias near LED8/LED9
    elif t.GetNetname() == "Net-(LED8-DOUT)":
        if (-70 <= x1 <= -54 or -70 <= x2 <= -54) and (46.5 <= y1 <= 50.5 or 46.5 <= y2 <= 50.5):
            tracks_to_delete.append(t)
    # Delete Net-(LED7-DOUT) tracks entering LED8.4
    elif t.GetNetname() == "Net-(LED7-DOUT)":
        if (-51 <= x1 <= -48 or -51 <= x2 <= -48) and (46.0 <= y1 <= 48.0 or 46.0 <= y2 <= 48.0):
            tracks_to_delete.append(t)
    # Delete Net-(LED10-DIN) tracks entering LED9.2
    elif t.GetNetname() == "Net-(LED10-DIN)":
        if (-75 <= x1 <= -73 or -75 <= x2 <= -73) and (48.0 <= y1 <= 50.0 or 48.0 <= y2 <= 50.0):
            tracks_to_delete.append(t)
    # Delete GND stubs into LED8.3 and LED9.3
    elif t.GetNetname() == "GND":
        if ((-50.5 <= x1 <= -49 or -50.5 <= x2 <= -49) and (48.5 <= y1 <= 50.0 or 48.5 <= y2 <= 50.0)) or \
           ((-69.5 <= x1 <= -68 or -69.5 <= x2 <= -68) and (48.5 <= y1 <= 50.5 or 48.5 <= y2 <= 50.5)):
            tracks_to_delete.append(t)

for t in tracks_to_delete:
    b.Delete(t)

print(f"Deleted {len(tracks_to_delete)} old tracks/vias near LED8/LED9.")

# Set new positions
led8.SetPosition(pt(-52.3875, TARGET_Y))
led9.SetPosition(pt(-71.4375, TARGET_Y))

netinfo = b.GetNetInfo()
net_d1k = netinfo.GetNetItem("Net-(D1-K)")
net_led8dout = netinfo.GetNetItem("Net-(LED8-DOUT)")
net_led7dout = netinfo.GetNetItem("Net-(LED7-DOUT)")
net_led10din = netinfo.GetNetItem("Net-(LED10-DIN)")
net_gnd = netinfo.GetNetItem("GND")

def add_trk(net, pts, layer=pcbnew.B_Cu, width=0.25):
    for i in range(len(pts)-1):
        t = pcbnew.PCB_TRACK(b)
        t.SetLayer(layer)
        t.SetNet(net)
        t.SetStart(pt(pts[i][0], pts[i][1]))
        t.SetEnd(pt(pts[i+1][0], pts[i+1][1]))
        t.SetWidth(mm(width))
        b.Add(t)

def add_via(net, x, y, drill=0.30, size=0.60):
    v = pcbnew.PCB_VIA(b)
    v.SetPosition(pt(x, y))
    v.SetDrill(mm(drill))
    v.SetWidth(mm(size))
    v.SetNet(net)
    b.Add(v)

# --- Re-route LED8 ---
# Pad 1 (Net-(D1-K)) at (-55.1875, 46.9500)
# Pad 2 (Net-(LED8-DOUT)) at (-55.1875, 48.3500)
# Pad 3 (GND) at (-49.5875, 48.3500)
# Pad 4 (Net-(LED7-DOUT)) at (-49.5875, 46.9500)

# 1. LED8 Pad 3 (GND)
add_trk(net_gnd, [(-49.5875, 48.3500), (-49.2875, 48.6500), (-49.2875, 58.288)], layer=pcbnew.B_Cu, width=0.25)

# 2. LED8 Pad 4 (Net-(LED7-DOUT))
add_trk(net_led7dout, [(-48.432, 45.7945), (-49.5875, 46.9500)], layer=pcbnew.B_Cu, width=0.25)

# 3. LED8 Pad 1 (Net-(D1-K))
# Route F.Cu track along Y = 45.400 (well north of LED8 cutout Y in [46.10, 49.20])
add_trk(net_d1k, [(-48.500, 48.112), (-50.150, 45.400), (-56.500, 45.400), (-56.500, 46.9500)], layer=pcbnew.F_Cu, width=0.25)
add_via(net_d1k, -56.500, 46.9500)
add_trk(net_d1k, [(-56.500, 46.9500), (-55.1875, 46.9500)], layer=pcbnew.B_Cu, width=0.25)

# 4. LED8 Pad 2 (Net-(LED8-DOUT))
# Route B.Cu to via at (-61.000, 48.350)
add_trk(net_led8dout, [(-55.1875, 48.3500), (-61.000, 48.3500)], layer=pcbnew.B_Cu, width=0.25)
add_via(net_led8dout, -61.000, 48.3500)
# F.Cu track to LED9 Pad 4 (-68.6375, 46.9500)
add_trk(net_led8dout, [(-61.000, 48.3500), (-67.000, 48.3500), (-68.400, 46.9500), (-68.6375, 46.9500)], layer=pcbnew.F_Cu, width=0.25)
add_via(net_led8dout, -68.6375, 46.9500)

# --- Re-route LED9 ---
# Pad 1 (Net-(D1-K)) at (-74.2375, 46.9500)
# Pad 2 (Net-(LED10-DIN)) at (-74.2375, 48.3500)
# Pad 3 (GND) at (-68.6375, 48.3500)
# Pad 4 (Net-(LED8-DOUT)) at (-68.6375, 46.9500)

# 1. LED9 Pad 3 (GND)
add_trk(net_gnd, [(-68.6375, 48.3500), (-68.3375, 48.6500), (-68.3375, 58.288)], layer=pcbnew.B_Cu, width=0.25)

# 2. LED9 Pad 1 (Net-(D1-K))
add_trk(net_d1k, [(-74.350, 48.625), (-74.350, 46.9500), (-74.2375, 46.9500)], layer=pcbnew.F_Cu, width=0.25)
add_via(net_d1k, -74.2375, 46.9500)

# 3. LED9 Pad 2 (Net-(LED10-DIN))
add_trk(net_led10din, [(-74.300, 49.413), (-74.300, 48.3500), (-74.2375, 48.3500)], layer=pcbnew.B_Cu, width=0.25)

filler = pcbnew.ZONE_FILLER(b)
filler.Fill(b.Zones())
b.Save(TEST_PCB)
print("Saved perfect left thumb LEDs to", TEST_PCB)
