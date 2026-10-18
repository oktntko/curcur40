import pcbnew

b = pcbnew.LoadBoard('scratch/head_pmw3360.kicad_pcb')
for fp in sorted(b.GetFootprints(), key=lambda f: f.GetReference()):
    ref = fp.GetReference()
    val = fp.GetValue()
    pos = fp.GetPosition()
    rot = fp.GetOrientationDegrees()
    print(f"FP {ref} ({val}) pos=({pos.x/1e6:.3f}, {pos.y/1e6:.3f}) rot={rot}:")
    for p in sorted(fp.Pads(), key=lambda p: p.GetName()):
        pp = p.GetPosition()
        print(f"  Pad {p.GetName()} ({p.GetNetname()}) at ({pp.x/1e6:.3f}, {pp.y/1e6:.3f})")
