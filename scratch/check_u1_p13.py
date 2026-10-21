from pathlib import Path
import re

text = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")

# Find U1 pad 13
pos = text.find('(property "Reference" "U1"')
start = text.rfind('(footprint', 0, pos)
count, end = 0, start
while end < len(text):
    if text[end] == '(': count += 1
    elif text[end] == ')':
        count -= 1
        if count == 0: break
    end += 1
u1_blk = text[start:end+1]

# find pad 13 in u1_blk
p13_pos = u1_blk.find('(pad "13"')
if p13_pos != -1:
    end_p13 = u1_blk.find(')', u1_blk.find('(net', p13_pos))
    print("Pad 13 block in U1:\n", u1_blk[p13_pos:end_p13+10])

# find all tracks with /NCS or /CS
print("\nTracks with NCS or CS:")
for m in re.finditer(r'\(segment\s+[^\)]*\(net\s+\"([^\"]*CS[^\"]*)\"\)[^\)]*\)', text):
    print(m.group(0))
