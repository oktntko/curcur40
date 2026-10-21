import re
from pathlib import Path

sch = Path("pcbs/curcur40/right/curcur40-right.kicad_sch").read_text(encoding="utf-8")
pwr_refs = re.findall(r'\(property\s+"Reference"\s+"(#PWR\d+)"', sch)
nums = [int(r.replace("#PWR", "").lstrip("0") or "0") for r in pwr_refs]
print(f"Max #PWR number: {max(nums) if nums else 0}")
print(f"Total #PWR symbols: {len(pwr_refs)}")
