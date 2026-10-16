import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.font_manager as fm
import numpy as np
from pathlib import Path

# Load Japanese font explicitly
font_path = r"C:\Windows\Fonts\meiryo.ttc"
jp_font = fm.FontProperties(fname=font_path)
jp_font_bold = fm.FontProperties(fname=font_path, weight='bold')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 9), dpi=160)
fig.patch.set_facecolor('#ffffff')

for ax in (ax1, ax2):
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':', alpha=0.6, color='#bbbbbb')
    ax.set_xlim(-16, 16)
    ax.set_ylim(-18, 19)
    ax.set_xlabel('X (mm) [光学中心基準]', fontproperties=jp_font, fontsize=11)
    ax.set_ylabel('Y (mm) [光学中心基準]', fontproperties=jp_font, fontsize=11)
    ax.axhline(0, color='#888888', linewidth=0.8, linestyle='--')
    ax.axvline(0, color='#888888', linewidth=0.8, linestyle='--')

# -------------------------------------------------------------
# Panel 1: Current / Old Design (現行設計 curcur40-pmw3360)
# -------------------------------------------------------------
ax1.set_title("【旧設計（現行）】curcur40-pmw3360.kicad_pcb\n(M3ネジ穴 4箇所 / 外形 23.5 x 33.0 mm)",
              fontproperties=jp_font_bold, fontsize=13, pad=12)

# Old Edge.Cuts: width 23.5 mm ([-11.75, +11.75]), height 33.0 mm ([-16.0, +17.0]), r=3.0mm
old_rect = patches.FancyBboxPatch((-11.75, -16.0), 23.5, 33.0,
                                 boxstyle="round,pad=0,rounding_size=3.0",
                                 facecolor="#f1f8e9", edgecolor="#33691e", linewidth=2.0)
ax1.add_patch(old_rect)

# Trackball cup outer circle (dia 28.0 mm, R=14.0 mm)
cup_circle_old = patches.Circle((0, 0), 14.0, fill=False, edgecolor="#0288d1", linewidth=1.8, linestyle="--")
ax1.add_patch(cup_circle_old)

# Optical opening cutout in PCB (17.3 x 8.7 mm)
old_opt_cut = patches.Rectangle((-8.65, -4.35), 17.3, 8.7, facecolor="#ffffff", edgecolor="#e65100", linewidth=1.5)
ax1.add_patch(old_opt_cut)

# PMW3360 IC body (14.2 x 19.6 mm)
ic_rect_old = patches.Rectangle((-7.1, -9.8), 14.2, 19.6, facecolor="none", edgecolor="#616161", linewidth=1.2, linestyle=":")
ax1.add_patch(ic_rect_old)

# J1 connector (1x8 pin header on left: X ~ -10.25, Y ~ +0.5 to +18.3)
j1_old = patches.Rectangle((-11.0, 0.5), 2.54, 8 * 2.54, facecolor="#fff9c4", edgecolor="#fbc02d", linewidth=1.2)
ax1.add_patch(j1_old)

# Old mounting holes: 4x M3 (dia 3.2 mm) at (+-8.75, -13.0 / +14.0)
old_holes = [(-8.75, -13.0), (8.75, -13.0), (-8.75, 14.0), (8.75, 14.0)]
for hx, hy in old_holes:
    hole = patches.Circle((hx, hy), 1.6, facecolor="#ffcdd2", edgecolor="#c62828", linewidth=1.5)
    ax1.add_patch(hole)
    ax1.plot(hx, hy, '+', color='#c62828', markersize=6)
    ax1.annotate(f"旧M3穴\n({hx:+.2f}, {hy:+.1f})", (hx, hy), textcoords="offset points",
                 xytext=(10 if hx > 0 else -60, 6 if hy > 0 else -20),
                 fontproperties=jp_font, fontsize=8, color="#c62828")

# Legend for panel 1
ax1.plot([], [], color="#33691e", linewidth=2.0, label="現行基板外形 (23.5 x 33.0 mm)")
ax1.plot([], [], color="#0288d1", linewidth=1.8, linestyle="--", label="トラックボールカップ外周 (dia 28mm)")
ax1.plot([], [], color="#e65100", linewidth=1.5, label="レンズ開口部 (17.3 x 8.7 mm)")
ax1.plot([], [], 'o', color="#ffcdd2", markeredgecolor="#c62828", label="旧M3ネジ穴 (dia 3.2mm, 4箇所)")
ax1.plot([], [], color="#fbc02d", linewidth=3.0, label="J1ピンヘッダ (1x8 メイン基板接続)")
ax1.legend(loc="upper right", prop=jp_font, fontsize=8.5, framealpha=0.92)


# -------------------------------------------------------------
# Panel 2: New Proposal Overlay & Edge.Cuts Options (新設計案)
# -------------------------------------------------------------
ax2.set_title("【新設計案】新ネジ穴 (M2 4箇所) と基板外形 (Edge.Cuts) の検討\n(カップ内側ネジ穴 X=+-4.5, Y=+-9.6 mm との整合)",
              fontproperties=jp_font_bold, fontsize=13, pad=12)

# Option A Edge.Cuts: Same outer shape (23.5 x 33.0 mm)
optA_rect = patches.FancyBboxPatch((-11.75, -16.0), 23.5, 33.0,
                                   boxstyle="round,pad=0,rounding_size=3.0",
                                   facecolor="#f9fbe7", edgecolor="#2e7d32", linewidth=2.0, linestyle="-")
ax2.add_patch(optA_rect)

# Option B Edge.Cuts: Compact shape (21.0 x 27.0 mm)
optB_rect = patches.FancyBboxPatch((-10.5, -13.5), 21.0, 27.0,
                                   boxstyle="round,pad=0,rounding_size=2.5",
                                   facecolor="none", edgecolor="#8e24aa", linewidth=2.0, linestyle="-.")
ax2.add_patch(optB_rect)

# Trackball cup outer circle (dia 28.0 mm, R=14.0 mm)
cup_circle_new = patches.Circle((0, 0), 14.0, fill=False, edgecolor="#0288d1", linewidth=1.8, linestyle="--")
ax2.add_patch(cup_circle_new)

# Optical opening
ax2.add_patch(patches.Rectangle((-8.65, -4.35), 17.3, 8.7, facecolor="#ffffff", edgecolor="#e65100", linewidth=1.5))

# IC body
ax2.add_patch(patches.Rectangle((-7.1, -9.8), 14.2, 19.6, facecolor="none", edgecolor="#616161", linewidth=1.2, linestyle=":"))

# J1 connector
ax2.add_patch(patches.Rectangle((-11.0, 0.5), 2.54, 8 * 2.54, facecolor="#fff9c4", edgecolor="#fbc02d", linewidth=1.2))

# Old mounting holes in faint dashed red
for hx, hy in old_holes:
    ax2.add_patch(patches.Circle((hx, hy), 1.6, facecolor="none", edgecolor="#e57373", linewidth=1.2, linestyle=":"))

# New mounting holes: 4x M2 (dia 2.2 mm, r=1.1 mm) at (+-4.50, +-9.60)
new_holes = [(-4.50, -9.60), (4.50, -9.60), (-4.50, 9.60), (4.50, 9.60)]
for hx, hy in new_holes:
    hole = patches.Circle((hx, hy), 1.1, facecolor="#c8e6c9", edgecolor="#1b5e20", linewidth=2.0)
    ax2.add_patch(hole)
    ax2.plot(hx, hy, '+', color='#1b5e20', markersize=7)
    ax2.annotate(f"新M2穴 ({hx:+.1f}, {hy:+.1f})", (hx, hy), textcoords="offset points",
                 xytext=(12 if hx > 0 else -70, 7 if hy > 0 else -16),
                 fontproperties=jp_font, fontsize=8.5, color="#1b5e20",
                 bbox=dict(boxstyle="round,pad=0.2", fc="#ffffff", ec="#81c784", alpha=0.9))

# Dimension line between new holes (pitch X = 9.0mm, pitch Y = 19.2mm)
ax2.annotate('', xy=(4.5, 9.6), xytext=(-4.5, 9.6), arrowprops=dict(arrowstyle='<->', color='#1b5e20', lw=1.2))
ax2.text(0, 10.3, "ピッチ 9.0 mm", fontproperties=jp_font, fontsize=8.5, ha='center', color='#1b5e20')

ax2.annotate('', xy=(4.5, 9.6), xytext=(4.5, -9.6), arrowprops=dict(arrowstyle='<->', color='#1b5e20', lw=1.2))
ax2.text(5.5, 0, "ピッチ 19.2 mm", fontproperties=jp_font, fontsize=8.5, ha='left', va='center', color='#1b5e20', rotation=90)

# Legend for panel 2
ax2.plot([], [], color="#2e7d32", linewidth=2.0, label="外形 案A: 現行外形維持 (23.5 x 33.0 mm)")
ax2.plot([], [], color="#8e24aa", linewidth=2.0, linestyle="-.", label="外形 案B: コンパクト外形 (21.0 x 27.0 mm)")
ax2.plot([], [], color="#0288d1", linewidth=1.8, linestyle="--", label="トラックボールカップ外周 (dia 28mm)")
ax2.plot([], [], 'o', color="#c8e6c9", markeredgecolor="#1b5e20", label="新M2ネジ穴 (dia 2.2mm, 4箇所)")
ax2.plot([], [], 'o', color="none", markeredgecolor="#e57373", linestyle=":", label="旧M3ネジ穴 (廃止)")
ax2.plot([], [], color="#fbc02d", linewidth=3.0, label="J1ピンヘッダ (1x8)")
ax2.legend(loc="upper right", prop=jp_font, fontsize=8.5, framealpha=0.92)

plt.tight_layout()
out_png = Path(r"C:\Users\oktnt\.gemini\antigravity\brain\dab819aa-2c9f-4dd2-be5e-39a298725eca\pmw3360_pcb_comparison.png")
plt.savefig(out_png, dpi=180)
print(f"Saved comparison to: {out_png}")
