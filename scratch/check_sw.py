import re

with open('pcbs/curcur40/left/curcur40-left.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

def get_fp(ref):
    pattern = rf'\(footprint [^\n]+\n\t\t\(layer \"[^\"]+\"\)\n\t\t\(uuid \"[^\"]+\"\)\n\t\t\(at [^\n]+\)\n\t\t\(descr [^\n]+\)\n\t\t\(tags [^\n]+\)\n\t\t\(property \"Reference\" \"{ref}\"'
    idx = text.find(f'property "Reference" "{ref}"')
    if idx == -1:
        return None
    # find preceding '(footprint'
    fp_start = text.rfind('\n\t(footprint ', 0, idx)
    # find end of footprint
    # count parens
    open_p = 0
    i = fp_start + 1
    while i < len(text):
        if text[i] == '(':
            open_p += 1
        elif text[i] == ')':
            open_p -= 1
            if open_p == 0:
                return text[fp_start:i+1]
        i += 1
    return None

sw2 = get_fp('SW2')
sw4 = get_fp('SW4')

print("SW2:")
for line in sw2.splitlines():
    if 'fp_poly' in line or 'layer "B.' in line or 'pts' in line:
        print("  ", line[:80])

print("\nSW4:")
for line in sw4.splitlines():
    if 'fp_poly' in line or 'layer "B.' in line or 'pts' in line:
        print("  ", line[:80])
