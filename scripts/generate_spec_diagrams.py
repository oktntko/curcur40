# -*- coding: utf-8 -*-
"""
Generate engineering specification diagrams for curcur40 case documentation.
Outputs high-resolution diagrams to docs/assets/
"""
from pathlib import Path
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

WORKSPACE = Path(__file__).resolve().parent.parent
ASSETS_DIR = WORKSPACE / "docs" / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams['font.sans-serif'] = ['Meiryo', 'Yu Gothic', 'MS Gothic', 'DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['axes.edgecolor'] = '#444444'
plt.rcParams['axes.linewidth'] = 0.8

def generate_vertical_stackup_diagram():
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=200)
    ax.set_xlim(-20, 160)
    ax.set_ylim(-15, 2)
    ax.set_facecolor('#fcfcfc')
    fig.patch.set_facecolor('#ffffff')

    layers = [
        ("Top Plate (FR4)", -2.0, -3.6, '#3a7ca5', 0.85, '#16425b'),
        ("Switch Gap (Kailh Choc v2)", -3.6, -4.2, '#e0e1dd', 0.4, '#778da9'),
        ("Main PCB (FR4)", -4.2, -5.8, '#2a9d8f', 0.85, '#1b4332'),
        ("Component Cavity", -5.8, -9.1, '#f4f1de', 0.4, '#e07a5f'),
        ("Case Boss & Tilted Floor (2.40mm Clamp)", -9.1, -11.5, '#495057', 0.85, '#212529'),
    ]

    for name, z_top, z_bot, col, a, ec in layers:
        h = z_top - z_bot
        rect = patches.Rectangle((20, z_bot), 80, h, linewidth=1.5, edgecolor=ec, facecolor=col, alpha=a)
        ax.add_patch(rect)
        fs_layer = 9.0 if h < 1.0 else 10.5
        tx = 32 if name == "Component Cavity" else 60
        ax.text(tx, (z_top + z_bot) / 2, name, ha='center', va='center', fontsize=fs_layer, fontweight='bold', color='#111111')

    # Component Protrusions on Under-PCB (B.Cu at Z = -5.80 mm)
    # 1. Choc Socket (1.80mm -> Z = -7.60mm)
    sock = patches.Rectangle((46, -5.8 - 1.80), 14, 1.80, linewidth=1, edgecolor='#d90429', facecolor='#ef233c', alpha=0.85)
    ax.add_patch(sock)
    ax.text(53, -6.70, "Choc\nSocket\n(1.80mm)", ha='center', va='center', fontsize=7.5, color='white', fontweight='bold')

    # 2. Mid-Mount USB-C J1/J2 (1.65mm below B.Cu -> Z = -7.45mm)
    usbc = patches.Rectangle((63, -5.8 - 1.65), 15, 1.65, linewidth=1, edgecolor='#6a040f', facecolor='#9d0208', alpha=0.85)
    ax.add_patch(usbc)
    ax.text(70.5, -6.625, "Mid-Mount\nUSB-C\n(1.65mm)", ha='center', va='center', fontsize=7.0, color='white', fontweight='bold')

    # 3. JST SH 6-pin Connectors rJ3 / rJ5 (2.95mm -> Z = -8.75mm)
    jst = patches.Rectangle((81, -5.8 - 2.95), 16, 2.95, linewidth=1, edgecolor='#003049', facecolor='#0077b6', alpha=0.85)
    ax.add_patch(jst)
    ax.text(89, -7.27, "JST SH rJ3/rJ5\n(2.95mm)", ha='center', va='center', fontsize=7.0, color='white', fontweight='bold')

    # Standoff Representation (5.5mm perimeter standoff stands on boss top Z=-9.1, reaches Z=-3.6 under Top Plate!)
    standoff = patches.Rectangle((108, -9.1), 6, 5.5, linewidth=1.5, edgecolor='#d4a373', facecolor='#faedcd', hatch='//')
    ax.add_patch(standoff)
    ax.text(111, -6.35, "M2\n5.5mm\nSpacer\n(Under\nPlate!)", ha='center', va='center', fontsize=7.0, fontweight='bold', color='#6b705c')

    # Case Floor Counterbore (unified 2.40mm solid floor above counterbore ceiling Z=-11.50mm)
    cb = patches.Rectangle((40, -12.3), 24, 0.8, linewidth=1.2, edgecolor='#e63946', facecolor='#ffffff', linestyle='--')
    ax.add_patch(cb)
    ax.text(52, -12.3 + 0.40, "Counterbore Ø4.6 (Ceil Z=-11.5)", ha='center', va='center', fontsize=7.5, color='#e63946', fontweight='bold')

    def draw_dim(x, z1, z2, label, offset_text=0):
        ax.annotate('', xy=(x, z1), xytext=(x, z2),
                    arrowprops=dict(arrowstyle='<->', color='#2b2d42', lw=1.2))
        ax.text(x - 1.5 + offset_text, (z1 + z2) / 2, label, ha='right', va='center', fontsize=9.0, fontweight='bold', color='#2b2d42')

    draw_dim(15, -2.0, -3.6, "1.60 mm")
    draw_dim(15, -3.6, -4.2, "0.60 mm")
    draw_dim(15, -4.2, -5.8, "1.60 mm")
    draw_dim(15, -5.8, -9.1, "3.30 mm")
    draw_dim(15, -9.1, -11.5, "2.40 mm")

    draw_dim(3, 0.0, -10.0, "Pinky: 10.00 mm\n(Thumb: 26.90 mm)", offset_text=-1)
    draw_dim(122, 0.0, -9.1, "Boss Top: -9.10 mm", offset_text=18)

    ax.annotate('Pinky Skim Floor Z=-8.00 (>=0.40mm clear)\nThumb Tilted Floor drops to Z=-24.50mm',
                xy=(89, -8.75), xytext=(116, -8.3),
                arrowprops=dict(facecolor='#d90429', shrink=0.05, width=1, headwidth=5),
                fontsize=8.0, fontweight='bold', color='#d90429',
                bbox=dict(boxstyle="round,pad=0.3", fc="#ffe3e0", ec="#d90429", lw=1))

    ax.set_title("curcur40 Vertical Z-Stackup Architecture (Main PCB & Perimeter Boss)", fontsize=14, fontweight='bold', pad=15)
    ax.set_xticks([])
    ax.set_yticks([0, -2.0, -3.6, -4.2, -5.8, -9.1, -11.5])
    ax.set_yticklabels(['Z=0.0 (Case Rim)', 'Z=-2.0 (Plate Top)', 'Z=-3.6 (Plate Bot)', 'Z=-4.2 (PCB Top)', 'Z=-5.8 (PCB Bot)', 'Z=-9.1 (Boss Top)', 'Z=-11.5 (CB Ceil)'])
    ax.grid(axis='y', linestyle=':', alpha=0.6, color='#888888')

    plt.tight_layout()
    out_file = ASSETS_DIR / "stackup_cross_section.png"
    plt.savefig(out_file, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_file}")

def generate_ports_and_screws_diagram():
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5.5), dpi=200)
    fig.patch.set_facecolor('#ffffff')

    # AX1: Split / Host USB-C Port (Section View, Y coordinate mapped directly to Z in [-11.5, +1.5])
    ax1.set_xlim(-3, 17)
    ax1.set_ylim(-11.5, 1.5)
    ax1.set_aspect('equal')
    ax1.set_facecolor('#f8f9fa')
    ax1.set_title("1. Mid-Mount USB-C Port (Section View)", fontsize=12, fontweight='bold')

    # Case wall representation (X in [5.5, 8.5], Z from -11.0 to 0.0)
    wall = patches.Rectangle((5.5, -11.0), 3.0, 11.0, linewidth=1.5, edgecolor='#333333', facecolor='#e9ecef')
    ax1.add_patch(wall)

    # Top Plate inside case (Z = -3.60 to -2.00)
    tp_plate = patches.Rectangle((0.0, -3.60), 5.2, 1.60, linewidth=1.2, edgecolor='#1d3557', facecolor='#457b9d', alpha=0.85)
    ax1.add_patch(tp_plate)
    ax1.text(2.6, -2.80, "Top Plate", ha='center', va='center', fontsize=6.5, color='white', fontweight='bold')
    ax1.plot([0.0, 9.5], [-2.00, -2.00], linestyle='--', color='#1d3557', lw=1.2)
    ax1.text(9.6, -1.90, "Plate Top (Z = -2.00mm)", ha='left', va='bottom', fontsize=7.5, fontweight='bold', color='#1d3557')

    # Main PCB (Z = -5.80 to -4.20, notched for mid-mount USB-C)
    pcb_rect = patches.Rectangle((0.0, -5.80), 1.4, 1.60, linewidth=1.2, edgecolor='#1b4332', facecolor='#2d6a4f', alpha=0.85)
    ax1.add_patch(pcb_rect)

    # USB-C Cutout Height 6.20mm centered at Z = -5.85 (Z = -8.95 to -2.75)
    center_y = -5.85
    hole_straight = patches.Rectangle((5.5, -8.95), 3.0, 6.20, linewidth=1.5, edgecolor='#d90429', facecolor='#ffffff')
    ax1.add_patch(hole_straight)

    # Mid-mount TYPE-C-31-M-13C shell inside (Z = -7.45 to -4.29, height 3.16mm)
    usbc_barrel = patches.Rectangle((1.4, -7.45), 4.6, 3.16, linewidth=1.2, edgecolor='#1d3557', facecolor='#a8dadc', alpha=0.9)
    ax1.add_patch(usbc_barrel)
    ax1.text(3.7, -5.87, "USB-C\n(J1/J2)", ha='center', va='center', fontsize=6.5, color='#1d3557', fontweight='bold')

    # Concealment annotation
    ax1.text(2.8, -1.55, "Top Edge Z = -2.75mm", ha='center', va='bottom', fontsize=6.5, fontweight='bold', color='#2d6a4f',
             bbox=dict(boxstyle="round,pad=0.2", fc="#d8f3dc", ec="#2d6a4f", lw=0.8))

    # Height dimension
    ax1.annotate('', xy=(9.4, -8.95), xytext=(9.4, -2.75),
                 arrowprops=dict(arrowstyle='<->', color='#d90429', lw=1.2))
    ax1.text(9.9, center_y, "Host (N) & Split (Inner)\nHeight: 6.20 mm (R=1.50)\nCenter Z = -5.85 mm\nY_split = -86.65 mm", ha='left', va='center', fontsize=7.8, fontweight='bold', color='#d90429')

    ax1.plot([0.2, 9.4], [center_y, center_y], linestyle='-.', color='#888888', lw=1)
    ax1.axis('off')

    # AX2: Host & Split USB-C Opening (Front View, Y mapped to Z in [-11.5, +1.5])
    ax2.set_xlim(-2, 18)
    ax2.set_ylim(-11.5, 1.5)
    ax2.set_aspect('equal')
    ax2.set_facecolor('#f8f9fa')
    ax2.set_title("2. Host & Split USB-C Cutout (Front View)", fontsize=12, fontweight='bold')

    # Case wall representation (Z from -10.5 to 0.0)
    wall2 = patches.Rectangle((0, -10.5), 16, 10.5, linewidth=1.5, edgecolor='#333333', facecolor='#e9ecef')
    ax2.add_patch(wall2)

    cx2 = 8.0
    w2 = 12.00
    h2 = 6.20
    # Top Plate top line (Z = -2.00)
    ax2.plot([0, 16], [-2.00, -2.00], linestyle='--', color='#1d3557', lw=1.2)
    ax2.text(0.4, -1.85, "Top Plate Top (Z = -2.00mm)", ha='left', va='bottom', fontsize=7.5, fontweight='bold', color='#1d3557')

    # Cutout centered at Z = -5.85 (Z = -8.95 to -2.75)
    cy2 = -5.85
    cutout_bot_y = cy2 - h2 / 2  # -8.95
    cutout_top_y = cy2 + h2 / 2  # -2.75
    cutout = patches.FancyBboxPatch((cx2 - w2/2, cutout_bot_y), w2, h2,
                                    boxstyle="round,pad=0,rounding_size=1.5",
                                    linewidth=1.5, edgecolor='#d90429', facecolor='#ffffff')
    ax2.add_patch(cutout)

    # Receptacle silhouette inside (8.94 x 3.16 mm, centered at Z = -5.87)
    rec = patches.FancyBboxPatch((cx2 - 8.94/2, -5.87 - 3.16/2), 8.94, 3.16,
                                 boxstyle="round,pad=0,rounding_size=1.0",
                                 linewidth=1.2, edgecolor='#1d3557', facecolor='#a8dadc', alpha=0.85)
    ax2.add_patch(rec)
    ax2.text(cx2, -5.87, "TYPE-C-31-M-13C\n(8.94 x 3.16 mm, Z = -5.87)", ha='center', va='center', fontsize=6.8, fontweight='bold', color='#1d3557')

    # Width dimension
    ax2.annotate('', xy=(cx2 - w2/2, 0.4), xytext=(cx2 + w2/2, 0.4),
                 arrowprops=dict(arrowstyle='<->', color='#d90429', lw=1.2))
    ax2.text(cx2, 0.65, "Width: 12.00 mm (R=1.50)", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#d90429')

    # Height dimension
    ax2.annotate('', xy=(cx2 + w2/2 + 0.5, cutout_bot_y), xytext=(cx2 + w2/2 + 0.5, cutout_top_y),
                 arrowprops=dict(arrowstyle='<->', color='#d90429', lw=1.2))
    ax2.text(cx2 + w2/2 + 0.75, cy2, "Height:\n6.20 mm\n(Z = -5.85)", ha='left', va='center', fontsize=7.8, fontweight='bold', color='#d90429')

    # Concealment text at bottom
    ax2.text(cx2, -9.8, "Cutout Z = -8.95 to -2.75 mm (>=1.47mm Plug Clearance)", ha='center', va='center', fontsize=7.0, fontweight='bold', color='#2d6a4f')

    ax2.axis('off')

    # AX3: Screw Counterbore (Section View)
    ax3.set_xlim(-2, 16)
    ax3.set_ylim(-1, 11)
    ax3.set_aspect('equal')
    ax3.set_facecolor('#f8f9fa')
    ax3.set_title("3. Bottom M2 Screw Counterbore (Section View)", fontsize=12, fontweight='bold')

    floor = patches.Rectangle((2, 3), 10, 6, linewidth=1.5, edgecolor='#333333', facecolor='#dee2e6')
    ax3.add_patch(floor)

    th_hole = patches.Rectangle((7 - 1.2, 3.9), 2.4, 5.1, linewidth=1.2, edgecolor='#d90429', facecolor='#ffffff')
    ax3.add_patch(th_hole)

    cb_hole = patches.Rectangle((7 - 2.3, 3), 4.6, 0.9, linewidth=1.2, edgecolor='#1d3557', facecolor='#ffffff')
    ax3.add_patch(cb_hole)

    screw_head = patches.Rectangle((7 - 2.0, 3.1), 4.0, 0.8, linewidth=1.2, edgecolor='#495057', facecolor='#adb5bd')
    screw_shaft = patches.Rectangle((7 - 1.0, 3.9), 2.0, 4.0, linewidth=1.2, edgecolor='#495057', facecolor='#ced4da')
    ax3.add_patch(screw_head)
    ax3.add_patch(screw_shaft)

    ax3.annotate('', xy=(3.8, 3.0), xytext=(3.8, 3.9),
                 arrowprops=dict(arrowstyle='<->', color='#1d3557', lw=1.2))
    ax3.text(3.4, 3.45, "Deep Counterbore\n(100% Recessed)", ha='right', va='center', fontsize=8.5, fontweight='bold', color='#1d3557')

    ax3.annotate('', xy=(7 - 2.3, 2.3), xytext=(7 + 2.3, 2.3),
                 arrowprops=dict(arrowstyle='<->', color='#1d3557', lw=1.2))
    ax3.text(7.0, 1.8, "Counterbore: Ø 4.60 mm\n(Screw Head Ø 4.0mm)", ha='center', va='top', fontsize=8.5, fontweight='bold', color='#1d3557')

    ax3.annotate('', xy=(7 - 1.2, 9.3), xytext=(7 + 1.2, 9.3),
                 arrowprops=dict(arrowstyle='<->', color='#d90429', lw=1.2))
    ax3.text(7.0, 9.7, "Through Hole: Ø 2.40 mm\nUnified Solid Floor: 2.40 mm", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#d90429')

    ax3.axis('off')

    plt.tight_layout()
    out_file = ASSETS_DIR / "ports_and_fasteners_diagram.png"
    plt.savefig(out_file, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_file}")

def generate_trackball_optical_diagram():
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=200)
    ax.set_xlim(-26, 26)
    ax.set_ylim(-10, 32)
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#ffffff')

    # Ø 25.0 mm Trackball Sphere (Radius = 12.50 mm)
    # Ball center at (0, 18.30), bottom of ball at Z_rel = 18.30 - 12.50 = +5.80 mm
    ball_center = (0, 18.30)
    ball = patches.Circle(ball_center, 12.50, linewidth=1.5, edgecolor='#0077b6', facecolor='#90e0ef', alpha=0.35)
    ax.add_patch(ball)
    ax.text(0, 18.30, "Ø 25 mm Trackball Sphere\n(Center Z_rel = +18.30 mm, Bottom Z_rel = +5.80 mm)", ha='center', va='center', fontsize=10, fontweight='bold', color='#03045e')

    # Cup profile (U-shaped arc for 25mm ball)
    cup_outline = patches.Arc(ball_center, 27.0, 27.0, theta1=205, theta2=335, linewidth=3, color='#023e8a')
    ax.add_patch(cup_outline)
    ax.text(-18, 12.0, "Trackball Cup Body\n(Claws: N 90°, E 0°, W 180°)", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#023e8a')

    # LM19-LSI Optical Lens (sits on F.Cu at Z_rel = 0.00 to +4.80 mm, Flange at Z_rel = +3.40 to +4.80 mm)
    lens_body = patches.Rectangle((-8.25, 0.0), 16.5, 3.4, linewidth=1.2, edgecolor='#f77f00', facecolor='#ffd166', alpha=0.75)
    lens_flange = patches.Rectangle((-10.5, 3.40), 21.0, 1.4, linewidth=1.5, edgecolor='#f77f00', facecolor='#fcbf49', alpha=0.85)
    ax.add_patch(lens_body)
    ax.add_patch(lens_flange)
    ax.text(0, 4.1, "LM19 Lens Flange (Z_rel = +3.40 to +4.80 mm)", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#7f4f24')
    ax.annotate('2.40 mm Optical Tracking Distance\n(Flange Bottom Z_rel=+3.40 to Ball Bottom Z_rel=+5.80)',
                xy=(0, 5.80), xytext=(8.5, 8.2),
                arrowprops=dict(facecolor='#0077b6', shrink=0.05, width=1, headwidth=4),
                fontsize=8, fontweight='bold', color='#0077b6',
                bbox=dict(boxstyle="round,pad=0.2", fc="#e0f2fe", ec="#0077b6", lw=0.8))

    # 4 Lens Positioning Legs extending DOWN through PCB cutout
    leg_left = patches.Rectangle((-7.1, -3.35), 1.0, 3.35, linewidth=1.2, edgecolor='#d48b00', facecolor='#ffb703')
    leg_right = patches.Rectangle((6.2, -3.35), 1.0, 3.35, linewidth=1.2, edgecolor='#d48b00', facecolor='#ffb703')
    ax.add_patch(leg_left)
    ax.add_patch(leg_right)
    ax.annotate('4 Lens Legs extend DOWN\nthrough 16.9x8.7mm PCB cutout',
                xy=(7.2, -2.5), xytext=(10.5, 1.2),
                arrowprops=dict(facecolor='#d48b00', shrink=0.05, width=1, headwidth=4),
                fontsize=8, fontweight='bold', color='#d48b00',
                bbox=dict(boxstyle="round,pad=0.2", fc="#fff3cd", ec="#d48b00", lw=0.8))

    # PCB (FR-4, thickness 1.6mm: Z_rel from -1.6 to 0.0)
    pcb_left = patches.Rectangle((-24, -1.6), 15.55, 1.6, linewidth=1.5, edgecolor='#2d6a4f', facecolor='#52b788', alpha=0.85)
    pcb_right = patches.Rectangle((8.45, -1.6), 15.55, 1.6, linewidth=1.5, edgecolor='#2d6a4f', facecolor='#52b788', alpha=0.85)
    ax.add_patch(pcb_left)
    ax.add_patch(pcb_right)
    ax.text(-16, -0.8, "Sensor PCB (1.6mm)", ha='center', va='center', fontsize=9, fontweight='bold', color='#ffffff')
    ax.text(16, -0.8, "Sensor PCB (1.6mm)", ha='center', va='center', fontsize=9, fontweight='bold', color='#ffffff')
    ax.text(0, -0.8, "PCB Cutout (16.9 x 8.7 mm)", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#1b4332')

    # PMW3360DM-T2QU Sensor Package (Mounted on B.Cu, Z_rel from -4.01 to -1.60)
    pmw_body = patches.Rectangle((-8.1, -4.01), 16.2, 2.41, linewidth=1.5, edgecolor='#14213d', facecolor='#2b2d42', alpha=0.95)
    ax.add_patch(pmw_body)
    ax.text(0, -3.0, "PMW3360 IC Solid Body (2.41mm)\n[NO THROUGH-HOLE IN SENSOR]", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#ffffff')

    # 16 Sensor Metal Pins emerging from IC sides and extending UP through PCB
    ax.plot([-8.1, -9.2, -9.2], [-2.3, -2.3, 0.8], color='#ffd166', lw=2.5)
    ax.plot([8.1, 9.2, 9.2], [-2.3, -2.3, 0.8], color='#ffd166', lw=2.5)
    ax.annotate('16 Pins emerge from IC sides,\nextend UP through PCB to F.Cu',
                xy=(-9.2, 0.4), xytext=(-24, 2.5),
                arrowprops=dict(facecolor='#cca000', shrink=0.05, width=1, headwidth=4),
                fontsize=8, fontweight='bold', color='#cca000',
                bbox=dict(boxstyle="round,pad=0.2", fc="#fff9db", ec="#cca000", lw=0.8))

    # Tilted Case Interior Floor (Z_rel = -6.29 to -8.16 mm / Global Z = -22.29 to -24.16 mm)
    floor = patches.Rectangle((-24, -8.7), 48, 2.4, linewidth=2, edgecolor='#495057', facecolor='#ced4da', alpha=0.7)
    ax.add_patch(floor)
    ax.text(0, -7.5, "Tilted Case Interior Floor (Z_rel = -6.29..-8.16 mm / Global Z = -22.29..-24.16 mm)\n(Zero Through-Hole or Sensor Pocket Needed!)", ha='center', va='center', fontsize=9.0, fontweight='bold', color='#212529')

    # Clearance arrow
    ax.annotate('', xy=(11.5, -4.01), xytext=(11.5, -6.29),
                arrowprops=dict(arrowstyle='<->', color='#d90429', lw=1.8))
    ax.text(12.5, -5.15, "Clearance: >= 2.28 mm\n(Completely safe)", ha='left', va='center', fontsize=8.5, fontweight='bold', color='#d90429')

    ax.set_title("Trackball & Optical Sensor Stackup (pmw3360-lens-pcb-assembly)", fontsize=13, fontweight='bold', pad=15)
    ax.axis('off')

    plt.tight_layout()
    out_file = ASSETS_DIR / "trackball_optical_stackup.png"
    plt.savefig(out_file, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_file}")

def generate_trackball_cup_fastening_diagram():
    fig, ax = plt.subplots(figsize=(13, 9.5), dpi=200)
    ax.set_xlim(-16, 26)
    ax.set_ylim(-6.5, 7.5)
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#ffffff')

    # Center axis (X = 0)
    ax.plot([0, 0], [-6.0, 6.8], linestyle='-.', color='#888888', lw=1.2, zorder=1)
    ax.text(0, 6.9, "Center Line (CL)", ha='center', va='bottom', fontsize=9, color='#666666', fontweight='bold')

    # -------------------------------------------------------------
    # Layer 3: Case Boss at TB1..TB4 (Boss Top Z_rel = -1.6 / Global Z = -17.60 mm)
    # 2.40 mm clamping thickness (Z_rel = -4.0 to -1.6) + Ø4.60 mm counterbore below Z_rel = -4.0
    # -------------------------------------------------------------
    boss_left = patches.Rectangle((-3.4, -5.2), 1.1, 3.6, linewidth=1.5, edgecolor='#343a40', facecolor='#adb5bd', alpha=0.9, zorder=2)
    boss_right = patches.Rectangle((2.3, -5.2), 1.1, 3.6, linewidth=1.5, edgecolor='#343a40', facecolor='#adb5bd', alpha=0.9, zorder=2)
    shelf_l = patches.Rectangle((-2.3, -4.0), 1.1, 2.4, linewidth=1.5, edgecolor='#343a40', facecolor='#adb5bd', alpha=0.9, zorder=2)
    shelf_r = patches.Rectangle((1.2, -4.0), 1.1, 2.4, linewidth=1.5, edgecolor='#343a40', facecolor='#adb5bd', alpha=0.9, zorder=2)
    ax.add_patch(boss_left)
    ax.add_patch(boss_right)
    ax.add_patch(shelf_l)
    ax.add_patch(shelf_r)

    # -------------------------------------------------------------
    # Layer 2: Sensor PCB (Z_rel = -1.6 to 0.0, Thickness 1.60 mm)
    # Through-hole for spacer: X = -1.65 to +1.65 (Ø 3.30 mm)
    # Sandwiched between Case Boss Top (Z_rel = -1.6) and Cup Ear Base (Z_rel = 0.0)!
    # -------------------------------------------------------------
    pcb_left = patches.Rectangle((-14, -1.6), 12.35, 1.6, linewidth=1.5, edgecolor='#1b4332', facecolor='#52b788', alpha=0.9, zorder=2)
    pcb_right = patches.Rectangle((1.65, -1.6), 12.35, 1.6, linewidth=1.5, edgecolor='#1b4332', facecolor='#52b788', alpha=0.9, zorder=2)
    ax.add_patch(pcb_left)
    ax.add_patch(pcb_right)

    # -------------------------------------------------------------
    # Layer 1: Cup Mounting Ear (Z_rel = 0.0 to +5.50, Height 5.50 mm)
    # Stepped hole:
    #   - Lower Z_rel = 0.0 to 3.90 (3.90 mm): Ø 3.30 mm (X = +/-1.65) for 5.50mm spacer
    #   - Upper Z_rel = 3.90 to 5.50 (1.60 mm): Ø 2.40 mm (X = +/-1.20) for M2 screw clamping
    # -------------------------------------------------------------
    ear_left_low = patches.Rectangle((-9.0, 0.0), 7.35, 3.90, linewidth=1.5, edgecolor='#1d3557', facecolor='#457b9d', alpha=0.9, zorder=2)
    ear_right_low = patches.Rectangle((1.65, 0.0), 7.35, 3.90, linewidth=1.5, edgecolor='#1d3557', facecolor='#457b9d', alpha=0.9, zorder=2)
    ear_left_top = patches.Rectangle((-9.0, 3.90), 7.80, 1.60, linewidth=1.5, edgecolor='#1d3557', facecolor='#457b9d', alpha=0.9, zorder=2)
    ear_right_top = patches.Rectangle((1.20, 3.90), 7.80, 1.60, linewidth=1.5, edgecolor='#1d3557', facecolor='#457b9d', alpha=0.9, zorder=2)
    ax.add_patch(ear_left_low)
    ax.add_patch(ear_right_low)
    ax.add_patch(ear_left_top)
    ax.add_patch(ear_right_top)

    # -------------------------------------------------------------
    # Spacer (Unified M2 5.50 mm female-female standoff, OD Ø 3.00 mm)
    # Sits on Case Boss Top (Z_rel = -1.60), passes through Sensor PCB (1.60 mm)
    # and enters Cup Ear socket (3.90 mm) up to Z_rel = +3.90 mm!
    # -------------------------------------------------------------
    spacer_body = patches.Rectangle((-1.5, -1.6), 3.0, 5.50, linewidth=1.8, edgecolor='#b08968', facecolor='#eddcd2', hatch='///', zorder=3)
    ax.add_patch(spacer_body)
    thread_core = patches.Rectangle((-1.0, -1.6), 2.0, 5.50, linewidth=1.0, edgecolor='#7f5539', facecolor='#ffffff', alpha=0.85, zorder=4)
    ax.add_patch(thread_core)

    # -------------------------------------------------------------
    # Top Screw: M2 x 4.0mm (Head Ø 4.0, Shaft Ø 2.0 x 4.0mm)
    # Head rests at Z_rel = +5.50 (top of ear), passes through 1.60mm ear roof,
    # and reaches Z_rel = +1.50 (engages 2.40mm into 5.50mm spacer!)
    # -------------------------------------------------------------
    top_head = patches.Rectangle((-2.0, 5.50), 4.0, 0.8, linewidth=1.5, edgecolor='#212529', facecolor='#6c757d', zorder=5)
    top_shaft = patches.Rectangle((-1.0, 1.50), 2.0, 4.0, linewidth=1.5, edgecolor='#212529', facecolor='#495057', zorder=5)
    ax.add_patch(top_head)
    ax.add_patch(top_shaft)
    ax.plot([0, 0], [5.7, 6.3], color='#ffffff', lw=1.5, zorder=6)

    # -------------------------------------------------------------
    # Bottom Screw: M2 x 4.0mm (Head Ø 4.0, Shaft Ø 2.0 x 4.0mm)
    # Head rests at Z_rel = -4.0 (counterbore ceiling), passes through 2.40mm boss floor,
    # and reaches Z_rel = 0.0 (engages 1.60mm into 5.50mm spacer!)
    # -------------------------------------------------------------
    bot_head = patches.Rectangle((-2.0, -4.8), 4.0, 0.8, linewidth=1.5, edgecolor='#212529', facecolor='#6c757d', zorder=5)
    bot_shaft = patches.Rectangle((-1.0, -4.0), 2.0, 4.0, linewidth=1.5, edgecolor='#212529', facecolor='#495057', zorder=5)
    ax.add_patch(bot_head)
    ax.add_patch(bot_shaft)
    ax.plot([0, 0], [-4.6, -4.0], color='#ffffff', lw=1.5, zorder=6)

    # -------------------------------------------------------------
    # Thread safety gap inside spacer (Z_rel = 0.00 to +1.50, gap = 1.50 mm!)
    # -------------------------------------------------------------
    ax.annotate('', xy=(0, 1.50), xytext=(0, 0.00),
                 arrowprops=dict(arrowstyle='<->', color='#2b9348', lw=2.2), zorder=7)
    ax.text(0.3, 0.75, "1.50 mm\nScrew Gap", ha='left', va='center', fontsize=8.5, fontweight='bold', color='#2b9348',
            bbox=dict(boxstyle="round,pad=0.2", fc="#d8f3dc", ec="#2b9348", lw=0.8), zorder=7)

    # -------------------------------------------------------------
    # Left Dimensions: Layer-by-layer Stackup
    # -------------------------------------------------------------
    def dim_left(z1, z2, label, x=-11.5, color='#1d3557'):
        ax.annotate('', xy=(x, z1), xytext=(x, z2),
                    arrowprops=dict(arrowstyle='<->', color=color, lw=1.2))
        ax.text(x - 0.5, (z1 + z2) / 2, label, ha='right', va='center', fontsize=9, fontweight='bold', color=color)

    dim_left(5.5, 3.9, "1a. Ear Top Roof:\n1.60 mm (Ø2.4)", -10.5, '#1d3557')
    dim_left(3.9, 0.0, "1b. Ear Socket:\n3.90 mm (Ø3.3)", -10.5, '#1d3557')
    dim_left(0.0, -1.6, "2. Sensor PCB:\n1.60 mm (Ø3.3)", -10.5, '#1b4332')
    dim_left(-1.6, -4.0, "3. Boss Floor:\n2.40 mm (Ø2.4)", -10.5, '#343a40')

    # -------------------------------------------------------------
    # Right Annotations: Detailed Explanations
    # -------------------------------------------------------------
    ax.annotate('Top M2 x 4.0mm Screw (Head Ø4.0 x 0.8mm)\n• Passes through 1.60mm Cup Ear roof (Ø2.40mm)\n• Engages 2.40mm thread into 5.50mm Spacer',
                xy=(1.5, 4.8), xytext=(8.5, 5.2),
                arrowprops=dict(facecolor='#212529', shrink=0.05, width=1.2, headwidth=5),
                fontsize=8.5, fontweight='bold', color='#212529',
                bbox=dict(boxstyle="round,pad=0.25", fc="#e9ecef", ec="#212529", lw=0.8))

    ax.annotate('Trackball Cup Stepped Ear (Height: 5.50 mm)\n• Upper 1.60mm: Ø2.40mm hole (clamps under screw head)\n• Lower 3.90mm: Ø3.30mm socket (2.40mm thread + 1.50mm gap)',
                xy=(3.5, 2.5), xytext=(8.5, 2.5),
                arrowprops=dict(facecolor='#1d3557', shrink=0.05, width=1.2, headwidth=5),
                fontsize=8.5, fontweight='bold', color='#1d3557',
                bbox=dict(boxstyle="round,pad=0.25", fc="#e0f2fe", ec="#1d3557", lw=0.8))

    ax.annotate('Sensor PCB Sandwich (Thickness: 1.60 mm, Hole: Ø 3.30 mm)\n• Sandwiched between Case Boss (Z=-17.6) & Cup Base (Z=-16.0)\n• Unified M2 5.50mm Spacer passes through PCB into Cup Ear',
                xy=(1.65, -0.8), xytext=(8.5, -0.5),
                arrowprops=dict(facecolor='#1b4332', shrink=0.05, width=1.2, headwidth=5),
                fontsize=8.5, fontweight='bold', color='#1b4332',
                bbox=dict(boxstyle="round,pad=0.25", fc="#d8f3dc", ec="#1b4332", lw=0.8))

    ax.annotate('Case Cylindrical Boss (Top Z = -17.60 mm, OD Ø6.80 mm)\n• Hole Ø2.40mm: supports both 5.50mm Spacer & Sensor PCB\n• Unified 2.40mm clamping floor + Ø4.60mm deep counterbore\n• Bottom M2 x 4.0mm screw engages 1.60mm into Spacer',
                xy=(2.3, -2.8), xytext=(8.5, -3.5),
                arrowprops=dict(facecolor='#d90429', shrink=0.05, width=1.2, headwidth=5),
                fontsize=8.5, fontweight='bold', color='#d90429',
                bbox=dict(boxstyle="round,pad=0.25", fc="#ffe3e0", ec="#d90429", lw=0.8))

    # Horizontal Diameters
    ax.annotate('', xy=(-2.0, 6.4), xytext=(2.0, 6.4),
                arrowprops=dict(arrowstyle='<->', color='#212529', lw=1.0))
    ax.text(0, 6.5, "Screw Head Ø 4.0mm", ha='center', va='bottom', fontsize=8, color='#212529', fontweight='bold')

    ax.annotate('', xy=(-2.3, -5.4), xytext=(2.3, -5.4),
                arrowprops=dict(arrowstyle='<->', color='#d90429', lw=1.0))
    ax.text(0, -5.6, "Counterbore Ø 4.60mm", ha='center', va='top', fontsize=8, color='#d90429', fontweight='bold')

    ax.set_title("Trackball Cup 4-Hole Fastening Architecture (5.50mm Stepped Ear & Sensor PCB Sandwich)", fontsize=13, fontweight='bold', pad=15)
    ax.axis('off')

    plt.tight_layout()
    out_file = ASSETS_DIR / "trackball_cup_fastening_diagram.png"
    plt.savefig(out_file, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_file}")

def generate_trackball_cup_detail_drawing():
    """
    Generate comprehensive engineering drawing of the trackball cup:
    - Left Panel: Front / Side Cross-Section (X-Z View) with Mounting Ears (Z=0 to 2.4mm, hole Ø3.6mm),
                  Ball (Ø25mm, center Z=18.30), Claws (Z=22.80), Bearings (Z=7.66), and Lens Pocket (Z=3.40).
    - Middle Panel: Top Plan View (X-Y View) with all 4 Mounting Ears (NE, NW, SW, SE at X=±12, Y=±11.3),
                    3 Claws (N 90°, E 0°, W 180°), South Open (270°), and 3 Bearings.
    - Right Panel: Side Elevation (Y-Z View) showing North Claw (Z=22.80) vs South Open Low Rim (Z<=12.0)
                   and South/North Mounting Ears (Y=±11.3).
    """
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(22, 10.5), dpi=200)
    fig.patch.set_facecolor('#ffffff')

    # =========================================================================
    # PANEL 1: X-Z Cross Section & Front View (側面断面図 / 正面図)
    # =========================================================================
    ax1.set_facecolor('#fcfcfc')
    ax1.set_xlim(-26, 26)
    ax1.set_ylim(-6, 36)
    ax1.set_aspect('equal')

    # Center axis
    ax1.plot([0, 0], [-5, 35], linestyle='-.', color='#888888', lw=1.0)
    ax1.text(0, 35.2, "CL (X=0)", ha='center', va='bottom', fontsize=8, color='#666666')

    # Main PCB at Z = -1.6 to 0.0
    pcb_xz = patches.Rectangle((-24, -1.6), 48, 1.6, linewidth=1.2, edgecolor='#1b4332', facecolor='#52b788', alpha=0.75, zorder=2)
    ax1.add_patch(pcb_xz)
    ax1.text(-19, -0.8, "Sensor PCB (1.6mm)", ha='center', va='center', fontsize=8, fontweight='bold', color='#ffffff', zorder=3)

    # 4 Mounting Ears: X-Z cross section shows Left Ear (X=-12, R=3.0) and Right Ear (X=+12, R=3.0), Height 5.50mm
    # Stepped hole: lower Z in [0, 3.9] is Ø 3.30 mm (±1.65), upper Z in [3.9, 5.5] is Ø 2.40 mm (±1.20)
    for ex_c in (-12.0, 12.0):
        ear_body = patches.Rectangle((ex_c - 3.0, 0.0), 6.0, 5.50, linewidth=1.2, edgecolor='#1d3557', facecolor='#457b9d', zorder=4)
        ear_h_low = patches.Rectangle((ex_c - 1.65, 0.0), 3.30, 3.90, linewidth=1.0, edgecolor='#d90429', facecolor='#ffffff', linestyle='--', zorder=4)
        ear_h_top = patches.Rectangle((ex_c - 1.20, 3.90), 2.40, 1.60, linewidth=1.0, edgecolor='#d90429', facecolor='#ffffff', linestyle='--', zorder=4)
        ax1.add_patch(ear_body)
        ax1.add_patch(ear_h_low)
        ax1.add_patch(ear_h_top)

    # Cup Body Profile (X-Z): Flush R=14.0mm cylindrical outer wall up to claw tip Z=22.80
    cup_wall_left = patches.Polygon([
        (-14.0, 0.0), (-14.0, 20.5), (-12.5, 22.8), (-11.2, 22.8),
        (-11.5, 20.5), (-12.0, 14.0), (-8.0, 5.8), (-5.5, 5.8), (-5.5, 3.4), (-10.5, 3.4), (-10.5, 0.0)
    ], closed=True, edgecolor='#1d3557', facecolor='#a8dadc', alpha=0.85, lw=1.5, zorder=3)
    ax1.add_patch(cup_wall_left)

    cup_wall_right = patches.Polygon([
        (14.0, 0.0), (14.0, 20.5), (12.5, 22.8), (11.2, 22.8),
        (11.5, 20.5), (12.0, 14.0), (8.0, 5.8), (5.5, 5.8), (5.5, 3.4), (10.5, 3.4), (10.5, 0.0)
    ], closed=True, edgecolor='#1d3557', facecolor='#a8dadc', alpha=0.85, lw=1.5, zorder=3)
    ax1.add_patch(cup_wall_right)

    # Claws highlight (West 180° and East 0°, flush outer R=14.0mm)
    claw_w = patches.Polygon([(-14.0, 14.0), (-14.0, 20.5), (-12.5, 22.8), (-11.2, 22.8), (-11.5, 20.5), (-12.0, 14.0)],
                             closed=True, edgecolor='#03045e', facecolor='#1d3557', zorder=5)
    claw_e = patches.Polygon([(14.0, 14.0), (14.0, 20.5), (12.5, 22.8), (11.2, 22.8), (11.5, 20.5), (12.0, 14.0)],
                             closed=True, edgecolor='#03045e', facecolor='#1d3557', zorder=5)
    ax1.add_patch(claw_w)
    ax1.add_patch(claw_e)
    ax1.text(-13.0, 23.5, "West Claw (180°)\nTip Z=+22.80", ha='center', va='bottom', fontsize=8, fontweight='bold', color='#1d3557')
    ax1.text(13.0, 23.5, "East Claw (0°)\nTip Z=+22.80", ha='center', va='bottom', fontsize=8, fontweight='bold', color='#1d3557')

    # LM19 Lens body in pocket
    lens_rect = patches.Rectangle((-9.0, 0.0), 18.0, 3.4, linewidth=1.2, edgecolor='#e76f51', facecolor='#f4a261', alpha=0.9, zorder=3)
    ax1.add_patch(lens_rect)
    ax1.text(0, 1.7, "LM19 Lens (Flange Z=+3.40mm)", ha='center', va='center', fontsize=7.0, fontweight='bold', color='#ffffff', zorder=4)

    # 25mm Trackball Sphere
    ball_xz = patches.Circle((0, 18.30), 12.50, linewidth=1.5, edgecolor='#0077b6', facecolor='#caf0f8', alpha=0.45, zorder=4)
    ax1.add_patch(ball_xz)
    # Ball center mark
    ax1.plot([0], [18.30], marker='+', markersize=10, color='#03045e', mew=1.5, zorder=5)
    ax1.text(0.5, 18.5, "Ball Center\nZ = +18.30 mm", ha='left', va='bottom', fontsize=8.5, fontweight='bold', color='#03045e')

    # Equator line
    ax1.plot([-13, 13], [18.30, 18.30], linestyle=':', color='#0077b6', lw=1.2, zorder=4)

    # Ceramic Bearings at Z = 7.66
    brg_l = patches.Circle((-7.20, 7.66), 1.0, linewidth=1.2, edgecolor='#6a040f', facecolor='#d90429', zorder=6)
    brg_r = patches.Circle((7.20, 7.66), 1.0, linewidth=1.2, edgecolor='#6a040f', facecolor='#d90429', zorder=6)
    ax1.add_patch(brg_l)
    ax1.add_patch(brg_r)
    ax1.text(4.2, 8.8, "Ø2.0mm Bearing\n(Z=+7.66mm)", ha='center', va='bottom', fontsize=7.0, fontweight='bold', color='#d90429', zorder=7)

    # Dimensions on Left/Right (Vertical Stackup - staggered Y so text boxes never overlap)
    def dim_v(z1, z2, label, x, col='#2b2d42', fs=7.5, y_text=None):
        ax1.annotate('', xy=(x, z1), xytext=(x, z2),
                     arrowprops=dict(arrowstyle='<->', color=col, lw=1.0))
        ty = (z1 + z2) / 2 if y_text is None else y_text
        ha = 'right' if x < 0 else 'left'
        dx_t = -0.4 if x < 0 else 0.4
        ax1.text(x + dx_t, ty, label, ha=ha, va='center', fontsize=fs, fontweight='bold', color=col,
                 bbox=dict(boxstyle="round,pad=0.15", fc="#ffffff", ec=col, lw=0.6, alpha=0.95))

    dim_v(3.4, 0.0, "Lens: 3.40mm", -15.8, '#e76f51', 7.5, y_text=1.5)
    dim_v(5.5, 0.0, "Ear: 5.50mm", -16.8, '#1d3557', 7.5, y_text=4.8)
    dim_v(18.30, 0.0, "Center: 18.30mm", -17.8, '#03045e', 7.5, y_text=15.0)
    dim_v(5.8, 0.0, "Ball Bot: 5.80mm", 15.8, '#0077b6', 7.5, y_text=2.9)
    dim_v(22.80, 18.30, "Claw Tip:\n+4.50mm", 15.8, '#1d3557', 7.5, y_text=20.5)
    dim_v(30.80, 0.0, "Ball Top:\n30.80mm", 17.5, '#0077b6', 7.5, y_text=28.5)

    # Horizontal Ear pitch dimension
    ax1.annotate('', xy=(-12.0, -3.2), xytext=(12.0, -3.2),
                 arrowprops=dict(arrowstyle='<->', color='#1d3557', lw=1.2))
    ax1.text(0, -3.6, "Ear Pitch X: 24.00 mm", ha='center', va='top', fontsize=8.5, fontweight='bold', color='#1d3557')

    # Ear Hole dimension callout
    ax1.annotate('Stepped Ear (Height: 5.50 mm)\nUpper 1.6mm: Ø2.4mm / Lower 3.9mm: Ø3.3mm',
                 xy=(-12.0, 5.5), xytext=(-25.2, 9.5),
                 arrowprops=dict(facecolor='#1d3557', shrink=0.05, width=1.0, headwidth=4),
                 fontsize=7.5, fontweight='bold', color='#1d3557',
                 bbox=dict(boxstyle="round,pad=0.2", fc="#e0f2fe", ec="#1d3557", lw=0.8))

    ax1.set_title("1. Trackball Cup Cross-Section (X-Z View)\n[側面断面・正面図: 西/東爪・耳厚み・光学系]", fontsize=11, fontweight='bold', pad=12)
    ax1.axis('off')

    # =========================================================================
    # PANEL 2: X-Y Top Plan View (天井からの平面図)
    # =========================================================================
    ax2.set_facecolor('#fcfcfc')
    ax2.set_xlim(-28, 28)
    ax2.set_ylim(-28, 28)
    ax2.set_aspect('equal')

    # Centerlines
    ax2.plot([0, 0], [-27, 27], linestyle='-.', color='#888888', lw=1.0)
    ax2.plot([-27, 27], [0, 0], linestyle='-.', color='#888888', lw=1.0)
    ax2.text(0, 27.2, "CL-Y (North 90°)", ha='center', va='bottom', fontsize=8, color='#666666', fontweight='bold')
    ax2.text(27.2, 0, "CL-X (East 0°)", ha='left', va='center', fontsize=8, color='#666666', fontweight='bold')

    # 4 Mounting Ears at NE (+12, +11.3), NW (-12, +11.3), SW (-12, -11.3), SE (+12, -11.3)
    ear_coords = [
        (12.0, 11.3, "NE (#1)"),
        (-12.0, 11.3, "NW (#2)"),
        (-12.0, -11.3, "SW (#3)"),
        (12.0, -11.3, "SE (#4)")
    ]

    for ex, ey, elab in ear_coords:
        boss = patches.Circle((ex, ey), 3.00, linewidth=1.5, edgecolor='#1d3557', facecolor='#457b9d', zorder=2)
        ax2.add_patch(boss)
        ang = np.arctan2(ey, ex)
        dx = 3.00 * np.sin(ang)
        dy = -3.00 * np.cos(ang)
        p_ear = [(ex + dx, ey + dy), (ex - dx, ey - dy),
                 (13.5 * np.cos(ang - 0.25), 13.5 * np.sin(ang - 0.25)),
                 (13.5 * np.cos(ang + 0.25), 13.5 * np.sin(ang + 0.25))]
        bridge = patches.Polygon(p_ear, closed=True, edgecolor='#1d3557', facecolor='#457b9d', zorder=1)
        ax2.add_patch(bridge)

        seat = patches.Circle((ex, ey), 1.65, linewidth=1.0, edgecolor='#adb5bd', facecolor='#6c757d', linestyle=':', zorder=3)
        ax2.add_patch(seat)
        hole = patches.Circle((ex, ey), 1.20, linewidth=1.2, edgecolor='#d90429', facecolor='#ffffff', zorder=4)
        ax2.add_patch(hole)
        ha_align = 'left' if ex > 0 else 'right'
        va_align = 'bottom' if ey > 0 else 'top'
        ax2.text(ex + (1.6 if ex > 0 else -1.6), ey + (1.6 if ey > 0 else -1.6),
                 f"{elab}\n({ex:+.1f}, {ey:+.1f})", ha=ha_align, va=va_align, fontsize=7.5, fontweight='bold', color='#1d3557',
                 bbox=dict(boxstyle="round,pad=0.15", fc="#ffffff", ec="#1d3557", lw=0.6, alpha=0.9))

    # Main Cup Outer Cylinder Ø28.0mm (R=14.0mm)
    cup_out = patches.Circle((0, 0), 14.0, linewidth=2.0, edgecolor='#1d3557', facecolor='#a8dadc', alpha=0.55, zorder=5)
    ax2.add_patch(cup_out)

    # Cup Inner Bowl Rim Ø25.7mm (R=12.85mm)
    cup_in = patches.Circle((0, 0), 12.85, linewidth=1.5, edgecolor='#0077b6', facecolor='#e0f2fe', alpha=0.7, zorder=6)
    ax2.add_patch(cup_in)

    # Ball Equator Profile Ø25.0mm (R=12.50mm)
    ball_top = patches.Circle((0, 0), 12.50, linewidth=1.5, edgecolor='#023e8a', facecolor='#caf0f8', alpha=0.5, linestyle='--', zorder=7)
    ax2.add_patch(ball_top)
    ax2.text(0, 0, "Ø25.0 mm Trackball\nNavigation Center", ha='center', va='center', fontsize=8, fontweight='bold', color='#03045e', zorder=8)

    # Optical Peephole at Bottom (11 x 8 mm)
    peep = patches.Rectangle((-5.5, -4.0), 11.0, 8.0, linewidth=1.2, edgecolor='#e76f51', facecolor='#fcbf49', alpha=0.85, zorder=7)
    ax2.add_patch(peep)

    # 3 Retention Claws (Cylindrical outer back face R=14.0mm, smooth spherical inner wrap: N 90°, E 0°, W 180°)
    claw_n = patches.Rectangle((-2.25, 11.6), 4.5, 2.4, linewidth=1.5, edgecolor='#03045e', facecolor='#1d3557', zorder=9)
    ax2.add_patch(claw_n)
    ax2.text(0, 14.5, "North Claw (90°)\n[Width: 4.50mm]", ha='center', va='bottom', fontsize=8, fontweight='bold', color='#03045e')

    claw_e_top = patches.Rectangle((11.6, -2.25), 2.4, 4.5, linewidth=1.5, edgecolor='#03045e', facecolor='#1d3557', zorder=9)
    ax2.add_patch(claw_e_top)
    ax2.text(14.6, 0, "East Claw\n(0° / 360°)", ha='left', va='center', fontsize=8, fontweight='bold', color='#03045e')

    claw_w_top = patches.Rectangle((-14.0, -2.25), 2.4, 4.5, linewidth=1.5, edgecolor='#03045e', facecolor='#1d3557', zorder=9)
    ax2.add_patch(claw_w_top)
    ax2.text(-14.6, 0, "West Claw\n(180°)", ha='right', va='center', fontsize=8, fontweight='bold', color='#03045e')

    # South side (270°): No claw needed, cup body naturally sits below equator all around
    ax2.annotate('South (270°): Claw-Free (爪なし)\n• Cup body rim is below equator all around\n• Ball is naturally accessible (低リム不要・全周均一)',
                 xy=(0, -14.0), xytext=(0, -21.0),
                 arrowprops=dict(facecolor='#1d3557', shrink=0.05, width=1.0, headwidth=4),
                 fontsize=8, fontweight='bold', color='#1d3557', ha='center',
                 bbox=dict(boxstyle="round,pad=0.25", fc="#f1faee", ec="#1d3557", lw=0.8), zorder=10)

    # 3 Ceramic Bearing Balls (30°, 150°, 270°) at R = 8.31mm
    brg_coords = [(7.20, 4.16, "#1 (30°)"), (-7.20, 4.16, "#2 (150°)"), (0.00, -8.31, "#3 (270°)")]
    orbit_c = patches.Circle((0, 0), 8.31, linewidth=0.8, edgecolor='#b7094c', facecolor='none', linestyle=':', zorder=8)
    ax2.add_patch(orbit_c)
    for bx, by, blab in brg_coords:
        b_dot = patches.Circle((bx, by), 1.0, linewidth=1.2, edgecolor='#6a040f', facecolor='#d90429', zorder=10)
        ax2.add_patch(b_dot)
        ax2.text(bx + (1.2 if bx >= 0 else -1.2), by + (1.0 if by > -5 else -1.5),
                 f"Brg {blab}", ha='left' if bx >= 0 else 'right', va='center', fontsize=7.5, fontweight='bold', color='#9d0208',
                 bbox=dict(boxstyle="round,pad=0.15", fc="#ffffff", ec="#9d0208", lw=0.6, alpha=0.9), zorder=11)

    # Pitch Dimensions placed with ample margin to prevent overlap
    ax2.annotate('', xy=(-12.0, 21.0), xytext=(12.0, 21.0),
                 arrowprops=dict(arrowstyle='<->', color='#1d3557', lw=1.2))
    ax2.text(0, 21.6, "Pitch X: 24.00 mm", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#1d3557',
             bbox=dict(boxstyle="round,pad=0.15", fc="#ffffff", ec="#1d3557", lw=0.6))

    ax2.annotate('', xy=(23.5, -11.3), xytext=(23.5, 11.3),
                 arrowprops=dict(arrowstyle='<->', color='#1d3557', lw=1.2))
    ax2.text(24.2, 0, "Pitch Y:\n22.60 mm", ha='left', va='center', fontsize=8.5, fontweight='bold', color='#1d3557',
             bbox=dict(boxstyle="round,pad=0.15", fc="#ffffff", ec="#1d3557", lw=0.6))

    ax2.set_title("2. Trackball Cup Top Plan View (X-Y View)\n[天井からの平面図: 4耳・3保持爪・南側爪なし・3支玉]", fontsize=11, fontweight='bold', pad=12)
    ax2.axis('off')

    # =========================================================================
    # PANEL 3: Y-Z Side Elevation View (South to North / 側面立面図)
    # =========================================================================
    ax3.set_facecolor('#fcfcfc')
    ax3.set_xlim(-26, 26)
    ax3.set_ylim(-6, 36)
    ax3.set_aspect('equal')

    # Center axis
    ax3.plot([0, 0], [-5, 35], linestyle='-.', color='#888888', lw=1.0)
    ax3.text(0, 35.2, "CL (Y=0)", ha='center', va='bottom', fontsize=8, color='#666666')

    # PCB at Z = -1.6 to 0.0
    pcb_yz = patches.Rectangle((-24, -1.6), 48, 1.6, linewidth=1.2, edgecolor='#1b4332', facecolor='#52b788', alpha=0.75, zorder=2)
    ax3.add_patch(pcb_yz)
    ax3.text(0, -0.8, "Sensor PCB (1.6mm)", ha='center', va='center', fontsize=8, fontweight='bold', color='#ffffff', zorder=3)

    # South Ear (Y = -11.3, R = 3.0) and North Ear (Y = +11.3, R = 3.0), Height 5.50mm stepped hole
    for ey_c in (-11.3, 11.3):
        ear_b = patches.Rectangle((ey_c - 3.0, 0.0), 6.0, 5.50, linewidth=1.2, edgecolor='#1d3557', facecolor='#457b9d', zorder=4)
        ear_hl = patches.Rectangle((ey_c - 1.65, 0.0), 3.30, 3.90, linewidth=1.0, edgecolor='#d90429', facecolor='#ffffff', linestyle='--', zorder=5)
        ear_ht = patches.Rectangle((ey_c - 1.20, 3.90), 2.40, 1.60, linewidth=1.0, edgecolor='#d90429', facecolor='#ffffff', linestyle='--', zorder=5)
        ax3.add_patch(ear_b)
        ax3.add_patch(ear_hl)
        ax3.add_patch(ear_ht)

    # Cup Body Profile in Y-Z:
    # Cup body has UNIFORM rim height Z = 14.0 mm all around (below Equator Z = 18.30 mm)
    # North side (+Y) has North Claw rising from Z = 14.0 to Z = 22.80 mm with flush outer R = 14.0 mm
    # South side (-Y) stops cleanly at Z = 14.0 mm (No claw!)
    cup_yz_poly = patches.Polygon([
        # South uniform rim (Z = 14.0)
        (-14.0, 0.0), (-14.0, 14.0), (-11.8, 14.0),
        # Inner bowl profile
        (-8.0, 5.8), (-5.5, 3.4), (5.5, 3.4), (8.0, 5.8),
        # North side: uniform rim at 14.0, then claw rises to 22.80 with flush outer R = 14.0
        (11.8, 14.0), (11.5, 20.5), (11.2, 22.8), (12.5, 22.8), (14.0, 20.5), (14.0, 14.0), (14.0, 0.0)
    ], closed=True, edgecolor='#1d3557', facecolor='#a8dadc', alpha=0.85, lw=1.5, zorder=3)
    ax3.add_patch(cup_yz_poly)

    # Uniform rim dashed indicator across cup
    ax3.plot([-14.0, 14.0], [14.0, 14.0], linestyle=':', color='#1d3557', lw=1.0, zorder=4)

    # North Claw highlight
    claw_n_yz = patches.Polygon([(11.5, 20.5), (11.2, 22.8), (12.5, 22.8), (14.0, 20.5), (14.0, 14.0), (11.8, 14.0)],
                                closed=True, edgecolor='#03045e', facecolor='#1d3557', zorder=5)
    ax3.add_patch(claw_n_yz)
    ax3.text(13.0, 23.5, "North Claw (90°)\nTip Z=+22.80mm", ha='center', va='bottom', fontsize=8, fontweight='bold', color='#03045e')

    # Ball in Y-Z
    ball_yz = patches.Circle((0, 18.30), 12.50, linewidth=1.5, edgecolor='#0077b6', facecolor='#caf0f8', alpha=0.45, zorder=4)
    ax3.add_patch(ball_yz)
    ax3.plot([0], [18.30], marker='+', markersize=10, color='#03045e', mew=1.5, zorder=5)

    # Equator line in Y-Z
    ax3.plot([-13, 13], [18.30, 18.30], linestyle=':', color='#0077b6', lw=1.2, zorder=4)

    # South Claw-Free callout
    ax3.annotate('South Side (270°): No Claw (爪なし)\n• Uniform rim height: Z = +14.00 mm\n• Entire cup is below Equator (Z = +18.30 mm)\n• Low-rim cutout NOT needed (低リム不要)',
                 xy=(-13.0, 14.0), xytext=(-24.5, 20.0),
                 arrowprops=dict(facecolor='#1d3557', shrink=0.05, width=1.0, headwidth=4),
                 fontsize=7.5, fontweight='bold', color='#1d3557',
                 bbox=dict(boxstyle="round,pad=0.25", fc="#e0f2fe", ec="#1d3557", lw=0.8), zorder=10)

    # Rim height dimension on Y-Z
    ax3.annotate('', xy=(-17.0, 14.0), xytext=(-17.0, 0.0),
                 arrowprops=dict(arrowstyle='<->', color='#1d3557', lw=1.0))
    ax3.text(-17.4, 7.0, "Uniform Rim:\n14.00 mm", ha='right', va='center', fontsize=7.5, fontweight='bold', color='#1d3557',
             bbox=dict(boxstyle="round,pad=0.15", fc="#ffffff", ec="#1d3557", lw=0.6, alpha=0.9))

    # Y Pitch Dimension at bottom
    ax3.annotate('', xy=(-11.3, -3.2), xytext=(11.3, -3.2),
                 arrowprops=dict(arrowstyle='<->', color='#1d3557', lw=1.2))
    ax3.text(0, -3.6, "Ear Pitch Y: 22.60 mm", ha='center', va='top', fontsize=8.5, fontweight='bold', color='#1d3557')

    ax3.text(-11.3, 6.0, "South Ear\n(5.5mm)", ha='center', va='bottom', fontsize=7.0, fontweight='bold', color='#1d3557')
    ax3.text(11.3, 6.0, "North Ear\n(5.5mm)", ha='center', va='bottom', fontsize=7.0, fontweight='bold', color='#1d3557')

    ax3.set_title("3. Longitudinal Elevation (Y-Z View)\n[側面立面図: 南側爪なし vs 北側保持爪]", fontsize=11, fontweight='bold', pad=12)
    ax3.axis('off')

    plt.tight_layout()
    out_file = ASSETS_DIR / "trackball_cup_detail_drawing.png"
    plt.savefig(out_file, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_file}")

if __name__ == "__main__":
    generate_vertical_stackup_diagram()
    generate_ports_and_screws_diagram()
    generate_trackball_optical_diagram()
    generate_trackball_cup_fastening_diagram()
    generate_trackball_cup_detail_drawing()
    print("All specification diagram images updated successfully!")


