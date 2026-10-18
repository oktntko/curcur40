def remove_segment_by_uuid(text, u):
    target = f'(uuid "{u}")'
    idx = text.find(target)
    if idx == -1:
        print(f"UUID {u} not found")
        return text
    seg_start = text.rfind('(segment', 0, idx)
    seg_end = text.find('\n\t)', idx)
    assert seg_start != -1 and seg_end != -1, f"Failed to delimit segment for {u}"
    end_pos = seg_end + len('\n\t)')
    if end_pos < len(text) and text[end_pos] == '\n':
        end_pos += 1
    start_pos = text.rfind('\n', 0, seg_start)
    if start_pos == -1:
        start_pos = seg_start
    else:
        start_pos += 1
    
    snippet = text[start_pos:end_pos]
    print(f"Removing snippet ({len(snippet)} chars):")
    for line in snippet.splitlines()[:3]:
        print("  ", line)
    return text[:start_pos] + text[end_pos:]

with open('pcbs/curcur40/left/curcur40-left.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

# Test on 457b7e8e-3d1c-4e6d-b480-feee933d49d7
t2 = remove_segment_by_uuid(text, '457b7e8e-3d1c-4e6d-b480-feee933d49d7')
print("Original len:", len(text), "New len:", len(t2), "Diff:", len(text) - len(t2))
