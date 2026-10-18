import re
import sys
from check_sw import get_fp

with open('pcbs/curcur40/left/curcur40-left.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

target_switches = ['SW4', 'SW9', 'SW5', 'SW13', 'SW11', 'SW14', 'SW8', 'SW12', 'SW17', 'EXSW3', 'SW1', 'SW7', 'EXSW2']

new_text = text
for ref in target_switches:
    fp_text = get_fp(ref)
    assert fp_text is not None, f'{ref} not found'
    new_fp = fp_text
    
    # 1. reference layer: (property "Reference" "{ref}"\n\t\t\t(at ...)\n\t\t\t(layer "B.Fab")
    new_fp = re.sub(
        rf'(\(property \"Reference\" \"{ref}\"[^\n]*\n\t\t\t\(at [^\n]+\)\n\t\t\t\(layer )\"B\.Fab\"',
        r'\1"B.SilkS"',
        new_fp
    )
    # 2. fp_poly layer
    poly_pattern = re.compile(r'(\(fp_poly\n\t\t\t\(pts.*?\n\t\t\t\)\n\t\t\t\(stroke\n\t\t\t\t\(width 0\.1\)\n\t\t\t\t\(type solid\)\n\t\t\t\)\n\t\t\t\(fill yes\)\n\t\t\t\(layer )\"B\.Fab\"', re.DOTALL)
    new_fp, count = poly_pattern.subn(r'\1"B.SilkS"', new_fp)
    if count == 0:
        print(f'Warning: fp_poly not matched in {ref}')
    
    new_text = new_text.replace(fp_text, new_fp)

with open('scratch/text_test.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(new_text)

print('Successfully written scratch/text_test.kicad_pcb')
