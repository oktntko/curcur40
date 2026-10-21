import re
from pathlib import Path

def inspect():
    pcb_path = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb")
    sch_path = Path("pcbs/curcur40/right/curcur40-right.kicad_sch")
    pmw_sch_path = Path("pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_sch")

    pcb_text = pcb_path.read_text(encoding="utf-8")
    sch_text = sch_path.read_text(encoding="utf-8")
    pmw_sch_text = pmw_sch_path.read_text(encoding="utf-8")

    print("=== FOOTPRINTS ON RIGHT PCB RELATED TO PMW ===")
    # Extract all footprints and their references
    # in kicad_pcb: (footprint "..." ... (property "Reference" "...") ... (property "Value" "...") ... (path "...") ...)
    fps = []
    idx = 0
    while True:
        pos = pcb_text.find("(footprint ", idx)
        if pos == -1: break
        count, end = 0, pos
        while end < len(pcb_text):
            if pcb_text[end] == '(': count += 1
            elif pcb_text[end] == ')':
                count -= 1
                if count == 0: break
            end += 1
        blk = pcb_text[pos:end+1]
        idx = end + 1

        m_name = re.match(r'\(footprint\s+\"([^\"]+)\"', blk)
        name = m_name.group(1) if m_name else ""
        m_ref = re.search(r'\(property\s+\"Reference\"\s+\"([^\"]+)\"', blk)
        ref = m_ref.group(1) if m_ref else ""
        m_val = re.search(r'\(property\s+\"Value\"\s+\"([^\"]+)\"', blk)
        val = m_val.group(1) if m_val else ""
        m_at = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', blk)
        at = (m_at.group(1), m_at.group(2)) if m_at else ("", "")
        m_path = re.search(r'\(path\s+\"([^\"]+)\"', blk)
        path_str = m_path.group(1) if m_path else ""

        # pads and nets
        pads = re.findall(r'\(pad\s+\"([^\"]+)\"\s+[^\)]*\(net\s+(\d+)\s+\"([^\"]+)\"', blk)

        fps.append({
            'ref': ref, 'val': val, 'name': name, 'at': at, 'path': path_str, 'pads': pads
        })

    # Find PMW related footprints
    pmw_fps = [f for f in fps if any(k in f['ref'] for k in ['U1', 'R1', 'R2', 'R3', 'R4', 'C1', 'C2', 'C3', 'C4', 'C5']) and not f['ref'].startswith('r')]
    # Also check if there are rU1, rR1, etc.
    all_refs = {f['ref']: f for f in fps}
    print(f"Total footprints on PCB: {len(fps)}")
    print("\nNon-prefixed R/C/U footprints (likely from PMW):")
    for f in pmw_fps:
        print(f"  [{f['ref']}] {f['val']} ({f['name']}) at {f['at']}, path={f['path']}")
        for p_num, net_id, net_name in f['pads']:
            print(f"      pad {p_num:4} -> net {net_name}")

    print("\n=== rJ3 on Right PCB ===")
    if 'rJ3' in all_refs:
        print("  Found rJ3 on PCB:", all_refs['rJ3'])
    else:
        print("  rJ3 NOT found on PCB!")

    print("\n=== rJ3 in Right SCH ===")
    # Search for rJ3 in sch_text
    rj3_pos = sch_text.find('"rJ3"')
    if rj3_pos != -1:
        print("  rJ3 is present in Right SCH!")
        # show surrounding symbol block
        # find start of symbol
        s_start = sch_text.rfind('(symbol', 0, rj3_pos)
        # find matching paren
        count, s_end = 0, s_start
        while s_end < len(sch_text):
            if sch_text[s_end] == '(': count += 1
            elif sch_text[s_end] == ')':
                count -= 1
                if count == 0: break
            s_end += 1
        print("rJ3 symbol block in sch:\n", sch_text[s_start:s_end+1][:800])
    else:
        print("  rJ3 NOT in Right SCH!")

    print("\n=== PMW symbols in PMW SCH ===")
    # Extract symbols from curcur40-pmw3360.kicad_sch
    # find all symbols
    s_idx = 0
    while True:
        pos = pmw_sch_text.find("(symbol ", s_idx)
        if pos == -1: break
        count, end = 0, pos
        while end < len(pmw_sch_text):
            if pmw_sch_text[end] == '(': count += 1
            elif pmw_sch_text[end] == ')':
                count -= 1
                if count == 0: break
            end += 1
        blk = pmw_sch_text[pos:end+1]
        s_idx = end + 1

        m_ref = re.search(r'\(property\s+\"Reference\"\s+\"([^\"]+)\"', blk)
        m_val = re.search(r'\(property\s+\"Value\"\s+\"([^\"]+)\"', blk)
        if m_ref and m_val:
            print(f"  PMW_SCH Symbol: [{m_ref.group(1)}] {m_val.group(1)}")

inspect()
