# -*- coding: utf-8 -*-
"""
Render all PCB/3D CAD preview images and generate engineering & visual BOM diagrams for the
Passive Magnetic Inertia Wheel Module (`curcur40-inertia-wheel`: Cup-Shaped SUS304 Flywheel +
Internal 9-Ball Eddy-Current-Free Ratchet + Twin 180°-Symmetric Pyramid-Deep-R Snap Covers).

Outputs into `docs/assets/`:
  1. render_pcb_wheel_sensor.png / render_pcb_wheel_sensor_back.png / render_pcb_wheel_eval.png
  2. render_inertia_wheel_flywheel.png / render_inertia_wheel_module.png / render_inertia_wheel_eval_pod.png
  3. render_curcur40_right_inertia_wheel_sunk.png
  4. passive_inertia_wheel_spec.png
  5. inertia_wheel_parts_guide.png
"""
from pathlib import Path
import json
import os
import subprocess
import tempfile
import textwrap
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches

WORKSPACE = Path(__file__).resolve().parent.parent
ASSETS_DIR = WORKSPACE / "docs" / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
KICAD_CLI = Path(os.path.expandvars(r"%LOCALAPPDATA%\Programs\KiCad\10.0\bin\kicad-cli.exe"))
UVX_EXE = Path(os.path.expandvars(r"%USERPROFILE%\.local\bin\uvx.exe"))

plt.rcParams["font.sans-serif"] = [
    "Meiryo",
    "Yu Gothic",
    "MS Gothic",
    "DejaVu Sans",
    "Arial",
]
plt.rcParams["axes.unicode_minus"] = False


def render_pcb_and_step_previews():
    """Render updated KiCad PCBs and 3D CAD STEP models into `docs/assets/`."""
    sensor_pcb = WORKSPACE / "pcbs" / "inertia-wheel-sensor" / "curcur40-wheel-sensor.kicad_pcb"
    eval_pcb = WORKSPACE / "pcbs" / "inertia-wheel-eval" / "curcur40-wheel-eval.kicad_pcb"

    pcb_jobs = [
        (sensor_pcb, "top", ASSETS_DIR / "render_pcb_wheel_sensor.png", 1200, 900),
        (sensor_pcb, "bottom", ASSETS_DIR / "render_pcb_wheel_sensor_back.png", 1200, 900),
        (eval_pcb, "top", ASSETS_DIR / "render_pcb_wheel_eval.png", 1400, 1000),
    ]
    for pcb_path, side, out_png, w, h in pcb_jobs:
        print(f"Rendering {out_png.name} ({side})...")
        subprocess.run(
            [
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
                str(w),
                "--height",
                str(h),
                "-o",
                str(out_png),
                str(pcb_path),
            ],
            check=True,
        )

    parts_dir = WORKSPACE / "cases" / "inertia_wheel"
    asm_dir = WORKSPACE / "cases" / "assemblies"
    step_jobs = [
        {
            "input": str(parts_dir / "sus304-flywheel.step"),
            "outputs": [str(ASSETS_DIR / "render_inertia_wheel_flywheel.png")],
            "camera": "iso",
            "display": "shaded",
        },
        {
            "input": str(asm_dir / "inertia-wheel-module-assembly.step"),
            "outputs": [str(ASSETS_DIR / "render_inertia_wheel_module.png")],
            "camera": "iso",
            "display": "parts",
        },
        {
            "input": str(asm_dir / "inertia-wheel-eval-pod-assembly.step"),
            "outputs": [str(ASSETS_DIR / "render_inertia_wheel_eval_pod.png")],
            "camera": "iso",
            "display": "parts",
        },
        {
            "input": str(asm_dir / "curcur40-right-with-inertia-wheel-sunk.step"),
            "outputs": [str(ASSETS_DIR / "render_curcur40_right_inertia_wheel_sunk.png")],
            "camera": "iso",
            "display": "parts",
        },
    ]
    with tempfile.TemporaryDirectory() as tmp_s:
        job_path = Path(tmp_s) / "preview_jobs.json"
        job_path.write_text(json.dumps({"jobs": step_jobs}, ensure_ascii=False, indent=2), encoding="utf-8")
        print("Rendering 4 STEP previews into docs/assets/...")
        subprocess.run(
            [
                str(UVX_EXE),
                "--no-config",
                "--managed-python",
                "--python",
                "3.13",
                "--from",
                "cadgen==0.7.26",
                "cadgen",
                "snapshot",
                "--job",
                str(job_path),
                "--width",
                "1600",
                "--height",
                "1200",
            ],
            check=True,
        )


def _draw_spec_diagram():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16.0, 7.6), dpi=200)
    fig.patch.set_facecolor("#ffffff")
    fig.suptitle(
        "パッシブ磁気慣性ホイール 内部断面・機構図（共通コアユニット ＋ #04B 沈み込み枠 ＋ #20 ツインカバー実装時）",
        fontsize=12.4,
        fontweight="bold",
        y=0.97,
        color="#1a1a1a",
    )

    z_axle = -2.00  # Sunk mount: rotary center aligned to Top Plate top surface Z = -2.00 mm (wheel top Z = +6.40 mm)

    # =========================================================================
    # Panel 1: X-Z Front Cross-Section (Centered Cup Wheel + Twin Symmetric Snap Covers)
    # =========================================================================
    ax1.set_title("① 正面断面図 (X–Z 断面：中央揃えカップ型ホイール × 左右対称スナップカバー)", fontsize=10.5, fontweight="bold", pad=10)
    ax1.set_xlim(-12.2, 12.2)
    ax1.set_ylim(-15.0, 9.2)
    ax1.set_aspect("equal")
    ax1.set_facecolor("#f8f9fa")
    ax1.grid(True, linestyle=":", linewidth=0.5, color="#cccccc")
    ax1.set_xlabel("モジュール X 座標 [mm]（ホイール中心 X=0.00 ＝ 直下キー rEXSW2 左右中央と完全一致！）", fontsize=9.1)
    ax1.set_ylabel("curcur40 グローバル Z 座標 [mm]（プレート上面 = -2.00 mm）", fontsize=9.1)

    ax1.axvline(0.0, color="#64748b", linestyle="-.", linewidth=0.9, zorder=1)
    ax1.axhline(3.60, color="#0077b6", linestyle=":", linewidth=1.1, zorder=2)
    ax1.text(-11.9, 3.82, "隣接キーキャップ上面 Z = +3.60 mm", fontsize=7.1, fontweight="bold", color="#0077b6")

    # Main PCB (-5.80..-4.20) with 18.50 mm inner cutout (±9.25 mm)
    ax1.add_patch(patches.Rectangle((-12.0, -5.80), 2.75, 1.60, fc="#2a9d8f", ec="#1b4332", lw=1.1, zorder=2))
    ax1.add_patch(patches.Rectangle((9.25, -5.80), 2.75, 1.60, fc="#2a9d8f", ec="#1b4332", lw=1.1, zorder=2))
    ax1.text(-10.6, -6.55, "メインPCB\n(-5.8〜-4.2)", ha="center", va="top", fontsize=6.6, color="#1b4332", fontweight="bold")

    # Top Plate (-3.60..-2.00) with Twin-Snap window (±8.20 mm hidden under ±9.30 mm Twin Covers!)
    ax1.add_patch(patches.Rectangle((-12.0, -3.60), 3.80, 1.60, fc="#3a7ca5", ec="#16425b", lw=1.1, zorder=2))
    ax1.add_patch(patches.Rectangle((8.20, -3.60), 3.80, 1.60, fc="#3a7ca5", ec="#16425b", lw=1.1, zorder=2))

    # #04B Sunk Base Frame (-13.75..-11.15 floor + East flange [9.35..12.0] up to -5.81)
    sunk_base_poly = patches.Polygon(
        [
            [-8.45, -13.75], [11.95, -13.75], [11.95, -5.81], [9.35, -5.81],
            [9.35, -11.15], [-8.45, -11.15],
        ],
        closed=True, fc="#264653", ec="#111111", lw=1.0, zorder=3,
    )
    ax1.add_patch(sunk_base_poly)
    ax1.add_patch(patches.Rectangle((10.50, -5.81), 1.35, 2.20, fc="#264653", ec="#111111", lw=0.9, zorder=3))
    ax1.text(0.4, -12.45, "#04B 沈み込みベース枠（既存ケース底面まで 3.65mm 以上の余裕・ケース無改造）",
             ha="center", va="center", fontsize=6.5, color="white", fontweight="bold", zorder=4)

    # #03 Slim Rounded-Ear Carriage Pillars (X in [-4.55, -3.05] & [+3.10, +5.35], Z in [-10.40, +1.45])
    ax1.add_patch(patches.Rectangle((-4.55, -10.40), 1.50, 11.85, fc="#dee2e6", ec="#495057", lw=1.0, zorder=3))
    ax1.add_patch(patches.Rectangle((-7.79, -9.15), 3.24, 1.90, fc="#dee2e6", ec="#495057", lw=0.9, zorder=3))
    ax1.add_patch(patches.Rectangle((3.10, -10.40), 2.25, 11.85, fc="#dee2e6", ec="#495057", lw=1.0, zorder=3))

    # #14 Shaft Ø2.0 mm (X in [-4.72, +5.18], Z = -2.00 ± 1.00)
    ax1.add_patch(patches.Rectangle((-4.72, z_axle - 1.0), 9.90, 2.0, fc="#f8f9fa", ec="#343a40", lw=1.1, zorder=5))
    ax1.text(0.25, z_axle, "SUS304軸 Ø2.0", ha="center", va="center", fontsize=6.1, fontweight="bold", color="#212529", zorder=9)

    # #12 Miniature Degreased Bearings (MR52: [-4.70, -2.75] & [+3.13, +5.13])
    ax1.add_patch(patches.Rectangle((-4.70, z_axle - 2.5), 1.95, 5.0, fc="#ffffff", ec="#0077b6", lw=1.2, zorder=4))
    ax1.add_patch(patches.Rectangle((3.13, z_axle - 2.5), 2.00, 5.0, fc="#ffffff", ec="#0077b6", lw=1.2, zorder=4))

    # #07 Stepped Sensor Sub-PCB (X in [-7.75, -6.95], Z in [-8.10, +0.56]) + #08 AS5600 + #16 Diametric Magnet
    ax1.add_patch(patches.Rectangle((-7.75, -8.10), 0.80, 8.66, fc="#2a9d8f", ec="#1b4332", lw=1.0, zorder=4))
    ax1.add_patch(patches.Rectangle((-6.94, -4.95), 1.25, 4.90, fc="#212529", ec="#000000", lw=1.0, zorder=5))
    ax1.text(-6.31, -2.50, "AS5600", ha="center", va="center", fontsize=5.3, color="white", rotation=90, zorder=6)
    ax1.add_patch(patches.Rectangle((-5.49, z_axle - 1.50), 0.75, 3.00, fc="#e63946", ec="#6a040f", lw=1.0, zorder=6))

    # Twin 180°-Symmetric #20 Pyramid-Deep-R Snap Covers (X in [-9.30, -3.13] & [+3.13, +9.30], Z in [-1.99, +2.68])
    # Section at Y = Y_AXLE: swept click-stroke tunnel (X >= -6.61, Z <= +1.83) & #07 PCB pocket (X in [-8.15, -5.75],
    # Z <= +0.93); 0.40 mm gap to the #01 wheel (>= 0.30 mm at the ±0.10 mm lateral snap-leg play)
    for sgn in (-1.0, 1.0):
        cov_pts = [
            [sgn * 3.13, 1.83],
            [sgn * 3.13, 2.68],
            [sgn * 8.30, 2.68],
            [sgn * 8.60, 2.62],
            [sgn * 8.90, 2.24],
            [sgn * 9.10, 1.38],
            [sgn * 9.25, 0.39],
            [sgn * 9.30, -0.40],
            [sgn * 9.30, -1.99],
            [sgn * 8.15, -1.99],
            [sgn * 8.15, 0.93],
            [sgn * 6.61, 0.93],
            [sgn * 6.61, 1.83],
        ]
        ax1.add_patch(patches.Polygon(cov_pts, closed=True, fc="#64748b", ec="#1e293b", lw=1.35, alpha=0.88, zorder=7))
        # Snap-leg indicator below the cover (X in [±3.95, ±5.75], 1.80 mm wide located by 2.00 mm plate windows)
        ax1.add_patch(patches.Rectangle((min(sgn * 3.95, sgn * 5.75), -4.55), 1.80, 2.56,
                                        fc="#94a3b8", ec="#334155", lw=0.9, linestyle="--", alpha=0.75, zorder=5))

    # #01 Cup-Shaped SUS304 Flywheel centered at X = 0.00 (X in [-2.73, +2.73], Z in [-10.40, +6.40])
    cup_poly = patches.Polygon(
        [
            [-2.73, z_axle - 8.40], [2.73, z_axle - 8.40], [2.73, z_axle - 6.25], [-0.57, z_axle - 6.25],
            [-0.57, z_axle + 6.25], [2.73, z_axle + 6.25], [2.73, z_axle + 8.40], [-2.73, z_axle + 8.40],
        ],
        closed=True, fc="#d8dee9", ec="#4c566a", lw=1.5, zorder=6,
    )
    ax1.add_patch(cup_poly)
    ax1.add_patch(patches.Rectangle((-0.65, z_axle + 7.90), 1.30, 0.52, fc="#f8f9fa", ec="#4c566a", lw=0.9, zorder=7))
    ax1.add_patch(patches.Rectangle((-0.65, z_axle - 8.42), 1.30, 0.52, fc="#f8f9fa", ec="#4c566a", lw=0.9, zorder=7))

    # #02 Internal 9-Ball Hub (X in [-0.49, +2.61]) + #13 Balls + #18/#17 Axial M2 Adjuster (Z = -6.30)
    ax1.add_patch(patches.Rectangle((-0.49, z_axle - 6.20), 3.10, 12.40, fc="#a8dadc", ec="#1d3557", lw=1.2, zorder=6))
    ax1.add_patch(patches.Circle((1.41, z_axle + 4.30), 1.00, fc="#495057", ec="#111111", lw=0.9, zorder=7))
    ax1.add_patch(patches.Circle((1.41, z_axle - 4.30), 1.00, fc="#495057", ec="#111111", lw=0.9, zorder=7))
    ax1.add_patch(patches.Rectangle((2.85, z_axle - 4.30 - 0.85), 1.00, 1.70, fc="#e63946", ec="#6a040f", lw=1.0, zorder=8))
    ax1.add_patch(patches.Rectangle((3.85, z_axle - 4.30 - 0.82), 1.85, 1.64, fc="#adb5bd", ec="#212529", lw=1.0, hatch="///", zorder=8))

    ax1.annotate("#01 カップ型SUS304 (X=0中央揃え)\n頂点 Z=+6.40mm (キー上 +2.8mm)",
                 xy=(0.0, 6.40), xytext=(0.0, 8.15), ha="center", va="center",
                 arrowprops=dict(arrowstyle="->", color="#1f2937", lw=1.15),
                 fontsize=6.9, fontweight="bold", color="#1f2937",
                 bbox=dict(boxstyle="round,pad=0.22", fc="#f1f5f9", ec="#4c566a", lw=0.9), zorder=10)
    ax1.annotate("#20 ホイールカバー (エッジ曲面ピラミッド)\n(180°対称共通部品×2 / 頂点 +2.68mm)\n#07基板＆軸受丸耳を完全目隠し!",
                 xy=(-6.2, 2.55), xytext=(-7.8, 6.75), ha="center", va="center",
                 arrowprops=dict(arrowstyle="->", color="#1e293b", lw=1.15),
                 fontsize=6.7, fontweight="bold", color="#0f172a",
                 bbox=dict(boxstyle="round,pad=0.22", fc="#e2e8f0", ec="#334155", lw=0.9), zorder=10)
    ax1.annotate("#02 内蔵9球ハブ\n(#01カップ内へ100%格納)",
                 xy=(1.5, 3.6), xytext=(7.8, 6.85), ha="center", va="center",
                 arrowprops=dict(arrowstyle="->", color="#1d3557", lw=1.15),
                 fontsize=6.8, fontweight="bold", color="#1d3557",
                 bbox=dict(boxstyle="round,pad=0.22", fc="#e0fbfc", ec="#1d3557", lw=0.9), zorder=10)

    # =========================================================================
    # Panel 2: Y-Z Side Section (Hinged Silent Click + Switch-Style Cover Snap Hooks)
    # =========================================================================
    ax2.set_title("② 側面機構図 (Y–Z 断面：スイッチ式カバー爪締結 × 一体揺動静音クリック)", fontsize=10.5, fontweight="bold", pad=10)
    ax2.set_xlim(-12.5, 13.5)
    ax2.set_ylim(-15.0, 9.2)
    ax2.set_aspect("equal")
    ax2.set_facecolor("#f8f9fa")
    ax2.grid(True, linestyle=":", linewidth=0.5, color="#cccccc")
    ax2.set_xlabel("モジュール Y 座標 [mm]（北 -Y ヒンジ軸 ／ 南 +Y 静音スイッチ ＆ 隣接キー rEXSW2）", fontsize=9.1)
    ax2.set_ylabel("curcur40 グローバル Z 座標 [mm]", fontsize=9.1)

    ax2.axhline(3.60, color="#0077b6", linestyle=":", linewidth=1.1, zorder=2)

    # Main PCB (-5.80..-4.20) & Top Plate (-3.60..-2.00, snap-window ±5.43 mm)
    ax2.add_patch(patches.Rectangle((-12.3, -5.80), 3.05, 1.60, fc="#2a9d8f", ec="#1b4332", lw=1.1, zorder=2))
    ax2.add_patch(patches.Rectangle((9.25, -5.80), 4.05, 1.60, fc="#2a9d8f", ec="#1b4332", lw=1.1, zorder=2))
    ax2.add_patch(patches.Rectangle((-12.3, -3.60), 6.77, 1.60, fc="#3a7ca5", ec="#16425b", lw=1.1, zorder=3))
    ax2.add_patch(patches.Rectangle((5.33, -3.60), 7.97, 1.60, fc="#3a7ca5", ec="#16425b", lw=1.1, zorder=3))

    # #04B Sunk Base Floor & North Hinge Pin Ø2.0 mm at (Y = -6.85, Z = -10.40)
    ax2.add_patch(patches.Rectangle((-8.80, -13.75), 17.60, 1.20, fc="#264653", ec="#111111", lw=1.0, zorder=2))
    ax2.add_patch(patches.Circle((-6.85, -10.40), 1.00, fc="#ffffff", ec="#212529", lw=1.5, zorder=6))
    ax2.text(-6.85, -11.65, "北端ヒンジ軸 Ø2.0", ha="center", va="top", fontsize=6.6, fontweight="bold", color="#212529",
             bbox=dict(boxstyle="round,pad=0.14", fc="#ffffff", ec="#adb5bd", lw=0.7), zorder=8)

    # Unitized Inner Carriage
    carriage_poly = patches.Polygon(
        [[-8.77, -10.40], [7.10, -8.17], [7.10, -7.32], [3.35, -7.32], [3.35, 1.45], [-3.55, 1.45], [-8.77, -7.25]],
        closed=True, fc="#dee2e6", ec="#495057", lw=1.1, alpha=0.55, zorder=2,
    )
    ax2.add_patch(carriage_poly)

    # #10 Kailh Square Silent Switch (H=4.3mm official drawing: 6.20 x 3.35 mm body + Ø3.00 x 0.95 mm plunger = 4.30 mm FP)
    ax2.add_patch(patches.Rectangle((2.60, -12.53), 6.20, 3.35, fc="#f4a261", ec="#9c4100", lw=1.2, zorder=4))
    ax2.add_patch(patches.Rectangle((4.20, -9.18), 3.00, 0.95, fc="#e63946", ec="#6a040f", lw=1.0, zorder=5))
    ax2.annotate("#10 静音マイクロSW (Kailh Silent)\nプレート下へ完全沈み込み!",
                 xy=(5.70, -10.8), xytext=(5.6, -14.25), ha="center", va="center",
                 arrowprops=dict(arrowstyle="->", color="#9c4100", lw=1.1),
                 fontsize=6.6, fontweight="bold", color="#7f2704",
                 bbox=dict(boxstyle="round,pad=0.18", fc="#fff3cd", ec="#d97706", lw=0.8), zorder=9)

    # #20 Pyramid-Deep-R Cover Side Silhouette (Y in [-7.80, +7.60], Z in [-1.99, +2.68]): stays >= 0.48 mm inside
    # the Ø16.80 mm wheel outline when viewed along the axle, + N/S Snap Hooks
    yc = -0.10
    cov_half = [(-1.99, 7.70), (-0.40, 7.70), (0.00, 7.66), (0.50, 7.49), (1.00, 7.25), (1.50, 7.02),
                (2.00, 6.72), (2.40, 6.18), (2.60, 5.61), (2.68, 5.10)]
    cov_yz = patches.Polygon(
        [[yc - v, z] for (z, v) in cov_half] + [[yc + v, z] for (z, v) in reversed(cov_half)],
        closed=True, fc="#64748b", ec="#1e293b", lw=1.25, alpha=0.42, zorder=7,
    )
    ax2.add_patch(cov_yz)
    for sgn in (-1.0, 1.0):
        hk = patches.Polygon(
            [
                [yc + sgn * 4.52, -1.99],
                [yc + sgn * 5.37, -1.99],
                [yc + sgn * 5.37, -3.63],
                [yc + sgn * 5.65, -3.76],
                [yc + sgn * 5.37, -4.55],
                [yc + sgn * 4.52, -4.55],
            ],
            closed=True, fc="#475569", ec="#0f172a", lw=1.0, zorder=8,
        )
        ax2.add_patch(hk)
    ax2.annotate("キースイッチ方式スナップ爪\n(1.6mmプレート裏面へパチン固定!)",
                 xy=(-5.65, -3.75), xytext=(-7.2, 6.80), ha="center", va="center",
                 arrowprops=dict(arrowstyle="->", color="#0f172a", lw=1.1),
                 fontsize=6.8, fontweight="bold", color="#0f172a",
                 bbox=dict(boxstyle="round,pad=0.22", fc="#e2e8f0", ec="#334155", lw=0.9), zorder=10)

    # Adjacent South Keycap (rEXSW2 North edge at Y = +10.95 mm, Z in [-0.80, +3.60])
    ax2.add_patch(patches.Rectangle((10.95, -0.80), 2.35, 4.40, fc="#e9ecef", ec="#495057", lw=1.2, zorder=5))
    ax2.annotate("南キー余裕\n2.72mm", xy=(8.30, 1.40), xytext=(9.65, 5.50),
                 arrowprops=dict(arrowstyle="<->", color="#2b9348", lw=1.1),
                 fontsize=6.8, fontweight="bold", color="#1b4332", ha="center", zorder=9)

    # Wheel Circle (Ø16.80 mm at Y = -0.10, Z = -2.00) + Internal 9-Ball Hub
    wy, wz = -0.10, z_axle
    ax2.add_patch(patches.Circle((wy, wz), 8.40, fc="#d8dee9", ec="#4c566a", lw=1.6, alpha=0.65, zorder=4))
    for a in np.linspace(0, 2 * np.pi, 36, endpoint=False):
        ax2.plot([wy + 7.95 * np.cos(a), wy + 8.40 * np.cos(a)],
                 [wz + 7.95 * np.sin(a), wz + 8.40 * np.sin(a)], color="#4c566a", lw=0.8, zorder=5)
    ax2.add_patch(patches.Circle((wy, wz), 6.20, fc="#a8dadc", ec="#1d3557", lw=1.1, linestyle="--", alpha=0.85, zorder=5))
    for a in np.linspace(0, 2 * np.pi, 9, endpoint=False):
        bx = wy + 4.30 * np.sin(a)
        bz = wz - 4.30 * np.cos(a)
        ax2.add_patch(patches.Circle((bx, bz), 1.00, fc="#495057", ec="#111111", lw=0.75, zorder=6))
    ax2.add_patch(patches.Circle((wy, wz), 1.00, fc="#ffffff", ec="#212529", lw=1.2, zorder=6))
    ax2.text(wy, 4.65, "Ø16.8 カップ型SUS304\n(中心 Z = -2.00 mm)", ha="center", va="center",
             fontsize=6.9, fontweight="bold", color="#1f2937", zorder=9)

    # Bottom Axial M2 Magnet Gap Adjuster at 6 o'clock (Y = -0.10, Z = -6.30)
    mz = wz - 4.30
    ax2.add_patch(patches.Circle((wy, mz), 1.05, fc="#e63946", ec="#6a040f", lw=1.3, zorder=8))
    ax2.annotate("#18 東軸受下部 M2磁力調整ネジ\n(基板下 Z=-6.30mm へ完全隠蔽)",
                 xy=(wy - 0.9, mz), xytext=(-8.2, -8.35), ha="center", va="center",
                 arrowprops=dict(arrowstyle="->", color="#d90429", lw=1.15),
                 fontsize=6.6, fontweight="bold", color="#9d0208",
                 bbox=dict(boxstyle="round,pad=0.20", fc="#ffe5ec", ec="#d90429", lw=0.85), zorder=9)

    plt.tight_layout(rect=[0, 0.01, 1, 0.94])
    out_path = ASSETS_DIR / "passive_inertia_wheel_spec.png"
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    print(f"Saved {out_path}")


def _autocrop_pil(img_path: Path, pad_frac: float = 0.08) -> tuple[np.ndarray, tuple[float, float, float]]:
    """Crop uniform background around rendered object."""
    raw = Image.open(img_path)
    if raw.mode in ("RGBA", "LA"):
        white = Image.new("RGBA", raw.size, (255, 255, 255, 255))
        im = Image.alpha_composite(white, raw.convert("RGBA")).convert("RGB")
    else:
        im = raw.convert("RGB")
    arr = np.asarray(im, dtype=np.uint8)
    bg = arr[2, 2].astype(np.int16)
    thresh = 35 if int(bg.min()) > 245 else 8
    diff = np.abs(arr.astype(np.int16) - bg).max(axis=2)
    ys, xs = np.where(diff > thresh)
    if len(xs) == 0:
        return arr.astype(np.float32) / 255.0, tuple((bg / 255.0).tolist())
    x0, x1 = int(xs.min()), int(xs.max())
    y0, y1 = int(ys.min()), int(ys.max())
    bw = max(1, x1 - x0)
    bh = max(1, y1 - y0)
    px = int(bw * pad_frac)
    py = int(bh * pad_frac)
    x0 = max(0, x0 - px)
    x1 = min(arr.shape[1] - 1, x1 + px)
    y0 = max(0, y0 - py)
    y1 = min(arr.shape[0] - 1, y1 + py)
    cropped = arr[y0 : y1 + 1, x0 : x1 + 1].astype(np.float32) / 255.0
    return cropped, tuple((bg / 255.0).tolist())


def _build_temp_part_renders(tmp_dir: Path) -> dict[str, Path]:
    """Build helper 3D STEP models for off-the-shelf & upright components & render all thumbnails in one cadgen job."""
    gen_code = textwrap.dedent(
        f"""
        import math, sys
        from pathlib import Path
        import build123d as bd

        sys.path.insert(0, {repr(str(WORKSPACE / "scripts"))})
        import generate_inertia_wheel as giw

        out = Path({repr(str(tmp_dir))})

        # 1. Upright Carriage (assembled orientation)
        car = giw.build_wheel_carriage_assembled()
        c_bb = car.bounding_box()
        car = car.moved(bd.Location((0, 0, -c_bb.min.Z)))
        bd.export_step(car, str(out / "p03_carriage.step"))

        # 1b. Upright #20 Pyramid-Deep-R Cover Pair (showing exterior pyramid curves + interior tunnel/snap hooks!)
        cov_w = giw.build_wheel_cover_plate_coords()
        cov_e = cov_w.moved(bd.Location((0.0, -giw.Y_AXLE, 0.0))).rotate(bd.Axis.Z, 180).moved(bd.Location((5.5, giw.Y_AXLE, 0.0))).solids()[0]
        cov_e.label = "Wheel_Pyramid_Cover_Companion"
        cov_w_shifted = cov_w.moved(bd.Location((-2.5, 0.0, 0.0))).solids()[0]
        cov_w_shifted.label = "Wheel_Pyramid_Cover_Sensor"
        bd.export_step(bd.Compound(children=[cov_w_shifted, cov_e]), str(out / "p20_cover_pair.step"))

        # 1c. 3D Exploded Module Assembly (including lifted #20 Twin Pyramid-Deep-R Covers!)
        mod_parts = giw.assemble_module_parts(origin=(0.0, 0.0, 0.0), sunk=True, include_covers=True)
        exp_offsets = {{
            "Wheel_Pyramid_Cover_Sensor": (-11.0, 0.0, 15.0),
            "Wheel_Pyramid_Cover_Companion": (11.0, 0.0, 15.0),
            "AS5600_Sensor_SubPCB": (-13.5, 0.0, 6.5),
            "AS5600_SOIC8_IC": (-12.5, 0.0, 6.5),
            "AS5600_Cap_C1_100nF": (-12.5, 0.0, 6.5),
            "AS5600_Cap_C2_1uF": (-12.5, 0.0, 6.5),
            "Diametric_Magnet_3x1mm": (-8.5, 0.0, 6.5),
            "Bearing_MR52_West": (-5.2, 0.0, 6.5),
            "SUS304_Flywheel_Cup_16p8mm": (-1.2, 0.0, 6.5),
            "SUS304_Axle_Shaft_2mm": (1.5, 0.0, 6.5),
            "Ratchet_Hub_Internal_Resin": (7.5, 0.0, 6.5),
            "Bearing_MR52_East": (15.5, 0.0, 6.5),
            "Wheel_Hinged_Carriage": (0.0, 0.0, -3.0),
            "M2_Magnet_Adjuster_And_NdFeB": (8.8, 0.0, -3.0),
            "Wheel_Base_Frame_Sunk": (0.0, 0.0, -12.5),
            "Kailh_Silent_Switch_6x6x4p3": (0.0, 0.0, -9.5),
            "Hinge_Pin_SUS304_2mm": (-10.5, 0.0, -11.5),
        }}
        exploded_children = []
        for s in mod_parts:
            lbl = s.label
            if lbl.startswith("Steel_Ball_2mm_"):
                dx, dy, dz = (10.2, 0.0, 6.5)
            else:
                dx, dy, dz = exp_offsets.get(lbl, (0.0, 0.0, 0.0))
            ms = s.moved(bd.Location((dx, dy, dz))).solids()[0]
            ms.label = lbl
            exploded_children.append(ms)
        bd.export_step(bd.Compound(children=exploded_children), str(out / "mod_exploded.step"))

        # 2. AS5600-ASOT (SOIC-8) + 2x SMD Capacitors (100nF, 1uF)
        ic_body = bd.Box(3.9, 4.9, 1.35, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((-1.5, 0, 0.25)))
        ic_body = ic_body - bd.Cylinder(0.35, 0.3, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((-2.7, 1.6, 1.40)))
        ic_body.label = "AS5600_Body"
        pins = []
        for idx, py in enumerate([-1.905, -0.635, 0.635, 1.905]):
            for side, sx in [("L", -1.0), ("R", 1.0)]:
                p1 = bd.Box(0.95, 0.42, 0.22, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((-1.5 + sx * 2.35, py, 0.0)))
                p2 = bd.Box(0.35, 0.42, 0.85, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((-1.5 + sx * 2.02, py, 0.0)))
                p = (p1 + p2).solids()[0]
                p.label = f"Pin_{{side}}_{{idx}}"
                pins.append(p)
        caps = []
        for ci, cy in enumerate([-1.2, 1.2]):
            cb = bd.Box(1.0, 1.6, 0.8, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((3.2, cy, 0.0)))
            cb.label = f"Cap_Body_{{ci}}"
            ct1 = bd.Box(1.04, 0.35, 0.82, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((3.2, cy - 0.65, 0.0)))
            ct1.label = f"Cap_T1_{{ci}}"
            ct2 = bd.Box(1.04, 0.35, 0.82, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((3.2, cy + 0.65, 0.0)))
            ct2.label = f"Cap_T2_{{ci}}"
            caps.extend([cb, ct1, ct2])
        bd.export_step(bd.Compound(children=[ic_body, *pins, *caps]), str(out / "p08_as5600.step"))

        # 3. Waveshare RP2040-Zero (23.5 x 18.0 mm)
        pcb = bd.Box(23.5, 18.0, 1.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        pcb.label = "RP2040_PCB"
        usbc = bd.Box(7.4, 8.9, 3.2, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((-12.8, 0.0, 1.0)))
        usbc = usbc - bd.Box(5.5, 7.6, 2.2, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER)).moved(bd.Location((-13.0, 0.0, 2.6)))
        usbc.label = "USBC_Receptacle"
        mcu = bd.Box(7.0, 7.0, 0.9, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((1.8, 0.0, 1.0)))
        mcu.label = "RP2040_Chip"
        btn1 = bd.Box(2.6, 3.4, 1.3, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((-2.8, 5.2, 1.0)))
        btn1.label = "BOOT_Btn"
        btn2 = bd.Box(2.6, 3.4, 1.3, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((-2.8, -5.2, 1.0)))
        btn2.label = "RESET_Btn"
        rgb = bd.Box(2.0, 2.0, 0.8, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((8.2, 0.0, 1.0)))
        rgb.label = "RGB_LED"
        pads = []
        for pi in range(9):
            px = -9.5 + pi * 2.54
            for sy in [-8.7, 8.7]:
                pd = bd.Cylinder(0.75, 1.04, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((px, sy, -0.02)))
                pd.label = f"Pad_{{pi}}_{{int(sy)}}"
                pads.append(pd)
        bd.export_step(bd.Compound(children=[pcb, usbc, mcu, btn1, btn2, rgb, *pads]), str(out / "p09_rp2040_zero.step"))

        # 4. Kailh Square Silent Switch (6.2 x 6.2 x 4.3 mm: 3.30 mm pins, 3.35 mm housing body, Ø3.00 x 0.95 mm plunger)
        sw_base = bd.Box(6.2, 6.2, 2.25, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((0, 0, 3.30)))
        sw_base.label = "SW_Base"
        sw_top = bd.Box(6.0, 6.0, 1.10, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((0, 0, 5.55)))
        sw_top.label = "SW_Cover"
        sw_btn = bd.Cylinder(1.50, 0.95, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((0, 0, 6.65)))
        sw_btn.label = "SW_Red_Button"
        pin_a = bd.Box(0.75, 0.4, 3.30, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((-2.5, 0, 0.0)))
        pin_a.label = "SW_Pin1"
        pin_b = bd.Box(0.75, 0.4, 3.30, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((2.5, 0, 0.0)))
        pin_b.label = "SW_Pin2"
        bd.export_step(bd.Compound(children=[sw_base, sw_top, sw_btn, pin_a, pin_b]), str(out / "p10_silent_sw.step"))

        # 5. 2x Open Degreased Miniature Bearings (DDL-520 / MR52: Ø5 x Ø2 x 2.0 mm)
        brg_parts = []
        for bi, bx in enumerate([-3.4, 3.4]):
            outer_r = (
                bd.Cylinder(2.50, 2.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
                - bd.Cylinder(2.02, 2.10, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((0, 0, -0.05)))
            ).moved(bd.Location((bx, 0, 0)))
            outer_r.label = f"OuterRace_{{bi}}"
            inner_r = (
                bd.Cylinder(1.42, 2.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
                - bd.Cylinder(1.00, 2.10, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((0, 0, -0.05)))
            ).moved(bd.Location((bx, 0, 0)))
            inner_r.label = f"InnerRace_{{bi}}"
            brg_parts.extend([outer_r, inner_r])
            for k in range(8):
                a = math.radians(k * 45.0)
                ball = bd.Sphere(0.32).moved(bd.Location((bx + 1.72 * math.cos(a), 1.72 * math.sin(a), 1.00)))
                ball.label = f"BrgBall_{{bi}}_{{k}}"
                brg_parts.append(ball)
        bd.export_step(bd.Compound(children=brg_parts), str(out / "p12_bearings.step"))

        # 6. 9x Ø2.00 mm SUJ2 Steel Balls in ring
        balls_9 = []
        for k in range(9):
            a = math.radians(k * (360.0 / 9.0))
            sp = bd.Sphere(1.00).moved(bd.Location((4.3 * math.cos(a), 4.3 * math.sin(a), 1.00)))
            sp.label = f"SUJ2_Ball_{{k:02d}}"
            balls_9.append(sp)
        bd.export_step(bd.Compound(children=balls_9), str(out / "p13_steel_balls.step"))

        # 7. Axle Shaft (Ø2.0 x 10.0 mm) & Hinge Pin (Ø2.0 x 17.1 mm)
        sh = bd.Cylinder(1.00, 10.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90)
        sh = bd.chamfer(sh.edges(), length=0.18)
        sh.label = "Axle_Shaft"
        bd.export_step(sh, str(out / "p14_axle_shaft.step"))

        hp = bd.Cylinder(1.00, 17.1, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90)
        hp = bd.chamfer(hp.edges(), length=0.18)
        hp.label = "Hinge_Pin"
        bd.export_step(hp, str(out / "p15_hinge_pin.step"))

        # 8. M2 Stainless Set Screw (M2 x 4.5 mm)
        ss = bd.Cylinder(1.00, 4.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        with bd.BuildPart() as hex_bp:
            with bd.BuildSketch(bd.Plane.XY.offset(3.1)):
                bd.RegularPolygon(radius=0.55, side_count=6)
            bd.extrude(amount=1.6)
        ss = ss - hex_bp.part
        for ti in range(6):
            groove = (
                bd.Cylinder(1.05, 0.22, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
                - bd.Cylinder(0.86, 0.22, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
            ).moved(bd.Location((0, 0, 0.45 + ti * 0.62)))
            ss = ss - groove
        ss = ss.rotate(bd.Axis.X, -65)
        ss.label = "M2_Set_Screw"
        bd.export_step(ss, str(out / "p18_m2_adjuster.step"))

        # 9. 6x M2 x 4.0mm Mounting Screws + 4x Rubber Feet
        hw = []
        for si in range(6):
            sx = -6.0 + (si % 3) * 4.5
            sy = -2.5 + (si // 3) * 5.0
            shk = bd.Cylinder(0.95, 4.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((sx, sy, 0.0)))
            hd = bd.Cylinder(1.75, 1.1, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((sx, sy, 4.0)))
            slt = bd.Box(2.0, 0.45, 0.6, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((sx, sy, 4.6)))
            slt2 = bd.Box(0.45, 2.0, 0.6, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((sx, sy, 4.6)))
            scr = (shk + hd - slt - slt2).solids()[0]
            scr.label = f"M2_Screw_{{si}}"
            hw.append(scr)
        for fi in range(4):
            fx = 7.5 + (fi % 2) * 7.8
            fy = -3.8 + (fi // 2) * 7.6
            ft = bd.Cylinder(3.2, 1.8, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((fx, fy, 0.0)))
            ft = bd.fillet(ft.edges().filter_by(lambda e: e.bounding_box().min.Z > 1.5), radius=0.6)
            ft.label = f"Rubber_Foot_{{fi}}"
            hw.append(ft)
        bd.export_step(bd.Compound(children=hw), str(out / "p19_screws_feet.step"))
        """
    )
    helper_py = tmp_dir / "build_thumbs.py"
    helper_py.write_text(gen_code, encoding="utf-8")
    subprocess.run(
        [
            str(UVX_EXE),
            "--no-config",
            "--managed-python",
            "--python",
            "3.13",
            "--from",
            "cadgen==0.7.26",
            "python",
            "-B",
            str(helper_py),
        ],
        check=True,
    )

    parts_dir = WORKSPACE / "cases" / "inertia_wheel"
    render_specs = [
        ("mod_west", tmp_dir / "mod_exploded.step", "iso", "parts"),
        ("p01", parts_dir / "sus304-flywheel.step", "iso", "shaded"),
        ("p02", parts_dir / "ratchet-hub.step", "iso", "shaded"),
        ("p03", tmp_dir / "p03_carriage.step", "iso", "shaded"),
        ("p04a", parts_dir / "wheel-base-frame.step", "iso", "shaded"),
        ("p04b", parts_dir / "wheel-base-frame-sunk.step", "iso", "shaded"),
        ("p20", tmp_dir / "p20_cover_pair.step", "iso", "parts"),
        ("p05", parts_dir / "eval-pod-stand.step", "iso", "shaded"),
        ("p08", tmp_dir / "p08_as5600.step", "iso", "parts"),
        ("p09", tmp_dir / "p09_rp2040_zero.step", "iso", "parts"),
        ("p10", tmp_dir / "p10_silent_sw.step", "iso", "parts"),
        ("p12", tmp_dir / "p12_bearings.step", "35:48", "parts"),
        ("p13", tmp_dir / "p13_steel_balls.step", "35:45", "parts"),
        ("p14", tmp_dir / "p14_axle_shaft.step", "iso", "shaded"),
        ("p15", tmp_dir / "p15_hinge_pin.step", "iso", "shaded"),
        ("p18", tmp_dir / "p18_m2_adjuster.step", "iso", "shaded"),
        ("p19", tmp_dir / "p19_screws_feet.step", "35:42", "parts"),
    ]

    jobs = []
    out_map: dict[str, Path] = {}
    for key, target, cam, disp in render_specs:
        op = tmp_dir / f"{key}.png"
        out_map[key] = op
        jobs.append(
            {
                "input": str(target),
                "outputs": [str(op)],
                "camera": cam,
                "display": disp,
            }
        )

    job_json = tmp_dir / "jobs.json"
    job_json.write_text(json.dumps({"jobs": jobs}, ensure_ascii=False, indent=2), encoding="utf-8")
    subprocess.run(
        [
            str(UVX_EXE),
            "--no-config",
            "--managed-python",
            "--python",
            "3.13",
            "--from",
            "cadgen==0.7.26",
            "cadgen",
            "snapshot",
            "--job",
            str(job_json),
            "--width",
            "1100",
            "--height",
            "820",
        ],
        check=True,
    )
    return out_map


def _draw_wire_card(ax):
    """Custom crisp illustration for #11 センサー4芯線 (4-wire micro harness + JST SH plug)."""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.5)
    ax.set_facecolor("#eff2f6")
    ax.axis("off")
    ax.add_patch(patches.FancyBboxPatch((0.55, 1.55), 1.65, 3.4, boxstyle="round,pad=0.1", fc="#ffffff", ec="#334155", lw=1.4, zorder=4))
    ax.text(1.38, 3.25, "JST SH\n(または\nJ2直結)", ha="center", va="center", fontsize=6.6, fontweight="bold", color="#1e293b", zorder=5)
    wire_defs = [
        (4.45, "#dc2626", "1: +3V3 (赤)"),
        (3.65, "#1e293b", "2: GND  (黒)"),
        (2.85, "#2563eb", "3: SDA  (青)"),
        (2.05, "#d97706", "4: SCL  (黄)"),
    ]
    xs = np.linspace(2.2, 7.2, 80)
    for wy, col, lbl in wire_defs:
        ys = wy + 0.16 * np.sin((xs - 2.2) * 1.25)
        ax.plot(xs, ys, color=col, lw=2.8, solid_capstyle="round", zorder=3)
        ax.plot([7.2, 7.75], [ys[-1], ys[-1]], color="#94a3b8", lw=2.4, zorder=4)
        ax.text(7.92, ys[-1], lbl, ha="left", va="center", fontsize=6.8, fontweight="bold", color=col)
    ax.text(5.0, 0.58, "柔らかい極細線 AWG30〜34 × 4本（長さ約 55〜65 mm）", ha="center", va="center", fontsize=6.8, fontweight="bold", color="#334155")


def _draw_magnet_card(ax, diametric: bool):
    """Clear N/S polarity diagram for #16 角度磁石 (Diametric) vs #17 ラチェット磁石 (Axial)."""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.5)
    ax.set_facecolor("#eff2f6")
    ax.axis("off")
    if diametric:
        ax.add_patch(patches.Wedge((3.1, 3.45), 1.85, 90, 270, fc="#ef4444", ec="#7f1d1d", lw=1.4, zorder=4))
        ax.add_patch(patches.Wedge((3.1, 3.45), 1.85, -90, 90, fc="#3b82f6", ec="#1e3a8a", lw=1.4, zorder=4))
        ax.plot([3.1, 3.1], [1.60, 5.30], color="#ffffff", lw=1.6, linestyle="--", zorder=5)
        ax.text(2.18, 3.45, "N", ha="center", va="center", fontsize=12, fontweight="bold", color="white", zorder=6)
        ax.text(4.02, 3.45, "S", ha="center", va="center", fontsize=12, fontweight="bold", color="white", zorder=6)
        ax.annotate("", xy=(5.15, 3.45), xytext=(1.05, 3.45), arrowprops=dict(arrowstyle="<->", color="#111827", lw=1.2), zorder=3)
        ax.text(3.1, 1.02, "Ø3.0 × 厚0.75〜1.0mm", ha="center", va="center", fontsize=7.2, fontweight="bold", color="#1e293b")
        ax.add_patch(patches.FancyBboxPatch((5.55, 1.55), 4.05, 3.75, boxstyle="round,pad=0.18", fc="#fff1f2", ec="#be123c", lw=1.2))
        ax.text(7.58, 3.42, "【重要】径方向着磁\n(Diametric 2極)\n\n直径の左右で N/S が\n分かれた AS5600専用品!", ha="center", va="center", fontsize=6.9, fontweight="bold", color="#9f1239")
    else:
        ax.add_patch(patches.Rectangle((1.75, 3.45), 2.7, 1.45, fc="#ef4444", ec="#7f1d1d", lw=1.4, zorder=4))
        ax.add_patch(patches.Rectangle((1.75, 2.00), 2.7, 1.45, fc="#3b82f6", ec="#1e3a8a", lw=1.4, zorder=4))
        ax.add_patch(patches.Ellipse((3.10, 4.90), 2.7, 0.68, fc="#f87171", ec="#7f1d1d", lw=1.3, zorder=5))
        ax.text(3.10, 4.10, "N", ha="center", va="center", fontsize=11.5, fontweight="bold", color="white", zorder=6)
        ax.text(3.10, 2.68, "S", ha="center", va="center", fontsize=11.5, fontweight="bold", color="white", zorder=6)
        ax.text(3.10, 1.02, "Ø1.5〜2.0 × 厚1.5mm", ha="center", va="center", fontsize=7.3, fontweight="bold", color="#1e293b")
        ax.add_patch(patches.FancyBboxPatch((5.35, 1.55), 4.25, 3.75, boxstyle="round,pad=0.18", fc="#eff6ff", ec="#1d4ed8", lw=1.2))
        ax.text(7.48, 3.42, "通常の軸方向着磁\n(Axial 円柱ネオジム)\n\n厚みの上下で N/S が\n分かれた一般的な磁石", ha="center", va="center", fontsize=6.9, fontweight="bold", color="#1e3a8a")


def generate_parts_guide():
    """Generate `docs/assets/inertia_wheel_parts_guide.png` with 3D callouts + 21-card (7x3) visual BOM."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp_dir = Path(tmp_s)
        rendered = _build_temp_part_renders(tmp_dir)

        fig = plt.figure(figsize=(16.8, 25.4), dpi=160)
        fig.patch.set_facecolor("#ffffff")

        fig.text(
            0.50,
            0.985,
            "パッシブ磁気慣性ホイール 部品名称・構成図鑑（共通呼称マップ #01〜#20）",
            ha="center",
            va="center",
            fontsize=16.0,
            fontweight="bold",
            color="#0f172a",
        )
        fig.text(
            0.50,
            0.972,
            "本ビルドガイドおよび設計・組み立ての会話では、以下の「番号＋太字の部品名（例：#03 キャリッジ、#20 ホイールカバー）」を共通名称として使用します",
            ha="center",
            va="center",
            fontsize=10.0,
            fontweight="bold",
            color="#475569",
        )

        # =====================================================================
        # Upper Section: 2 Assembly Callout Panels (Standalone Pod + Sunk Exploded Module)
        # =====================================================================
        ax_pod = fig.add_axes([0.020, 0.735, 0.470, 0.222])
        ax_mod = fig.add_axes([0.510, 0.735, 0.470, 0.222])

        pod_img, pod_bg = _autocrop_pil(ASSETS_DIR / "render_inertia_wheel_eval_pod.png", pad_frac=0.22)
        ax_pod.set_facecolor(pod_bg)
        ax_pod.imshow(pod_img, extent=[0, 100, 0, 100], aspect="auto", zorder=1)
        ax_pod.set_xlim(-6, 106)
        ax_pod.set_ylim(-6, 106)
        ax_pod.set_xticks([])
        ax_pod.set_yticks([])
        for sp in ax_pod.spines.values():
            sp.set_edgecolor("#94a3b8")
            sp.set_linewidth(1.3)
        ax_pod.set_title("【構成例 A】オンボード実装：単体評価ポッド全体（#04A 枠使用）", fontsize=11.5, fontweight="bold", color="#0f172a", pad=7)

        pod_callouts = [
            (63.0, 77.0, 44.0, 97.5, "#01 カップ型フライホイール", "#1d3557"),
            (67.2, 68.0, 84.0, 97.0, "#02 内蔵9球ハブ (#01内部格納)", "#1d3557"),
            (65.5, 44.5, 89.0, 83.0, "#03 キャリッジ (スリム丸耳)", "#1d3557"),
            (70.2, 60.5, 86.5, 68.5, "#12 ベアリング + #14 軸", "#005f73"),
            (78.2, 47.0, 89.5, 53.0, "#10 静音スイッチ", "#1b4332"),
            (68.0, 34.5, 84.5, 35.5, "#04A オンボード枠 + #15 ピン", "#1d3557"),
            (62.8, 25.8, 84.5, 19.0, "#19 固定M2ネジ穴 (四隅)", "#9b2226"),
            (60.0, 16.5, 54.0, 1.5, "#05 ポッド台座", "#1d3557"),
            (42.0, 34.0, 13.0, 6.5, "#06 キャリア基板", "#1b4332"),
            (37.5, 48.5, 14.5, 24.0, "#11 センサー4芯線 接続先(J1)", "#1b4332"),
            (31.0, 66.0, 11.5, 86.0, "#09 RP2040-Zero", "#1b4332"),
            (70.5, 51.8, 17.5, 43.0, "#18 磁力調整ネジ (+#17 磁石)", "#9b2226"),
        ]
        for tx, ty, lx, ly, txt, col in pod_callouts:
            ax_pod.annotate(
                txt,
                xy=(tx, ty),
                xytext=(lx, ly),
                ha="center",
                va="center",
                fontsize=7.5,
                fontweight="bold",
                color="#0f172a",
                bbox=dict(boxstyle="round,pad=0.24", fc="#ffffff", ec=col, lw=1.3),
                arrowprops=dict(arrowstyle="-|>", color=col, lw=1.35, shrinkA=0, shrinkB=1),
                zorder=8,
            )

        mod_img, mod_bg = _autocrop_pil(rendered["mod_west"], pad_frac=0.20)
        ax_mod.set_facecolor(mod_bg)
        ax_mod.imshow(mod_img, extent=[0, 100, 0, 100], aspect="auto", zorder=1)
        ax_mod.set_xlim(-6, 106)
        ax_mod.set_ylim(-6, 106)
        ax_mod.set_xticks([])
        ax_mod.set_yticks([])
        for sp in ax_mod.spines.values():
            sp.set_edgecolor("#94a3b8")
            sp.set_linewidth(1.3)
        ax_mod.set_title("【構成例 B】沈み込み実装：コア ＋ #04B 枠 ＋ #20 ツインカバー分解図", fontsize=11.5, fontweight="bold", color="#0f172a", pad=7)

        mod_callouts = [
            (33.0, 84.0, 14.5, 97.0, "#20 ホイールカバー (西:基板側)", "#1d3557"),
            (73.0, 77.0, 86.0, 97.0, "#20 ホイールカバー (東:180°反転)", "#1d3557"),
            (28.5, 73.0, 13.5, 82.5, "#07 段付きセンサー基板 + #08 IC", "#1b4332"),
            (38.0, 68.0, 12.5, 67.5, "#16 角度磁石 (径方向)", "#9b2226"),
            (49.5, 70.0, 49.0, 97.0, "#01 カップ型フライホイール", "#1d3557"),
            (63.5, 63.5, 86.5, 82.0, "#02 内蔵9球ハブ + #13 鋼球", "#005f73"),
            (78.5, 55.5, 88.0, 66.5, "#12 ベアリング + #14 軸", "#005f73"),
            (56.5, 42.0, 88.5, 48.0, "#03 キャリッジ (スリム丸耳)", "#1d3557"),
            (66.5, 39.5, 15.5, 49.5, "#18 磁力調整ネジ + #17 磁石", "#9b2226"),
            (34.5, 25.0, 13.5, 29.0, "#15 ヒンジピン (北端軸)", "#005f73"),
            (55.0, 14.0, 49.0, 1.5, "#04B 沈み込みベース枠", "#1d3557"),
            (66.5, 21.0, 88.0, 21.0, "#10 静音スイッチ (南東)", "#1b4332"),
        ]
        for tx, ty, lx, ly, txt, col in mod_callouts:
            ax_mod.annotate(
                txt,
                xy=(tx, ty),
                xytext=(lx, ly),
                ha="center",
                va="center",
                fontsize=7.5,
                fontweight="bold",
                color="#0f172a",
                bbox=dict(boxstyle="round,pad=0.24", fc="#ffffff", ec=col, lw=1.3),
                arrowprops=dict(arrowstyle="-|>", color=col, lw=1.35, shrinkA=0, shrinkB=2),
                zorder=8,
            )

        # =====================================================================
        # Lower Section: 7 Rows x 3 Columns = 21 Individual Part Cards (#01..#20)
        # =====================================================================
        C_CUSTOM = ("#1d3557", "#f1f5f9")
        C_ELEC = ("#1b4332", "#ecfdf5")
        C_MECH = ("#005f73", "#ecfeff")
        C_MAG = ("#9b2226", "#fff1f2")

        cards = [
            ("#01  カップ型フライホイール", rendered["p01"], "数量: 1個 ｜ Ø16.8 × 幅5.46 mm (5.66g / X=0中央揃え)", "JLCCNC (SUS304) : sus304-flywheel.step", C_CUSTOM),
            ("#02  内蔵9球ハブ", rendered["p02"], "数量: 1個 ｜ Ø12.4 × 3.10 mm (#01カップ内部へ完全格納)", "JLC3DP (SLA) : ratchet-hub.step", C_CUSTOM),
            ("#03  キャリッジ (スリム丸耳)", rendered["p03"], "数量: 1個 ｜ 13.77 × 15.87 × 14.24 mm", "JLC3DP (SLA) : wheel-carriage.step", C_CUSTOM),
            ("#04A  オンボードベース枠 [基板上載せ用]", rendered["p04a"], "数量: 1個 ｜ 17.18 × 17.56 × 4.10 mm", "JLC3DP (SLA) : wheel-base-frame.step", C_CUSTOM),
            ("#04B  沈み込みベース枠 [メイン基板組込用]", rendered["p04b"], "任意: 1個 ｜ 23.35 × 23.70 × 10.14 mm (軸Z=-2.0mm)", "JLC3DP (SLA) : wheel-base-frame-sunk.step", C_CUSTOM),
            ("#20  ホイールカバー [ツインスナップ式]", rendered["p20"], "任意: 2個 (180°回転対称の完全共通部品!) ｜ 15.4×6.17×7.23 mm", "JLC3DP (SLA) : wheel-cover.step (エッジ曲面ピラミッド)", C_CUSTOM),
            ("#05  ポッド台座", rendered["p05"], "数量: 1個 ｜ 52.0 × 36.0 × 6.6 mm", "JLC3DP (SLA) : eval-pod-stand.step", C_CUSTOM),
            ("#06  キャリア基板", ASSETS_DIR / "render_pcb_wheel_eval.png", "数量: 1枚 ｜ 48.0 × 32.0 × 板厚1.6 mm", "JLCPCB (Top PCBA) : curcur40-wheel-eval", C_ELEC),
            ("#07  センサー基板 [PCBA実装済・段付き]", ASSETS_DIR / "render_pcb_wheel_sensor.png", "数量: 1枚 ｜ 22×22枠→折って8.8/7.9×8.66 (厚0.8mm)", "JLCPCB (0.8mm Top PCBA) : #08実装済・#20カバー内格納!", C_ELEC),
            ("#08  AS5600 IC [個別購入不要]", rendered["p08"], "PCBA実装済 ｜ U1(C499458)＋C1/C2パスコン", "JLCPCB PCBA : #07の表面へ自動実装済!", C_ELEC),
            ("#09  RP2040-Zero", rendered["p09"], "数量: 1個 ｜ ピンヘッダ未実装タイプ", "通販 : Waveshare RP2040-Zero (USB-C)", C_ELEC),
            ("#10  静音スイッチ", rendered["p10"], "数量: 1個 ｜ 6.2 × 6.2 × 高4.3 mm", "遊舎工房/通販 : Kailh Square Silent (2ピン)", C_ELEC),
            ("#11  センサー4芯線", "CUSTOM_WIRE", "数量: 1式 ｜ AWG30〜34 約60mm × 4本", "通販 : 極細シリコン撚り線 または JST SH線", C_ELEC),
            ("#12  ベアリング [要脱脂]", rendered["p12"], "数量: 2個 ｜ 内径Ø2 × 外径Ø5 × 幅2.0 mm", "通販 : DDL-520 / MR52 オープン形 (★脱脂洗浄)", C_MECH),
            ("#13  ラチェット鋼球", rendered["p13"], "数量: 9個 ｜ 直径 Ø2.00 mm 精密球", "通販 : SUJ2 または SUS440C 磁性鋼球 (セラミック不可)", C_MECH),
            ("#14  回転シャフト", rendered["p14"], "数量: 1本 ｜ Ø2.0 × 長さ 10 mm", "通販 : 非磁性 SUS304/316 平行ピン (ホイール軸)", C_MECH),
            ("#15  ヒンジピン", rendered["p15"], "数量: 1本 ｜ Ø2.0 × 長さ 16〜17 mm", "通販 : 非磁性 SUS304/316 平行ピン (北端揺動軸)", C_MECH),
            ("#16  角度磁石 [径方向着磁]", "CUSTOM_MAG_DIAM", "数量: 1個 ｜ Ø3.0 × 厚0.75〜1.0 mm", "通販 : 径方向2極着磁ネオジム (AS5600用)", C_MAG),
            ("#17  ラチェット磁石 [軸方向]", "CUSTOM_MAG_AXIAL", "数量: 1個 ｜ Ø1.5〜2.0 × 厚1.0〜1.5 mm", "通販 : 通常の軸方向着磁ネオジム (N35等)", C_MAG),
            ("#18  磁力調整ネジ", rendered["p18"], "数量: 1本 ｜ M2 × 長さ 3〜4 mm", "通販 : 非磁性ステンレス M2 イモネジ/小ねじ", C_MAG),
            ("#19  固定M2ネジ ＆ ゴム足", rendered["p19"], "数量: M2×4mmネジ 6本 ＋ ゴム足 4個", "通販 : ベース固定2本＋台座4本 (沈み込み版は3本)", C_MAG),
        ]

        n_cols, n_rows = 3, 7
        left0, bottom0 = 0.020, 0.010
        total_w, total_h = 0.960, 0.706
        gap_x, gap_y = 0.014, 0.009
        card_w = (total_w - gap_x * (n_cols - 1)) / n_cols
        card_h = (total_h - gap_y * (n_rows - 1)) / n_rows

        for idx, (title, src, line1, line2, (hdr_col, foot_bg)) in enumerate(cards):
            r = idx // n_cols
            c = idx % n_cols
            cx = left0 + c * (card_w + gap_x)
            cy = bottom0 + (n_rows - 1 - r) * (card_h + gap_y)

            cax = fig.add_axes([cx, cy, card_w, card_h])
            cax.set_xlim(0, 100)
            cax.set_ylim(0, 100)
            cax.set_xticks([])
            cax.set_yticks([])
            for sp in cax.spines.values():
                sp.set_edgecolor(hdr_col)
                sp.set_linewidth(1.35)

            cax.add_patch(patches.Rectangle((0, 81), 100, 19, fc=hdr_col, ec="none", zorder=3))
            cax.text(3.5, 90.5, title, ha="left", va="center", fontsize=9.8, fontweight="bold", color="white", zorder=4)

            cax.add_patch(patches.Rectangle((0, 0), 100, 24, fc=foot_bg, ec="none", zorder=3))
            cax.plot([0, 100], [24, 24], color="#cbd5e1", lw=0.8, zorder=4)
            cax.text(50.0, 15.8, line1, ha="center", va="center", fontsize=7.8, fontweight="bold", color="#0f172a", zorder=4)
            cax.text(50.0, 6.4, line2, ha="center", va="center", fontsize=7.1, color="#334155", zorder=4)

            vax = fig.add_axes([cx + 0.004, cy + card_h * 0.242, card_w - 0.008, card_h * 0.565])
            if src == "CUSTOM_WIRE":
                _draw_wire_card(vax)
            elif src == "CUSTOM_MAG_DIAM":
                _draw_magnet_card(vax, diametric=True)
            elif src == "CUSTOM_MAG_AXIAL":
                _draw_magnet_card(vax, diametric=False)
            else:
                im_arr, bg_col = _autocrop_pil(Path(src), pad_frac=0.07)
                ih, iw, _ = im_arr.shape
                vax.set_facecolor(bg_col)
                box_aspect = (card_w * 16.8) / (card_h * 0.565 * 25.4)
                img_aspect = iw / max(1.0, float(ih))
                if img_aspect >= box_aspect:
                    disp_w = 100.0
                    disp_h = 100.0 * (box_aspect / img_aspect)
                else:
                    disp_h = 100.0
                    disp_w = 100.0 * (img_aspect / box_aspect)
                x0 = 50.0 - disp_w / 2.0
                y0 = 50.0 - disp_h / 2.0
                vax.imshow(im_arr, extent=[x0, x0 + disp_w, y0, y0 + disp_h], aspect="auto", zorder=2)
                if title.startswith("#14 "):
                    vax.text(72, 82, "短い方: 10mm", ha="center", va="center", fontsize=7.0, fontweight="bold", color="#005f73",
                             bbox=dict(boxstyle="round,pad=0.2", fc="#ffffff", ec="#005f73", lw=0.9), zorder=5)
                elif title.startswith("#15 "):
                    vax.text(72, 82, "長い方: 16〜17mm", ha="center", va="center", fontsize=7.0, fontweight="bold", color="#005f73",
                             bbox=dict(boxstyle="round,pad=0.2", fc="#ffffff", ec="#005f73", lw=0.9), zorder=5)
                vax.set_xlim(0, 100)
                vax.set_ylim(0, 100)
                vax.axis("off")

        out_guide = ASSETS_DIR / "inertia_wheel_parts_guide.png"
        fig.savefig(out_guide, dpi=160)
        plt.close(fig)
        print(f"Saved {out_guide}")


def main():
    render_pcb_and_step_previews()
    _draw_spec_diagram()
    generate_parts_guide()


if __name__ == "__main__":
    main()
