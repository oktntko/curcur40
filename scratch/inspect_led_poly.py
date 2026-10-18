import pcbnew

b = pcbnew.LoadBoard('pcbs/curcur40/left/curcur40-left.kicad_pcb')
fp = b.FindFootprintByReference('LED1')
for g in fp.GraphicalItems():
    if g.GetLayerName() == "B.Silkscreen":
        sh = g.Cast()
        print(f"Shape: {sh.GetShapeStr()}")
        poly = sh.GetPolyShape()
        print(f"Poly corners: {poly.PointCount()}")
        for i in range(poly.PointCount()):
            pt = poly.CPoint(i)
            print(f"   ({pcbnew.ToMM(pt.x):.3f}, {pcbnew.ToMM(pt.y):.3f})")
for p in fp.Pads():
    pos = p.GetPosition()
    print(f"Pad {p.GetName()} at ({pcbnew.ToMM(pos.x):.3f}, {pcbnew.ToMM(pos.y):.3f}) size=({pcbnew.ToMM(p.GetSize().x):.3f}, {pcbnew.ToMM(p.GetSize().y):.3f})")
