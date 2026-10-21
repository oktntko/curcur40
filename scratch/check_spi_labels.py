from pathlib import Path
import re

sch = Path("pcbs/curcur40/right/curcur40-right.kicad_sch").read_text(encoding="utf-8")

for name in ['SCLK', 'MOSI', 'MISO', 'NCS']:
    for m in re.finditer(rf'\(([a-zA-Z_]+)\s+\"{name}\"[^)]*\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', sch):
        print(f"  {m.group(1)} '{name}' at ({m.group(2)}, {m.group(3)})")
