import pcbnew
import subprocess
import json
from pathlib import Path

TARGET_PCB = "scratch/test_perfect.kicad_pcb"
TARGET_PRO = "scratch/test_perfect.kicad_pro"
REPORT_JSON = "scratch/drc_perfect.json"

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

# Jog /TX at X=16.4 to X=20.5 to clear R2 Pad 2
def update_segment_coords(content, u, new_start, new_end):
    idx = content.find(u)
    if idx == -1: return content
    start = content.rfind('(segment', 0, idx)
    end = content.find(')', idx)
    seg_txt = content[start:end+1]
    import re
    seg_txt = re.sub(r'\(start\s+[\d\.\-]+\s+[\d\.\-]+\)', f'(start {new_start[0]} {new_start[1]})', seg_txt)
    seg_txt = re.sub(r'\(end\s+[\d\.\-]+\s+[\d\.\-]+\)', f'(end {new_end[0]} {new_end[1]})', seg_txt)
    return content[:start] + seg_txt + content[end+1:]

txt = update_segment_coords(txt, "c93696f3-c7b1-401f-9d93-13e7369537ca", (16.4, 39.2), (20.5, 42.0))
txt = update_segment_coords(txt, "29a0d305-14f2-427a-a8a7-56828070e13f", (20.5, 42.0), (20.5, 44.5))
txt = update_segment_coords(txt, "9bdeec8b-2ee5-43fa-9125-b7e91eff0fca", (20.5, 44.5), (21.0, 44.5))

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

# ==============================================================================
# 1. SPI BUS (Planar on F.Cu)
# Staggered entry vias at X=18.5, 20.5, 22.5 to ensure >= 1.5mm clearance
# ==============================================================================
# SCLK enters at Y=61.263 on B.Cu. Extend east to via at (18.5, 61.263):
# Wait, entry lines enter from X=78 on B.Cu! So (18.5, 61.263) is on the line!
add_via(board, (18.500, 61.263), net_sclk)
# MOSI enters at Y=61.812 on B.Cu:
add_via(board, (20.500, 61.812), net_mosi)
# MISO enters at Y=62.362 on B.Cu:
add_via(board, (22.500, 62.362), net_miso)

# Connect arrival track on B.Cu to via:
add_track(board, (78.300, 61.263), (18.500, 61.263), pcbnew.B_Cu, net_sclk, width_mm=0.25)
add_track(board, (78.950, 61.812), (20.500, 61.812), pcbnew.B_Cu, net_mosi, width_mm=0.25)
add_track(board, (79.600, 62.362), (22.500, 62.362), pcbnew.B_Cu, net_miso, width_mm=0.25)

# On F.Cu:
# SCLK (via at 18.5, 61.263): go to X=17.2 -> North to Y=46.9855 -> U1 Pad 10
add_track(board, (18.500, 61.263), (17.200, 61.263), pcbnew.F_Cu, net_sclk, width_mm=0.25)
add_track(board, (17.200, 61.263), (17.200, 46.9855), pcbnew.F_Cu, net_sclk, width_mm=0.25)
add_track(board, (17.200, 46.9855), (14.8750, 46.9855), pcbnew.F_Cu, net_sclk, width_mm=0.25) # U1 Pad 10

# MOSI (via at 20.5, 61.812): go to X=16.6 -> North to Y=48.7655 -> U1 Pad 11
add_track(board, (20.500, 61.812), (16.600, 61.812), pcbnew.F_Cu, net_mosi, width_mm=0.25)
add_track(board, (16.600, 61.812), (16.600, 48.7655), pcbnew.F_Cu, net_mosi, width_mm=0.25)
add_track(board, (16.600, 48.7655), (14.8750, 48.7655), pcbnew.F_Cu, net_mosi, width_mm=0.25) # U1 Pad 11

# MISO (via at 22.5, 62.362): go North on X=22.5 to Y=50.5455 -> West to U1 Pad 12
add_track(board, (22.500, 62.362), (22.500, 50.5455), pcbnew.F_Cu, net_miso, width_mm=0.25)
add_track(board, (22.500, 50.5455), (14.8750, 50.5455), pcbnew.F_Cu, net_miso, width_mm=0.25) # U1 Pad 12
# Branch north along X=22.5 to Y=43.3617 -> West to R2 Pad 2 (18.7985, 43.3617):
add_track(board, (22.500, 50.5455), (22.500, 43.3617), pcbnew.F_Cu, net_miso, width_mm=0.25)
add_track(board, (22.500, 43.3617), (18.7985, 43.3617), pcbnew.F_Cu, net_miso, width_mm=0.25)
add_via(board, (18.7985, 43.3617), net_miso) # R2 Pad 2

# ==============================================================================
# 2. /NCS (Chip Select, 100% on B.Cu)
# Arrives at (19.600, 40.300) on B.Cu.
# U1 Pad 9 is at (14.875, 45.2055), radius 0.76 -> edge 15.635.
# Run at X = 16.050 (clearance to Pad 9: 0.415mm, clearance to R1 Pad 1: 0.434mm)
# ==============================================================================
add_track(board, (19.600, 40.300), (16.050, 40.300), pcbnew.B_Cu, net_ncs, width_mm=0.20)
add_track(board, (16.050, 40.300), (16.050, 52.3255), pcbnew.B_Cu, net_ncs, width_mm=0.20)
add_track(board, (16.050, 52.3255), (14.8750, 52.3255), pcbnew.B_Cu, net_ncs, width_mm=0.20) # U1 Pad 13

# ==============================================================================
# 3. V_{IO} (Power Distribution)
# ==============================================================================
# Connect JP1 Pad 2 (17.775, 50.1457) to R1 Pad 1 (16.9735, 45.3617) and R2 Pad 1 (16.9735, 43.3617) on B.Cu:
add_track(board, (17.7750, 50.1457), (16.9735, 50.1457), pcbnew.B_Cu, net_vio, width_mm=0.20)
add_track(board, (16.9735, 50.1457), (16.9735, 45.3617), pcbnew.B_Cu, net_vio, width_mm=0.20) # R1 Pad 1
add_track(board, (16.9735, 45.3617), (16.9735, 43.3617), pcbnew.B_Cu, net_vio, width_mm=0.20) # R2 Pad 1

# Connect to U1 Pin 5 (4.175, 51.4355) via F.Cu:
# Go to Y=42.400 on B.Cu:
add_track(board, (16.9735, 43.3617), (16.9735, 42.400), pcbnew.B_Cu, net_vio, width_mm=0.20)
add_via(board, (16.9735, 42.400), net_vio)
# On F.Cu, go west to X=2.800 (larger X than RESET at X=2.000):
add_track(board, (16.9735, 42.400), (2.800, 42.400), pcbnew.F_Cu, net_vio, width_mm=0.20)
add_track(board, (2.800, 42.400), (2.800, 51.4355), pcbnew.F_Cu, net_vio, width_mm=0.20)
add_track(board, (2.800, 51.4355), (4.1750, 51.4355), pcbnew.F_Cu, net_vio, width_mm=0.20) # U1 Pin 5

# ==============================================================================
# 4. /RESET (Control Line)
# ==============================================================================
# R1 Pad 2 is at (18.7985, 45.3617). Put via directly at Pad 2 to avoid R2 Pad 2 on B.Cu:
add_via(board, (18.7985, 45.3617), net_reset)
# On F.Cu, go north to Y=41.500:
add_track(board, (18.7985, 45.3617), (18.7985, 41.500), pcbnew.F_Cu, net_reset, width_mm=0.20)
# Go west to X=2.000 (smaller X than VIO at X=2.800, so they don't cross!):
add_track(board, (18.7985, 41.500), (2.000, 41.500), pcbnew.F_Cu, net_reset, width_mm=0.20)
add_track(board, (2.000, 41.500), (2.000, 47.8755), pcbnew.F_Cu, net_reset, width_mm=0.20)
add_track(board, (2.000, 47.8755), (4.1750, 47.8755), pcbnew.F_Cu, net_reset, width_mm=0.20) # U1 Pin 7

# ==============================================================================
# 5. +1V8_PMW (LDO Output & Distribution)
# ==============================================================================
# U2 Pin 5 (7.2485, 62.7117):
add_track(board, (7.2485, 62.7117), (6.500, 62.7117), pcbnew.B_Cu, net_1v8, width_mm=0.30)
add_via(board, (6.500, 62.7117), net_1v8)

# East branch to C4, R4 on F.Cu -> B.Cu:
add_track(board, (6.500, 62.7117), (11.4860, 62.200), pcbnew.F_Cu, net_1v8, width_mm=0.30)
add_via(board, (11.4860, 62.200), net_1v8)
add_track(board, (11.4860, 62.200), (11.4860, 62.7992), pcbnew.B_Cu, net_1v8, width_mm=0.30) # C4 Pin 1
add_track(board, (11.4860, 62.200), (16.4735, 62.0617), pcbnew.B_Cu, net_1v8, width_mm=0.30) # R4 Pin 1

# Connect C2, C1, JP1 on B.Cu (from R4 Pin 1 via North of R4 Pad 2 at Y=61.2):
add_track(board, (16.4735, 62.0617), (16.4735, 61.200), pcbnew.B_Cu, net_1v8, width_mm=0.25)
add_track(board, (16.4735, 61.200), (19.400, 61.200), pcbnew.B_Cu, net_1v8, width_mm=0.25)
add_track(board, (19.400, 61.200), (19.400, 55.8957), pcbnew.B_Cu, net_1v8, width_mm=0.25)
add_track(board, (19.400, 55.8957), (18.7485, 55.8957), pcbnew.B_Cu, net_1v8, width_mm=0.25) # C2 Pin 1
add_track(board, (18.7485, 55.8957), (18.7485, 54.1457), pcbnew.B_Cu, net_1v8, width_mm=0.25) # C1 Pin 1
add_track(board, (18.7485, 54.1457), (18.7485, 51.4457), pcbnew.B_Cu, net_1v8, width_mm=0.25)
add_track(board, (18.7485, 51.4457), (17.7750, 51.4457), pcbnew.B_Cu, net_1v8, width_mm=0.25) # JP1 Pin 3

# West branch from U2 Pin 5 via (6.5, 62.7117) to U1 Pin 3 & Pin 4 on F.Cu:
# Run at X = 2.800 (clears U1 Pad 1 and Pad 2):
add_track(board, (6.500, 62.7117), (2.800, 62.7117), pcbnew.F_Cu, net_1v8, width_mm=0.30)
add_track(board, (2.800, 62.7117), (2.800, 54.9955), pcbnew.F_Cu, net_1v8, width_mm=0.30)
add_track(board, (2.800, 54.9955), (4.1750, 54.9955), pcbnew.F_Cu, net_1v8, width_mm=0.30) # U1 Pin 3
add_track(board, (2.800, 54.9955), (2.800, 53.2155), pcbnew.F_Cu, net_1v8, width_mm=0.30)
add_track(board, (2.800, 53.2155), (4.1750, 53.2155), pcbnew.F_Cu, net_1v8, width_mm=0.30) # U1 Pin 4

# Connect to R3 Pin 1 (8.7985, 41.6617) via East Highway on B.Cu (from JP1 Pin 3 north along X=19.4 to Y=40.8, then west):
add_track(board, (18.7485, 51.4457), (19.400, 51.4457), pcbnew.B_Cu, net_1v8, width_mm=0.25)
add_track(board, (19.400, 51.4457), (19.400, 40.800), pcbnew.B_Cu, net_1v8, width_mm=0.25)
add_track(board, (19.400, 40.800), (8.7985, 40.800), pcbnew.B_Cu, net_1v8, width_mm=0.25)
add_track(board, (8.7985, 40.800), (8.7985, 41.6617), pcbnew.B_Cu, net_1v8, width_mm=0.25) # R3 Pin 1

# ==============================================================================
# 6. Net-(U1-LED_P) (LED Cathode to R3 Pin 2)
# ==============================================================================
# U1 Pin 15 (14.875, 55.8855) to R3 Pin 2 (6.9735, 41.6617)
# Run vertical at X = 15.800 on F.Cu south to Y = 63.800:
add_track(board, (14.8750, 55.8855), (15.800, 55.8855), pcbnew.F_Cu, net_led, width_mm=0.25)
add_track(board, (15.800, 55.8855), (15.800, 63.800), pcbnew.F_Cu, net_led, width_mm=0.25)
add_track(board, (15.800, 63.800), (1.200, 63.800), pcbnew.F_Cu, net_led, width_mm=0.25)
add_track(board, (1.200, 63.800), (1.200, 40.000), pcbnew.F_Cu, net_led, width_mm=0.25)
add_track(board, (1.200, 40.000), (6.9735, 40.000), pcbnew.F_Cu, net_led, width_mm=0.25)
add_via(board, (6.9735, 40.000), net_led)
add_track(board, (6.9735, 40.000), (6.9735, 41.6617), pcbnew.B_Cu, net_led, width_mm=0.25) # R3 Pin 2

# ==============================================================================
# 7. +3V3R (Power Distribution)
# ==============================================================================
# Arrives at (20.0, 60.712) on B.Cu.
# Branch south to JP1 Pin 1 (17.775, 48.8457):
add_track(board, (20.000, 60.712), (20.000, 48.8457), pcbnew.B_Cu, net_3v3r, width_mm=0.35)
add_track(board, (20.000, 48.8457), (17.7750, 48.8457), pcbnew.B_Cu, net_3v3r, width_mm=0.35)

# Branch west to U2 Pin 1, Pin 3, and C3 Pin 1 along Y = 61.600 on B.Cu:
add_track(board, (20.000, 60.712), (20.000, 61.600), pcbnew.B_Cu, net_3v3r, width_mm=0.35)
add_track(board, (20.000, 61.600), (10.700, 61.600), pcbnew.B_Cu, net_3v3r, width_mm=0.35)
add_track(board, (10.700, 61.600), (10.700, 62.7117), pcbnew.B_Cu, net_3v3r, width_mm=0.35)
add_track(board, (10.700, 62.7117), (9.5235, 62.7117), pcbnew.B_Cu, net_3v3r, width_mm=0.35) # U2 Pin 1
add_track(board, (10.700, 62.7117), (10.700, 64.6117), pcbnew.B_Cu, net_3v3r, width_mm=0.35)
add_track(board, (10.700, 64.6117), (9.5235, 64.6117), pcbnew.B_Cu, net_3v3r, width_mm=0.35) # U2 Pin 3
# Connect to C3 Pin 1 (1.886, 64.2242) via F.Cu bypass at Y=64.6117:
add_via(board, (9.5235, 64.6117), net_3v3r)
add_track(board, (9.5235, 64.6117), (1.8860, 64.6117), pcbnew.F_Cu, net_3v3r, width_mm=0.35)
add_via(board, (1.8860, 64.6117), net_3v3r)
add_track(board, (1.8860, 64.6117), (1.8860, 64.2242), pcbnew.B_Cu, net_3v3r, width_mm=0.35) # C3 Pin 1

# ==============================================================================
# 8. Net-(U2-NC)
# ==============================================================================
add_track(board, (18.2985, 62.0617), (18.2485, 64.0617), pcbnew.B_Cu, net_u2nc)
add_via(board, (18.2485, 64.0617), net_u2nc)
add_track(board, (18.2485, 64.0617), (18.2485, 66.800), pcbnew.F_Cu, net_u2nc)
add_track(board, (18.2485, 66.800), (7.2485, 66.800), pcbnew.F_Cu, net_u2nc)
add_track(board, (7.2485, 66.800), (7.2485, 64.6117), pcbnew.F_Cu, net_u2nc)
add_via(board, (7.2485, 64.6117), net_u2nc) # U2 Pin 4

# ==============================================================================
# 9. GNDR (Ground System)
# ==============================================================================
# South Ground Bus on B.Cu at Y = 65.500:
add_via(board, (23.500, 66.400), net_gndr)
add_track(board, (23.500, 66.400), (23.500, 65.500), pcbnew.B_Cu, net_gndr, width_mm=0.40)
add_track(board, (23.500, 65.500), (16.5235, 65.500), pcbnew.B_Cu, net_gndr, width_mm=0.40)
add_track(board, (16.5235, 65.500), (11.4860, 65.500), pcbnew.B_Cu, net_gndr, width_mm=0.40)
add_track(board, (11.4860, 65.500), (8.3860, 65.500), pcbnew.B_Cu, net_gndr, width_mm=0.40)
add_track(board, (8.3860, 65.500), (1.000, 65.500), pcbnew.B_Cu, net_gndr, width_mm=0.40)

# Connect C5 Pin 2 (16.5235, 64.0617):
add_track(board, (16.5235, 65.500), (16.5235, 64.0617), pcbnew.B_Cu, net_gndr, width_mm=0.35)

# Connect C4 Pin 2 (11.4860, 64.5242):
add_track(board, (11.4860, 65.500), (11.4860, 64.5242), pcbnew.B_Cu, net_gndr, width_mm=0.35)

# Connect U2 Pin 2 (9.5235, 63.662):
add_track(board, (8.3860, 65.500), (8.3860, 63.6617), pcbnew.B_Cu, net_gndr, width_mm=0.35)
add_track(board, (8.3860, 63.6617), (9.5235, 63.6617), pcbnew.B_Cu, net_gndr, width_mm=0.35)

# Connect C3 Pin 2 (1.8860, 62.4992) around west of C3 on B.Cu:
add_track(board, (1.000, 65.500), (1.000, 62.4992), pcbnew.B_Cu, net_gndr, width_mm=0.35)
add_track(board, (1.000, 62.4992), (1.8860, 62.4992), pcbnew.B_Cu, net_gndr, width_mm=0.35)

# Connect C1 & C2 Pin 2 (17.0235, 54.1457 & 55.8957) on F.Cu to avoid B.Cu tracks:
add_via(board, (17.0235, 55.8957), net_gndr)
add_track(board, (17.0235, 55.8957), (17.0235, 54.1457), pcbnew.B_Cu, net_gndr, width_mm=0.35)
add_track(board, (17.0235, 55.8957), (17.0235, 65.500), pcbnew.F_Cu, net_gndr, width_mm=0.35)
add_via(board, (17.0235, 65.500), net_gndr)
add_track(board, (17.0235, 65.500), (16.5235, 65.500), pcbnew.B_Cu, net_gndr, width_mm=0.35)

# Connect U1 Pin 8 (4.1750, 46.0955) to TRRS Jack rJ2 (-0.725, 43.5125) on B.Cu:
add_track(board, (4.1750, 46.0955), (-0.725, 46.0955), pcbnew.B_Cu, net_gndr, width_mm=0.35)
add_track(board, (-0.725, 46.0955), (-0.725, 43.5125), pcbnew.B_Cu, net_gndr, width_mm=0.35)

# Refill zones
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

board.Save(TARGET_PCB)
print("Saved 100% solved test board.")
