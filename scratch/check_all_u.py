from pathlib import Path
import re

text = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")

# Search for any footprint with U in reference or LDO
for m in re.finditer(r'\(property\s+\"Reference\"\s+\"([^\"]+)\"', text):
    ref = m.group(1)
    if 'u' in ref.lower():
        pos = m.start()
        start = text.rfind('(footprint', 0, pos)
        count, end = 0, start
        while end < len(text):
            if text[end] == '(': count += 1
            elif text[end] == ')':
                count -= 1
                if count == 0: break
            end += 1
        blk = text[start:end+1]
        val = re.search(r'\(property\s+\"Value\"\s+\"([^\"]+)\"', blk)
        v = val.group(1) if val else ""
        print(f"Footprint [{ref}] {v}")

print("\n=== Check all nets in curcur40-right.kicad_pcb ===")
# net definitions at top of kicad_pcb: (net 0 "") (net 1 "+3.3V") ...
for m in re.finditer(r'\(net\s+\d+\s+\"([^\"]+)\"\)', text):
    n = m.group(1)
    if any(k in n.lower() for k in ['pmw', '1v8', 'miso', 'mosi', 'sclk', 'cs', 'reset', 'motion', 'v_']):
        print(f"  Net: {n}")
