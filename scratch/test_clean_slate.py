import pcbnew

SRC_PCB = r"scratch/head_pmw3360.kicad_pcb"
board = pcbnew.LoadBoard(SRC_PCB)

for t in list(board.GetTracks()):
    board.Delete(t)
for z in list(board.Zones()):
    board.Delete(z)

print("Remaining tracks:", len(board.GetTracks()))
print("Remaining zones:", len(board.Zones()))
