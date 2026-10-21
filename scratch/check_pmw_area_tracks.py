from pathlib import Path
import re

pcb = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")

# Let's find all tracks in the region X in [-10, 25], Y in [40, 70]
tracks = []
idx = 0
while True:
    pos = pcb.find("(segment", idx)
    if pos == -1: break
    count, end = 0, pos
    while end < len(pcb):
        if pcb[end] == '(': count += 1
        elif pcb[end] == ')':
            count -= 1
            if count == 0: break
        end += 1
    blk = pcb[pos:end+1]
    idx = end + 1

    m_start = re.search(r'\(start\s+([\d\.\-]+)\s+([\d\.\-]+)\)', blk)
    m_end = re.search(r'\(end\s+([\d\.\-]+)\s+([\d\.\-]+)\)', blk)
    m_net = re.search(r'\(net\s+\"([^\"]+)\"\)', blk)
    m_layer = re.search(r'\(layer\s+\"([^\"]+)\"\)', blk)
    if m_start and m_end and m_net and m_layer:
        sx, sy = float(m_start.group(1)), float(m_start.group(2))
        ex, ey = float(m_end.group(1)), float(m_end.group(2))
        if -10 <= sx <= 25 and 40 <= sy <= 70:
            tracks.append((m_net.group(1), m_layer.group(1), sx, sy, ex, ey))

print(f"Tracks in PMW area: {len(tracks)}")
for t in tracks:
    print(f"  {t[0]:12} | {t[1]:5}: ({t[2]:7.3f}, {t[3]:7.3f}) -> ({t[4]:7.3f}, {t[5]:7.3f})")

# Let's also look at all vias in this region
print("\n=== Vias in PMW area ===")
for m in re.finditer(r'\(via\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)\)[^)]*\(net\s+\"([^\"]+)\"\)', pcb):
    vx, vy, net = float(m.group(1)), float(m.group(2)), m.group(3)
    if -10 <= vx <= 25 and 40 <= vy <= 70:
        print(f"  via {net:12} at ({vx:7.3f}, {vy:7.3f})")
