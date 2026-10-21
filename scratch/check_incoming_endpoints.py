import pcbnew

board = pcbnew.LoadBoard("pcbs/curcur40/right/curcur40-right.kicad_pcb")

print("Incoming tracks at X = -0.725:")
for t in board.GetTracks():
    if not isinstance(t, pcbnew.PCB_VIA):
        st = t.GetStart()
        en = t.GetEnd()
        sx, sy = pcbnew.ToMM(st.x), pcbnew.ToMM(st.y)
        ex, ey = pcbnew.ToMM(en.x), pcbnew.ToMM(en.y)
        if abs(sx - (-0.725)) < 0.01 or abs(ex - (-0.725)) < 0.01:
            print(f"  {t.GetNetname():15} | ({sx:.4f}, {sy:.4f}) -> ({ex:.4f}, {ey:.4f}) layer={t.GetLayerName()}")
