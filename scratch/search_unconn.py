from pathlib import Path

rpt = Path("scratch/drc_after_sync.rpt").read_text(encoding="utf-8")
for i, line in enumerate(rpt.splitlines()):
    if "unconnected" in line.lower() or "未配線" in line.lower():
        print(f"Line {i+1}: {line}")
