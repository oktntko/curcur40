# -*- coding: utf-8 -*-
"""
Generate engineering cross-section diagram for the Passive Magnetic Inertia Wheel Module
(curcur40-inertia-wheel: SUS304 2-way wheel + Eddy-current-free 11x Ø2.0mm ball ratchet + M2 gap adjuster + Silent middle click).
Outputs high-resolution PNG to docs/assets/passive_inertia_wheel_spec.png.
"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

WORKSPACE = Path(__file__).resolve().parent.parent
ASSETS_DIR = WORKSPACE / "docs" / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

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


if __name__ == "__main__":
    main()
