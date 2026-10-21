from pathlib import Path
import re

pmw_pcb = Path("pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pcb").read_text(encoding="utf-8")
segs = re.findall(r'\(segment\s', pmw_pcb)
vias = re.findall(r'\(via\s', pmw_pcb)
print(f"curcur40-pmw3360.kicad_pcb: {len(segs)} segments, {len(vias)} vias")

for n in ['+1V8_PMW', 'V_{IN}', 'V_{IO}', 'LED_P', '/RESET', '/MOTION']:
    print(f"  pmw3360 pcb has '{n}': {pmw_pcb.count(f'\"{n}\"')}")
