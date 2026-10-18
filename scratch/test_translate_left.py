import pcbnew
import json

LEFT_PCB = r"pcbs/curcur40/left/curcur40-left.kicad_pcb"
TEST_PCB = r"scratch/test_translate_leds.kicad_pcb"

b = pcbnew.LoadBoard(LEFT_PCB)

def mm(v): return pcbnew.FromMM(float(v))
def pt(x, y): return pcbnew.VECTOR2I(mm(x), mm(y))

TARGET_Y = 47.6500

led8 = b.FindFootprintByReference("LED8")
led9 = b.FindFootprintByReference("LED9")

dy8 = TARGET_Y - led8.GetPosition().y / 1e6 # -0.6625
dy9 = TARGET_Y - led9.GetPosition().y / 1e6 # -1.0625

print(f"dy8 = {dy8:.4f}, dy9 = {dy9:.4f}")

# Move footprints
led8.SetPosition(pt(-52.3875, TARGET_Y))
led9.SetPosition(pt(-71.4375, TARGET_Y))

# For each LED, find the local tracks and vias that move with it:
for t in b.GetTracks():
    p1, p2 = t.GetStart(), t.GetEnd()
    x1, y1 = p1.x/1e6, p1.y/1e6
    x2, y2 = p2.x/1e6, p2.y/1e6
    is_via = (t.GetClass() == "PCB_VIA")
    
    # LED8 cluster: X in [-57, -48], Y in [46.0, 50.5]
    if (-57 <= x1 <= -48 and -57 <= x2 <= -48) and (46.0 <= y1 <= 50.5 and 46.0 <= y2 <= 50.5):
        if t.GetNetname() in ["Net-(D1-K)", "Net-(LED8-DOUT)", "GND", "Net-(LED7-DOUT)"]:
            t.SetStart(pt(x1, y1 + dy8))
            t.SetEnd(pt(x2, y2 + dy8))
    # Vertical track for Net-(LED7-DOUT) from LED7: adjust its south end
    elif t.GetNetname() == "Net-(LED7-DOUT)" and abs(x1 - (-48.432)) < 0.1 and abs(x2 - (-48.432)) < 0.1:
        if y2 > 40:
            t.SetEnd(pt(x2, y2 + dy8))
    # Vertical track for GND south into switch: adjust its north end
    elif t.GetNetname() == "GND" and abs(x1 - (-49.288)) < 0.1 and abs(x2 - (-49.288)) < 0.1:
        if y1 < 52:
            t.SetStart(pt(x1, y1 + dy8))
            
    # LED9 cluster: X in [-75, -67], Y in [47.0, 51.0]
    if (-75 <= x1 <= -67 and -75 <= x2 <= -67) and (47.0 <= y1 <= 51.0 and 47.0 <= y2 <= 51.0):
        if t.GetNetname() in ["Net-(D1-K)", "Net-(LED10-DIN)", "GND", "Net-(LED8-DOUT)"]:
            t.SetStart(pt(x1, y1 + dy9))
            t.SetEnd(pt(x2, y2 + dy9))
    # Vertical track for Net-(D1-K) from SW18: adjust its south end
    elif t.GetNetname() == "Net-(D1-K)" and abs(x1 - (-74.350)) < 0.1 and abs(x2 - (-74.350)) < 0.1:
        if y2 < 50:
            t.SetEnd(pt(x2, y2 + dy9))
    # Vertical track for Net-(LED10-DIN) south to SW10: adjust its north end
    elif t.GetNetname() == "Net-(LED10-DIN)" and abs(x1 - (-74.300)) < 0.1 and abs(x2 - (-74.300)) < 0.1:
        if y2 < 52:
            t.SetEnd(pt(x2, y2 + dy9))
    # Vertical track for GND south into switch: adjust its north end
    elif t.GetNetname() == "GND" and abs(x1 - (-68.338)) < 0.1 and abs(x2 - (-68.338)) < 0.1:
        if y1 < 52:
            t.SetStart(pt(x1, y1 + dy9))

filler = pcbnew.ZONE_FILLER(b)
filler.Fill(b.Zones())
b.Save(TEST_PCB)
print("Saved to", TEST_PCB)
