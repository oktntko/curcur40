import re
import shutil
import pcbnew
import subprocess
from pathlib import Path

SRC_PCB = "scratch/backup_before_sync/curcur40-right.kicad_pcb"
TEST_PCB = "scratch/test_clean_pmw_route.kicad_pcb"

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

# Step 1: Text-based removal of dead stubs
content = Path(SRC_PCB).read_text(encoding="utf-8")

def remove_segment_by_uuid(txt, u):
    target = f'uuid "{u}"'
    idx = txt.find(target)
    if idx == -1:
        return txt
    start = txt.rfind('\n\t(segment', 0, idx)
    if start == -1:
        start = txt.rfind('\n\t(via', 0, idx)
    end = txt.find('\n\t)', idx)
    if start != -1 and end != -1:
        cut_end = end + len('\n\t)')
        if cut_end < len(txt) and txt[cut_end] == '\n':
            cut_end += 1
        return txt[:start] + txt[cut_end:]
    return txt

for u in DEAD_STUB_UUIDS:
    content = remove_segment_by_uuid(content, u)

# Step 2: Adjust /TX track in text
# Find segment (start 19.2 42) (end 19.2 44.5)
# Find segment (start 16.4 39.2) (end 19.2 42)
# Find segment (start 19.2 44.5) (end 21 44.5)
content = content.replace(
    '(start 19.2 42)\n\t\t(end 19.2 44.5)',
    '(start 20.3 42)\n\t\t(end 20.3 44.5)'
)
content = content.replace(
    '(start 16.4 39.2)\n\t\t(end 19.2 42)',
    '(start 16.4 39.2)\n\t\t(end 20.3 42)'
)
content = content.replace(
    '(start 19.2 44.5)\n\t\t(end 21 44.5)',
    '(start 20.3 44.5)\n\t\t(end 21 44.5)'
)

Path(TEST_PCB).write_text(content, encoding="utf-8")
print("Cleaned base board written to text file.")

# Step 3: Load into pcbnew and add clean tracks
board = pcbnew.LoadBoard(TEST_PCB)

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
# 1. Connect MCU via (20.0, 60.712) to JP1 Pin 1 (17.775, 48.8457) on B.Cu
add_track(board, (20.0, 60.712), (20.0, 48.8457), pcbnew.B_Cu, net_3v3r, width_mm=0.35)
add_track(board, (20.0, 48.8457), (17.775, 48.8457), pcbnew.B_Cu, net_3v3r, width_mm=0.35)

# 2. Connect (20.0, 60.712) to U2 Pin 1 (9.5235, 62.7117) & Pin 3 (9.5235, 64.6117)
# On F.Cu: (20.0, 60.712) -> (9.5235, 60.712) -> via to B.Cu at (9.5235, 61.5)
add_track(board, (20.0, 60.712), (9.5235, 60.712), pcbnew.F_Cu, net_3v3r, width_mm=0.35)
add_track(board, (9.5235, 60.712), (9.5235, 61.5), pcbnew.F_Cu, net_3v3r, width_mm=0.35)
add_via(board, (9.5235, 61.5), net_3v3r)
add_track(board, (9.5235, 61.5), (9.5235, 62.7117), pcbnew.B_Cu, net_3v3r, width_mm=0.35)
add_track(board, (9.5235, 62.7117), (9.5235, 64.6117), pcbnew.B_Cu, net_3v3r, width_mm=0.35)

# 3. Connect U2 Pin 3 (9.5235, 64.6117) to C3 Pin 1 (1.8860, 64.2242) on B.Cu
add_track(board, (9.5235, 64.6117), (9.5235, 64.2242), pcbnew.B_Cu, net_3v3r, width_mm=0.35)
add_track(board, (9.5235, 64.2242), (1.8860, 64.2242), pcbnew.B_Cu, net_3v3r, width_mm=0.35)

# --- B. Net-(U2-NC) ---
# Connect R4 Pin 2 (18.2985, 62.0617) to C5 Pin 1 (18.2485, 64.0617) on B.Cu
add_track(board, (18.2985, 62.0617), (18.2485, 64.0617), pcbnew.B_Cu, net_u2nc)
# Via at (18.2485, 65.2), run on F.Cu to (7.2485, 65.2), via to B.Cu, to U2 Pin 4 (7.2485, 64.6117)
add_track(board, (18.2485, 64.0617), (18.2485, 65.2), pcbnew.B_Cu, net_u2nc)
add_via(board, (18.2485, 65.2), net_u2nc)
add_track(board, (18.2485, 65.2), (7.2485, 65.2), pcbnew.F_Cu, net_u2nc)
add_via(board, (7.2485, 65.2), net_u2nc)
add_track(board, (7.2485, 65.2), (7.2485, 64.6117), pcbnew.B_Cu, net_u2nc)

# --- C. +1V8_PMW ---
# U2 Pin 5 (7.2485, 62.7117) -> C4 Pin 1 (11.4860, 62.7992) -> R4 Pin 1 (16.4735, 62.0617) on B.Cu
add_track(board, (7.2485, 62.7117), (11.4860, 62.7992), pcbnew.B_Cu, net_1v8, width_mm=0.3)
add_track(board, (11.4860, 62.7992), (16.4735, 62.0617), pcbnew.B_Cu, net_1v8, width_mm=0.3)

# R4 Pin 1 (16.4735, 62.0617) -> (17.5, 62.0617) -> (17.5, 57.0) -> (18.7485, 57.0) -> C2 Pin 1 (18.7485, 55.8957)
add_track(board, (16.4735, 62.0617), (17.5, 62.0617), pcbnew.B_Cu, net_1v8, width_mm=0.3)
add_track(board, (17.5, 62.0617), (17.5, 57.0), pcbnew.B_Cu, net_1v8, width_mm=0.3)
add_track(board, (17.5, 57.0), (18.7485, 57.0), pcbnew.B_Cu, net_1v8, width_mm=0.3)
add_track(board, (18.7485, 57.0), (18.7485, 55.8957), pcbnew.B_Cu, net_1v8, width_mm=0.3)

# C2 Pin 1 (18.7485, 55.8957) -> C1 Pin 1 (18.7485, 54.1457) -> (18.7485, 51.4457) -> JP1 Pin 3 (17.7750, 51.4457) on B.Cu
add_track(board, (18.7485, 55.8957), (18.7485, 54.1457), pcbnew.B_Cu, net_1v8, width_mm=0.3)
add_track(board, (18.7485, 54.1457), (18.7485, 51.4457), pcbnew.B_Cu, net_1v8, width_mm=0.3)
add_track(board, (18.7485, 51.4457), (17.7750, 51.4457), pcbnew.B_Cu, net_1v8, width_mm=0.3)

# Connect +1V8 to U1 Pin 3 & Pin 4 (4.1750, 54.9955 & 53.2155):
# Via at (18.7485, 53.5), run on F.Cu to (4.1750, 53.5)
add_via(board, (18.7485, 53.5), net_1v8)
add_track(board, (18.7485, 53.5), (4.1750, 53.5), pcbnew.F_Cu, net_1v8, width_mm=0.35)
add_track(board, (4.1750, 53.5), (4.1750, 53.2155), pcbnew.F_Cu, net_1v8, width_mm=0.35)
add_track(board, (4.1750, 53.5), (4.1750, 54.9955), pcbnew.F_Cu, net_1v8, width_mm=0.35)

# Connect to R3 Pin 1 (8.7985, 41.6617):
# On F.Cu: from (4.1750, 53.2155) -> (5.5, 53.2155) -> (5.5, 40.5) -> (8.7985, 40.5) -> via to B.Cu -> (8.7985, 41.6617)
add_track(board, (4.1750, 53.2155), (5.5, 53.2155), pcbnew.F_Cu, net_1v8, width_mm=0.3)
add_track(board, (5.5, 53.2155), (5.5, 40.5), pcbnew.F_Cu, net_1v8, width_mm=0.3)
add_track(board, (5.5, 40.5), (8.7985, 40.5), pcbnew.F_Cu, net_1v8, width_mm=0.3)
add_via(board, (8.7985, 40.5), net_1v8)
add_track(board, (8.7985, 40.5), (8.7985, 41.6617), pcbnew.B_Cu, net_1v8, width_mm=0.3)

# --- D. V_{IO} ---
# Connect R2 Pin 1 (16.9735, 43.3617) to R1 Pin 1 (16.9735, 45.3617) -> JP1 Pin 2 (17.7750, 50.1457) on B.Cu
add_track(board, (16.9735, 43.3617), (16.9735, 45.3617), pcbnew.B_Cu, net_vio)
add_track(board, (16.9735, 45.3617), (16.9735, 50.1457), pcbnew.B_Cu, net_vio)
add_track(board, (16.9735, 50.1457), (17.7750, 50.1457), pcbnew.B_Cu, net_vio)

# Connect to U1 Pin 5 (4.1750, 51.4355) on B.Cu:
add_track(board, (16.9735, 50.1457), (16.0, 50.1457), pcbnew.B_Cu, net_vio)
add_track(board, (16.0, 50.1457), (16.0, 51.4355), pcbnew.B_Cu, net_vio)
add_track(board, (16.0, 51.4355), (4.1750, 51.4355), pcbnew.B_Cu, net_vio)

# --- E. /RESET ---
# U1 Pin 7 (4.1750, 47.8755) to R1 Pin 2 (18.7985, 45.3617)
# On F.Cu: (4.1750, 47.8755) -> (6.5, 47.8755) -> (6.5, 45.3617) -> (18.0, 45.3617), via to B.Cu -> (18.7985, 45.3617)
add_track(board, (4.1750, 47.8755), (6.5, 47.8755), pcbnew.F_Cu, net_reset)
add_track(board, (6.5, 47.8755), (6.5, 45.3617), pcbnew.F_Cu, net_reset)
add_track(board, (6.5, 45.3617), (18.0, 45.3617), pcbnew.F_Cu, net_reset)
add_via(board, (18.0, 45.3617), net_reset)
add_track(board, (18.0, 45.3617), (18.7985, 45.3617), pcbnew.B_Cu, net_reset)

# --- F. Net-(U1-LED_P) ---
# U1 Pin 15 (14.8750, 55.8855) to R3 Pin 2 (6.9735, 41.6617)
# On F.Cu: (14.8750, 55.8855) -> (13.5, 55.8855) -> (13.5, 39.5) -> (6.9735, 39.5) -> via to B.Cu -> (6.9735, 41.6617)
add_track(board, (14.8750, 55.8855), (13.5, 55.8855), pcbnew.F_Cu, net_led)
add_track(board, (13.5, 55.8855), (13.5, 39.5), pcbnew.F_Cu, net_led)
add_track(board, (13.5, 39.5), (6.9735, 39.5), pcbnew.F_Cu, net_led)
add_via(board, (6.9735, 39.5), net_led)
add_track(board, (6.9735, 39.5), (6.9735, 41.6617), pcbnew.B_Cu, net_led)

# --- G. SPI Lines ---
# /NCS: incoming MCU via at (19.600, 40.300) to U1 Pin 13 (14.8750, 52.3255)
# On F.Cu:
add_track(board, (19.600, 40.300), (17.5, 42.4), pcbnew.F_Cu, net_ncs)
add_track(board, (17.5, 42.4), (17.5, 52.3255), pcbnew.F_Cu, net_ncs)
add_track(board, (17.5, 52.3255), (14.8750, 52.3255), pcbnew.F_Cu, net_ncs)

# /SCLK: incoming MCU track on B.Cu at (19.200, 61.263) to U1 Pin 10 (14.8750, 46.9855)
add_via(board, (19.200, 61.263), net_sclk)
add_track(board, (19.200, 61.263), (15.5, 61.263), pcbnew.F_Cu, net_sclk)
add_track(board, (15.5, 61.263), (15.5, 46.9855), pcbnew.F_Cu, net_sclk)
add_track(board, (15.5, 46.9855), (14.8750, 46.9855), pcbnew.F_Cu, net_sclk)

# /MOSI: incoming MCU track on B.Cu at (19.650, 61.812) to U1 Pin 11 (14.8750, 48.7655)
add_via(board, (19.650, 61.812), net_mosi)
add_track(board, (19.650, 61.812), (16.2, 61.812), pcbnew.F_Cu, net_mosi)
add_track(board, (16.2, 61.812), (16.2, 48.7655), pcbnew.F_Cu, net_mosi)
add_track(board, (16.2, 48.7655), (14.8750, 48.7655), pcbnew.F_Cu, net_mosi)

# /MISO: incoming MCU track on B.Cu at (20.100, 62.362) to U1 Pin 12 (14.8750, 50.5455) & R2 Pin 2 (18.7985, 43.3617)
add_via(board, (20.100, 62.362), net_miso)
add_track(board, (20.100, 62.362), (16.9, 62.362), pcbnew.F_Cu, net_miso)
add_track(board, (16.9, 62.362), (16.9, 50.5455), pcbnew.F_Cu, net_miso)
add_track(board, (16.9, 50.5455), (14.8750, 50.5455), pcbnew.F_Cu, net_miso)

# /MISO to R2 Pin 2 (18.7985, 43.3617):
add_track(board, (16.9, 50.5455), (16.9, 43.3617), pcbnew.F_Cu, net_miso)
add_track(board, (16.9, 43.3617), (18.0, 43.3617), pcbnew.F_Cu, net_miso)
add_via(board, (18.0, 43.3617), net_miso)
add_track(board, (18.0, 43.3617), (18.7985, 43.3617), pcbnew.B_Cu, net_miso)

# --- H. GND Vias ---
# U2 Pin 2 (9.5235, 63.6617)
add_via(board, (9.5235, 63.6617), net_gndr)
# C3 Pin 2 (1.8860, 62.4992)
add_via(board, (1.8860, 61.2), net_gndr)
add_track(board, (1.8860, 62.4992), (1.8860, 61.2), pcbnew.B_Cu, net_gndr, width_mm=0.3)
# C4 Pin 2 (11.4860, 64.5242)
add_via(board, (11.4860, 65.5), net_gndr)
add_track(board, (11.4860, 64.5242), (11.4860, 65.5), pcbnew.B_Cu, net_gndr, width_mm=0.3)
# C5 Pin 2 (16.5235, 64.0617)
add_via(board, (16.5235, 65.0), net_gndr)
add_track(board, (16.5235, 64.0617), (16.5235, 65.0), pcbnew.B_Cu, net_gndr, width_mm=0.3)
# C1 & C2 Pin 2 (17.0235, 54.1457 & 55.8957)
add_track(board, (17.0235, 54.1457), (17.0235, 55.8957), pcbnew.B_Cu, net_gndr, width_mm=0.3)
add_via(board, (16.2, 55.0), net_gndr)
add_track(board, (17.0235, 55.0), (16.2, 55.0), pcbnew.B_Cu, net_gndr, width_mm=0.3)

# Refill zones
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

board.Save(TEST_PCB)
print("Finished clean routing.")
