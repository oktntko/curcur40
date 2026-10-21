import re
from pathlib import Path

rpt = Path("scratch/drc_current.rpt").read_text(encoding="utf-8")
types = set(re.findall(r'\[([^\]]+)\]:', rpt))
print("Violation types in drc_current.rpt:")
for t in sorted(types):
    cnt = len(re.findall(rf'\[{re.escape(t)}\]:', rpt))
    print(f"  [{t}]: {cnt}")

print("\nUnconnected items sample:")
unconn_pos = rpt.find("** Unconnected items")
if unconn_pos != -1:
    print(rpt[unconn_pos:unconn_pos+1000])
