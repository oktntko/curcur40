import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.font_manager as fm
from PIL import Image
import numpy as np
from pathlib import Path

font_path = r"C:\Windows\Fonts\meiryo.ttc"
jp_font = fm.FontProperties(fname=font_path)
jp_font_bold = fm.FontProperties(fname=font_path, weight='bold')

img_path = r"C:\Users\oktnt\.gemini\antigravity\brain\dab819aa-2c9f-4dd2-be5e-39a298725eca\render_pmw3360_top.png"
im = Image.open(img_path)

# Board physical dimensions:
# Width: 23.50 mm (X: -11.75 to +11.75)
# Height: 33.00 mm (Y: -16.0 to +17.0, so center Y is at +0.50 mm)
# In image (1176 x 1176), board occupies approximately:
# Let's inspect where board edges are in pixel space:
# Top edge ~ y=30, bottom edge ~ y=1140 -> height ~ 1110 px -> ~33.6 px/mm
# Left edge ~ x=125, right edge ~ x=915 -> width ~ 790 px -> ~33.6 px/mm
# Center of optical aperture: X ~ 520 px, Y ~ 590 px

fig, ax = plt.subplots(figsize=(10, 10), dpi=160)
fig.patch.set_facecolor('#ffffff')
ax.imshow(im)
ax.set_title("【実基板レイアウト重ね合わせ】新M2ネジ穴・カップ外周と既存パターンの位置関係",
             fontproperties=jp_font_bold, fontsize=13, pad=12)

# Approximate pixel mapping:
# Optical center (0, 0) is around pixel (588, 565)
# Scale: ~33.2 pixels per mm
ox = 588
oy = 565
scale = 33.2

def to_px(x, y):
    # in image, Y goes down, so y_px = oy - y * scale
    return ox + x * scale, oy - y * scale

# 1. Trackball cup outer circle (dia 28 mm, R = 14 mm)
r_px = 14.0 * scale
cup_circ = patches.Circle((ox, oy), r_px, fill=False, edgecolor="#00b0ff", linewidth=2.5, linestyle="--", label="新トラックボールカップ外周 (dia 28mm)")
ax.add_patch(cup_circ)

# 2. Old M3 holes (ghost)
old_holes = [(-8.75, -13.0), (8.75, -13.0), (-8.75, 14.0), (8.75, 14.0)]
for hx, hy in old_holes:
    px, py = to_px(hx, hy)
    c = patches.Circle((px, py), 1.6 * scale, fill=False, edgecolor="#ef5350", linewidth=2.0, linestyle=":")
    ax.add_patch(c)
ax.plot([], [], 'o', color="none", markeredgecolor="#ef5350", linestyle=":", label="旧M3ネジ穴 (廃止)")

# 3. New M2 holes (dia 2.2 mm, r = 1.1 mm) at (+-4.50, +-9.60)
new_holes = [(-4.50, -9.60), (4.50, -9.60), (-4.50, 9.60), (4.50, 9.60)]
for hx, hy in new_holes:
    px, py = to_px(hx, hy)
    # Hole cut
    h_patch = patches.Circle((px, py), 1.1 * scale, facecolor="#00e676", edgecolor="#1b5e20", linewidth=2.2, alpha=0.75)
    ax.add_patch(h_patch)
    # Screw head seat area (dia 3.8 mm, r = 1.9 mm)
    seat_patch = patches.Circle((px, py), 1.9 * scale, fill=False, edgecolor="#1b5e20", linewidth=1.2, linestyle="--")
    ax.add_patch(seat_patch)
    ax.plot(px, py, '+', color='#1b5e20', markersize=8, markeredgewidth=2)
    ax.annotate(f"新M2穴\n({hx:+.1f}, {hy:+.1f})", (px, py), textcoords="offset points",
                xytext=(15 if hx > 0 else -75, 10 if hy > 0 else -28),
                fontproperties=jp_font, fontsize=9, color="#1b5e20",
                bbox=dict(boxstyle="round,pad=0.2", fc="#ffffff", ec="#00e676", alpha=0.95))

ax.plot([], [], 'o', color="#00e676", markeredgecolor="#1b5e20", label="新M2ネジ穴 (dia 2.2mm / 座面 dia 3.8mm)")

# Pitch dimensions
p1x, p1y = to_px(-4.5, 9.6)
p2x, p2y = to_px(4.5, 9.6)
ax.annotate('', xy=(p2x, p2y), xytext=(p1x, p1y), arrowprops=dict(arrowstyle='<->', color='#1b5e20', lw=1.5))
ax.text((p1x+p2x)/2, p1y - 18, "ピッチ 9.0 mm", fontproperties=jp_font, fontsize=9, ha='center', color='#1b5e20',
        bbox=dict(boxstyle="round,pad=0.15", fc="#ffffff", ec="#1b5e20", alpha=0.9))

p3x, p3y = to_px(4.5, -9.6)
ax.annotate('', xy=(p2x, p3y), xytext=(p2x, p2y), arrowprops=dict(arrowstyle='<->', color='#1b5e20', lw=1.5))
ax.text(p2x + 18, (p2y+p3y)/2, "ピッチ 19.2 mm", fontproperties=jp_font, fontsize=9, ha='left', va='center', color='#1b5e20', rotation=-90,
        bbox=dict(boxstyle="round,pad=0.15", fc="#ffffff", ec="#1b5e20", alpha=0.9))

# Optical Center marker
ax.plot(ox, oy, 'x', color='#e65100', markersize=10, markeredgewidth=2.5, label="光学中心 (0, 0)")

ax.legend(loc="lower left", prop=jp_font, fontsize=9, framealpha=0.95)
ax.axis('off')

plt.tight_layout()
out_png = Path(r"C:\Users\oktnt\.gemini\antigravity\brain\dab819aa-2c9f-4dd2-be5e-39a298725eca\pmw3360_actual_overlay.png")
plt.savefig(out_png, dpi=180)
print(f"Saved actual overlay to: {out_png}")
