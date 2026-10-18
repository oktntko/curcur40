with open("pcbs/curcur40/left/curcur40-left.kicad_pcb", "r", encoding="utf-8") as f:
    text = f.read()

pos = text.find('"LED1"')
start = text.rfind('(footprint', 0, pos)
end = text.find('(footprint', pos)
print(text[start+800:start+2200])
