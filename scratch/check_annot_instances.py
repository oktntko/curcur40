import re
from pathlib import Path

sch = Path("pcbs/curcur40/right/curcur40-right.kicad_sch").read_text(encoding="utf-8")

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

pos_lib = sch.find("(lib_symbols")
c, end_lib = 0, pos_lib
while end_lib < len(sch):
    if sch[end_lib] == '(': c += 1
    elif sch[end_lib] == ')':
        c -= 1
        if c == 0: break
    end_lib += 1

body = sch[end_lib+1:]
symbols = parse_blocks(body, "symbol")

print(f"Total symbols in body: {len(symbols)}")
for s in symbols:
    m_ref = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', s)
    ref = m_ref.group(1) if m_ref else ""
    # check if reference ends with ? or has ?
    if '?' in ref:
        print(f"Contains ?: {ref}")
    # check unit
    m_unit = re.search(r'\(unit\s+(\d+)\)', s)
    # check in_bom, on_board
    # check instances
    m_inst = re.search(r'\(instances.*?\)', s, re.DOTALL)
    if not m_inst:
        print(f"No instances: {ref}")
    else:
        # check if reference in instance matches symbol reference!
        m_inst_ref = re.search(r'\(reference\s+"([^"]+)"\)', m_inst.group(0))
        if m_inst_ref and m_inst_ref.group(1) != ref:
            print(f"Ref mismatch: sym={ref} != inst={m_inst_ref.group(1)}")
        if not m_inst_ref:
            print(f"No reference in instance: {ref}")
