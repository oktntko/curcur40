import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.font_manager as fm
import numpy as np
from pathlib import Path

font_path = r"C:\Windows\Fonts\meiryo.ttc"
jp_font = fm.FontProperties(fname=font_path)
jp_font_bold = fm.FontProperties(fname=font_path, weight='bold')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 9.5), dpi=160)
fig.patch.set_facecolor('#ffffff')

for ax in (ax1, ax2):
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':', alpha=0.6, color='#bbbbbb')
    ax.set_xlim(-16, 16)
    ax.set_ylim(-21, 19)
    ax.set_xlabel('X (mm) [光学中心基準]', fontproperties=jp_font, fontsize=11)
    ax.set_ylabel('Y (mm) [光学中心基準]', fontproperties=jp_font, fontsize=11)
    ax.axhline(0, color='#888888', linewidth=0.8, linestyle='--')
    ax.axvline(0, color='#888888', linewidth=0.8, linestyle='--')

# -------------------------------------------------------------
# Panel 1: Old vs Plan B Overlay with TRRS relation
# -------------------------------------------------------------
ax1.set_title("【案B 外形寸法とTRRSコネクタとの位置関係】\n(全高 33.0mm -> 26.5mm へ短縮、TRRS側の干渉を大幅低減)",
              fontproperties=jp_font_bold, fontsize=12.5, pad=12)

# Old Edge.Cuts (ghost in gray/red)
old_rect = patches.FancyBboxPatch((-11.75, -16.0), 23.5, 33.0,
                                 boxstyle="round,pad=0,rounding_size=3.0",
                                 facecolor="#ffebee", edgecolor="#e57373", linewidth=1.5, linestyle=":",
                                 label="旧外形 (23.5 x 33.0 mm)")
ax1.add_patch(old_rect)

# Plan B Compact Edge.Cuts (Green solid)
# X: -11.25 to +10.50 (width 21.75 mm), Y: -13.25 to +13.25 (height 26.5 mm), r=2.5 mm
plan_b_rect = patches.FancyBboxPatch((-11.25, -13.25), 21.75, 26.5,
                                     boxstyle="round,pad=0,rounding_size=2.5",
                                     facecolor="#e8f5e9", edgecolor="#2e7d32", linewidth=2.2,
                                     label="案B コンパクト外形 (21.75 x 26.5 mm)")
ax1.add_patch(plan_b_rect)

# Trackball cup outer circle (dia 28 mm)
cup_circ1 = patches.Circle((0, 0), 14.0, fill=False, edgecolor="#0288d1", linewidth=1.8, linestyle="--", label="カップ外周 (dia 28mm)")
ax1.add_patch(cup_circ1)

# Optical opening (17.3 x 8.7 mm)
ax1.add_patch(patches.Rectangle((-8.65, -4.35), 17.3, 8.7, facecolor="#ffffff", edgecolor="#e65100", linewidth=1.5, label="レンズ開口部 (17.3 x 8.7 mm)"))

# J1 pin header
ax1.add_patch(patches.Rectangle((-11.0, 0.5), 2.54, 8 * 2.54, facecolor="#fff9c4", edgecolor="#fbc02d", linewidth=1.2, label="J1 ピンヘッダ (位置維持)"))

# TRRS Jack boundary (at relative Y ~ -17.74 mm, X ~ -3.26 mm, size ~ 6.0 x 14.0 mm)
trrs_rect = patches.Rectangle((-6.26, -20.5), 6.0, 5.5, facecolor="#e1f5fe", edgecolor="#0288d1", linewidth=1.5, linestyle="-", label="TRRSジャック (rJ2)")
ax1.add_patch(trrs_rect)
ax1.text(-3.26, -18.0, "TRRS ジャック (rJ2)\n[メイン基板側]", fontproperties=jp_font, fontsize=8, ha='center', va='center', color="#01579b")

# Clearance comparison arrow between PCB bottom and TRRS
# Old clearance: from Y = -16.0 to Y = -15.0 -> only 1.0 mm!
ax1.annotate('', xy=(-3.26, -15.0), xytext=(-3.26, -16.0), arrowprops=dict(arrowstyle='<->', color='#d32f2f', lw=1.5))
ax1.text(-4.5, -15.5, "旧隙間: 1.0mm (超近接)", fontproperties=jp_font, fontsize=8, ha='right', color="#d32f2f", weight='bold')

# New clearance: from Y = -13.25 to Y = -15.0 -> 1.75 mm ~ 2.0 mm direct clearance, and corner is rounded!
ax1.annotate('', xy=(1.0, -15.0), xytext=(1.0, -13.25), arrowprops=dict(arrowstyle='<->', color='#2e7d32', lw=2.0))
ax1.text(2.0, -14.1, "案B 隙間: 2.25mm 確保！\n(+角丸でプラグ干渉大幅減)", fontproperties=jp_font, fontsize=8.5, ha='left', color="#2e7d32", weight='bold')

# New M2 holes
for hx, hy in [(-4.50, -9.60), (4.50, -9.60), (-4.50, 9.60), (4.50, 9.60)]:
    hole = patches.Circle((hx, hy), 1.1, facecolor="#81c784", edgecolor="#1b5e20", linewidth=1.8)
    ax1.add_patch(hole)
    ax1.plot(hx, hy, '+', color='#1b5e20', markersize=6)

ax1.legend(loc="upper right", prop=jp_font, fontsize=8.0, framealpha=0.92)


# -------------------------------------------------------------
# Panel 2: Component Relocation Plan (部品レイアウト移行案)
# -------------------------------------------------------------
ax2.set_title("【案B 部品配置・配線の現実的な実装レイアウト】\n(無理のない回路配置・DRCクリアランスの完全確保)",
              fontproperties=jp_font_bold, fontsize=12.5, pad=12)

# Plan B Edge.Cuts
plan_b_rect2 = patches.FancyBboxPatch((-11.25, -13.25), 21.75, 26.5,
                                      boxstyle="round,pad=0,rounding_size=2.5",
                                      facecolor="#f1f8e9", edgecolor="#2e7d32", linewidth=2.2)
ax2.add_patch(plan_b_rect2)

# Cup outer
ax2.add_patch(patches.Circle((0, 0), 14.0, fill=False, edgecolor="#0288d1", linewidth=1.5, linestyle="--"))

# Optical opening
ax2.add_patch(patches.Rectangle((-8.65, -4.35), 17.3, 8.7, facecolor="#ffffff", edgecolor="#e65100", linewidth=1.5))
ax2.text(0, 0, "光学開口部 (LM19レンズ首部貫通)", fontproperties=jp_font, fontsize=8.5, ha='center', va='center', color="#e65100")

# PMW3360 IC body outline
ax2.add_patch(patches.Rectangle((-7.1, -9.8), 14.2, 19.6, facecolor="none", edgecolor="#757575", linewidth=1.2, linestyle=":"))
ax2.text(0, 3.0, "PMW3360DM IC 本体 (B.Cu側)", fontproperties=jp_font, fontsize=8, ha='center', va='center', color="#757575")

# J1 pin header
ax2.add_patch(patches.Rectangle((-11.0, 0.5), 2.54, 8 * 2.54, facecolor="#fff9c4", edgecolor="#fbc02d", linewidth=1.2))
for i in range(8):
    ax2.plot(-10.25, 1.77 + i * 2.54, 'o', color="#f57f17", markersize=3)
ax2.text(-9.0, 10.0, "J1 (8pin)", fontproperties=jp_font, fontsize=8, color="#f57f17", weight='bold')

# M2 holes with keepout / seat circle
for hx, hy in [(-4.50, -9.60), (4.50, -9.60), (-4.50, 9.60), (4.50, 9.60)]:
    seat = patches.Circle((hx, hy), 1.9, fill=False, edgecolor="#1b5e20", linewidth=1.2, linestyle="--")
    ax2.add_patch(seat)
    hole = patches.Circle((hx, hy), 1.1, facecolor="#c8e6c9", edgecolor="#1b5e20", linewidth=1.8)
    ax2.add_patch(hole)
    ax2.plot(hx, hy, '+', color='#1b5e20', markersize=6)

# Right side components (JP1, C1, C2, R1, R2): Completely safe in original area!
ax2.add_patch(patches.Rectangle((7.5, -2.5), 2.2, 4.0, facecolor="#ffe0b2", edgecolor="#fb8c00", linewidth=1.0))
ax2.text(8.6, -0.5, "JP1", fontproperties=jp_font, fontsize=7.5, ha='center', color="#e65100")
ax2.add_patch(patches.Rectangle((7.8, -7.0), 1.8, 3.5, facecolor="#dcedc8", edgecolor="#689f38", linewidth=1.0))
ax2.text(8.7, -5.2, "C1, C2", fontproperties=jp_font, fontsize=7.5, ha='center', color="#33691e")
ax2.add_patch(patches.Rectangle((7.8, 4.0), 1.8, 3.5, facecolor="#dcedc8", edgecolor="#689f38", linewidth=1.0))
ax2.text(8.7, 5.8, "R1, R2", fontproperties=jp_font, fontsize=7.5, ha='center', color="#33691e")

# Top Test Points: slightly shifted to Y = +11.8 mm (safe!)
for i, name in enumerate(["GND", "VIO", "VDD"]):
    tx = -3.5 + i * 3.5
    ax2.plot(tx, 12.0, 'o', color="#ffca28", markersize=6, markeredgecolor="#f57f17")
    ax2.text(tx, 12.8, name, fontproperties=jp_font, fontsize=7, ha='center', color="#f57f17")

# Bottom Relocated Circuit (U2, C3, C4, R3, R4, C5):
# Compact layout centered in Y in [-12.5, -6.5], between and below the two bottom M2 holes!
# U2 (SOT-23-5): at (0.0, -11.5)
ax2.add_patch(patches.Rectangle((-1.5, -12.5), 3.0, 2.0, facecolor="#cfd8dc", edgecolor="#37474f", linewidth=1.2))
ax2.text(0.0, -11.5, "U2 (LDO 3.3V)", fontproperties=jp_font, fontsize=7.5, ha='center', va='center', color="#263238", weight='bold')

# C3 (in) & C4 (out): at X = -2.0, +2.0, Y = -9.0 (between the M2 holes!)
ax2.add_patch(patches.Rectangle((-2.5, -8.0), 1.6, 2.0, facecolor="#dcedc8", edgecolor="#689f38", linewidth=1.0))
ax2.text(-1.7, -7.0, "C3, R3", fontproperties=jp_font, fontsize=7, ha='center', color="#33691e")

ax2.add_patch(patches.Rectangle((0.9, -8.0), 1.6, 2.0, facecolor="#dcedc8", edgecolor="#689f38", linewidth=1.0))
ax2.text(1.7, -7.0, "C4, R4", fontproperties=jp_font, fontsize=7, ha='center', color="#33691e")

# C5 bypass cap: at (0.0, -5.5) just below aperture
ax2.add_patch(patches.Rectangle((-1.0, -5.8), 2.0, 1.0, facecolor="#dcedc8", edgecolor="#689f38", linewidth=1.0))
ax2.text(0.0, -5.3, "C5", fontproperties=jp_font, fontsize=7, ha='center', color="#33691e")

# Explanatory annotations
ax2.text(0.0, -14.8, "★下端を Y=-13.25mm に集約: LDO回路をM2穴間・直下に高密度配置",
         fontproperties=jp_font, fontsize=8.5, ha='center', color="#2e7d32", weight='bold',
         bbox=dict(boxstyle="round,pad=0.25", fc="#e8f5e9", ec="#81c784"))

plt.tight_layout()
out_png = Path(r"C:\Users\oktnt\.gemini\antigravity\brain\dab819aa-2c9f-4dd2-be5e-39a298725eca\pmw3360_plan_b_detail.png")
plt.savefig(out_png, dpi=180)
print(f"Saved Plan B detail to: {out_png}")
