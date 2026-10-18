import json
import re
import shutil
import subprocess

# Read original left pcb
with open('pcbs/curcur40/left/curcur40-left.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

# We want to restore:
# 1. In all switches (SW*, EXSW*), any fp_poly on "B.Fab" -> "B.SilkS"
# 2. In all switches (SW*, EXSW*), Reference on "B.Fab" -> "B.SilkS"
# 3. In all LEDs (LED*, EXLED*), any fp_poly on "B.Fab" -> "B.SilkS"
# 4. In all LEDs (LED*, EXLED*), Reference on "B.Fab" -> "B.SilkS"

# Let's write a helper to replace within footprints
def replace_in_footprints(content, prefix, change_poly=True, change_ref=True):
    # Find each footprint block
    # Pattern: \t(footprint "..." ... \n\t)
    pattern = re.compile(r'(\t\(footprint \"[^\"]+\"\n.*?\n\t\))', re.DOTALL)
    
    def fp_repl(match):
        fp = match.group(1)
        # Check reference
        ref_m = re.search(r'\(property \"Reference\" \"([^\"]+)\"', fp)
        if not ref_m:
            return fp
        ref_name = ref_m.group(1)
        if not any(ref_name.startswith(p) for p in prefix):
            return fp
        
        # Modify fp_poly
        if change_poly:
            # Change fp_poly layer "B.Fab" to "B.SilkS"
            fp = re.sub(
                r'(\(fp_poly\b.*?\blayer )\"B\.Fab\"',
                r'\1"B.SilkS"',
                fp,
                flags=re.DOTALL
            )
        # Modify reference layer
        if change_ref:
            fp = re.sub(
                rf'(\(property \"Reference\" \"{re.escape(ref_name)}\"[^\n]*\n\t\t\t\(at [^\n]+\)\n\t\t\t\(layer )\"B\.Fab\"',
                r'\1"B.SilkS"',
                fp
            )
        return fp

    return pattern.sub(fp_repl, content)

new_text = replace_in_footprints(text, ['SW', 'EXSW', 'SMDSW', 'LED', 'EXLED'])

# Also check SMD switches
with open('pcbs/curcur40/left/curcur40-left-fulltest.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(new_text)

shutil.copy('pcbs/curcur40/left/curcur40-left.kicad_pro', 'pcbs/curcur40/left/curcur40-left-fulltest.kicad_pro')

cmd = [
    r'C:\Users\oktnt\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe',
    'pcb', 'drc',
    '--severity-all',
    '--format', 'json',
    '-o', 'scratch/fulltest_drc.json',
    'pcbs/curcur40/left/curcur40-left-fulltest.kicad_pcb'
]
res = subprocess.run(cmd, capture_output=True, text=True)
print('DRC Output:', res.stdout)
if res.stderr:
    print('DRC Error:', res.stderr)

with open('scratch/fulltest_drc.json', 'r', encoding='utf-8') as f:
    drc = json.load(f)

print('Unconnected:', len(drc.get('unconnected_items', [])))
violations = drc.get('violations', [])
counts = {}
for v in violations:
    t = v.get('type', 'unknown')
    counts[t] = counts.get(t, 0) + 1

for t, c in sorted(counts.items(), key=lambda x: -x[1]):
    print(f'  {t}: {c}')
