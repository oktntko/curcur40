import re
import sys

pcb_path = 'pcbs/curcur40/left/curcur40-left.kicad_pcb'

with open(pcb_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Helper to find and update footprints
pattern = re.compile(r'(\t\(footprint \"[^\"]+\"\n.*?\n\t\))', re.DOTALL)

sw_poly_updated = 0
sw_ref_updated = 0
led_poly_updated = 0
led_ref_updated = 0
smdsw_ref_updated = 0

def repl(match):
    global sw_poly_updated, sw_ref_updated, led_poly_updated, led_ref_updated, smdsw_ref_updated
    fp = match.group(1)
    
    ref_m = re.search(r'\(property \"Reference\" \"([^\"]+)\"', fp)
    if not ref_m:
        return fp
    ref = ref_m.group(1)
    
    # 1. Switches: SW*, EXSW*
    if ref.startswith('SW') or ref.startswith('EXSW'):
        # Check fp_poly on B.Fab
        if '(layer "B.Fab")' in fp and 'fp_poly' in fp:
            new_fp, count = re.subn(
                r'(\(fp_poly\b.*?\blayer )\"B\.Fab\"',
                r'\1"B.SilkS"',
                fp,
                flags=re.DOTALL
            )
            if count > 0:
                sw_poly_updated += count
                fp = new_fp
        # Check Reference on B.Fab
        new_fp, count = re.subn(
            rf'(\(property \"Reference\" \"{re.escape(ref)}\"[^\n]*\n\t\t\t\(at [^\n]+\)\n\t\t\t\(layer )\"B\.Fab\"',
            r'\1"B.SilkS"',
            fp
        )
        if count > 0:
            sw_ref_updated += count
            fp = new_fp

    # 2. LEDs: LED*, EXLED*
    elif ref.startswith('LED') or ref.startswith('EXLED'):
        if '(layer "B.Fab")' in fp and 'fp_poly' in fp:
            new_fp, count = re.subn(
                r'(\(fp_poly\b.*?\blayer )\"B\.Fab\"',
                r'\1"B.SilkS"',
                fp,
                flags=re.DOTALL
            )
            if count > 0:
                led_poly_updated += count
                fp = new_fp
        new_fp, count = re.subn(
            rf'(\(property \"Reference\" \"{re.escape(ref)}\"[^\n]*\n\t\t\t\(at [^\n]+\)\n\t\t\t\(layer )\"B\.Fab\"',
            r'\1"B.SilkS"',
            fp
        )
        if count > 0:
            led_ref_updated += count
            fp = new_fp

    # 3. SMDSW: SMDSW1, SMDSW2
    elif ref.startswith('SMDSW'):
        new_fp, count = re.subn(
            rf'(\(property \"Reference\" \"{re.escape(ref)}\"[^\n]*\n\t\t\t\(at [^\n]+\)\n\t\t\t\(layer )\"B\.Fab\"',
            r'\1"B.SilkS"',
            fp
        )
        if count > 0:
            smdsw_ref_updated += count
            fp = new_fp

    return fp

new_text = pattern.sub(repl, text)

print(f'SW poly updated: {sw_poly_updated}')
print(f'SW ref updated: {sw_ref_updated}')
print(f'LED poly updated: {led_poly_updated}')
print(f'LED ref updated: {led_ref_updated}')
print(f'SMDSW ref updated: {smdsw_ref_updated}')

with open(pcb_path, 'w', encoding='utf-8') as f:
    f.write(new_text)

print('Updated pcbs/curcur40/left/curcur40-left.kicad_pcb successfully.')
