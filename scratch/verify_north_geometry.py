import pcbnew
import subprocess
import re

RIGHT_PCB = r"pcbs/curcur40/right/curcur40-right.kicad_pcb"
KICAD_CLI = r"C:\Users\oktnt\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe"

# Re-read fresh board from disk (or restore from git if needed)
# First let's check git status of right PCB
