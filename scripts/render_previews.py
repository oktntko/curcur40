# -*- coding: utf-8 -*-
"""
Render all 3D preview images for curcur40 into docs/assets/:
- Full Assembly (ISO, Top, Bottom) from cases/assembly-full.step via cadgen
- Left & Right Main PCBs (Top, Bottom, ISO) via kicad-cli pcb render
- Left & Right Top Plates via kicad-cli pcb render
"""
import os
import subprocess
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
ASSETS_DIR = WORKSPACE / "docs" / "assets"
KICAD_CLI = Path(os.path.expandvars(r"%LOCALAPPDATA%\Programs\KiCad\10.0\bin\kicad-cli.exe"))
UVX_EXE = Path(os.path.expandvars(r"%USERPROFILE%\.local\bin\uvx.exe"))


def render_kicad_pcb(pcb_path: Path, out_path: Path, side="top", rotate=None, width=1600, height=1200):
    cmd = [
        str(KICAD_CLI),
        "pcb",
        "render",
        "--quality",
        "high",
        "--preset",
        "follow_pcb_editor",
        "--side",
        side,
        "--width",
        str(width),
        "--height",
        str(height),
        "-o",
        str(out_path),
    ]
    if rotate:
        cmd.extend(["--rotate", rotate])
    cmd.append(str(pcb_path))
    print(f"Rendering {out_path.name} from {pcb_path.name} ({side})...")
    subprocess.run(cmd, check=True)


def render_assembly_step():
    step_jobs = [
        (WORKSPACE / "cases" / "assembly-full.step", "iso", ASSETS_DIR / "render_full_assembly_iso.png", 1600, 1000),
        (WORKSPACE / "cases" / "assembly-full.step", "top", ASSETS_DIR / "render_full_assembly_top.png", 1600, 1000),
        (WORKSPACE / "cases" / "assembly-full.step", "bottom", ASSETS_DIR / "render_full_assembly_bottom.png", 1600, 1000),
        (WORKSPACE / "cases" / "trackball-cup.step", "iso", ASSETS_DIR / "trackball_cup_render.png", 1200, 1000),
        (WORKSPACE / "cases" / "trackball-cup-with-ball.step", "iso", ASSETS_DIR / "trackball_cup_with_ball_render.png", 1200, 1000),
    ]
    for step_path, view_name, out_path, w, h in step_jobs:
        print(f"Rendering {out_path.name} from {step_path.name} ({view_name})...")
        subprocess.run(
            [
                str(UVX_EXE),
                "--no-config",
                "--managed-python",
                "--python",
                "3.13",
                "--from",
                "cadgen==0.7.21",
                "cadgen",
                "step",
                "snapshot",
                str(step_path),
                str(out_path),
                "--camera",
                view_name,
                "--width",
                str(w),
                "--height",
                str(h),
            ],
            check=True,
        )


def main():
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Full Assembly STEP Renders
    render_assembly_step()

    # 2. Left Main PCB Renders
    left_pcb = WORKSPACE / "pcbs" / "left" / "curcur40-left.kicad_pcb"
    render_kicad_pcb(left_pcb, ASSETS_DIR / "render_left_top.png", side="top", width=1600, height=1000)
    render_kicad_pcb(left_pcb, ASSETS_DIR / "render_left_bottom.png", side="bottom", width=1600, height=1000)
    render_kicad_pcb(
        left_pcb, ASSETS_DIR / "render_left_iso.png", side="top", rotate="-35,0,25", width=1600, height=1100
    )

    # 3. Right Main PCB Renders
    right_pcb = WORKSPACE / "pcbs" / "right" / "curcur40-right.kicad_pcb"
    render_kicad_pcb(right_pcb, ASSETS_DIR / "render_right_top.png", side="top", width=1600, height=1200)
    render_kicad_pcb(right_pcb, ASSETS_DIR / "render_right_bottom.png", side="bottom", width=1600, height=1200)
    render_kicad_pcb(
        right_pcb, ASSETS_DIR / "render_right_iso.png", side="top", rotate="-35,0,-25", width=1600, height=1200
    )

    # 3b. PMW3360 Sensor Sub-PCB Renders
    pmw_pcb = WORKSPACE / "pcbs" / "pmw3360" / "curcur40-pmw3360.kicad_pcb"
    render_kicad_pcb(pmw_pcb, ASSETS_DIR / "render_pmw3360_top.png", side="top", width=1000, height=1000)
    render_kicad_pcb(pmw_pcb, ASSETS_DIR / "render_pmw3360_bottom.png", side="bottom", width=1000, height=1000)

    # 4. Top Plate Renders
    left_plate = WORKSPACE / "plates" / "pcb" / "plate-top-left.kicad_pcb"
    right_plate = WORKSPACE / "plates" / "pcb" / "plate-top-right.kicad_pcb"
    render_kicad_pcb(left_plate, ASSETS_DIR / "render_plate_left.png", side="top", width=1400, height=1000)
    render_kicad_pcb(right_plate, ASSETS_DIR / "render_plate_right.png", side="top", width=1600, height=1200)

    print("All preview images rendered into docs/assets/ successfully!")


if __name__ == "__main__":
    main()
