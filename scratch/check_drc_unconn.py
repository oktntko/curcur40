import re
from pathlib import Path

rpt = Path("scratch/drc_current.rpt").read_text(encoding="utf-8")
for line in rpt.splitlines():
    if "unconnected_items" in line or "未配線" in line:
        print(line[:120])
    elif "Symbol" in line or "Footprint" in line or "Pad" in line or "Track" in line or "Via" in line:
        if "unconnected" in line.lower() or "U1" in line or "U2" in line or "JP1" in line:
            print("  ", line.strip()[:120])
