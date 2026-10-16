# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

plt.rcParams['font.family'] = 'Yu Gothic UI'
plt.rcParams['axes.unicode_minus'] = False

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7.5), dpi=150)

def draw_setup(ax, cx, title, shift_label):
    cy = -109.5375
    ax.set_aspect('equal')
    ax.set_xlim(5, 42)
    ax.set_ylim(-128, -92)
    ax.grid(True, ls='--', alpha=0.35)
    ax.set_title(title, fontsize=12, weight='bold')
    ax.set_xlabel('X座標 (mm) [ケース座標系]')
    ax.set_ylabel('Y座標 (mm) [ケース座標系]')
    
    # Left walls
    ax.axvline(7.025, color='black', lw=2.0, label='ケース左外壁 (X=7.03)')
    ax.axvline(8.525, color='gray', ls='--', lw=1.5, label='ケース左内壁 (X=8.53)')
    
    # Original Front inner wall
    ax.axhline(-120.8125, color='gray', ls=':', lw=1.0)
    
    # Cup
    cup_edge = cx - 14.0
    cup_color = 'red' if cup_edge < 8.525 else 'green'
    cup_pat = patches.Circle((cx, cy), 14.0, fill=True, facecolor='#eef9ee' if cup_edge >= 8.525 else '#ffeeee',
                             edgecolor=cup_color, lw=2.0, label='カップ外周 (R=14.0mm)')
    ax.add_patch(cup_pat)
    ax.plot(cx, cy, 'b+', markersize=10, markeredgewidth=2)
    ax.text(cx, cy + 1.5, f'中心 X={cx:.3f}', ha='center', fontsize=9, weight='bold', color='blue')
    
    # Cup leftmost point
    ax.plot(cup_edge, cy, 'o', color=cup_color, markersize=7)
    
    # rSW1 switch reference
    rsw1_x = 47.622 # approximate case X for rSW1
    ax.text(35, -100, '← rSW1キー側 (余裕10mm以上)', fontsize=9, color='darkgreen', weight='bold')
    
    return cup_edge

# Left plot: Current (Interference)
edge1 = draw_setup(ax1, 21.8125, '【現状】カップとケース左壁の干渉', 'シフトなし')
ax1.annotate(f'干渉量: 0.71mm！\nカップ左端 (X={edge1:.3f}) が\nケース左内壁 (X=8.525) を貫通',
             xy=(edge1, -109.5375), xytext=(11.0, -118.0),
             arrowprops=dict(facecolor='red', edgecolor='red', arrowstyle='->', lw=1.8),
             fontsize=9.5, weight='bold', color='darkred',
             bbox=dict(boxstyle='round', facecolor='#ffeeee', edgecolor='red'))
ax1.legend(loc='upper right', fontsize=8.5)

# Right plot: Shift +1.5mm (Clearance)
shift = 1.5
cx2 = 21.8125 + shift
edge2 = draw_setup(ax2, cx2, f'【改善案】右へ +{shift:.1f}mm シフト時', f'+{shift}mm')
clearance = edge2 - 8.525
ax2.annotate(f'クリアランス: +{clearance:.3f}mm\n干渉解消！壁との間に\n約0.8mmの適正隙間を確保',
             xy=(edge2, -109.5375), xytext=(11.0, -118.0),
             arrowprops=dict(facecolor='green', edgecolor='green', arrowstyle='->', lw=1.8),
             fontsize=9.5, weight='bold', color='darkgreen',
             bbox=dict(boxstyle='round', facecolor='#eefbee', edgecolor='green'))
ax2.legend(loc='upper right', fontsize=8.5)

plt.tight_layout()
out_png = r"C:\Users\oktnt\.gemini\antigravity\brain\dab819aa-2c9f-4dd2-be5e-39a298725eca\stage4_issue1_trackball_shift.png"
plt.savefig(out_png, bbox_inches='tight')
print("Saved shift comparison to:", out_png)
