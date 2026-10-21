with open('pcbs/curcur40/right/curcur40-right.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('25.4 -22.86')
if idx != -1:
    print(text[idx-100:idx+200])
else:
    print('Not found')
