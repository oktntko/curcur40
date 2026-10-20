# -*- coding: utf-8 -*-
"""
Generate engineering specification diagrams for curcur40 case documentation.
Outputs high-resolution diagrams to docs/curcur40/assets/
"""
from pathlib import Path
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

ASSETS_DIR = Path(r"c:\Users\oktnt\workspace\curcur40\docs\curcur40\assets")
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams['font.sans-serif'] = ['Meiryo', 'Yu Gothic', 'MS Gothic', 'DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.unicode_minus'] = False
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
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=200)
    ax.set_xlim(-26, 26)
    ax.set_ylim(-16, 24)
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#ffffff')

    # Ø 25.0 mm Trackball Sphere (Radius = 12.50 mm)
    # Ball center at (0, 8.0), bottom of ball at Z = 8.0 - 12.5 = -4.5 mm
    ball_center = (0, 8.0)
    ball = patches.Circle(ball_center, 12.50, linewidth=1.5, edgecolor='#0077b6', facecolor='#90e0ef', alpha=0.35)
    ax.add_patch(ball)
    ax.text(0, 8.0, "Ø 25 mm Trackball Sphere\n(Radius = 12.50 mm)", ha='center', va='center', fontsize=11, fontweight='bold', color='#03045e')

    # Cup profile (U-shaped arc for 25mm ball)
    cup_outline = patches.Arc(ball_center, 29.0, 29.0, theta1=205, theta2=335, linewidth=3, color='#023e8a')
    ax.add_patch(cup_outline)
    ax.text(-18, 5.0, "Trackball Cup Body\n(Claws: N 90°, E 0°, W 180°)", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#023e8a')

    # LM19-LSI Optical Lens (sits on F.Cu at Z in [-0.53, 0.0] or above PCB)
    # Flange: 21.15 x 18.85 mm, Flange thickness 0.53mm
    lens_flange = patches.Rectangle((-10.5, 0.0), 21.0, 1.4, linewidth=1.5, edgecolor='#f77f00', facecolor='#fcbf49', alpha=0.85)
    ax.add_patch(lens_flange)
    ax.text(0, 0.7, "LM19 Optical Lens Flange (F.Cu side)", ha='center', va='center', fontsize=9, fontweight='bold', color='#7f4f24')

    # 4 Lens Positioning Legs extending DOWN through PCB cutout
    # 2 round pins (dia 0.9mm) + 2 rectangular ribs
    leg_left = patches.Rectangle((-4.5, -3.35), 1.2, 3.35, linewidth=1.2, edgecolor='#d48b00', facecolor='#ffb703')
    leg_right = patches.Rectangle((3.3, -3.35), 1.2, 3.35, linewidth=1.2, edgecolor='#d48b00', facecolor='#ffb703')
    ax.add_patch(leg_left)
    ax.add_patch(leg_right)
    ax.annotate('4 Lens Legs extend DOWN\nthrough PCB cutout into IC pockets',
                xy=(4.5, -2.5), xytext=(12, -0.5),
                arrowprops=dict(facecolor='#d48b00', shrink=0.05, width=1, headwidth=4),
                fontsize=8, fontweight='bold', color='#d48b00',
                bbox=dict(boxstyle="round,pad=0.2", fc="#fff3cd", ec="#d48b00", lw=0.8))

    # PCB (FR-4, thickness 1.6mm: Z from -1.6 to 0.0)
    pcb_left = patches.Rectangle((-24, -1.6), 15.25, 1.6, linewidth=1.5, edgecolor='#2d6a4f', facecolor='#52b788', alpha=0.85)
    pcb_right = patches.Rectangle((8.75, -1.6), 15.25, 1.6, linewidth=1.5, edgecolor='#2d6a4f', facecolor='#52b788', alpha=0.85)
    ax.add_patch(pcb_left)
    ax.add_patch(pcb_right)
    ax.text(-16, -0.8, "Main PCB (1.6mm)", ha='center', va='center', fontsize=9, fontweight='bold', color='#ffffff')
    ax.text(16, -0.8, "Main PCB (1.6mm)", ha='center', va='center', fontsize=9, fontweight='bold', color='#ffffff')
    ax.text(0, -0.8, "PCB Cutout (16.9 x 8.7 mm)\n(Lens legs & light pass through)", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#1b4332')

    # PMW3360DM-T2QU Sensor Package (Mounted on B.Cu, Z from -4.01 to -1.60)
    # Solid package (NO holes in IC!)
    pmw_body = patches.Rectangle((-8.1, -4.01), 16.2, 2.41, linewidth=1.5, edgecolor='#14213d', facecolor='#2b2d42', alpha=0.95)
    ax.add_patch(pmw_body)
    ax.text(0, -3.0, "PMW3360 IC Solid Body (2.41mm)\n[NO THROUGH-HOLE IN SENSOR]", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#ffffff')

    # 16 Sensor Metal Pins emerging from IC sides and extending UP through PCB
    # Left pins
    ax.plot([-8.1, -9.2, -9.2], [-2.3, -2.3, 0.6], color='#ffd166', lw=2.5)
    # Right pins
    ax.plot([8.1, 9.2, 9.2], [-2.3, -2.3, 0.6], color='#ffd166', lw=2.5)
    ax.annotate('16 Pins emerge from IC sides,\nextend UP through PCB to F.Cu',
                xy=(-9.2, 0.2), xytext=(-23, 2.0),
                arrowprops=dict(facecolor='#cca000', shrink=0.05, width=1, headwidth=4),
                fontsize=8, fontweight='bold', color='#cca000',
                bbox=dict(boxstyle="round,pad=0.2", fc="#fff9db", ec="#cca000", lw=0.8))

    # Flat Case Interior Floor (Z = -7.21 or -8.4 mm)
    floor = patches.Rectangle((-24, -9.0), 48, 2.6, linewidth=2, edgecolor='#495057', facecolor='#ced4da', alpha=0.7)
    ax.add_patch(floor)
    ax.text(0, -7.7, "Flat Case Interior Floor\n(Zero Through-Hole or Sensor Pocket Needed!)", ha='center', va='center', fontsize=10, fontweight='bold', color='#212529')

    # Clearance arrow
    ax.annotate('', xy=(12, -4.01), xytext=(12, -6.4),
                arrowprops=dict(arrowstyle='<->', color='#d90429', lw=1.8))
    ax.text(13.5, -5.2, "Clearance: > 1.5mm\n(Completely safe)", ha='left', va='center', fontsize=9, fontweight='bold', color='#d90429')

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
    ax.set_ylim(-10, 5.5)
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#ffffff')

    # Center axis (X = 0)
    ax.plot([0, 0], [-9.5, 4.5], linestyle='-.', color='#888888', lw=1.2, zorder=1)
    ax.text(0, 4.7, "Center Line (CL)", ha='center', va='bottom', fontsize=9, color='#666666', fontweight='bold')

    # -------------------------------------------------------------
    # Layer 4: Case Floor (Z = -8.2 to -5.0, Total thickness 3.2 mm)
    # -------------------------------------------------------------
    # Left solid floor
    floor_left = patches.Rectangle((-14, -8.2), 11.7, 3.2, linewidth=1.5, edgecolor='#343a40', facecolor='#adb5bd', alpha=0.9, zorder=2)
    # Right solid floor
    floor_right = patches.Rectangle((2.3, -8.2), 11.7, 3.2, linewidth=1.5, edgecolor='#343a40', facecolor='#adb5bd', alpha=0.9, zorder=2)
    # Solid floor shelf above counterbore (from X=-2.3 to -1.2, and 1.2 to 2.3, Z = -7.0 to -5.0)
    shelf_l = patches.Rectangle((-2.3, -7.0), 1.1, 2.0, linewidth=1.5, edgecolor='#343a40', facecolor='#adb5bd', alpha=0.9, zorder=2)
    shelf_r = patches.Rectangle((1.2, -7.0), 1.1, 2.0, linewidth=1.5, edgecolor='#343a40', facecolor='#adb5bd', alpha=0.9, zorder=2)
    ax.add_patch(floor_left)
    ax.add_patch(floor_right)
    ax.add_patch(shelf_l)
    ax.add_patch(shelf_r)

    # -------------------------------------------------------------
    # Layer 2: Main PCB (Z = -1.6 to 0.0, Thickness 1.6 mm)
    # -------------------------------------------------------------
    # Through-hole for spacer: X = -1.9 to +1.9 (Ø 3.8 mm)
    pcb_left = patches.Rectangle((-14, -1.6), 12.1, 1.6, linewidth=1.5, edgecolor='#1b4332', facecolor='#52b788', alpha=0.9, zorder=2)
    pcb_right = patches.Rectangle((1.9, -1.6), 12.1, 1.6, linewidth=1.5, edgecolor='#1b4332', facecolor='#52b788', alpha=0.9, zorder=2)
    ax.add_patch(pcb_left)
    ax.add_patch(pcb_right)

    # -------------------------------------------------------------
    # Layer 1: Cup Mounting Ear (Z = 0.0 to 2.4, Thickness 2.4 mm)
    # -------------------------------------------------------------
    # Hole in ear: X = -1.75 to +1.75 (Ø 3.5 mm)
    ear_left = patches.Rectangle((-9.0, 0.0), 7.25, 2.4, linewidth=1.5, edgecolor='#1d3557', facecolor='#457b9d', alpha=0.9, zorder=2)
    ear_right = patches.Rectangle((1.75, 0.0), 7.25, 2.4, linewidth=1.5, edgecolor='#1d3557', facecolor='#457b9d', alpha=0.9, zorder=2)
    ax.add_patch(ear_left)
    ax.add_patch(ear_right)

    # -------------------------------------------------------------
    # Spacer (M2 5.0 mm female-female standoff)
    # Spans from Case Floor (Z = -5.0) UP THROUGH PCB to Z = 0.0
    # Outer width: X = -1.7 to +1.7 (Ø 3.4 mm)
    # -------------------------------------------------------------
    spacer_body = patches.Rectangle((-1.7, -5.0), 3.4, 5.0, linewidth=1.8, edgecolor='#b08968', facecolor='#eddcd2', hatch='///', zorder=3)
    ax.add_patch(spacer_body)
    # Thread core visualization
    thread_core = patches.Rectangle((-1.0, -5.0), 2.0, 5.0, linewidth=1.0, edgecolor='#7f5539', facecolor='#ffffff', alpha=0.85, zorder=4)
    ax.add_patch(thread_core)

    # -------------------------------------------------------------
    # Top Screw: M2 x 4mm (Head Ø 4.0, Shaft Ø 2.0 x 4.0mm)
    # Head rests at Z = 2.4 (top of ear), shaft reaches Z = -1.6 (bottom of PCB)
    # -------------------------------------------------------------
    top_head = patches.Rectangle((-2.0, 2.4), 4.0, 0.8, linewidth=1.5, edgecolor='#212529', facecolor='#6c757d', zorder=5)
    top_shaft = patches.Rectangle((-1.0, -1.6), 2.0, 4.0, linewidth=1.5, edgecolor='#212529', facecolor='#495057', zorder=5)
    ax.add_patch(top_head)
    ax.add_patch(top_shaft)
    # Screw drive groove
    ax.plot([0, 0], [2.6, 3.2], color='#ffffff', lw=1.5, zorder=6)

    # -------------------------------------------------------------
    # Bottom Screw: M2 x 4mm (Head Ø 4.0, Shaft Ø 2.0 x 4.0mm)
    # Head rests at Z = -7.0 (recessed in counterbore), shaft reaches Z = -3.0
    # -------------------------------------------------------------
    bot_head = patches.Rectangle((-2.0, -7.8), 4.0, 0.8, linewidth=1.5, edgecolor='#212529', facecolor='#6c757d', zorder=5)
    bot_shaft = patches.Rectangle((-1.0, -7.0), 2.0, 4.0, linewidth=1.5, edgecolor='#212529', facecolor='#495057', zorder=5)
    ax.add_patch(bot_head)
    ax.add_patch(bot_shaft)
    # Screw drive groove
    ax.plot([0, 0], [-7.6, -7.0], color='#ffffff', lw=1.5, zorder=6)

    # -------------------------------------------------------------
    # Thread safety gap inside spacer (Z = -3.0 to -1.6, gap = 1.4 mm)
    # -------------------------------------------------------------
    ax.annotate('', xy=(0, -1.6), xytext=(0, -3.0),
                arrowprops=dict(arrowstyle='<->', color='#2b9348', lw=2.2), zorder=7)
    ax.text(0.3, -2.3, "1.4 mm\nSafety Gap", ha='left', va='center', fontsize=8.5, fontweight='bold', color='#2b9348',
            bbox=dict(boxstyle="round,pad=0.2", fc="#d8f3dc", ec="#2b9348", lw=0.8), zorder=7)

    # -------------------------------------------------------------
    # Left Dimensions: Layer-by-layer Stackup
    # -------------------------------------------------------------
    def dim_left(z1, z2, label, x=-11.5, color='#1d3557'):
        ax.annotate('', xy=(x, z1), xytext=(x, z2),
                    arrowprops=dict(arrowstyle='<->', color=color, lw=1.2))
        ax.text(x - 0.5, (z1 + z2) / 2, label, ha='right', va='center', fontsize=9, fontweight='bold', color=color)

    dim_left(2.4, 0.0, "1. Cup Ear:\n2.40 mm", -11.0, '#1d3557')
    dim_left(0.0, -1.6, "2. Main PCB:\n1.60 mm", -11.0, '#1b4332')
    dim_left(-1.6, -5.0, "3. Under-PCB Cavity:\n3.40 mm", -11.0, '#b08968')
    dim_left(-5.0, -7.0, "4a. Solid Floor:\n2.00 mm", -11.0, '#343a40')
    dim_left(-7.0, -8.2, "4b. Counterbore:\n1.20 mm", -11.0, '#d90429')

    # Total case floor thickness
    dim_left(-5.0, -8.2, "Case Floor\nTotal 3.20 mm", -14.5, '#212529')

    # -------------------------------------------------------------
    # Right Annotations: Detailed Explanations
    # -------------------------------------------------------------
    # 1. Top screw callout
    ax.annotate('Top M2 x 4mm Screw (Head Ø4.0 x 0.8mm)\n• Passes through Cup Ear (2.4mm)\n• Engages 1.6mm thread into Spacer (in PCB layer)',
                xy=(1.5, 2.0), xytext=(8.5, 2.8),
                arrowprops=dict(facecolor='#1d3557', shrink=0.05, width=1.2, headwidth=5),
                fontsize=8.5, fontweight='bold', color='#1d3557',
                bbox=dict(boxstyle="round,pad=0.3", fc="#e0f2fe", ec="#1d3557", lw=1))

    # 2. Cup Ear sizing & tolerance callout
    ax.annotate('Cup Ear Hole: Ø 3.50 mm (Counterbore/Clearance)\n• Allows Spacer (Ø3.4mm) alignment & slight shift\n• M2 Screw Head (Ø4.0mm) catches securely on top',
                xy=(4.5, 1.2), xytext=(8.5, 1.1),
                arrowprops=dict(facecolor='#457b9d', shrink=0.05, width=1, headwidth=4),
                fontsize=8, fontweight='bold', color='#1d3557',
                bbox=dict(boxstyle="round,pad=0.25", fc="#f1faee", ec="#457b9d", lw=0.8))

    # 3. PCB through-hole & spacer penetration callout
    ax.annotate('Main PCB Spacer Through-Hole: Ø 3.80 mm\n• Spacer completely PENETRATES through the PCB!\n• Top of Spacer reaches PCB top surface (Z = 0.0mm)',
                xy=(1.8, -0.8), xytext=(8.5, -0.6),
                arrowprops=dict(facecolor='#1b4332', shrink=0.05, width=1.2, headwidth=5),
                fontsize=8.5, fontweight='bold', color='#1b4332',
                bbox=dict(boxstyle="round,pad=0.3", fc="#d8f3dc", ec="#1b4332", lw=1))

    # 4. Spacer Length & Placement callout
    ax.annotate('M2 5.0 mm Female-Female Spacer\n• Spans Layer 2 (PCB 1.6mm) + Layer 3 (Cavity 3.4mm)\n• Total height: 1.6 + 3.4 = 5.00 mm\n• Sits directly on FLAT case floor (Z = -5.0mm)',
                xy=(1.8, -3.8), xytext=(8.5, -2.4),
                arrowprops=dict(facecolor='#b08968', shrink=0.05, width=1.2, headwidth=5),
                fontsize=8.5, fontweight='bold', color='#6b705c',
                bbox=dict(boxstyle="round,pad=0.3", fc="#faedcd", ec="#b08968", lw=1))

    # 5. Flat Case Interior Floor & NO BOSS callout
    ax.annotate('Flat Case Interior Floor (Z = -5.00 mm)\n• ★ ZERO CASE BOSSES NEEDED! (ボス不要・完全平坦)\n• Spacer stands firmly on the flat bottom floor',
                xy=(-3.5, -5.0), xytext=(8.5, -4.3),
                arrowprops=dict(facecolor='#d90429', shrink=0.05, width=1.4, headwidth=5),
                fontsize=9, fontweight='bold', color='#d90429',
                bbox=dict(boxstyle="round,pad=0.3", fc="#ffe3e0", ec="#d90429", lw=1.2))

    # 6. Bottom Screw & Counterbore callout
    ax.annotate('Bottom M2 x 4mm Screw & Counterbore\n• Counterbore: Ø 4.60 mm x Depth 1.20 mm\n• Solid floor thickness: 2.00 mm\n• Screw engages 2.00 mm thread into bottom of Spacer\n• Head recessed 0.4mm inside counterbore (flush with desk)',
                xy=(2.0, -7.4), xytext=(8.5, -6.8),
                arrowprops=dict(facecolor='#212529', shrink=0.05, width=1.2, headwidth=5),
                fontsize=8.5, fontweight='bold', color='#212529',
                bbox=dict(boxstyle="round,pad=0.3", fc="#e9ecef", ec="#495057", lw=1))

    # Horizontal Diameters
    # Screw head Ø4.0
    ax.annotate('', xy=(-2.0, 3.4), xytext=(2.0, 3.4),
                arrowprops=dict(arrowstyle='<->', color='#212529', lw=1.0))
    ax.text(0, 3.6, "Screw Head Ø 4.0mm", ha='center', va='bottom', fontsize=8, color='#212529', fontweight='bold')

    # Counterbore Ø4.6
    ax.annotate('', xy=(-2.3, -8.5), xytext=(2.3, -8.5),
                arrowprops=dict(arrowstyle='<->', color='#d90429', lw=1.0))
    ax.text(0, -8.7, "Counterbore Ø 4.60mm", ha='center', va='top', fontsize=8, color='#d90429', fontweight='bold')

    # Through hole Ø2.4
    ax.annotate('', xy=(-1.2, -7.0), xytext=(1.2, -7.0),
                arrowprops=dict(arrowstyle='<->', color='#495057', lw=0.9))

    ax.set_title("Trackball Cup 4-Hole Fastening Architecture (Through-PCB Spacer Stackup)", fontsize=13, fontweight='bold', pad=15)
    ax.axis('off')

    plt.tight_layout()
    out_file = ASSETS_DIR / "trackball_cup_fastening_diagram.png"
    plt.savefig(out_file, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_file}")

def generate_trackball_cup_detail_drawing():
    """
    Generate comprehensive engineering drawing of the trackball cup:
    - Left Panel: Front / Side Cross-Section (X-Z View) with Mounting Ears (Z=0 to 2.4mm, hole Ø3.5mm),
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
    ax1.text(-19, -0.8, "Main PCB (1.6mm)", ha='center', va='center', fontsize=8, fontweight='bold', color='#ffffff', zorder=3)

    # 4 Mounting Ears: X-Z cross section shows Left Ear (X=-12) and Right Ear (X=+12)
    # Left Ear: body X in [-15.25, -8.75], Z in [0, 2.4]
    ear_l_solid1 = patches.Rectangle((-15.25, 0.0), 1.50, 2.4, linewidth=1.2, edgecolor='#1d3557', facecolor='#457b9d', zorder=4)
    ear_l_solid2 = patches.Rectangle((-10.25, 0.0), 1.50, 2.4, linewidth=1.2, edgecolor='#1d3557', facecolor='#457b9d', zorder=4)
    ear_l_hole = patches.Rectangle((-13.75, 0.0), 3.50, 2.4, linewidth=1.0, edgecolor='#d90429', facecolor='#ffffff', linestyle='--', zorder=4)
    ax1.add_patch(ear_l_solid1)
    ax1.add_patch(ear_l_solid2)
    ax1.add_patch(ear_l_hole)

    # Right Ear: body X in [8.75, 15.25], Z in [0, 2.4]
    ear_r_solid1 = patches.Rectangle((8.75, 0.0), 1.50, 2.4, linewidth=1.2, edgecolor='#1d3557', facecolor='#457b9d', zorder=4)
    ear_r_solid2 = patches.Rectangle((13.75, 0.0), 1.50, 2.4, linewidth=1.2, edgecolor='#1d3557', facecolor='#457b9d', zorder=4)
    ear_r_hole = patches.Rectangle((10.25, 0.0), 3.50, 2.4, linewidth=1.0, edgecolor='#d90429', facecolor='#ffffff', linestyle='--', zorder=4)
    ax1.add_patch(ear_r_solid1)
    ax1.add_patch(ear_r_solid2)
    ax1.add_patch(ear_r_hole)

    # Cup Body Profile (X-Z)
    cup_wall_left = patches.Polygon([
        (-14.0, 0.0), (-14.0, 20.5), (-14.5, 20.5), (-12.5, 22.8), (-11.2, 22.8),
        (-11.5, 20.5), (-12.0, 14.0), (-8.0, 5.8), (-5.5, 5.8), (-5.5, 3.4), (-10.5, 3.4), (-10.5, 0.0)
    ], closed=True, edgecolor='#1d3557', facecolor='#a8dadc', alpha=0.85, lw=1.5, zorder=3)
    ax1.add_patch(cup_wall_left)

    cup_wall_right = patches.Polygon([
        (14.0, 0.0), (14.0, 20.5), (14.5, 20.5), (12.5, 22.8), (11.2, 22.8),
        (11.5, 20.5), (12.0, 14.0), (8.0, 5.8), (5.5, 5.8), (5.5, 3.4), (10.5, 3.4), (10.5, 0.0)
    ], closed=True, edgecolor='#1d3557', facecolor='#a8dadc', alpha=0.85, lw=1.5, zorder=3)
    ax1.add_patch(cup_wall_right)

    # Claws highlight (West 180° and East 0°)
    claw_w = patches.Polygon([(-14.5, 20.5), (-12.5, 22.8), (-11.2, 22.8), (-11.5, 20.5), (-14.0, 20.5)],
                             closed=True, edgecolor='#03045e', facecolor='#1d3557', zorder=5)
    claw_e = patches.Polygon([(14.5, 20.5), (12.5, 22.8), (11.2, 22.8), (11.5, 20.5), (14.0, 20.5)],
                             closed=True, edgecolor='#03045e', facecolor='#1d3557', zorder=5)
    ax1.add_patch(claw_w)
    ax1.add_patch(claw_e)
    ax1.text(-13.0, 23.5, "West Claw (180°)\nTip Z=+22.80", ha='center', va='bottom', fontsize=8, fontweight='bold', color='#1d3557')
    ax1.text(13.0, 23.5, "East Claw (0°)\nTip Z=+22.80", ha='center', va='bottom', fontsize=8, fontweight='bold', color='#1d3557')

    # LM19 Lens body in pocket
    lens_rect = patches.Rectangle((-10.5, 0.0), 21.0, 3.4, linewidth=1.2, edgecolor='#e76f51', facecolor='#f4a261', alpha=0.9, zorder=3)
    ax1.add_patch(lens_rect)
    ax1.text(0, 1.7, "LM19 Lens Body (Flange Z=+3.40mm)", ha='center', va='center', fontsize=8, fontweight='bold', color='#ffffff', zorder=4)

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
    ax1.text(7.5, 7.0, "Ø2.0mm Bearing\n(Z=+7.66mm)", ha='left', va='top', fontsize=7.5, fontweight='bold', color='#d90429')

    # Dimensions on Left (Vertical Stackup)
    def dim_v(z1, z2, label, x, col='#2b2d42', fs=8):
        ax1.annotate('', xy=(x, z1), xytext=(x, z2),
                     arrowprops=dict(arrowstyle='<->', color=col, lw=1.0))
        ax1.text(x - 0.4, (z1 + z2) / 2, label, ha='right', va='center', fontsize=fs, fontweight='bold', color=col,
                 bbox=dict(boxstyle="round,pad=0.15", fc="#ffffff", ec=col, lw=0.6, alpha=0.9))

    dim_v(2.4, 0.0, "Ear: 2.40mm", -16.0, '#1d3557', 7.5)
    dim_v(3.4, 0.0, "Lens: 3.40mm", -19.0, '#e76f51', 7.5)
    dim_v(5.8, 0.0, "PCB to Ball:\n5.80mm", -22.0, '#0077b6', 7.5)
    dim_v(18.30, 0.0, "Center: 18.30mm", -24.5, '#03045e', 7.5)
    dim_v(22.80, 18.30, "Claw Tip:\n+4.50mm", 16.5, '#1d3557', 7.5)
    dim_v(30.80, 0.0, "Ball Top:\n30.80mm", 20.5, '#0077b6', 7.5)

    # Horizontal Ear pitch dimension
    ax1.annotate('', xy=(-12.0, -3.2), xytext=(12.0, -3.2),
                 arrowprops=dict(arrowstyle='<->', color='#1d3557', lw=1.2))
    ax1.text(0, -3.6, "Ear Pitch X: 24.00 mm", ha='center', va='top', fontsize=8.5, fontweight='bold', color='#1d3557')

    # Ear Hole dimension callout
    ax1.annotate('Ear Hole: Ø 3.50 mm\n(Ear Thickness: 2.40 mm)',
                 xy=(-12.0, 1.2), xytext=(-22.0, 8.5),
                 arrowprops=dict(facecolor='#1d3557', shrink=0.05, width=1.0, headwidth=4),
                 fontsize=8, fontweight='bold', color='#1d3557',
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
        boss = patches.Circle((ex, ey), 3.25, linewidth=1.5, edgecolor='#1d3557', facecolor='#457b9d', zorder=2)
        ax2.add_patch(boss)
        ang = np.arctan2(ey, ex)
        dx = 3.25 * np.sin(ang)
        dy = -3.25 * np.cos(ang)
        p_ear = [(ex + dx, ey + dy), (ex - dx, ey - dy),
                 (13.5 * np.cos(ang - 0.25), 13.5 * np.sin(ang - 0.25)),
                 (13.5 * np.cos(ang + 0.25), 13.5 * np.sin(ang + 0.25))]
        bridge = patches.Polygon(p_ear, closed=True, edgecolor='#1d3557', facecolor='#457b9d', zorder=1)
        ax2.add_patch(bridge)

        seat = patches.Circle((ex, ey), 2.0, linewidth=1.0, edgecolor='#adb5bd', facecolor='#6c757d', linestyle=':', zorder=3)
        ax2.add_patch(seat)
        hole = patches.Circle((ex, ey), 1.75, linewidth=1.2, edgecolor='#d90429', facecolor='#ffffff', zorder=4)
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

    # 3 Retention Claws (T-shape orthogonal: N 90°, E 0°, W 180°)
    claw_n = patches.Rectangle((-2.25, 12.0), 4.5, 3.8, linewidth=1.5, edgecolor='#03045e', facecolor='#1d3557', zorder=9)
    lip_n = patches.Rectangle((-2.0, 11.3), 4.0, 0.8, linewidth=1.0, edgecolor='#03045e', facecolor='#023e8a', zorder=9)
    ax2.add_patch(claw_n)
    ax2.add_patch(lip_n)
    ax2.text(0, 16.2, "North Claw (90°)\n[Width: 4.50mm]", ha='center', va='bottom', fontsize=8, fontweight='bold', color='#03045e')

    claw_e_top = patches.Rectangle((12.0, -2.25), 3.8, 4.5, linewidth=1.5, edgecolor='#03045e', facecolor='#1d3557', zorder=9)
    lip_e = patches.Rectangle((11.3, -2.0), 0.8, 4.0, linewidth=1.0, edgecolor='#03045e', facecolor='#023e8a', zorder=9)
    ax2.add_patch(claw_e_top)
    ax2.add_patch(lip_e)
    ax2.text(16.5, 0, "East Claw\n(0° / 360°)", ha='left', va='center', fontsize=8, fontweight='bold', color='#03045e')

    claw_w_top = patches.Rectangle((-15.8, -2.25), 3.8, 4.5, linewidth=1.5, edgecolor='#03045e', facecolor='#1d3557', zorder=9)
    lip_w = patches.Rectangle((-12.1, -2.0), 0.8, 4.0, linewidth=1.0, edgecolor='#03045e', facecolor='#023e8a', zorder=9)
    ax2.add_patch(claw_w_top)
    ax2.add_patch(lip_w)
    ax2.text(-16.5, 0, "West Claw\n(180°)", ha='right', va='center', fontsize=8, fontweight='bold', color='#03045e')

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
    ax3.text(0, -0.8, "Main PCB (1.6mm)", ha='center', va='center', fontsize=8, fontweight='bold', color='#ffffff', zorder=3)

    # South Ear (Y = -11.3) and North Ear (Y = +11.3)
    ear_s = patches.Rectangle((-14.55, 0.0), 6.5, 2.4, linewidth=1.2, edgecolor='#1d3557', facecolor='#457b9d', zorder=4)
    ear_s_h = patches.Rectangle((-13.05, 0.0), 3.5, 2.4, linewidth=1.0, edgecolor='#d90429', facecolor='#ffffff', linestyle='--', zorder=5)
    ax3.add_patch(ear_s)
    ax3.add_patch(ear_s_h)

    ear_n = patches.Rectangle((8.05, 0.0), 6.5, 2.4, linewidth=1.2, edgecolor='#1d3557', facecolor='#457b9d', zorder=4)
    ear_n_h = patches.Rectangle((9.55, 0.0), 3.5, 2.4, linewidth=1.0, edgecolor='#d90429', facecolor='#ffffff', linestyle='--', zorder=5)
    ax3.add_patch(ear_n)
    ax3.add_patch(ear_n_h)

    # Cup Body Profile in Y-Z:
    # Cup body has UNIFORM rim height Z = 14.0 mm all around (below Equator Z = 18.30 mm)
    # North side (+Y) has North Claw rising from Z = 14.0 to Z = 22.80 mm
    # South side (-Y) stops cleanly at Z = 14.0 mm (No claw!)
    cup_yz_poly = patches.Polygon([
        # South uniform rim (Z = 14.0)
        (-14.0, 0.0), (-14.0, 14.0), (-11.8, 14.0),
        # Inner bowl profile
        (-8.0, 5.8), (-5.5, 3.4), (5.5, 3.4), (8.0, 5.8),
        # North side: uniform rim at 14.0, then claw rises to 22.80
        (11.8, 14.0), (11.5, 20.5), (11.2, 22.8), (12.5, 22.8), (14.5, 20.5), (14.0, 14.0), (14.0, 0.0)
    ], closed=True, edgecolor='#1d3557', facecolor='#a8dadc', alpha=0.85, lw=1.5, zorder=3)
    ax3.add_patch(cup_yz_poly)

    # Uniform rim dashed indicator across cup
    ax3.plot([-14.0, 14.0], [14.0, 14.0], linestyle=':', color='#1d3557', lw=1.0, zorder=4)

    # North Claw highlight
    claw_n_yz = patches.Polygon([(11.5, 20.5), (11.2, 22.8), (12.5, 22.8), (14.5, 20.5), (14.0, 14.0), (11.8, 14.0)],
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

    ax3.text(-11.3, 3.2, "South Ear", ha='center', va='bottom', fontsize=7.5, fontweight='bold', color='#1d3557')
    ax3.text(11.3, 3.2, "North Ear", ha='center', va='bottom', fontsize=7.5, fontweight='bold', color='#1d3557')

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


