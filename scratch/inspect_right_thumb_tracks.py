import pcbnew

b = pcbnew.LoadBoard('pcbs/curcur40/right/curcur40-right.kicad_pcb')
print('=== Right PCB Tracks near rLED1, rLED8, rLED9 ===')
for t in b.GetTracks():
    p1, p2 = t.GetStart(), t.GetEnd()
    x1, y1 = p1.x/1e6, p1.y/1e6
    x2, y2 = p2.x/1e6, p2.y/1e6
    if (25 <= x1 <= 78 or 25 <= x2 <= 78) and (46 <= y1 <= 53 or 46 <= y2 <= 53):
        t_type = "VIA" if t.GetClass() == "PCB_VIA" else "TRK"
        print(f"  {t_type} {t.GetNetname():15} {t.GetLayerName():5} ({x1:.3f}, {y1:.3f}) -> ({x2:.3f}, {y2:.3f})")
