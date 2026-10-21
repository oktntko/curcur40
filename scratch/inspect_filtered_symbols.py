import re
from pathlib import Path

WORKSPACE = Path(r"c:\Users\oktnt\workspace\curcur40")
SCH_PMW_PATH = WORKSPACE / "pcbs" / "curcur40" / "pmw3360" / "curcur40-pmw3360.kicad_sch"
text = SCH_PMW_PATH.read_text(encoding="utf-8")

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

pos_lib = text.find("(lib_symbols")
count, end_lib = 0, pos_lib
while end_lib < len(text):
    if text[end_lib] == '(': count += 1
    elif text[end_lib] == ')':
        count -= 1
        if count == 0: break
    end_lib += 1
body = text[end_lib+1:]
symbols = parse_blocks(body, "symbol")

for s in symbols:
    m_ref = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', s)
    ref = m_ref.group(1) if m_ref else ""
    m_val = re.search(r'\(property\s+"Value"\s+"([^"]+)"', s)
    val = m_val.group(1) if m_val else ""
    m_lib = re.search(r'\(lib_id\s+"([^"]+)"', s)
    lib = m_lib.group(1) if m_lib else ""
    m_at = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', s)
    x = float(m_at.group(1)) if m_at else 0
    y = float(m_at.group(2)) if m_at else 0
    if x < 215:
        print(f"{ref:10} {val:20} {lib:35} at ({x}, {y})")
