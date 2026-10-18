import pcbnew
import json

RIGHT_PCB = r"pcbs/curcur40/right/curcur40-right.kicad_pcb"
TEST_PCB = r"scratch/perfect_right_thumb_leds.kicad_pcb"

b = pcbnew.LoadBoard(RIGHT_PCB)

def mm(v): return pcbnew.FromMM(float(v))
def pt(x, y): return pcbnew.VECTOR2I(mm(x), mm(y))

TARGET_Y = 47.6500

rled1 = b.FindFootprintByReference("rLED1")
rled8 = b.FindFootprintByReference("rLED8")
rled9 = b.FindFootprintByReference("rLED9")

# 1. Identify and delete specific tracks/vias connecting to rLED1, rLED8, rLED9
tracks_to_delete = []
for t in b.GetTracks():
    p1, p2 = t.GetStart(), t.GetEnd()
    x1, y1 = p1.x/1e6, p1.y/1e6
    x2, y2 = p2.x/1e6, p2.y/1e6
    is_via = (t.GetClass() == "PCB_VIA")
    
    # Net-(rD1-K) in thumb area:
    if t.GetNetname() == "Net-(rD1-K)":
        if (27 <= x1 <= 70 or 27 <= x2 <= 70) and (45.0 <= y1 <= 49.5 or 45.0 <= y2 <= 49.5):
            tracks_to_delete.append(t)
            
    # Net-(rLED1-DOUT):
    elif t.GetNetname() == "Net-(rLED1-DOUT)":
        if (28 <= x1 <= 32 or 28 <= x2 <= 32) and (48.0 <= y1 <= 51.0 or 48.0 <= y2 <= 51.0):
            tracks_to_delete.append(t)
            
    # /LED into rLED1.4:
    elif t.GetNetname() == "/LED":
        if abs(x1 - 36.138) < 0.05 and abs(x2 - 36.138) < 0.05 and max(y1, y2) > 45:
            tracks_to_delete.append(t)
            
    # Net-(rLED8-DOUT):
    elif t.GetNetname() == "Net-(rLED8-DOUT)":
        if (49 <= x1 <= 51 or 49 <= x2 <= 51) and (48.5 <= y1 <= 51.0 or 48.5 <= y2 <= 51.0):
            tracks_to_delete.append(t)
        elif (73 <= x1 <= 75 or 73 <= x2 <= 75) and (47.5 <= y1 <= 50.0 or 47.5 <= y2 <= 50.0):
            tracks_to_delete.append(t)
            
    # Net-(rLED7-DOUT) into rLED8.4:
    elif t.GetNetname() == "Net-(rLED7-DOUT)":
        if (55 <= x1 <= 57 or 55 <= x2 <= 57) and (47.0 <= y1 <= 49.5 or 47.0 <= y2 <= 49.5):
            tracks_to_delete.append(t)
            
    # Net-(rLED10-DIN):
    elif t.GetNetname() == "Net-(rLED10-DIN)":
        if (59 <= x1 <= 70 or 59 <= x2 <= 70) and (47.5 <= y1 <= 51.0 or 47.5 <= y2 <= 51.0):
            tracks_to_delete.append(t)
            
    # GNDR stubs into rLED1.3, rLED8.3, rLED9.3:
    elif t.GetNetname() == "GNDR":
        if (abs(x1 - 36.138) < 0.05 and abs(y1 - 49.413) < 0.05) or \
           (abs(x1 - 55.188) < 0.05 and abs(y1 - 49.663) < 0.05) or \
           (abs(x1 - 73.737) < 0.05 and abs(y1 - 49.413) < 0.05):
            tracks_to_delete.append(t)

for t in tracks_to_delete:
    b.Delete(t)

print(f"Deleted {len(tracks_to_delete)} tracks on Right PCB.")

# Move footprints
rled1.SetPosition(pt(33.3375, TARGET_Y))
rled8.SetPosition(pt(52.3875, TARGET_Y))
rled9.SetPosition(pt(71.4375, TARGET_Y))

netinfo = b.GetNetInfo()
net_rd1k = netinfo.GetNetItem("Net-(rD1-K)")
net_rled1dout = netinfo.GetNetItem("Net-(rLED1-DOUT)")
net_rled8dout = netinfo.GetNetItem("Net-(rLED8-DOUT)")
net_rled7dout = netinfo.GetNetItem("Net-(rLED7-DOUT)")
net_rled10din = netinfo.GetNetItem("Net-(rLED10-DIN)")
net_led = netinfo.GetNetItem("/LED")
net_gndr = netinfo.GetNetItem("GNDR")

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

# --- rLED1 Wiring ---
# Pad 1 (Net-(rD1-K)): (30.5375, 46.9500)
# Pad 2 (Net-(rLED1-DOUT)): (30.5375, 48.3500)
# Pad 3 (GNDR): (36.1375, 48.3500)
# Pad 4 (/LED): (36.1375, 46.9500)

# Pad 3 GNDR:
add_trk(net_gndr, [(36.1375, 48.3500), (36.438, 48.6500), (36.438, 49.712)], layer=pcbnew.B_Cu, width=0.25)

# Pad 4 /LED:
add_trk(net_led, [(36.138, 42.600), (36.1375, 46.9500)], layer=pcbnew.B_Cu, width=0.25)

# Pad 2 Net-(rLED1-DOUT):
add_trk(net_rled1dout, [(30.5375, 48.3500), (29.800, 48.3500)], layer=pcbnew.B_Cu, width=0.25)
add_via(net_rled1dout, 29.800, 48.3500)
add_trk(net_rled1dout, [(26.444, 49.413), (27.507, 48.3500), (29.800, 48.3500)], layer=pcbnew.F_Cu, width=0.25)

# Pad 1 Net-(rD1-K):
add_trk(net_rd1k, [(30.5375, 46.9500), (29.800, 46.9500)], layer=pcbnew.B_Cu, width=0.25)
add_via(net_rd1k, 29.800, 46.9500)
add_trk(net_rd1k, [(27.188, 39.225), (27.188, 45.400), (29.800, 45.400), (29.800, 46.9500)], layer=pcbnew.F_Cu, width=0.25)

# Net-(rD1-K) highway east across to rLED8:
# Route on F.Cu at Y = 45.400 (well north of rLED1 and rLED8 cutouts):
add_trk(net_rd1k, [(29.800, 45.400), (48.800, 45.400), (48.800, 46.9500)], layer=pcbnew.F_Cu, width=0.25)

# --- rLED8 Wiring ---
# Pad 1 (Net-(rD1-K)): (49.5875, 46.9500)
# Pad 2 (Net-(rLED8-DOUT)): (49.5875, 48.3500)
# Pad 3 (GNDR): (55.1875, 48.3500)
# Pad 4 (Net-(rLED7-DOUT)): (55.1875, 46.9500)

# Pad 1 Net-(rD1-K):
add_via(net_rd1k, 48.800, 46.9500)
add_trk(net_rd1k, [(48.800, 46.9500), (49.5875, 46.9500)], layer=pcbnew.B_Cu, width=0.25)

# Pad 2 Net-(rLED8-DOUT):
add_trk(net_rled8dout, [(49.5875, 48.3500), (49.400, 48.5375), (49.400, 49.850)], layer=pcbnew.B_Cu, width=0.25)

# Pad 3 GNDR:
add_trk(net_gndr, [(55.1875, 48.3500), (55.487, 48.6500), (55.487, 49.962)], layer=pcbnew.B_Cu, width=0.25)

# Pad 4 Net-(rLED7-DOUT):
add_trk(net_rled7dout, [(56.200, 46.712), (55.950, 46.9500), (55.1875, 46.9500)], layer=pcbnew.B_Cu, width=0.25)

# Net-(rD1-K) highway east from rLED8 to rLED9:
# Along Y = 45.400 on F.Cu:
add_trk(net_rd1k, [(48.800, 45.400), (67.800, 45.400), (67.800, 46.9500)], layer=pcbnew.F_Cu, width=0.25)

# --- rLED9 Wiring ---
# Pad 1 (Net-(rD1-K)): (68.6375, 46.9500)
# Pad 2 (Net-(rLED10-DIN)): (68.6375, 48.3500)
# Pad 3 (GNDR): (73.7375, 48.3500)
# Pad 4 (Net-(rLED8-DOUT)): (73.7375, 46.9500)

# Pad 1 Net-(rD1-K):
add_via(net_rd1k, 67.800, 46.9500)
add_trk(net_rd1k, [(67.800, 46.9500), (68.6375, 46.9500)], layer=pcbnew.B_Cu, width=0.25)

# Pad 2 Net-(rLED10-DIN):
add_trk(net_rled10din, [(68.6375, 48.3500), (67.800, 48.3500)], layer=pcbnew.B_Cu, width=0.25)
add_via(net_rled10din, 67.800, 48.3500)
add_trk(net_rled10din, [(59.500, 40.885), (59.500, 48.3500), (67.800, 48.3500)], layer=pcbnew.F_Cu, width=0.25)

# Pad 3 GNDR:
add_trk(net_gndr, [(73.7375, 48.3500), (74.537, 49.1500), (74.537, 50.212)], layer=pcbnew.B_Cu, width=0.25)

# Pad 4 Net-(rLED8-DOUT):
add_trk(net_rled8dout, [(74.350, 60.163), (74.350, 47.5625), (73.7375, 46.9500)], layer=pcbnew.F_Cu, width=0.25)
add_via(net_rled8dout, 73.7375, 46.9500)

filler = pcbnew.ZONE_FILLER(b)
filler.Fill(b.Zones())
b.Save(TEST_PCB)
print("Saved perfect right thumb LEDs to", TEST_PCB)
