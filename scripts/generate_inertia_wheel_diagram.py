# -*- coding: utf-8 -*-
"""
Generate engineering cross-section diagram for the Passive Magnetic Inertia Wheel Module
(curcur40-inertia-wheel: SUS304 2-way wheel + Eddy-current-free 11x Ø2.0mm ball ratchet + M2 gap adjuster + Silent middle click).
Outputs high-resolution PNG to docs/assets/passive_inertia_wheel_spec.png.
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


def main():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.8, 7.5), dpi=200)
    fig.patch.set_facecolor("#ffffff")
    fig.suptitle(
        "パッシブ磁気慣性ホイール確定仕様図（SUS304 削り出し 7.96g × 渦電流ゼロ Ø2.0鋼球×11個磁気ラチェット × 静音ミドルクリック）",
        fontsize=13.2,
        fontweight="bold",
        y=0.97,
        color="#1a1a1a",
    )

    # Module seated at F.Cu = -4.20 mm -> Z_mod = +10.30 mm corresponds to Z_global = +6.10 mm
    z_axle = 6.10  # Wheel Ø16.80 -> bottom Z = -2.30 mm, top Z = +14.50 mm (< +14.80mm 25mm trackball!)

    # =========================================================================
    # Panel 1: X-Z Front Cross-Section (17.60 mm Module inside 18.00 mm Courtyard)
    # =========================================================================
    ax1.set_title("① 正面断面図 (X–Z 軸方向積層：17.60 mm 幅・電磁部品ゼロ構成)", fontsize=11, fontweight="bold", pad=10)
    ax1.set_xlim(-11.5, 11.5)
    ax1.set_ylim(-6.5, 17.2)
    ax1.set_aspect("equal")
    ax1.set_facecolor("#f8f9fa")
    ax1.grid(True, linestyle=":", linewidth=0.5, color="#cccccc")
    ax1.set_xlabel("X 座標 [mm]（モジュール枠 ±8.80 mm = 17.60 mm ／ 18.00 mm コートヤード内）", fontsize=9.3)
    ax1.set_ylabel("curcur40 グローバル Z 座標 [mm]（ケース上縁 = 0.00 mm）", fontsize=9.3)

    ax1.axvline(-9.0, color="#d90429", linestyle="--", linewidth=1.2)
    ax1.axvline(9.0, color="#d90429", linestyle="--", linewidth=1.2)
    ax1.text(-8.85, 15.9, "-9.0mm", color="#d90429", fontsize=8, fontweight="bold")
    ax1.text(6.55, 15.9, "+9.0mm", color="#d90429", fontsize=8, fontweight="bold")

    # Main PCB & Top Plate (18.20 mm opening = ±9.10 mm)
    ax1.add_patch(patches.Rectangle((-11.2, -5.8), 22.4, 1.6, fc="#2a9d8f", ec="#1b4332", lw=1.2, alpha=0.85, zorder=2))
    ax1.text(0.0, -5.0, "curcur40-right Rev2 メインPCB / 単体評価キャリア基板 (48×32mm)", ha="center", va="center", fontsize=7.8, color="white", fontweight="bold", zorder=3)

    ax1.add_patch(patches.Rectangle((-11.2, -3.6), 2.1, 1.6, fc="#3a7ca5", ec="#16425b", lw=1.1, zorder=2))
    ax1.add_patch(patches.Rectangle((9.1, -3.6), 2.1, 1.6, fc="#3a7ca5", ec="#16425b", lw=1.1, zorder=2))
    ax1.text(-10.15, -1.3, "プレート開口\n18.20 mm", ha="center", va="bottom", fontsize=7.1, color="#16425b", fontweight="bold")

    # Base Frame (17.60 x 17.60 mm = ±8.80 mm)
    ax1.add_patch(patches.Rectangle((-8.8, -4.2), 4.6, 1.2, fc="#264653", ec="#111111", lw=1.0, zorder=3))
    ax1.add_patch(patches.Rectangle((2.5, -4.2), 6.3, 1.2, fc="#264653", ec="#111111", lw=1.0, zorder=3))

    # Hinged Inner Carriage U-Frame & Bearing Pillars
    ax1.add_patch(patches.Rectangle((-6.5, -2.5), 2.4, 11.4, fc="#dee2e6", ec="#495057", lw=1.0, zorder=3))
    ax1.add_patch(patches.Rectangle((6.2, -2.5), 2.4, 11.4, fc="#dee2e6", ec="#495057", lw=1.0, zorder=3))

    # Shaft Ø2.0 mm (SUS304 non-magnetic, X = -6.8 to +8.6)
    ax1.add_patch(patches.Rectangle((-6.8, z_axle - 1.0), 15.4, 2.0, fc="#f8f9fa", ec="#343a40", lw=1.1, zorder=5))
    ax1.text(-0.85, z_axle, "SUS304 平行軸 Ø2.0", ha="center", va="center", fontsize=6.4, fontweight="bold", color="#212529", zorder=9)

    # Miniature Degreased Stainless Bearings (DDL-520 / MR52: Ø2 x Ø5 x 2.5mm)
    ax1.add_patch(patches.Rectangle((-6.45, z_axle - 2.5), 2.5, 5.0, fc="#ffffff", ec="#0077b6", lw=1.3, zorder=4))
    ax1.add_patch(patches.Rectangle((6.30, z_axle - 2.5), 2.5, 5.0, fc="#ffffff", ec="#0077b6", lw=1.3, zorder=4))
    ax1.text(-5.20, z_axle + 2.85, "脱脂MR52\n(DDL-520)", ha="center", va="bottom", fontsize=6.5, color="#0077b6", fontweight="bold")
    ax1.text(7.55, z_axle + 2.85, "脱脂MR52\n(DDL-520)", ha="center", va="bottom", fontsize=6.5, color="#0077b6", fontweight="bold")

    # West Sensor Sub-PCB (8.8 x 8.8 x 0.8 mm) + AS5600-ASOT (SOIC-8) + Ø3x1.0mm Diametric Magnet
    ax1.add_patch(patches.Rectangle((-8.75, z_axle - 4.4), 0.8, 8.8, fc="#2a9d8f", ec="#1b4332", lw=1.0, zorder=4))
    ax1.add_patch(patches.Rectangle((-7.95, z_axle - 2.45), 1.35, 4.9, fc="#212529", ec="#000000", lw=1.0, zorder=5))
    ax1.text(-7.28, z_axle, "AS5600\n12-bit I2C", ha="center", va="center", fontsize=5.5, color="white", rotation=90, zorder=6)
    ax1.add_patch(patches.Rectangle((-6.35, z_axle - 1.5), 1.0, 3.0, fc="#e63946", ec="#6a040f", lw=1.0, zorder=6))
    ax1.annotate("径方向磁石 Ø3×1mm\n(非接触12-bit検出)", xy=(-6.35, z_axle + 1.5), xytext=(-11.2, 12.6),
                 arrowprops=dict(arrowstyle="->", color="#6a040f", lw=1.0), fontsize=7.0, fontweight="bold", color="#6a040f")

    # SUS304 Silver Stainless Flywheel (Ø16.80 x 5.60 mm, X = -3.65 to +1.95, mass 7.96 g)
    ax1.add_patch(patches.Rectangle((-3.65, z_axle - 8.4), 5.6, 16.8, fc="#d8dee9", ec="#4c566a", lw=1.5, zorder=6))
    ax1.add_patch(patches.Rectangle((-1.50, z_axle + 7.9), 1.3, 0.52, fc="#f8f9fa", ec="#4c566a", lw=0.9, zorder=7))
    ax1.add_patch(patches.Rectangle((-1.50, z_axle - 8.42), 1.3, 0.52, fc="#f8f9fa", ec="#4c566a", lw=0.9, zorder=7))
    ax1.text(-0.85, z_axle + 4.4, "SUS304 ステンレス\n削り出しホイール\nØ16.8×5.6mm (7.96g)\n(36溝＋中央2way溝)", ha="center", va="center", fontsize=6.7, fontweight="bold", color="#1f2937", zorder=8)

    # Coaxial Eddy-Current-Free Resin Ratchet Hub (Ø12.40 x 3.75 mm, X = +2.35 to +6.10) + 11x Ø2.00mm SUJ2 Steel Balls
    ax1.add_patch(patches.Rectangle((2.35, z_axle - 6.2), 3.75, 12.4, fc="#a8dadc", ec="#1d3557", lw=1.2, zorder=6))
    ax1.add_patch(patches.Circle((4.225, z_axle + 5.1), 1.0, fc="#495057", ec="#111111", lw=0.9, zorder=7))
    ax1.add_patch(patches.Circle((4.225, z_axle - 5.1), 1.0, fc="#495057", ec="#111111", lw=0.9, zorder=7))
    ax1.annotate("絶縁SLAハブ Ø12.4×3.75mm\n＋ Ø2.0鋼球×11個 (渦電流ゼロ!)", xy=(4.225, z_axle + 6.2), xytext=(4.8, 14.3),
                 arrowprops=dict(arrowstyle="->", color="#1d3557", lw=1.1), fontsize=7.0, fontweight="bold", color="#1d3557", ha="center",
                 bbox=dict(boxstyle="round,pad=0.2", fc="#e0fbfc", ec="#1d3557", lw=0.8))

    # =========================================================================
    # Panel 2: Y-Z Side Section (Hinged Silent Click + North-East M2 Magnet Gap Adjuster)
    # =========================================================================
    ax2.set_title("② 側面機構図 (Y–Z 断面：一体揺動静音クリック ＆ M2ネジ磁力調整機構)", fontsize=11, fontweight="bold", pad=10)
    ax2.set_xlim(-10.8, 11.2)
    ax2.set_ylim(-6.5, 17.2)
    ax2.set_aspect("equal")
    ax2.set_facecolor("#f8f9fa")
    ax2.grid(True, linestyle=":", linewidth=0.5, color="#cccccc")
    ax2.set_xlabel("Y 座標 [mm]（北側 -Y ヒンジ軸＆磁力調整ネジ ／ 南側 +Y 静音マイクロスイッチ）", fontsize=9.3)
    ax2.set_ylabel("curcur40 グローバル Z 座標 [mm]", fontsize=9.3)

    ax2.axvline(-8.8, color="#d90429", linestyle="--", linewidth=1.2)
    ax2.axvline(8.8, color="#d90429", linestyle="--", linewidth=1.2)

    # Main PCB & Base Frame (17.60 mm = ±8.80 mm)
    ax2.add_patch(patches.Rectangle((-10.5, -5.8), 21.3, 1.6, fc="#2a9d8f", ec="#1b4332", lw=1.1, alpha=0.85, zorder=1))
    ax2.add_patch(patches.Rectangle((-8.8, -4.2), 17.6, 1.0, fc="#264653", ec="#111111", lw=1.0, zorder=2))

    # North Hinge Pin Ø2.0 mm at Y = -6.85, Z = -2.05
    ax2.add_patch(patches.Circle((-6.85, -2.05), 1.0, fc="#ffffff", ec="#212529", lw=1.5, zorder=6))
    ax2.text(-7.2, -3.15, "北端ヒンジ軸 Ø2.0\n(Y=-6.85mm)", ha="center", va="top", fontsize=6.9, fontweight="bold", color="#212529",
             bbox=dict(boxstyle="round,pad=0.15", fc="#ffffff", ec="#adb5bd", lw=0.7), zorder=8)

    # Unitized Inner Carriage
    carriage_poly = patches.Polygon(
        [[-8.3, -2.8], [8.3, -1.2], [8.3, 6.8], [-8.3, 6.8]],
        closed=True, fc="#dee2e6", ec="#495057", lw=1.2, alpha=0.55, zorder=2
    )
    ax2.add_patch(carriage_poly)
    ax2.annotate("一体揺動キャリッジ\n(クリック押下中も磁気ギャップ不変!)",
                 xy=(-2.8, 6.8), xytext=(1.2, 15.1),
                 arrowprops=dict(arrowstyle="->", color="#1d3557", lw=1.1),
                 fontsize=7.1, fontweight="bold", color="#1d3557",
                 bbox=dict(boxstyle="round,pad=0.22", fc="#e0fbfc", ec="#1d3557", lw=0.9), zorder=9)

    # Kailh Square Silent Micro Switch (6.2 x 6.2 x 4.3 mm) at South-East Y = +5.70
    ax2.add_patch(patches.Rectangle((2.6, -4.2), 6.2, 2.7, fc="#f4a261", ec="#9c4100", lw=1.2, zorder=4))
    ax2.add_patch(patches.Rectangle((4.9, -1.5), 1.6, 0.55, fc="#e63946", ec="#6a040f", lw=1.0, zorder=5))
    ax2.annotate("静音マイクロSW (Kailh Silent 6.2×6.2)\nスピン停止時に誤爆しない適切荷重!",
                 xy=(5.7, -2.8), xytext=(-0.2, -5.6),
                 arrowprops=dict(arrowstyle="->", color="#9c4100", lw=1.1),
                 fontsize=6.9, fontweight="bold", color="#7f2704",
                 bbox=dict(boxstyle="round,pad=0.18", fc="#fff3cd", ec="#d97706", lw=0.8), zorder=9)

    # Adjacent South Keycap boundary (rEXSW2 North edge at Y = +10.45 mm -> 2.15 mm clearance from Y = +8.30 mm wheel!)
    ax2.add_patch(patches.Rectangle((10.45, -1.0), 0.75, 8.5, fc="#ced4da", ec="#495057", lw=1.0, zorder=3))
    ax2.annotate("南キー余裕\n2.15mm", xy=(8.3, z_axle), xytext=(9.38, z_axle + 4.8),
                 arrowprops=dict(arrowstyle="<->", color="#2b9348", lw=1.1),
                 fontsize=6.8, fontweight="bold", color="#1b4332", ha="center", zorder=8)

    # Wheel Circle (Ø16.80 mm at Y = -0.10, Z = +6.10) + Insulated 11-Ball Ratchet Hub (Ø12.40 mm, R_orbit = 5.10 mm)
    wy, wz = -0.10, z_axle
    ax2.add_patch(patches.Circle((wy, wz), 8.4, fc="#d8dee9", ec="#4c566a", lw=1.6, alpha=0.65, zorder=3))
    for a in np.linspace(0, 2 * np.pi, 36, endpoint=False):
        ax2.plot([wy + 7.95 * np.cos(a), wy + 8.40 * np.cos(a)],
                 [wz + 7.95 * np.sin(a), wz + 8.40 * np.sin(a)], color="#4c566a", lw=0.8, zorder=4)

    ax2.add_patch(patches.Circle((wy, wz), 6.2, fc="#a8dadc", ec="#1d3557", lw=1.1, alpha=0.90, zorder=4))
    for a in np.linspace(0, 2 * np.pi, 11, endpoint=False):
        bx = wy + 5.10 * np.cos(a)
        bz = wz + 5.10 * np.sin(a)
        ax2.add_patch(patches.Circle((bx, bz), 1.00, fc="#495057", ec="#111111", lw=0.75, zorder=5))
    ax2.add_patch(patches.Circle((wy, wz), 1.0, fc="#ffffff", ec="#212529", lw=1.2, zorder=6))
    ax2.text(wy, wz + 6.95, "Ø16.8 SUS304\n(頂点 Z=+14.5mm)", ha="center", va="center", fontsize=7.3, fontweight="bold", color="#1f2937", zorder=7)

    # North-East M2 Magnet Gap Adjuster Boss at Z_global = +1.45 mm (Z_mod = +5.65 mm), Y = -8.6..-4.8 mm
    mz = 1.45
    ax2.add_patch(patches.Rectangle((-6.25, mz - 1.0), 1.5, 2.0, fc="#e63946", ec="#6a040f", lw=1.1, zorder=7))
    ax2.add_patch(patches.Rectangle((-8.75, mz - 0.85), 2.5, 1.7, fc="#adb5bd", ec="#212529", lw=1.1, hatch="///", zorder=6))
    ax2.annotate("", xy=(-6.3, mz), xytext=(-4.2, mz),
                 arrowprops=dict(arrowstyle="<->", color="#d90429", lw=1.4), zorder=8)

    ax2.annotate("北東 M2イモネジ磁力調整 (0.4mm/周)\n・締める → コリコリ強ノッチ\n・緩める → 3〜7秒の慣性スピン!",
                 xy=(-6.8, mz + 1.0), xytext=(-10.5, 14.3),
                 arrowprops=dict(arrowstyle="->", color="#d90429", lw=1.2),
                 fontsize=7.0, fontweight="bold", color="#9d0208",
                 bbox=dict(boxstyle="round,pad=0.22", fc="#ffe5ec", ec="#d90429", lw=0.9), zorder=9)

    plt.tight_layout(rect=[0, 0.01, 1, 0.94])
    out_path = ASSETS_DIR / "passive_inertia_wheel_spec.png"
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    print(f"Saved {out_path}")

    # =========================================================================
    # Second Diagram: Standard vs Low-Profile Sunk Z-Height Comparison
    # =========================================================================
    fig2, (bx1, bx2) = plt.subplots(1, 2, figsize=(15.2, 6.6), dpi=200)
    fig2.patch.set_facecolor("#ffffff")
    fig2.suptitle(
        "curcur40-right ホイール高さ比較：タイプA（基板無加工ポン付け） vs タイプB（マウスホイール同等・沈み込み版）",
        fontsize=13.0,
        fontweight="bold",
        y=0.97,
        color="#1a1a1a",
    )

    for ax, is_sunk in [(bx1, False), (bx2, True)]:
        ax.set_xlim(-14.5, 22.5)
        ax.set_ylim(-14.0, 17.0)
        ax.set_aspect("equal")
        ax.set_facecolor("#f8f9fa")
        ax.grid(True, linestyle=":", linewidth=0.5, color="#cccccc")
        ax.set_xlabel("Y 座標 [mm]（北 -Y ── ホイール rEXSW1 ── 南 +Y キー rEXSW2）", fontsize=9.2)
        ax.set_ylabel("curcur40 グローバル Z 座標 [mm]（ケース上縁 = 0.00 mm）", fontsize=9.2)

        # Case Rim reference Z = 0.00 mm & Case Inner Cavity indicator
        ax.axhline(0.0, color="#6c757d", linestyle="-.", linewidth=0.9)
        ax.text(-14.0, 0.35, "ケース上縁リム Z=0.00", fontsize=7.2, color="#495057")
        ax.add_patch(patches.Rectangle((-14.5, -14.0), 37.0, 1.3, fc="#adb5bd", ec="#495057", lw=0.9, alpha=0.5, zorder=1))
        ax.text(4.0, -13.35, "既存ケース内底面は Z = -20.5 mm（さらに下方へ 10 mm 以上の余裕あり・ケース無改造）",
                ha="center", va="center", fontsize=7.3, fontweight="bold", color="#343a40")

        # Keycap center reference line Z = +1.40 mm & Keycap top Z = +3.60 mm
        ax.axhline(1.40, color="#2b9348", linestyle="--", linewidth=1.3, zorder=8)
        ax.axhline(3.60, color="#0077b6", linestyle=":", linewidth=1.0, zorder=8)

        # Adjacent South Switch + Keycap (rEXSW2 centered at y = +19.05 -> North cap edge at +10.95)
        ax.add_patch(patches.Rectangle((10.95, -0.80), 11.0, 4.40, fc="#e9ecef", ec="#212529", lw=1.3, zorder=5))
        ax.text(16.45, 1.40, "隣接キーキャップ\n(Z = -0.8〜+3.6)\n中央 Z = +1.4mm", ha="center", va="center", fontsize=6.9, fontweight="bold", color="#212529",
                bbox=dict(boxstyle="round,pad=0.15", fc="#e9ecef", ec="none", alpha=0.92), zorder=9)

        if not is_sunk:
            ax.set_title("タイプA：標準ポン付け版（メインPCB開口なし：頂点 Z = +14.50 mm）", fontsize=10.8, fontweight="bold", pad=9)
            # Continuous Main PCB (-5.80..-4.20) & Top Plate (-3.60..-2.00) with 18.2mm cutout
            ax.add_patch(patches.Rectangle((-14.5, -5.80), 37.0, 1.60, fc="#2a9d8f", ec="#1b4332", lw=1.1, zorder=2))
            ax.add_patch(patches.Rectangle((-14.5, -3.60), 5.4, 1.60, fc="#3a7ca5", ec="#16425b", lw=1.1, zorder=2))
            ax.add_patch(patches.Rectangle((9.1, -3.60), 13.4, 1.60, fc="#3a7ca5", ec="#16425b", lw=1.1, zorder=2))
            ax.add_patch(patches.Rectangle((-8.8, -4.20), 17.6, 1.40, fc="#264653", ec="#111111", lw=1.0, zorder=3))
            wz = 6.10
            ax.annotate("キー上面から +10.9 mm 突出\n(やや背が高い)", xy=(0.0, wz + 8.4), xytext=(-13.5, 13.5),
                        arrowprops=dict(arrowstyle="->", color="#d90429", lw=1.2),
                        fontsize=7.6, fontweight="bold", color="#9d0208",
                        bbox=dict(boxstyle="round,pad=0.22", fc="#ffe5ec", ec="#d90429", lw=0.9), zorder=10)
        else:
            ax.set_title("タイプB：ロープロファイル沈み込み版（マウスホイール同等：頂点 Z = +9.80 mm）", fontsize=10.8, fontweight="bold", pad=9, color="#1b4332")
            # Main PCB with 18.2mm inner cutout (outer dimensions 100% unchanged!)
            ax.add_patch(patches.Rectangle((-14.5, -5.80), 5.4, 1.60, fc="#2a9d8f", ec="#1b4332", lw=1.1, zorder=2))
            ax.add_patch(patches.Rectangle((9.1, -5.80), 13.4, 1.60, fc="#2a9d8f", ec="#1b4332", lw=1.1, zorder=2))
            ax.add_patch(patches.Rectangle((-14.5, -3.60), 5.4, 1.60, fc="#3a7ca5", ec="#16425b", lw=1.1, zorder=2))
            ax.add_patch(patches.Rectangle((9.1, -3.60), 13.4, 1.60, fc="#3a7ca5", ec="#16425b", lw=1.1, zorder=2))
            # Sunk Under-PCB Basket + North Mounting Lug + Spacer Post
            ax.add_patch(patches.Rectangle((-8.8, -10.10), 17.6, 1.20, fc="#264653", ec="#111111", lw=1.0, zorder=3))
            ax.add_patch(patches.Rectangle((-13.8, -10.10), 5.0, 4.29, fc="#264653", ec="#111111", lw=1.0, zorder=3))
            ax.add_patch(patches.Rectangle((-13.0, -5.81), 3.4, 2.20, fc="#264653", ec="#111111", lw=1.0, zorder=3))
            wz = 1.40
            ax.annotate("キー上面から +6.2 mm 浮き出し!\n(一般的なマウスホイールと同等・\n ホイール中心 = キー中央 Z=+1.4mm)",
                        xy=(0.0, wz + 8.4), xytext=(-13.8, 12.2),
                        arrowprops=dict(arrowstyle="->", color="#1b4332", lw=1.3),
                        fontsize=7.6, fontweight="bold", color="#1b4332",
                        bbox=dict(boxstyle="round,pad=0.25", fc="#d8f3dc", ec="#2b9348", lw=1.0), zorder=10)
            ax.text(0.0, -11.3, "メインPCB・プレート内窓 18.5×18.5mm 通過（基板・プレート外形は 100% 変更なし）",
                    ha="center", va="center", fontsize=7.1, fontweight="bold", color="#264653")

        # Draw SUS304 Wheel Ø16.80 mm at (-0.10, wz)
        wy = -0.10
        ax.add_patch(patches.Circle((wy, wz), 8.40, fc="#d8dee9", ec="#4c566a", lw=1.6, alpha=0.88, zorder=6))
        ax.add_patch(patches.Circle((wy, wz), 5.10, fc="none", ec="#1d3557", lw=0.9, linestyle="--", zorder=7))
        ax.add_patch(patches.Circle((wy, wz), 1.05, fc="#ffffff", ec="#212529", lw=1.2, zorder=8))
        ax.plot([wy], [wz], marker="+", color="#d90429", markersize=8, markeredgewidth=1.5, zorder=9)
        ax.text(wy, wz - 2.6, f"軸中心 Z = {wz:+.2f} mm\n頂点 Z = {wz+8.4:+.2f} mm",
                ha="center", va="center", fontsize=7.5, fontweight="bold", color="#1f2937",
                bbox=dict(boxstyle="round,pad=0.18", fc="#ffffff", ec="#adb5bd", lw=0.8), zorder=9)

    plt.tight_layout(rect=[0, 0.035, 1, 0.93])
    out_comp = ASSETS_DIR / "inertia_wheel_height_comparison.png"
    fig2.savefig(out_comp, dpi=200)
    plt.close(fig2)
    print(f"Saved {out_comp}")

    generate_parts_guide()


def _autocrop_pil(img_path: Path, pad_frac: float = 0.08) -> tuple[np.ndarray, tuple[float, float, float]]:
    """Crop uniform background (and light KiCad drop shadow if white bg) around rendered object."""
    im = Image.open(img_path).convert("RGB")
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
    """Build helper 3D STEP models for off-the-shelf components & render all thumbnails in one cadgen job."""
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

        # 1b. 3D Exploded Module Assembly (cleanly separated along X & Z to reveal all internal parts!)
        mod_parts = giw.assemble_module_parts(origin=(0.0, 0.0, 0.0), sunk=False)
        exp_offsets = {{
            "AS5600_Sensor_SubPCB": (-13.5, 0.0, 7.5),
            "AS5600_SOIC8_IC": (-12.5, 0.0, 7.5),
            "Diametric_Magnet_3x1mm": (-8.5, 0.0, 7.5),
            "Bearing_MR52_West": (-5.0, 0.0, 7.5),
            "SUS304_Flywheel_16p8mm": (-0.5, 0.0, 7.5),
            "SUS316_Axle_Shaft_2mm": (1.0, 0.0, 7.5),
            "Ratchet_Hub_Resin": (6.2, 0.0, 7.5),
            "Bearing_MR52_East": (12.2, 0.0, 7.5),
            "Wheel_Hinged_Carriage": (0.0, 0.0, -2.5),
            "M2_Magnet_Adjuster_And_NdFeB": (0.0, -5.8, -2.5),
            "Wheel_Base_Frame": (0.0, 0.0, -10.5),
            "Kailh_Silent_Switch_6x6x4p3": (0.0, 0.0, -8.0),
            "Hinge_Pin_SUS304_2mm": (-10.5, 0.0, -10.5),
        }}
        exploded_children = []
        for s in mod_parts:
            lbl = s.label
            if lbl.startswith("Steel_Ball_2mm_"):
                dx, dy, dz = (6.2, 0.0, 7.5)
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

        # 4. Kailh Square Silent Switch (6.2 x 6.2 x 4.3 mm)
        sw_base = bd.Box(6.2, 6.2, 2.6, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((0, 0, 2.5)))
        sw_base.label = "SW_Base"
        sw_top = bd.Box(6.0, 6.0, 1.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((0, 0, 5.1)))
        sw_top.label = "SW_Cover"
        sw_btn = bd.Cylinder(1.45, 0.65, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((0, 0, 6.3)))
        sw_btn.label = "SW_Red_Button"
        pin_a = bd.Box(0.6, 0.4, 2.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((-2.5, 0, 0.0)))
        pin_a.label = "SW_Pin1"
        pin_b = bd.Box(0.6, 0.4, 2.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((2.5, 0, 0.0)))
        pin_b.label = "SW_Pin2"
        bd.export_step(bd.Compound(children=[sw_base, sw_top, sw_btn, pin_a, pin_b]), str(out / "p10_silent_sw.step"))

        # 5. 2x Open Degreased Miniature Bearings (DDL-520 / MR52: Ø5 x Ø2 x 2.5 mm)
        brg_parts = []
        for bi, bx in enumerate([-3.4, 3.4]):
            outer_r = (
                bd.Cylinder(2.50, 2.50, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
                - bd.Cylinder(2.02, 2.60, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((0, 0, -0.05)))
            ).moved(bd.Location((bx, 0, 0)))
            outer_r.label = f"OuterRace_{{bi}}"
            inner_r = (
                bd.Cylinder(1.42, 2.50, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
                - bd.Cylinder(1.00, 2.60, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((0, 0, -0.05)))
            ).moved(bd.Location((bx, 0, 0)))
            inner_r.label = f"InnerRace_{{bi}}"
            brg_parts.extend([outer_r, inner_r])
            for k in range(8):
                a = math.radians(k * 45.0)
                ball = bd.Sphere(0.32).moved(bd.Location((bx + 1.72 * math.cos(a), 1.72 * math.sin(a), 1.25)))
                ball.label = f"BrgBall_{{bi}}_{{k}}"
                brg_parts.append(ball)
        bd.export_step(bd.Compound(children=brg_parts), str(out / "p12_bearings.step"))

        # 6. 11x Ø2.00 mm SUJ2 Steel Balls in ring
        balls_11 = []
        for k in range(11):
            a = math.radians(k * (360.0 / 11.0))
            sp = bd.Sphere(1.00).moved(bd.Location((5.1 * math.cos(a), 5.1 * math.sin(a), 1.00)))
            sp.label = f"SUJ2_Ball_{{k:02d}}"
            balls_11.append(sp)
        bd.export_step(bd.Compound(children=balls_11), str(out / "p13_steel_balls.step"))

        # 7. Axle Shaft (Ø2.0 x 14.2 mm) & Hinge Pin (Ø2.0 x 17.2 mm)
        sh = bd.Cylinder(1.00, 14.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90)
        sh = bd.chamfer(sh.edges(), length=0.18)
        sh.label = "Axle_Shaft"
        bd.export_step(sh, str(out / "p14_axle_shaft.step"))

        hp = bd.Cylinder(1.00, 17.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90)
        hp = bd.chamfer(hp.edges(), length=0.18)
        hp.label = "Hinge_Pin"
        bd.export_step(hp, str(out / "p15_hinge_pin.step"))

        # 8. M2 Stainless Set Screw (イモネジ M2 x 4.5 mm with hex socket & thread rings)
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
    asm_dir = WORKSPACE / "cases" / "assemblies"
    render_specs = [
        ("mod_west", tmp_dir / "mod_exploded.step", "iso", "parts", 1400, 1000),
        ("p01", parts_dir / "sus304-flywheel.step", "iso", "shaded", 720, 520),
        ("p02", parts_dir / "ratchet-hub-11ball.step", "iso", "shaded", 720, 520),
        ("p03", tmp_dir / "p03_carriage.step", "iso", "shaded", 720, 520),
        ("p04a", parts_dir / "wheel-base-frame.step", "iso", "shaded", 720, 520),
        ("p04b", parts_dir / "wheel-base-frame-sunk.step", "iso", "shaded", 720, 520),
        ("p05", parts_dir / "eval-pod-stand.step", "iso", "shaded", 720, 520),
        ("p08", tmp_dir / "p08_as5600.step", "iso", "parts", 720, 520),
        ("p09", tmp_dir / "p09_rp2040_zero.step", "iso", "parts", 720, 520),
        ("p10", tmp_dir / "p10_silent_sw.step", "iso", "parts", 720, 520),
        ("p12", tmp_dir / "p12_bearings.step", "35:48", "parts", 720, 520),
        ("p13", tmp_dir / "p13_steel_balls.step", "35:45", "parts", 720, 520),
        ("p14", tmp_dir / "p14_axle_shaft.step", "iso", "shaded", 720, 520),
        ("p15", tmp_dir / "p15_hinge_pin.step", "iso", "shaded", 720, 520),
        ("p18", tmp_dir / "p18_m2_adjuster.step", "iso", "shaded", 720, 520),
        ("p19", tmp_dir / "p19_screws_feet.step", "35:42", "parts", 720, 520),
    ]

    jobs = []
    out_map: dict[str, Path] = {}
    for key, target, cam, disp, w, h in render_specs:
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
    # Left: JST SH 6P housing
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
        # Tinned stripped end
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
        # Disc viewed tilted + top plan showing left N (red) / right S (blue) split across diameter!
        # Left: 3D cylinder side-front
        ax.add_patch(patches.Wedge((3.1, 3.45), 1.85, 90, 270, fc="#ef4444", ec="#7f1d1d", lw=1.4, zorder=4))
        ax.add_patch(patches.Wedge((3.1, 3.45), 1.85, -90, 90, fc="#3b82f6", ec="#1e3a8a", lw=1.4, zorder=4))
        ax.plot([3.1, 3.1], [1.60, 5.30], color="#ffffff", lw=1.6, linestyle="--", zorder=5)
        ax.text(2.18, 3.45, "N", ha="center", va="center", fontsize=12, fontweight="bold", color="white", zorder=6)
        ax.text(4.02, 3.45, "S", ha="center", va="center", fontsize=12, fontweight="bold", color="white", zorder=6)
        ax.annotate("", xy=(5.15, 3.45), xytext=(1.05, 3.45), arrowprops=dict(arrowstyle="<->", color="#111827", lw=1.2), zorder=3)
        ax.text(3.1, 1.02, "Ø3.0 × 厚1.0mm", ha="center", va="center", fontsize=7.3, fontweight="bold", color="#1e293b")
        ax.add_patch(patches.FancyBboxPatch((5.55, 1.55), 4.05, 3.75, boxstyle="round,pad=0.18", fc="#fff1f2", ec="#be123c", lw=1.2))
        ax.text(7.58, 3.42, "【重要】径方向着磁\n(Diametric 2極)\n\n直径の左右で N/S が\n分かれた AS5600専用品!", ha="center", va="center", fontsize=6.9, fontweight="bold", color="#9f1239")
    else:
        # Axial cylinder: Top half N (red), Bottom half S (blue) along thickness!
        ax.add_patch(patches.Rectangle((1.75, 3.45), 2.7, 1.45, fc="#ef4444", ec="#7f1d1d", lw=1.4, zorder=4))
        ax.add_patch(patches.Rectangle((1.75, 2.00), 2.7, 1.45, fc="#3b82f6", ec="#1e3a8a", lw=1.4, zorder=4))
        ax.add_patch(patches.Ellipse((3.10, 4.90), 2.7, 0.68, fc="#f87171", ec="#7f1d1d", lw=1.3, zorder=5))
        ax.text(3.10, 4.10, "N", ha="center", va="center", fontsize=11.5, fontweight="bold", color="white", zorder=6)
        ax.text(3.10, 2.68, "S", ha="center", va="center", fontsize=11.5, fontweight="bold", color="white", zorder=6)
        ax.text(3.10, 1.02, "Ø1.5〜2.0 × 厚1.5mm", ha="center", va="center", fontsize=7.3, fontweight="bold", color="#1e293b")
        ax.add_patch(patches.FancyBboxPatch((5.35, 1.55), 4.25, 3.75, boxstyle="round,pad=0.18", fc="#eff6ff", ec="#1d4ed8", lw=1.2))
        ax.text(7.48, 3.42, "通常の軸方向着磁\n(Axial 円柱ネオジム)\n\n厚みの上下で N/S が\n分かれた一般的な磁石", ha="center", va="center", fontsize=6.9, fontweight="bold", color="#1e3a8a")


def generate_parts_guide():
    """Generate docs/assets/inertia_wheel_parts_guide.png with 3D callouts + 20-card visual BOM."""
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp_dir = Path(tmp_s)
        rendered = _build_temp_part_renders(tmp_dir)

        fig = plt.figure(figsize=(16.6, 22.4), dpi=160)
        fig.patch.set_facecolor("#ffffff")

        # Master Title Banner
        fig.text(
            0.50,
            0.983,
            "パッシブ磁気慣性ホイール 部品名称・構成図鑑（共通呼称マップ #01〜#19）",
            ha="center",
            va="center",
            fontsize=16.0,
            fontweight="bold",
            color="#0f172a",
        )
        fig.text(
            0.50,
            0.968,
            "本ビルドガイドおよび設計・組み立ての会話では、以下の「番号＋太字の部品名（例：#03 キャリッジ、#16 角度磁石）」を共通名称として使用します",
            ha="center",
            va="center",
            fontsize=10.0,
            fontweight="bold",
            color="#475569",
        )

        # =====================================================================
        # Upper Section: 2 Assembly Callout Panels (North-East Pod + South-West Module)
        # =====================================================================
        ax_pod = fig.add_axes([0.020, 0.700, 0.470, 0.250])
        ax_mod = fig.add_axes([0.510, 0.700, 0.470, 0.250])

        # --- Left Panel: Full Standalone Pod (North-East ISO) ---
        pod_img, pod_bg = _autocrop_pil(ASSETS_DIR / "render_inertia_wheel_eval_pod.png", pad_frac=0.22)
        ph, pw, _ = pod_img.shape
        ax_pod.set_facecolor(pod_bg)
        ax_pod.imshow(pod_img, extent=[0, 100, 0, 100], aspect="auto", zorder=1)
        ax_pod.set_xlim(-6, 106)
        ax_pod.set_ylim(-6, 106)
        ax_pod.set_xticks([])
        ax_pod.set_yticks([])
        for sp in ax_pod.spines.values():
            sp.set_edgecolor("#94a3b8")
            sp.set_linewidth(1.3)
        ax_pod.set_title("【全体配置 A】単体評価ポッド全体（北東アイソメ図）", fontsize=11.5, fontweight="bold", color="#0f172a", pad=7)

        pod_callouts = [
            # (target_x, target_y, text_x, text_y, label, border_color)
            (59.5, 76.0, 44.0, 97.5, "#01 フライホイール", "#1d3557"),
            (66.5, 63.0, 84.0, 97.0, "#02 11球ハブ (+#13 鋼球)", "#1d3557"),
            (72.5, 57.5, 89.0, 83.0, "#03 キャリッジ", "#1d3557"),
            (69.5, 51.5, 84.5, 68.5, "#12 ベアリング + #14 軸", "#005f73"),
            (73.2, 39.5, 89.5, 53.0, "#10 静音スイッチ", "#1b4332"),
            (63.8, 30.8, 84.0, 35.5, "#04A 標準ベース枠 + #15 ピン", "#1d3557"),
            (57.2, 23.8, 84.5, 19.0, "#19 固定M2ネジ穴 (四隅)", "#9b2226"),
            (56.0, 14.5, 54.0, 1.5, "#05 ポッド台座", "#1d3557"),
            (39.0, 32.0, 13.0, 6.5, "#06 キャリア基板", "#1b4332"),
            (37.5, 48.5, 14.5, 24.0, "#11 センサー4芯線 接続先(J1)", "#1b4332"),
            (29.5, 64.0, 11.5, 86.0, "#09 RP2040-Zero", "#1b4332"),
            (59.6, 42.2, 16.5, 43.0, "#18 磁力調整ネジ (+#17 磁石)", "#9b2226"),
        ]
        for tx, ty, lx, ly, txt, col in pod_callouts:
            ax_pod.annotate(
                txt,
                xy=(tx, ty),
                xytext=(lx, ly),
                ha="center",
                va="center",
                fontsize=7.6,
                fontweight="bold",
                color="#0f172a",
                bbox=dict(boxstyle="round,pad=0.25", fc="#ffffff", ec=col, lw=1.3),
                arrowprops=dict(arrowstyle="-|>", color=col, lw=1.35, shrinkA=0, shrinkB=1),
                zorder=8,
            )

        # --- Right Panel: 3D Exploded Module Assembly ---
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
        ax_mod.set_title("【全体配置 B】ホイールモジュール 3D分解構造図（内部パーツ展開）", fontsize=11.5, fontweight="bold", color="#0f172a", pad=7)

        mod_callouts = [
            (28.5, 81.5, 13.5, 96.5, "#07 センサー基板 + #08 IC", "#1b4332"),
            (38.0, 75.5, 12.5, 81.0, "#16 角度磁石 (径方向)", "#9b2226"),
            (43.0, 72.5, 13.5, 66.0, "#12 ベアリング (西側)", "#005f73"),
            (49.5, 76.0, 48.0, 97.5, "#01 フライホイール", "#1d3557"),
            (65.0, 69.0, 84.5, 96.5, "#02 11球ハブ + #13 鋼球", "#005f73"),
            (77.5, 58.0, 88.0, 80.5, "#12 ベアリング (東側)", "#005f73"),
            (58.5, 65.5, 88.0, 65.0, "#14 回転シャフト (中心軸)", "#005f73"),
            (59.0, 44.0, 88.5, 47.0, "#03 キャリッジ", "#1d3557"),
            (43.5, 42.5, 15.5, 46.5, "#18 磁力調整ネジ + #17 磁石", "#9b2226"),
            (34.5, 25.0, 13.5, 28.0, "#15 ヒンジピン (北端軸)", "#005f73"),
            (55.0, 14.0, 48.0, 1.5, "#04A 標準ベース枠", "#1d3557"),
            (68.5, 22.0, 88.0, 21.0, "#10 静音スイッチ (南東)", "#1b4332"),
        ]
        for tx, ty, lx, ly, txt, col in mod_callouts:
            ax_mod.annotate(
                txt,
                xy=(tx, ty),
                xytext=(lx, ly),
                ha="center",
                va="center",
                fontsize=7.7,
                fontweight="bold",
                color="#0f172a",
                bbox=dict(boxstyle="round,pad=0.26", fc="#ffffff", ec=col, lw=1.3),
                arrowprops=dict(arrowstyle="-|>", color=col, lw=1.35, shrinkA=0, shrinkB=2),
                zorder=8,
            )

        # =====================================================================
        # Lower Section: 5 Rows x 4 Columns = 20 Individual Part Cards
        # =====================================================================
        C_CUSTOM = ("#1d3557", "#f1f5f9")
        C_ELEC = ("#1b4332", "#ecfdf5")
        C_MECH = ("#005f73", "#ecfeff")
        C_MAG = ("#9b2226", "#fff1f2")

        cards = [
            # (code_title, img_source, qty_spec, route_spec, colors)
            ("#01  フライホイール", rendered["p01"], "数量: 1個 ｜ Ø16.8 × 5.6 mm (7.96g)", "JLCCNC (SUS304) : sus304-flywheel.step", C_CUSTOM),
            ("#02  11球ハブ", rendered["p02"], "数量: 1個 ｜ Ø12.4 × 3.75 mm", "JLC3DP (SLA) : ratchet-hub-11ball.step", C_CUSTOM),
            ("#03  キャリッジ", rendered["p03"], "数量: 1個 ｜ 13.6 × 17.3 × 16.7 mm", "JLC3DP (SLA) : wheel-carriage.step", C_CUSTOM),
            ("#04A  標準ベース枠", rendered["p04a"], "数量: 1個 ｜ 17.6 × 17.6 × 4.1 mm", "JLC3DP (SLA) : wheel-base-frame.step", C_CUSTOM),
            ("#04B  沈み込みベース枠 [移植用]", rendered["p04b"], "任意: 1個 ｜ 23.7 × 23.7 × 6.5 mm", "JLC3DP (SLA) : wheel-base-frame-sunk.step", C_CUSTOM),
            ("#05  ポッド台座", rendered["p05"], "数量: 1個 ｜ 52.0 × 36.0 × 6.6 mm", "JLC3DP (SLA) : eval-pod-stand.step", C_CUSTOM),
            ("#06  キャリア基板", ASSETS_DIR / "render_pcb_wheel_eval.png", "数量: 1枚 ｜ 48.0 × 32.0 × 板厚1.6 mm", "JLCPCB (Top PCBA) : curcur40-wheel-eval", C_ELEC),
            ("#07  センサー基板", ASSETS_DIR / "render_pcb_wheel_sensor.png", "数量: 1枚 ｜ 8.8 × 8.8 × 板厚0.8 mm必須", "JLCPCB (0.8mm生基板) : curcur40-wheel-sensor", C_ELEC),
            ("#08  AS5600 IC (＋パスコン)", rendered["p08"], "数量: IC×1 ＋ コンデンサ 100nF/1μF 各1", "通販 : AS5600-ASOT (SOIC-8) ※#07へ実装", C_ELEC),
            ("#09  RP2040-Zero", rendered["p09"], "数量: 1個 ｜ ピンヘッダ未実装タイプ", "通販 : Waveshare RP2040-Zero (USB-C)", C_ELEC),
            ("#10  静音スイッチ", rendered["p10"], "数量: 1個 ｜ 6.2 × 6.2 × 高4.3 mm", "遊舎工房/通販 : Kailh Square Silent (2ピン)", C_ELEC),
            ("#11  センサー4芯線", "CUSTOM_WIRE", "数量: 1式 ｜ AWG30〜34 約60mm × 4本", "通販 : 極細シリコン撚り線 または JST SH線", C_ELEC),
            ("#12  ベアリング [要脱脂]", rendered["p12"], "数量: 2個 ｜ 内径Ø2 × 外径Ø5 × 幅2.5 mm", "通販 : DDL-520 / MR52 (★パーツクリーナー脱脂)", C_MECH),
            ("#13  ラチェット鋼球", rendered["p13"], "数量: 11個 ｜ 直径 Ø2.00 mm 精密球", "通販 : SUJ2 または SUS440C 磁性鋼球 (セラミック不可)", C_MECH),
            ("#14  回転シャフト", rendered["p14"], "数量: 1本 ｜ Ø2.0 × 長さ 14〜15 mm", "通販 : 非磁性 SUS304/316 平行ピン (ホイール軸)", C_MECH),
            ("#15  ヒンジピン", rendered["p15"], "数量: 1本 ｜ Ø2.0 × 長さ 16〜17 mm", "通販 : 非磁性 SUS304/316 平行ピン (北端揺動軸)", C_MECH),
            ("#16  角度磁石 [径方向着磁]", "CUSTOM_MAG_DIAM", "数量: 1個 ｜ Ø3.0 × 厚1.0〜1.5 mm", "通販 : 径方向2極着磁ネオジム (AS5600用)", C_MAG),
            ("#17  ラチェット磁石 [軸方向]", "CUSTOM_MAG_AXIAL", "数量: 1個 ｜ Ø1.5〜2.0 × 厚1.5 mm", "通販 : 通常の軸方向着磁ネオジム (N35等)", C_MAG),
            ("#18  磁力調整ネジ", rendered["p18"], "数量: 1本 ｜ M2 × 長さ 4〜5 mm", "通販 : 非磁性ステンレス M2 イモネジ/小ねじ", C_MAG),
            ("#19  固定M2ネジ ＆ ゴム足", rendered["p19"], "数量: M2×4mmネジ 6本 ＋ ゴム足 4個", "通販 : ベース固定2本＋台座4本 (沈み込み版は3本)", C_MAG),
        ]

        n_cols, n_rows = 4, 5
        left0, bottom0 = 0.020, 0.012
        total_w, total_h = 0.960, 0.668
        gap_x, gap_y = 0.012, 0.011
        card_w = (total_w - gap_x * (n_cols - 1)) / n_cols
        card_h = (total_h - gap_y * (n_rows - 1)) / n_rows

        for idx, (title, src, line1, line2, (hdr_col, foot_bg)) in enumerate(cards):
            r = idx // n_cols
            c = idx % n_cols
            cx = left0 + c * (card_w + gap_x)
            cy = bottom0 + (n_rows - 1 - r) * (card_h + gap_y)

            # Card container axis
            cax = fig.add_axes([cx, cy, card_w, card_h])
            cax.set_xlim(0, 100)
            cax.set_ylim(0, 100)
            cax.set_xticks([])
            cax.set_yticks([])
            for sp in cax.spines.values():
                sp.set_edgecolor(hdr_col)
                sp.set_linewidth(1.35)

            # Header bar (top 18%) + Footer bar (bottom 23%)
            cax.add_patch(patches.Rectangle((0, 82), 100, 18, fc=hdr_col, ec="none", zorder=3))
            cax.text(4.0, 91.0, title, ha="left", va="center", fontsize=9.8, fontweight="bold", color="white", zorder=4)

            cax.add_patch(patches.Rectangle((0, 0), 100, 23, fc=foot_bg, ec="none", zorder=3))
            cax.plot([0, 100], [23, 23], color="#cbd5e1", lw=0.8, zorder=4)
            cax.text(50.0, 15.2, line1, ha="center", va="center", fontsize=7.5, fontweight="bold", color="#0f172a", zorder=4)
            cax.text(50.0, 6.2, line2, ha="center", va="center", fontsize=6.8, color="#334155", zorder=4)

            # Middle viewport [cy + 0.23*card_h .. cy + 0.82*card_h]
            vax = fig.add_axes([cx + 0.004, cy + card_h * 0.232, card_w - 0.008, card_h * 0.585])
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
                # Preserve aspect ratio centered inside viewport
                box_aspect = (card_w * 16.6) / (card_h * 0.585 * 22.4)
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
                    vax.text(72, 82, "短い方: 14〜15mm", ha="center", va="center", fontsize=6.9, fontweight="bold", color="#005f73",
                             bbox=dict(boxstyle="round,pad=0.2", fc="#ffffff", ec="#005f73", lw=0.9), zorder=5)
                elif title.startswith("#15 "):
                    vax.text(72, 82, "長い方: 16〜17mm", ha="center", va="center", fontsize=6.9, fontweight="bold", color="#005f73",
                             bbox=dict(boxstyle="round,pad=0.2", fc="#ffffff", ec="#005f73", lw=0.9), zorder=5)
                vax.set_xlim(0, 100)
                vax.set_ylim(0, 100)
                vax.axis("off")

        out_guide = ASSETS_DIR / "inertia_wheel_parts_guide.png"
        fig.savefig(out_guide, dpi=160)
        plt.close(fig)
        print(f"Saved {out_guide}")


if __name__ == "__main__":
    main()
