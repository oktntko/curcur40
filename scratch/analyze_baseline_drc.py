from pathlib import Path
import re

rpt = Path("scratch/drc_current.rpt").read_text(encoding="utf-8")
errors = re.findall(r';\s*error', rpt, re.IGNORECASE)
warnings = re.findall(r';\s*warning', rpt, re.IGNORECASE)
print(f"In drc_current.rpt (BEFORE our changes): errors={len(errors)}, warnings={len(warnings)}")

types_err = {}
types_warn = {}
current_type = None
for line in rpt.splitlines():
    m = re.match(r'\[([^\]]+)\]:', line)
    if m:
        current_type = m.group(1)
    if '; error' in line:
        types_err[current_type] = types_err.get(current_type, 0) + 1
    elif '; warning' in line:
        types_warn[current_type] = types_warn.get(current_type, 0) + 1

print("\nErrors by type:")
for k, v in types_err.items():
    print(f"  [{k}]: {v}")

print("\nWarnings by type:")
for k, v in types_warn.items():
    print(f"  [{k}]: {v}")
