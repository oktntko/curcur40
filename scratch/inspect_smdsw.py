import pcbnew
b = pcbnew.LoadBoard('scratch/test_left_orig.kicad_pcb')
for ref in ['SMDSW1', 'SMDSW2']:
    fp = b.FindFootprintByReference(ref)
    print(f"FP {ref} at ({pcbnew.ToMM(fp.GetPosition().x):.3f}, {pcbnew.ToMM(fp.GetPosition().y):.3f})")
    for p in fp.Pads():
        pos = p.GetPosition()
        size = p.GetSize()
        print(f"  Pad {p.GetName()} at ({pcbnew.ToMM(pos.x):.3f}, {pcbnew.ToMM(pos.y):.3f}) size=({pcbnew.ToMM(size.x):.3f}, {pcbnew.ToMM(size.y):.3f}) layer={p.GetLayerSet().FmtHex()}")
