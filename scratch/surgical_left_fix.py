import re

with open('pcbs/curcur40/left/curcur40-left.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

stubs_to_remove = {
    '457b7e8e-3d1c-4e6d-b480-feee933d49d7',
    'cd2b8868-0e90-480c-bfff-4afa63930c20',
    '8ab20a03-8668-4212-8c55-9e79ce186662',
    'f6253545-e5d1-41ec-a578-0aa082be40cc',
    'da23cc49-8906-4d2d-9067-57922964cf24'
}

new_text = text
# Remove stubs
for u in stubs_to_remove:
    pattern = re.compile(rf'\t\(segment\b[^\n]*\n\t\t\(start [^\n]+\n\t\t\(end [^\n]+\n\t\t\(width [^\n]+\n\t\t\(layer [^\n]+\n\t\t\(net [^\n]+\n\t\t\(uuid \"{u}\"\)\n\t\)\n', re.MULTILINE)
    match = pattern.search(new_text)
    if match:
        new_text = pattern.sub('', new_text)
        print(f"Removed stub {u}")
    else:
        pattern2 = re.compile(rf'\t\(segment\b.*?\buuid \"{u}\"\)\n\t\)\n', re.DOTALL)
        new_text = pattern2.sub('', new_text)
        print(f"Removed stub (alt) {u}")

# 1. Update 65f1e2cd-90da-4f7c-a910-9d559ae83bf1: start (-6.5425 38.62) -> (-6.5425 38.54625)
p1 = re.compile(r'(\(segment\n\t\t\(start -6\.5425 )38\.62(\)\n\t\t\(end -24\.762 38\.62\)\n\t\t\(width [^\n]+\)\n\t\t\(layer \"F\.Cu\"\)\n\t\t\(net \d+\)\n\t\t\(uuid \"65f1e2cd-90da-4f7c-a910-9d559ae83bf1\"\)\n\t\))')
new_text, c1 = p1.subn(r'\g<1>38.54625\2', new_text)
print(f"Updated +5V_1: {c1}")

# 2. Update c8a9f606-30ad-4058-8bb4-353dffd90861: end (-6.5425 30.596) -> (-6.5425 30.74625)
p2 = re.compile(r'(\(segment\n\t\t\(start -24\.832 30\.596\)\n\t\t\(end -6\.5425 )30\.596(\)\n\t\t\(width [^\n]+\)\n\t\t\(layer \"F\.Cu\"\)\n\t\t\(net \d+\)\n\t\t\(uuid \"c8a9f606-30ad-4058-8bb4-353dffd90861\"\)\n\t\))')
new_text, c2 = p2.subn(r'\g<1>30.74625\2', new_text)
print(f"Updated +5V_3: {c2}")

# 3. Update 7948b160-acc5-4b1d-9d8b-e5b1c2f6d66b: end (-39.9125 41.24) -> (-39.9175 41.245)
p3 = re.compile(r'(\(segment\n\t\t\(start -39\.236 41\.24\)\n\t\t\(end )-39\.9125 41\.24(\)\n\t\t\(width [^\n]+\)\n\t\t\(layer \"F\.Cu\"\)\n\t\t\(net \d+\)\n\t\t\(uuid \"7948b160-acc5-4b1d-9d8b-e5b1c2f6d66b\"\)\n\t\))')
new_text, c3 = p3.subn(r'\g<1>-39.9175 41.245\2', new_text)
print(f"Updated +5V_2: {c3}")

with open('pcbs/curcur40/left/curcur40-left.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(new_text)

print("Updated pcbs/curcur40/left/curcur40-left.kicad_pcb cleanly.")
