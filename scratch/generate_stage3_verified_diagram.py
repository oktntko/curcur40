# -*- coding: utf-8 -*-
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

plt.rcParams['font.family'] = 'Yu Gothic UI'
plt.rcParams['axes.unicode_minus'] = False

with open("scratch/pcb_plot_data.json", "r") as f:
    data = json.load(f)

fig, ax = plt.subplots(figsize=(10, 10), dpi=150)

# Set view region around trackball
ax.set_aspect('equal')
ax.set_xlim(-7, 26)
ax.set_ylim(70, 36)
ax.grid(True, ls='--', alpha=0.35)

cx, cy = 7.525, 52.3875

# 1. Edge.Cuts
for dr in data["drawings"]:
    if dr["type"] == "line":
        sx, sy = dr["start"]
        ex, ey = dr["end"]
        if (-8 <= sx <= 30 or -8 <= ex <= 30) and (30 <= sy <= 72 or 30 <= ey <= 72):
            ax.plot([sx, ex], [sy, ey], 'k-', lw=2.5)
    elif dr["type"] == "arc":
        cx_a, cy_a = dr["center"]
        r = dr["radius"]
        arc_pat = patches.Arc((cx_a, cy_a), 2*r, 2*r, angle=0, theta1=0, theta2=360, edgecolor='k', lw=2.5)
        ax.add_patch(arc_pat)
    elif dr["type"] == "circle":
        c = dr["center"]
        r = dr["radius"]
        cir = patches.Circle((c[0], c[1]), r, fill=False, edgecolor='k', lw=2.0)
        ax.add_patch(cir)

# 2. Tracks
for tr in data["tracks"]:
    sx, sy = tr["start"]
    ex, ey = tr["end"]
    if (-7 <= sx <= 26 or -7 <= ex <= 26) and (36 <= sy <= 70 or 36 <= ey <= 70):
        net = tr["net"]
        w = tr["width"]
        if tr["layer"] == "F.Cu":
            col = 'red'
            ls = '--'
        else:
            col = 'blue'
            ls = '-'
        ax.plot([sx, ex], [sy, ey], color=col, lw=w*5, ls=ls)

for p in data["vias"]:
    px, py = p
    if -7 <= px <= 26 and 36 <= py <= 70:
        ax.add_patch(patches.Circle((px, py), 0.4, facecolor='gold', edgecolor='black', lw=1.0))

# 3. Holes
for h in data["holes"]:
    hx, hy = h["pos"]
    ref = h["ref"]
    dr = h["drill"]
    if -7 <= hx <= 26 and 36 <= hy <= 70:
        is_h = ref.startswith("rH")
        edge_col = 'red' if is_h else 'gray'
        ax.add_patch(patches.Circle((hx, hy), dr/2, facecolor='white', edgecolor=edge_col, lw=1.8))
        if is_h:
            ax.text(hx, hy - 1.6, f'{ref} (M2)', ha='center', fontsize=9, weight='bold', color='darkred')

for fp in data["fps"]:
    ref = fp["ref"]
    px, py = fp["pos"]
    if -7 <= px <= 26 and 36 <= py <= 70:
        if not ref.startswith("rH"):
            ax.text(px, py, ref, ha='center', fontsize=8, color='green', weight='bold')

# Trackball cup outline overlay
ax.add_patch(patches.Circle((cx, cy), 14.0, fill=False, edgecolor='deepskyblue', ls=':', lw=2.0, label='トラックボールカップ外周 (R=14.0mm)'))
ax.plot(cx, cy, 'b+', markersize=12, markeredgewidth=2)
ax.text(cx + 0.5, cy - 0.5, 'トラックボール中心', color='blue', fontsize=9, weight='bold')

# Reference lines
ax.axhline(63.1625, color='gray', ls=':', lw=1.2, label='旧基板端 (Y=63.16mm)')
ax.axhline(67.500, color='green', ls='--', lw=1.2, label='新基板手前端 (Y=67.50mm)')

# Annotations
ax.annotate('新基板外形（+4.34mm拡張タブ＆45度テーパー）\n手前ネジ穴に約4mmの十分な基板肉厚を確保',
            xy=(10.0, 67.5), xytext=(0.5, 69.3),
            arrowprops=dict(facecolor='black', arrowstyle='->', lw=1.2),
            fontsize=9.5, weight='bold', bbox=dict(boxstyle='round', facecolor='#eefbee'))

ax.annotate('SPI 4本配線（B.Cu）\n手前ネジ穴の下を均一ピッチで安全に迂回',
            xy=(12.0, 65.4), xytext=(12.0, 58.5),
            arrowprops=dict(facecolor='blue', arrowstyle='->', lw=1.2),
            fontsize=9.5, weight='bold', color='blue', bbox=dict(boxstyle='round', facecolor='#eef2ff'))

ax.annotate('/NCS 配線（F.Cu）\n奥側ネジ穴の上部を迂回（クリアランス>1.4mm）',
            xy=(7.5, 39.8), xytext=(7.5, 46.0),
            arrowprops=dict(facecolor='red', arrowstyle='->', lw=1.2),
            fontsize=9.5, weight='bold', color='darkred', bbox=dict(boxstyle='round', facecolor='#ffeeee'))

ax.set_title('右メイン基板（ステップ3）トラックボール部の修正結果（KiCad配線＆外形検証図）', fontsize=12, weight='bold', pad=12)
ax.set_xlabel('X座標 (mm) [KiCad座標系]', fontsize=10)
ax.set_ylabel('Y座標 (mm) [KiCad座標系 (下方向が手前)]', fontsize=10)
ax.legend(loc='lower left', fontsize=8.5)

out_file = r"C:\Users\oktnt\.gemini\antigravity\brain\dab819aa-2c9f-4dd2-be5e-39a298725eca\stage3_pcb_verified_diagram.png"
plt.tight_layout()
plt.savefig(out_file, bbox_inches='tight')
print("Saved diagram to:", out_file)
