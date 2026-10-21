import pcbnew

pcb = pcbnew.LoadBoard("scratch/pmw3360_pcb_b9043a22.kicad_pcb")
u1_p = pcb.FindFootprintByReference("U1").GetPosition()

print(f"{'Net':15} | {'Layer':6} | {'Start':18} | {'End':18}")
for t in pcb.GetTracks():
    if isinstance(t, pcbnew.PCB_VIA):
        pos = t.GetPosition()
        x, y = pcbnew.ToMM(pos.x - u1_p.x), pcbnew.ToMM(pos.y - u1_p.y)
        print(f"{t.GetNetname():15} | {'VIA':6} | ({x:7.3f}, {y:7.3f}) | drill={pcbnew.ToMM(t.GetDrill()):.2f}")
    else:
        st = t.GetStart()
        en = t.GetEnd()
        sx, sy = pcbnew.ToMM(st.x - u1_p.x), pcbnew.ToMM(st.y - u1_p.y)
        ex, ey = pcbnew.ToMM(en.x - u1_p.x), pcbnew.ToMM(en.y - u1_p.y)
        layer = "F.Cu" if t.GetLayer() == pcbnew.F_Cu else "B.Cu"
        print(f"{t.GetNetname():15} | {layer:6} | ({sx:7.3f}, {sy:7.3f}) -> ({ex:7.3f}, {ey:7.3f})")
