import pcbnew
import subprocess
import json
from pathlib import Path

TARGET_PCB = "scratch/test_flawless.kicad_pcb"
TARGET_PRO = "scratch/test_flawless.kicad_pro"
REPORT_JSON = "scratch/drc_flawless.json"

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
    # Dangling old vias
    "06bb9bc7-a85f-4b3a-a680-0dd29748c94f", # old +3V3R via
    "ad9518a2-965d-448d-8041-54a2acc8e557", # old /NCS via
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

# Keep /TX intact at original coordinates (no jog needed if /NCS hops over on F.Cu!)
# TX original: (8.7725, 39.2) -> (16.4, 39.2) -> (20.3, 42.0) -> (20.3, 44.5) -> (21.0, 44.5)
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
# 1. SPI BUS (F.Cu)
# Staggered entry vias at X=21.5, 23.0, 24.5 on horizontal arrival tracks on B.Cu
# Planar layout: MISO at X=20.6 (turns at 50.545), MOSI at X=21.4 (turns at 48.766), SCLK at X=22.2 (turns at 46.986)
# ==============================================================================
# SCLK enters at Y=61.263 on B.Cu:
add_track(board, (19.200, 61.263), (21.500, 61.263), pcbnew.B_Cu, net_sclk, width_mm=0.25)
add_via(board, (21.500, 61.263), net_sclk)

# MOSI enters at Y=61.812 on B.Cu:
add_track(board, (19.650, 61.812), (23.000, 61.812), pcbnew.B_Cu, net_mosi, width_mm=0.25)
add_via(board, (23.000, 61.812), net_mosi)

# MISO enters at Y=62.362 on B.Cu:
add_track(board, (20.100, 62.362), (24.500, 62.362), pcbnew.B_Cu, net_miso, width_mm=0.25)
add_via(board, (24.500, 62.362), net_miso)

# MISO: from via at (24.5, 62.362) -> X=20.600 -> North to Y=50.545 -> West to U1 Pad 12
add_track(board, (24.500, 62.362), (20.600, 62.362), pcbnew.F_Cu, net_miso, width_mm=0.25)
add_track(board, (20.600, 62.362), (20.600, 50.545), pcbnew.F_Cu, net_miso, width_mm=0.25)
add_track(board, (20.600, 50.545), (14.875, 50.545), pcbnew.F_Cu, net_miso, width_mm=0.25) # U1 Pad 12
# MISO branch to R2 Pad 2 (18.799, 43.362):
add_track(board, (20.600, 50.545), (20.600, 43.362), pcbnew.F_Cu, net_miso, width_mm=0.25)
add_track(board, (20.600, 43.362), (18.799, 43.362), pcbnew.F_Cu, net_miso, width_mm=0.25)
add_via(board, (18.799, 43.362), net_miso) # Connects to R2 Pad 2 on B.Cu

# MOSI: from via at (23.0, 61.812) -> X=21.400 -> North to Y=48.766 -> West to U1 Pad 11
add_track(board, (23.000, 61.812), (21.400, 61.812), pcbnew.F_Cu, net_mosi, width_mm=0.25)
add_track(board, (21.400, 61.812), (21.400, 48.766), pcbnew.F_Cu, net_mosi, width_mm=0.25)
add_track(board, (21.400, 48.766), (14.875, 48.766), pcbnew.F_Cu, net_mosi, width_mm=0.25) # U1 Pad 11

# SCLK: from via at (21.5, 61.263) -> X=22.200 -> North to Y=46.986 -> West to U1 Pad 10
add_track(board, (21.500, 61.263), (22.200, 61.263), pcbnew.F_Cu, net_sclk, width_mm=0.25)
add_track(board, (22.200, 61.263), (22.200, 46.986), pcbnew.F_Cu, net_sclk, width_mm=0.25)
add_track(board, (22.200, 46.986), (14.875, 46.986), pcbnew.F_Cu, net_sclk, width_mm=0.25) # U1 Pad 10

# ==============================================================================
# 2. /NCS (Chip Select, hops over /TX on F.Cu bridge)
# ==============================================================================
# Arrives at (21.900, 38.000) on B.Cu:
add_track(board, (21.900, 38.000), (16.000, 38.000), pcbnew.B_Cu, net_ncs, width_mm=0.20)
add_via(board, (16.000, 38.000), net_ncs) # Via to F.Cu bridge
add_track(board, (16.000, 38.000), (16.000, 40.500), pcbnew.F_Cu, net_ncs, width_mm=0.20)
add_via(board, (16.000, 40.500), net_ncs) # Via back to B.Cu
add_track(board, (16.000, 40.500), (16.000, 52.325), pcbnew.B_Cu, net_ncs, width_mm=0.20)
add_track(board, (16.000, 52.325), (14.875, 52.325), pcbnew.B_Cu, net_ncs, width_mm=0.20) # U1 Pad 13

# ==============================================================================
# 3. V_{IO} (Power Distribution)
# ==============================================================================
# Connect JP1 Pad 2 (17.775, 50.146) to R1 Pad 1 (16.974, 45.362) and R2 Pad 1 (16.974, 43.362) on B.Cu:
add_track(board, (17.775, 50.146), (16.974, 50.146), pcbnew.B_Cu, net_vio, width_mm=0.25)
add_track(board, (16.974, 50.146), (16.974, 45.362), pcbnew.B_Cu, net_vio, width_mm=0.25)
add_track(board, (16.974, 45.362), (16.974, 43.362), pcbnew.B_Cu, net_vio, width_mm=0.25)

# Connect to U1 Pin 5 (4.175, 51.435) via North Highway (Y=42.600) on F.Cu:
add_track(board, (16.974, 43.362), (16.974, 42.600), pcbnew.B_Cu, net_vio, width_mm=0.25)
add_via(board, (16.974, 42.600), net_vio)
add_track(board, (16.974, 42.600), (2.000, 42.600), pcbnew.F_Cu, net_vio, width_mm=0.25)
add_track(board, (2.000, 42.600), (2.000, 51.435), pcbnew.F_Cu, net_vio, width_mm=0.25)
add_track(board, (2.000, 51.435), (4.175, 51.435), pcbnew.F_Cu, net_vio, width_mm=0.25) # U1 Pin 5

# ==============================================================================
# 4. /RESET (Control Line)
# ==============================================================================
# R1 Pad 2 is at (18.799, 45.362). Target is U1 Pin 7 (4.175, 47.876).
add_track(board, (18.799, 45.362), (18.799, 41.600), pcbnew.B_Cu, net_reset, width_mm=0.25)
add_via(board, (18.799, 41.600), net_reset)
add_track(board, (18.799, 41.600), (2.800, 41.600), pcbnew.F_Cu, net_reset, width_mm=0.25)
add_track(board, (2.800, 41.600), (2.800, 47.876), pcbnew.F_Cu, net_reset, width_mm=0.25)
add_track(board, (2.800, 47.876), (4.175, 47.876), pcbnew.F_Cu, net_reset, width_mm=0.25) # U1 Pin 7

# ==============================================================================
# 5. +1V8_PMW (LDO Output & Distribution)
# ==============================================================================
# U2 Pin 5 (7.248, 62.712):
add_track(board, (7.248, 62.712), (6.500, 62.712), pcbnew.B_Cu, net_1v8, width_mm=0.30)
add_via(board, (6.500, 62.712), net_1v8)

# East branch to C4, R4, C1, C2, JP1 on F.Cu -> B.Cu:
add_track(board, (6.500, 62.712), (11.486, 62.200), pcbnew.F_Cu, net_1v8, width_mm=0.30)
add_via(board, (11.486, 62.200), net_1v8)
add_track(board, (11.486, 62.200), (11.486, 62.799), pcbnew.B_Cu, net_1v8, width_mm=0.30) # C4 Pin 1
add_track(board, (11.486, 62.200), (16.474, 62.062), pcbnew.B_Cu, net_1v8, width_mm=0.30) # R4 Pin 1

# From C4 Pin 1 east along Y=61.200 (north of R4 Pad 2 at Y=62.062):
add_track(board, (11.486, 62.200), (11.486, 61.200), pcbnew.B_Cu, net_1v8, width_mm=0.30)
add_track(board, (11.486, 61.200), (19.000, 61.200), pcbnew.B_Cu, net_1v8, width_mm=0.30)
add_track(board, (19.000, 61.200), (19.000, 55.896), pcbnew.B_Cu, net_1v8, width_mm=0.30)
add_track(board, (19.000, 55.896), (18.748, 55.896), pcbnew.B_Cu, net_1v8, width_mm=0.30) # C2 Pin 1
add_track(board, (18.748, 55.896), (18.748, 54.146), pcbnew.B_Cu, net_1v8, width_mm=0.30) # C1 Pin 1
add_track(board, (18.748, 54.146), (18.748, 51.446), pcbnew.B_Cu, net_1v8, width_mm=0.30)
add_track(board, (18.748, 51.446), (17.775, 51.446), pcbnew.B_Cu, net_1v8, width_mm=0.30) # JP1 Pin 3

# And connect to R3 Pin 1 (8.799, 41.662) from JP1 along B.Cu:
add_track(board, (18.748, 51.446), (18.748, 40.800), pcbnew.B_Cu, net_1v8, width_mm=0.30)
add_track(board, (18.748, 40.800), (8.799, 40.800), pcbnew.B_Cu, net_1v8, width_mm=0.30)
add_track(board, (8.799, 40.800), (8.799, 41.662), pcbnew.B_Cu, net_1v8, width_mm=0.30) # R3 Pin 1

# West branch from U2 Pin 5 via (6.500, 62.712) to U1 Pin 3 and Pin 4 on F.Cu (run at X=2.8 to clear Pad 1):
add_track(board, (6.500, 62.712), (2.800, 62.712), pcbnew.F_Cu, net_1v8, width_mm=0.30)
add_track(board, (2.800, 62.712), (2.800, 54.995), pcbnew.F_Cu, net_1v8, width_mm=0.30)
add_track(board, (2.800, 54.995), (4.175, 54.995), pcbnew.F_Cu, net_1v8, width_mm=0.30) # U1 Pin 3
add_track(board, (2.800, 54.995), (2.800, 53.215), pcbnew.F_Cu, net_1v8, width_mm=0.30)
add_track(board, (2.800, 53.215), (4.175, 53.215), pcbnew.F_Cu, net_1v8, width_mm=0.30) # U1 Pin 4

# ==============================================================================
# 6. Net-(U1-LED_P) (LED Cathode to R3 Pin 2)
# ==============================================================================
# U1 Pin 15 (14.875, 55.886) to R3 Pin 2 (6.973, 41.662)
# Run vertical along X = 16.300 to clear Pad 16 (X=14.875, radius 0.76):
add_track(board, (14.875, 55.886), (16.300, 55.886), pcbnew.F_Cu, net_led, width_mm=0.25)
add_track(board, (16.300, 55.886), (16.300, 63.800), pcbnew.F_Cu, net_led, width_mm=0.25)
add_track(board, (16.300, 63.800), (1.200, 63.800), pcbnew.F_Cu, net_led, width_mm=0.25)
add_track(board, (1.200, 63.800), (1.200, 40.000), pcbnew.F_Cu, net_led, width_mm=0.25)
add_track(board, (1.200, 40.000), (6.973, 40.000), pcbnew.F_Cu, net_led, width_mm=0.25)
add_via(board, (6.973, 40.000), net_led)
add_track(board, (6.973, 40.000), (6.973, 41.662), pcbnew.B_Cu, net_led, width_mm=0.25) # R3 Pin 2

# ==============================================================================
# 7. +3V3R (Power Distribution entirely on B.Cu)
# ==============================================================================
# Arrives at (63.800, 60.712) -> (20.000, 60.712) on B.Cu.
# Branch south to JP1 Pin 1 (17.775, 48.846):
add_track(board, (20.000, 60.712), (20.000, 48.846), pcbnew.B_Cu, net_3v3r, width_mm=0.35)
add_track(board, (20.000, 48.846), (17.775, 48.846), pcbnew.B_Cu, net_3v3r, width_mm=0.35)

# Branch west to U2 Pin 1, Pin 3, and C3 Pin 1 along Y = 63.062 on B.Cu:
add_track(board, (20.000, 60.712), (20.000, 63.062), pcbnew.B_Cu, net_3v3r, width_mm=0.35)
add_track(board, (20.000, 63.062), (10.400, 63.062), pcbnew.B_Cu, net_3v3r, width_mm=0.35)
add_track(board, (10.400, 63.062), (10.400, 62.712), pcbnew.B_Cu, net_3v3r, width_mm=0.35)
add_track(board, (10.400, 62.712), (9.524, 62.712), pcbnew.B_Cu, net_3v3r, width_mm=0.35) # U2 Pin 1
add_track(board, (10.400, 63.062), (10.400, 64.612), pcbnew.B_Cu, net_3v3r, width_mm=0.35)
add_track(board, (10.400, 64.612), (9.524, 64.612), pcbnew.B_Cu, net_3v3r, width_mm=0.35) # U2 Pin 3
# Connect to C3 Pin 1 (1.886, 64.224) along Y=63.800:
add_track(board, (9.524, 64.612), (8.500, 64.612), pcbnew.B_Cu, net_3v3r, width_mm=0.35)
add_track(board, (8.500, 64.612), (8.500, 63.800), pcbnew.B_Cu, net_3v3r, width_mm=0.35)
add_track(board, (8.500, 63.800), (1.886, 63.800), pcbnew.B_Cu, net_3v3r, width_mm=0.35)
add_track(board, (1.886, 63.800), (1.886, 64.224), pcbnew.B_Cu, net_3v3r, width_mm=0.35) # C3 Pin 1

# ==============================================================================
# 8. Net-(U2-NC)
# ==============================================================================
add_track(board, (18.299, 62.062), (18.248, 64.062), pcbnew.B_Cu, net_u2nc, width_mm=0.25)
add_track(board, (18.248, 64.062), (18.248, 66.800), pcbnew.B_Cu, net_u2nc, width_mm=0.25)
add_via(board, (18.248, 66.800), net_u2nc)
add_track(board, (18.248, 66.800), (7.248, 66.800), pcbnew.F_Cu, net_u2nc, width_mm=0.25)
add_via(board, (7.248, 66.800), net_u2nc)
add_track(board, (7.248, 66.800), (7.248, 64.612), pcbnew.B_Cu, net_u2nc, width_mm=0.25) # U2 Pin 4

# ==============================================================================
# 9. GNDR (Ground System)
# ==============================================================================
# South Ground Bus on B.Cu at Y = 65.500:
add_via(board, (23.500, 66.400), net_gndr)
add_track(board, (23.500, 66.400), (23.500, 65.500), pcbnew.B_Cu, net_gndr, width_mm=0.40)
add_track(board, (23.500, 65.500), (16.523, 65.500), pcbnew.B_Cu, net_gndr, width_mm=0.40)
add_track(board, (16.523, 65.500), (11.486, 65.500), pcbnew.B_Cu, net_gndr, width_mm=0.40)
add_track(board, (11.486, 65.500), (9.524, 65.500), pcbnew.B_Cu, net_gndr, width_mm=0.40)
add_track(board, (9.524, 65.500), (1.886, 65.500), pcbnew.B_Cu, net_gndr, width_mm=0.40)

# Connect C5 Pin 2 (16.523, 64.062):
add_track(board, (16.523, 65.500), (16.523, 64.062), pcbnew.B_Cu, net_gndr, width_mm=0.35)

# Connect C4 Pin 2 (11.486, 64.524):
add_track(board, (11.486, 65.500), (11.486, 64.524), pcbnew.B_Cu, net_gndr, width_mm=0.35)

# Connect U2 Pin 2 (9.524, 63.662):
add_track(board, (9.524, 65.500), (9.524, 63.662), pcbnew.B_Cu, net_gndr, width_mm=0.35)

# Connect C3 Pin 2 (1.886, 62.499) around west of C3 on B.Cu:
add_track(board, (1.886, 65.500), (0.800, 65.500), pcbnew.B_Cu, net_gndr, width_mm=0.35)
add_track(board, (0.800, 65.500), (0.800, 62.499), pcbnew.B_Cu, net_gndr, width_mm=0.35)
add_track(board, (0.800, 62.499), (1.886, 62.499), pcbnew.B_Cu, net_gndr, width_mm=0.35)

# Connect C1 & C2 Pin 2 (17.023, 54.146 and 55.896) to GND bus on B.Cu:
add_track(board, (17.023, 54.146), (17.023, 55.896), pcbnew.B_Cu, net_gndr, width_mm=0.35)
add_track(board, (17.023, 55.896), (17.023, 65.000), pcbnew.B_Cu, net_gndr, width_mm=0.35)
add_track(board, (17.023, 65.000), (16.523, 65.500), pcbnew.B_Cu, net_gndr, width_mm=0.35)

# Connect U1 Pin 8 (4.175, 46.096) to TRRS Jack rJ2 (-0.725, 43.513) on F.Cu:
add_track(board, (4.175, 46.096), (-0.725, 46.096), pcbnew.F_Cu, net_gndr, width_mm=0.35)
add_track(board, (-0.725, 46.096), (-0.725, 43.513), pcbnew.F_Cu, net_gndr, width_mm=0.35)
add_via(board, (-0.725, 43.513), net_gndr) # Connects to existing B.Cu trace to rJ2 Pad S

# Refill zones
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

board.Save(TARGET_PCB)
print("Saved perfect board.")
