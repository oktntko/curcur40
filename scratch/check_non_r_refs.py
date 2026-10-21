from pathlib import Path
import re

pcb = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")
refs = re.findall(r'\(property\s+"Reference"\s+"([^"]+)"', pcb)
print("Refs without 'r':", [r for r in refs if not r.startswith("r") and not r.startswith("#")])
