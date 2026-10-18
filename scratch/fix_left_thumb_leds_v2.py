import pcbnew
import json

LEFT_PCB = r"pcbs/curcur40/left/curcur40-left.kicad_pcb"
TEST_PCB = r"scratch/perfect_left_thumb_leds_v2.kicad_pcb"

b = pcbnew.LoadBoard(LEFT_PCB)

def mm(v): return pcbnew.FromMM(float(v))
def pt(x, y): return pcbnew.VECTOR2I(mm(x), mm(y))

TARGET_Y = 47.6500

led8 = b.FindFootprintByReference("LED8")
led9 = b.FindFootprintByReference("LED9")

# 1. Identify and delete ONLY the specific tracks/vias that connect directly to LED8 and LED9:
tracks_to_delete = []
for t in b.GetTracks():
    p1, p2 = t.GetStart(), t.GetEnd()
    x1, y1 = p1.x/1e6, p1.y/1e6
    x2, y2 = p2.x/1e6, p2.y/1e6
    is_via = (t.GetClass() == "PCB_VIA")
    
    # LED8.1 (Net-(D1-K)):
    if t.GetNetname() == "Net-(D1-K)":
        # The via at (-56.000, 47.612) and B.Cu stub to LED8.1
        if (-56.5 <= x1 <= -55.0 and -56.5 <= x2 <= -55.0) and (47.0 <= y1 <= 48.0 and 47.0 <= y2 <= 48.0):
            tracks_to_delete.append(t)
        # F.Cu track segment ending at the via (-56.000, 47.612)
        if not is_via and t.GetLayerName() == "F.Cu":
            if abs(x2 - (-56.000)) < 0.01 and abs(y2 - 47.612) < 0.01:
                tracks_to_delete.append(t)
            elif abs(x1 - (-56.000)) < 0.01 and abs(y1 - 46.462) < 0.01:
                tracks_to_delete.append(t)
            elif abs(x2 - (-56.000)) < 0.01 and abs(y2 - 46.462) < 0.01:
                tracks_to_delete.append(t)
            elif abs(x2 - (-73.737)) < 0.01 and abs(y2 - 48.013) < 0.01: # LED9.1 F.Cu incoming
                tracks_to_delete.append(t)
            elif abs(x2 - (-74.350)) < 0.01 and abs(y2 - 48.625) < 0.01 and y1 > 50: # SW18 D1-K vertical
                tracks_to_delete.append(t)
        if is_via and abs(x1 - (-73.737)) < 0.01 and abs(y1 - 48.013) < 0.01: # LED9.1 via
            tracks_to_delete.append(t)
            
    # Net-(LED8-DOUT):
    elif t.GetNetname() == "Net-(LED8-DOUT)":
        tracks_to_delete.append(t)
        
    # Net-(LED7-DOUT):
    elif t.GetNetname() == "Net-(LED7-DOUT)":
        # Only the B.Cu diagonal stub entering LED8.4: (-48.432, 46.458) -> (-49.587, 47.612)
        if abs(x1 - (-48.432)) < 0.01 and abs(y1 - 46.458) < 0.01 and abs(x2 - (-49.587)) < 0.01:
            tracks_to_delete.append(t)
            
    # Net-(LED10-DIN):
    elif t.GetNetname() == "Net-(LED10-DIN)":
        # The B.Cu track entering LED9.2: (-74.300, 49.413) -> (-73.737, 49.413)
        if abs(x2 - (-73.737)) < 0.01 and abs(y2 - 49.413) < 0.01:
            tracks_to_delete.append(t)
        # Vertical B.Cu track from (-74.300, 62.002) to (-74.300, 49.413)
        if abs(x1 - (-74.300)) < 0.01 and abs(x2 - (-74.300)) < 0.01 and max(y1, y2) > 55:
            tracks_to_delete.append(t)
            
    # GND stubs:
    elif t.GetNetname() == "GND":
        if abs(x1 - (-49.587)) < 0.01 and abs(y1 - 49.013) < 0.01: # LED8.3 GND
            tracks_to_delete.append(t)
        elif abs(x1 - (-68.638)) < 0.01 and abs(y1 - 49.413) < 0.01: # LED9.3 GND
            tracks_to_delete.append(t)

for t in tracks_to_delete:
    b.Delete(t)

print(f"Deleted {len(tracks_to_delete)} specific tracks.")

# Move footprints
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

# --- LED8 Wiring ---
# Pad 1 (Net-(D1-K)) at (-55.1875, 46.9500)
# Pad 2 (Net-(LED8-DOUT)) at (-55.1875, 48.3500)
# Pad 3 (GND) at (-49.5875, 48.3500)
# Pad 4 (Net-(LED7-DOUT)) at (-49.5875, 46.9500)

# 1. LED8 Pad 3 GND: connect to (-49.288, 49.312)
add_trk(net_gnd, [(-49.5875, 48.3500), (-49.288, 48.6500), (-49.288, 49.312)], layer=pcbnew.B_Cu, width=0.25)

# 2. LED8 Pad 4 Net-(LED7-DOUT): connect from (-48.432, 46.458)
add_trk(net_led7dout, [(-48.432, 46.458), (-48.924, 46.9500), (-49.5875, 46.9500)], layer=pcbnew.B_Cu, width=0.25)

# 3. LED8 Pad 1 Net-(D1-K):
# Incoming from (-50.150, 46.462) on F.Cu:
# Route along Y = 45.400 (well north of LED8 cutout Y in [46.10, 49.20])
add_trk(net_d1k, [(-50.150, 46.462), (-50.650, 45.400), (-56.500, 45.400), (-56.500, 46.9500)], layer=pcbnew.F_Cu, width=0.25)
add_via(net_d1k, -56.500, 46.9500)
add_trk(net_d1k, [(-56.500, 46.9500), (-55.1875, 46.9500)], layer=pcbnew.B_Cu, width=0.25)

# 4. Net-(LED8-DOUT) from LED8.2 to LED9.4:
# LED8.2 is at (-55.1875, 48.3500) on B.Cu
# LED9.4 is at (-68.6375, 46.9500) on B.Cu
add_trk(net_led8dout, [(-55.1875, 48.3500), (-61.000, 48.3500), (-61.000, 49.8000)], layer=pcbnew.B_Cu, width=0.25)
add_via(net_led8dout, -61.000, 49.8000)
add_trk(net_led8dout, [(-61.000, 49.8000), (-67.000, 49.8000), (-68.6375, 48.1625), (-68.6375, 46.9500)], layer=pcbnew.F_Cu, width=0.25)
add_via(net_led8dout, -68.6375, 46.9500)

# --- LED9 Wiring ---
# Pad 1 (Net-(D1-K)) at (-74.2375, 46.9500)
# Pad 2 (Net-(LED10-DIN)) at (-74.2375, 48.3500)
# Pad 3 (GND) at (-68.6375, 48.3500)
# Pad 4 (Net-(LED8-DOUT)) at (-68.6375, 46.9500)

# 1. LED9 Pad 3 GND: connect to (-68.338, 49.712)
add_trk(net_gnd, [(-68.6375, 48.3500), (-68.338, 48.6500), (-68.338, 49.712)], layer=pcbnew.B_Cu, width=0.25)

# 2. LED9 Pad 1 Net-(D1-K):
# From (-74.350, 57.763) on F.Cu:
add_trk(net_d1k, [(-74.350, 57.763), (-74.350, 46.9500), (-74.2375, 46.9500)], layer=pcbnew.F_Cu, width=0.25)
add_via(net_d1k, -74.2375, 46.9500)

# 3. LED9 Pad 2 Net-(LED10-DIN):
# From (-74.300, 62.002) down on B.Cu to Y = 48.3500, then into Pad 2 (-74.2375, 48.3500)
add_trk(net_led10din, [(-74.300, 62.002), (-74.300, 48.3500), (-74.2375, 48.3500)], layer=pcbnew.B_Cu, width=0.25)

filler = pcbnew.ZONE_FILLER(b)
filler.Fill(b.Zones())
b.Save(TEST_PCB)
print("Saved perfect left thumb LEDs v2 to", TEST_PCB)
