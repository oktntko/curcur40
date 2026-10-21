import subprocess
import re
from pathlib import Path

# Run kicad-cli pcb drc if available
kicad_cli = r"C:\Program Files\KiCad\8.0\bin\kicad-cli.exe"
if not Path(kicad_cli).exists():
    kicad_cli = r"C:\Program Files\KiCad\7.0\bin\kicad-cli.exe"
print(f"KiCad CLI path: {kicad_cli} (exists: {Path(kicad_cli).exists()})")

def run_drc(pcb_path, rpt_path):
    if Path(kicad_cli).exists():
        res = subprocess.run([kicad_cli, "pcb", "drc", "--output", str(rpt_path), str(pcb_path)], capture_output=True, text=True)
        print(f"DRC for {pcb_path}: returncode {res.returncode}")
        if Path(rpt_path).exists():
            text = Path(rpt_path).read_text(encoding="utf-8")
            err_count = len(re.findall(r'\[error\]', text))
            warn_count = len(re.findall(r'\[warning\]', text))
            print(f"  Errors: {err_count}, Warnings: {warn_count}")
            # print error types
            errors = re.findall(r'\[error\]:\s+([^\n]+)', text)
            for e in errors[:10]:
                print(f"    Error: {e}")
            warnings = re.findall(r'\[warning\]:\s+([^\n]+)', text)
            types = {}
            for w in warnings:
                types[w.split(':')[0]] = types.get(w.split(':')[0], 0) + 1
            print(f"    Warning summary: {types}")

run_drc("pcbs/curcur40/left/curcur40-left.kicad_pcb", "scratch/drc_left_now.rpt")
run_drc("pcbs/curcur40/right/curcur40-right.kicad_pcb", "scratch/drc_right_now.rpt")
if Path("pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pcb").exists():
    run_drc("pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pcb", "scratch/drc_pmw_now.rpt")
