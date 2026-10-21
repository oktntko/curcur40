from pathlib import Path
import re

pcb = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")

pmw_refs = ['U1', 'U2', 'JP1', 'R1', 'R2', 'R3', 'R4', 'C1', 'C2', 'C3', 'C4', 'C5']

print("=== PMW FOOTPRINT LOCATIONS AND PADS ON RIGHT PCB ===")
for ref in pmw_refs:
    pos = pcb.find(f'(property "Reference" "{ref}"')
    if pos == -1: continue
    start = pcb.rfind('(footprint', 0, pos)
    count, end = 0, start
    while end < len(pcb):
        if pcb[end] == '(': count += 1
        elif pcb[end] == ')':
            count -= 1
            if count == 0: break
        end += 1
    blk = pcb[start:end+1]
    
    m_at = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)(?:\s+([\d\.\-]+))?\)', blk)
    fx, fy = float(m_at.group(1)), float(m_at.group(2))
    frot = float(m_at.group(3)) if m_at.group(3) else 0.0

    print(f"\n[{ref}] at ({fx:.3f}, {fy:.3f}, rot={frot})")
    
    # print pads
    p_idx = 0
    while True:
        pos_p = blk.find("(pad ", p_idx)
        if pos_p == -1: break
        c, end_p = 0, pos_p
        while end_p < len(blk):
            if blk[end_p] == '(': c += 1
            elif blk[end_p] == ')':
                c -= 1
                if c == 0: break
            end_p += 1
        pad_blk = blk[pos_p:end_p+1]
        p_idx = end_p + 1

        m_p = re.match(r'\(pad\s+\"([^\"]+)\"', pad_blk)
        m_net = re.search(r'\(net\s+\"([^\"]+)\"\)', pad_blk)
        m_pat = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', pad_blk)
        p_num = m_p.group(1) if m_p else "?"
        net_str = m_net.group(1) if m_net else "(no net)"
        px = float(m_pat.group(1)) if m_pat else 0.0
        py = float(m_pat.group(2)) if m_pat else 0.0
        
        # calculate absolute pad coordinate
        # Note: rotation in KiCad is CCW or CW? standard is CCW:
        import math
        rad = math.radians(frot)
        # on bottom layer B.Cu, x is mirrored if not handled, but here let's see:
        # absolute pos:
        cos_r = math.cos(rad)
        sin_r = math.sin(rad)
        # for B.Cu or standard:
        abs_x = fx + px * cos_r - py * sin_r
        abs_y = fy + px * sin_r + py * cos_r
        print(f"  Pad {p_num:4} ({net_str:16}) at local ({px:6.2f}, {py:6.2f}) -> board (~{abs_x:6.2f}, ~{abs_y:6.2f})")
