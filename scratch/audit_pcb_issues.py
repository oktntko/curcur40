import re
from pathlib import Path

def audit():
    print("=================== 1. CHECK CRITICAL-1 & PCB ARCHITECTURE ===================")
    # Check right PCB: is PMW integrated or separate daughterboard?
    right_pcb = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")
    right_sch = Path("pcbs/curcur40/right/curcur40-right.kicad_sch").read_text(encoding="utf-8")
    
    has_pmw_footprint = "PMW3360DM-T2QU" in right_pcb
    has_pmw_cutout = "Edge.Cuts" in right_pcb
    has_rj3_pcb = "rJ3" in right_pcb
    has_rj3_sch = "rJ3" in right_sch
    has_pmw_sch = "PMW3360" in right_sch or "U1" in right_sch

    print(f"Right PCB has PMW3360 footprint: {has_pmw_footprint}")
    print(f"Right PCB has rJ3 (6-pin header): {has_rj3_pcb}")
    print(f"Right SCH has rJ3 (6-pin header): {has_rj3_sch}")
    print(f"Right SCH has PMW3360 / U1: {has_pmw_sch}")

    # Check trackball mounting holes in Right PCB
    print("\n--- Trackball 4 Mounting Holes in curcur40-right.kicad_pcb ---")
    tb_holes = []
    for m in re.finditer(r'\(gr_circle\s*\(center\s+([\d\.\-]+)\s+([\d\.\-]+)\)\s*\(end\s+([\d\.\-]+)\s+([\d\.\-]+)\)', right_pcb):
        pos = m.start()
        end = right_pcb.find(')', right_pcb.find('(layer', pos))
        blk = right_pcb[pos:end+1]
        if '"Edge.Cuts"' in blk:
            cx, cy, ex, ey = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
            r = ((ex - cx)**2 + (ey - cy)**2)**0.5
            if abs(cy - 52.3875) < 15 and abs(cx - 9.525) < 15:
                tb_holes.append((cx, cy, r*2))
    for cx, cy, d in tb_holes:
        print(f"  Center: ({cx:7.3f}, {cy:7.3f}) | Diam: {d:.3f} mm (Should be 3.60 mm!)")

    print("\n=================== 2. CHECK CRITICAL-2: SPACER HOLES ===================")
    # Left PCB spacer holes
    left_pcb = Path("pcbs/curcur40/left/curcur40-left.kicad_pcb").read_text(encoding="utf-8")
    print("Left PCB holes:")
    for m in re.finditer(r'\(gr_circle\s*\(center\s+([\d\.\-]+)\s+([\d\.\-]+)\)\s*\(end\s+([\d\.\-]+)\s+([\d\.\-]+)\)', left_pcb):
        pos = m.start()
        end = left_pcb.find(')', left_pcb.find('(layer', pos))
        blk = left_pcb[pos:end+1]
        if '"Edge.Cuts"' in blk:
            cx, cy, ex, ey = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
            r = ((ex - cx)**2 + (ey - cy)**2)**0.5
            print(f"  Center: ({cx:7.3f}, {cy:7.3f}) | Diam: {d:.3f} mm")

    print("\n=================== 3. CHECK CRITICAL-4 & MAJOR-1: PMW3360 DAUGHTERBOARD ===================")
    pmw_pcb_path = Path("pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pcb")
    if pmw_pcb_path.exists():
        pmw_pcb = pmw_pcb_path.read_text(encoding="utf-8")
        f_silk_count = len(re.findall(r'\(layer\s+\"F\.Silkscreen\"\)', pmw_pcb))
        b_silk_count = len(re.findall(r'\(layer\s+\"B\.Silkscreen\"\)', pmw_pcb))
        print(f"PMW3360 PCB F.Silkscreen elements: {f_silk_count}, B.Silkscreen elements: {b_silk_count}")
    
    bom_pmw_path = Path("pcbs/curcur40/pmw3360/jlcpcb/production_files/BOM-curcur40-pmw3360.csv")
    if bom_pmw_path.exists():
        bom_pmw = bom_pmw_path.read_text(encoding="utf-8")
        print(f"R1 in BOM-curcur40-pmw3360: {'R1' in bom_pmw}")
    cpl_pmw_path = Path("pcbs/curcur40/pmw3360/jlcpcb/production_files/CPL-curcur40-pmw3360.csv")
    if cpl_pmw_path.exists():
        cpl_pmw = cpl_pmw_path.read_text(encoding="utf-8")
        print(f"R1 in CPL-curcur40-pmw3360: {'R1' in cpl_pmw}")

    print("\n=================== 4. CHECK MAJOR-3: TOP PLATES ===================")
    plate_left = Path("plates/curcur40/pcb/plate-top-left.kicad_pcb").read_text(encoding="utf-8")
    plate_right = Path("plates/curcur40/pcb/plate-top-right.kicad_pcb").read_text(encoding="utf-8")
    print(f"Plate Top Left has counterbore/circles: {len(re.findall(r'gr_circle', plate_left))}")
    print(f"Plate Top Right has counterbore/circles: {len(re.findall(r'gr_circle', plate_right))}")

    print("\n=================== 5. CHECK MINOR ISSUES ===================")
    # Right PCB text thickness
    small_text = re.findall(r'\(effects\s+\(font\s+\(size\s+([\d\.\-]+)\s+([\d\.\-]+)\)\s+\(thickness\s+([\d\.\-]+)\)', right_pcb)
    too_thin = [t for t in small_text if float(t[2]) < 0.08]
    print(f"Right PCB font thickness < 0.08mm: {len(too_thin)} items")

    # Silk differences between left and right
    print(f"Left PCB B.Silkscreen count: {len(re.findall(r'\(layer\s+\"B\.Silkscreen\"\)', left_pcb))}")
    print(f"Right PCB B.Silkscreen count: {len(re.findall(r'\(layer\s+\"B\.Silkscreen\"\)', right_pcb))}")

audit()
