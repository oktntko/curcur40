import pcbnew
import subprocess
import re
from pathlib import Path

# ==============================================================================
# PART 1: Update Right PCB (curcur40-right.kicad_pcb)
# ==============================================================================
RIGHT_PCB = "pcbs/curcur40/right/curcur40-right.kicad_pcb"

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
    # Also remove old GNDR track near TB_NW hole so we reroute it cleanly at X=-4.750:
    "75aa8edf-cd0d-4360-8f29-b8b3903fba87",
    "59eec94d-38a5-441c-a9b9-48ee46eff734",
    "7dc92b6b-aadd-40f0-8f55-34e130a5d034",
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

def update_via_coords(content, u, new_at):
    idx = content.find(u)
    if idx == -1: return content
    start = content.rfind('(via', 0, idx)
    end = content.find(')', idx)
    v_txt = content[start:end+1]
    v_txt = re.sub(r'\(at\s+[\d\.\-]+\s+[\d\.\-]+\)', f'(at {new_at[0]} {new_at[1]})', v_txt)
    return content[:start] + v_txt + content[end+1:]

# Jog /TX on B.Cu: stay at X=19.200 past the NE screw hole (21.525, 41.0875), then jog to X=20.000 at Y=42.800
txt = update_segment_coords(txt, "c93696f3-c7b1-401f-9d93-13e7369537ca", (16.4, 39.2), (19.2, 42.0))
txt = update_segment_coords(txt, "29a0d305-14f2-427a-a8a7-56828070e13f", (19.2, 42.0), (20.0, 42.8))
txt = update_segment_coords(txt, "9bdeec8b-2ee5-43fa-9125-b7e91eff0fca", (20.0, 42.8), (20.0, 44.5))

# Move /NCS via at (19.6, 40.3) [uuid ad9518a2-965d-448d-8041-54a2acc8e557] to (19.6, 39.6) and angle diagonal away from 3.6mm NE hole (21.525, 41.0875):
txt = update_segment_coords(txt, "405d092f-6f5e-4846-ae4b-aac4c06eb790", (21.9, 38.0), (20.3, 38.8))
txt = update_via_coords(txt, "ad9518a2-965d-448d-8041-54a2acc8e557", (19.6, 39.6))

# Trim /MISO, /MOSI, /SCLK arrival segments on B.Cu so each stops cleanly before the SE hole or next inner line's via:
txt = update_segment_coords(txt, "2f89b3bf-61d3-4855-bf9c-d0f1bb6e77e8", (78.300, 61.2625), (19.100, 61.2625))
txt = update_segment_coords(txt, "0969c714-6562-4ffe-bc59-bdfb32431259", (78.950, 61.8125), (23.450, 61.8125))
txt = update_segment_coords(txt, "76f9bef9-74ce-46ef-87f6-b97989bb439e", (79.600, 62.3625), (24.100, 62.3625))

# Fix the inverted 270-degree bottom-left corner arc (ad53813f-cf76-4052-adaf-42c6c88ee5dd) to a clean 90-degree outer fillet:
txt = txt.replace("(mid -3.555393 65.792893)", "(mid -4.969607 67.207107)")

Path(RIGHT_PCB).write_text(txt, encoding="utf-8")

board = pcbnew.LoadBoard(RIGHT_PCB)

# Set 0.05mm solder mask margin on JP1 and U2
for ref in ["JP1", "U2"]:
    fp = board.FindFootprintByReference(ref)
    fp.SetLocalSolderMaskMargin(pcbnew.FromMM(0.05))

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

# Complete /NCS segment on B.Cu to new via at (19.6, 39.6):
add_track(board, (20.300, 38.800), (19.600, 39.600), pcbnew.B_Cu, net_ncs, width_mm=0.20)

# 1. SPI BUS
# /MISO stops at X=24.100 on B.Cu, jogs to (24.100, 62.5625)
add_track(board, (24.100, 62.3625), (24.100, 62.5625), pcbnew.B_Cu, net_miso, width_mm=0.20)
add_via(board, (24.100, 62.5625), net_miso)
# On F.Cu: pass south of 3.6mm SE hole (21.525, 63.6875) along Y=65.750 to X=19.600, then (17.300, 63.450) -> North to U1 Pad 12
add_track(board, (24.100, 62.5625), (24.100, 65.750), pcbnew.F_Cu, net_miso, width_mm=0.20)
add_track(board, (24.100, 65.750), (19.600, 65.750), pcbnew.F_Cu, net_miso, width_mm=0.20)
add_track(board, (19.600, 65.750), (17.300, 63.450), pcbnew.F_Cu, net_miso, width_mm=0.20)
add_track(board, (17.300, 63.450), (17.300, 50.5455), pcbnew.F_Cu, net_miso, width_mm=0.20)
add_track(board, (17.300, 50.5455), (14.8750, 50.5455), pcbnew.F_Cu, net_miso, width_mm=0.20)
# Branch from (24.100, 62.5625) north along X=24.100 on F.Cu to R2 Pad 2 (18.7985, 43.3617):
add_track(board, (24.100, 62.5625), (24.100, 43.3617), pcbnew.F_Cu, net_miso, width_mm=0.20)
add_track(board, (24.100, 43.3617), (18.7985, 43.3617), pcbnew.F_Cu, net_miso, width_mm=0.20)
add_via(board, (18.7985, 43.3617), net_miso)

# /MOSI stops at X=23.450 on B.Cu (east of 3.6mm SE hole!), via at (23.450, 61.980), then passes north of SE hole on F.Cu at Y=61.400:
add_track(board, (23.450, 61.8125), (23.450, 61.980), pcbnew.B_Cu, net_mosi, width_mm=0.20)
add_via(board, (23.450, 61.980), net_mosi)
add_track(board, (23.450, 61.980), (22.870, 61.400), pcbnew.F_Cu, net_mosi, width_mm=0.20)
add_track(board, (22.870, 61.400), (20.100, 61.400), pcbnew.F_Cu, net_mosi, width_mm=0.20)
add_track(board, (20.100, 61.400), (19.520, 61.980), pcbnew.F_Cu, net_mosi, width_mm=0.20)
add_track(board, (19.520, 61.980), (17.900, 61.980), pcbnew.F_Cu, net_mosi, width_mm=0.20)
add_track(board, (17.900, 61.980), (17.900, 48.7655), pcbnew.F_Cu, net_mosi, width_mm=0.20)
add_track(board, (17.900, 48.7655), (14.8750, 48.7655), pcbnew.F_Cu, net_mosi, width_mm=0.20)

# /SCLK stops at X=19.100 on B.Cu, jogs to (19.100, 61.150)
add_track(board, (19.100, 61.2625), (19.100, 61.150), pcbnew.B_Cu, net_sclk, width_mm=0.20)
add_via(board, (19.100, 61.150), net_sclk)
add_track(board, (19.100, 61.150), (18.500, 61.150), pcbnew.F_Cu, net_sclk, width_mm=0.20)
add_track(board, (18.500, 61.150), (18.500, 46.9855), pcbnew.F_Cu, net_sclk, width_mm=0.20)
add_track(board, (18.500, 46.9855), (14.8750, 46.9855), pcbnew.F_Cu, net_sclk, width_mm=0.20)

# 2. /NCS (from new via at (19.600, 39.600) on F.Cu -> (18.900, 40.300) -> (16.050, 40.300))
add_track(board, (19.600, 39.600), (18.900, 40.300), pcbnew.F_Cu, net_ncs, width_mm=0.20)
add_track(board, (18.900, 40.300), (16.050, 40.300), pcbnew.F_Cu, net_ncs, width_mm=0.20)
add_via(board, (16.050, 40.300), net_ncs)
add_track(board, (16.050, 40.300), (16.050, 52.3255), pcbnew.B_Cu, net_ncs, width_mm=0.20)
add_track(board, (16.050, 52.3255), (14.8750, 52.3255), pcbnew.B_Cu, net_ncs, width_mm=0.20)

# 3. 4 Nested Planar Loops on F.Cu
# Loop 1: /RESET
add_via(board, (18.7985, 45.3617), net_reset)
add_track(board, (18.7985, 45.3617), (17.800, 45.3617), pcbnew.F_Cu, net_reset, width_mm=0.20)
add_track(board, (17.800, 45.3617), (17.800, 42.400), pcbnew.F_Cu, net_reset, width_mm=0.20)
add_track(board, (17.800, 42.400), (2.700, 42.400), pcbnew.F_Cu, net_reset, width_mm=0.20)
add_track(board, (2.700, 42.400), (2.700, 47.8755), pcbnew.F_Cu, net_reset, width_mm=0.20)
add_track(board, (2.700, 47.8755), (4.1750, 47.8755), pcbnew.F_Cu, net_reset, width_mm=0.20)

# Loop 2: V_{IO}
add_track(board, (17.7750, 50.1457), (16.650, 50.1457), pcbnew.B_Cu, net_vio, width_mm=0.20)
add_track(board, (16.650, 50.1457), (16.650, 45.3617), pcbnew.B_Cu, net_vio, width_mm=0.20)
add_track(board, (16.650, 45.3617), (16.9735, 45.3617), pcbnew.B_Cu, net_vio, width_mm=0.20)
add_track(board, (16.9735, 45.3617), (16.9735, 43.3617), pcbnew.B_Cu, net_vio, width_mm=0.20)
add_track(board, (16.9735, 43.3617), (16.650, 41.600), pcbnew.B_Cu, net_vio, width_mm=0.20)
add_via(board, (16.650, 41.600), net_vio)
add_track(board, (16.650, 41.600), (2.100, 41.600), pcbnew.F_Cu, net_vio, width_mm=0.20)
add_track(board, (2.100, 41.600), (2.100, 51.4355), pcbnew.F_Cu, net_vio, width_mm=0.20)
add_track(board, (2.100, 51.4355), (4.1750, 51.4355), pcbnew.F_Cu, net_vio, width_mm=0.20)

# Loop 3: +1V8_PMW
add_track(board, (7.2485, 62.7117), (7.2485, 61.800), pcbnew.B_Cu, net_1v8, width_mm=0.25)
add_track(board, (7.2485, 61.800), (11.4860, 61.800), pcbnew.B_Cu, net_1v8, width_mm=0.25)
add_track(board, (11.4860, 61.800), (11.4860, 62.7992), pcbnew.B_Cu, net_1v8, width_mm=0.25)
add_track(board, (11.4860, 61.800), (16.4735, 61.800), pcbnew.B_Cu, net_1v8, width_mm=0.25)
add_track(board, (16.4735, 61.800), (16.4735, 62.0617), pcbnew.B_Cu, net_1v8, width_mm=0.25)
add_track(board, (16.4735, 61.800), (16.4735, 57.500), pcbnew.B_Cu, net_1v8, width_mm=0.25)
add_track(board, (16.4735, 57.500), (18.7485, 57.500), pcbnew.B_Cu, net_1v8, width_mm=0.25)
add_track(board, (18.7485, 57.500), (18.7485, 55.8957), pcbnew.B_Cu, net_1v8, width_mm=0.25)
add_track(board, (18.7485, 55.8957), (18.7485, 54.1457), pcbnew.B_Cu, net_1v8, width_mm=0.25)
add_track(board, (18.7485, 54.1457), (18.7485, 51.4457), pcbnew.B_Cu, net_1v8, width_mm=0.25)
add_track(board, (18.7485, 51.4457), (17.7750, 51.4457), pcbnew.B_Cu, net_1v8, width_mm=0.25)

add_track(board, (7.2485, 62.7117), (6.500, 62.7117), pcbnew.B_Cu, net_1v8, width_mm=0.25)
add_via(board, (6.500, 62.7117), net_1v8)
add_track(board, (6.500, 62.7117), (1.500, 62.7117), pcbnew.F_Cu, net_1v8, width_mm=0.25)
add_track(board, (1.500, 62.7117), (1.500, 54.9955), pcbnew.F_Cu, net_1v8, width_mm=0.25)
add_track(board, (1.500, 54.9955), (4.1750, 54.9955), pcbnew.F_Cu, net_1v8, width_mm=0.25)
add_track(board, (1.500, 54.9955), (1.500, 53.2155), pcbnew.F_Cu, net_1v8, width_mm=0.25)
add_track(board, (1.500, 53.2155), (4.1750, 53.2155), pcbnew.F_Cu, net_1v8, width_mm=0.25)
add_track(board, (1.500, 53.2155), (1.500, 40.800), pcbnew.F_Cu, net_1v8, width_mm=0.25)
add_track(board, (1.500, 40.800), (8.7985, 40.800), pcbnew.F_Cu, net_1v8, width_mm=0.25)
add_via(board, (8.7985, 40.800), net_1v8)
add_track(board, (8.7985, 40.800), (8.7985, 41.6617), pcbnew.B_Cu, net_1v8, width_mm=0.25)

# Loop 4: Net-(U1-LED_P)
add_track(board, (14.8750, 55.8855), (16.000, 55.8855), pcbnew.F_Cu, net_led, width_mm=0.25)
add_track(board, (16.000, 55.8855), (16.000, 63.400), pcbnew.F_Cu, net_led, width_mm=0.25)
add_track(board, (16.000, 63.400), (0.800, 63.400), pcbnew.F_Cu, net_led, width_mm=0.25)
add_track(board, (0.800, 63.400), (0.800, 40.000), pcbnew.F_Cu, net_led, width_mm=0.25)
add_track(board, (0.800, 40.000), (6.9735, 40.000), pcbnew.F_Cu, net_led, width_mm=0.25)
add_via(board, (6.9735, 40.000), net_led)
add_track(board, (6.9735, 40.000), (6.9735, 41.6617), pcbnew.B_Cu, net_led, width_mm=0.25)

# 4. South Corridor (+3V3R, Net-(U2-NC), GNDR)
add_track(board, (20.000, 60.712), (20.000, 48.8457), pcbnew.F_Cu, net_3v3r, width_mm=0.30)
add_via(board, (20.000, 48.8457), net_3v3r)
add_track(board, (20.000, 48.8457), (17.7750, 48.8457), pcbnew.B_Cu, net_3v3r, width_mm=0.30)

add_track(board, (24.800, 60.712), (24.800, 60.500), pcbnew.B_Cu, net_3v3r, width_mm=0.25)
add_via(board, (24.800, 60.500), net_3v3r)
add_track(board, (24.800, 60.500), (24.800, 66.200), pcbnew.F_Cu, net_3v3r, width_mm=0.25)
add_track(board, (24.800, 66.200), (19.400, 66.200), pcbnew.F_Cu, net_3v3r, width_mm=0.25)
add_track(board, (19.400, 66.200), (18.500, 65.300), pcbnew.F_Cu, net_3v3r, width_mm=0.25)
add_track(board, (18.500, 65.300), (10.450, 65.300), pcbnew.F_Cu, net_3v3r, width_mm=0.25)
add_via(board, (10.450, 65.300), net_3v3r)
add_track(board, (10.450, 65.300), (10.600, 64.6117), pcbnew.B_Cu, net_3v3r, width_mm=0.20)
add_track(board, (10.600, 64.6117), (9.5235, 64.6117), pcbnew.B_Cu, net_3v3r, width_mm=0.20)
add_track(board, (10.600, 64.6117), (10.600, 62.7117), pcbnew.B_Cu, net_3v3r, width_mm=0.20)
add_track(board, (10.600, 62.7117), (9.5235, 62.7117), pcbnew.B_Cu, net_3v3r, width_mm=0.20)

add_track(board, (10.450, 65.300), (1.8860, 65.300), pcbnew.F_Cu, net_3v3r, width_mm=0.25)
add_via(board, (1.8860, 65.300), net_3v3r)
add_track(board, (1.8860, 65.300), (1.8860, 64.2242), pcbnew.B_Cu, net_3v3r, width_mm=0.25)

# Net-(U2-NC)
add_track(board, (18.2985, 62.0617), (18.2485, 64.0617), pcbnew.B_Cu, net_u2nc, width_mm=0.20)
add_track(board, (18.2485, 64.0617), (18.2485, 66.000), pcbnew.B_Cu, net_u2nc, width_mm=0.20)
add_via(board, (18.2485, 66.000), net_u2nc)
add_track(board, (18.2485, 66.000), (7.2485, 66.000), pcbnew.F_Cu, net_u2nc, width_mm=0.20)
add_via(board, (7.2485, 66.000), net_u2nc)
add_track(board, (7.2485, 66.000), (7.2485, 64.6117), pcbnew.B_Cu, net_u2nc, width_mm=0.20)

# GNDR
add_via(board, (23.500, 66.900), net_gndr)
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

add_track(board, (17.0235, 54.1457), (17.0235, 55.8957), pcbnew.B_Cu, net_gndr, width_mm=0.25)
add_track(board, (17.0235, 54.1457), (16.650, 54.1457), pcbnew.B_Cu, net_gndr, width_mm=0.25)
add_via(board, (16.650, 54.1457), net_gndr)
add_track(board, (16.650, 54.1457), (16.650, 64.250), pcbnew.F_Cu, net_gndr, width_mm=0.25)
add_track(board, (16.650, 64.250), (15.650, 64.250), pcbnew.F_Cu, net_gndr, width_mm=0.25)
add_via(board, (15.650, 64.250), net_gndr)
add_track(board, (15.650, 64.250), (16.5235, 64.0617), pcbnew.B_Cu, net_gndr, width_mm=0.25)

# Connect lower GNDR bus (0.800, 62.4992) -> (0.800, 61.400) -> (-4.750, 61.400) -> (-4.750, 46.0955) [U1 Pin 8] -> (-4.750, 38.54625) [rJ2 Pad S] on B.Cu (clearing 3.6mm TB_SW & TB_NW holes!):
add_track(board, (0.800, 62.4992), (0.800, 61.400), pcbnew.B_Cu, net_gndr, width_mm=0.25)
add_track(board, (0.800, 61.400), (-4.750, 61.400), pcbnew.B_Cu, net_gndr, width_mm=0.25)
add_track(board, (-4.750, 61.400), (-4.750, 46.0955), pcbnew.B_Cu, net_gndr, width_mm=0.25)
add_track(board, (4.1750, 46.0955), (-4.750, 46.0955), pcbnew.B_Cu, net_gndr, width_mm=0.25)
add_track(board, (-4.750, 46.0955), (-4.750, 38.54625), pcbnew.B_Cu, net_gndr, width_mm=0.25)
add_track(board, (-4.750, 38.54625), (-2.4575, 38.54625), pcbnew.B_Cu, net_gndr, width_mm=0.25)

# ==============================================================================
# Edge.Cuts Update on Right PCB:
# 1. Remove duplicate bottom line (7fe5b3ae)
# 2. Remove the 9 top-edge U-notch segments/arcs between X=16.8575 and X=118.0625
# 3. Remove all existing Edge.Cuts circles
# 4. Add straight top line (16.8575, -24.3125) -> (118.0625, -24.3125)
# 5. Add TRRS cutout 3 lines
# 6. Add 8 unified 3.60mm (r=1.80mm) circles
# ==============================================================================
REMOVE_EDGE_UUIDS_RIGHT = {
    "7fe5b3ae-2c4a-45b5-a08d-f31251082324", # duplicate bottom line
    "ee89917d-5b29-43a7-90ac-f6e175958281", # top U-notch seg 1
    "b169cb8c-f3e8-4169-9c64-373bb2512e75", # top U-notch seg 2
    "adbbe220-d139-4ccf-8c90-2dae805fa141", # top U-notch arc 1
    "011062ac-6373-444a-9ac9-6c020bb9edc3", # top U-notch seg 3
    "fcc79097-cfad-40b2-9e36-8197c947e6dc", # top U-notch seg 4
    "48135028-5a3d-4bee-a1c3-4d836d9e0de3", # top U-notch seg 5
    "ac11842c-80f7-4e2a-a34c-d2b523be5ae1", # top U-notch arc 2
    "9716c3ad-1225-4981-a614-d412341c1286", # top U-notch seg 6
    "62cc997b-ca53-4e44-9b43-0b7fd3399e1b", # top U-notch seg 7
}

for d in list(board.GetDrawings()):
    if d.GetLayer() == pcbnew.Edge_Cuts:
        if d.GetShape() == pcbnew.SHAPE_T_CIRCLE or d.m_Uuid.AsString() in REMOVE_EDGE_UUIDS_RIGHT:
            board.Delete(d)

def add_edge_line(b, p1, p2):
    s = pcbnew.PCB_SHAPE(b)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetStart(pcbnew.VECTOR2I_MM(p1[0], p1[1]))
    s.SetEnd(pcbnew.VECTOR2I_MM(p2[0], p2[1]))
    s.SetWidth(pcbnew.FromMM(0.1))
    b.Add(s)

def add_edge_circle(b, center, radius_mm=1.80):
    c = pcbnew.PCB_SHAPE(b)
    c.SetShape(pcbnew.SHAPE_T_CIRCLE)
    c.SetLayer(pcbnew.Edge_Cuts)
    c.SetCenter(pcbnew.VECTOR2I_MM(center[0], center[1]))
    c.SetEnd(pcbnew.VECTOR2I_MM(center[0] + radius_mm, center[1]))
    c.SetWidth(pcbnew.FromMM(0.1))
    b.Add(c)

# Straight top line without U-notches
add_edge_line(board, (16.8575, -24.3125), (118.0625, -24.3125))

# TRRS cutout
add_edge_line(board, (-5.2625, 31.5), (7.7425, 31.5))
add_edge_line(board, (7.7425, 31.5), (7.7425, 37.8))
add_edge_line(board, (7.7425, 37.8), (-5.2625, 37.8))

# 8 unified ∅3.60mm (r=1.80mm) holes on Right PCB:
RIGHT_HOLES = [
    # 4 Trackball holes
    (-2.4750, 41.0875),
    (21.5250, 41.0875),
    (-2.4750, 63.6875),
    (21.5250, 63.6875),
    # Perimeter holes
    (0.0000, -15.0000),
    (0.0000, 25.0000),
    (109.5375, -20.0000),
    (98.0000, 38.0000),
]
for h in RIGHT_HOLES:
    add_edge_circle(board, h, radius_mm=1.80)

filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())
board.Save(RIGHT_PCB)
print("Updated Right PCB.")

# ==============================================================================
# PART 2: Update Left PCB (curcur40-left.kicad_pcb)
# ==============================================================================
LEFT_PCB = "pcbs/curcur40/left/curcur40-left.kicad_pcb"
board_l = pcbnew.LoadBoard(LEFT_PCB)

for d in list(board_l.GetDrawings()):
    if d.GetLayer() == pcbnew.Edge_Cuts:
        if d.GetShape() == pcbnew.SHAPE_T_CIRCLE:
            board_l.Delete(d)
        else:
            p1 = (round(pcbnew.ToMM(d.GetStart().x), 4), round(pcbnew.ToMM(d.GetStart().y), 4))
            p2 = (round(pcbnew.ToMM(d.GetEnd().x), 4), round(pcbnew.ToMM(d.GetEnd().y), 4))
            # Remove the 9 top-edge U-notch segments/arcs between X=-118.0625 and X=-16.8575
            if min(p1[0], p2[0]) >= -118.1 and max(p1[0], p2[0]) <= -16.8 and max(p1[1], p2[1]) <= -22.0:
                board_l.Delete(d)

# Straight top line without U-notches on Left PCB
add_edge_line(board_l, (-118.0625, -24.3125), (-16.8575, -24.3125))

# 5 unified ∅3.60mm (r=1.80mm) holes on Left PCB:
LEFT_HOLES = [
    (0.0000, -15.0000),
    (0.0000, 25.0000),
    (-109.5375, -20.0000),
    (-98.0000, 38.0000),
    (-23.8125, 64.0000),
]
for h in LEFT_HOLES:
    add_edge_circle(board_l, h, radius_mm=1.80)

filler_l = pcbnew.ZONE_FILLER(board_l)
filler_l.Fill(board_l.Zones())
board_l.Save(LEFT_PCB)
print("Updated Left PCB.")
