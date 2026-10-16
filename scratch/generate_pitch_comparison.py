import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.font_manager as fm
import numpy as np
from pathlib import Path

font_path = r"C:\Windows\Fonts\meiryo.ttc"
jp_font = fm.FontProperties(fname=font_path)
jp_font_bold = fm.FontProperties(fname=font_path, weight='bold')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8.5), dpi=160)
fig.patch.set_facecolor('#ffffff')

for ax in (ax1, ax2):
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':', alpha=0.6, color='#bbbbbb')
    ax.set_xlabel('X (mm) [光学中心基準]', fontproperties=jp_font, fontsize=11)
    ax.set_ylabel('Y (mm) [光学中心基準]', fontproperties=jp_font, fontsize=11)
    ax.axhline(0, color='#888888', linewidth=0.8, linestyle='--')
    ax.axvline(0, color='#888888', linewidth=0.8, linestyle='--')

# -------------------------------------------------------------
# Panel 1: Current Y = 9.60mm (Pitch 19.2mm)
# -------------------------------------------------------------
ax1.set_xlim(1.5, 7.5)
ax1.set_ylim(6.0, 12.0)
ax1.set_title("【現状】縦ピッチ 19.2 mm (Y = +-9.60 mm)\nネジ穴が開口部の角に 0.15mm 食い込み発生",
              fontproperties=jp_font_bold, fontsize=12.5, pad=12, color="#c62828")

# Lens neck outline: 8.47 x 16.50 mm (X: 0 to 4.235, Y: 0 to 8.25)
lens_neck1 = patches.Rectangle((0, 0), 4.235, 8.25, facecolor="#e0f7fa", edgecolor="#0097a7", linewidth=1.5, linestyle="--", label="LM19レンズ首部 (8.47 x 16.50mm)")
ax1.add_patch(lens_neck1)

# Current PCB Opening: 8.70 x 17.30 mm (X: 0 to 4.35, Y: 0 to 8.65)
pcb_cut1 = patches.Rectangle((0, 0), 4.35, 8.65, facecolor="none", edgecolor="#e65100", linewidth=2.0, label="現状の基板開口部 (長さ 17.3mm)")
ax1.add_patch(pcb_cut1)

# Current M2 hole at (4.50, 9.60)
# Drill dia 2.2mm (r=1.1mm)
hole1 = patches.Circle((4.50, 9.60), 1.10, facecolor="#ffcdd2", edgecolor="#c62828", linewidth=2.0, label="M2ネジ穴 (dia 2.2mm)")
ax1.add_patch(hole1)
# Seat dia 3.8mm (r=1.9mm)
seat1 = patches.Circle((4.50, 9.60), 1.90, fill=False, edgecolor="#e57373", linewidth=1.2, linestyle=":", label="ネジ座面 (dia 3.8mm)")
ax1.add_patch(seat1)
ax1.plot(4.50, 9.60, '+', color='#c62828', markersize=8, markeredgewidth=2)

# Cup outer wall arc R=14.0mm
theta = np.linspace(np.radians(40), np.radians(80), 100)
ax1.plot(14.0 * np.cos(theta), 14.0 * np.sin(theta), color="#0288d1", linewidth=2.0, linestyle="-", label="カップ外周 (R=14.0mm)")

# Annotate interference
ax1.annotate("食い込み (被り)\n0.15 mm", xy=(4.35, 8.55), xytext=(2.2, 9.2),
             arrowprops=dict(arrowstyle="->", color="#c62828", lw=1.8),
             fontproperties=jp_font_bold, fontsize=10, color="#c62828",
             bbox=dict(boxstyle="round,pad=0.3", fc="#ffebee", ec="#c62828"))

ax1.legend(loc="upper left", prop=jp_font, fontsize=8.5, framealpha=0.95)


# -------------------------------------------------------------
# Panel 2: Proposed Y = 10.00mm (Pitch 20.0mm) + Adjusted Opening
# -------------------------------------------------------------
ax2.set_xlim(1.5, 7.5)
ax2.set_ylim(6.0, 12.0)
ax2.set_title("【解消案】縦ピッチ 20.0 mm (Y = +-10.00 mm) へ移動\n開口部との間に 0.45mm の健全な肉厚（壁）を確保！",
              fontproperties=jp_font_bold, fontsize=12.5, pad=12, color="#2e7d32")

# Lens neck outline: 8.47 x 16.50 mm (X: 0 to 4.235, Y: 0 to 8.25)
lens_neck2 = patches.Rectangle((0, 0), 4.235, 8.25, facecolor="#e0f7fa", edgecolor="#0097a7", linewidth=1.5, linestyle="--", label="LM19レンズ首部 (8.47 x 16.50mm)")
ax2.add_patch(lens_neck2)

# Optimized PCB Opening: 8.70 x 16.90 mm (X: 0 to 4.35, Y: 0 to 8.45 - clearance +0.2mm per side)
pcb_cut2 = patches.Rectangle((0, 0), 4.35, 8.45, facecolor="none", edgecolor="#e65100", linewidth=2.0, label="適正化開口部 (長さ 16.9mm)")
ax2.add_patch(pcb_cut2)

# Proposed M2 hole at (4.50, 10.00)
# Drill dia 2.2mm (r=1.1mm)
hole2 = patches.Circle((4.50, 10.00), 1.10, facecolor="#c8e6c9", edgecolor="#2e7d32", linewidth=2.0, label="新M2ネジ穴 (Y = 10.00mm)")
ax2.add_patch(hole2)
seat2 = patches.Circle((4.50, 10.00), 1.90, fill=False, edgecolor="#81c784", linewidth=1.2, linestyle=":", label="ネジ座面 (dia 3.8mm)")
ax2.add_patch(seat2)
ax2.plot(4.50, 10.00, '+', color='#2e7d32', markersize=8, markeredgewidth=2)

# Cup outer wall arc R=14.0mm
ax2.plot(14.0 * np.cos(theta), 14.0 * np.sin(theta), color="#0288d1", linewidth=2.0, linestyle="-", label="カップ外周 (R=14.0mm)")

# Annotate clearance / bridge
ax2.annotate('', xy=(4.50, 8.45), xytext=(4.50, 8.90),
             arrowprops=dict(arrowstyle="<->", color="#2e7d32", lw=2.0))
ax2.text(4.7, 8.65, "肉厚 0.45 mm 確保！\n(完全に独立した穴)", fontproperties=jp_font_bold, fontsize=9.5, color="#2e7d32", va='center',
         bbox=dict(boxstyle="round,pad=0.25", fc="#e8f5e9", ec="#2e7d32"))

# Annotate outer wall thickness in cup:
# At (4.5, 10.0), r = 10.97, seat edge = 10.97 + 1.95 = 12.92 -> wall = 14.0 - 12.92 = 1.08 mm
ax2.annotate("カップ外壁肉厚\n1.08 mm (強度十分)", xy=(6.0, 11.0), xytext=(5.2, 11.5),
             fontproperties=jp_font, fontsize=9, color="#0288d1",
             bbox=dict(boxstyle="round,pad=0.25", fc="#e1f5fe", ec="#0288d1"))

ax2.legend(loc="upper left", prop=jp_font, fontsize=8.5, framealpha=0.95)

plt.tight_layout()
out_png = Path(r"C:\Users\oktnt\.gemini\antigravity\brain\dab819aa-2c9f-4dd2-be5e-39a298725eca\pitch_comparison.png")
plt.savefig(out_png, dpi=180)
print(f"Saved pitch comparison to: {out_png}")
