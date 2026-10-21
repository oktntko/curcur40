with open('pcbs/curcur40/right/curcur40-right.kicad_pcb', encoding='utf-8') as f:
    txt = f.read()

def show_fp(ref):
    idx = txt.find(f'"Reference" "{ref}"')
    if idx == -1: return
    start = txt.rfind('(footprint', 0, idx)
    depth = 0
    i = start
    while i < len(txt):
        if txt[i] == '(': depth += 1
        elif txt[i] == ')':
            depth -= 1
            if depth == 0:
                break
        i += 1
    print(f'=== {ref} ===')
    print(txt[start:i+1])

show_fp('JP1')
show_fp('U2')
