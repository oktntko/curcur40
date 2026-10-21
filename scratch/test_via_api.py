import pcbnew

board = pcbnew.LoadBoard("pcbs/curcur40/right/curcur40-right.kicad_pcb")

v = pcbnew.PCB_VIA(board)
v.SetPosition(pcbnew.VECTOR2I_MM(10, 10))
v.SetWidth(pcbnew.FromMM(0.6))
v.SetDrill(pcbnew.FromMM(0.3))
v.SetNet(board.FindNet("GNDR"))
print("Created via successfully, pos:", v.GetPosition())
