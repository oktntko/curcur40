# -*- coding: utf-8 -*-
import cadgen.build123d as bd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

plt.rcParams['font.family'] = 'Yu Gothic UI'
plt.rcParams['axes.unicode_minus'] = False

# Trackball center in case coordinates
cx, cy = 21.8125, -109.5375

fig, ax = plt.subplots(figsize=(10, 10), dpi=150)
ax.set_aspect('equal')
ax.set_xlim(0, 45)
ax.set_ylim(-130, -90)
ax.grid(True, ls='--', alpha=0.35)

# 1. Existing Case walls in right.step
# Left outer wall: X = 7.025
# Left inner wall: X = 8.525
# Front outer wall: Y = -122.3125
# Front inner wall: Y = -120.8125
ax.axvline(7.025, color='black', lw=2.0, label='現行ケース外壁 (左: X=7.03, 手前: Y=-122.31)')
ax.axhline(-122.3125, color='black', lw=2.0)
ax.axvline(8.525, color='gray', ls='--', lw=1.2, label='現行ケース内壁 (左: X=8.53, 手前: Y=-120.81)')
ax.axhline(-120.8125, color='gray', ls='--', lw=1.2)

# 2. Existing floor cutout in right.step: X in [17.21, 26.41], Y in [-118.44, -100.64]
old_cutout = patches.Rectangle((17.21, -118.44), 26.41 - 17.21, -100.64 - (-118.44),
                               fill=True, facecolor='#eeeeee', edgecolor='purple', ls='--', lw=1.5,
                               label='現行ケース底面開口 (9.2 x 17.8mm)')
ax.add_patch(old_cutout)

# 3. Trackball Cup outline (R = 14.0 mm)
cup = patches.Circle((cx, cy), 14.0, fill=False, edgecolor='blue', lw=2.0, label='トラックボールカップ外周 (R=14.0mm)')
ax.add_patch(cup)
ax.plot(cx, cy, 'b+', markersize=12, markeredgewidth=2)
ax.text(cx + 0.5, cy + 0.5, 'トラックボール中心 (21.81, -109.54)', color='blue', fontsize=9, weight='bold')

# 4. New Unified 4x M2 Mounting Holes (cx +- 4.5, cy +- 10.0)
holes = [
    (cx - 4.5, cy + 10.0, 'H1: 奥側左 (17.31, -99.54)'),
    (cx + 4.5, cy + 10.0, 'H2: 奥側右 (26.31, -99.54)'),
    (cx - 4.5, cy - 10.0, 'H3: 手前左 (17.31, -119.54)'),
    (cx + 4.5, cy - 10.0, 'H4: 手前右 (26.31, -119.54)'),
]
for hx, hy, lbl in holes:
    ax.add_patch(patches.Circle((hx, hy), 1.1, facecolor='#ffcccc', edgecolor='red', lw=1.8))
    ax.plot(hx, hy, 'r+', markersize=8)
    ax.text(hx, hy - 1.6, lbl, ha='center', fontsize=8, color='darkred', weight='bold')

# 5. Right Main PCB new bottom edge overlay (Step 3)
# In case coords: PCB edge extends to Y = -124.65 mm, with 45 deg chamfer to X = 37.12 mm
pcb_tab_x = [8.525, 8.525, 32.7875, 37.125, 45.0]
pcb_tab_y = [-90.0, -124.65, -124.65, -120.3125, -120.3125]
ax.plot(pcb_tab_x, pcb_tab_y, color='darkorange', lw=2.2, ls='-', label='修正後メインPCB外形 (手前Y=-124.65mm)')

# 6. PMW3360 Compact PCB outline (21.75 x 26.50 mm)
pmw_rect = patches.Rectangle((cx - 21.75/2, cy - 26.5/2), 21.75, 26.50,
                             fill=False, edgecolor='green', lw=1.8, ls='-.',
                             label='PMW3360センサー基板 (21.75 x 26.5mm)')
ax.add_patch(pmw_rect)

# 7. Proposed Case Modification (Front Bulge / Bezel)
# Case front wall expanded around trackball to Y_outer = -126.65 mm
case_new_x = [7.025, 7.025, 34.0, 39.5, 45.0]
case_new_y = [-90.0, -126.65, -126.65, -122.3125, -122.3125]
ax.plot(case_new_x, case_new_y, color='red', lw=2.5, ls='--', label='ケース修正案: 手前壁拡張 (+4.34mm)')

# Annotations
ax.annotate('【課題①】カップ外周(R=14mm)が\n現行ケース外壁(Y=-122.31)を1.23mmはみ出す',
            xy=(cx, cy - 14.0), xytext=(cx - 15.0, -128.5),
            arrowprops=dict(facecolor='blue', arrowstyle='->', lw=1.5),
            fontsize=9.5, color='blue', weight='bold',
            bbox=dict(boxstyle='round', facecolor='#eef6ff', edgecolor='blue'))

ax.annotate('【課題②】新メインPCBの手前拡張タブ(Y=-124.65)を\n収容するためケース手前壁を+4.34mm拡張',
            xy=(25.0, -126.65), xytext=(15.0, -133.0),
            arrowprops=dict(facecolor='red', arrowstyle='->', lw=1.5),
            fontsize=9.5, color='darkred', weight='bold',
            bbox=dict(boxstyle='round', facecolor='#ffeeee', edgecolor='red'))

ax.annotate('【課題③】現行の底面開口(紫点線)は旧ピッチ用。\n新PMW3360基板(21.75x26.5mm)および\n新ネジ位置(赤丸)に合わせて開口を拡張',
            xy=(26.31, -119.54), xytext=(29.0, -114.0),
            arrowprops=dict(facecolor='purple', arrowstyle='->', lw=1.5),
            fontsize=9.5, color='purple', weight='bold',
            bbox=dict(boxstyle='round', facecolor='#fbf0ff', edgecolor='purple'))

ax.set_ylim(-136, -92)
ax.set_title('右3Dプリントケース（ステップ4）トラックボール部の幾何検証と課題', fontsize=12, weight='bold', pad=12)
ax.set_xlabel('X座標 (mm) [ケース座標系]', fontsize=10)
ax.set_ylabel('Y座標 (mm) [ケース座標系 (下方向が手前)]', fontsize=10)
ax.legend(loc='upper right', fontsize=8.5)

out_file = r"C:\Users\oktnt\.gemini\antigravity\brain\dab819aa-2c9f-4dd2-be5e-39a298725eca\stage4_case_investigation.png"
plt.tight_layout()
plt.savefig(out_file, bbox_inches='tight')
print("Saved diagram to:", out_file)
