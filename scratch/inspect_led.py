import pcbnew

b = pcbnew.LoadBoard('pcbs/curcur40/left/curcur40-left.kicad_pcb')
fp = b.FindFootprintByReference('LED1')
print("LED1 items:")
for g in fp.GraphicalItems():
    print(f"  {g.GetClass()} on {g.GetLayerName()}")
