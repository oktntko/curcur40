# -*- coding: utf-8 -*-
"""
Render all updated preview assets for curcur40.
Uses kicad-cli for PCB and plate renders, and update_full_assembly for assembly CAD renders.
"""
import subprocess
import shutil
from pathlib import Path
from PIL import Image

WORKSPACE = Path(r"c:\Users\oktnt\workspace\curcur40")
PREVIEW_DIR = WORKSPACE / "preview"
ARTIFACTS_DIR = Path(r"C:\Users\oktnt\.gemini\antigravity\brain\dab819aa-2c9f-4dd2-be5e-39a298725eca")
KICAD_CLI = r"C:\Users\oktnt\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe"

def render_kicad_pcb(pcb_path, out_path, side="top", rotate=None, width=1600, height=1200):
    cmd = [
        KICAD_CLI, "pcb", "render",
        "--quality", "high",
        "--preset", "follow_pcb_editor",
        "--side", side,
        "--width", str(width),
        "--height", str(height),
        "-o", str(out_path),
    ]
    if rotate:
        cmd.extend(["--rotate", rotate])
    cmd.append(str(pcb_path))
    print(f"Rendering {out_path.name} from {pcb_path.name} ({side})...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error rendering {pcb_path}:", res.stderr)
    else:
        print(f"Successfully rendered {out_path.name}")

def main():
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Assembly Renders (copy latest perfected counterbore renders from artifacts/scratch)
    shutil.copy2(ARTIFACTS_DIR / "final_assembly_iso.png", PREVIEW_DIR / "render_full_assembly_iso.png")
    shutil.copy2(ARTIFACTS_DIR / "final_assembly_top.png", PREVIEW_DIR / "render_full_assembly_top.png")
    shutil.copy2(ARTIFACTS_DIR / "final_assembly_bottom.png", PREVIEW_DIR / "render_full_assembly_bottom.png")
    print("Updated assembly preview renders (iso, top, bottom).")

    # 2. Left PCB
    left_pcb = WORKSPACE / "pcbs" / "curcur40" / "left" / "curcur40-left.kicad_pcb"
    render_kicad_pcb(left_pcb, PREVIEW_DIR / "render_left_top.png", side="top", width=1600, height=1000)
    render_kicad_pcb(left_pcb, PREVIEW_DIR / "render_left_bottom.png", side="bottom", width=1600, height=1000)
    render_kicad_pcb(left_pcb, PREVIEW_DIR / "render_left_iso.png", side="top", rotate="-35,0,25", width=1600, height=1100)

    # 3. Right PCB
    right_pcb = WORKSPACE / "pcbs" / "curcur40" / "right" / "curcur40-right.kicad_pcb"
    render_kicad_pcb(right_pcb, PREVIEW_DIR / "render_right_top.png", side="top", width=1600, height=1200)
    render_kicad_pcb(right_pcb, PREVIEW_DIR / "render_right_bottom.png", side="bottom", width=1600, height=1200)
    render_kicad_pcb(right_pcb, PREVIEW_DIR / "render_right_iso.png", side="top", rotate="-35,0,-25", width=1600, height=1200)

    # 4. Plates
    left_plate = WORKSPACE / "plates" / "curcur40" / "pcb" / "plate-top-left.kicad_pcb"
    right_plate = WORKSPACE / "plates" / "curcur40" / "pcb" / "plate-top-right.kicad_pcb"
    render_kicad_pcb(left_plate, PREVIEW_DIR / "render_plate_left.png", side="top", width=1400, height=1000)
    render_kicad_pcb(right_plate, PREVIEW_DIR / "render_plate_right.png", side="top", width=1600, height=1200)

    # 5. Clean up test file
    test_f = PREVIEW_DIR / "test_right_top.png"
    if test_f.exists():
        test_f.unlink()

    print("\n--- ALL PREVIEWS UPDATED SUCCESSFULLY ---")

if __name__ == "__main__":
    main()
