import re
from pathlib import Path

rpt = Path("scratch/drc_after_sync.rpt").read_text(encoding="utf-8")

unconn_section = rpt.split("** Unconnected items")[1].split("**")[0] if "** Unconnected items" in rpt else ""

items = []
current = []
for line in unconn_section.splitlines():
    if line.startswith("[unconnected_items]"):
        if current:
            items.append("\n".join(current))
            current = []
    if line.strip():
        current.append(line.strip())
if current:
    items.append("\n".join(current))

print(f"Total unconnected items: {len(items)}")
for i, it in enumerate(items):
    print(f"--- Item {i+1} ---")
    print(it)
