# -*- coding: utf-8 -*-
"""
Render close-up verification views of updated right case (cases/curcur40/right.step).
"""
import os
import sys
import math
from pathlib import Path

WORKSPACE = Path(r"c:\Users\oktnt\workspace\curcur40")
CASES_DIR = WORKSPACE / "cases" / "curcur40"
ARTIFACTS_DIR = Path(r"C:\Users\oktnt\.gemini\antigravity\brain\dab819aa-2c9f-4dd2-be5e-39a298725eca")

sys.path.insert(0, str(ARTIFACTS_DIR / "scratch"))
from update_full_assembly import load_step, extract_triangles, render_scene

def main():
    print("Loading right case...")
    right_case = load_step(CASES_DIR / "right.step")
    tb_cup = load_step(CASES_DIR / "trackball-cup.step")
    from update_full_assembly import translate_shape
    tb_cup_placed = translate_shape(tb_cup, 23.8125, -109.5375, 10.60)

    tris_case = extract_triangles(right_case, (70, 80, 95))
    tris_cup = extract_triangles(tb_cup_placed, (200, 150, 60))
    all_tris = tris_case + tris_cup

    print("Rendering right case ISO...")
    render_scene(all_tris, str(ARTIFACTS_DIR / "right_case_verified_iso.png"), pitch_deg=34.0, yaw_deg=-15.0)
    print("Rendering right case Top...")
    render_scene(all_tris, str(ARTIFACTS_DIR / "right_case_verified_top.png"), pitch_deg=0.0, yaw_deg=0.0)
    print("Rendering right case Bottom...")
    render_scene(tris_case, str(ARTIFACTS_DIR / "right_case_verified_bottom.png"), pitch_deg=180.0, yaw_deg=0.0)
    print("Right case renders complete!")

if __name__ == "__main__":
    main()
