import pcbnew
import subprocess
import re
from pathlib import Path

TARGET_PCB = "scratch/test_clean.kicad_pcb"
TARGET_PRO = "scratch/test_clean.kicad_pro"

DEAD_STUBS = [
    "7dd8caa0-e0ec-4328-9359-e11e838afc78",
    "cca78c47-6ed6-402a-881a-9ecabf679da4",
    "de626d39-723b-4d4f-a77f-be0d6917e35e",
    "0e592887-f89b-4cbd-bd9a-1a7c0ca4d07e",
    "5434aa9a-bec4-4cf9-a5b0-2d31b9914dc3",
    "5a65bc72-1bca-4713-ab6c-fda0404686bb",
    "8e50b458-c280-4c85-a9f4-899e27803557",
    "0421ef6a-b236-49f4-9838-11a9a193e74c",
    "2f81a7ee-c63c-4164-82db-1a629d2ea3fa",
    "c036dd03-31ee-4b11-ba6d-13255176dedc",
    "e720b2c2-879b-48cc-a258-589fb75e26bf",
    "f1c48cec-dc6c-4014-a0e7-04df29c943d2",
    "3272d24a-e03b-4ef4-bc4a-cfe7b4bc7771",
    "50feb961-ce63-4319-9f53-20f34c92782e",
    "74209c90-d7cb-4a69-89c0-697b2f062ea7",
    "a207e794-754c-4f20-923f-00ab0d23be1f",
    "e41e7fc7-a5aa-48df-847e-e05ac583225f",
    "342256ce-1564-4692-bc7f-580472c86144",
    "787d6e71-65b3-4a6f-b78e-a2d7d166ecda",
    "b8ad9be3-135d-4409-8aa0-06399dcef1c0",
    "c66cee38-fa84-4961-90b4-34ffc325a265",
    "f9ff5571-2a2f-47cf-a162-b81268f1b988",
    "641eb885-feb9-470d-a712-431b092d0147",
    "c100eb31-44bd-432a-a260-686177818298",
    "dabf49da-b110-4530-a011-a731221fd294",
    "e4ad1662-dc8d-4f41-abe5-a71459cf3c58",
]

txt = subprocess.check_output(["git", "show", "20bc8a19:pcbs/curcur40/right/curcur40-right.kicad_pcb"], encoding="utf-8")

def remove_by_uuid(content, u):
    idx = content.find(u)
    if idx == -1: return content
    start = content.rfind('(segment', 0, idx)
    if start == -1: start = content.rfind('(via', 0, idx)
    if start == -1: return content
    real_start = content.rfind('\n', 0, start)
    real_start = real_start + 1 if real_start != -1 else start
    depth, end = 0, start
    while end < len(content):
        if content[end] == '(': depth += 1
        elif content[end] == ')':
            depth -= 1
            if depth == 0: break
        end += 1
    if end + 1 < len(content) and content[end+1] == '\n':
        end += 1
    return content[:real_start] + content[end+1:]

for u in DEAD_STUBS:
    txt = remove_by_uuid(txt, u)

def update_segment_coords(content, u, new_start, new_end):
    idx = content.find(u)
    if idx == -1: return content
    start = content.rfind('(segment', 0, idx)
    end = content.find(')', idx)
    seg_txt = content[start:end+1]
    seg_txt = re.sub(r'\(start\s+[\d\.\-]+\s+[\d\.\-]+\)', f'(start {new_start[0]} {new_start[1]})', seg_txt)
    seg_txt = re.sub(r'\(end\s+[\d\.\-]+\s+[\d\.\-]+\)', f'(end {new_end[0]} {new_end[1]})', seg_txt)
    return content[:start] + seg_txt + content[end+1:]

# Jog /TX on B.Cu: stay at X=19.200 past the NE screw hole (21.525, 41.0875), then jog to X=20.000 at Y=42.300 to clear R2 Pad 2
txt = update_segment_coords(txt, "c93696f3-c7b1-401f-9d93-13e7369537ca", (16.4, 39.2), (19.2, 42.0))
txt = update_segment_coords(txt, "29a0d305-14f2-427a-a8a7-56828070e13f", (19.2, 42.0), (20.0, 42.8))
txt = update_segment_coords(txt, "9bdeec8b-2ee5-43fa-9125-b7e91eff0fca", (20.0, 42.8), (20.0, 44.5))

# Trim /MISO, /MOSI, /SCLK arrival segments on B.Cu so each stops cleanly before the next inner line's via:
txt = update_segment_coords(txt, "2f89b3bf-61d3-4855-bf9c-d0f1bb6e77e8", (78.300, 61.2625), (19.100, 61.2625))
txt = update_segment_coords(txt, "0969c714-6562-4ffe-bc59-bdfb32431259", (78.950, 61.8125), (20.000, 61.8125))
txt = update_segment_coords(txt, "76f9bef9-74ce-46ef-87f6-b97989bb439e", (79.600, 62.3625), (24.000, 62.3625))

pro_src = Path("pcbs/curcur40/right/curcur40-right.kicad_pro")
Path(TARGET_PRO).write_bytes(pro_src.read_bytes())
Path(TARGET_PCB).write_text(txt, encoding="utf-8")

board = pcbnew.LoadBoard(TARGET_PCB)

# Fix U1 Pad 13 net assignment to /NCS
net_ncs = board.FindNet("/NCS")
u1 = board.FindFootprintByReference("U1")
pad13 = u1.FindPadByNumber("13")
pad13.SetNet(net_ncs)

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
net_tx = board.FindNet("/TX")

def add_track(b, p1, p2, layer, net, width_mm=0.25):
    t = pcbnew.PCB_TRACK(b)
    t.SetStart(pcbnew.VECTOR2I_MM(p1[0], p1[1]))
    t.SetEnd(pcbnew.VECTOR2I_MM(p2[0], p2[1]))
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

# Complete /TX jog from (20.0, 44.5) to (21.0, 44.5) on B.Cu:
add_track(board, (20.000, 44.500), (21.000, 44.500), pcbnew.B_Cu, net_tx, width_mm=0.25)

# ==============================================================================
# 1. SPI BUS (100% Planar on F.Cu, Jogged Vias on B.Cu for >= 0.30mm Clearance)
# ==============================================================================
# /MISO stops first at X=24.000 on B.Cu, jogs 0.20mm South to (24.000, 62.5625) away from /MOSI (Y=61.8125)
add_track(board, (24.000, 62.3625), (24.000, 62.5625), pcbnew.B_Cu, net_miso, width_mm=0.20)
add_via(board, (24.000, 62.5625), net_miso)
# On F.Cu: pass south of SE hole (21.525, 63.6875) along Y=65.550 to X=19.600, then (17.300, 63.250) -> North to U1 Pad 12
add_track(board, (24.000, 62.5625), (24.000, 65.550), pcbnew.F_Cu, net_miso, width_mm=0.20)
add_track(board, (24.000, 65.550), (19.600, 65.550), pcbnew.F_Cu, net_miso, width_mm=0.20)
add_track(board, (19.600, 65.550), (17.300, 63.250), pcbnew.F_Cu, net_miso, width_mm=0.20)
add_track(board, (17.300, 63.250), (17.300, 50.5455), pcbnew.F_Cu, net_miso, width_mm=0.20)
add_track(board, (17.300, 50.5455), (14.8750, 50.5455), pcbnew.F_Cu, net_miso, width_mm=0.20)
# Branch from (24.000, 62.5625) north along X=24.000 on F.Cu to R2 Pad 2 (18.7985, 43.3617):
add_track(board, (24.000, 62.5625), (24.000, 43.3617), pcbnew.F_Cu, net_miso, width_mm=0.20)
add_track(board, (24.000, 43.3617), (18.7985, 43.3617), pcbnew.F_Cu, net_miso, width_mm=0.20)
add_via(board, (18.7985, 43.3617), net_miso) # R2 Pad 2

# /MOSI stops at X=20.000 on B.Cu (where /MISO is already gone!), jogs to (20.000, 61.980) away from /SCLK (Y=61.2625)
add_track(board, (20.000, 61.8125), (20.000, 61.980), pcbnew.B_Cu, net_mosi, width_mm=0.20)
add_via(board, (20.000, 61.980), net_mosi)
add_track(board, (20.000, 61.980), (17.900, 61.980), pcbnew.F_Cu, net_mosi, width_mm=0.20)
add_track(board, (17.900, 61.980), (17.900, 48.7655), pcbnew.F_Cu, net_mosi, width_mm=0.20)
add_track(board, (17.900, 48.7655), (14.8750, 48.7655), pcbnew.F_Cu, net_mosi, width_mm=0.20)

# /SCLK stops at X=19.100 on B.Cu (where both +3V3R and /MOSI are already gone!), jogs to (19.100, 61.150) to clear R4 Pad 2
add_track(board, (19.100, 61.2625), (19.100, 61.150), pcbnew.B_Cu, net_sclk, width_mm=0.20)
add_via(board, (19.100, 61.150), net_sclk)
add_track(board, (19.100, 61.150), (18.500, 61.150), pcbnew.F_Cu, net_sclk, width_mm=0.20)
add_track(board, (18.500, 61.150), (18.500, 46.9855), pcbnew.F_Cu, net_sclk, width_mm=0.20)
add_track(board, (18.500, 46.9855), (14.8750, 46.9855), pcbnew.F_Cu, net_sclk, width_mm=0.20)

# ==============================================================================
# 2. /NCS (Chip Select, hops over /TX on F.Cu, runs in B.Cu X=16.050 corridor)
# ==============================================================================
add_track(board, (19.600, 40.300), (16.050, 40.300), pcbnew.F_Cu, net_ncs, width_mm=0.20)
add_via(board, (16.050, 40.300), net_ncs)
add_track(board, (16.050, 40.300), (16.050, 52.3255), pcbnew.B_Cu, net_ncs, width_mm=0.20)
add_track(board, (16.050, 52.3255), (14.8750, 52.3255), pcbnew.B_Cu, net_ncs, width_mm=0.20) # U1 Pad 13

# ==============================================================================
# 3. 4 Nested Planar Loops on F.Cu (North-West of U1)
# ==============================================================================

# --- Loop 1: /RESET ---
add_via(board, (18.7985, 45.3617), net_reset) # R1 Pad 2
add_track(board, (18.7985, 45.3617), (17.800, 45.3617), pcbnew.F_Cu, net_reset, width_mm=0.20)
add_track(board, (17.800, 45.3617), (17.800, 42.400), pcbnew.F_Cu, net_reset, width_mm=0.20)
add_track(board, (17.800, 42.400), (2.700, 42.400), pcbnew.F_Cu, net_reset, width_mm=0.20)
add_track(board, (2.700, 42.400), (2.700, 47.8755), pcbnew.F_Cu, net_reset, width_mm=0.20)
add_track(board, (2.700, 47.8755), (4.1750, 47.8755), pcbnew.F_Cu, net_reset, width_mm=0.20) # U1 Pin 7

# --- Loop 2: V_{IO} ---
add_track(board, (17.7750, 50.1457), (16.650, 50.1457), pcbnew.B_Cu, net_vio, width_mm=0.20)
add_track(board, (16.650, 50.1457), (16.650, 45.3617), pcbnew.B_Cu, net_vio, width_mm=0.20)
add_track(board, (16.650, 45.3617), (16.9735, 45.3617), pcbnew.B_Cu, net_vio, width_mm=0.20) # R1 Pad 1
add_track(board, (16.9735, 45.3617), (16.9735, 43.3617), pcbnew.B_Cu, net_vio, width_mm=0.20) # R2 Pad 1
add_track(board, (16.9735, 43.3617), (16.650, 41.600), pcbnew.B_Cu, net_vio, width_mm=0.20)
add_via(board, (16.650, 41.600), net_vio)
add_track(board, (16.650, 41.600), (2.100, 41.600), pcbnew.F_Cu, net_vio, width_mm=0.20)
add_track(board, (2.100, 41.600), (2.100, 51.4355), pcbnew.F_Cu, net_vio, width_mm=0.20)
add_track(board, (2.100, 51.4355), (4.1750, 51.4355), pcbnew.F_Cu, net_vio, width_mm=0.20) # U1 Pin 5

# --- Loop 3: +1V8_PMW ---
add_track(board, (7.2485, 62.7117), (7.2485, 61.800), pcbnew.B_Cu, net_1v8, width_mm=0.25)
add_track(board, (7.2485, 61.800), (11.4860, 61.800), pcbnew.B_Cu, net_1v8, width_mm=0.25)
add_track(board, (11.4860, 61.800), (11.4860, 62.7992), pcbnew.B_Cu, net_1v8, width_mm=0.25) # C4 Pin 1
add_track(board, (11.4860, 61.800), (16.4735, 61.800), pcbnew.B_Cu, net_1v8, width_mm=0.25)
add_track(board, (16.4735, 61.800), (16.4735, 62.0617), pcbnew.B_Cu, net_1v8, width_mm=0.25) # R4 Pin 1
add_track(board, (16.4735, 61.800), (16.4735, 57.500), pcbnew.B_Cu, net_1v8, width_mm=0.25)
add_track(board, (16.4735, 57.500), (18.7485, 57.500), pcbnew.B_Cu, net_1v8, width_mm=0.25)
add_track(board, (18.7485, 57.500), (18.7485, 55.8957), pcbnew.B_Cu, net_1v8, width_mm=0.25) # C2 Pin 1
add_track(board, (18.7485, 55.8957), (18.7485, 54.1457), pcbnew.B_Cu, net_1v8, width_mm=0.25) # C1 Pin 1
add_track(board, (18.7485, 54.1457), (18.7485, 51.4457), pcbnew.B_Cu, net_1v8, width_mm=0.25)
add_track(board, (18.7485, 51.4457), (17.7750, 51.4457), pcbnew.B_Cu, net_1v8, width_mm=0.25) # JP1 Pin 3

add_track(board, (7.2485, 62.7117), (6.500, 62.7117), pcbnew.B_Cu, net_1v8, width_mm=0.25)
add_via(board, (6.500, 62.7117), net_1v8)
add_track(board, (6.500, 62.7117), (1.500, 62.7117), pcbnew.F_Cu, net_1v8, width_mm=0.25)
add_track(board, (1.500, 62.7117), (1.500, 54.9955), pcbnew.F_Cu, net_1v8, width_mm=0.25)
add_track(board, (1.500, 54.9955), (4.1750, 54.9955), pcbnew.F_Cu, net_1v8, width_mm=0.25) # U1 Pin 3
add_track(board, (1.500, 54.9955), (1.500, 53.2155), pcbnew.F_Cu, net_1v8, width_mm=0.25)
add_track(board, (1.500, 53.2155), (4.1750, 53.2155), pcbnew.F_Cu, net_1v8, width_mm=0.25) # U1 Pin 4
add_track(board, (1.500, 53.2155), (1.500, 40.800), pcbnew.F_Cu, net_1v8, width_mm=0.25)
add_track(board, (1.500, 40.800), (8.7985, 40.800), pcbnew.F_Cu, net_1v8, width_mm=0.25)
add_via(board, (8.7985, 40.800), net_1v8)
add_track(board, (8.7985, 40.800), (8.7985, 41.6617), pcbnew.B_Cu, net_1v8, width_mm=0.25) # R3 Pin 1

# --- Loop 4: Net-(U1-LED_P) (Y=63.400 in south for extra clearance to GNDR via at Y=64.250) ---
add_track(board, (14.8750, 55.8855), (16.000, 55.8855), pcbnew.F_Cu, net_led, width_mm=0.25)
add_track(board, (16.000, 55.8855), (16.000, 63.400), pcbnew.F_Cu, net_led, width_mm=0.25)
add_track(board, (16.000, 63.400), (0.800, 63.400), pcbnew.F_Cu, net_led, width_mm=0.25)
add_track(board, (0.800, 63.400), (0.800, 40.000), pcbnew.F_Cu, net_led, width_mm=0.25)
add_track(board, (0.800, 40.000), (6.9735, 40.000), pcbnew.F_Cu, net_led, width_mm=0.25)
add_via(board, (6.9735, 40.000), net_led)
add_track(board, (6.9735, 40.000), (6.9735, 41.6617), pcbnew.B_Cu, net_led, width_mm=0.25) # R3 Pin 2

# ==============================================================================
# 4. South Corridor (+3V3R, Net-(U2-NC), GNDR)
# ==============================================================================
# --- +3V3R ---
# Use the existing via at (20.000, 60.712) to go north on F.Cu to (20.000, 48.8457), then via to B.Cu -> JP1 Pin 1!
add_track(board, (20.000, 60.712), (20.000, 48.8457), pcbnew.F_Cu, net_3v3r, width_mm=0.30)
add_via(board, (20.000, 48.8457), net_3v3r)
add_track(board, (20.000, 48.8457), (17.7750, 48.8457), pcbnew.B_Cu, net_3v3r, width_mm=0.30) # JP1 Pin 1

# South branch from (24.800, 60.712) jogged north to (24.800, 60.500) to clear /SCLK (Y=61.263):
add_track(board, (24.800, 60.712), (24.800, 60.500), pcbnew.B_Cu, net_3v3r, width_mm=0.25)
add_via(board, (24.800, 60.500), net_3v3r)
add_track(board, (24.800, 60.500), (24.800, 66.050), pcbnew.F_Cu, net_3v3r, width_mm=0.25)
add_track(board, (24.800, 66.050), (19.400, 66.050), pcbnew.F_Cu, net_3v3r, width_mm=0.25)
add_track(board, (19.400, 66.050), (18.650, 65.300), pcbnew.F_Cu, net_3v3r, width_mm=0.25)
add_track(board, (18.650, 65.300), (10.450, 65.300), pcbnew.F_Cu, net_3v3r, width_mm=0.25)
add_via(board, (10.450, 65.300), net_3v3r)
add_track(board, (10.450, 65.300), (10.600, 64.6117), pcbnew.B_Cu, net_3v3r, width_mm=0.20)
add_track(board, (10.600, 64.6117), (9.5235, 64.6117), pcbnew.B_Cu, net_3v3r, width_mm=0.20) # U2 Pin 3
add_track(board, (10.600, 64.6117), (10.600, 62.7117), pcbnew.B_Cu, net_3v3r, width_mm=0.20)
add_track(board, (10.600, 62.7117), (9.5235, 62.7117), pcbnew.B_Cu, net_3v3r, width_mm=0.20) # U2 Pin 1

add_track(board, (10.450, 65.300), (1.8860, 65.300), pcbnew.F_Cu, net_3v3r, width_mm=0.25)
add_via(board, (1.8860, 65.300), net_3v3r)
add_track(board, (1.8860, 65.300), (1.8860, 64.2242), pcbnew.B_Cu, net_3v3r, width_mm=0.25) # C3 Pin 1

# --- Net-(U2-NC) ---
add_track(board, (18.2985, 62.0617), (18.2485, 64.0617), pcbnew.B_Cu, net_u2nc, width_mm=0.20)
add_track(board, (18.2485, 64.0617), (18.2485, 66.000), pcbnew.B_Cu, net_u2nc, width_mm=0.20)
add_via(board, (18.2485, 66.000), net_u2nc)
add_track(board, (18.2485, 66.000), (7.2485, 66.000), pcbnew.F_Cu, net_u2nc, width_mm=0.20)
add_via(board, (7.2485, 66.000), net_u2nc)
add_track(board, (7.2485, 66.000), (7.2485, 64.6117), pcbnew.B_Cu, net_u2nc, width_mm=0.20) # U2 Pin 4

# --- GNDR (Ground System) ---
add_via(board, (23.500, 66.850), net_gndr)
add_track(board, (23.500, 66.850), (23.500, 66.900), pcbnew.B_Cu, net_gndr, width_mm=0.30)
add_track(board, (23.500, 66.900), (16.5235, 66.900), pcbnew.B_Cu, net_gndr, width_mm=0.30)
add_track(board, (16.5235, 66.900), (11.4860, 66.900), pcbnew.B_Cu, net_gndr, width_mm=0.30)
add_track(board, (11.4860, 66.900), (8.3860, 66.900), pcbnew.B_Cu, net_gndr, width_mm=0.30)
add_track(board, (8.3860, 66.900), (0.800, 66.900), pcbnew.B_Cu, net_gndr, width_mm=0.30)

add_track(board, (16.5235, 66.900), (16.5235, 64.0617), pcbnew.B_Cu, net_gndr, width_mm=0.30)
add_track(board, (11.4860, 66.900), (11.4860, 64.5242), pcbnew.B_Cu, net_gndr, width_mm=0.30)
add_track(board, (8.3860, 66.900), (8.3860, 63.6617), pcbnew.B_Cu, net_gndr, width_mm=0.30)
add_track(board, (8.3860, 63.6617), (9.5235, 63.6617), pcbnew.B_Cu, net_gndr, width_mm=0.30)
add_track(board, (0.800, 66.900), (0.800, 62.4992), pcbnew.B_Cu, net_gndr, width_mm=0.30)
add_track(board, (0.800, 62.4992), (1.8860, 62.4992), pcbnew.B_Cu, net_gndr, width_mm=0.30)

# Connect C1 & C2 Pin 2 (17.0235, 54.1457 & 55.8957) via F.Cu at X=16.650 down to Y=64.250:
add_track(board, (17.0235, 54.1457), (17.0235, 55.8957), pcbnew.B_Cu, net_gndr, width_mm=0.25)
add_track(board, (17.0235, 54.1457), (16.650, 54.1457), pcbnew.B_Cu, net_gndr, width_mm=0.25)
add_via(board, (16.650, 54.1457), net_gndr)
add_track(board, (16.650, 54.1457), (16.650, 64.250), pcbnew.F_Cu, net_gndr, width_mm=0.25)
add_track(board, (16.650, 64.250), (15.650, 64.250), pcbnew.F_Cu, net_gndr, width_mm=0.25)
add_via(board, (15.650, 64.250), net_gndr)
add_track(board, (15.650, 64.250), (16.5235, 64.0617), pcbnew.B_Cu, net_gndr, width_mm=0.25)

# Connect U1 Pin 8 (4.1750, 46.0955) to TRRS Jack rJ2 (-0.725, 43.5125) on B.Cu:
add_track(board, (4.1750, 46.0955), (-0.725, 46.0955), pcbnew.B_Cu, net_gndr, width_mm=0.35)
add_track(board, (-0.725, 46.0955), (-0.725, 43.5125), pcbnew.B_Cu, net_gndr, width_mm=0.35)

# Refill zones
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

board.Save(TARGET_PCB)
print("Saved clean test board v3.")
