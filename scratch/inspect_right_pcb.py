# -*- coding: utf-8 -*-
import pcbnew

board = pcbnew.LoadBoard(r"c:\Users\oktnt\workspace\curcur40\pcbs\curcur40\right\curcur40-right.kicad_pcb")
cx, cy = 7.525, 52.3875

print("=== TRACKS & VIAS NEAR BOTTOM TRACKBALL AREA ===")
for item in board.GetTracks():
    s = item.GetStart()
    e = item.GetEnd()
    sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
    ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)
    
    if (-6.0 <= sx <= 26.0 or -6.0 <= ex <= 26.0) and (sy >= 55.0 or ey >= 55.0):
        net_name = item.GetNetname()
        if item.GetClass() == "PCB_VIA":
            print(f"VIA: {net_name} at ({sx:.3f}, {sy:.3f})")
        else:
            layer = board.GetLayerName(item.GetLayer())
            w = pcbnew.ToMM(item.GetWidth())
            print(f"TRACK: {net_name} [{layer}] ({sx:.3f}, {sy:.3f}) -> ({ex:.3f}, {ey:.3f}) w={w:.3f}")

print("\n=== ZONES ===")
for zone in board.Zones():
    print(f"ZONE: net={zone.GetNetname()} layer={board.GetLayerName(zone.GetLayer())}")

print("\n=== FOOTPRINTS NEAR TRACKBALL ===")
for fp in board.GetFootprints():
    pos = fp.GetPosition()
    px, py = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
    if -8.0 <= px <= 25.0 and 30.0 <= py <= 70.0:
        print(f"FP: {fp.GetReference()} '{fp.GetValue()}' at ({px:.3f}, {py:.3f}) rot={fp.GetOrientationDegrees()}")
