import json
import subprocess

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
    return text[:start_pos] + text[end_pos:]

# 1. LEFT PCB
with open('pcbs/curcur40/left/curcur40-left.kicad_pcb', 'r', encoding='utf-8') as f:
    left_text = f.read()

left_stubs = [
    '457b7e8e-3d1c-4e6d-b480-feee933d49d7',
    'cd2b8868-0e90-480c-bfff-4afa63930c20',
    '8ab20a03-8668-4212-8c55-9e79ce186662',
    'f6253545-e5d1-41ec-a578-0aa082be40cc',
    'da23cc49-8906-4d2d-9067-57922964cf24',
    '7948b160-acc5-4b1d-9d8b-e5b1c2f6d66b'
]
for u in left_stubs:
    left_text = remove_segment_by_uuid(left_text, u)

# Reconnect seg1 start to J2 pin T (y=38.54625)
# Find exact block for 65f1e2cd-90da-4f7c-a910-9d559ae83bf1
idx1 = left_text.find('65f1e2cd-90da-4f7c-a910-9d559ae83bf1')
if idx1 != -1:
    s1_start = left_text.rfind('(segment', 0, idx1)
    s1_end = left_text.find('\n\t)', idx1) + len('\n\t)')
    old_s1 = left_text[s1_start:s1_end]
    new_s1 = old_s1.replace('(start -6.5425 38.62)', '(start -6.5425 38.54625)')
    left_text = left_text[:s1_start] + new_s1 + left_text[s1_end:]
    print("Reconnected seg1 on Left PCB")

# Reconnect seg2 end to J2 pin T (y=30.74625)
idx2 = left_text.find('c8a9f606-30ad-4058-8bb4-353dffd90861')
if idx2 != -1:
    s2_start = left_text.rfind('(segment', 0, idx2)
    s2_end = left_text.find('\n\t)', idx2) + len('\n\t)')
    old_s2 = left_text[s2_start:s2_end]
    new_s2 = old_s2.replace('(end -6.5425 30.596)', '(end -6.5425 30.74625)')
    left_text = left_text[:s2_start] + new_s2 + left_text[s2_end:]
    print("Reconnected seg2 on Left PCB")

with open('pcbs/curcur40/left/curcur40-left.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(left_text)

# 2. RIGHT PCB
with open('pcbs/curcur40/right/curcur40-right.kicad_pcb', 'r', encoding='utf-8') as f:
    right_text = f.read()

right_text = remove_segment_by_uuid(right_text, 'f1739e41-80b3-4b66-9e9b-95efcace4f59')
print("Removed NCS stub on Right PCB")

with open('pcbs/curcur40/right/curcur40-right.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(right_text)

print("Running DRC on Left and Right PCBs...")
for name, pcb in [('Left', 'pcbs/curcur40/left/curcur40-left.kicad_pcb'), ('Right', 'pcbs/curcur40/right/curcur40-right.kicad_pcb')]:
    cmd = [
        r'C:\Users\oktnt\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe',
        'pcb', 'drc',
        '--severity-all',
        '--format', 'json',
        '-o', f'scratch/{name}_drc_clean.json',
        pcb
    ]
    subprocess.run(cmd, check=True)
    with open(f'scratch/{name}_drc_clean.json', 'r', encoding='utf-8') as f:
        d = json.load(f)
    print(f"=== {name} PCB ===")
    print("  Unconnected items:", len(d.get('unconnected_items', [])))
    dangling = [v for v in d.get('violations', []) if v.get('type') == 'track_dangling']
    print("  Dangling tracks:", len(dangling))
