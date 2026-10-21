import pcbnew
import subprocess
import os

KICAD_CLI = os.path.expandvars(r"%LOCALAPPDATA%\Programs\KiCad\10.0\bin\kicad-cli.exe")
PCB_PATH = "pcbs/curcur40/right/curcur40-right.kicad_pcb"
board = pcbnew.LoadBoard(PCB_PATH)

# Make sure U1 Pin 13 is net /NCS
net_ncs = board.FindNet("/NCS")
u1 = board.FindFootprintByReference("U1")
pad13 = u1.FindPadByNumber("13")
if pad13 and pad13.GetNetname() != "/NCS":
    pad13.SetNet(net_ncs)
    print("Set U1 Pad 13 to net /NCS")

net_gndr = board.FindNet("GNDR")
net_3v3r = board.FindNet("+3V3R")
net_1v8 = board.FindNet("+1V8_PMW")
net_vio = board.FindNet("V_{IO}")
net_sclk = board.FindNet("/SCLK")
net_mosi = board.FindNet("/MOSI")
net_miso = board.FindNet("/MISO")
net_reset = board.FindNet("/RESET")
net_led = board.FindNet("Net-(U1-LED_P)")
net_u2nc = board.FindNet("Net-(U2-NC)")

def add_track(b, start_xy, end_xy, layer, net, width_mm=0.25):
    t = pcbnew.PCB_TRACK(b)
    t.SetStart(pcbnew.VECTOR2I_MM(start_xy[0], start_xy[1]))
    t.SetEnd(pcbnew.VECTOR2I_MM(end_xy[0], end_xy[1]))
    t.SetLayer(layer)
    t.SetWidth(pcbnew.FromMM(width_mm))
    t.SetNet(net)
    b.Add(t)
    return t

def add_via(b, xy, net, drill_mm=0.3, width_mm=0.6):
    v = pcbnew.PCB_VIA(b)
    v.SetPosition(pcbnew.VECTOR2I_MM(xy[0], xy[1]))
    v.SetDrill(pcbnew.FromMM(drill_mm))
    v.SetWidth(pcbnew.FromMM(width_mm))
    v.SetNet(net)
    b.Add(v)
    return v

# 1. SPI Lines
# /NCS: incoming at (-0.7250, 48.5925) on F.Cu -> U1 Pin 13 (14.8750, 52.3255)
add_track(board, (-0.7250, 48.5925), (2.5, 48.5925), pcbnew.F_Cu, net_ncs)
add_track(board, (2.5, 48.5925), (6.2, 52.3255), pcbnew.F_Cu, net_ncs)
add_track(board, (6.2, 52.3255), (14.8750, 52.3255), pcbnew.F_Cu, net_ncs)

# /MISO: incoming at (-0.7250, 51.1325) on B.Cu -> U1 Pin 12 (14.8750, 50.5455) & R2 Pin 2 (18.7985, 43.3617)
add_track(board, (-0.7250, 51.1325), (14.8750, 50.5455), pcbnew.B_Cu, net_miso)
add_track(board, (14.8750, 50.5455), (16.2, 50.5455), pcbnew.B_Cu, net_miso)
add_track(board, (16.2, 50.5455), (16.2, 43.3617), pcbnew.B_Cu, net_miso)
add_track(board, (16.2, 43.3617), (18.7985, 43.3617), pcbnew.B_Cu, net_miso)

# /MOSI: incoming at (-0.7250, 53.6725) on B.Cu -> U1 Pin 11 (14.8750, 48.7655)
add_track(board, (-0.7250, 53.6725), (1.5, 53.6725), pcbnew.B_Cu, net_mosi)
add_via(board, (1.5, 53.6725), net_mosi)
add_track(board, (1.5, 53.6725), (1.5, 48.7655), pcbnew.F_Cu, net_mosi)
add_track(board, (1.5, 48.7655), (14.8750, 48.7655), pcbnew.F_Cu, net_mosi)

# /SCLK: incoming at (-0.7250, 56.2125) on B.Cu -> U1 Pin 10 (14.8750, 46.9855)
add_track(board, (-0.7250, 56.2125), (0.2, 56.2125), pcbnew.B_Cu, net_sclk)
add_via(board, (0.2, 56.2125), net_sclk)
add_track(board, (0.2, 56.2125), (0.2, 46.9855), pcbnew.F_Cu, net_sclk)
add_track(board, (0.2, 46.9855), (14.8750, 46.9855), pcbnew.F_Cu, net_sclk)

# 2. Control Lines
# /RESET: U1 Pin 7 (4.1750, 47.8755) -> R1 Pin 2 (18.7985, 45.3617)
add_track(board, (4.1750, 47.8755), (4.1750, 45.3617), pcbnew.F_Cu, net_reset)
add_track(board, (4.1750, 45.3617), (18.0, 45.3617), pcbnew.F_Cu, net_reset)
add_via(board, (18.0, 45.3617), net_reset)
add_track(board, (18.0, 45.3617), (18.7985, 45.3617), pcbnew.B_Cu, net_reset)

# Net-(U1-LED_P): U1 Pin 15 (14.8750, 55.8855) -> R3 Pin 2 (6.9735, 41.6617)
add_track(board, (14.8750, 55.8855), (13.2, 55.8855), pcbnew.F_Cu, net_led)
add_track(board, (13.2, 55.8855), (13.2, 40.5), pcbnew.F_Cu, net_led)
add_track(board, (13.2, 40.5), (6.9735, 40.5), pcbnew.F_Cu, net_led)
add_via(board, (6.9735, 40.5), net_led)
add_track(board, (6.9735, 40.5), (6.9735, 41.6617), pcbnew.B_Cu, net_led)

# Net-(U2-NC): U2 Pin 4 (7.2485, 64.6117) -> C5 Pin 1 (18.2485, 64.0617) & R4 Pin 2 (18.2985, 62.0617)
add_track(board, (18.2985, 62.0617), (18.2485, 64.0617), pcbnew.B_Cu, net_u2nc)
add_via(board, (18.2485, 65.5), net_u2nc)
add_track(board, (18.2485, 64.0617), (18.2485, 65.5), pcbnew.B_Cu, net_u2nc)
add_track(board, (18.2485, 65.5), (7.2485, 65.5), pcbnew.F_Cu, net_u2nc)
add_via(board, (7.2485, 65.5), net_u2nc)
add_track(board, (7.2485, 65.5), (7.2485, 64.6117), pcbnew.B_Cu, net_u2nc)

# 3. V_{IO}
# JP1 Pin 2 (17.7750, 50.1457) -> R1 Pin 1 (16.9735, 45.3617), R2 Pin 1 (16.9735, 43.3617), U1 Pin 5 (4.1750, 51.4355)
add_track(board, (16.9735, 43.3617), (16.9735, 45.3617), pcbnew.B_Cu, net_vio)
add_track(board, (16.9735, 45.3617), (16.9735, 50.1457), pcbnew.B_Cu, net_vio)
add_track(board, (16.9735, 50.1457), (17.7750, 50.1457), pcbnew.B_Cu, net_vio)
add_track(board, (16.9735, 50.1457), (16.0, 50.1457), pcbnew.B_Cu, net_vio)
add_track(board, (16.0, 50.1457), (16.0, 51.4355), pcbnew.B_Cu, net_vio)
add_track(board, (16.0, 51.4355), (4.1750, 51.4355), pcbnew.B_Cu, net_vio)

# 4. +1V8_PMW
# U2 Pin 5 (7.2485, 62.7117) -> C4 Pin 1 (11.4860, 62.7992) -> R4 Pin 1 (16.4735, 62.0617)
# -> C2 Pin 1 (18.7485, 55.8957) -> C1 Pin 1 (18.7485, 54.1457) -> JP1 Pin 3 (17.7750, 51.4457)
# -> U1 Pin 3 (4.1750, 54.9955) & Pin 4 (4.1750, 53.2155) -> R3 Pin 1 (8.7985, 41.6617)
add_track(board, (7.2485, 62.7117), (11.4860, 62.7992), pcbnew.B_Cu, net_1v8, width_mm=0.35)
add_track(board, (11.4860, 62.7992), (16.4735, 62.0617), pcbnew.B_Cu, net_1v8, width_mm=0.35)
add_track(board, (16.4735, 62.0617), (19.8, 62.0617), pcbnew.B_Cu, net_1v8, width_mm=0.35)
add_track(board, (19.8, 62.0617), (19.8, 55.8957), pcbnew.B_Cu, net_1v8, width_mm=0.35)
add_track(board, (19.8, 55.8957), (18.7485, 55.8957), pcbnew.B_Cu, net_1v8, width_mm=0.35)
add_track(board, (18.7485, 55.8957), (18.7485, 54.1457), pcbnew.B_Cu, net_1v8, width_mm=0.35)
add_track(board, (18.7485, 54.1457), (18.7485, 51.4457), pcbnew.B_Cu, net_1v8, width_mm=0.35)
add_track(board, (18.7485, 51.4457), (17.7750, 51.4457), pcbnew.B_Cu, net_1v8, width_mm=0.35)

# Connect to U1 Pin 3 and Pin 4 via F.Cu
add_via(board, (19.8, 54.1457), net_1v8)
add_track(board, (19.8, 54.1457), (4.1750, 54.1457), pcbnew.F_Cu, net_1v8, width_mm=0.35)
add_track(board, (4.1750, 54.1457), (4.1750, 54.9955), pcbnew.F_Cu, net_1v8, width_mm=0.35)
add_track(board, (4.1750, 54.1457), (4.1750, 53.2155), pcbnew.F_Cu, net_1v8, width_mm=0.35)

# Connect U1 Pin 3 (4.1750, 54.9955) to R3 Pin 1 (8.7985, 41.6617)
add_track(board, (4.1750, 54.9955), (4.1750, 42.5), pcbnew.B_Cu, net_1v8, width_mm=0.35)
add_track(board, (4.1750, 42.5), (8.7985, 42.5), pcbnew.B_Cu, net_1v8, width_mm=0.35)
add_track(board, (8.7985, 42.5), (8.7985, 41.6617), pcbnew.B_Cu, net_1v8, width_mm=0.35)

# 5. +3V3R
# Incoming track (-0.7250, 46.0525) on F.Cu -> C3 Pin 1 (1.8860, 64.2242) -> U2 Pin 3 (9.5235, 64.6117) & Pin 1 (9.5235, 62.7117)
add_track(board, (-0.7250, 46.0525), (-0.7250, 64.2242), pcbnew.F_Cu, net_3v3r, width_mm=0.4)
add_via(board, (-0.7250, 64.2242), net_3v3r)
add_track(board, (-0.7250, 64.2242), (1.8860, 64.2242), pcbnew.B_Cu, net_3v3r, width_mm=0.4)
add_track(board, (1.8860, 64.2242), (9.5235, 64.6117), pcbnew.B_Cu, net_3v3r, width_mm=0.4)
add_track(board, (9.5235, 64.6117), (9.5235, 62.7117), pcbnew.B_Cu, net_3v3r, width_mm=0.4)

# Connect to JP1 Pin 1 (17.7750, 48.8457) on B.Cu
# Existing +3V3R track is at (20.0, 60.712)
add_track(board, (20.0, 60.712), (20.0, 48.8457), pcbnew.B_Cu, net_3v3r, width_mm=0.4)
add_track(board, (20.0, 48.8457), (17.7750, 48.8457), pcbnew.B_Cu, net_3v3r, width_mm=0.4)

# 6. GNDR Connections
# Connect SMD GND pads to GND plane via vias
add_via(board, (9.5235, 61.5), net_gndr)
add_track(board, (9.5235, 63.6617), (9.5235, 61.5), pcbnew.B_Cu, net_gndr, width_mm=0.35)

add_via(board, (1.8860, 61.2), net_gndr)
add_track(board, (1.8860, 62.4992), (1.8860, 61.2), pcbnew.B_Cu, net_gndr, width_mm=0.35)

add_via(board, (11.4860, 65.8), net_gndr)
add_track(board, (11.4860, 64.5242), (11.4860, 65.8), pcbnew.B_Cu, net_gndr, width_mm=0.35)

add_via(board, (16.5235, 65.5), net_gndr)
add_track(board, (16.5235, 64.0617), (16.5235, 65.5), pcbnew.B_Cu, net_gndr, width_mm=0.35)

add_track(board, (17.0235, 54.1457), (17.0235, 55.8957), pcbnew.B_Cu, net_gndr, width_mm=0.35)
add_via(board, (16.0, 55.0), net_gndr)
add_track(board, (17.0235, 55.0), (16.0, 55.0), pcbnew.B_Cu, net_gndr, width_mm=0.35)

# Connect U1 Pin 8 (PTH at 4.1750, 46.0955) to incoming GNDR track at (-0.7250, 43.5125)
add_track(board, (-0.7250, 43.5125), (4.1750, 43.5125), pcbnew.F_Cu, net_gndr, width_mm=0.4)
add_track(board, (4.1750, 43.5125), (4.1750, 46.0955), pcbnew.F_Cu, net_gndr, width_mm=0.4)

# Refill all zones
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

board.Save(PCB_PATH)
print("Saved routed board.")
