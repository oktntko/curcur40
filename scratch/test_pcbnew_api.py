import pcbnew

board = pcbnew.LoadBoard("pcbs/curcur40/right/curcur40-right.kicad_pcb")

# Check PCB_TRACK creation
t = pcbnew.PCB_TRACK(board)
t.SetStart(pcbnew.VECTOR2I_MM(0, 0))
t.SetEnd(pcbnew.VECTOR2I_MM(1, 1))
t.SetWidth(pcbnew.FromMM(0.25))
t.SetLayer(pcbnew.B_Cu)
net = board.FindNet("GNDR")
if net:
    t.SetNet(net)
print("Created track successfully, net:", t.GetNetname())
