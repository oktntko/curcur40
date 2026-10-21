import re
from pathlib import Path

def check_all_pcbs_and_plates():
    for name, path in [
        ("LEFT PCB", "pcbs/curcur40/left/curcur40-left.kicad_pcb"),
        ("RIGHT PCB", "pcbs/curcur40/right/curcur40-right.kicad_pcb"),
        ("PLATE TOP LEFT", "plates/curcur40/pcb/plate-top-left.kicad_pcb"),
        ("PLATE TOP RIGHT", "plates/curcur40/pcb/plate-top-right.kicad_pcb"),
    ]:
        print(f"\n=================== {name} ({path}) ===================")
        text = Path(path).read_text(encoding="utf-8")
        
        # Look for circles in Edge.Cuts
        circles = []
        for m in re.finditer(r'\(gr_circle\s*\(center\s+([\d\.\-]+)\s+([\d\.\-]+)\)\s*\(end\s+([\d\.\-]+)\s+([\d\.\-]+)\)', text):
            # check if layer is Edge.Cuts in this block
            pos = m.start()
            end = text.find(')', text.find('(layer', pos))
            blk = text[pos:end+1]
            if '"Edge.Cuts"' in blk:
                cx, cy, ex, ey = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
                r = ((ex - cx)**2 + (ey - cy)**2)**0.5
                circles.append((cx, cy, r*2))
        
        print(f"Edge.Cuts Circles ({len(circles)}):")
        for cx, cy, d in circles:
            print(f"  Center: ({cx:8.3f}, {cy:8.3f}) | Diam: {d:.3f} mm")

        # Also look for any arcs/lines forming notches around holes
        # e.g. at (-100, -22.5), (23.812, -22.5), (-23.812, -22.5), (100, -22.5)
        for target_x, target_y in [(-100.0, -22.5), (-23.812, -22.5), (23.812, -22.5), (100.0, -22.5)]:
            # check for arcs
            for m in re.finditer(r'\(gr_arc\s*\(start\s+([\d\.\-]+)\s+([\d\.\-]+)\)\s*\(mid\s+([\d\.\-]+)\s+([\d\.\-]+)\)\s*\(end\s+([\d\.\-]+)\s+([\d\.\-]+)\)', text):
                sx, sy = float(m.group(1)), float(m.group(2))
                if abs(sx - target_x) < 5 and abs(sy - target_y) < 5:
                    print(f"  Found gr_arc near ({target_x}, {target_y}): start=({sx}, {sy})")

check_all_pcbs_and_plates()
