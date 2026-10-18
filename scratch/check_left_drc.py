import pcbnew
import subprocess

LEFT_PCB = r"pcbs/curcur40/left/curcur40-left.kicad_pcb"
KICAD_CLI = r"C:\Users\oktnt\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe"

board = pcbnew.LoadBoard(LEFT_PCB)

# 1. Inspect DRC violations in left PCB
rpt_before = r"scratch/drc_left_before.rpt"
subprocess.run([KICAD_CLI, "pcb", "drc", "-o", rpt_before, LEFT_PCB], check=True)
with open(rpt_before, "r", encoding="utf-8") as f:
    print(f.read())
