import re
from pathlib import Path

pcb = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")

def parse_blocks(b_text, tag):
    blocks = []
    idx = 0
    tag_prefix = f"({tag}"
    while True:
        pos = b_text.find(tag_prefix, idx)
        if pos == -1: break
        count, end = 0, pos
        while end < len(b_text):
            if b_text[end] == '(': count += 1
            elif b_text[end] == ')':
                count -= 1
                if count == 0: break
            end += 1
        blocks.append(b_text[pos:end+1])
        idx = end + 1
    return blocks

segments = parse_blocks(pcb, "segment")
vias = parse_blocks(pcb, "via")

print("Checking segments/vias for V_{IN} and +3V3R...")
vin_tracks = [s for s in segments if '"V_{IN}"' in s]
vin_vias = [v for v in vias if '"V_{IN}"' in v]
print(f"V_{{IN}} tracks: {len(vin_tracks)}, vias: {len(vin_vias)}")
for s in vin_tracks:
    print("  vin segment:", s.strip().replace('\n', ' '))

p3v3r_near_pmw = []
for s in segments:
    if '"+3V3R"' in s:
        # check coords
        pts = re.findall(r'\(xy\s+([\d\.\-]+)\s+([\d\.\-]+)\)', s)
        if pts:
            x1, y1 = float(pts[0][0]), float(pts[0][1])
            if x1 < 30 and y1 > 30 and y1 < 80:
                p3v3r_near_pmw.append(s)
print(f"+3V3R near PMW: {len(p3v3r_near_pmw)}")
for s in p3v3r_near_pmw:
    print("  +3v3r segment:", s.strip().replace('\n', ' '))
