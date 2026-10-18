import pcbnew
import json
import subprocess

def snap_tracks_to_vias(pcb_path):
    board = pcbnew.LoadBoard(pcb_path)
    vias = [t for t in board.GetTracks() if t.GetClass() == 'PCB_VIA']
    tracks = [t for t in board.GetTracks() if t.GetClass() == 'PCB_TRACK']
    
    snapped = 0
    # Collect map of coordinates
    with open(pcb_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # In text file, let's find segments and vias
    # If a segment endpoint differs from a via by < 0.001mm (1000 nm), snap it textually!
    # Let's inspect each via
    for v in vias:
        v_pos = v.GetPosition()
        vx_str = f"{v_pos.x / 1e6:.6f}".rstrip('0').rstrip('.')
        vy_str = f"{v_pos.y / 1e6:.6f}".rstrip('0').rstrip('.')
        for t in tracks:
            # check start
            ds = (t.GetStart() - v_pos).EuclideanNorm()
            if 0 < ds < 1000: # between 1nm and 1000nm (0.001mm)
                snapped += 1
                t.SetStart(v_pos)
            de = (t.GetEnd() - v_pos).EuclideanNorm()
            if 0 < de < 1000:
                snapped += 1
                t.SetEnd(v_pos)

    print(f"{pcb_path}: snapped {snapped} endpoints")
    return snapped

snap_tracks_to_vias('pcbs/curcur40/left/curcur40-left.kicad_pcb')
snap_tracks_to_vias('pcbs/curcur40/right/curcur40-right.kicad_pcb')
