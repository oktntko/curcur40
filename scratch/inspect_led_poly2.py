import pcbnew

b = pcbnew.LoadBoard('pcbs/curcur40/left/curcur40-left.kicad_pcb')
led = b.FindFootprintByReference('LED1')
pad3 = led.FindPadByNumber('3')
pos = pad3.GetPosition()
lpos = led.GetPosition()
print("LED1 center:", pcbnew.ToMM(lpos.x), pcbnew.ToMM(lpos.y))
print("Pad 3 pos:", pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y))
for g in led.GraphicalItems():
    if g.GetLayerName() == "B.SilkS":
        sh = g.Cast()
        print("B.SilkS shape:", sh.GetShapeStr())
        poly = sh.GetPolyShape()
        pts = [(pcbnew.ToMM(poly.CPoint(i).x), pcbnew.ToMM(poly.CPoint(i).y)) for i in range(poly.FullPointCount())]
        print("Global pts:", pts)
