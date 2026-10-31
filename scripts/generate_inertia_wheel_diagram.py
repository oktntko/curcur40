# -*- coding: utf-8 -*-
"""
Render 3D CAD preview images and generate engineering cross-section, visual BOM,
and kid-friendly mechanism guide diagrams for the Under-Plate 1-Piece Integral-Shaft
Passive Magnetic Inertia Wheel (`curcur40-inertia-wheel`).

Outputs into `docs/assets/`:
  1. render_inertia_wheel_flywheel.png
  2. render_inertia_wheel_module.png
  3. render_curcur40_right_wheel.png
  4. passive_inertia_wheel_spec.png
  5. inertia_wheel_parts_guide.png
  6. inertia_wheel_easy_guide.png
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
UVX_EXE = Path(os.path.expandvars(r"%USERPROFILE%\.local\bin\uvx.exe"))

plt.rcParams["font.sans-serif"] = [
    "Meiryo",
    "Yu Gothic",
    "MS Gothic",
    "DejaVu Sans",
    "Arial",
]
plt.rcParams["axes.unicode_minus"] = False


def render_step_previews():
    """Render 3D CAD STEP previews for the wheel flywheel, sub-assembly, and right keyboard integration."""
    parts_dir = WORKSPACE / "cases" / "inertia_wheel"
    asm_dir = WORKSPACE / "cases" / "assemblies"
    step_jobs = [
        {
            "input": str(parts_dir / "steel-flywheel.step"),
            "outputs": [str(ASSETS_DIR / "render_inertia_wheel_flywheel.png")],
            "camera": "iso",
            "display": "shaded",
        },
        {
            "input": str(asm_dir / "inertia-wheel-assembly.step"),
            "outputs": [str(ASSETS_DIR / "render_inertia_wheel_module.png")],
            "camera": "iso",
            "display": "parts",
        },
        {
            "input": str(asm_dir / "curcur40-right-wheel-assembly.step"),
            "outputs": [str(ASSETS_DIR / "render_curcur40_right_wheel.png")],
            "camera": "iso",
            "display": "parts",
        },
    ]
    with tempfile.TemporaryDirectory() as tmp_s:
        job_path = Path(tmp_s) / "preview_jobs.json"
        job_path.write_text(json.dumps({"jobs": step_jobs}, ensure_ascii=False, indent=2), encoding="utf-8")
        print("Rendering 3 STEP previews into docs/assets/...")
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
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18.4, 8.8), dpi=200)
    fig.patch.set_facecolor("#ffffff")
    fig.suptitle(
        "アンダープレート一体軸パッシブ磁気慣性ホイール 内部断面・機構図（幅6.50mm大慣性・#01〜#12全番号明記・6自由度ロック構造）",
        fontsize=12.6,
        fontweight="bold",
        y=0.975,
        color="#1a1a1a",
    )

    z_axle = -6.90  # Global Z of wheel rotary axis (wheel OD Ø22.00 mm -> top Z = +4.10 mm, bottom Z = -17.90 mm)

    # =========================================================================
    # Panel 1: X–Z Front Cross-Section along Axle (Y_pcb = -2.00 mm)
    # Local u = x_pcb - 14.2875 mm (+u = East, -u = West; wheel aligned with south key rEXSW2!)
    # =========================================================================
    ax1.set_title("① 正面断面図 (X–Z 断面：幅6.5mm一体軸ホイール × #02マグネットホルダー × Cクリップ連結シーソークリック)", fontsize=9.9, fontweight="bold", pad=10)
    ax1.set_xlim(-21.2, 11.6)
    ax1.set_ylim(-23.2, 8.8)
    ax1.set_aspect("equal")
    ax1.set_facecolor("#f8f9fa")
    ax1.grid(True, linestyle=":", linewidth=0.5, color="#cccccc")
    ax1.set_xlabel("ホイール軸方向ローカル座標 u [mm]（u = 0.00 がホイール中心 / 西 -u 側が #02・センサー・スイッチ）", fontsize=8.7)
    ax1.set_ylabel("curcur40 グローバル Z 座標 [mm]（ケース上縁 = 0.00 / プレート上面 = -2.00）", fontsize=8.7)

    ax1.axvline(0.0, color="#64748b", linestyle="-.", linewidth=0.9, zorder=1)
    ax1.axhline(3.60, color="#0077b6", linestyle=":", linewidth=1.1, zorder=2)
    ax1.text(-20.8, 3.85, "隣接 Choc V2 キーキャップ天面 Z = +3.60 mm", fontsize=6.8, fontweight="bold", color="#0077b6")

    # #12 Top Plate (-3.60..-2.00) with 7.70 mm slot (u in [-3.85, +3.85])
    ax1.add_patch(patches.Rectangle((-20.6, -3.60), 16.75, 1.60, fc="#3a7ca5", ec="#16425b", lw=1.2, zorder=3))
    ax1.add_patch(patches.Rectangle((3.85, -3.60), 7.20, 1.60, fc="#3a7ca5", ec="#16425b", lw=1.2, zorder=3))
    ax1.text(-9.9, -2.80, "#12 右プレート (7.7×22.0mm窓)", ha="center", va="center", fontsize=6.1, color="white", fontweight="bold", zorder=4)

    # Right Main PCB (-5.80..-4.20) with cross cutout (u in [-9.45, +7.05] open at v = 0)
    ax1.add_patch(patches.Rectangle((-20.6, -5.80), 11.15, 1.60, fc="#2a9d8f", ec="#1b4332", lw=1.2, zorder=3))
    ax1.add_patch(patches.Rectangle((7.05, -5.80), 4.00, 1.60, fc="#2a9d8f", ec="#1b4332", lw=1.2, zorder=3))
    ax1.text(-15.0, -5.00, "右メイン基板 (-5.8〜-4.2)", ha="center", va="center", fontsize=6.2, color="white", fontweight="bold", zorder=4)

    # Sealed Tilted Case Floor (~Z = -21.8 to -19.2 in wheel region — 100% hole-free)
    ax1.add_patch(patches.Polygon([[-20.6, -22.5], [11.0, -21.1], [11.0, -19.1], [-20.6, -20.5]],
                                  closed=True, fc="#495057", ec="#212529", lw=1.1, alpha=0.85, zorder=2))
    ax1.text(-4.5, -21.2, "100% 密閉・穴なし傾斜ボトムケース床（肉厚 2.40 mm）", ha="center", va="center", fontsize=6.7, color="white", fontweight="bold", zorder=3)

    # #04 Wheel Cradle (static under-PCB bracket: Captive Ø3.06 C-clip snap-in hinge around u = -8.12, Z = -8.15 + West rest-stop bridge u in [-11.65, -10.52])
    ax1.add_patch(patches.Rectangle((-11.65, -10.80), 6.10, 5.00, fc="#cbd5e1", ec="#334155", lw=1.0, alpha=0.68, linestyle="--", zorder=2))
    ax1.add_patch(patches.Rectangle((-11.65, -13.40), 1.13, 7.60, fc="#94a3b8", ec="#334155", lw=1.0, zorder=3))

    # #03 Wheel Rocker (West ear [-6.62, -3.55], East ear [+3.55, +6.62], C-clip top Z = -4.55, bottom stirrup [-19.70, -18.35],
    # West striker arm [-17.65, -6.62] at Z in [-12.00, -10.30] + integral West Keeper Tab [-10.50, -9.62] rising to Z = -8.05)
    rocker_poly = patches.Polygon(
        [
            [-6.62, -19.70], [6.62, -19.70], [6.62, -4.55], [3.55, -4.55],
            [3.55, -18.35], [-3.55, -18.35], [-3.55, -4.55], [-6.62, -4.55],
        ],
        closed=True, fc="#dee2e6", ec="#495057", lw=1.1, zorder=4,
    )
    ax1.add_patch(rocker_poly)
    ax1.add_patch(patches.Rectangle((-17.65, -12.00), 11.03, 1.70, fc="#dee2e6", ec="#495057", lw=1.1, zorder=4))
    # Integral West Keeper Tab on #03 (u in [-10.50, -9.62], Z in [-10.30, -8.05])
    ax1.add_patch(patches.Rectangle((-10.50, -10.30), 0.88, 2.25, fc="#adb5bd", ec="#212529", lw=1.15, zorder=6))
    # Integral Ø3.00 mm Pivot Trunnion at (u = -8.12, Z = -8.15 -> snapped into #04 Ø3.06 C-clip saddle!)
    ax1.add_patch(patches.Circle((-8.12, -8.15), 1.50, fc="#f8fafc", ec="#0f172a", lw=1.4, zorder=7))
    ax1.plot([-8.12], [-8.15], marker="+", color="#0f172a", markersize=6, zorder=8)

    # #01 1-Piece Integral-Shaft 45# Steel Flywheel:
    # Rim u in [-3.25, +3.25], Z in [-17.90, +4.10]; Integral Ø2.90mm shoulders [-3.45, +3.45]; Integral Ø1.98mm shaft [-7.98, +5.72]
    ax1.add_patch(patches.Rectangle((-7.98, z_axle - 0.99), 13.70, 1.98, fc="#e2e8f0", ec="#334155", lw=1.1, zorder=6))
    ax1.add_patch(patches.Rectangle((-3.45, z_axle - 1.45), 6.90, 2.90, fc="#cbd5e1", ec="#334155", lw=1.0, zorder=6))
    ax1.add_patch(patches.Rectangle((-3.25, z_axle - 11.00), 6.50, 22.00, fc="#b8c4d0", ec="#1e293b", lw=1.5, zorder=7))
    ax1.text(0.0, -1.0, "#01 一体軸\n45#鋼ホイール\nØ22.0×6.50\n(19.31g)", ha="center", va="center", fontsize=6.7, fontweight="bold", color="#0f172a", zorder=8)

    # #07 2x NMB DDL-520ZZ Bearings (Ø2 x Ø5 x 2.30 mm at [-5.75, -3.45] & [+3.45, +5.75])
    for bu in (-5.75, 3.45):
        ax1.add_patch(patches.Rectangle((bu, z_axle - 2.50), 2.30, 5.00, fc="#ffffff", ec="#0077b6", lw=1.2, zorder=5))

    # #02 PA12 Magnet Holder (u in [-9.05, -7.00], Ø5.72 mm) + #08 D4x1mm Diametric Magnet (u in [-9.02, -8.02])
    ax1.add_patch(patches.Rectangle((-9.05, z_axle - 2.86), 2.05, 5.72, fc="#2ec4b6", ec="#0f766e", lw=1.35, zorder=6))
    ax1.add_patch(patches.Rectangle((-9.02, z_axle), 1.00, 2.00, fc="#ef4444", ec="#7f1d1d", lw=1.0, zorder=7))
    ax1.add_patch(patches.Rectangle((-9.02, z_axle - 2.00), 1.00, 2.00, fc="#3b82f6", ec="#1e3a8a", lw=1.0, zorder=7))

    # #05 Onboard rU6: TMAG5273A1QDBVR 3D Hall Sensor on Main PCB B.Cu (u = -11.28, Z = -6.95..-5.80)
    ax1.add_patch(patches.Rectangle((-12.13, -6.95), 1.70, 1.15, fc="#1e293b", ec="#000000", lw=1.0, zorder=6))
    ax1.text(-11.28, -6.38, "#05 rU6", ha="center", va="center", fontsize=5.2, color="white", fontweight="bold", zorder=7)

    # #06 Onboard rEXSW1: Kailh Square Silent Switch on Main PCB B.Cu (u = -16.30, body Z = -9.15..-5.80, plunger Z = -10.10..-9.15)
    ax1.add_patch(patches.Rectangle((-19.40, -9.15), 6.20, 3.35, fc="#f4a261", ec="#9c4100", lw=1.2, zorder=5))
    ax1.add_patch(patches.Rectangle((-17.80, -10.10), 3.00, 0.95, fc="#e63946", ec="#6a040f", lw=1.0, zorder=6))

    # Callouts on Panel 1 — Explicitly labeling #01, #02, #03, #04, #05, #06, #07, #08, #12!
    ax1.annotate("#01 1ピースCNC一体軸ホイール (幅6.50mm)\n質量 19.31g・頂点 Z=+4.10mm（キー上+0.50mm）\n段付き肩一体＝シム不要（#12 7.7×22.0mm窓）",
                 xy=(0.0, 4.10), xytext=(4.8, 6.55), ha="center", va="center",
                 arrowprops=dict(arrowstyle="->", color="#1e293b", lw=1.15),
                 fontsize=6.2, fontweight="bold", color="#0f172a",
                 bbox=dict(boxstyle="round,pad=0.20", fc="#f1f5f9", ec="#475569", lw=0.9), zorder=10)

    ax1.annotate("★ #02 マグネットホルダー (PA12キャップ)\n＋ #08 D4×1mm径方向磁石\n• #01西端Dカット軸にタイト圧入して一体回転\n• 西側は #03 キーパータブで抜け止め（接着ゼロ!）",
                 xy=(-8.05, -4.04), xytext=(-6.4, 6.55), ha="center", va="center",
                 arrowprops=dict(arrowstyle="->", color="#0f766e", lw=1.3),
                 fontsize=6.1, fontweight="bold", color="#0f766e",
                 bbox=dict(boxstyle="round,pad=0.20", fc="#ccfbf1", ec="#0f766e", lw=1.05), zorder=10)

    ax1.annotate("#05 rU6: TMAG5273\n(右メイン基板 B.Cu 自動実装済)\n横から(Bx,Bz)磁界を非接触検出!",
                 xy=(-11.28, -5.80), xytext=(-16.8, 6.55), ha="center", va="center",
                 arrowprops=dict(arrowstyle="->", color="#15803d", lw=1.15),
                 fontsize=6.1, fontweight="bold", color="#14532d",
                 bbox=dict(boxstyle="round,pad=0.20", fc="#dcfce7", ec="#15803d", lw=0.9), zorder=10)

    ax1.annotate("#06 rEXSW1 静音SW（B.Cu直付け）\n#03 シーソーロッカー（Ø3.0トラニオン支点\n＆西キーパータブ）の1:1てこで約70gfクリック",
                 xy=(-16.30, -10.10), xytext=(-15.5, -16.8), ha="center", va="center",
                 arrowprops=dict(arrowstyle="->", color="#9c4100", lw=1.15),
                 fontsize=6.1, fontweight="bold", color="#7f2704",
                 bbox=dict(boxstyle="round,pad=0.20", fc="#fff3cd", ec="#d97706", lw=0.85), zorder=10)

    ax1.annotate("#04 アンダーPCBクレードル\nØ3.06 Cクリップ軸受(開口2.66mm)へ\nパチン連結! 単体で抜けず西受け台で静止保持",
                 xy=(-11.10, -13.40), xytext=(-6.4, -17.1), ha="center", va="center",
                 arrowprops=dict(arrowstyle="->", color="#334155", lw=1.1),
                 fontsize=6.0, fontweight="bold", color="#1e293b",
                 bbox=dict(boxstyle="round,pad=0.20", fc="#e2e8f0", ec="#475569", lw=0.85), zorder=10)

    ax1.annotate("#07 DDL-520ZZ×2 (脱脂)\n#03 Cクリップ軸受座(開口4.56mm)\nへスナップインし上抜け完全防止!",
                 xy=(4.60, -6.90), xytext=(7.2, -13.2), ha="center", va="center",
                 arrowprops=dict(arrowstyle="->", color="#0077b6", lw=1.1),
                 fontsize=6.1, fontweight="bold", color="#023e8a",
                 bbox=dict(boxstyle="round,pad=0.20", fc="#e0f2fe", ec="#0077b6", lw=0.85), zorder=10)

    # =========================================================================
    # Panel 2: Y–Z Side Cross-Section along Wheel Plane (u = 0.00 mm)
    # Local v = -(y_pcb + 2.00 mm) (+v = North, -v = South)
    # =========================================================================
    ax2.set_title("② 側面機構図 (Y–Z 断面：#09/#10/#11 24溝磁気デテント調整 × #04 クレードル締結)", fontsize=10.2, fontweight="bold", pad=10)
    ax2.set_xlim(-22.0, 17.0)
    ax2.set_ylim(-23.2, 8.8)
    ax2.set_aspect("equal")
    ax2.set_facecolor("#f8f9fa")
    ax2.grid(True, linestyle=":", linewidth=0.5, color="#cccccc")
    ax2.set_xlabel("南北ローカル座標 v [mm]（南 -v 側：#09/#10/#11 接着不要ラチェット磁力調整 ／ 北 +v 側）", fontsize=8.7)
    ax2.set_ylabel("curcur40 グローバル Z 座標 [mm]", fontsize=8.7)

    ax2.axhline(3.60, color="#0077b6", linestyle=":", linewidth=1.1, zorder=2)

    # #12 Top Plate (-3.60..-2.00, 22.00 mm window v in [-11.00, +11.00])
    ax2.add_patch(patches.Rectangle((-21.5, -3.60), 10.50, 1.60, fc="#3a7ca5", ec="#16425b", lw=1.2, zorder=3))
    ax2.add_patch(patches.Rectangle((11.00, -3.60), 5.50, 1.60, fc="#3a7ca5", ec="#16425b", lw=1.2, zorder=3))

    # Main PCB (-5.80..-4.20, 22.50 mm window v in [-11.50, +11.00])
    ax2.add_patch(patches.Rectangle((-21.5, -5.80), 10.00, 1.60, fc="#2a9d8f", ec="#1b4332", lw=1.2, zorder=3))
    ax2.add_patch(patches.Rectangle((11.00, -5.80), 5.50, 1.60, fc="#2a9d8f", ec="#1b4332", lw=1.2, zorder=3))

    # Sealed Case Floor
    ax2.add_patch(patches.Rectangle((-21.5, -22.0), 38.0, 2.2, fc="#495057", ec="#212529", lw=1.1, alpha=0.85, zorder=2))

    # Adjacent South Keycap (rEXSW2 at x_pcb = 14.2875, y_pcb = +19.05 -> v = -21.05, 100% aligned with wheel center!)
    ax2.add_patch(patches.Rectangle((-21.3, -0.80), 8.80, 4.40, fc="#e9ecef", ec="#495057", lw=1.2, zorder=4))
    ax2.text(-16.9, 1.40, "南隣接キー\nrEXSW2\n(X軸一致!)", ha="center", va="center", fontsize=6.4, fontweight="bold", color="#343a40", zorder=5)

    # Projected #04 Cradle Boss (WC1/WC2) + #10 Brass Insert (M2xL3.0) + #11 Sub-Flush Top-Down M2x6.0mm Screw
    ax2.add_patch(patches.Rectangle((11.6, -9.70), 4.2, 3.90, fc="#cbd5e1", ec="#334155", lw=1.1, zorder=3))
    ax2.add_patch(patches.Rectangle((12.9, -8.80), 1.6, 3.00, fc="#e9c46a", ec="#7f5539", lw=1.0, hatch="///", zorder=4))
    ax2.add_patch(patches.Rectangle((12.3, -4.20), 2.8, 1.15, fc="#adb5bd", ec="#212529", lw=1.0, zorder=6))
    ax2.add_patch(patches.Rectangle((13.1, -10.20), 1.2, 6.00, fc="#ced4da", ec="#212529", lw=0.9, zorder=5))

    # #01 Ø22.00 x 6.50 mm 24-Flute Ferromagnetic 45# Steel Wheel (centered at v = 0.00, Z = -6.90)
    ax2.add_patch(patches.Circle((0.0, z_axle), 11.00, fc="#b8c4d0", ec="#1e293b", lw=1.6, alpha=0.85, zorder=5))
    for i in range(24):
        ang = np.deg2rad(i * 15.0)
        ax2.plot([10.50 * np.cos(ang), 11.00 * np.cos(ang)],
                 [z_axle + 10.50 * np.sin(ang), z_axle + 11.00 * np.sin(ang)],
                 color="#1e293b", lw=1.0, zorder=6)
    ax2.add_patch(patches.Circle((0.0, z_axle), 1.45, fc="#cbd5e1", ec="#334155", lw=1.0, zorder=6))
    ax2.add_patch(patches.Circle((0.0, z_axle), 0.99, fc="#f8fafc", ec="#0f172a", lw=1.2, zorder=7))
    ax2.text(0.0, -5.0, "#01 Ø22.0×幅6.50mm 45#鋼ホイール\n外周24フルート溝 (15°ピッチ)\n質量 19.31g・J ≈ 1160 g·mm² 大慣性!",
             ha="center", va="center", fontsize=6.6, fontweight="bold", color="#0f172a",
             bbox=dict(boxstyle="round,pad=0.20", fc="#f8fafc", ec="#475569", lw=0.8, alpha=0.92), zorder=8)

    # #03 Rocker Bottom Bridge & South Glue-Free Magnetic Detent Boss (v in [-16.40, -11.40], bore at Z = -11.30 mm)
    rocker_yz = patches.Polygon(
        [
            [-16.40, -19.70], [3.40, -19.70], [3.40, -18.35],
            [-11.40, -18.35], [-11.40, -8.50], [-16.40, -8.50],
        ],
        closed=True, fc="#dee2e6", ec="#495057", lw=1.2, zorder=4,
    )
    ax2.add_patch(rocker_yz)
    z_det = -11.30
    ax2.add_patch(patches.Rectangle((-16.40, z_det - 1.425), 5.00, 2.85, fc="#ffffff", ec="#495057", lw=0.9, zorder=5))
    ax2.add_patch(patches.Rectangle((-16.40, z_det - 1.55), 3.00, 3.10, fc="#e9c46a", ec="#7f5539", lw=1.0, hatch="///", zorder=6))
    ax2.add_patch(patches.Rectangle((-19.10, z_det - 0.98), 6.00, 1.96, fc="#ced4da", ec="#212529", lw=1.0, hatch="//", zorder=7))
    ax2.add_patch(patches.Rectangle((-20.30, z_det - 1.90), 1.20, 3.80, fc="#adb5bd", ec="#212529", lw=1.1, zorder=7))
    ax2.add_patch(patches.Rectangle((-13.08, z_det - 1.00), 2.00, 2.00, fc="#e63946", ec="#6a040f", lw=1.2, zorder=8))

    # Callouts on Panel 2 — Explicitly labeling #03, #04, #09, #10, #11, #12!
    ax2.annotate("接着剤ゼロ! 磁気デテント無段階調整機構\n• #03 ロッカー南ボス ＋ #10 真鍮インサート\n• #11 鉄製M2×6mmネジ先端に #09 Ø2×2mm磁石が自己吸着!\n• #01 24溝とのギャップ加減でフリースピン〜24ノッチ調整",
                 xy=(-12.1, z_det), xytext=(-13.8, -16.2), ha="center", va="center",
                 arrowprops=dict(arrowstyle="->", color="#d90429", lw=1.2),
                 fontsize=6.2, fontweight="bold", color="#9d0208",
                 bbox=dict(boxstyle="round,pad=0.22", fc="#ffe5ec", ec="#d90429", lw=0.9), zorder=10)

    ax2.annotate("#04 クレードル WC1/WC2 締結（#10 ＋ #11 M2×6mm）\n• 全12箇所 プレート Ø4.4mm 穴でネジ頭は完全沈み込み!\n• メイン基板を直接ネジ固定・プレートはスイッチ嵌合保持",
                 xy=(13.7, -4.20), xytext=(5.2, 6.20), ha="center", va="center",
                 arrowprops=dict(arrowstyle="->", color="#1d3557", lw=1.15),
                 fontsize=6.3, fontweight="bold", color="#1d3557",
                 bbox=dict(boxstyle="round,pad=0.22", fc="#e0f2fe", ec="#1d3557", lw=0.9), zorder=10)

    plt.tight_layout(rect=[0, 0.01, 1, 0.94])
    out_path = ASSETS_DIR / "passive_inertia_wheel_spec.png"
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    print(f"Saved {out_path}")


def _draw_easy_guide_diagram():
    """
    Generate `docs/assets/inertia_wheel_easy_guide.png`:
    Kid-friendly 3-panel illustrated guide explaining:
      1. Fast-scroll inertia spin & exact location/role of `#02 Magnet Holder`
      2. Magnetic 24-notch detent adjustment without springs or wear
      3. Playground seesaw lever pressing backside silent switch `rEXSW1` for middle click
    """
    fig = plt.figure(figsize=(17.0, 17.6), dpi=180)
    fig.patch.set_facecolor("#fffdf9")
    fig.suptitle(
        "小学生でもわかる！ curcur40 高速スクロールホイールの「3つのしくみ」と #02 の場所",
        fontsize=15.0,
        fontweight="bold",
        y=0.982,
        color="#1e293b",
    )
    fig.text(
        0.5,
        0.957,
        "バネも・ボンドも・細い電線もゼロ！「鉄の重さ」「磁石の力」「公園のシーソー」の3つだけで動くシンプルなしくみ図鑑",
        ha="center",
        va="center",
        fontsize=10.2,
        fontweight="bold",
        color="#475569",
    )

    gs = fig.add_gridspec(
        nrows=3,
        ncols=2,
        width_ratios=[1.22, 1.0],
        hspace=0.24,
        wspace=0.08,
        left=0.03,
        right=0.97,
        top=0.932,
        bottom=0.022,
    )

    def style_card(ax, bg="#ffffff", ec="#cbd5e1"):
        ax.set_facecolor(bg)
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_edgecolor(ec)
            sp.set_linewidth(1.8)

    # =========================================================================
    # ROW 1: Fast Scroll + #02 Magnet Holder Location ("Heavy Iron Top + Air Compass")
    # =========================================================================
    ax1_l = fig.add_subplot(gs[0, 0])
    style_card(ax1_l, bg="#f0fdfa", ec="#0d9488")
    ax1_l.set_xlim(-14.8, 9.2)
    ax1_l.set_ylim(-6.8, 7.2)
    ax1_l.set_aspect("equal")
    ax1_l.set_title(
        "しくみ① 高速スクロールと「#02 マグネットホルダー」の場所（正面から見た拡大図）",
        fontsize=11.0,
        fontweight="bold",
        color="#0f766e",
        loc="left",
        pad=8,
    )

    # Right Main PCB ceiling & Top Plate
    ax1_l.add_patch(patches.Rectangle((-14.3, 4.3), 23.0, 0.9, fc="#dbeafe", ec="#3b82f6", lw=1.0, alpha=0.6))
    ax1_l.add_patch(patches.Rectangle((-14.3, 4.3), 7.8, 0.9, fc="#3a7ca5", ec="#16425b", lw=1.2))
    ax1_l.add_patch(patches.Rectangle((4.2, 4.3), 4.5, 0.9, fc="#3a7ca5", ec="#16425b", lw=1.2))
    ax1_l.text(-10.4, 4.75, "#12 トッププレート", ha="center", va="center", fontsize=7.5, color="white", fontweight="bold")

    ax1_l.add_patch(patches.Rectangle((-14.3, 2.3), 5.3, 1.1, fc="#2a9d8f", ec="#1b4332", lw=1.2))
    ax1_l.add_patch(patches.Rectangle((6.2, 2.3), 2.5, 1.1, fc="#2a9d8f", ec="#1b4332", lw=1.2))
    ax1_l.text(-11.6, 2.85, "右メイン基板", ha="center", va="center", fontsize=7.5, color="white", fontweight="bold")

    # #05 Air Compass Sensor rU6 under PCB
    ax1_l.add_patch(patches.FancyBboxPatch((-12.8, 1.0), 2.5, 1.25, boxstyle="round,pad=0.08", fc="#1e293b", ec="#0f172a", lw=1.3, zorder=6))
    ax1_l.text(-11.55, 1.62, "#05 空中コンパス\n(磁気センサー rU6)", ha="center", va="center", fontsize=6.8, color="#38bdf8", fontweight="bold", zorder=7)

    # Magnetic field waves from #08 to #05
    for r_arc in (1.3, 2.1, 2.9):
        arc = patches.Arc((-7.7, 0.0), r_arc * 2, r_arc * 1.8, theta1=115, theta2=195, color="#ec4899", lw=1.6, linestyle="--", zorder=5)
        ax1_l.add_patch(arc)
    ax1_l.text(-11.3, -0.55, "空中で磁力の向きを\n非接触キャッチ！\n(こすれゼロ！)", ha="center", va="center", fontsize=7.4, fontweight="bold", color="#be185d",
               bbox=dict(boxstyle="round,pad=0.22", fc="#fdf2f8", ec="#ec4899", lw=1.0), zorder=8)

    # #03 Rocker ears + West Keeper Tab
    ax1_l.add_patch(patches.Rectangle((-5.4, -3.5), 2.2, 6.2, fc="#e2e8f0", ec="#475569", lw=1.2, zorder=3))
    ax1_l.add_patch(patches.Rectangle((3.6, -3.5), 2.2, 6.2, fc="#e2e8f0", ec="#475569", lw=1.2, zorder=3))
    ax1_l.add_patch(patches.Rectangle((-10.2, -4.6), 16.0, 1.1, fc="#e2e8f0", ec="#475569", lw=1.2, zorder=3))
    # Keeper tab right to the left of #02/#08!
    ax1_l.add_patch(patches.Rectangle((-9.4, -3.5), 0.85, 2.7, fc="#94a3b8", ec="#1e293b", lw=1.4, zorder=6))
    ax1_l.annotate("#03 抜け止め壁\n(キーパータブ)\n左へ抜けるのを\n通せんぼ！",
                   xy=(-8.98, -2.2), xytext=(-12.1, -4.5), ha="center", va="center",
                   arrowprops=dict(arrowstyle="->", color="#1e293b", lw=1.3),
                   fontsize=7.2, fontweight="bold", color="#1e293b",
                   bbox=dict(boxstyle="round,pad=0.22", fc="#f1f5f9", ec="#475569", lw=1.0), zorder=9)

    # #07 Bearings (West & East)
    for bx in (-5.2, 3.8):
        ax1_l.add_patch(patches.Rectangle((bx, -2.3), 1.8, 4.6, fc="#ffffff", ec="#0284c7", lw=1.5, zorder=5))
    ax1_l.annotate("#07 ベアリング×2\n(Cクリップでパチン固定)",
                   xy=(4.7, -2.3), xytext=(6.2, -5.5), ha="center", va="center",
                   arrowprops=dict(arrowstyle="->", color="#0284c7", lw=1.3),
                   fontsize=6.9, fontweight="bold", color="#0369a1",
                   bbox=dict(boxstyle="round,pad=0.20", fc="#e0f2fe", ec="#0284c7", lw=1.0), zorder=9)

    # #01 Heavy Steel Wheel + Integral Axle
    ax1_l.add_patch(patches.Rectangle((-7.0, -0.9), 13.0, 1.8, fc="#cbd5e1", ec="#334155", lw=1.4, zorder=6))
    ax1_l.add_patch(patches.FancyBboxPatch((-3.1, -5.8), 6.2, 11.8, boxstyle="round,pad=0.12", fc="#94a3b8", ec="#0f172a", lw=2.0, zorder=7))
    ax1_l.text(0.0, 0.2, "#01 鉄のコマ\n(一体軸ホイール)\n\n幅 6.50 mm!\n重さ 19.3 g!\n(10円玉4枚以上)", ha="center", va="center", fontsize=8.3, fontweight="bold", color="#0f172a",
               bbox=dict(boxstyle="round,pad=0.25", fc="#f8fafc", ec="#334155", lw=1.1), zorder=8)

    # #02 Magnet Holder Cap (Bright Teal) + #08 Red/Blue Magnet!
    ax1_l.add_patch(patches.FancyBboxPatch((-8.2, -2.55), 2.1, 5.1, boxstyle="round,pad=0.06", fc="#14b8a6", ec="#115e59", lw=1.8, zorder=7))
    ax1_l.add_patch(patches.Rectangle((-8.15, 0.0), 1.05, 1.85, fc="#ef4444", ec="#7f1d1d", lw=1.2, zorder=8))
    ax1_l.add_patch(patches.Rectangle((-8.15, -1.85), 1.05, 1.85, fc="#3b82f6", ec="#1e3a8a", lw=1.2, zorder=8))
    ax1_l.text(-7.62, 0.92, "N", ha="center", va="center", fontsize=7.5, fontweight="bold", color="white", zorder=9)
    ax1_l.text(-7.62, -0.92, "S", ha="center", va="center", fontsize=7.5, fontweight="bold", color="white", zorder=9)

    ax1_l.annotate("★ここが #02 マグネットホルダー！\n鉄の軸の左はし(Dカット)に刺さって\n#08 赤青磁石を持つ緑のキャップ！",
                   xy=(-7.15, 2.55), xytext=(-5.6, 5.85), ha="center", va="center",
                   arrowprops=dict(arrowstyle="->", color="#0f766e", lw=1.8),
                   fontsize=7.7, fontweight="bold", color="#134e4a",
                   bbox=dict(boxstyle="round,pad=0.26", fc="#99f6e4", ec="#0f766e", lw=1.4), zorder=10)

    ax1_r = fig.add_subplot(gs[0, 1])
    style_card(ax1_r, bg="#ffffff", ec="#0d9488")
    ax1_r.text(
        0.04,
        0.93,
        "【小学生でもわかる！高速スクロール 3つのひみつ】",
        transform=ax1_r.transAxes,
        fontsize=10.8,
        fontweight="bold",
        color="#0f766e",
        va="top",
    )
    ax1_r.text(
        0.04,
        0.79,
        "① なぜ一度はじくと「シューーッ！」と長く回るの？\n"
        "   軽いプラスチックではなく、幅 6.5mm・重さ 19.3g（10円玉4枚分以上！）の\n"
        "   ズッシリ重い「#01 鉄のコマ」を、2個のミニベアリング(#07)で支えているから！\n"
        "   自転車の車輪と同じで、はじくと何秒も回り続け、指で触れればピタッと止まります。\n\n"
        "② 「#02 マグネットホルダー」はどこで何をしているの？\n"
        "   #01 鉄のコマの軸の左はし（かまぼこ型のDカット軸）にスポッと刺さっている\n"
        "   小さなキャップが #02 です！中に「#08 赤青2極磁石」を入れて軸と一緒に回します。\n"
        "   右は軸の段差、左は #03 の「抜け止め壁」に挟まれるのでボンドなしでも絶対抜けません！\n\n"
        "③ どうやって回転を読み取っているの？（こすれゼロ！）\n"
        "   基板の裏についた「#05 空中コンパス (rU6)」が、空中でさわらずに #08 磁石の\n"
        "   N極・S極の向きを毎秒約1,000回キャッチ！部品どうしが一切こすれないから超高速！",
        transform=ax1_r.transAxes,
        fontsize=8.65,
        fontweight="bold",
        color="#1e293b",
        va="top",
        linespacing=1.46,
    )

    # =========================================================================
    # ROW 2: Notch Adjustment ("24 Iron Hills + Magnet Screw Distance Play")
    # =========================================================================
    ax2_l = fig.add_subplot(gs[1, 0])
    style_card(ax2_l, bg="#fffbeb", ec="#d97706")
    ax2_l.set_xlim(-12.5, 12.5)
    ax2_l.set_ylim(-6.5, 7.0)
    ax2_l.set_aspect("equal")
    ax2_l.set_title(
        "しくみ② カリカリ感（ノッチ）調整のしくみ（横から見た拡大図）",
        fontsize=11.0,
        fontweight="bold",
        color="#b45309",
        loc="left",
        pad=8,
    )

    # Wheel bottom arc with exaggerated clear 24 hills & valleys on left side
    wheel_cx, wheel_cy, wheel_r = 2.8, 5.8, 7.6
    angles = np.linspace(np.deg2rad(165), np.deg2rad(315), 360)
    r_wave = wheel_r + 0.34 * np.cos(24 * angles)
    wx = wheel_cx + r_wave * np.cos(angles)
    wy = wheel_cy + r_wave * np.sin(angles)
    poly_pts = np.column_stack([wx, wy]).tolist() + [[wheel_cx + 4.5, 6.5], [wheel_cx - 7.0, 6.5]]
    ax2_l.add_patch(patches.Polygon(poly_pts, closed=True, fc="#94a3b8", ec="#0f172a", lw=1.8, zorder=5))
    ax2_l.text(3.2, 2.6, "#01 鉄のコマの外周\n24個の「鉄の山と谷」！\n(磁石がくっつく鉄製)", ha="center", va="center", fontsize=8.4, fontweight="bold", color="#0f172a",
               bbox=dict(boxstyle="round,pad=0.24", fc="#f8fafc", ec="#334155", lw=1.1), zorder=7)

    # #03 South tunnel + #10 Brass insert + #11 Iron Screw + #09 Magnet self-attracted to screw tip!
    ax2_l.add_patch(patches.FancyBboxPatch((-9.6, -4.6), 6.2, 4.4, boxstyle="round,pad=0.1", fc="#e2e8f0", ec="#475569", lw=1.5, zorder=3))
    ax2_l.add_patch(patches.Rectangle((-9.6, -3.55), 6.2, 2.3, fc="#ffffff", ec="#475569", lw=1.0, zorder=4))
    # #10 Brass insert
    ax2_l.add_patch(patches.Rectangle((-9.6, -3.7), 3.0, 2.6, fc="#fbbf24", ec="#92400e", lw=1.2, hatch="///", zorder=5))
    # #11 Iron screw
    ax2_l.add_patch(patches.Rectangle((-11.3, -3.15), 5.6, 1.5, fc="#cbd5e1", ec="#1e293b", lw=1.3, hatch="//", zorder=6))
    ax2_l.add_patch(patches.Rectangle((-12.2, -3.9), 0.95, 3.0, fc="#94a3b8", ec="#1e293b", lw=1.4, zorder=7))
    # #09 Small magnet stuck to tip of #11 screw!
    ax2_l.add_patch(patches.Rectangle((-5.7, -3.25), 1.3, 1.7, fc="#3b82f6", ec="#1e3a8a", lw=1.2, zorder=8))
    ax2_l.add_patch(patches.Rectangle((-4.4, -3.25), 1.3, 1.7, fc="#ef4444", ec="#7f1d1d", lw=1.2, zorder=8))
    ax2_l.text(-5.05, -2.4, "S", ha="center", va="center", fontsize=7.5, fontweight="bold", color="white", zorder=9)
    ax2_l.text(-3.75, -2.4, "N", ha="center", va="center", fontsize=7.5, fontweight="bold", color="white", zorder=9)

    # Attraction lines across air gap between #09 magnet and nearest steel hill!
    ax2_l.annotate("", xy=(-1.55, -0.85), xytext=(-3.0, -2.1),
                   arrowprops=dict(arrowstyle="<->", color="#dc2626", lw=2.2), zorder=9)
    ax2_l.text(2.4, -2.7, "空中のすき間（ギャップ）!\n近づける ＝ カチカチ強め\n遠ざける ＝ ツルツル軽い",
               ha="center", va="center", fontsize=8.0, fontweight="bold", color="#991b1b",
               bbox=dict(boxstyle="round,pad=0.25", fc="#fee2e2", ec="#dc2626", lw=1.2), zorder=9)

    ax2_l.text(-8.2, -5.5, "#11 鉄のネジ ＆ #10 金色インサート", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#78350f")
    ax2_l.annotate("#09 小さな磁石\n(鉄ネジの先にパチンと\n 磁力でくっつく＝ボンド不要!)",
                   xy=(-4.3, -1.5), xytext=(-7.6, 3.8), ha="center", va="center",
                   arrowprops=dict(arrowstyle="->", color="#b91c1c", lw=1.5),
                   fontsize=7.5, fontweight="bold", color="#991b1b",
                   bbox=dict(boxstyle="round,pad=0.24", fc="#fef2f2", ec="#dc2626", lw=1.1), zorder=9)

    ax2_r = fig.add_subplot(gs[1, 1])
    style_card(ax2_r, bg="#ffffff", ec="#d97706")
    ax2_r.text(
        0.04,
        0.93,
        "【小学生でもわかる！カリカリ感（ノッチ）調整のひみつ】",
        transform=ax2_r.transAxes,
        fontsize=10.8,
        fontweight="bold",
        color="#b45309",
        va="top",
    )
    ax2_r.text(
        0.04,
        0.79,
        "① なぜさわっていないのに「カチ・カチ・カチ」と止まるの？\n"
        "   #01 鉄のコマのまわりには 24個の「山」と「谷」が彫ってあります。\n"
        "   すぐ下にいる #09 磁石は、遠い「谷」より近い「山」が大好きなので、\n"
        "   コマが回るたびに一番近い「山」を空中でキュッ！と引っ張って1周24回止めます。\n\n"
        "② ドライバー1本で「好みの重さ」にいつでもチェンジ！\n"
        "   • ネジ(#11)を右へ回して磁石を近づける → 「カチカチ！」しっかり24ノッチ！\n"
        "   • ネジ(#11)を左へ回して磁石を遠ざける → 引っ張りゼロの「無限スピン」！\n"
        "   その中間の「普段はかるくコリコリ、はじけばギュンギュン回る」絶妙な位置も自在！\n\n"
        "③ 空中の磁力だから「一生すり減らない」！\n"
        "   プラスチックのツメやバネをこすり合わせていないので、何年使っても劣化ゼロです。",
        transform=ax2_r.transAxes,
        fontsize=8.65,
        fontweight="bold",
        color="#1e293b",
        va="top",
        linespacing=1.46,
    )

    # =========================================================================
    # ROW 3: Middle Click ("Playground Seesaw Pressing Backside Silent Switch")
    # =========================================================================
    ax3_l = fig.add_subplot(gs[2, 0])
    style_card(ax3_l, bg="#eff6ff", ec="#2563eb")
    ax3_l.set_xlim(-14.5, 9.5)
    ax3_l.set_ylim(-6.8, 7.0)
    ax3_l.set_aspect("equal")
    ax3_l.set_title(
        "しくみ③ 背面スイッチへのミドルクリックのしくみ（「公園のシーソー」拡大図）",
        fontsize=11.0,
        fontweight="bold",
        color="#1d4ed8",
        loc="left",
        pad=8,
    )

    # Right Main PCB ceiling
    ax3_l.add_patch(patches.Rectangle((-14.0, 2.6), 11.5, 1.2, fc="#2a9d8f", ec="#1b4332", lw=1.3, zorder=4))
    ax3_l.text(-8.2, 3.2, "右メイン基板（ウラ面 B.Cu が Z = -5.8mm の天井！）", ha="center", va="center", fontsize=7.3, color="white", fontweight="bold", zorder=5)

    # Upside-down Silent Switch #06 on PCB underside (left)
    ax3_l.add_patch(patches.FancyBboxPatch((-12.8, 0.3), 4.0, 2.25, boxstyle="round,pad=0.06", fc="#fb923c", ec="#9a3412", lw=1.4, zorder=5))
    ax3_l.add_patch(patches.Rectangle((-11.6, -0.55), 1.6, 0.85, fc="#ef4444", ec="#7f1d1d", lw=1.2, zorder=6))
    ax3_l.text(-10.8, 1.45, "#06 静音スイッチ\n(rEXSW1 逆さま実装)", ha="center", va="center", fontsize=6.7, fontweight="bold", color="#431407", zorder=7)

    # #04 Cradle U-saddle + West Rest-Stop Bench
    ax3_l.add_patch(patches.Polygon([[-5.6, 2.6], [-5.6, -0.3], [-2.4, -0.3], [-2.4, 2.6], [-3.1, 2.6], [-3.1, 0.5], [-4.9, 0.5], [-4.9, 2.6]],
                                    closed=True, fc="#cbd5e1", ec="#334155", lw=1.3, zorder=4))
    ax3_l.add_patch(patches.Rectangle((-8.0, -4.8), 1.5, 1.6, fc="#94a3b8", ec="#334155", lw=1.3, zorder=4))
    ax3_l.text(-7.25, -5.5, "#04 やすみ台\n(戻りストッパー)", ha="center", va="center", fontsize=7.0, fontweight="bold", color="#334155")

    # #03 Seesaw Beam + Pivot Circle + Right Wheel
    seesaw_beam = patches.Polygon(
        [[-12.5, -2.5], [4.5, -3.1], [4.5, -1.6], [-3.5, -1.3], [-4.0, 1.6], [-4.6, -1.3], [-12.5, -1.1]],
        closed=True, fc="#bfdbfe", ec="#1d4ed8", lw=1.6, zorder=6
    )
    ax3_l.add_patch(seesaw_beam)
    ax3_l.add_patch(patches.Circle((-4.0, 1.55), 0.98, fc="#fef08a", ec="#854d0e", lw=1.8, zorder=8))
    ax3_l.plot([-4.0], [1.55], marker="+", color="#854d0e", markersize=8, zorder=9)

    ax3_l.annotate("支点！(#03 丸棒 Ø3.0mm)\n#04 のCクリップ軸受けへ\n「パチン！」と嵌まって抜けない!",
                   xy=(-4.0, 2.5), xytext=(-2.6, 5.45), ha="center", va="center",
                   arrowprops=dict(arrowstyle="->", color="#854d0e", lw=1.5),
                   fontsize=7.3, fontweight="bold", color="#713f12",
                   bbox=dict(boxstyle="round,pad=0.22", fc="#fef9c3", ec="#ca8a04", lw=1.1), zorder=10)

    # Right side: Wheel pushed DOWN by finger
    ax3_l.add_patch(patches.Circle((3.2, 0.2), 4.2, fc="#94a3b8", ec="#0f172a", lw=1.8, alpha=0.9, zorder=7))
    ax3_l.text(3.2, 0.2, "#01 ホイール\n(シーソー右側)", ha="center", va="center", fontsize=8.0, fontweight="bold", color="#0f172a",
               bbox=dict(boxstyle="round,pad=0.18", fc="#f8fafc", ec="#334155", lw=0.9), zorder=8)
    ax3_l.annotate("① 指でホイールを\n下にグッと押す！\n(わずか 0.31mm 沈む)",
                   xy=(3.2, 4.4), xytext=(5.6, 5.75), ha="center", va="center",
                   arrowprops=dict(arrowstyle="->", color="#dc2626", lw=2.2),
                   fontsize=7.6, fontweight="bold", color="#991b1b",
                   bbox=dict(boxstyle="round,pad=0.22", fc="#fee2e2", ec="#dc2626", lw=1.2), zorder=10)

    # Left side: Seesaw arm goes UP to press red button!
    ax3_l.annotate("", xy=(-10.8, -0.55), xytext=(-10.8, -2.1),
                   arrowprops=dict(arrowstyle="->", color="#16a34a", lw=2.6), zorder=9)
    ax3_l.text(-11.2, -3.9, "② 反対側の左うでが\nグイッと上に持ち上がり\n赤いボタンを下からポチッ！",
               ha="center", va="center", fontsize=7.5, fontweight="bold", color="#14532d",
               bbox=dict(boxstyle="round,pad=0.22", fc="#dcfce7", ec="#16a34a", lw=1.2), zorder=10)

    # Lever ratio annotation
    ax3_l.annotate("", xy=(-10.8, -2.85), xytext=(-4.0, -2.85), arrowprops=dict(arrowstyle="<->", color="#1d4ed8", lw=1.3))
    ax3_l.annotate("", xy=(-4.0, -2.85), xytext=(3.2, -2.85), arrowprops=dict(arrowstyle="<->", color="#1d4ed8", lw=1.3))
    ax3_l.text(-0.5, -4.3, "左のうで 8.2mm ： 右のうで 8.1mm（ほぼ 1 : 1 のシーソー！）",
               ha="center", va="center", fontsize=7.6, fontweight="bold", color="#1e40af",
               bbox=dict(boxstyle="round,pad=0.18", fc="#dbeafe", ec="#2563eb", lw=0.9), zorder=9)

    ax3_r = fig.add_subplot(gs[2, 1])
    style_card(ax3_r, bg="#ffffff", ec="#2563eb")
    ax3_r.text(
        0.04,
        0.93,
        "【小学生でもわかる！シーソー式ミドルクリックのひみつ】",
        transform=ax3_r.transAxes,
        fontsize=10.8,
        fontweight="bold",
        color="#1d4ed8",
        va="top",
    )
    ax3_r.text(
        0.04,
        0.79,
        "① なぜ基板の「裏」にあるスイッチを押せるの？\n"
        "   ホイールを支えている #03 ロッカーが「公園のシーソー」になっています！\n"
        "   指で右側（#01 ホイール）を下に押すと、真ん中の支点を境にして\n"
        "   反対側の左うでが「上」へ持ち上がり、基板ウラの赤いボタンを下からポチッ！\n\n"
        "② クリックの重さはどれくらい？\n"
        "   支点から右（8.1mm）と左（8.2mm）の長さがほぼ同じ「1 : 1 のてこ」なので、\n"
        "   約 70g の軽快な力で「コトッ」と静かにミドルクリックできます（配線もゼロ！）。\n\n"
        "③ 外れたりグラグラしたりしないの？（Cクリップでパチンと機械連結！）\n"
        "   • 支点の丸棒（Ø3.0mm）は #04 の「Cクリップ軸受け(239°抱え込み)」にパチンと連結！\n"
        "   • 基板がなくても単体で上にも横にも抜けず、左うでは #04 の「やすみ台」に着地\n"
        "   だから回すときはガタつきゼロで、押したときだけ 2.2° シーソーが動きます！",
        transform=ax3_r.transAxes,
        fontsize=8.65,
        fontweight="bold",
        color="#1e293b",
        va="top",
        linespacing=1.46,
    )

    out_path = ASSETS_DIR / "inertia_wheel_easy_guide.png"
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    print(f"Saved {out_path}")


def _autocrop_pil(
    img_path: Path, pad_frac: float = 0.08, target_aspect: float | None = None
) -> tuple[np.ndarray, tuple[float, float, float]]:
    """Crop uniform background around rendered object, optionally letterboxing to `target_aspect` (w/h)."""
    raw = Image.open(img_path)
    if raw.mode in ("RGBA", "LA"):
        white = Image.new("RGBA", raw.size, (255, 255, 255, 255))
        im = Image.alpha_composite(white, raw.convert("RGBA")).convert("RGB")
    else:
        im = raw.convert("RGB")
    arr = np.asarray(im, dtype=np.uint8)
    bg = arr[2, 2].astype(np.int16)
    bg_u8 = arr[2, 2]
    thresh = 35 if int(bg.min()) > 245 else 8
    diff = np.abs(arr.astype(np.int16) - bg).max(axis=2)
    ys, xs = np.where(diff > thresh)
    if len(xs) == 0:
        cropped_u8 = arr
    else:
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
        cropped_u8 = arr[y0 : y1 + 1, x0 : x1 + 1]

    if target_aspect is not None:
        ch, cw = cropped_u8.shape[:2]
        cur_asp = cw / max(1, ch)
        if cur_asp < target_aspect:
            new_w = int(round(ch * target_aspect))
            canvas = np.broadcast_to(bg_u8, (ch, new_w, 3)).copy()
            ox = (new_w - cw) // 2
            canvas[:, ox : ox + cw, :] = cropped_u8
            cropped_u8 = canvas
        elif cur_asp > target_aspect:
            new_h = int(round(cw / target_aspect))
            canvas = np.broadcast_to(bg_u8, (new_h, cw, 3)).copy()
            oy = (new_h - ch) // 2
            canvas[oy : oy + ch, :, :] = cropped_u8
            cropped_u8 = canvas

    cropped = cropped_u8.astype(np.float32) / 255.0
    return cropped, tuple((bg / 255.0).tolist())


def _build_temp_part_renders(tmp_dir: Path) -> dict[str, Path]:
    """Build helper 3D STEP models for off-the-shelf & exploded components and render thumbnails in one cadgen job."""
    gen_code = textwrap.dedent(
        f"""
        import math, sys
        from pathlib import Path
        from cadgen import build123d as bd

        sys.path.insert(0, {repr(str(WORKSPACE / "scripts"))})
        import generate_inertia_wheel as giw

        out = Path({repr(str(tmp_dir))})

        # 0. Exploded 3D Assembly of the Under-Plate Inertia Wheel
        mov, stat, screws = giw.assemble_wheel_parts_global(click_deg=0.0)
        exp_offsets = {{
            "Magnet_D4x1mm_Diametric": (-13.0, 0.0, 9.5),
            "Magnet_Holder_PA12": (-8.5, 0.0, 9.5),
            "Bearing_DDL520ZZ_West": (-4.5, 0.0, 9.5),
            "Steel_Flywheel_22mm": (1.8, 0.0, 9.5),
            "Bearing_DDL520ZZ_East": (9.8, 0.0, 9.5),
            "Wheel_Rocker_PA12": (0.0, 0.0, -2.5),
            "Magnet_D2x2mm_Axial_Detent": (0.0, -5.5, -2.5),
            "HeatSet_Insert_M2_Detent": (0.0, -9.5, -2.5),
            "Screw_M2x6_Detent_Adjuster": (0.0, -14.5, -2.5),
            "Wheel_Cradle_PA12": (0.0, 0.0, -13.5),
            "HeatSet_Insert_M2_WC1": (0.0, 0.0, -9.5),
            "HeatSet_Insert_M2_WC2": (0.0, 0.0, -9.5),
            "Top_Screw_M2x6_WC1": (0.0, 0.0, 15.5),
            "Top_Screw_M2x6_WC2": (0.0, 0.0, 15.5),
        }}
        exp_children = []
        for s in mov + stat + screws:
            lbl = s.label
            dx, dy, dz = exp_offsets.get(lbl, (0.0, 0.0, 0.0))
            ms = s.moved(bd.Location((dx, dy, dz))).solids()[0]
            ms.label = lbl
            exp_children.append(ms)
        bd.export_step(bd.Compound(children=exp_children), str(out / "mod_exploded.step"))

        # 1. Assembled-orientation Flywheel (axle horizontal)
        fw = giw.build_steel_flywheel_local()
        fw = fw.moved(bd.Location((0, 0, -fw.bounding_box().min.Z))).solids()[0]
        fw.label = "Steel_Flywheel_22mm"
        bd.export_step(fw, str(out / "p01_flywheel.step"))

        # 2. Upright Cradle (showing upward U-saddles & WC1/WC2 bosses)
        cr = giw.build_wheel_cradle_local()
        cr = cr.moved(bd.Location((0, 0, -cr.bounding_box().min.Z))).solids()[0]
        cr.label = "Wheel_Cradle_PA12"
        bd.export_step(cr, str(out / "p04_cradle_upright.step"))

        # 3. Onboard rU6: TMAG5273A1QDBVR (SOT-23-6) + SMD Passives (rC18, rR11..rR13)
        ic = bd.Box(1.70, 2.95, 0.95, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((-1.4, 0.0, 0.15)))
        ic = ic - bd.Cylinder(0.22, 0.25, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((-1.95, 1.05, 0.92)))
        ic.label = "TMAG5273_SOT23_6"
        sot_parts = [ic]
        for idx, py in enumerate([-0.95, 0.0, 0.95]):
            for side, sx in [("L", -1.0), ("R", 1.0)]:
                lead = bd.Box(0.65, 0.36, 0.22, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((-1.4 + sx * 1.12, py, 0.0)))
                lead.label = f"Lead_{{side}}_{{idx}}"
                sot_parts.append(lead)
        for ci, cy in enumerate([-1.3, 0.0, 1.3]):
            sm = bd.Box(1.0, 1.6, 0.55, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((2.2, cy, 0.0)))
            sm.label = f"SMD_0603_{{ci}}"
            sot_parts.append(sm)
        bd.export_step(bd.Compound(children=sot_parts), str(out / "p05_tmag5273.step"))

        # 4. rEXSW1: Kailh Square Silent Switch (6.2 x 6.2 x 4.3 mm)
        sw_base = bd.Box(6.2, 6.2, 2.25, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((0, 0, 2.0)))
        sw_base.label = "SW_Base"
        sw_top = bd.Box(6.0, 6.0, 1.10, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((0, 0, 4.25)))
        sw_top.label = "SW_Cover"
        sw_btn = bd.Cylinder(1.50, 0.95, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((0, 0, 5.35)))
        sw_btn.label = "SW_Red_Button"
        pin_a = bd.Box(0.75, 0.4, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((-2.5, 0, 0.0)))
        pin_a.label = "SW_Pin1"
        pin_b = bd.Box(0.75, 0.4, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((2.5, 0, 0.0)))
        pin_b.label = "SW_Pin2"
        bd.export_step(bd.Compound(children=[sw_base, sw_top, sw_btn, pin_a, pin_b]), str(out / "p06_silent_sw.step"))

        # 5. 2x NMB DDL-520ZZ Shielded Miniature Bearings (Ø2 x Ø5 x 2.30 mm — zero shims!)
        brg_parts = []
        for bi, bx in enumerate([-3.4, 3.4]):
            outer_r = (
                bd.Cylinder(2.50, 2.30, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
                - bd.Cylinder(2.05, 2.40, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((0, 0, -0.05)))
            ).moved(bd.Location((bx, 0, 0))).solids()[0]
            outer_r.label = f"OuterRace_{{bi}}"
            shield = (
                bd.Cylinder(2.05, 2.06, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
                - bd.Cylinder(1.42, 2.16, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((0, 0, -0.05)))
            ).moved(bd.Location((bx, 0, 0.12))).solids()[0]
            shield.label = f"MetalShieldZZ_{{bi}}"
            inner_r = (
                bd.Cylinder(1.42, 2.30, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
                - bd.Cylinder(1.00, 2.40, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((0, 0, -0.05)))
            ).moved(bd.Location((bx, 0, 0))).solids()[0]
            inner_r.label = f"InnerRace_{{bi}}"
            brg_parts.extend([outer_r, shield, inner_r])
        bd.export_step(bd.Compound(children=brg_parts), str(out / "p07_bearings_zz.step"))

        # 6. M2 x L=3.0 x OD=3.2 mm Knurled Brass Heat-Set Inserts (3x shown)
        inserts = []
        for ii, ix in enumerate([-4.5, 0.0, 4.5]):
            band1 = bd.Cylinder(1.62, 1.05, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((ix, 0, 0.35)))
            band2 = bd.Cylinder(1.62, 1.05, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((ix, 0, 1.75)))
            pilot = bd.Cylinder(1.42, 3.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((ix, 0, 0.0)))
            ins = (pilot + band1 + band2 - bd.Cylinder(1.00, 3.20, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((ix, 0, -0.1)))).solids()[0]
            ins.label = f"Brass_Insert_{{ii}}"
            inserts.append(ins)
        bd.export_step(bd.Compound(children=inserts), str(out / "p10_inserts.step"))

        # 7. Unified M2 x 6.0 mm Pan/Low-Head Steel Screws (3x shown)
        screws_3 = []
        for si, sx in enumerate([-5.2, 0.0, 5.2]):
            shk = bd.Cylinder(0.98, 6.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((sx, 0, 0.0)))
            hd = bd.Cylinder(1.90, 1.15, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((sx, 0, 6.00)))
            slt1 = bd.Box(2.1, 0.45, 0.6, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((sx, 0, 6.60)))
            slt2 = bd.Box(0.45, 2.1, 0.6, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((sx, 0, 6.60)))
            sc = (shk + hd - slt1 - slt2).solids()[0]
            sc.label = f"M2x6_Screw_{{si}}"
            screws_3.append(sc)
        bd.export_step(bd.Compound(children=screws_3), str(out / "p11_screws.step"))

        # 8. Right Top Plate (7.70 x 22.00 mm slot) + Right Main PCB Cross Slot Close-Up
        tp = bd.Box(26.0, 30.0, 1.60, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((-1.5, 0.0, 2.20)))
        tp = (tp - bd.Box(7.70, 22.00, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((2.0, 0.0, 2.00)))
                 - bd.Cylinder(2.20, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((-5.65, 7.8, 2.00)))
                 - bd.Cylinder(2.20, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((8.95, -8.0, 2.00)))).solids()[0]
        tp.label = "Right_Top_Plate_Window"
        mp = bd.Box(26.0, 30.0, 1.60, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((-1.5, 0.0, 0.0)))
        mp = (mp - bd.Box(7.70, 22.50, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((2.0, -0.25, -0.20)))
                 - bd.Box(16.5, 7.50, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((0.8, 0.0, -0.20)))
                 - bd.Cylinder(1.20, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((-5.65, 7.8, -0.20)))
                 - bd.Cylinder(1.20, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((8.95, -8.0, -0.20)))).solids()[0]
        mp.label = "Right_Main_PCB_Window"
        bd.export_step(bd.Compound(children=[tp, mp]), str(out / "p12_plate_pcb.step"))
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
        ("exploded", tmp_dir / "mod_exploded.step", "iso", "parts"),
        ("p01", tmp_dir / "p01_flywheel.step", "iso", "shaded"),
        ("p02", parts_dir / "magnet-holder.step", "iso", "shaded"),
        ("p03", parts_dir / "wheel-rocker.step", "iso", "shaded"),
        ("p04", tmp_dir / "p04_cradle_upright.step", "iso", "shaded"),
        ("p05", tmp_dir / "p05_tmag5273.step", "iso", "parts"),
        ("p06", tmp_dir / "p06_silent_sw.step", "iso", "parts"),
        ("p07", tmp_dir / "p07_bearings_zz.step", "35:45", "parts"),
        ("p10", tmp_dir / "p10_inserts.step", "35:42", "parts"),
        ("p11", tmp_dir / "p11_screws.step", "35:42", "parts"),
        ("p12", tmp_dir / "p12_plate_pcb.step", "iso", "parts"),
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


def _draw_magnet_card(ax, diametric: bool):
    """Clear N/S polarity diagram for #08 Diametric Magnet vs #09 Axial Detent Magnet."""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.5)
    ax.set_facecolor("#eff2f6")
    ax.axis("off")
    if diametric:
        ax.add_patch(patches.Wedge((3.0, 3.45), 1.85, 90, 270, fc="#ef4444", ec="#7f1d1d", lw=1.4, zorder=4))
        ax.add_patch(patches.Wedge((3.0, 3.45), 1.85, -90, 90, fc="#3b82f6", ec="#1e3a8a", lw=1.4, zorder=4))
        ax.plot([3.0, 3.0], [1.60, 5.30], color="#ffffff", lw=1.6, linestyle="--", zorder=5)
        ax.text(2.08, 3.45, "N", ha="center", va="center", fontsize=12, fontweight="bold", color="white", zorder=6)
        ax.text(3.92, 3.45, "S", ha="center", va="center", fontsize=12, fontweight="bold", color="white", zorder=6)
        ax.annotate("", xy=(5.05, 3.45), xytext=(0.95, 3.45), arrowprops=dict(arrowstyle="<->", color="#111827", lw=1.2), zorder=3)
        ax.text(3.0, 1.00, "Ø4.0 × 厚1.0 mm", ha="center", va="center", fontsize=7.3, fontweight="bold", color="#1e293b")
        ax.add_patch(patches.FancyBboxPatch((5.45, 1.45), 4.15, 3.90, boxstyle="round,pad=0.18", fc="#fff1f2", ec="#be123c", lw=1.2))
        ax.text(7.52, 3.40, "【重要】径方向着磁\n(Diametric 2極)\n\n#02 ポケット＋#03壁\nで接着剤ゼロ完全固定!", ha="center", va="center", fontsize=6.7, fontweight="bold", color="#9f1239")
    else:
        ax.add_patch(patches.Rectangle((1.70, 3.45), 2.6, 1.45, fc="#ef4444", ec="#7f1d1d", lw=1.4, zorder=4))
        ax.add_patch(patches.Rectangle((1.70, 2.00), 2.6, 1.45, fc="#3b82f6", ec="#1e3a8a", lw=1.4, zorder=4))
        ax.add_patch(patches.Ellipse((3.00, 4.90), 2.6, 0.65, fc="#f87171", ec="#7f1d1d", lw=1.3, zorder=5))
        ax.text(3.00, 4.10, "N", ha="center", va="center", fontsize=11.5, fontweight="bold", color="white", zorder=6)
        ax.text(3.00, 2.68, "S", ha="center", va="center", fontsize=11.5, fontweight="bold", color="white", zorder=6)
        ax.text(3.0, 1.00, "Ø2.0 × 長2.0 mm", ha="center", va="center", fontsize=7.3, fontweight="bold", color="#1e293b")
        ax.add_patch(patches.FancyBboxPatch((5.45, 1.45), 4.15, 3.90, boxstyle="round,pad=0.18", fc="#eff6ff", ec="#1d4ed8", lw=1.2))
        ax.text(7.52, 3.40, "軸方向着磁 (標準品)\n二六製作所 NE280 等\n\n鉄M2×6mmネジ先端に\n磁力で自己吸着・接着不要!", ha="center", va="center", fontsize=6.6, fontweight="bold", color="#1e3a8a")


def _draw_parts_guide_diagram():
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp_dir = Path(tmp_s)
        print("Building & rendering 3D component thumbnails for parts guide...")
        thumbs = _build_temp_part_renders(tmp_dir)

        fig = plt.figure(figsize=(18.5, 19.5), dpi=180)
        fig.patch.set_facecolor("#ffffff")
        fig.suptitle(
            "curcur40 アンダープレート一体軸慣性ホイール 部品構成・組立ビジュアルガイド（幅6.50mm大慣性・全12要素・6自由度ロック構造）",
            fontsize=13.8,
            fontweight="bold",
            y=0.985,
            color="#0f172a",
        )

        gs = fig.add_gridspec(
            nrows=5,
            ncols=3,
            height_ratios=[1.42, 1.0, 1.0, 1.0, 1.0],
            hspace=0.30,
            wspace=0.16,
            left=0.03,
            right=0.97,
            top=0.952,
            bottom=0.02,
        )

        gs_top = gs[0, :].subgridspec(1, 2, wspace=0.10)

        ax_top_l = fig.add_subplot(gs_top[0, 0])
        img_r, bg_r = _autocrop_pil(ASSETS_DIR / "render_curcur40_right_wheel.png", pad_frac=0.04, target_aspect=2.05)
        ax_top_l.set_facecolor(bg_r)
        ax_top_l.imshow(img_r, aspect="auto")
        ax_top_l.set_xticks([])
        ax_top_l.set_yticks([])
        ax_top_l.set_title(
            "A. 右キーボード 実装外観（幅6.50mmホイール・Ø5.2mmフラットボスで基板直締結＋スイッチ嵌合プレート）",
            fontsize=10.0,
            fontweight="bold",
            color="#0f172a",
            pad=7,
        )

        ax_top_r = fig.add_subplot(gs_top[0, 1])
        img_e, bg_e = _autocrop_pil(thumbs["exploded"], pad_frac=0.05, target_aspect=2.05)
        ax_top_r.set_facecolor(bg_e)
        ax_top_r.imshow(img_e, aspect="auto")
        ax_top_r.set_xticks([])
        ax_top_r.set_yticks([])
        ax_top_r.set_title(
            "B. アンダープレート一体軸ホイール 3D分解斜視図（4造形部品＋市販ベアリング・磁石・共通M2×6mmネジ）",
            fontsize=10.0,
            fontweight="bold",
            color="#0f172a",
            pad=7,
        )

        cards = [
            (
                "#01 一体軸スチールホイール ×1",
                "JLCCNC 切削 (45#鋼+無電解Ni)",
                "#0f766e",
                "p01",
                "cases/inertia_wheel/steel-flywheel.step\nØ22.0×幅6.50mm・24溝・質量 19.31g\nJ≈1160g·mm²・段付き軸一体＝シム不要!",
            ),
            (
                "#02 マグネットホルダー ×1",
                "JLC3DP 造形 (MJF/SLS PA12)",
                "#1d4ed8",
                "p02",
                "cases/inertia_wheel/magnet-holder.step\nØ5.72×2.05mm・#01西側Dカット軸へ圧入\n西ポケットで#08磁石を接着剤ゼロ保持",
            ),
            (
                "#03 シーソーロッカー ×1",
                "JLC3DP 造形 (MJF/SLS PA12)",
                "#1d4ed8",
                "p03",
                "cases/inertia_wheel/wheel-rocker.step\nCクリップ軸受座＋一体Ø3.0トラニオン支点\n西キーパータブで#02/#08抜け完全阻止!",
            ),
            (
                "#04 アンダーPCBクレードル ×1",
                "JLC3DP 造形 (MJF/SLS PA12)",
                "#1d4ed8",
                "p04",
                "cases/inertia_wheel/wheel-cradle.step\nWC1/WC2の2箇所で右メイン基板裏面へ固定\nØ3.06 Cクリップ軸受へ#03をパチンと機械連結!",
            ),
            (
                "#05 3Dホールセンサー (rU6)",
                "PCBA自動実装済 (手配・配線不要)",
                "#15803d",
                "p05",
                "TI TMAG5273A1QDBVR (SOT-23-6 / C3716049)\n右メイン基板 B.Cu にJLCPCB実装済!\nサブ基板・SH 6P手配線ケーブル完全不要",
            ),
            (
                "#06 静音ミドルクリックSW (rEXSW1)",
                "市販購入品 ×1 (基板B.Cu直付け)",
                "#b45309",
                "p06",
                "Kailh Square Silent 6.2×6.2×4.3mm (赤軸)\n右メイン基板 B.Cu へ挿しF.Cu側2ピンはんだ\n(飛び出しピン先端のみニッパーで平切り)",
            ),
            (
                "#07 ミニチュアベアリング ×2",
                "市販購入品 ×2 (脱脂して使用)",
                "#b45309",
                "p07",
                "NMB ミネベアミツミ DDL-520ZZ\n内径Ø2×外径Ø5×幅2.3mm 標準両シールド\n#03 Cクリップ座へパチンと嵌めて上抜けゼロ",
            ),
            (
                "#08 角度検出磁石 (D4×1mm) ×1",
                "市販購入品 ×1 (径方向2極着磁)",
                "#be123c",
                "mag_diam",
                "Ø4.0×厚1.0mm ネオジム磁石 (Diametric)\n#02ホルダー西ポケット＋#03キーパータブで\n両方向ロックされ接着剤なしで脱落ゼロ!",
            ),
            (
                "#09 ラチェット磁石 (Ø2×2mm) ×1",
                "市販購入品 ×1 (軸方向着磁)",
                "#be123c",
                "mag_axial",
                "Ø2.0×長2.0mm 円柱ネオジム (NE280等)\n45#鋼製ホイールの24溝を直接磁気吸引!\nネジ回転だけでフリースピン〜24ノッチ調整",
            ),
            (
                "#10 真鍮ヒートセットインサート",
                "市販購入品 (ホイール3個 / 全体17個)",
                "#7c2d12",
                "p10",
                "M2 × 長さ3.0 × 外径3.2mm ローレット真鍮\nクレードルWC1/WC2に2個＋ロッカー南に1個\n220〜250℃の普通のはんだごてで簡単圧入!",
            ),
            (
                "#11 統一 M2 × 6.0mm 精密ネジ",
                "市販購入品 (ホイール3本 / 全体17本)",
                "#7c2d12",
                "p11",
                "キーボード全17箇所すべて同一 M2×6.0mm!\n外周10箇所＋WC1/WC2でメイン基板を直接固定\n(南ラチェット用1本は磁石が付く鉄/鋼製)",
            ),
            (
                "#12 右プレート＆右メイン基板窓",
                "JLCPCB 基板・プレート (カバー不要)",
                "#334155",
                "p12",
                "プレート: 7.7×22.0mm ゆとりある幅広窓\n全12箇所 Ø4.4mm ネジ頭沈み込み穴でキー干渉ゼロ\nトッププレートはChoc V2スイッチでパチンと保持!",
            ),
        ]

        for idx, (title, badge, badge_col, thumb_key, desc) in enumerate(cards):
            r = 1 + (idx // 3)
            c = idx % 3
            cell_gs = gs[r, c].subgridspec(2, 1, height_ratios=[1.55, 0.95], hspace=0.04)
            ax_img = fig.add_subplot(cell_gs[0, 0])
            ax_txt = fig.add_subplot(cell_gs[1, 0])

            if thumb_key == "mag_diam":
                _draw_magnet_card(ax_img, diametric=True)
            elif thumb_key == "mag_axial":
                _draw_magnet_card(ax_img, diametric=False)
            else:
                im_arr, bg_c = _autocrop_pil(thumbs[thumb_key], pad_frac=0.08, target_aspect=2.45)
                ax_img.set_facecolor(bg_c)
                ax_img.imshow(im_arr, aspect="auto")
                ax_img.set_xticks([])
                ax_img.set_yticks([])
                for sp in ax_img.spines.values():
                    sp.set_edgecolor("#cbd5e1")
                    sp.set_linewidth(1.0)

            ax_img.set_title(title, fontsize=9.1, fontweight="bold", color="#0f172a", loc="left", pad=5)
            ax_img.text(
                0.99,
                1.03,
                badge,
                transform=ax_img.transAxes,
                ha="right",
                va="bottom",
                fontsize=6.9,
                fontweight="bold",
                color="white",
                bbox=dict(boxstyle="round,pad=0.18", fc=badge_col, ec="none"),
            )

            ax_txt.set_facecolor("#f8fafc")
            ax_txt.set_xticks([])
            ax_txt.set_yticks([])
            for sp in ax_txt.spines.values():
                sp.set_edgecolor("#e2e8f0")
                sp.set_linewidth(1.0)
            ax_txt.text(
                0.03,
                0.50,
                desc,
                transform=ax_txt.transAxes,
                ha="left",
                va="center",
                fontsize=7.9,
                color="#1e293b",
                linespacing=1.38,
                fontweight="bold",
            )

        out_path = ASSETS_DIR / "inertia_wheel_parts_guide.png"
        fig.savefig(out_path, dpi=180)
        plt.close(fig)
        print(f"Saved {out_path}")


def main():
    render_step_previews()
    _draw_spec_diagram()
    _draw_easy_guide_diagram()
    _draw_parts_guide_diagram()
    print("All inertia wheel previews & specification diagrams generated successfully!")


if __name__ == "__main__":
    main()
