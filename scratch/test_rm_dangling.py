import re
import subprocess
import json

# Left board test
with open('pcbs/curcur40/left/curcur40-left.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

uuids_to_remove = [
    '457b7e8e-3d1c-4e6d-b480-feee933d49d7',
    '65f1e2cd-90da-4f7c-a910-9d559ae83bf1',
    '7948b160-acc5-4b1d-9d8b-e5b1c2f6d66b',
    'c8a9f606-30ad-4058-8bb4-353dffd90861',
    'cd2b8868-0e90-480c-bfff-4afa63930c20',
    '8ab20a03-8668-4212-8c55-9e79ce186662',
    'f6253545-e5d1-41ec-a578-0aa082be40cc',
    'da23cc49-8906-4d2d-9067-57922964cf24'
]

# Track s-expression pattern:
# \t(segment (start ...) (end ...) (width ...) (layer ...) (net ...) (tstamp|uuid "..."))
new_text = text
for u in uuids_to_remove:
    # Match segment containing uuid
    pattern = re.compile(rf'\t\(segment\b[^\n]*\n\t\t\(start [^\n]+\n\t\t\(end [^\n]+\n\t\t\(width [^\n]+\n\t\t\(layer [^\n]+\n\t\t\(net [^\n]+\n\t\t\(uuid \"{u}\"\)\n\t\)\n', re.MULTILINE)
    match = pattern.search(new_text)
    if match:
        new_text = pattern.sub('', new_text)
        print(f"Removed segment {u}")
    else:
        # try shorter pattern
        pattern2 = re.compile(rf'\t\(segment\b.*?\buuid \"{u}\"\)\n\t\)\n', re.DOTALL)
        if pattern2.search(new_text):
            new_text = pattern2.sub('', new_text)
            print(f"Removed segment (alt) {u}")
        else:
            print(f"Failed to find segment {u}")

with open('scratch/test_rm_dangling.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(new_text)

# Run DRC on test_rm_dangling.kicad_pcb using left.kicad_pro
import shutil
shutil.copy('pcbs/curcur40/left/curcur40-left.kicad_pro', 'scratch/test_rm_dangling.kicad_pro')

cmd = [
    r'C:\Users\oktnt\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe',
    'pcb', 'drc',
    '--severity-all',
    '--format', 'json',
    '-o', 'scratch/test_rm_dangling_drc.json',
    'scratch/test_rm_dangling.kicad_pcb'
]
subprocess.run(cmd, check=True)

with open('scratch/test_rm_dangling_drc.json', 'r', encoding='utf-8') as f:
    drc = json.load(f)

print("Unconnected items:", len(drc.get('unconnected_items', [])))
print("Dangling tracks:", len([v for v in drc.get('violations', []) if v.get('type') == 'track_dangling']))
print("Other violations:", len(drc.get('violations', [])))
