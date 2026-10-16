# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from pathlib import Path

# Set font for Japanese
plt.rcParams['font.family'] = 'Yu Gothic UI'
plt.rcParams['axes.unicode_minus'] = False

OUT_PNG = Path(r"C:\Users\oktnt\.gemini\antigravity\brain\dab819aa-2c9f-4dd2-be5e-39a298725eca\stage3_trackball_investigation.png")

fig, ax = plt.subplots(figsize=(11, 9.5), dpi=150)

# Trackball center in PCB coordinates
cx, cy = 7.525, 52.3875

# 1. Right Main PCB Edge.Cuts
# Bottom straight edge at Y = 63.1625 from X = -4.263 to 25.0
# Left edge at X = -5.263 from Y = 38.800 to 62.163
# Arc from (-5.263, 62.163) to (-4.263, 63.163)
ax.plot([-5.263, -5.263, -4.263, 25.0], [38.800, 62.163, 63.163, 63.163], 'k-', lw=2.5, label='現行PCB外形 (Edge.Cuts)')

# Shaded PCB area
pcb_poly = patches.Polygon([(-5.263, 38.0), (-5.263, 62.163), (-4.263, 63.163), (25.0, 63.163), (25.0, 38.0)],
                           facecolor='lightgreen', alpha=0.2, label='基板領域 (手前側)')
ax.add_patch(pcb_poly)

# Case outer wall: Y_step = -122.3125 => y_pcb = 65.1625
ax.axhline(65.1625, color='gray', ls='--', lw=1.8, label='右ケース外壁 (y = 65.16mm)')
# Case inner wall: y_pcb = 63.6625
ax.axhline(63.6625, color='gray', ls=':', lw=1.2, label='右ケース内壁 (y = 63.66mm)')

# 2. Existing central circle cutout (R = 5.0 mm)
center_hole = patches.Circle((cx, cy), 5.0, facecolor='white', edgecolor='purple', ls='--', lw=1.5, label='現行開口部 (R=5.0mm)')
ax.add_patch(center_hole)

# 3. Trackball Cup boundary (R = 14.00 mm)
cup_circle = patches.Circle((cx, cy), 14.0, facecolor='none', edgecolor='blue', lw=2.0, label='トラックボールカップ外周 (R=14.0mm)')
ax.add_patch(cup_circle)

# 4. Existing SPI tracks on bottom of PCB (B.Cu)
spi_tracks = [
    (60.71, '+3V3R', 'orange'),
    (61.26, '/SCLK', 'teal'),
    (61.81, '/MOSI', 'magenta'),
    (62.36, '/MISO', 'brown'),
]
for y_tr, name, col in spi_tracks:
    ax.plot([0.0, 22.0], [y_tr, y_tr], color=col, lw=1.3, ls='-', label=f'既存配線 {name} (y={y_tr:.2f})')

# 5. rJ3 footprint at (-2.725, 61.7705)
ax.plot(-2.725, 61.7705, 's', color='darkred', markersize=10, label='rJ3 コネクタ (-2.73, 61.77)')
ax.text(-2.725, 61.7705 - 1.2, 'rJ3 (PMW3360 Conn)', ha='center', fontsize=9, color='darkred', weight='bold')

# 6. TRRS rJ2 at (4.268, 34.646)
ax.plot(4.268, 34.646, '^', color='brown', markersize=10, label='rJ2 (TRRS) (4.27, 34.65)')
ax.text(4.268, 34.646 + 1.2, 'rJ2 (TRRS Jack)', ha='center', fontsize=9, color='brown', weight='bold')

# 7. Proposed 4x M2 Holes at (cx +- 4.5, cy +- 10.0)
hole_coords = [
    (cx - 4.5, cy - 10.0, '奥側左 (3.03, 42.39)'),
    (cx + 4.5, cy - 10.0, '奥側右 (12.03, 42.39)'),
    (cx - 4.5, cy + 10.0, '手前左 (3.03, 62.39)'),
    (cx + 4.5, cy + 10.0, '手前右 (12.03, 62.39)'),
]

for hx, hy, lbl in hole_coords:
    # M2 hole dia 2.2mm
    is_bottom = (hy > cy)
    edge_col = 'red' if is_bottom else 'green'
    fill_col = '#ffcccc' if is_bottom else '#ccffcc'
    hole_pat = patches.Circle((hx, hy), 1.1, facecolor=fill_col, edgecolor=edge_col, lw=2.0)
    ax.add_patch(hole_pat)
    ax.plot(hx, hy, '+', color=edge_col, markersize=8)
    ax.text(hx, hy + (1.6 if is_bottom else -1.6), lbl, ha='center', fontsize=8.5, weight='bold', color=edge_col)

# Annotations pointing out the issues
ax.annotate('【課題①】基板端(y=63.16)までわずか 0.77mm！\n穴径2.2mm(半径1.1mm)のため基板外へ 0.33mm はみ出す',
            xy=(cx - 4.5, cy + 10.0 + 1.1), xytext=(cx - 4.5 - 4.2, cy + 10.0 + 4.5),
            arrowprops=dict(facecolor='red', edgecolor='red', arrowstyle='->', lw=1.5),
            fontsize=9.5, color='darkred', weight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#ffeeee', edgecolor='red'))

ax.annotate('【課題②】カップ外周(R=14mm)が基板端を 3.2mm、\nケース外壁を 1.2mm はみ出す',
            xy=(cx, cy + 14.0), xytext=(cx + 3.0, cy + 14.0 + 3.0),
            arrowprops=dict(facecolor='blue', edgecolor='blue', arrowstyle='->', lw=1.5),
            fontsize=9.5, color='blue', weight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#eef6ff', edgecolor='blue'))

ax.annotate('【課題③】既存SPI配線(4本)が\nネジ穴位置の真下を通過している',
            xy=(cx + 4.5, 61.8), xytext=(cx + 4.5 + 2.5, 61.8 - 4.5),
            arrowprops=dict(facecolor='purple', edgecolor='purple', arrowstyle='->', lw=1.5),
            fontsize=9.5, color='purple', weight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#f9eeff', edgecolor='purple'))

# Proposed PCB extension line (Option A)
tab_x = [-4.0, -4.0, 19.0, 19.0]
tab_y = [63.1625, 67.5, 67.5, 63.1625]
ax.plot(tab_x, tab_y, color='darkorange', ls='--', lw=2.0, label='案A: 基板外形の手前張り出し案 (+4.3mm)')
ax.fill_between([-4.0, 19.0], [63.1625, 63.1625], [67.5, 67.5], color='orange', alpha=0.15)

# Trackball center mark
ax.plot(cx, cy, 'b+', markersize=14, markeredgewidth=2)
ax.text(cx + 0.5, cy - 0.5, 'トラックボール中心 (7.525, 52.3875)', fontsize=10, weight='bold', color='blue')

ax.set_aspect('equal')
ax.set_xlim(-8, 25)
ax.set_ylim(70, 32) # Inverted Y for PCB coordinates (KiCad top-to-bottom)
ax.set_xlabel('X座標 (mm) [KiCad座標系]', fontsize=11)
ax.set_ylabel('Y座標 (mm) [KiCad座標系 (下方向が手前)]', fontsize=11)
ax.set_title('右メイン基板（ステップ3）トラックボール周辺の幾何検証と課題', fontsize=13, weight='bold', pad=15)
ax.grid(True, linestyle='--', alpha=0.4)
ax.legend(loc='upper right', fontsize=8.5, framealpha=0.9)

plt.tight_layout()
plt.savefig(OUT_PNG, bbox_inches='tight')
print(f"Saved investigation diagram to: {OUT_PNG}")
