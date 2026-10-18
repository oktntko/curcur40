import pcbnew

board = pcbnew.LoadBoard('pcbs/curcur40/left/curcur40-left.kicad_pcb')

# 1. Update +5V_1 to connect exactly to J2 pin T (x=-6.5425, y=38.54625)
# UUID: 65f1e2cd-90da-4f7c-a910-9d559ae83bf1
# Start: (-6.5425, 38.6200) -> (-6.5425, 38.54625)

# 2. Update +5V_3 to connect exactly to J2 pin T (x=-6.5425, y=30.74625)
# UUID: c8a9f606-30ad-4058-8bb4-353dffd90861
# End: (-6.5425, 30.5960) -> (-6.5425, 30.74625)

# 3. Update +5V_2 to connect to C6 pin 1 (x=-39.9175, y=41.2450)
# UUID: 7948b160-acc5-4b1d-9d8b-e5b1c2f6d66b

# 4. Remove orphan stubs:
# GND: 457b7e8e-3d1c-4e6d-b480-feee933d49d7
# D1-K_1: cd2b8868-0e90-480c-bfff-4afa63930c20
# D1-K_2: 8ab20a03-8668-4212-8c55-9e79ce186662
# D1-K_3: f6253545-e5d1-41ec-a578-0aa082be40cc
# EXLED1-DIN: da23cc49-8906-4d2d-9067-57922964cf24

stubs_to_remove = {
    '457b7e8e-3d1c-4e6d-b480-feee933d49d7',
    'cd2b8868-0e90-480c-bfff-4afa63930c20',
    '8ab20a03-8668-4212-8c55-9e79ce186662',
    'f6253545-e5d1-41ec-a578-0aa082be40cc',
    'da23cc49-8906-4d2d-9067-57922964cf24'
}

for t in list(board.GetTracks()):
    u = str(t.m_Uuid.AsString())
    if u in stubs_to_remove:
        board.Remove(t)
        print(f"Removed stub {u}")
    elif u == '65f1e2cd-90da-4f7c-a910-9d559ae83bf1':
        # connect to J2 pin T
        t.SetStart(pcbnew.VECTOR2I(int(-6.5425 * 1e6), int(38.54625 * 1e6)))
        print("Updated +5V_1 to J2 pin T")
    elif u == 'c8a9f606-30ad-4058-8bb4-353dffd90861':
        # connect to J2 pin T
        t.SetEnd(pcbnew.VECTOR2I(int(-6.5425 * 1e6), int(30.74625 * 1e6)))
        print("Updated +5V_3 to J2 pin T")
    elif u == '7948b160-acc5-4b1d-9d8b-e5b1c2f6d66b':
        t.SetEnd(pcbnew.VECTOR2I(int(-39.9175 * 1e6), int(41.2450 * 1e6)))
        print("Updated +5V_2 to C6 pin 1")

board.Save('pcbs/curcur40/left/curcur40-left.kicad_pcb')
print("Saved left board successfully.")
