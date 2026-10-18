# Let's inspect Left PCB tracks around J2 +5V
with open('pcbs/curcur40/left/curcur40-left.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# 1. On F.Cu: track 65f1e2cd-90da-4f7c-a910-9d559ae83bf1
# Change start from -6.5425 to the via (-8.5000 38.6200)
# (start -6.5425 38.54625) -> (start -8.5 38.62)
text = text.replace('(start -6.5425 38.54625)', '(start -8.5 38.62)')

# 2. On F.Cu: track c8a9f606-30ad-4058-8bb4-353dffd90861
# Change end from -6.5425 to the via (-8.5000 30.5960)
# (end -6.5425 30.74625) -> (end -8.5 30.596)
text = text.replace('(end -6.5425 30.74625)', '(end -8.5 30.596)')

# 3. On B.Cu: connect from via (-8.5 38.62) to J2 pad T (-6.5425 38.54625)
# Find segment on B.Cu with start -8.5 38.62 and end -6.5425 38.62
text = text.replace('(end -6.5425 38.62)', '(end -6.5425 38.54625)')

# 4. On B.Cu: connect from via (-8.5 30.596) to J2 pad T (-6.5425 30.74625)
# Find segment on B.Cu with start -8.5 30.596 and end -6.5425 30.596
text = text.replace('(end -6.5425 30.596)', '(end -6.5425 30.74625)')

with open('pcbs/curcur40/left/curcur40-left.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated J2 +5V tracks cleanly.")
