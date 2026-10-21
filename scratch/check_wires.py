import subprocess

txt = subprocess.check_output(['git', 'show', 'f54d205e~1:pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_sch'], encoding='utf-8')

lines = txt.splitlines()
for i, l in enumerate(lines):
    if 'RESET' in l or 'label "CS"' in l:
        for j in range(max(0, i-5), min(len(lines), i+6)):
            print(f"{j}: {lines[j]}")
        print("---")
