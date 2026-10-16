# -*- coding: utf-8 -*-
"""
Resolve Issue (4):
- Fill the over-enlarged 23x28mm hole on the right case bottom.
- Cut accurate compact optical window (8.0 x 12.0 mm, R=1.5 mm) at (cx=23.8125, cy=-109.5375).
- Cut 4x M2 mounting screw holes (dia 2.20 mm) at (+-4.50, +-10.00) relative to (cx, cy).
- Export cases/curcur40/right.step, right.stl, and update cases/curcur40/assembly-full.step.
- Generate bottom verification render.
"""
import os
import sys
import math
from pathlib import Path

WORKSPACE = Path(r"c:\Users\oktnt\workspace\curcur40")
CASES_DIR = WORKSPACE / "cases" / "curcur40"
ARTIFACTS_DIR = Path(r"C:\Users\oktnt\.gemini\antigravity\brain\dab819aa-2c9f-4dd2-be5e-39a298725eca")

sys.path.insert(0, str(ARTIFACTS_DIR / "scratch"))

import cadgen.build123d as bd

def fix_right_case():
    print("1. Loading right.step...")
    case = bd.import_step(str(CASES_DIR / "right.step"))
    print("Initial volume:", case.volume)

    # Trackball center in case coordinates (+2.0mm shifted)
    cx, cy = 23.8125, -109.5375

    # 2. Fill the over-enlarged hole
    print("2. Filling over-enlarged bottom hole...")
    plug = bd.Box(23.20, 28.20, 2.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((21.8125, -109.5375, -11.40)))
    case_filled = case + plug
    print("Filled volume:", case_filled.volume)

    # 3. Cut compact optical sensor window (8.0 x 12.0 mm, R=1.5 mm)
    print("3. Cutting compact optical window (8x12mm)...")
    with bd.BuildSketch(bd.Plane.XY.offset(-12.0)) as sk_opt:
        with bd.Locations([(cx, cy)]):
            bd.RectangleRounded(8.00, 12.00, radius=1.50)
    opt_solid = bd.extrude(sk_opt.sketch, amount=4.0)
    case_with_opt = case_filled - opt_solid

    # 4. Cut 4x M2 mounting holes (dia 2.20 mm, pitch 9.0 x 20.0 mm)
    print("4. Cutting 4x M2 mounting holes...")
    tb_screws = [
        (cx - 4.50, cy - 10.00),
        (cx + 4.50, cy - 10.00),
        (cx - 4.50, cy + 10.00),
        (cx + 4.50, cy + 10.00),
    ]
    case_final = case_with_opt
    for sx, sy in tb_screws:
        hole = bd.Cylinder(
            radius=1.10,
            height=10.0,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER),
        ).moved(bd.Location((sx, sy, -10.0)))
        case_final = case_final - hole

    solids = case_final.solids()
    print(f"Final solid: {len(solids)} solid(s), volume = {case_final.volume:.2f} mm^3")
    assert len(solids) == 1, f"Expected 1 solid, got {len(solids)}"

    print("5. Exporting updated right.step and right.stl...")
    bd.export_step(case_final, str(CASES_DIR / "right.step"))
    bd.export_stl(case_final, str(CASES_DIR / "right.stl"))
    print("Case files updated successfully!")
    return case_final

def main():
    case_fixed = fix_right_case()

    print("6. Updating cases/curcur40/assembly-full.step...")
    from update_assembly_issue1_only import main as update_assembly
    update_assembly()

    print("7. Rendering bottom verification image...")
    from render_right_case_views import extract_triangles, render_scene
    tris_case = extract_triangles(case_fixed.wrapped, (70, 80, 95))
    render_scene(tris_case, str(ARTIFACTS_DIR / "issue4_fixed_case_bottom.png"), pitch_deg=180.0, yaw_deg=0.0)
    render_scene(tris_case, str(ARTIFACTS_DIR / "issue4_fixed_case_iso.png"), pitch_deg=34.0, yaw_deg=-15.0)
    print("Done!")

if __name__ == "__main__":
    main()
