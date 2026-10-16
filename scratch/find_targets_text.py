import re

with open(r"pcbs/curcur40/right/curcur40-right.kicad_pcb", "r", encoding="utf-8") as f:
    text = f.read()

# Let's search for "rJ3" and "rJ2" directly in text
for target in ["rJ3", "rJ2", "PJ-398A"]:
    pos = 0
    while True:
        idx = text.find(target, pos)
        if idx == -1:
            break
        print(f"=== Found {target} at {idx} ===")
        # print 500 chars around idx
        start = max(0, idx - 100)
        end = min(len(text), idx + 300)
        print(text[start:end])
        pos = idx + len(target)
