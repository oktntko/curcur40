import re
from pathlib import Path

rpt = Path("scratch/drc_after_routing.rpt").read_text(encoding="utf-8")

# Check unconnected items
unconn_pos = rpt.find("** Found")
print("Unconnected section:")
if unconn_pos != -1:
    print(rpt[unconn_pos:])

# Breakdown of violations
types = {}
for line in rpt.splitlines():
    m = re.match(r'\[([^\]]+)\]:', line)
    if m:
        t = m.group(1)
        types[t] = types.get(t, 0) + 1

print("\nViolations by type:")
for t, cnt in sorted(types.items()):
    print(f"  [{t}]: {cnt}")
