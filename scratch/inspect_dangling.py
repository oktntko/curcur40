import pcbnew

def inspect_track(board, x_mm, y_mm, layer_name):
    target = pcbnew.VECTOR2I(int(x_mm * 1e6), int(y_mm * 1e6))
    for t in board.GetTracks():
        if t.GetLayerName() != layer_name:
            continue
        # check start, end, or mid
        dist_start = (t.GetStart() - target).EuclideanNorm()
        dist_end = (t.GetEnd() - target).EuclideanNorm()
        dist_mid = (t.GetMidPoint() - target).EuclideanNorm() if hasattr(t, 'GetMidPoint') else 999999999
        if dist_start < 2000000 or dist_end < 2000000 or dist_mid < 2000000:
            print(f"Track on {t.GetLayerName()} net={t.GetNetname()} len={t.GetLength()/1e6:.4f}mm: start={t.GetStart().x/1e6:.4f},{t.GetStart().y/1e6:.4f} end={t.GetEnd().x/1e6:.4f},{t.GetEnd().y/1e6:.4f}")

print("=== LEFT BOARD ===")
b_left = pcbnew.LoadBoard('pcbs/curcur40/left/curcur40-left.kicad_pcb')
inspect_track(b_left, -29.1148, 25.9602, "B.Cu")
inspect_track(b_left, -6.5425, 38.6200, "F.Cu")
inspect_track(b_left, -39.2360, 41.2400, "F.Cu")
inspect_track(b_left, -24.8320, 30.5960, "F.Cu")
inspect_track(b_left, -117.8625, -14.3688, "F.Cu")
inspect_track(b_left, -115.6225, 24.4413, "B.Cu")
inspect_track(b_left, -114.5425, 4.9688, "B.Cu")
inspect_track(b_left, -112.9191, -11.7629, "F.Cu")

print("\n=== RIGHT BOARD ===")
b_right = pcbnew.LoadBoard('pcbs/curcur40/right/curcur40-right.kicad_pcb')
inspect_track(b_right, 0.5000, 39.8000, "F.Cu")
