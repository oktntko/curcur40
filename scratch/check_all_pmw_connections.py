from pathlib import Path
import re

pcb = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")

pmw_refs = ['U1', 'U2', 'JP1', 'R1', 'R2', 'R3', 'R4', 'C1', 'C2', 'C3', 'C4', 'C5']

print("=== ALL PADS OF PMW COMPONENTS IN RIGHT PCB ===")
pad_info = []
for ref in pmw_refs:
    pos = pcb.find(f'(property "Reference" "{ref}"')
    if pos == -1: 
        print(f"[{ref}] NOT FOUND")
        continue
    start = pcb.rfind('(footprint', 0, pos)
    count, end = 0, start
    while end < len(pcb):
        if pcb[end] == '(': count += 1
        elif pcb[end] == ')':
            count -= 1
            if count == 0: break
        end += 1
    blk = pcb[start:end+1]
    
    # Footprint pos & rot
    m_at = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)(?:\s+([\d\.\-]+))?\)', blk)
    fx, fy = float(m_at.group(1)), float(m_at.group(2))
    frot = float(m_at.group(3)) if m_at.group(3) else 0.0

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
        p_num = m_p.group(1) if m_p else "?"
        net_str = m_net.group(1) if m_net else "(NO NET)"
        
        # pad relative position
        m_pat = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', pad_blk)
        px = float(m_pat.group(1)) if m_pat else 0.0
        py = float(m_pat.group(2)) if m_pat else 0.0

        pad_info.append((ref, p_num, net_str, px, py))
        print(f"[{ref:4}] Pad {p_num:4} -> net: '{net_str}'")

print("\n=== SUMMARY OF ALL NETS IN PMW COMPONENTS ===")
unique_nets = set(p[2] for p in pad_info)
for n in sorted(unique_nets):
    # count how many times this net appears in segments or vias
    seg_count = len(re.findall(rf'\(net\s+\"{re.escape(n)}\"\)', pcb))
    print(f"  Net '{n}': {seg_count} segment/pad occurrences in PCB")
