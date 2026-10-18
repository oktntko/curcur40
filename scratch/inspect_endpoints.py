import pcbnew

board = pcbnew.LoadBoard('pcbs/curcur40/left/curcur40-left.kicad_pcb')

uuids = [
    ('GND', '457b7e8e-3d1c-4e6d-b480-feee933d49d7'),
    ('+5V_1', '65f1e2cd-90da-4f7c-a910-9d559ae83bf1'),
    ('+5V_2', '7948b160-acc5-4b1d-9d8b-e5b1c2f6d66b'),
    ('+5V_3', 'c8a9f606-30ad-4058-8bb4-353dffd90861'),
    ('D1-K_1', 'cd2b8868-0e90-480c-bfff-4afa63930c20'),
    ('D1-K_2', '8ab20a03-8668-4212-8c55-9e79ce186662'),
    ('D1-K_3', 'f6253545-e5d1-41ec-a578-0aa082be40cc'),
    ('EXLED1-DIN', 'da23cc49-8906-4d2d-9067-57922964cf24')
]

for label, u in uuids:
    track = None
    for t in board.GetTracks():
        if hasattr(t, 'm_Uuid') and str(t.m_Uuid.AsString()) == u:
            track = t
            break
    if not track:
        continue
    
    start = track.GetStart()
    end = track.GetEnd()
    print(f"\n=== {label} ({track.GetNetname()}, layer {track.GetLayerName()}) ===")
    print(f"  Start: ({start.x/1e6:.4f}, {start.y/1e6:.4f})")
    print(f"  End:   ({end.x/1e6:.4f}, {end.y/1e6:.4f})")
    print(f"  Length: {track.GetLength()/1e6:.4f} mm")
    
    # Check nearby pads at start
    for p in board.GetPads():
        d_s = (p.GetPosition() - start).EuclideanNorm() / 1e6
        d_e = (p.GetPosition() - end).EuclideanNorm() / 1e6
        fp = p.GetParentFootprint()
        ref = fp.GetReference() if fp else "None"
        if d_s < 1.0:
            print(f"  Nearby pad at Start: {ref} pin {p.GetNumber()} at dist {d_s:.4f}mm (net {p.GetNetname()})")
        if d_e < 1.0:
            print(f"  Nearby pad at End:   {ref} pin {p.GetNumber()} at dist {d_e:.4f}mm (net {p.GetNetname()})")

    # Check connecting tracks
    conn_start = 0
    conn_end = 0
    for other in board.GetTracks():
        if other == track:
            continue
        if (other.GetStart() - start).EuclideanNorm() < 1000 or (other.GetEnd() - start).EuclideanNorm() < 1000:
            conn_start += 1
        if (other.GetStart() - end).EuclideanNorm() < 1000 or (other.GetEnd() - end).EuclideanNorm() < 1000:
            conn_end += 1
    print(f"  Connected other tracks at Start: {conn_start}, at End: {conn_end}")
