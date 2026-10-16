# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

plt.rcParams['font.family'] = 'Yu Gothic UI'
plt.rcParams['axes.unicode_minus'] = False

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), dpi=150)

cx, cy = 7.525, 52.3875

def draw_common(ax, title):
    ax.set_aspect('equal')
    ax.set_xlim(-8, 28)
    ax.set_ylim(70, 36)
    ax.grid(True, ls='--', alpha=0.4)
    ax.set_title(title, fontsize=12, weight='bold')
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    
    # Trackball cup
    ax.add_patch(patches.Circle((cx, cy), 14.0, fill=False, edgecolor='blue', lw=1.5, ls='--', label='カップ外周 (R=14mm)'))
    ax.plot(cx, cy, 'b+', markersize=10)
    
    # 4 mounting holes
    holes = [
        (cx - 4.5, cy - 10.0, 'H1'),
        (cx + 4.5, cy - 10.0, 'H2'),
        (cx - 4.5, cy + 10.0, 'H3'),
        (cx + 4.5, cy + 10.0, 'H4'),
    ]
    for hx, hy, name in holes:
        ax.add_patch(patches.Circle((hx, hy), 1.1, facecolor='#ffdddd', edgecolor='red', lw=1.5))
        ax.plot(hx, hy, 'r+', markersize=6)
        ax.text(hx, hy - 1.5, f'{name} (d=2.2)', ha='center', fontsize=8, color='darkred', weight='bold')
        
    # rJ3
    ax.plot(-2.725, 61.770, 's', color='purple', markersize=8)
    ax.text(-2.725, 61.770 - 1.0, 'rJ3', ha='center', fontsize=8, color='purple')
    
    # Rerouted SPI tracks (B.Cu)
    # y = 64.20 (+3V3R), 64.75 (/SCLK), 65.30 (/MOSI), 65.85 (/MISO)
    tracks = [
        (60.712, 64.20, 1.2, '+3V3R', 'orange'),
        (61.263, 64.75, 0.0, '/SCLK', 'teal'),
        (61.812, 65.30, -0.5, '/MOSI', 'magenta'),
        (62.362, 65.85, -1.0, '/MISO', 'brown'),
    ]
    for orig_y, tab_y, west_x, net, col in tracks:
        # Route: east side (X=25 to 18) at orig_y
        # 45 deg down from (18, orig_y) to (18 - (tab_y - orig_y), tab_y)
        turn_x = 18.0 - (tab_y - orig_y)
        ax.plot([25.0, 18.0, turn_x, west_x, west_x], 
                [orig_y, orig_y, tab_y, tab_y, orig_y - 2.0], 
                color=col, lw=1.2, label=f'{net} (迂回配線)')

# Subplot 1: 90-degree step with R=1 fillets
draw_common(ax1, '形状案1: 直角ステップ (R=1mm フィレット)')
# Contour
pts1 = [
    (-5.263, 38.8),
    (-5.263, 66.5),
    (-4.263, 67.5),
    (19.0, 67.5),
    (20.0, 66.5),
    (20.0, 64.163),
    (21.0, 63.163),
    (26.0, 63.163)
]
px1, py1 = zip(*pts1)
ax1.plot(px1, py1, 'k-', lw=2.5, label='Edge.Cuts (基板外形)')
ax1.axhline(63.163, color='gray', ls=':', lw=1.0, label='旧基板端 (y=63.16)')
ax1.legend(loc='upper right', fontsize=8)

# Subplot 2: 45-degree chamfer transition
draw_common(ax2, '形状案2: 45度テーパー (滑らかな斜め移行)')
pts2 = [
    (-5.263, 38.8),
    (-5.263, 66.5),
    (-4.263, 67.5),
    (18.5, 67.5),
    (22.8375, 63.163),
    (26.0, 63.163)
]
px2, py2 = zip(*pts2)
ax2.plot(px2, py2, 'k-', lw=2.5, label='Edge.Cuts (基板外形)')
ax2.axhline(63.163, color='gray', ls=':', lw=1.0, label='旧基板端 (y=63.16)')
ax2.legend(loc='upper right', fontsize=8)

plt.tight_layout()
out_png = r"C:\Users\oktnt\.gemini\antigravity\brain\dab819aa-2c9f-4dd2-be5e-39a298725eca\stage3_tab_options.png"
plt.savefig(out_png, bbox_inches='tight')
print('Saved to:', out_png)
