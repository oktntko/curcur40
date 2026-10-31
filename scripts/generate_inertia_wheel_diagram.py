# -*- coding: utf-8 -*-
"""
Render 3D CAD preview images and generate engineering cross-section & visual BOM diagrams
for the Under-Plate 1-Piece Integral-Shaft Passive Magnetic Inertia Wheel (`curcur40-inertia-wheel`).

Outputs into `docs/assets/`:
  1. render_inertia_wheel_flywheel.png
  2. render_inertia_wheel_module.png
  3. render_curcur40_right_wheel.png
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
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(17.2, 8.2), dpi=200)
    fig.patch.set_facecolor("#ffffff")
    fig.suptitle(
        "アンダープレート一体軸パッシブ磁気慣性ホイール 内部断面・機構図（接着剤ゼロ・シムゼロ・サブ基板ゼロ・カバーゼロ）",
        fontsize=12.6,
        fontweight="bold",
        y=0.97,
        color="#1a1a1a",
    )

    z_axle = -6.90  # Global Z of wheel rotary axis (wheel OD Ø22.00 mm -> top Z = +4.10 mm, bottom Z = -17.90 mm)

    # =========================================================================
    # Panel 1: X–Z Front Cross-Section along Axle (Y_pcb = -2.00 mm)
    # Local u = x_pcb - 14.2875 mm (+u = East, -u = West)
    # =========================================================================
    ax1.set_title("① 正面断面図 (X–Z 断面：一体軸スチールホイール × 基板直付け3Dホール＆静音クリック)", fontsize=10.4, fontweight="bold", pad=10)
    ax1.set_xlim(-19.5, 10.2)
    ax1.set_ylim(-22.5, 7.6)
    ax1.set_aspect("equal")
    ax1.set_facecolor("#f8f9fa")
    ax1.grid(True, linestyle=":", linewidth=0.5, color="#cccccc")
    ax1.set_xlabel("ホイール軸方向ローカル座標 u [mm]（u = 0.00 がホイール中心 / 西 -u 側がセンサー＆スイッチ）", fontsize=8.8)
    ax1.set_ylabel("curcur40 グローバル Z 座標 [mm]（ケース上縁 = 0.00 / プレート上面 = -2.00）", fontsize=8.8)

    ax1.axvline(0.0, color="#64748b", linestyle="-.", linewidth=0.9, zorder=1)
    ax1.axhline(3.60, color="#0077b6", linestyle=":", linewidth=1.1, zorder=2)
    ax1.text(-19.1, 3.85, "隣接 Choc V2 キーキャップ天面 Z = +3.60 mm", fontsize=7.0, fontweight="bold", color="#0077b6")

    # Top Plate (-3.60..-2.00) with clean 5.60 mm slot (u in [-2.80, +2.80]) — NO COVERS!
    ax1.add_patch(patches.Rectangle((-19.0, -3.60), 16.20, 1.60, fc="#3a7ca5", ec="#16425b", lw=1.2, zorder=3))
    ax1.add_patch(patches.Rectangle((2.80, -3.60), 7.00, 1.60, fc="#3a7ca5", ec="#16425b", lw=1.2, zorder=3))
    ax1.text(-11.2, -2.80, "右トッププレート (-3.6〜-2.0 / 5.6×22.0mm 窓)", ha="center", va="center", fontsize=6.6, color="white", fontweight="bold", zorder=4)

    # Right Main PCB (-5.80..-4.20) with cross cutout (u in [-8.29, +6.12] open at v = 0)
    ax1.add_patch(patches.Rectangle((-19.0, -5.80), 10.71, 1.60, fc="#2a9d8f", ec="#1b4332", lw=1.2, zorder=3))
    ax1.add_patch(patches.Rectangle((6.12, -5.80), 3.68, 1.60, fc="#2a9d8f", ec="#1b4332", lw=1.2, zorder=3))
    ax1.text(-13.6, -5.00, "右メイン基板 (-5.8〜-4.2)", ha="center", va="center", fontsize=6.4, color="white", fontweight="bold", zorder=4)

    # Sealed Tilted Case Floor (~Z = -21.8 to -19.4 in wheel region — 100% hole-free)
    ax1.add_patch(patches.Polygon([[-19.0, -22.2], [9.8, -21.2], [9.8, -19.2], [-19.0, -20.2]],
                                  closed=True, fc="#495057", ec="#212529", lw=1.1, alpha=0.85, zorder=2))
    ax1.text(-4.5, -21.0, "100% 密閉・穴なし傾斜ボトムケース床（肉厚 2.40 mm）", ha="center", va="center", fontsize=6.8, color="white", fontweight="bold", zorder=3)

    # #04 Wheel Cradle (static under-PCB bracket: U-saddle around u = -6.95, Z = -7.55 + West rest-stop bridge u in [-10.55, -9.35], Z in [-13.90, -12.45])
    ax1.add_patch(patches.Rectangle((-10.55, -9.70), 6.70, 3.90, fc="#cbd5e1", ec="#334155", lw=1.0, alpha=0.65, linestyle="--", zorder=2))
    ax1.add_patch(patches.Rectangle((-10.55, -13.90), 1.20, 8.10, fc="#94a3b8", ec="#334155", lw=1.0, zorder=3))

    # #03 Wheel Rocker (West ear [-5.60, -2.55], East ear [+2.55, +5.65], bottom stirrup [-19.70, -18.35], West striker arm [-16.50, -5.60] at Z in [-12.00, -10.25])
    rocker_poly = patches.Polygon(
        [
            [-5.60, -19.70], [5.65, -19.70], [5.65, -5.35], [2.55, -5.35],
            [2.55, -18.35], [-2.55, -18.35], [-2.55, -5.35], [-5.60, -5.35],
        ],
        closed=True, fc="#dee2e6", ec="#495057", lw=1.1, zorder=4,
    )
    ax1.add_patch(rocker_poly)
    ax1.add_patch(patches.Rectangle((-16.50, -12.00), 10.90, 1.75, fc="#dee2e6", ec="#495057", lw=1.1, zorder=4))
    # Integral Ø2.70 mm Pivot Trunnion at (u = -6.95, Z = -7.55)
    ax1.add_patch(patches.Circle((-6.95, -7.55), 1.35, fc="#f8fafc", ec="#0f172a", lw=1.4, zorder=7))
    ax1.plot([-6.95], [-7.55], marker="+", color="#0f172a", markersize=6, zorder=8)

    # #01 1-Piece Integral-Shaft 45# Steel Flywheel:
    # Rim u in [-2.20, +2.20], Z in [-17.90, +4.10]; Integral Ø2.90mm shoulders [-2.45, +2.45]; Integral Ø1.98mm shaft [-6.90, +4.72]
    ax1.add_patch(patches.Rectangle((-6.90, z_axle - 0.99), 11.62, 1.98, fc="#e2e8f0", ec="#334155", lw=1.1, zorder=6))
    ax1.add_patch(patches.Rectangle((-2.45, z_axle - 1.45), 4.90, 2.90, fc="#cbd5e1", ec="#334155", lw=1.0, zorder=6))
    ax1.add_patch(patches.Rectangle((-2.20, z_axle - 11.00), 4.40, 22.00, fc="#b8c4d0", ec="#1e293b", lw=1.5, zorder=7))
    ax1.text(0.0, -1.2, "#01 一体軸\n45#鋼ホイール\nØ22.0×4.4\n(13.12g)", ha="center", va="center", fontsize=6.5, fontweight="bold", color="#0f172a", zorder=8)

    # #07 2x NMB DDL-520ZZ Bearings (Ø2 x Ø5 x 2.30 mm at [-4.75, -2.45] & [+2.45, +4.75])
    for bu in (-4.75, 2.45):
        ax1.add_patch(patches.Rectangle((bu, z_axle - 2.50), 2.30, 5.00, fc="#ffffff", ec="#0077b6", lw=1.2, zorder=5))

    # #02 PA12 Magnet Holder (u in [-7.97, -5.92], Ø5.68 mm) + #08 D4x1mm Diametric Magnet (u in [-7.94, -6.94])
    ax1.add_patch(patches.Rectangle((-7.97, z_axle - 2.84), 2.05, 5.68, fc="#94d2bd", ec="#005f73", lw=1.1, zorder=6))
    ax1.add_patch(patches.Rectangle((-7.94, z_axle - 2.00), 1.00, 4.00, fc="#e63946", ec="#6a040f", lw=1.1, zorder=7))

    # #05 Onboard rU6: TMAG5273A1QDBVR 3D Hall Sensor on Main PCB B.Cu (u = -10.11, Z = -6.95..-5.80)
    ax1.add_patch(patches.Rectangle((-10.95, -6.95), 1.70, 1.15, fc="#1e293b", ec="#000000", lw=1.0, zorder=6))
    ax1.text(-10.11, -6.38, "rU6", ha="center", va="center", fontsize=5.6, color="white", fontweight="bold", zorder=7)

    # #06 Onboard rEXSW1: Kailh Square Silent Switch on Main PCB B.Cu (u = -15.14, body Z = -9.15..-5.80, plunger Z = -10.10..-9.15)
    ax1.add_patch(patches.Rectangle((-18.24, -9.15), 6.20, 3.35, fc="#f4a261", ec="#9c4100", lw=1.2, zorder=5))
    ax1.add_patch(patches.Rectangle((-16.64, -10.10), 3.00, 0.95, fc="#e63946", ec="#6a040f", lw=1.0, zorder=6))

    # Callouts on Panel 1
    ax1.annotate("#01 1ピースCNC一体軸ホイール\n頂点 Z=+4.10mm（キー上わずか +0.50mm!）\n段付き軸一体削り出し＝シムリング不要",
                 xy=(0.0, 4.10), xytext=(2.8, 5.85), ha="center", va="center",
                 arrowprops=dict(arrowstyle="->", color="#1e293b", lw=1.15),
                 fontsize=6.6, fontweight="bold", color="#0f172a",
                 bbox=dict(boxstyle="round,pad=0.22", fc="#f1f5f9", ec="#475569", lw=0.9), zorder=10)

    ax1.annotate("#05 rU6: TMAG5273 (PCBA実装済)\n＋ #08 D4×1mm磁石（#02 D穴圧入・接着不要）\nサブ基板・手配線ハーネスを完全廃止!",
                 xy=(-8.5, -6.5), xytext=(-11.6, 5.85), ha="center", va="center",
                 arrowprops=dict(arrowstyle="->", color="#005f73", lw=1.15),
                 fontsize=6.5, fontweight="bold", color="#005f73",
                 bbox=dict(boxstyle="round,pad=0.22", fc="#e0fbfc", ec="#005f73", lw=0.9), zorder=10)

    ax1.annotate("#06 rEXSW1 静音SW（B.Cu直付け）\n一体トラニオン支点(u=-6.95)のてこ比で\n約68gfの軽快な静音ミドルクリック",
                 xy=(-15.14, -10.10), xytext=(-13.8, -16.8), ha="center", va="center",
                 arrowprops=dict(arrowstyle="->", color="#9c4100", lw=1.15),
                 fontsize=6.5, fontweight="bold", color="#7f2704",
                 bbox=dict(boxstyle="round,pad=0.22", fc="#fff3cd", ec="#d97706", lw=0.85), zorder=10)

    ax1.annotate("#07 DDL-520ZZ×2\n(標準2.3mm厚・脱脂)",
                 xy=(3.60, -6.90), xytext=(6.6, -12.6), ha="center", va="center",
                 arrowprops=dict(arrowstyle="->", color="#0077b6", lw=1.1),
                 fontsize=6.5, fontweight="bold", color="#023e8a",
                 bbox=dict(boxstyle="round,pad=0.20", fc="#e0f2fe", ec="#0077b6", lw=0.85), zorder=10)

    # =========================================================================
    # Panel 2: Y–Z Side Cross-Section along Wheel Plane (u = 0.00 mm)
    # Local v = -(y_pcb + 2.00 mm) (+v = North, -v = South)
    # =========================================================================
    ax2.set_title("② 側面機構図 (Y–Z 断面：24溝磁気デテント無段階調整 × 上方向M2×6mmヒートセット締結)", fontsize=10.4, fontweight="bold", pad=10)
    ax2.set_xlim(-21.5, 16.5)
    ax2.set_ylim(-22.5, 7.6)
    ax2.set_aspect("equal")
    ax2.set_facecolor("#f8f9fa")
    ax2.grid(True, linestyle=":", linewidth=0.5, color="#cccccc")
    ax2.set_xlabel("南北ローカル座標 v [mm]（南 -v 側：接着不要ラチェット磁力調整ネジ ／ 北 +v 側）", fontsize=8.8)
    ax2.set_ylabel("curcur40 グローバル Z 座標 [mm]", fontsize=8.8)

    ax2.axhline(3.60, color="#0077b6", linestyle=":", linewidth=1.1, zorder=2)

    # Top Plate (-3.60..-2.00, 22.00 mm window v in [-11.00, +11.00]) + WC1/WC2 Ø4.40mm clearance bore shown at v = +7.80 (projected)
    ax2.add_patch(patches.Rectangle((-21.0, -3.60), 10.00, 1.60, fc="#3a7ca5", ec="#16425b", lw=1.2, zorder=3))
    ax2.add_patch(patches.Rectangle((11.00, -3.60), 5.00, 1.60, fc="#3a7ca5", ec="#16425b", lw=1.2, zorder=3))

    # Main PCB (-5.80..-4.20, 23.00 mm window v in [-11.50, +11.50])
    ax2.add_patch(patches.Rectangle((-21.0, -5.80), 9.50, 1.60, fc="#2a9d8f", ec="#1b4332", lw=1.2, zorder=3))
    ax2.add_patch(patches.Rectangle((11.50, -5.80), 4.50, 1.60, fc="#2a9d8f", ec="#1b4332", lw=1.2, zorder=3))

    # Sealed Case Floor
    ax2.add_patch(patches.Rectangle((-21.0, -21.8), 37.0, 2.2, fc="#495057", ec="#212529", lw=1.1, alpha=0.85, zorder=2))

    # Adjacent South Keycap (rEXSW2 at y_pcb = +16.05 -> v = -18.05, North edge around v = -10.5 below / keycap North edge v = -11.45)
    ax2.add_patch(patches.Rectangle((-20.8, -0.80), 8.80, 4.40, fc="#e9ecef", ec="#495057", lw=1.2, zorder=4))
    ax2.text(-16.4, 1.40, "南隣接キー\nrEXSW2", ha="center", va="center", fontsize=6.6, fontweight="bold", color="#343a40", zorder=5)

    # Projected WC1 Cradle Boss + Brass Insert (M2xL3.0) + Sub-Flush Top-Down M2x6.0mm Screw at North (v = +13.2 schematic)
    ax2.add_patch(patches.Rectangle((11.6, -9.70), 4.2, 3.90, fc="#cbd5e1", ec="#334155", lw=1.1, zorder=3))
    ax2.add_patch(patches.Rectangle((12.9, -8.80), 1.6, 3.00, fc="#e9c46a", ec="#7f5539", lw=1.0, hatch="///", zorder=4))
    ax2.add_patch(patches.Rectangle((12.3, -4.20), 2.8, 1.15, fc="#adb5bd", ec="#212529", lw=1.0, zorder=6))
    ax2.add_patch(patches.Rectangle((13.1, -10.20), 1.2, 6.00, fc="#ced4da", ec="#212529", lw=0.9, zorder=5))

    # #01 Ø22.00 mm 24-Flute Ferromagnetic 45# Steel Wheel (centered at v = 0.00, Z = -6.90)
    ax2.add_patch(patches.Circle((0.0, z_axle), 11.00, fc="#b8c4d0", ec="#1e293b", lw=1.6, alpha=0.85, zorder=5))
    for i in range(24):
        ang = np.deg2rad(i * 15.0)
        ax2.plot([10.50 * np.cos(ang), 11.00 * np.cos(ang)],
                 [z_axle + 10.50 * np.sin(ang), z_axle + 11.00 * np.sin(ang)],
                 color="#1e293b", lw=1.0, zorder=6)
    ax2.add_patch(patches.Circle((0.0, z_axle), 1.45, fc="#cbd5e1", ec="#334155", lw=1.0, zorder=6))
    ax2.add_patch(patches.Circle((0.0, z_axle), 0.99, fc="#f8fafc", ec="#0f172a", lw=1.2, zorder=7))
    ax2.text(0.0, -5.2, "Ø22.0mm 一体軸45#鋼ホイール\n外周24フルート溝 (15°ピッチ)\nJ ≈ 790 g·mm² の大慣性スピン",
             ha="center", va="center", fontsize=6.7, fontweight="bold", color="#0f172a",
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
    # Bore at Z = -11.30 mm (w = -4.40) + M2xL3.0 Brass Insert (v in [-16.40, -13.40]) + Steel M2x6mm Screw + Ø2x2mm Axial Magnet (v in [-13.08, -11.08])
    z_det = -11.30
    ax2.add_patch(patches.Rectangle((-16.40, z_det - 1.425), 5.00, 2.85, fc="#ffffff", ec="#495057", lw=0.9, zorder=5))
    ax2.add_patch(patches.Rectangle((-16.40, z_det - 1.55), 3.00, 3.10, fc="#e9c46a", ec="#7f5539", lw=1.0, hatch="///", zorder=6))
    ax2.add_patch(patches.Rectangle((-19.10, z_det - 0.98), 6.00, 1.96, fc="#ced4da", ec="#212529", lw=1.0, hatch="//", zorder=7))
    ax2.add_patch(patches.Rectangle((-20.30, z_det - 1.90), 1.20, 3.80, fc="#adb5bd", ec="#212529", lw=1.1, zorder=7))
    ax2.add_patch(patches.Rectangle((-13.08, z_det - 1.00), 2.00, 2.00, fc="#e63946", ec="#6a040f", lw=1.2, zorder=8))

    # Callouts on Panel 2
    ax2.annotate("接着剤ゼロ! 磁気デテント調整機構\n• 真鍮インサート(#10)＋鉄M2×6mmネジ(#11)\n• ネジ先端に #09 Ø2×2mm磁石が自己吸着!\n• 45#鋼24溝とのギャップ加減で\n  完全フリースピン〜明快ノッチを自在調整",
                 xy=(-12.1, z_det), xytext=(-14.2, -15.8), ha="center", va="center",
                 arrowprops=dict(arrowstyle="->", color="#d90429", lw=1.2),
                 fontsize=6.4, fontweight="bold", color="#9d0208",
                 bbox=dict(boxstyle="round,pad=0.22", fc="#ffe5ec", ec="#d90429", lw=0.9), zorder=10)

    ax2.annotate("WC1/WC2 上方向 M2×6mm 締結\n• プレート Ø4.4mm 頭逃げ穴でネジ頭沈み込み\n• #04 クレードルの真鍮インサートへ直締結\n• スナップカバー・5.5mmスペーサー完全廃止!",
                 xy=(13.7, -4.20), xytext=(5.8, 5.55), ha="center", va="center",
                 arrowprops=dict(arrowstyle="->", color="#1d3557", lw=1.15),
                 fontsize=6.5, fontweight="bold", color="#1d3557",
                 bbox=dict(boxstyle="round,pad=0.22", fc="#e0f2fe", ec="#1d3557", lw=0.9), zorder=10)

    plt.tight_layout(rect=[0, 0.01, 1, 0.94])
    out_path = ASSETS_DIR / "passive_inertia_wheel_spec.png"
    fig.savefig(out_path, dpi=200)
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
            "Magnet_D4x1mm_Diametric": (-11.5, 0.0, 9.0),
            "Magnet_Holder_PA12": (-7.5, 0.0, 9.0),
            "Bearing_DDL520ZZ_West": (-3.8, 0.0, 9.0),
            "Steel_Flywheel_22mm": (1.5, 0.0, 9.0),
            "Bearing_DDL520ZZ_East": (8.5, 0.0, 9.0),
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

        # 8. Right Top Plate + Right Main PCB Wheel Slot Cutout Close-Up
        tp = bd.Box(24.0, 30.0, 1.60, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((-2.0, 0.0, 2.20)))
        tp = (tp - bd.Box(5.60, 22.00, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((2.0, 0.0, 2.00)))
                 - bd.Cylinder(2.20, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((-4.5, 7.8, 2.00)))
                 - bd.Cylinder(2.20, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((8.1, -7.8, 2.00)))).solids()[0]
        tp.label = "Right_Top_Plate_Window"
        mp = bd.Box(24.0, 30.0, 1.60, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((-2.0, 0.0, 0.0)))
        mp = (mp - bd.Box(5.60, 23.00, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((2.0, 0.0, -0.20)))
                 - bd.Box(14.4, 7.50, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((0.9, 0.0, -0.20)))
                 - bd.Cylinder(1.20, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((-4.5, 7.8, -0.20)))
                 - bd.Cylinder(1.20, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((8.1, -7.8, -0.20)))).solids()[0]
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
        ax.text(7.52, 3.40, "【重要】径方向着磁\n(Diametric 2極)\n\n#02 ポケットへ押し込む\nだけで接着剤ゼロ固定!", ha="center", va="center", fontsize=6.7, fontweight="bold", color="#9f1239")
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
            "curcur40 アンダープレート一体軸慣性ホイール 部品構成・組立ビジュアルガイド（全12要素・接着剤＆シム＆配線ゼロ）",
            fontsize=14.2,
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

        # Top Left (cols 0..1? Let's make 2 equal wide panels using subgridspec on row 0!)
        gs_top = gs[0, :].subgridspec(1, 2, wspace=0.10)

        ax_top_l = fig.add_subplot(gs_top[0, 0])
        img_r, bg_r = _autocrop_pil(ASSETS_DIR / "render_curcur40_right_wheel.png", pad_frac=0.04, target_aspect=2.05)
        ax_top_l.set_facecolor(bg_r)
        ax_top_l.imshow(img_r, aspect="auto")
        ax_top_l.set_xticks([])
        ax_top_l.set_yticks([])
        ax_top_l.set_title(
            "A. 右キーボード アンダープレート実装外観（カバー不要・キー天面比 +0.50mm 低背プロファイル）",
            fontsize=10.2,
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
            fontsize=10.2,
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
                "cases/inertia_wheel/steel-flywheel.step\nØ22.0×4.4mm・外周24溝・質量 13.12g\nØ2.90段付き肩＆Dカット軸一体＝シム不要!",
            ),
            (
                "#02 マグネットホルダー ×1",
                "JLC3DP 造形 (MJF/SLS PA12)",
                "#1d4ed8",
                "p02",
                "cases/inertia_wheel/magnet-holder.step\nØ5.68×2.05mm・東側D穴を#01西軸へ圧入\n西ポケットに#08磁石を接着剤なしで保持",
            ),
            (
                "#03 シーソーロッカー ×1",
                "JLC3DP 造形 (MJF/SLS PA12)",
                "#1d4ed8",
                "p03",
                "cases/inertia_wheel/wheel-rocker.step\n左右DDL-520ZZ軸受＋一体Ø2.7トラニオン支点\n西アームで静音SW押下・南ボスで磁力調整",
            ),
            (
                "#04 アンダーPCBクレードル ×1",
                "JLC3DP 造形 (MJF/SLS PA12)",
                "#1d4ed8",
                "p04",
                "cases/inertia_wheel/wheel-cradle.step\nWC1/WC2の2箇所で右メイン基板裏面へ固定\n上開きU字溝と基板裏面で支点軸を挟み保持",
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
                "NMB ミネベアミツミ DDL-520ZZ\n内径Ø2×外径Ø5×幅2.3mm 標準両シールド\nパーツクリーナー脱脂で軽快回転・シム不要",
            ),
            (
                "#08 角度検出磁石 (D4×1mm) ×1",
                "市販購入品 ×1 (径方向2極着磁)",
                "#be123c",
                "mag_diam",
                "Ø4.0×厚1.0mm ネオジム磁石 (Diametric)\n#02ホルダー西穴へ入れるだけで軸端と基板窓\nで抜け止めされ接着剤ゼロで確実に保持!",
            ),
            (
                "#09 ラチェット磁石 (Ø2×2mm) ×1",
                "市販購入品 ×1 (軸方向着磁)",
                "#be123c",
                "mag_axial",
                "Ø2.0×長2.0mm 円柱ネオジム (NE280等)\n45#鋼製ホイールの24溝を直接磁気吸引!\n9個鋼球ハブ廃止＝部品1個で無摩耗ノッチ",
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
                "キーボード全17箇所すべて同一 M2×6.0mm!\nWC1/WC2固定2本＋南ラチェット調整1本\n(ラチェット用1本は磁石が付く鉄/鋼製を使用)",
            ),
            (
                "#12 右プレート＆右メイン基板窓",
                "JLCPCB 基板・プレート (カバー不要)",
                "#334155",
                "p12",
                "プレート: 5.6×22.0mm シンプル角丸長穴\nWC1/WC2はØ4.4mm頭逃げ穴でネジ頭沈み込み\nスナップカバー廃止で外観スッキリ＆組立一瞬",
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
    _draw_parts_guide_diagram()
    print("All inertia wheel previews & specification diagrams generated successfully!")


if __name__ == "__main__":
    main()
