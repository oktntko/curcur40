import subprocess

txt = subprocess.check_output(['git', 'show', 'f54d205e~1:pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_sch'], encoding='utf-8')

for line in txt.splitlines():
    if '66.04' in line or '81.28' in line:
        print(line)
