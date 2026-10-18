with open('pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('property "Reference" "H1"')
if idx != -1:
    start = text.rfind('(symbol', 0, idx)
    print(text[start:start+700])
