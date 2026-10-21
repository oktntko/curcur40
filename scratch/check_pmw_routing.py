from pathlib import Path
import re

pcb = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")

# Let's search for any segment having net "+1V8_PMW" or "V_{IN}" or "V_{IO}" or "LED_P" or "/RESET"
for n in ['+1V8_PMW', 'V_{IN}', 'V_{IO}', 'LED_P', '/RESET', '/MOTION', 'U2-NC']:
    found = re.findall(rf'\(segment[^\)]*\(net\s+\"[^\"]*{re.escape(n)}[^\"]*\"\)', pcb)
    print(f"Segments with net matching '{n}': {len(found)}")

# Also search without regex in entire file
for n in ['+1V8_PMW', 'V_{IN}', 'V_{IO}', 'LED_P', '/RESET', '/MOTION']:
    count = pcb.count(f'"{n}"')
    print(f"Total occurrences of '\"{n}\"' in pcb: {count}")
