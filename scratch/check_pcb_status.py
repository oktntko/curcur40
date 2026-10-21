import re
from pathlib import Path

def get_circles(text):
    circles = []
    # Find each (gr_circle ...) block
    idx = 0
    while True:
        pos = text.find("(gr_circle", idx)
        if pos == -1:
            break
        # find matching paren
        count = 0
        end = pos
        while end < len(text):
            if text[end] == '(':
                count += 1
            elif text[end] == ')':
                count -= 1
                if count == 0:
                    break
            end += 1
        blk = text[pos:end+1]
        idx = end + 1

        if '"Edge.Cuts"' in blk:
            m_c = re.search(r'\(center\s+([\d\.\-]+)\s+([\d\.\-]+)\)', blk)
            m_e = re.search(r'\(end\s+([\d\.\-]+)\s+([\d\.\-]+)\)', blk)
            if m_c and m_e:
                cx, cy = float(m_c.group(1)), float(m_c.group(2))
                ex, ey = float(m_e.group(1)), float(m_e.group(2))
                r = ((ex - cx)**2 + (ey - cy)**2)**0.5
                circles.append((cx, cy, r*2))
    return circles

def get_footprints(text):
    fps = []
    idx = 0
    while True:
        pos = text.find("(footprint ", idx)
        if pos == -1:
            break
        count = 0
        end = pos
        while end < len(text):
            if text[end] == '(':
                count += 1
            elif text[end] == ')':
                count -= 1
                if count == 0:
                    break
            end += 1
        blk = text[pos:end+1]
        idx = end + 1

        m_name = re.match(r'\(footprint\s+\"([^\"]+)\"', blk)
        name = m_name.group(1) if m_name else "unknown"
        m_at = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', blk)
        at = (float(m_at.group(1)), float(m_at.group(2))) if m_at else (0, 0)
        m_ref = re.search(r'\(property\s+\"Reference\"\s+\"([^\"]+)\"', blk)
        ref = m_ref.group(1) if m_ref else ""
        fps.append((ref, name, at))
    return fps

def run():
    for label, path in [
        ("LEFT PCB", "pcbs/curcur40/left/curcur40-left.kicad_pcb"),
        ("RIGHT PCB", "pcbs/curcur40/right/curcur40-right.kicad_pcb"),
        ("PMW3360 PCB", "pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pcb"),
        ("PLATE TOP LEFT", "plates/curcur40/pcb/plate-top-left.kicad_pcb"),
        ("PLATE TOP RIGHT", "plates/curcur40/pcb/plate-top-right.kicad_pcb"),
    ]:
        p = Path(path)
        if not p.exists():
            print(f"File not found: {path}")
            continue
        text = p.read_text(encoding="utf-8")
        circles = get_circles(text)
        print(f"\n=================== {label} ===================")
        print(f"File: {path}")
        print(f"Edge.Cuts circles ({len(circles)} found):")
        for cx, cy, d in circles:
            print(f"  Center: ({cx:8.3f}, {cy:8.3f}) | Diam: {d:6.3f} mm (Radius {d/2:6.3f} mm)")

        fps = get_footprints(text)
        mount_fps = [fp for fp in fps if any(k in fp[1].lower() or k in fp[0].lower() for k in ['mount', 'hole', 'h1', 'h2', 'h3', 'h4', 'rh'])]
        if mount_fps:
            print("Mounting / Hole footprints:")
            for ref, name, at in mount_fps:
                print(f"  [{ref}] {name} at {at}")

        # Check U1 / PMW3360
        pmw_fps = [fp for fp in fps if 'pmw' in fp[1].lower() or 'pmw' in fp[0].lower() or fp[0] in ['U1', 'rU1']]
        if pmw_fps:
            print("PMW footprints:")
            for ref, name, at in pmw_fps:
                print(f"  [{ref}] {name} at {at}")

run()
