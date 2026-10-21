import re
from pathlib import Path

WORKSPACE = Path(r"c:\Users\oktnt\workspace\curcur40")
SCH_RIGHT_PATH = WORKSPACE / "pcbs" / "curcur40" / "right" / "curcur40-right.kicad_sch"
PCB_RIGHT_PATH = WORKSPACE / "pcbs" / "curcur40" / "right" / "curcur40-right.kicad_pcb"
SCH_PMW_PATH = WORKSPACE / "pcbs" / "curcur40" / "pmw3360" / "curcur40-pmw3360.kicad_sch"

def parse_blocks(text, tag):
    blocks = []
    idx = 0
    tag_prefix = f"({tag}"
    while True:
        pos = text.find(tag_prefix, idx)
        if pos == -1: break
        count, end = 0, pos
        while end < len(text):
            if text[end] == '(': count += 1
            elif text[end] == ')':
                count -= 1
                if count == 0: break
            end += 1
        blocks.append((pos, end+1, text[pos:end+1]))
        idx = end + 1
    return blocks

def sync():
    sch_right = SCH_RIGHT_PATH.read_text(encoding="utf-8")
    sch_pmw = SCH_PMW_PATH.read_text(encoding="utf-8")
    pcb_right = PCB_RIGHT_PATH.read_text(encoding="utf-8")

    # 1. Extract 3 lib_symbols from sch_pmw
    pos_lib = sch_pmw.find("(lib_symbols")
    count, end_lib = 0, pos_lib
    while end_lib < len(sch_pmw):
        if sch_pmw[end_lib] == '(': count += 1
        elif sch_pmw[end_lib] == ')':
            count -= 1
            if count == 0: break
        end_lib += 1
    pmw_lib_text = sch_pmw[pos_lib:end_lib+1]

    needed_syms = ["PMW3360_PCB:PMW3360DM-T2QU", "PMW3360_PCB:TLV74318PDBVR", "Jumper:SolderJumper_3_Open"]
    extracted_lib_syms = []
    for s_name in needed_syms:
        pos = pmw_lib_text.find(f'(symbol "{s_name}"')
        if pos == -1:
            print(f"ERROR: {s_name} not found in pmw lib_symbols")
            continue
        c, s_end = 0, pos
        while s_end < len(pmw_lib_text):
            if pmw_lib_text[s_end] == '(': c += 1
            elif pmw_lib_text[s_end] == ')':
                c -= 1
                if c == 0: break
            s_end += 1
        extracted_lib_syms.append(pmw_lib_text[pos:s_end+1])

    print(f"Extracted {len(extracted_lib_syms)} lib_symbols")

    # 2. Add lib_symbols to sch_right before closing ')' of (lib_symbols ...)
    # Find end of (lib_symbols ...) in sch_right
    r_pos_lib = sch_right.find("(lib_symbols")
    c, r_end_lib = 0, r_pos_lib
    while r_end_lib < len(sch_right):
        if sch_right[r_end_lib] == '(': c += 1
        elif sch_right[r_end_lib] == ')':
            c -= 1
            if c == 0: break
        r_end_lib += 1
    
    # Check if already present
    insert_syms = []
    for s_name, s_def in zip(needed_syms, extracted_lib_syms):
        if f'(symbol "{s_name}"' not in sch_right:
            insert_syms.append("\t\t" + s_def.replace("\n", "\n\t\t"))
    
    if insert_syms:
        # insert before r_end_lib
        syms_text = "\n" + "\n".join(insert_syms) + "\n\t"
        sch_right = sch_right[:r_end_lib] + syms_text + sch_right[r_end_lib:]
        print(f"Inserted {len(insert_syms)} lib_symbols into curcur40-right.kicad_sch")
    else:
        print("lib_symbols already present in curcur40-right.kicad_sch")

    # 3. Remove rJ3 from sch_right
    # find rJ3 symbol block
    rj3_pos = sch_right.find('"rJ3"')
    if rj3_pos != -1:
        s_start = sch_right.rfind('(symbol', 0, rj3_pos)
        c, s_end = 0, s_start
        while s_end < len(sch_right):
            if sch_right[s_end] == '(': c += 1
            elif sch_right[s_end] == ')':
                c -= 1
                if c == 0: break
            s_end += 1
        sch_right = sch_right[:s_start] + sch_right[s_end+1:]
        print("Removed rJ3 symbol from curcur40-right.kicad_sch")
    else:
        print("rJ3 symbol already absent")

    # Also remove wires and labels connected to old rJ3 at (303.53, 44.45)
    # The old wires connected (303.53, y) to (309.88, y)
    old_wires_to_remove = [
        "44.45", "41.91", "39.37", "36.83", "46.99", "49.53"
    ]
    # We will clean up the old wires/labels around rJ3
    # Let's see what wires exist around 303.53 to 309.88
    # We will replace this entire section with the cleanly wired PMW subcircuit!

sync()
