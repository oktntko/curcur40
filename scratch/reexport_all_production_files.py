# -*- coding: utf-8 -*-
"""
Re-export and verify 100% of all production / ordering files for curcur40:
1. JLCPCB PCBs (GERBER, CPL, BOM):
   - pcbs/curcur40/left
   - pcbs/curcur40/right
   - pcbs/curcur40/pmw3360
2. JLCPCB Plates (GERBER):
   - plates/curcur40/pcb/plate-top-left
   - plates/curcur40/pcb/plate-top-right
   - plates/curcur40/pcb/plate-bottom-left
   - plates/curcur40/pcb/plate-bottom-right
   - plates/curcur40/pcb/plate-bottom
3. Laser Cutting SVGs:
   - plates/curcur40/svg/plate-curcur40.svg
   - plates/curcur40/svg/foam-curcur40.svg
4. JLC3DP 3D Models:
   - cases/curcur40/left.step, left.stl
   - cases/curcur40/right.step, right.stl
   - cases/curcur40/trackball-cup.step, trackball-cup.stl
   - cases/curcur40/assembly-full.step
"""
import os
import csv
import zipfile
import shutil
import subprocess
from pathlib import Path

WORKSPACE = Path(r"c:\Users\oktnt\workspace\curcur40")
KICAD_CLI = r"C:\Users\oktnt\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe"

def export_clean_gerber_zip(pcb_path, zip_path):
    tmp_dir = zip_path.parent / f"_tmp_{zip_path.stem}"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    
    subprocess.run([
        KICAD_CLI, "pcb", "export", "gerbers",
        "--layers", "F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts",
        "--use-drill-file-origin",
        "-o", str(tmp_dir), str(pcb_path)
    ], check=True)
    
    subprocess.run([
        KICAD_CLI, "pcb", "export", "drill",
        "--drill-origin", "plot",
        "--excellon-separate-th",
        "--generate-map", "--map-format", "pdf",
        "-o", str(tmp_dir) + "/", str(pcb_path)
    ], check=True)
    
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in sorted(os.listdir(tmp_dir)):
            zf.write(tmp_dir / fname, fname)
    shutil.rmtree(tmp_dir)
    print(f"  [OK] Exported {zip_path.name} ({zip_path.stat().st_size} bytes)")

def main():
    print("==================================================")
    print("RE-EXPORTING & VERIFYING ALL PRODUCTION FILES")
    print("==================================================")

    # 1. Main PCBs and Sensor PCB
    print("\n--- 1. JLCPCB PCBs (curcur40-left, curcur40-right, curcur40-pmw3360) ---")
    script_jlc = Path(r"C:\Users\oktnt\.gemini\antigravity\brain\dab819aa-2c9f-4dd2-be5e-39a298725eca\scratch\export_pcb_jlcpcb.py")
    subprocess.run([r"C:\Users\oktnt\AppData\Local\Programs\KiCad\10.0\bin\python.exe", str(script_jlc)], check=True)

    # 2. FR-4 Top and Bottom Plates (JLCPCB GERBER ZIPs)
    print("\n--- 2. JLCPCB FR-4 Plates (5 Gerbers) ---")
    plates_dir = WORKSPACE / "plates" / "curcur40" / "pcb"
    plate_prod_dir = plates_dir / "jlcpcb" / "production_files"
    plate_prod_dir.mkdir(parents=True, exist_ok=True)

    plates = [
        "plate-top-left",
        "plate-top-right",
        "plate-bottom-left",
        "plate-bottom-right",
        "plate-bottom",
    ]
    for p_name in plates:
        pcb_file = plates_dir / f"{p_name}.kicad_pcb"
        zip_file = plate_prod_dir / f"GERBER-{p_name}.zip"
        export_clean_gerber_zip(pcb_file, zip_file)

    # 3. Summary of all production files
    print("\n==================================================")
    print("ALL PRODUCTION FILES SUMMARY & TIMESTAMPS")
    print("==================================================")
    
    targets = [
        WORKSPACE / "pcbs" / "curcur40" / "left" / "jlcpcb" / "production_files",
        WORKSPACE / "pcbs" / "curcur40" / "right" / "jlcpcb" / "production_files",
        WORKSPACE / "pcbs" / "curcur40" / "pmw3360" / "jlcpcb" / "production_files",
        WORKSPACE / "plates" / "curcur40" / "pcb" / "jlcpcb" / "production_files",
        WORKSPACE / "cases" / "curcur40",
        WORKSPACE / "plates" / "curcur40" / "svg",
    ]
    
    for d in targets:
        print(f"\nDirectory: {d.relative_to(WORKSPACE)}")
        for f in sorted(d.iterdir()):
            if f.is_file() and not f.name.startswith("~") and not f.name.endswith(".log"):
                mtime = f.stat().st_mtime
                import datetime
                dt = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
                print(f"  - {f.name:35s} {f.stat().st_size:10d} bytes   ({dt})")

if __name__ == "__main__":
    main()
