with open('pcbs/curcur40/left/curcur40-left.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('property "Reference" "R4"')
print(text[idx:idx+250])
