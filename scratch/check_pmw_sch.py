import subprocess
import re

txt = subprocess.check_output(["git", "show", "f54d205e~1:pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_sch"], encoding="utf-8")

# find all labels
for m in re.finditer(r'\(label "(.*?)"\s+\(at ([\d\.\-]+) ([\d\.\-]+)', txt):
    print(f"Label: {m.group(1)} at ({m.group(2)}, {m.group(3)})")

# find symbol U1
m_u1 = re.search(r'\(property "Reference" "U1".*?\(at ([\d\.\-]+) ([\d\.\-]+)', txt, re.DOTALL)
if m_u1:
    print(f"U1 at ({m_u1.group(1)}, {m_u1.group(2)})")
