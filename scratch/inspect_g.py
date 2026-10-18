with open('scratch/test_left_orig.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('G***')
fp_start = text.rfind('(footprint', 0, pos)
# find closing
count = 0
fp_end = fp_start
for i in range(fp_start, len(text)):
    if text[i] == '(': count += 1
    elif text[i] == ')':
        count -= 1
        if count == 0:
            fp_end = i + 1
            break

g_text = text[fp_start:fp_end]
print(f"G*** block length: {len(g_text)}")
import re
layers = set(re.findall(r'\(layer\s+\"([^\"]+)\"\)', g_text))
print("Layers in G***:", layers)
for l in g_text.splitlines():
    if 'fp_text' in l or 'fp_poly' in l or 'fp_line' in l or 'pad' in l:
        print(l[:80])
