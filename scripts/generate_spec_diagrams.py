# -*- coding: utf-8 -*-
"""
Generate engineering specification diagrams for curcur40 case documentation.
Outputs high-resolution diagrams to docs/curcur40/assets/
"""
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

ASSETS_DIR = Path(r"c:\Users\oktnt\workspace\curcur40\docs\curcur40\assets")
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#444444'
plt.rcParams['axes.linewidth'] = 0.8

def generate_vertical_stackup_diagram():
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=200)
    ax.set_xlim(-20, 160)
    ax.set_ylim(-14, 2)
    ax.set_facecolor('#fcfcfc')
    fig.patch.set_facecolor('#ffffff')

    layers = [
        ("Top Plate (FR4)", 0.0, -1.6, '#3a7ca5', 0.85, '#16425b'),
        ("Switch Gap (Kailh Choc v2)", -1.6, -3.6, '#e0e1dd', 0.4, '#778da9'),
        ("Main PCB (FR4)", -3.6, -5.2, '#2a9d8f', 0.85, '#1b4332'),
        ("Component Cavity (Air Gap)", -5.2, -8.4, '#f4f1de', 0.4, '#e07a5f'),
        ("Case Floor (3D Print Solid)", -8.4, -11.6, '#495057', 0.85, '#212529'),
    ]

    for name, z_top, z_bot, col, a, ec in layers:
        h = z_top - z_bot
        rect = patches.Rectangle((20, z_bot), 80, h, linewidth=1.5, edgecolor=ec, facecolor=col, alpha=a)
        ax.add_patch(rect)
        ax.text(60, (z_top + z_bot) / 2, name, ha='center', va='center', fontsize=11, fontweight='bold', color='#111111')

    # Component Protrusions on Under-PCB (B.Cu)
    # 1. Choc Socket
    sock = patches.Rectangle((28, -5.2 - 2.0), 12, 2.0, linewidth=1, edgecolor='#d90429', facecolor='#ef233c', alpha=0.85)
    ax.add_patch(sock)
    ax.text(34, -6.2, "Choc\nSocket\n(2.0mm)", ha='center', va='center', fontsize=8, color='white', fontweight='bold')

    # 2. TRRS Jack
    trrs = patches.Rectangle((48, -5.2 - 2.3), 16, 2.3, linewidth=1, edgecolor='#6a040f', facecolor='#9d0208', alpha=0.85)
    ax.add_patch(trrs)
    ax.text(56, -6.35, "TRRS Jack\n(2.3mm)", ha='center', va='center', fontsize=8, color='white', fontweight='bold')

    # 3. PMW3360 Sensor Body
    pmw = patches.Rectangle((70, -5.2 - 2.2), 18, 2.2, linewidth=1, edgecolor='#003049', facecolor='#0077b6', alpha=0.85)
    ax.add_patch(pmw)
    ax.text(79, -6.3, "PMW3360 IC\n(2.2mm)", ha='center', va='center', fontsize=8, color='white', fontweight='bold')

    # Standoff Representation
    standoff = patches.Rectangle((108, -8.7), 6, 5.1, linewidth=1.5, edgecolor='#d4a373', facecolor='#faedcd', hatch='//')
    ax.add_patch(standoff)
    ax.text(111, -6.15, "M2\n5.5mm\nSpacer", ha='center', va='center', fontsize=8, fontweight='bold', color='#6b705c')

    # Case Floor Counterbore
    cb = patches.Rectangle((40, -11.6), 10, 1.3, linewidth=1.2, edgecolor='#e63946', facecolor='#ffffff', linestyle='--')
    ax.add_patch(cb)
    ax.text(45, -11.6 + 0.65, "Counterbore Ø4.6 x 1.3", ha='center', va='center', fontsize=7.5, color='#e63946', fontweight='bold')

    def draw_dim(x, z1, z2, label, offset_text=0):
        ax.annotate('', xy=(x, z1), xytext=(x, z2),
                    arrowprops=dict(arrowstyle='<->', color='#2b2d42', lw=1.2))
        ax.text(x - 1.5 + offset_text, (z1 + z2) / 2, label, ha='right', va='center', fontsize=9.5, fontweight='bold', color='#2b2d42')

    draw_dim(15, 0.0, -1.6, "1.60 mm")
    draw_dim(15, -1.6, -3.6, "2.00 mm")
    draw_dim(15, -3.6, -5.2, "1.60 mm")
    draw_dim(15, -5.2, -8.4, "3.20 mm")
    draw_dim(15, -8.4, -11.6, "3.20 mm")

    draw_dim(5, 0.0, -11.6, "TOTAL: 11.60 mm", offset_text=-1)

    ax.annotate('Safe Clearance: 0.90 mm\n(Floor Z=-8.4 to Max Part Z=-7.5)',
                xy=(79, -7.4), xytext=(115, -7.8),
                arrowprops=dict(facecolor='#d90429', shrink=0.05, width=1, headwidth=5),
                fontsize=8.5, fontweight='bold', color='#d90429',
                bbox=dict(boxstyle="round,pad=0.3", fc="#ffe3e0", ec="#d90429", lw=1))

    ax.set_title("curcur40 Vertical Z-Stackup Architecture (Standard Specs)", fontsize=14, fontweight='bold', pad=15)
    ax.set_xticks([])
    ax.set_yticks([0, -1.6, -3.6, -5.2, -8.4, -11.6])
    ax.set_yticklabels(['Z=0.0 (Plate Top)', 'Z=-1.6 (Plate Bot)', 'Z=-3.6 (PCB Top)', 'Z=-5.2 (PCB Bot)', 'Z=-8.4 (Floor)', 'Z=-11.6 (Case Bot)'])
    ax.grid(axis='y', linestyle=':', alpha=0.6, color='#888888')

    plt.tight_layout()
    out_file = ASSETS_DIR / "stackup_cross_section.png"
    plt.savefig(out_file, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_file}")

def generate_ports_and_screws_diagram():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=200)
    fig.patch.set_facecolor('#ffffff')

    # AX1: TRRS Hole
    ax1.set_xlim(-2, 16)
    ax1.set_ylim(-1, 11)
    ax1.set_aspect('equal')
    ax1.set_facecolor('#f8f9fa')
    ax1.set_title("TRRS Jack Side Wall Port (Section View)", fontsize=12, fontweight='bold')

    wall = patches.Rectangle((3, 1), 6, 8, linewidth=1.5, edgecolor='#333333', facecolor='#e9ecef')
    ax1.add_patch(wall)

    center_y = 5.0
    hole_inner = patches.Rectangle((3, center_y - 2.75), 3.5, 5.5, linewidth=1.2, edgecolor='#d90429', facecolor='#ffffff')
    ax1.add_patch(hole_inner)

    hole_outer = patches.Rectangle((6.5, center_y - 3.75), 2.5, 7.5, linewidth=1.2, edgecolor='#1d3557', facecolor='#ffffff')
    ax1.add_patch(hole_outer)

    ax1.annotate('', xy=(2.2, center_y - 2.75), xytext=(2.2, center_y + 2.75),
                 arrowprops=dict(arrowstyle='<->', color='#d90429', lw=1.2))
    ax1.text(1.7, center_y, "Through-Hole\nØ 5.50 mm", ha='right', va='center', fontsize=9, fontweight='bold', color='#d90429')

    ax1.annotate('', xy=(9.8, center_y - 3.75), xytext=(9.8, center_y + 3.75),
                 arrowprops=dict(arrowstyle='<->', color='#1d3557', lw=1.2))
    ax1.text(10.3, center_y, "Plug Counterbore\nØ 7.50 mm", ha='left', va='center', fontsize=9, fontweight='bold', color='#1d3557')

    ax1.plot([2.5, 9.5], [center_y, center_y], linestyle='-.', color='#888888', lw=1)
    ax1.text(2.6, center_y + 0.3, "CL", ha='left', va='bottom', fontsize=8, color='#666666')
    ax1.axis('off')

    # AX2: Screw Counterbore
    ax2.set_xlim(-2, 16)
    ax2.set_ylim(-1, 11)
    ax2.set_aspect('equal')
    ax2.set_facecolor('#f8f9fa')
    ax2.set_title("Bottom M2 Screw Counterbore (Section View)", fontsize=12, fontweight='bold')

    floor = patches.Rectangle((2, 3), 10, 6, linewidth=1.5, edgecolor='#333333', facecolor='#dee2e6')
    ax2.add_patch(floor)

    th_hole = patches.Rectangle((7 - 1.2, 5), 2.4, 4, linewidth=1.2, edgecolor='#d90429', facecolor='#ffffff')
    ax2.add_patch(th_hole)

    cb_hole = patches.Rectangle((7 - 2.3, 3), 4.6, 2.0, linewidth=1.2, edgecolor='#1d3557', facecolor='#ffffff')
    ax2.add_patch(cb_hole)

    screw_head = patches.Rectangle((7 - 2.0, 3.2), 4.0, 0.8, linewidth=1.2, edgecolor='#495057', facecolor='#adb5bd')
    screw_shaft = patches.Rectangle((7 - 1.0, 4.0), 2.0, 3.2, linewidth=1.2, edgecolor='#495057', facecolor='#ced4da')
    ax2.add_patch(screw_head)
    ax2.add_patch(screw_shaft)

    ax2.annotate('', xy=(3.8, 3.0), xytext=(3.8, 5.0),
                 arrowprops=dict(arrowstyle='<->', color='#1d3557', lw=1.2))
    ax2.text(3.4, 4.0, "Depth: 1.3 ~ 1.5mm\n(Recessed 0.5mm)", ha='right', va='center', fontsize=8.5, fontweight='bold', color='#1d3557')

    ax2.annotate('', xy=(7 - 2.3, 2.3), xytext=(7 + 2.3, 2.3),
                 arrowprops=dict(arrowstyle='<->', color='#1d3557', lw=1.2))
    ax2.text(7.0, 1.8, "Counterbore: Ø 4.60 mm\n(Screw Head Ø 4.0mm)", ha='center', va='top', fontsize=8.5, fontweight='bold', color='#1d3557')

    ax2.annotate('', xy=(7 - 1.2, 9.3), xytext=(7 + 1.2, 9.3),
                 arrowprops=dict(arrowstyle='<->', color='#d90429', lw=1.2))
    ax2.text(7.0, 9.7, "Through Hole: Ø 2.40 mm", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#d90429')

    ax2.axis('off')

    plt.tight_layout()
    out_file = ASSETS_DIR / "ports_and_fasteners_diagram.png"
    plt.savefig(out_file, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_file}")

def generate_trackball_optical_diagram():
    fig, ax = plt.subplots(figsize=(11, 7), dpi=200)
    ax.set_xlim(-26, 26)
    ax.set_ylim(-16, 25)
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#ffffff')

    ball_center = (0, 7.0)
    ball = patches.Circle(ball_center, 17.0, linewidth=1.5, edgecolor='#0077b6', facecolor='#90e0ef', alpha=0.35)
    ax.add_patch(ball)
    ax.text(0, 11.0, "Ø 34 mm Trackball Sphere", ha='center', va='center', fontsize=12, fontweight='bold', color='#03045e')

    # Cup profile (U-shaped arc)
    cup_outline = patches.Arc((0, 7.0), 38.0, 38.0, theta1=205, theta2=335, linewidth=3, color='#023e8a')
    ax.add_patch(cup_outline)
    ax.text(-17, 3.5, "Trackball Cup Body\n(120° Claws on top)", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#023e8a')

    # Lens LM19 on F.Cu
    lens = patches.Rectangle((-10, -2.5), 20, 2.5, linewidth=1.5, edgecolor='#f77f00', facecolor='#fcbf49', alpha=0.85)
    ax.add_patch(lens)
    ax.text(0, -1.25, "LM19 Optical Lens (F.Cu side)", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#7f4f24')

    # PCB
    pcb_left = patches.Rectangle((-24, -4.1), 15.5, 1.6, linewidth=1.5, edgecolor='#2d6a4f', facecolor='#52b788', alpha=0.85)
    pcb_right = patches.Rectangle((8.5, -4.1), 15.5, 1.6, linewidth=1.5, edgecolor='#2d6a4f', facecolor='#52b788', alpha=0.85)
    ax.add_patch(pcb_left)
    ax.add_patch(pcb_right)
    ax.text(-16, -3.3, "Main PCB (1.6mm)", ha='center', va='center', fontsize=9, fontweight='bold', color='#ffffff')
    ax.text(16, -3.3, "Main PCB (1.6mm)", ha='center', va='center', fontsize=9, fontweight='bold', color='#ffffff')
    ax.text(0, -3.3, "PCB Cutout\n16.9 x 8.7 mm", ha='center', va='center', fontsize=8, fontweight='bold', color='#1b4332')

    # PMW3360 on B.Cu
    pmw_body = patches.Rectangle((-7.1, -6.5), 14.2, 2.4, linewidth=1.5, edgecolor='#14213d', facecolor='#2b2d42', alpha=0.95)
    ax.add_patch(pmw_body)
    ax.text(0, -5.3, "PMW3360 Sensor Body\n(Mounted on B.Cu, Facing Up)", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#ffffff')

    # Flat Case Floor
    floor = patches.Rectangle((-24, -11.0), 48, 2.8, linewidth=2, edgecolor='#495057', facecolor='#ced4da', alpha=0.7)
    ax.add_patch(floor)
    ax.text(0, -9.6, "Flat Case Interior Floor (Z = -8.4 mm)\nZero Cutout Needed!", ha='center', va='center', fontsize=10, fontweight='bold', color='#212529')

    # Clearance arrow
    ax.annotate('', xy=(12, -6.5), xytext=(12, -8.2),
                arrowprops=dict(arrowstyle='<->', color='#d90429', lw=1.8))
    ax.text(13.5, -7.35, "Clearance: 1.70 mm\n(Completely safe)", ha='left', va='center', fontsize=9, fontweight='bold', color='#d90429')

    ax.set_title("Trackball & Optical Sensor Stackup Alignment", fontsize=14, fontweight='bold', pad=15)
    ax.axis('off')

    plt.tight_layout()
    out_file = ASSETS_DIR / "trackball_optical_stackup.png"
    plt.savefig(out_file, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_file}")

if __name__ == "__main__":
    generate_vertical_stackup_diagram()
    generate_ports_and_screws_diagram()
    generate_trackball_optical_diagram()
    print("All specification diagram images updated successfully!")
