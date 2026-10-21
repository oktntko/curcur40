import re
from pathlib import Path
import pcbnew

pcb_pmw = pcbnew.LoadBoard("scratch/pmw3360_pcb_b9043a22.kicad_pcb")
pcb_right = pcbnew.LoadBoard("pcbs/curcur40/right/curcur40-right.kicad_pcb")

u1_p = pcb_pmw.FindFootprintByReference("U1").GetPosition()
u1_r = pcb_right.FindFootprintByReference("U1").GetPosition()
dx = u1_r.x - u1_p.x
dy = u1_r.y - u1_p.y

# Map nets from PMW to Right:
net_map = {
    "GND": "GNDR",
    "VDD": "+1V8_PMW",
    "V_{IN}": "+3V3R",
    "V_{IO}": "V_{IO}",
    "/CS": "/NCS",
    "/SCLK": "/SCLK",
    "/MOSI": "/MOSI",
    "/MISO": "/MISO",
    "/RESET": "/RESET",
    "/MOTION": "/MOTION",
    "Net-(U1-LED_P)": "Net-(U1-LED_P)",
    "Net-(U2-NC)": "Net-(U2-NC)",
}

# For each track in PMW, translate and swap layer F.Cu <-> B.Cu
# Check how close it is to pads in Right PCB
tracks_pmw = pcb_pmw.GetTracks()
print(f"Total tracks in PMW: {len(tracks_pmw)}")

# Test one track connected to U2 pin 1
for t in tracks_pmw:
    net_name = t.GetNetname()
    start = t.GetStart()
    end = t.GetEnd()
    # translated:
    sx = pcbnew.ToMM(start.x + dx)
    sy = pcbnew.ToMM(start.y + dy)
    ex = pcbnew.ToMM(end.x + dx)
    ey = pcbnew.ToMM(end.y + dy)
    layer = "B.Cu" if t.GetLayer() == pcbnew.F_Cu else "F.Cu"

    # If it connects to U2
    if net_name in ["V_{IN}", "VDD"]:
        print(f"Track {net_name} ({layer}): ({sx:.3f}, {sy:.3f}) -> ({ex:.3f}, {ey:.3f})")
        break

# Compare with U2 Pad 1 in Right
p1_u2 = pcb_right.FindFootprintByReference("U2").FindPadByNumber("1").GetPosition()
print(f"U2 Pad 1 in Right: ({pcbnew.ToMM(p1_u2.x):.3f}, {pcbnew.ToMM(p1_u2.y):.3f})")
