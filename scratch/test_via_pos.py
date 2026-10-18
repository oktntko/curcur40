import pcbnew

b = pcbnew.LoadBoard('scratch/test_left_orig.kicad_pcb')

def check_pos(name, x, y, r=0.8):
    print(f"--- Checking {name} at ({x:.2f}, {y:.2f}) r={r}mm ---")
    conflict = False
    for t in b.GetTracks():
        if t.GetClass() == 'PCB_TRACK':
            s, e = t.GetStart(), t.GetEnd()
            sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
            ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)
            # check distance from point to segment
            # simplified: check bounding box with margin
            if (min(sx, ex) - r <= x <= max(sx, ex) + r) and (min(sy, ey) - r <= y <= max(sy, ey) + r):
                print(f"  Track [{t.GetNetname()}] on {t.GetLayerName()}: ({sx:.2f}, {sy:.2f}) -> ({ex:.2f}, {ey:.2f})")
                conflict = True
        elif t.GetClass() == 'PCB_VIA':
            pos = t.GetPosition()
            vx, vy = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
            d = ((vx - x)**2 + (vy - y)**2)**0.5
            if d < r + 0.5:
                print(f"  Via [{t.GetNetname()}] at ({vx:.2f}, {vy:.2f}) d={d:.2f}")
                conflict = True
    if not conflict:
        print("  CLEAN! No tracks or vias within range.")

check_pos("Left Via 1 (KEY16)", -103.5, 33.5)
check_pos("Left Via 2 (KEY17)", -102.5, 33.0)
check_pos("Right Via 1 (KEY16)", -85.5, 40.5)
check_pos("Right Via 2 (KEY17)", -84.5, 39.5)
