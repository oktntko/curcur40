with open('pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('property "Reference" "H1"')
start = text.rfind('(symbol', 0, idx)
end = text.find('\n\t)', idx) + len('\n\t)')
print(text[start:end])
