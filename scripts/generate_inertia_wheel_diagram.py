# -*- coding: utf-8 -*-
"""
Generate Phase 1 engineering cross-section diagram for the Passive Magnetic Inertia Wheel Module
(curcur40-inertia-wheel: SUS304 2-way wheel + Eddy-current-free 18-ball ratchet + M2 gap adjuster + Silent middle click).
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
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.8, 7.4), dpi=200)
    fig.patch.set_facecolor("#ffffff")
    fig.suptitle(
        "パッシブ磁気慣性ホイール仕様図（SUS304 削り出し × 渦電流ゼロ磁気ラチェット × 静音ミドルクリック）",
        fontsize=13.5,
        fontweight="bold",
        y=0.97,
        color="#1a1a1a",
    )

    z_axle = 5.00  # Wheel Ø16.80 -> bottom Z = -3.40 mm, top Z = +13.40 mm (< +14.80mm trackball!)

    # =========================================================================
    # Panel 1: X-Z Front Cross-Section (18.0 mm Width Envelope)
    # =========================================================================
    ax1.set_title("① 正面断面図 (X–Z 軸方向積層：18.0 mm 幅内・電磁部品ゼロ構成)", fontsize=11, fontweight="bold", pad=10)
    ax1.set_xlim(-11.5, 11.5)
    ax1.set_ylim(-6.5, 16.5)
    ax1.set_aspect("equal")
    ax1.set_facecolor("#f8f9fa")
    ax1.grid(True, linestyle=":", linewidth=0.5, color="#cccccc")
    ax1.set_xlabel("X 座標 [mm]（モジュール中心基準：±9.00 mm = 18.00 mm 枠）", fontsize=9.5)
    ax1.set_ylabel("curcur40 グローバル Z 座標 [mm]（ケース上縁 = 0.00 mm）", fontsize=9.5)

    ax1.axvline(-9.0, color="#d90429", linestyle="--", linewidth=1.2)
    ax1.axvline(9.0, color="#d90429", linestyle="--", linewidth=1.2)
    ax1.text(-8.8, 15.3, "-9.0mm", color="#d90429", fontsize=8, fontweight="bold")
    ax1.text(6.6, 15.3, "+9.0mm", color="#d90429", fontsize=8, fontweight="bold")

    # Main PCB & Top Plate (18.20 mm opening = ±9.10 mm)
    ax1.add_patch(patches.Rectangle((-11.2, -5.8), 22.4, 1.6, fc="#2a9d8f", ec="#1b4332", lw=1.2, alpha=0.85, zorder=2))
    ax1.text(0.0, -5.0, "curcur40-right Rev2 メインPCB / 単体評価キャリア基板", ha="center", va="center", fontsize=8, color="white", fontweight="bold", zorder=3)

    ax1.add_patch(patches.Rectangle((-11.2, -3.6), 2.1, 1.6, fc="#3a7ca5", ec="#16425b", lw=1.1, zorder=2))
    ax1.add_patch(patches.Rectangle((9.1, -3.6), 2.1, 1.6, fc="#3a7ca5", ec="#16425b", lw=1.1, zorder=2))
    ax1.text(-10.15, -1.3, "プレート開口\n18.2 mm", ha="center", va="bottom", fontsize=7.2, color="#16425b", fontweight="bold")

    # Base Frame / Sub-PCB (17.8 x 17.8 x 0.8 mm, Z = -4.2 to -3.4 with open slot under wheel)
    ax1.add_patch(patches.Rectangle((-8.9, -4.2), 5.6, 0.8, fc="#264653", ec="#111111", lw=1.0, zorder=3))
    ax1.add_patch(patches.Rectangle((2.7, -4.2), 6.2, 0.8, fc="#264653", ec="#111111", lw=1.0, zorder=3))

    # Hinged Inner Carriage U-Frame & Bearing Pillars
    ax1.add_patch(patches.Rectangle((-5.5, -2.8), 2.2, 10.3, fc="#dee2e6", ec="#495057", lw=1.0, zorder=3))
    ax1.add_patch(patches.Rectangle((5.8, -2.8), 2.2, 10.3, fc="#dee2e6", ec="#495057", lw=1.0, zorder=3))

    # Shaft Ø2.0 mm (SUS304/316 non-magnetic, X = -5.8 to +8.2)
    ax1.add_patch(patches.Rectangle((-5.7, z_axle - 1.0), 14.0, 2.0, fc="#f8f9fa", ec="#343a40", lw=1.1, zorder=5))
    ax1.text(0.8, z_axle, "SUS316 非磁性シャフト Ø2.0", ha="center", va="center", fontsize=6.7, fontweight="bold", color="#212529", zorder=9)

    # Miniature Degreased Stainless Bearings (DDL-520 / MR52: Ø2 x Ø5 x 2.5mm)
    ax1.add_patch(patches.Rectangle((-5.5, z_axle - 2.5), 2.5, 5.0, fc="#ffffff", ec="#0077b6", lw=1.3, zorder=4))
    ax1.add_patch(patches.Rectangle((5.7, z_axle - 2.5), 2.5, 5.0, fc="#ffffff", ec="#0077b6", lw=1.3, zorder=4))
    ax1.text(-4.25, z_axle + 2.9, "脱脂MR52\n(DDL-520)", ha="center", va="bottom", fontsize=6.6, color="#0077b6", fontweight="bold")
    ax1.text(6.95, z_axle + 2.9, "脱脂MR52\n(DDL-520)", ha="center", va="bottom", fontsize=6.6, color="#0077b6", fontweight="bold")

    # West Sensor PCB + AS5600-ASOT (SOIC-8) + Ø3x1.5mm Diametric Magnet
    ax1.add_patch(patches.Rectangle((-8.8, 0.8), 0.8, 8.4, fc="#2a9d8f", ec="#1b4332", lw=1.0, zorder=4))
    ax1.add_patch(patches.Rectangle((-8.0, z_axle - 2.45), 1.5, 4.9, fc="#212529", ec="#000000", lw=1.0, zorder=5))
    ax1.text(-7.25, z_axle, "AS5600\n12-bit I2C", ha="center", va="center", fontsize=5.7, color="white", rotation=90, zorder=6)
    ax1.add_patch(patches.Rectangle((-6.0, z_axle - 1.5), 1.3, 3.0, fc="#e63946", ec="#6a040f", lw=1.0, zorder=6))
    ax1.annotate("径方向磁石\n(非接触角度検出)", xy=(-6.1, z_axle + 1.5), xytext=(-11.1, 11.8),
                 arrowprops=dict(arrowstyle="->", color="#6a040f", lw=1.0), fontsize=7.1, fontweight="bold", color="#6a040f")

    # SUS304 Silver Stainless Flywheel (Ø16.80 x 5.60 mm, X = -2.80 to +2.80)
    # With MX-Master-style 2-way center groove (1.3mm wide x 0.5mm deep) for optional O-ring!
    ax1.add_patch(patches.Rectangle((-2.8, z_axle - 8.4), 5.6, 16.8, fc="#d8dee9", ec="#4c566a", lw=1.5, zorder=6))
    # Subtle center 2-way groove top & bottom
    ax1.add_patch(patches.Rectangle((-0.65, z_axle + 7.9), 1.3, 0.52, fc="#f8f9fa", ec="#4c566a", lw=0.9, zorder=7))
    ax1.add_patch(patches.Rectangle((-0.65, z_axle - 8.42), 1.3, 0.52, fc="#f8f9fa", ec="#4c566a", lw=0.9, zorder=7))
    ax1.text(0.0, z_axle + 4.3, "SUS304 ステンレス\n削り出しホイール\nØ16.8×5.6mm\n(シルバー・横溝＋\n中央2wayリング溝)", ha="center", va="center", fontsize=7.0, fontweight="bold", color="#1f2937", zorder=8)

    # Coaxial Eddy-Current-Free Resin Ratchet Hub (Ø10.8 x 2.0mm, X = +3.2 to +5.2) + Ø1.0mm SUJ2 Steel Balls
    ax1.add_patch(patches.Rectangle((3.2, z_axle - 5.4), 2.0, 10.8, fc="#a8dadc", ec="#1d3557", lw=1.2, zorder=6))
    ax1.add_patch(patches.Circle((4.2, z_axle + 4.9), 0.55, fc="#495057", ec="#111111", lw=0.9, zorder=7))
    ax1.add_patch(patches.Circle((4.2, z_axle - 4.9), 0.55, fc="#495057", ec="#111111", lw=0.9, zorder=7))
    ax1.annotate("絶縁樹脂リング＋Ø1.0鋼球×18個\n(渦電流ブレーキ完全ゼロ!)", xy=(4.2, z_axle + 5.4), xytext=(4.6, 13.5),
                 arrowprops=dict(arrowstyle="->", color="#1d3557", lw=1.1), fontsize=7.2, fontweight="bold", color="#1d3557", ha="center",
                 bbox=dict(boxstyle="round,pad=0.2", fc="#e0fbfc", ec="#1d3557", lw=0.8))

    # =========================================================================
    # Panel 2: Y-Z Side Section (Hinged Silent Click + M2 Screw Magnet Gap Adjuster)
    # =========================================================================
    ax2.set_title("② 側面機構図 (Y–Z 断面：静音ミドルクリック ＆ M2ネジ磁力調整機構)", fontsize=11, fontweight="bold", pad=10)
    ax2.set_xlim(-10.8, 10.8)
    ax2.set_ylim(-6.5, 16.5)
    ax2.set_aspect("equal")
    ax2.set_facecolor("#f8f9fa")
    ax2.grid(True, linestyle=":", linewidth=0.5, color="#cccccc")
    ax2.set_xlabel("Y 座標 [mm]（北側 -Y ヒンジ軸 ／ 南側 +Y 静音スイッチ ＆ 磁力調整ネジ）", fontsize=9.5)
    ax2.set_ylabel("curcur40 グローバル Z 座標 [mm]", fontsize=9.5)

    ax2.axvline(-9.0, color="#d90429", linestyle="--", linewidth=1.2)
    ax2.axvline(9.0, color="#d90429", linestyle="--", linewidth=1.2)

    # Main PCB & Base Frame
    ax2.add_patch(patches.Rectangle((-10.5, -5.8), 21.0, 1.6, fc="#2a9d8f", ec="#1b4332", lw=1.1, alpha=0.85, zorder=1))
    ax2.add_patch(patches.Rectangle((-8.9, -4.2), 17.8, 0.8, fc="#264653", ec="#111111", lw=1.0, zorder=2))

    # North Hinge Pin at Y = -7.8, Z = -2.2
    ax2.add_patch(patches.Circle((-7.8, -2.2), 0.85, fc="#ffffff", ec="#212529", lw=1.5, zorder=6))
    ax2.text(-7.8, -0.7, "北端ヒンジ軸\n(Y=-7.8mm)", ha="center", va="bottom", fontsize=7.2, fontweight="bold", color="#212529")

    # Unitized Inner Carriage
    carriage_poly = patches.Polygon(
        [[-8.3, -2.7], [8.3, -1.5], [8.3, 5.8], [-2.0, 5.8], [-8.3, -1.5]],
        closed=True, fc="#dee2e6", ec="#495057", lw=1.2, alpha=0.65, zorder=2
    )
    ax2.add_patch(carriage_poly)
    ax2.annotate("一体揺動キャリッジ\n(クリック中も磁石ギャップ不変!)",
                 xy=(-6.5, -0.3), xytext=(-10.3, 13.8),
                 arrowprops=dict(arrowstyle="->", color="#1d3557", lw=1.1),
                 fontsize=7.2, fontweight="bold", color="#1d3557",
                 bbox=dict(boxstyle="round,pad=0.25", fc="#e0fbfc", ec="#1d3557", lw=0.9), zorder=9)

    # Kailh Square Silent Micro Switch (6.0 x 6.0 x 4.3 mm) at South Y = +6.6
    ax2.add_patch(patches.Rectangle((4.2, -3.4), 4.5, 1.8, fc="#f4a261", ec="#9c4100", lw=1.2, zorder=4))
    ax2.add_patch(patches.Rectangle((5.7, -1.6), 1.5, 0.45, fc="#e63946", ec="#6a040f", lw=1.0, zorder=5))
    ax2.annotate("静音マイクロSW (Kailh Silent 6×6×4.3)\n指先荷重 ~185gf: スピン停止時に誤爆しない!",
                 xy=(6.4, -2.6), xytext=(0.2, -5.5),
                 arrowprops=dict(arrowstyle="->", color="#9c4100", lw=1.1),
                 fontsize=7.0, fontweight="bold", color="#7f2704",
                 bbox=dict(boxstyle="round,pad=0.2", fc="#fff3cd", ec="#d97706", lw=0.8), zorder=9)

    # Wheel Circle (Ø16.80 mm at Y = -0.8, Z = +5.0) + Insulated 18-Ball Ratchet Ring (Ø10.8 mm)
    wy, wz = -0.8, z_axle
    ax2.add_patch(patches.Circle((wy, wz), 8.4, fc="#d8dee9", ec="#4c566a", lw=1.6, alpha=0.65, zorder=3))
    # Draw transverse grip flutes along rim
    for a in np.linspace(0, 2 * np.pi, 36, endpoint=False):
        ax2.plot([wy + 7.95 * np.cos(a), wy + 8.40 * np.cos(a)],
                 [wz + 7.95 * np.sin(a), wz + 8.40 * np.sin(a)], color="#4c566a", lw=0.8, zorder=4)

    # Resin ring + 18 discrete Ø1.0mm steel balls (orbit radius 4.9mm)
    ax2.add_patch(patches.Circle((wy, wz), 5.4, fc="#a8dadc", ec="#1d3557", lw=1.1, alpha=0.90, zorder=4))
    for a in np.linspace(0, 2 * np.pi, 18, endpoint=False):
        bx = wy + 4.85 * np.cos(a)
        bz = wz + 4.85 * np.sin(a)
        ax2.add_patch(patches.Circle((bx, bz), 0.50, fc="#495057", ec="#111111", lw=0.7, zorder=5))
    ax2.add_patch(patches.Circle((wy, wz), 1.0, fc="#ffffff", ec="#212529", lw=1.2, zorder=6))
    ax2.text(wy, wz + 6.4, "Ø16.8 SUS304\n(頂点 Z=+13.4mm)", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#1f2937", zorder=7)

    # Horizontal M2 Gap Adjuster Screw + Ø2x1.5mm NdFeB Magnet at Z = +2.8, Y = +4.6..+8.8
    mz = 2.6
    # Magnet at Y = +4.45 (gap ~0.35mm from R=5.4 ring at Z=2.6: wy + sqrt(5.4^2 - 2.4^2) = -0.8 + 4.83 = +4.03!)
    ax2.add_patch(patches.Rectangle((4.40, mz - 1.0), 1.5, 2.0, fc="#e63946", ec="#6a040f", lw=1.1, zorder=7))
    # M2 adjustment screw behind magnet (Y = +5.9 to +8.9)
    ax2.add_patch(patches.Rectangle((5.90, mz - 0.8), 2.9, 1.6, fc="#adb5bd", ec="#212529", lw=1.1, hatch="///", zorder=6))
    ax2.annotate("", xy=(4.25, mz), xytext=(6.0, mz),
                 arrowprops=dict(arrowstyle="<->", color="#d90429", lw=1.5), zorder=8)

    ax2.annotate("M2イモネジ距離調整 (0.4mm/周)\n・近づける → コリコリ強ノッチ\n・離す → 3〜7秒の伸びやかな慣性スピン!",
                 xy=(5.2, mz + 1.0), xytext=(0.6, 13.5),
                 arrowprops=dict(arrowstyle="->", color="#d90429", lw=1.2),
                 fontsize=7.2, fontweight="bold", color="#9d0208",
                 bbox=dict(boxstyle="round,pad=0.25", fc="#ffe5ec", ec="#d90429", lw=0.9), zorder=9)

    plt.tight_layout(rect=[0, 0.01, 1, 0.94])
    out_path = ASSETS_DIR / "passive_inertia_wheel_spec.png"
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
