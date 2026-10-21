from pathlib import Path

rpt = Path("scratch/erc_after_sync3.rpt").read_text(encoding="utf-8")
for i, line in enumerate(rpt.splitlines()):
    if line.startswith("["):
        print(f"Line {i+1}: {line}")
