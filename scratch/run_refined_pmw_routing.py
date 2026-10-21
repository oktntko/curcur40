import pcbnew
import subprocess
from pathlib import Path

PCB_PATH = "pcbs/curcur40/right/curcur40-right.kicad_pcb"
TEST_PCB = "scratch/test_refined.kicad_pcb"

DEAD_STUB_UUIDS = [
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

txt = Path(PCB_PATH).read_text(encoding="utf-8")

def remove_by_uuid(content, u):
    idx = content.find(u)
    if idx == -1:
        return content
    start = content.rfind('(segment', 0, idx)
    if start == -1:
        start = content.rfind('(via', 0, idx)
    if start == -1:
        return content
    
    real_start = content.rfind('\n', 0, start)
    if real_start == -1:
        real_start = start
    else:
        real_start += 1
    
    depth = 0
    end = start
    while end < len(content):
        if content[end] == '(':
            depth += 1
        elif content[end] == ')':
            depth -= 1
            if depth == 0:
                break
        end += 1
    
    if end + 1 < len(content) and content[end+1] == '\n':
        end += 1
        
    return content[:real_start] + content[end+1:]

for u in DEAD_STUB_UUIDS:
    txt = remove_by_uuid(txt, u)

def update_segment_coords(content, u, new_start, new_end):
    idx = content.find(u)
    if idx == -1:
        return content
    start = content.rfind('(segment', 0, idx)
    end = content.find(')', idx)
    seg_txt = content[start:end+1]
    import re
    seg_txt = re.sub(r'\(start\s+[\d\.\-]+\s+[\d\.\-]+\)', f'(start {new_start[0]} {new_start[1]})', seg_txt)
    seg_txt = re.sub(r'\(end\s+[\d\.\-]+\s+[\d\.\-]+\)', f'(end {new_end[0]} {new_end[1]})', seg_txt)
    return content[:start] + seg_txt + content[end+1:]

txt = update_segment_coords(txt, "c93696f3-c7b1-401f-9d93-13e7369537ca", (16.4, 39.2), (20.3, 42.0))
txt = update_segment_coords(txt, "29a0d305-14f2-427a-a8a7-56828070e13f", (20.3, 42.0), (20.3, 44.5))
txt = update_segment_coords(txt, "9bdeec8b-2ee5-43fa-9125-b7e91eff0fca", (20.3, 44.5), (21.0, 44.5))

Path(PCB_PATH).write_text(txt, encoding="utf-8")
print("Clean base written successfully.")

board = pcbnew.LoadBoard(PCB_PATH)

net_gndr = board.FindNet("GNDR")
net_3v3r = board.FindNet("+3V3R")
net_1v8 = board.FindNet("+1V8_PMW")
net_vio = board.FindNet("V_{IO}")
net_sclk = board.FindNet("/SCLK")
net_mosi = board.FindNet("/MOSI")
net_miso = board.FindNet("/MISO")
net_ncs = board.FindNet("/NCS")
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

# --- A. +3V3R ---
# 1. MCU via at (20.0, 60.712) to JP1 Pin 1 (17.775, 48.8457) on B.Cu
add_track(board, (20.0, 60.712), (20.0, 48.8457), pcbnew.B_Cu, net_3v3r, width_mm=0.35)
add_track(board, (20.0, 48.8457), (17.775, 48.8457), pcbnew.B_Cu, net_3v3r, width_mm=0.35)

# 2. From (20.0, 60.712) to U2 Pin 1 & Pin 3 on F.Cu
add_track(board, (20.0, 60.712), (10.4, 60.712), pcbnew.F_Cu, net_3v3r, width_mm=0.35)
add_track(board, (10.4, 60.712), (10.4, 61.5), pcbnew.F_Cu, net_3v3r, width_mm=0.35)
add_via(board, (10.4, 61.5), net_3v3r)
add_track(board, (10.4, 61.5), (10.4, 62.7117), pcbnew.B_Cu, net_3v3r, width_mm=0.35)
add_track(board, (10.4, 62.7117), (9.5235, 62.7117), pcbnew.B_Cu, net_3v3r, width_mm=0.35) # U2 Pin 1
add_track(board, (10.4, 62.7117), (10.4, 64.6117), pcbnew.B_Cu, net_3v3r, width_mm=0.35) # jog right around Pin 2
add_track(board, (10.4, 64.6117), (9.5235, 64.6117), pcbnew.B_Cu, net_3v3r, width_mm=0.35) # U2 Pin 3

# 3. U2 Pin 3 (9.5235, 64.6117) to C3 Pin 1 (1.8860, 64.2242) on B.Cu
add_track(board, (9.5235, 64.6117), (1.8860, 64.6117), pcbnew.B_Cu, net_3v3r, width_mm=0.35)
add_track(board, (1.8860, 64.6117), (1.8860, 64.2242), pcbnew.B_Cu, net_3v3r, width_mm=0.35)

# --- B. Net-(U2-NC) ---
# R4 Pin 2 (18.2985, 62.0617) to C5 Pin 1 (18.2485, 64.0617) on B.Cu
add_track(board, (18.2985, 62.0617), (18.2485, 64.0617), pcbnew.B_Cu, net_u2nc)
# Via at (18.2485, 65.2), run on F.Cu to (7.2485, 65.2), via to B.Cu, to U2 Pin 4 (7.2485, 64.6117)
add_track(board, (18.2485, 64.0617), (18.2485, 65.2), pcbnew.B_Cu, net_u2nc)
add_via(board, (18.2485, 65.2), net_u2nc)
add_track(board, (18.2485, 65.2), (7.2485, 65.2), pcbnew.F_Cu, net_u2nc)
add_via(board, (7.2485, 65.2), net_u2nc)
add_track(board, (7.2485, 65.2), (7.2485, 64.6117), pcbnew.B_Cu, net_u2nc)

# --- C. +1V8_PMW ---
# U2 Pin 5 (7.2485, 62.7117) to C4 Pin 1 (11.4860, 62.7992) via F.Cu
add_track(board, (7.2485, 62.7117), (6.5, 62.7117), pcbnew.B_Cu, net_1v8, width_mm=0.3)
add_via(board, (6.5, 62.7117), net_1v8)
add_track(board, (6.5, 62.7117), (6.5, 62.0), pcbnew.F_Cu, net_1v8, width_mm=0.3)
add_track(board, (6.5, 62.0), (12.5, 62.0), pcbnew.F_Cu, net_1v8, width_mm=0.3)
add_via(board, (12.5, 62.0), net_1v8)
add_track(board, (12.5, 62.0), (11.4860, 62.7992), pcbnew.B_Cu, net_1v8, width_mm=0.3) # C4 Pin 1
add_track(board, (12.5, 62.0), (16.4735, 62.0617), pcbnew.B_Cu, net_1v8, width_mm=0.3) # R4 Pin 1

# From (12.5, 62.0) continue east to X = 19.8 (north of cutout at Y = 62.0!)
add_track(board, (12.5, 62.0), (19.8, 62.0), pcbnew.F_Cu, net_1v8, width_mm=0.3)
add_via(board, (19.8, 62.0), net_1v8)
add_track(board, (19.8, 62.0), (19.8, 55.8957), pcbnew.B_Cu, net_1v8, width_mm=0.3)
add_track(board, (19.8, 55.8957), (18.7485, 55.8957), pcbnew.B_Cu, net_1v8, width_mm=0.3) # C2 Pin 1
add_track(board, (19.8, 55.8957), (19.8, 54.1457), pcbnew.B_Cu, net_1v8, width_mm=0.3)
add_track(board, (19.8, 54.1457), (18.7485, 54.1457), pcbnew.B_Cu, net_1v8, width_mm=0.3) # C1 Pin 1
add_track(board, (19.8, 54.1457), (19.8, 51.4457), pcbnew.B_Cu, net_1v8, width_mm=0.3)
add_track(board, (19.8, 51.4457), (17.7750, 51.4457), pcbnew.B_Cu, net_1v8, width_mm=0.3) # JP1 Pin 3

# Connect U2 Pin 5 to U1 Pin 3 & Pin 4 (4.1750, 54.9955 & 53.2155):
# Directly down west of cutout at X = 4.1750!
add_track(board, (6.5, 62.0), (4.1750, 62.0), pcbnew.F_Cu, net_1v8, width_mm=0.35)
add_track(board, (4.1750, 62.0), (4.1750, 54.9955), pcbnew.F_Cu, net_1v8, width_mm=0.35) # U1 Pin 3
add_track(board, (4.1750, 54.9955), (4.1750, 53.2155), pcbnew.F_Cu, net_1v8, width_mm=0.35) # U1 Pin 4

# Connect to R3 Pin 1 (8.7985, 41.6617) south of cutout:
add_track(board, (4.1750, 53.2155), (3.5, 53.2155), pcbnew.F_Cu, net_1v8, width_mm=0.3)
add_track(board, (3.5, 53.2155), (3.5, 41.6617), pcbnew.F_Cu, net_1v8, width_mm=0.3)
add_track(board, (3.5, 41.6617), (8.7985, 41.6617), pcbnew.F_Cu, net_1v8, width_mm=0.3)
add_via(board, (8.7985, 41.6617), net_1v8)

# --- D. V_{IO} ---
# Connect R2 Pin 1 (16.9735, 43.3617) to R1 Pin 1 (16.9735, 45.3617)
add_track(board, (16.9735, 43.3617), (16.9735, 45.3617), pcbnew.B_Cu, net_vio)
add_track(board, (16.9735, 45.3617), (16.0, 45.3617), pcbnew.B_Cu, net_vio)
add_via(board, (16.0, 45.3617), net_vio)
add_track(board, (16.0, 45.3617), (16.0, 50.1457), pcbnew.F_Cu, net_vio)
add_via(board, (16.0, 50.1457), net_vio)
add_track(board, (16.0, 50.1457), (17.7750, 50.1457), pcbnew.B_Cu, net_vio) # JP1 Pin 2

# To U1 Pin 5 (4.1750, 51.4355) south of cutout at Y = 43.0:
add_track(board, (16.0, 45.3617), (16.0, 43.0), pcbnew.F_Cu, net_vio)
add_track(board, (16.0, 43.0), (3.0, 43.0), pcbnew.F_Cu, net_vio)
add_track(board, (3.0, 43.0), (3.0, 51.4355), pcbnew.F_Cu, net_vio)
add_track(board, (3.0, 51.4355), (4.1750, 51.4355), pcbnew.F_Cu, net_vio) # U1 Pin 5

# --- E. /RESET ---
# U1 Pin 7 (4.1750, 47.8755) to R1 Pin 2 (18.7985, 45.3617)
# Run south of cutout at Y = 42.4:
add_track(board, (4.1750, 47.8755), (2.2, 47.8755), pcbnew.F_Cu, net_reset)
add_track(board, (2.2, 47.8755), (2.2, 42.4), pcbnew.F_Cu, net_reset)
add_track(board, (2.2, 42.4), (18.7985, 42.4), pcbnew.F_Cu, net_reset)
add_track(board, (18.7985, 42.4), (18.7985, 45.3617), pcbnew.F_Cu, net_reset)
add_via(board, (18.7985, 45.3617), net_reset)

# --- F. Net-(U1-LED_P) ---
# U1 Pin 15 (14.8750, 55.8855) to R3 Pin 2 (6.9735, 41.6617)
# Run north of cutout at Y = 62.4, west at X = 1.5, south to Y = 40.5:
add_track(board, (14.8750, 55.8855), (14.8750, 62.4), pcbnew.F_Cu, net_led)
add_track(board, (14.8750, 62.4), (1.5, 62.4), pcbnew.F_Cu, net_led)
add_track(board, (1.5, 62.4), (1.5, 40.5), pcbnew.F_Cu, net_led)
add_track(board, (1.5, 40.5), (6.9735, 40.5), pcbnew.F_Cu, net_led)
add_via(board, (6.9735, 40.5), net_led)
add_track(board, (6.9735, 40.5), (6.9735, 41.6617), pcbnew.B_Cu, net_led)

# --- G. SPI Lines ---
# /NCS: incoming MCU via at (19.600, 40.300) to U1 Pin 13 (14.8750, 52.3255)
# Run at X = 15.8 (east of cutout, safe from U1 pads at 14.875):
add_track(board, (19.600, 40.300), (16.2, 40.300), pcbnew.F_Cu, net_ncs)
add_track(board, (16.2, 40.300), (16.2, 52.3255), pcbnew.F_Cu, net_ncs)
add_track(board, (16.2, 52.3255), (14.8750, 52.3255), pcbnew.F_Cu, net_ncs)

# /SCLK: incoming MCU track on B.Cu at (19.200, 61.263) to U1 Pin 10 (14.8750, 46.9855)
add_via(board, (19.200, 61.263), net_sclk)
add_track(board, (19.200, 61.263), (20.3, 61.263), pcbnew.F_Cu, net_sclk)
add_track(board, (20.3, 61.263), (20.3, 46.9855), pcbnew.F_Cu, net_sclk)
add_track(board, (20.3, 46.9855), (14.8750, 46.9855), pcbnew.F_Cu, net_sclk)

# /MOSI: incoming MCU track on B.Cu at (19.650, 61.812) to U1 Pin 11 (14.8750, 48.7655)
add_via(board, (19.650, 61.812), net_mosi)
add_track(board, (19.650, 61.812), (20.8, 61.812), pcbnew.F_Cu, net_mosi)
add_track(board, (20.8, 61.812), (20.8, 48.7655), pcbnew.F_Cu, net_mosi)
add_track(board, (20.8, 48.7655), (14.8750, 48.7655), pcbnew.F_Cu, net_mosi)

# /MISO: incoming MCU track on B.Cu at (20.100, 62.362) to U1 Pin 12 (14.8750, 50.5455) & R2 Pin 2 (18.7985, 43.3617)
add_via(board, (20.100, 62.362), net_miso)
add_track(board, (20.100, 62.362), (21.3, 62.362), pcbnew.F_Cu, net_miso)
add_track(board, (21.3, 62.362), (21.3, 50.5455), pcbnew.F_Cu, net_miso)
add_track(board, (21.3, 50.5455), (14.8750, 50.5455), pcbnew.F_Cu, net_miso)

# /MISO to R2 Pin 2 (18.7985, 43.3617):
add_track(board, (21.3, 50.5455), (21.3, 43.3617), pcbnew.F_Cu, net_miso)
add_track(board, (21.3, 43.3617), (18.7985, 43.3617), pcbnew.F_Cu, net_miso)
add_via(board, (18.7985, 43.3617), net_miso)

# --- H. GND Backbone & Connections ---
# Main GND rail arrives at (23.500, 66.400) on F.Cu.
# Run GND backbone at Y = 65.5 on F.Cu:
add_track(board, (23.500, 66.400), (23.500, 65.5), pcbnew.F_Cu, net_gndr, width_mm=0.4)
add_track(board, (23.500, 65.5), (16.5235, 65.5), pcbnew.F_Cu, net_gndr, width_mm=0.4)
add_track(board, (16.5235, 65.5), (11.4860, 65.5), pcbnew.F_Cu, net_gndr, width_mm=0.4)
add_track(board, (11.4860, 65.5), (8.3860, 65.5), pcbnew.F_Cu, net_gndr, width_mm=0.4)
add_track(board, (8.3860, 65.5), (1.8860, 65.5), pcbnew.F_Cu, net_gndr, width_mm=0.4)

# Connect to C5 Pin 2 (16.5235, 64.0617) on B.Cu
add_via(board, (16.5235, 65.5), net_gndr)
add_track(board, (16.5235, 65.5), (16.5235, 64.0617), pcbnew.B_Cu, net_gndr, width_mm=0.35)

# Connect to C4 Pin 2 (11.4860, 64.5242) on B.Cu
add_via(board, (11.4860, 65.5), net_gndr)
add_track(board, (11.4860, 65.5), (11.4860, 64.5242), pcbnew.B_Cu, net_gndr, width_mm=0.35)

# Connect to U2 Pin 2 (9.5235, 63.6617) on B.Cu
add_track(board, (8.3860, 65.5), (8.3860, 63.6617), pcbnew.F_Cu, net_gndr, width_mm=0.35)
add_via(board, (8.3860, 63.6617), net_gndr)
add_track(board, (8.3860, 63.6617), (9.5235, 63.6617), pcbnew.B_Cu, net_gndr, width_mm=0.35)

# Connect to C3 Pin 2 (1.8860, 62.4992) on B.Cu
add_track(board, (1.8860, 65.5), (1.8860, 61.2), pcbnew.F_Cu, net_gndr, width_mm=0.35)
add_via(board, (1.8860, 61.2), net_gndr)
add_track(board, (1.8860, 61.2), (1.8860, 62.4992), pcbnew.B_Cu, net_gndr, width_mm=0.35)

# Connect C1 & C2 Pin 2 (17.0235, 54.1457 & 55.8957) on B.Cu
add_track(board, (17.0235, 54.1457), (17.0235, 55.8957), pcbnew.B_Cu, net_gndr, width_mm=0.35)
add_track(board, (17.0235, 55.8957), (17.0235, 57.5), pcbnew.B_Cu, net_gndr, width_mm=0.35)
add_via(board, (17.0235, 57.5), net_gndr)
add_track(board, (17.0235, 57.5), (17.0235, 65.5), pcbnew.F_Cu, net_gndr, width_mm=0.35)

# Connect U1 Pin 8 (4.1750, 46.0955) on F.Cu
add_track(board, (4.1750, 46.0955), (0.8, 46.0955), pcbnew.F_Cu, net_gndr, width_mm=0.35)
add_track(board, (0.8, 46.0955), (0.8, 65.5), pcbnew.F_Cu, net_gndr, width_mm=0.35)
add_track(board, (0.8, 65.5), (1.8860, 65.5), pcbnew.F_Cu, net_gndr, width_mm=0.35)

# Connect TRRS rJ2 Pad S on F.Cu
add_track(board, (-0.725, 43.513), (0.8, 43.513), pcbnew.F_Cu, net_gndr, width_mm=0.35)

# Refill all zones
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

board.Save(PCB_PATH)
print("Saved official routed board successfully.")
