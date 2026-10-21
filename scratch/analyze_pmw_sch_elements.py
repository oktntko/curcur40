from pathlib import Path
import re

text = Path("pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_sch").read_text(encoding="utf-8")

# Let's extract everything after lib_symbols
pos_lib = text.find("(lib_symbols")
count, end_lib = 0, pos_lib
while end_lib < len(text):
    if text[end_lib] == '(': count += 1
    elif text[end_lib] == ')':
        count -= 1
        if count == 0: break
    end_lib += 1

body = text[end_lib+1:]

# In body, let's list all elements:
# (symbol ...), (wire ...), (junction ...), (label ...)
# We want to keep everything EXCEPT J1 and H1-H4 and TP1-TP3
def parse_body_elements(b_text):
    elems = []
    idx = 0
    while idx < len(b_text):
        pos = b_text.find("(", idx)
        if pos == -1: break
        c, end = 0, pos
        while end < len(b_text):
            if b_text[end] == '(': c += 1
            elif b_text[end] == ')':
                c -= 1
                if c == 0: break
            end += 1
        blk = b_text[pos:end+1]
        idx = end + 1
        
        # determine tag
        m_tag = re.match(r'^\(([a-zA-Z0-9_]+)', blk)
        tag = m_tag.group(1) if m_tag else ""
        elems.append((tag, blk))
    return elems

elems = parse_body_elements(body)
print(f"Total body elements: {len(elems)}")
counts = {}
for tag, blk in elems:
    counts[tag] = counts.get(tag, 0) + 1
print("Counts by tag:", counts)

# Inspect symbols
for tag, blk in elems:
    if tag == "symbol":
        m_ref = re.search(r'\(property\s+\"Reference\"\s+\"([^\"]+)\"', blk)
        m_val = re.search(r'\(property\s+\"Value\"\s+\"([^\"]+)\"', blk)
        m_at = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', blk)
        ref = m_ref.group(1) if m_ref else ""
        val = m_val.group(1) if m_val else ""
        at = (m_at.group(1), m_at.group(2)) if m_at else ("", "")
        print(f"  Symbol: [{ref:8}] {val:15} at {at}")
