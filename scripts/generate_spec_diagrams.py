# -*- coding: utf-8 -*-
"""
Generate engineering specification diagrams for curcur40 case documentation.
Outputs high-resolution diagrams to docs/assets/
"""
from pathlib import Path
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
    fig, ax = plt.subplots(figsize=(13.4, 7.6), dpi=200)
    ax.set_xlim(-24, 174)
    ax.set_ylim(-15.0, 2.2)
    ax.set_facecolor('#fcfcfc')
    fig.patch.set_facecolor('#ffffff')

    # Main PCB & Top Plate stack on left/center (X in [20, 102]), compact flat-topped perimeter boss at X = 112
    # Top Plate (FR4, Z = -3.6 to -2.0) with Ø4.40mm screw-head clearance hole around X = 112 (X in [107.2, 116.8] scaled)
    ax.add_patch(patches.Rectangle((20, -3.6), 87.2, 1.6, linewidth=1.5, edgecolor='#16425b', facecolor='#3a7ca5', alpha=0.88))
    ax.add_patch(patches.Rectangle((116.8, -3.6), 9.2, 1.6, linewidth=1.5, edgecolor='#16425b', facecolor='#3a7ca5', alpha=0.88))
    ax.text(60, -2.8, "Top Plate (FR4, 1.60mm — Choc V2 Switch Snap-Retained)", ha='center', va='center', fontsize=10.0, fontweight='bold', color='#ffffff')

    # Switch Gap (Z = -4.2 to -3.6)
    ax.add_patch(patches.Rectangle((20, -4.2), 87.2, 0.6, linewidth=1.2, edgecolor='#778da9', facecolor='#e0e1dd', alpha=0.45))
    ax.add_patch(patches.Rectangle((116.8, -4.2), 9.2, 0.6, linewidth=1.2, edgecolor='#778da9', facecolor='#e0e1dd', alpha=0.45))
    ax.text(60, -3.9, "Switch Gap (Kailh Choc v2: 0.60mm)", ha='center', va='center', fontsize=8.8, fontweight='bold', color='#111111')

    # Main PCB (FR4, Z = -5.8 to -4.2) with Ø2.40mm M2 screw hole around X = 112 (X in [109.6, 114.4] scaled)
    ax.add_patch(patches.Rectangle((20, -5.8), 89.6, 1.6, linewidth=1.5, edgecolor='#1b4332', facecolor='#2a9d8f', alpha=0.88))
    ax.add_patch(patches.Rectangle((114.4, -5.8), 11.6, 1.6, linewidth=1.5, edgecolor='#1b4332', facecolor='#2a9d8f', alpha=0.88))
    ax.text(60, -5.0, "Main PCB (FR4, 1.60mm — Directly Screw-Clamped!)", ha='center', va='center', fontsize=10.2, fontweight='bold', color='#ffffff')

    # Component Cavity (Z = -11.2 to -5.8)
    ax.add_patch(patches.Rectangle((20, -11.2), 86.8, 5.4, linewidth=1.3, edgecolor='#e07a5f', facecolor='#f4f1de', alpha=0.42))
    ax.text(32, -8.5, "Component\nCavity\n(Tilted Floor)", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#333333')

    # Sealed Case Floor (2.40mm uniform wall, 100% hole-free outer bottom!) + Compact Flat-Topped Ø5.20mm Boss at Z = -5.80mm:
    # Single-stage Ø5.20mm cylinder (1.175mm thick wall around Ø2.85mm bore — zero thin neck bottleneck during heat-set!)
    case_poly = patches.Polygon(
        [
            (20.0, -13.6), (126.0, -13.6), (126.0, -11.2),
            (117.2, -11.2), (117.2, -5.8), (114.8, -5.8),
            (114.8, -10.8), (109.2, -10.8), (109.2, -5.8),
            (106.8, -5.8), (106.8, -11.2),
            (20.0, -11.2),
        ],
        closed=True, linewidth=1.6, edgecolor='#212529', facecolor='#495057', alpha=0.88, zorder=3
    )
    ax.add_patch(case_poly)
    ax.text(74, -12.4, "100% Sealed Hole-Free Case Bottom Wall (Uniform 2.40 mm, 7.47° Tenting)",
            ha='center', va='center', fontsize=9.5, fontweight='bold', color='#ffffff', zorder=4)

    # Brass Heat-Set Insert (M2 x L=3.0 x OD=3.2 mm at Z = -8.80 to -5.80 mm) inside Ø2.85mm pilot bore
    ins_l = patches.Rectangle((109.0, -8.80), 1.4, 3.00, linewidth=1.2, edgecolor='#7f5539', facecolor='#e9c46a', hatch='///', zorder=4)
    ins_r = patches.Rectangle((113.6, -8.80), 1.4, 3.00, linewidth=1.2, edgecolor='#7f5539', facecolor='#e9c46a', hatch='///', zorder=4)
    ax.add_patch(ins_l)
    ax.add_patch(ins_r)

    # Top-Down Unified M2 x 6.0mm Screw (Head at Z = -4.20..-3.00 submerged inside Plate Ø4.4mm hole; shank Z = -10.20..-4.20)
    scr_head = patches.Rectangle((108.2, -4.20), 7.6, 1.20, linewidth=1.3, edgecolor='#212529', facecolor='#adb5bd', zorder=6)
    scr_shank = patches.Rectangle((110.2, -10.20), 3.6, 6.00, linewidth=1.3, edgecolor='#212529', facecolor='#ced4da', hatch='//', zorder=5)
    ax.add_patch(scr_head)
    ax.add_patch(scr_shank)

    # Component Protrusions on Under-PCB (B.Cu at Z = -5.80 mm)
    # 1. Choc Socket (1.80mm -> Z = -7.60mm)
    sock = patches.Rectangle((45, -5.8 - 1.80), 15, 1.80, linewidth=1, edgecolor='#d90429', facecolor='#ef233c', alpha=0.88, zorder=4)
    ax.add_patch(sock)
    ax.text(52.5, -6.70, "Choc\nSocket\n(1.80mm)", ha='center', va='center', fontsize=7.5, color='white', fontweight='bold', zorder=5)

    # 2. Mid-Mount USB-C J1/J2 (1.65mm below B.Cu -> Z = -7.45mm)
    usbc = patches.Rectangle((63, -5.8 - 1.65), 16, 1.65, linewidth=1, edgecolor='#6a040f', facecolor='#9d0208', alpha=0.88, zorder=4)
    ax.add_patch(usbc)
    ax.text(71.0, -6.625, "Mid-Mount\nUSB-C\n(1.65mm)", ha='center', va='center', fontsize=7.0, color='white', fontweight='bold', zorder=5)

    # 3. JST SH 6-pin Connector rJ3 (2.95mm -> Z = -8.75mm; wheel sensor & click are onboard B.Cu!)
    jst = patches.Rectangle((82, -5.8 - 2.95), 18, 2.95, linewidth=1, edgecolor='#003049', facecolor='#0077b6', alpha=0.88, zorder=4)
    ax.add_patch(jst)
    ax.text(91.0, -7.27, "JST SH rJ3\n(TB Sensor)\n(2.95mm)", ha='center', va='center', fontsize=7.0, color='white', fontweight='bold', zorder=5)

    def draw_dim(x, z1, z2, label, offset_text=0):
        ax.annotate('', xy=(x, z1), xytext=(x, z2),
                    arrowprops=dict(arrowstyle='<->', color='#2b2d42', lw=1.2))
        ax.text(x - 1.5 + offset_text, (z1 + z2) / 2, label, ha='right', va='center', fontsize=9.0, fontweight='bold', color='#2b2d42')

    draw_dim(17, -2.0, -3.6, "1.60 mm")
    draw_dim(17, -3.6, -4.2, "0.60 mm")
    draw_dim(17, -4.2, -5.8, "1.60 mm")
    draw_dim(17, -5.8, -11.2, "2.20..18.7 mm")
    draw_dim(17, -11.2, -13.6, "2.40 mm")

    draw_dim(7.5, 0.0, -11.2, "Pinky: 10.0 mm\n(Thumb: 26.9 mm)", offset_text=1.0)

    ax.annotate('Compact Valley Boss (All 12x: L1..L6, R1..R6)\n• Ø5.20mm cylinder (1.175mm thick wall!)\n• Clamps Main PCB (-4.20) via Ø2.40mm hole\n• Screw head submerged in Plate Ø4.40mm hole!',
                xy=(115.8, -3.60), xytext=(126.5, -2.6),
                arrowprops=dict(facecolor='#1d3557', shrink=0.05, width=1.0, headwidth=5),
                fontsize=7.3, fontweight='bold', color='#1d3557',
                bbox=dict(boxstyle="round,pad=0.25", fc="#e0f2fe", ec="#1d3557", lw=0.9))

    ax.annotate('M2 × L3.0 × OD3.2mm Brass Insert\n• Pressed straight into Ø2.85mm bore (-5.80)\n• Unified M2×6.0mm screws (zero standoffs!)',
                xy=(115.0, -7.20), xytext=(126.5, -8.2),
                arrowprops=dict(facecolor='#7f5539', shrink=0.05, width=1.0, headwidth=5),
                fontsize=7.5, fontweight='bold', color='#7f5539',
                bbox=dict(boxstyle="round,pad=0.25", fc="#fefae0", ec="#7f5539", lw=0.9))

    ax.annotate('Pinky Skim Floor Z=-8.00 (>=0.35mm clear)\nThumb Tilted Floor drops to Z=-24.50mm',
                xy=(52.5, -7.60), xytext=(55.0, -9.9),
                arrowprops=dict(facecolor='#d90429', shrink=0.05, width=1.0, headwidth=5),
                fontsize=7.8, fontweight='bold', color='#d90429',
                bbox=dict(boxstyle="round,pad=0.25", fc="#ffe3e0", ec="#d90429", lw=0.9))

    ax.set_title("curcur40 Vertical Z-Stackup Architecture (Compact Ø5.20mm PCB Boss, Switch-Retained Plate & Unified M2×6mm)", fontsize=12.8, fontweight='bold', pad=15)
    ax.set_xticks([])
    ax.set_yticks([0, -2.0, -3.6, -4.2, -5.8, -8.8, -11.2, -13.6])
    ax.set_yticklabels([
        'Z=0.0 (Case Rim)',
        'Z=-2.0 (Plate Top)',
        'Z=-3.6 (Plate Bot)',
        'Z=-4.2 (PCB Top)',
        'Z=-5.8 (PCB Bot)',
        'Z=-8.8 (Cavity)',
        'Z_floor (-8.0..-24.5)',
        'Z_bot (-10.0..-26.9)',
    ])
    ax.grid(axis='y', linestyle=':', alpha=0.6, color='#888888')

    plt.tight_layout()
    out_file = ASSETS_DIR / "stackup_cross_section.png"
    plt.savefig(out_file, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_file}")


def generate_ports_and_screws_diagram():
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18.5, 5.6), dpi=200)
    fig.patch.set_facecolor('#ffffff')

    # AX1: Split / Host USB-C Port (Section View, Y coordinate mapped directly to Z in [-11.5, +1.5])
    ax1.set_xlim(-3, 17)
    ax1.set_ylim(-11.5, 1.5)
    ax1.set_aspect('equal')
    ax1.set_facecolor('#f8f9fa')
    ax1.set_title("1. Mid-Mount USB-C Port (Section View)", fontsize=12, fontweight='bold')

    wall = patches.Rectangle((5.5, -11.0), 3.0, 11.0, linewidth=1.5, edgecolor='#333333', facecolor='#e9ecef')
    ax1.add_patch(wall)

    tp_plate = patches.Rectangle((0.0, -3.60), 5.2, 1.60, linewidth=1.2, edgecolor='#1d3557', facecolor='#457b9d', alpha=0.85)
    ax1.add_patch(tp_plate)
    ax1.text(2.6, -2.80, "Top Plate", ha='center', va='center', fontsize=6.5, color='white', fontweight='bold')
    ax1.plot([0.0, 9.5], [-2.00, -2.00], linestyle='--', color='#1d3557', lw=1.2)
    ax1.text(9.6, -1.90, "Plate Top (Z = -2.00mm)", ha='left', va='bottom', fontsize=7.5, fontweight='bold', color='#1d3557')

    pcb_rect = patches.Rectangle((0.0, -5.80), 1.4, 1.60, linewidth=1.2, edgecolor='#1b4332', facecolor='#2d6a4f', alpha=0.85)
    ax1.add_patch(pcb_rect)

    center_y = -5.85
    hole_straight = patches.Rectangle((5.5, -8.95), 3.0, 6.20, linewidth=1.5, edgecolor='#d90429', facecolor='#ffffff')
    ax1.add_patch(hole_straight)

    usbc_barrel = patches.Rectangle((1.4, -7.45), 4.6, 3.16, linewidth=1.2, edgecolor='#1d3557', facecolor='#a8dadc', alpha=0.9)
    ax1.add_patch(usbc_barrel)
    ax1.text(3.7, -5.87, "USB-C\n(J1/J2)", ha='center', va='center', fontsize=6.5, color='#1d3557', fontweight='bold')

    ax1.text(2.8, -1.55, "Top Edge Z = -2.75mm", ha='center', va='bottom', fontsize=6.5, fontweight='bold', color='#2d6a4f',
             bbox=dict(boxstyle="round,pad=0.2", fc="#d8f3dc", ec="#2d6a4f", lw=0.8))

    ax1.annotate('', xy=(9.4, -8.95), xytext=(9.4, -2.75),
                 arrowprops=dict(arrowstyle='<->', color='#d90429', lw=1.2))
    ax1.text(9.9, center_y, "Host (N) & Split (Inner)\nHeight: 6.20 mm (R=1.50)\nCenter Z = -5.85 mm\n+ Hidden Z=-5.80mm\n  PCB Support Shelves", ha='left', va='center', fontsize=7.5, fontweight='bold', color='#d90429')

    ax1.plot([0.2, 9.4], [center_y, center_y], linestyle='-.', color='#888888', lw=1)
    ax1.axis('off')

    # AX2: Host & Split USB-C Opening (Front View)
    ax2.set_xlim(-2, 18)
    ax2.set_ylim(-11.5, 1.5)
    ax2.set_aspect('equal')
    ax2.set_facecolor('#f8f9fa')
    ax2.set_title("2. Host & Split USB-C Cutout (Front View)", fontsize=12, fontweight='bold')

    wall2 = patches.Rectangle((0, -10.5), 16, 10.5, linewidth=1.5, edgecolor='#333333', facecolor='#e9ecef')
    ax2.add_patch(wall2)

    cx2 = 8.0
    w2 = 12.00
    h2 = 6.20
    ax2.plot([0, 16], [-2.00, -2.00], linestyle='--', color='#1d3557', lw=1.2)
    ax2.text(0.4, -1.85, "Top Plate Top (Z = -2.00mm)", ha='left', va='bottom', fontsize=7.5, fontweight='bold', color='#1d3557')

    cy2 = -5.85
    cutout_bot_y = cy2 - h2 / 2
    cutout_top_y = cy2 + h2 / 2
    cutout = patches.FancyBboxPatch((cx2 - w2/2, cutout_bot_y), w2, h2,
                                    boxstyle="round,pad=0,rounding_size=1.5",
                                    linewidth=1.5, edgecolor='#d90429', facecolor='#ffffff')
    ax2.add_patch(cutout)

    rec = patches.FancyBboxPatch((cx2 - 8.94/2, -5.87 - 3.16/2), 8.94, 3.16,
                                 boxstyle="round,pad=0,rounding_size=1.0",
                                 linewidth=1.2, edgecolor='#1d3557', facecolor='#a8dadc', alpha=0.85)
    ax2.add_patch(rec)
    ax2.text(cx2, -5.87, "TYPE-C-31-M-13C\n(8.94 x 3.16 mm, Z = -5.87)", ha='center', va='center', fontsize=6.8, fontweight='bold', color='#1d3557')

    ax2.annotate('', xy=(cx2 - w2/2, 0.4), xytext=(cx2 + w2/2, 0.4),
                 arrowprops=dict(arrowstyle='<->', color='#d90429', lw=1.2))
    ax2.text(cx2, 0.65, "Width: 12.00 mm (R=1.50)", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#d90429')

    ax2.annotate('', xy=(cx2 + w2/2 + 0.5, cutout_bot_y), xytext=(cx2 + w2/2 + 0.5, cutout_top_y),
                 arrowprops=dict(arrowstyle='<->', color='#d90429', lw=1.2))
    ax2.text(cx2 + w2/2 + 0.75, cy2, "Height:\n6.20 mm\n(Z = -5.85)", ha='left', va='center', fontsize=7.8, fontweight='bold', color='#d90429')

    ax2.text(cx2, -9.8, "Cutout Z = -8.95 to -2.75 mm (>=1.47mm Plug Clearance)", ha='center', va='center', fontsize=7.0, fontweight='bold', color='#2d6a4f')
    ax2.axis('off')

    # AX3: Compact Ø5.20mm PCB Boss + Brass Heat-Set Insert + M2 x 6.0mm Screw (Section View)
    ax3.set_xlim(-9.8, 9.8)
    ax3.set_ylim(-14.2, 0.7)
    ax3.set_aspect('equal')
    ax3.set_facecolor('#f8f9fa')
    ax3.set_title("3. Compact Ø5.2mm Boss & M2×6mm Screw", fontsize=12, fontweight='bold')

    ax3.axvline(0.0, linestyle='-.', color='#888888', lw=0.9)

    # Top Plate (Z = -3.60 to -2.00) with Ø4.40mm screw-head clearance hole (X = ±2.20)
    ax3.add_patch(patches.Rectangle((-8.0, -3.60), 5.80, 1.60, lw=1.2, ec='#16425b', fc='#3a7ca5', alpha=0.88))
    ax3.add_patch(patches.Rectangle((2.20, -3.60), 5.80, 1.60, lw=1.2, ec='#16425b', fc='#3a7ca5', alpha=0.88))
    ax3.text(-5.1, -2.80, "Top Plate", ha='center', va='center', fontsize=6.8, color='white', fontweight='bold')

    # Main PCB (Z = -5.80 to -4.20) with Ø2.40mm M2 clamping hole (X = ±1.20)
    ax3.add_patch(patches.Rectangle((-8.0, -5.80), 6.80, 1.60, lw=1.2, ec='#1b4332', fc='#2a9d8f', alpha=0.88))
    ax3.add_patch(patches.Rectangle((1.20, -5.80), 6.80, 1.60, lw=1.2, ec='#1b4332', fc='#2a9d8f', alpha=0.88))
    ax3.text(-4.8, -5.00, "Main PCB", ha='center', va='center', fontsize=6.8, color='white', fontweight='bold')

    # Case Compact Flat-Topped Ø5.20mm Boss (X = ±2.60, Z = -11.00..-5.80)
    # + Ø2.85mm blind bore (X = ±1.425, Z = -11.00..-5.80 -> 1.175mm thick wall!) + 2.40mm Sealed Floor (-13.40..-11.00)
    boss_floor = patches.Polygon(
        [
            (-8.0, -13.40), (8.0, -13.40), (8.0, -11.00),
            (2.60, -11.00), (2.60, -5.80),
            (1.425, -5.80), (1.425, -10.80), (-1.425, -10.80), (-1.425, -5.80),
            (-2.60, -5.80), (-2.60, -11.00),
            (-8.0, -11.00),
        ],
        closed=True, lw=1.4, ec='#212529', fc='#dee2e6', zorder=2
    )
    ax3.add_patch(boss_floor)
    ax3.text(0.0, -12.25, "Sealed Solid Bottom Wall (2.40 mm — Zero Holes)", ha='center', va='center', fontsize=7.0, fontweight='bold', color='#212529', zorder=3)

    # Brass Heat-Set Insert (M2 x L=3.0 x OD=3.2mm: X in [1.00, 1.60], Z in [-8.80, -5.80])
    ax3.add_patch(patches.Rectangle((-1.60, -8.80), 0.60, 3.00, lw=1.0, ec='#7f5539', fc='#e9c46a', hatch='///', zorder=4))
    ax3.add_patch(patches.Rectangle((1.00, -8.80), 0.60, 3.00, lw=1.0, ec='#7f5539', fc='#e9c46a', hatch='///', zorder=4))

    # Top-Down M2 x 6.0mm Screw (Head Ø3.8 x 1.2mm at Z = -4.20..-3.00 submerged in Plate Ø4.4mm hole; Shank Ø2.0 x 6.0mm at Z = -10.20..-4.20)
    ax3.add_patch(patches.Rectangle((-1.90, -4.20), 3.80, 1.20, lw=1.2, ec='#343a40', fc='#adb5bd', zorder=6))
    ax3.add_patch(patches.Rectangle((-1.00, -10.20), 2.00, 6.00, lw=1.2, ec='#343a40', fc='#ced4da', zorder=5))

    ax3.text(0.0, -0.35, "12x Flat Ø5.2mm Valley Boss (Main PCB Ø2.4mm Clamped)\n[Screw Head Submerged in Plate Ø4.4mm Hole]",
             ha='center', va='bottom', fontsize=6.5, fontweight='bold', color='#16425b')

    ax3.annotate('Ø5.20 Flat Boss (-5.80)\n1.175mm Uniform Wall!\n+ Flush M2×L3.0 Insert', xy=(2.60, -7.00), xytext=(3.60, -9.20),
                 arrowprops=dict(arrowstyle='->', color='#7f5539', lw=1.1),
                 fontsize=6.5, fontweight='bold', color='#7f5539',
                 bbox=dict(boxstyle="round,pad=0.18", fc="#fefae0", ec="#7f5539", lw=0.7))

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

    ball_center = (0, 18.30)
    ball = patches.Circle(ball_center, 12.50, linewidth=1.5, edgecolor='#0077b6', facecolor='#90e0ef', alpha=0.35)
    ax.add_patch(ball)
    ax.text(0, 18.30, "Ø 25 mm Trackball Sphere\n(Center Z_rel = +18.30 mm, Bottom Z_rel = +5.80 mm)", ha='center', va='center', fontsize=10, fontweight='bold', color='#03045e')

    cup_outline = patches.Arc(ball_center, 27.0, 27.0, theta1=205, theta2=335, linewidth=3, color='#023e8a')
    ax.add_patch(cup_outline)
    ax.text(-18, 12.0, "Trackball Cup Body\n(Claws: N 90°, E 0°, W 180°)", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#023e8a')

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

    leg_left = patches.Rectangle((-7.1, -3.35), 1.0, 3.35, linewidth=1.2, edgecolor='#d48b00', facecolor='#ffb703')
    leg_right = patches.Rectangle((6.2, -3.35), 1.0, 3.35, linewidth=1.2, edgecolor='#d48b00', facecolor='#ffb703')
    ax.add_patch(leg_left)
    ax.add_patch(leg_right)
    ax.annotate('4 Lens Legs extend DOWN\nthrough 16.9x8.7mm PCB cutout',
                xy=(7.2, -2.5), xytext=(10.5, 1.2),
                arrowprops=dict(facecolor='#d48b00', shrink=0.05, width=1, headwidth=4),
                fontsize=8, fontweight='bold', color='#d48b00',
                bbox=dict(boxstyle="round,pad=0.2", fc="#fff3cd", ec="#d48b00", lw=0.8))

    pcb_left = patches.Rectangle((-24, -1.6), 15.55, 1.6, linewidth=1.5, edgecolor='#2d6a4f', facecolor='#52b788', alpha=0.85)
    pcb_right = patches.Rectangle((8.45, -1.6), 15.55, 1.6, linewidth=1.5, edgecolor='#2d6a4f', facecolor='#52b788', alpha=0.85)
    ax.add_patch(pcb_left)
    ax.add_patch(pcb_right)
    ax.text(-16, -0.8, "Sensor PCB (1.6mm)", ha='center', va='center', fontsize=9, fontweight='bold', color='#ffffff')
    ax.text(16, -0.8, "Sensor PCB (1.6mm)", ha='center', va='center', fontsize=9, fontweight='bold', color='#ffffff')
    ax.text(0, -0.8, "PCB Cutout (16.9 x 8.7 mm)", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#1b4332')

    pmw_body = patches.Rectangle((-8.1, -4.01), 16.2, 2.41, linewidth=1.5, edgecolor='#14213d', facecolor='#2b2d42', alpha=0.95)
    ax.add_patch(pmw_body)
    ax.text(0, -3.0, "PMW3360 IC Solid Body (2.41mm)\n[NO THROUGH-HOLE IN SENSOR]", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#ffffff')

    ax.plot([-8.1, -9.2, -9.2], [-2.3, -2.3, 0.8], color='#ffd166', lw=2.5)
    ax.plot([8.1, 9.2, 9.2], [-2.3, -2.3, 0.8], color='#ffd166', lw=2.5)
    ax.annotate('16 Pins emerge from IC sides,\nextend UP through PCB to F.Cu',
                xy=(-9.2, 0.4), xytext=(-24, 2.5),
                arrowprops=dict(facecolor='#cca000', shrink=0.05, width=1, headwidth=4),
                fontsize=8, fontweight='bold', color='#cca000',
                bbox=dict(boxstyle="round,pad=0.2", fc="#fff9db", ec="#cca000", lw=0.8))

    floor = patches.Rectangle((-24, -8.7), 48, 2.4, linewidth=2, edgecolor='#495057', facecolor='#ced4da', alpha=0.7)
    ax.add_patch(floor)
    ax.text(0, -7.5, "Sealed Tilted Case Floor (Z_rel = -6.29..-8.16 mm / Global Z = -22.29..-24.16 mm)\n(Zero Through-Hole or Sensor Pocket Needed!)", ha='center', va='center', fontsize=9.0, fontweight='bold', color='#212529')

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
    fig, ax = plt.subplots(figsize=(13, 8.8), dpi=200)
    ax.set_xlim(-16, 26)
    ax.set_ylim(-8.5, 5.2)
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#ffffff')

    # Center axis (X = 0)
    ax.plot([0, 0], [-8.0, 4.5], linestyle='-.', color='#888888', lw=1.2, zorder=1)
    ax.text(0, 4.6, "Center Line (CL)", ha='center', va='bottom', fontsize=9, color='#666666', fontweight='bold')

    # -------------------------------------------------------------
    # Layer 3: Case Boss at TB1..TB4 (Boss Top Z_rel = -1.60 / Global Z = -17.60 mm)
    # OD Ø6.00 mm (X = ±3.00), Blind Ø2.85 mm pilot bore 3.80 mm deep to Z_rel = -5.40 (Global Z = -21.40 mm)
    # Rising from 100% Sealed 2.40 mm Tilted Case Floor!
    # -------------------------------------------------------------
    case_boss = patches.Polygon(
        [
            (-14.0, -7.80), (14.0, -7.80), (14.0, -5.40),
            (3.00, -5.40), (3.00, -1.60), (1.425, -1.60), (1.425, -5.40),
            (-1.425, -5.40), (-1.425, -1.60), (-3.00, -1.60), (-3.00, -5.40),
            (-14.0, -5.40),
        ],
        closed=True, linewidth=1.5, edgecolor='#343a40', facecolor='#adb5bd', alpha=0.92, zorder=2
    )
    ax.add_patch(case_boss)
    ax.text(0, -6.65, "100% Sealed Case Bottom Wall (2.40 mm Solid — Zero Bottom Holes)",
            ha='center', va='center', fontsize=9.0, fontweight='bold', color='#212529', zorder=3)

    # Brass Heat-Set Insert (M2 x L=3.0 x OD=3.2 mm: Z_rel = -4.60 to -1.60 mm)
    ins_l = patches.Rectangle((-1.60, -4.60), 0.60, 3.00, linewidth=1.2, edgecolor='#7f5539', facecolor='#e9c46a', hatch='///', zorder=4)
    ins_r = patches.Rectangle((1.00, -4.60), 0.60, 3.00, linewidth=1.2, edgecolor='#7f5539', facecolor='#e9c46a', hatch='///', zorder=4)
    ax.add_patch(ins_l)
    ax.add_patch(ins_r)

    # -------------------------------------------------------------
    # Layer 2: Sensor PCB (Z_rel = -1.60 to 0.00, Thickness 1.60 mm, Straight Ø2.40 mm hole)
    # -------------------------------------------------------------
    pcb_left = patches.Rectangle((-14, -1.60), 12.80, 1.60, linewidth=1.5, edgecolor='#1b4332', facecolor='#52b788', alpha=0.90, zorder=2)
    pcb_right = patches.Rectangle((1.20, -1.60), 12.80, 1.60, linewidth=1.5, edgecolor='#1b4332', facecolor='#52b788', alpha=0.90, zorder=2)
    ax.add_patch(pcb_left)
    ax.add_patch(pcb_right)

    # -------------------------------------------------------------
    # Layer 1: Cup Flat Mounting Ear (Z_rel = 0.00 to +2.00, Height 2.00 mm, Straight Ø2.40 mm hole)
    # -------------------------------------------------------------
    ear_left = patches.Rectangle((-9.0, 0.00), 7.80, 2.00, linewidth=1.5, edgecolor='#1d3557', facecolor='#457b9d', alpha=0.90, zorder=2)
    ear_right = patches.Rectangle((1.20, 0.00), 7.80, 2.00, linewidth=1.5, edgecolor='#1d3557', facecolor='#457b9d', alpha=0.90, zorder=2)
    ax.add_patch(ear_left)
    ax.add_patch(ear_right)

    # -------------------------------------------------------------
    # Top-Down Unified M2 x 6.0mm Screw
    # Head rests at Z_rel = +2.00, shank Ø2.0 x 6.0mm reaches Z_rel = -4.00 (engages 2.40mm into 3.0mm insert!)
    # -------------------------------------------------------------
    top_head = patches.Rectangle((-1.95, 2.00), 3.90, 1.15, linewidth=1.5, edgecolor='#212529', facecolor='#6c757d', zorder=6)
    top_shaft = patches.Rectangle((-1.00, -4.00), 2.00, 6.00, linewidth=1.5, edgecolor='#212529', facecolor='#495057', zorder=5)
    ax.add_patch(top_head)
    ax.add_patch(top_shaft)

    # Blind-bore bottom clearance (Z_rel = -4.00 to -5.40 = 1.40 mm)
    ax.annotate('', xy=(0, -4.00), xytext=(0, -5.40),
                arrowprops=dict(arrowstyle='<->', color='#2b9348', lw=2.0), zorder=7)
    ax.text(0.35, -4.70, "1.40 mm\nBottom Gap", ha='left', va='center', fontsize=8.0, fontweight='bold', color='#2b9348',
            bbox=dict(boxstyle="round,pad=0.18", fc="#d8f3dc", ec="#2b9348", lw=0.8), zorder=7)

    # Left Dimensions: Layer-by-layer Stackup
    def dim_left(z1, z2, label, x=-10.5, color='#1d3557'):
        ax.annotate('', xy=(x, z1), xytext=(x, z2),
                    arrowprops=dict(arrowstyle='<->', color=color, lw=1.2))
        ax.text(x - 0.5, (z1 + z2) / 2, label, ha='right', va='center', fontsize=8.8, fontweight='bold', color=color)

    dim_left(2.00, 0.00, "1. Flat Cup Ear:\n2.00 mm (Ø2.4)", -10.2, '#1d3557')
    dim_left(0.00, -1.60, "2. Sensor PCB:\n1.60 mm (Ø2.4)", -10.2, '#1b4332')
    dim_left(-1.60, -4.60, "3. Brass Insert:\n3.00 mm (M2)", -10.2, '#7f5539')
    dim_left(-5.40, -7.80, "4. Sealed Floor:\n2.40 mm Solid", -10.2, '#343a40')

    # Right Annotations
    ax.annotate('Unified Top-Down M2 × 6.0mm Screw\n• Same screw length as all 19 fastening points!\n• Clamps 2.00mm Cup Ear + 1.60mm Sensor PCB\n• Engages 2.40mm (6 full threads) into Brass Insert',
                xy=(1.95, 2.55), xytext=(8.5, 2.7),
                arrowprops=dict(facecolor='#212529', shrink=0.05, width=1.1, headwidth=5),
                fontsize=8.3, fontweight='bold', color='#212529',
                bbox=dict(boxstyle="round,pad=0.25", fc="#e9ecef", ec="#212529", lw=0.8))

    ax.annotate('Simplified Flat Cup Ear (Height: 2.00 mm)\n• Straight Ø2.40mm clearance hole (zero stepped bore!)\n• Eliminates 5.50mm standoffs & <0.80mm ear steps',
                xy=(3.5, 1.0), xytext=(8.5, 0.4),
                arrowprops=dict(facecolor='#1d3557', shrink=0.05, width=1.1, headwidth=5),
                fontsize=8.3, fontweight='bold', color='#1d3557',
                bbox=dict(boxstyle="round,pad=0.25", fc="#e0f2fe", ec="#1d3557", lw=0.8))

    ax.annotate('Sensor PCB Sandwich (Thickness: 1.60 mm, Hole: Ø2.40 mm)\n• Sandwiched directly between Boss (-17.6) & Cup (-16.0)',
                xy=(3.5, -0.8), xytext=(8.5, -1.7),
                arrowprops=dict(facecolor='#1b4332', shrink=0.05, width=1.1, headwidth=5),
                fontsize=8.3, fontweight='bold', color='#1b4332',
                bbox=dict(boxstyle="round,pad=0.25", fc="#d8f3dc", ec="#1b4332", lw=0.8))

    ax.annotate('Case Heat-Set Boss (Top Z = -17.60 mm, OD Ø6.00 mm)\n• Blind Ø2.85mm pilot bore (depth 3.80mm to Z = -21.40)\n• M2 × L3.0 × OD3.2mm Brass Heat-Set Insert\n• 100% sealed outer bottom (zero counterbores)',
                xy=(3.00, -3.20), xytext=(8.5, -4.2),
                arrowprops=dict(facecolor='#7f5539', shrink=0.05, width=1.1, headwidth=5),
                fontsize=8.3, fontweight='bold', color='#7f5539',
                bbox=dict(boxstyle="round,pad=0.25", fc="#fefae0", ec="#7f5539", lw=0.8))

    ax.annotate('', xy=(-3.0, -5.8), xytext=(3.0, -5.8),
                arrowprops=dict(arrowstyle='<->', color='#343a40', lw=1.0))
    ax.text(0, -6.0, "Boss OD Ø 6.00 mm", ha='center', va='top', fontsize=8.0, color='#343a40', fontweight='bold')

    ax.set_title("Trackball Cup 4-Hole Fastening Architecture (2.00mm Flat Ear + Top-Down M2×6mm + Brass Heat-Set Insert)", fontsize=12.5, fontweight='bold', pad=15)
    ax.axis('off')

    plt.tight_layout()
    out_file = ASSETS_DIR / "trackball_cup_fastening_diagram.png"
    plt.savefig(out_file, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_file}")


def generate_trackball_cup_detail_drawing():
    """
    Generate comprehensive engineering drawing of the trackball cup:
    - Left Panel: Front / Side Cross-Section (X-Z View) with Flat Mounting Ears (Z=0 to 2.0mm, straight hole Ø2.4mm),
                  Ball (Ø25mm, center Z=18.30), Claws (Z=22.80), Bearings (Z=7.66), and Lens Pocket (Z=3.40).
    - Middle Panel: Top Plan View (X-Y View) with all 4 Mounting Ears (NE, NW, SW, SE at X=±12, Y=±11.3),
                    3 Claws (N 90°, E 0°, W 180°), South Open (270°), and 3 Bearings.
    - Right Panel: Side Elevation (Y-Z View) showing North Claw (Z=22.80) vs South Uniform Rim (Z=14.00)
                   and South/North Mounting Ears (Y=±11.3).
    """
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(22, 10.5), dpi=200)
    fig.patch.set_facecolor('#ffffff')

    # =========================================================================
    # PANEL 1: X-Z Cross Section & Front View
    # =========================================================================
    ax1.set_facecolor('#fcfcfc')
    ax1.set_xlim(-26, 26)
    ax1.set_ylim(-6, 36)
    ax1.set_aspect('equal')

    ax1.plot([0, 0], [-5, 35], linestyle='-.', color='#888888', lw=1.0)
    ax1.text(0, 35.2, "CL (X=0)", ha='center', va='bottom', fontsize=8, color='#666666')

    pcb_xz = patches.Rectangle((-24, -1.6), 48, 1.6, linewidth=1.2, edgecolor='#1b4332', facecolor='#52b788', alpha=0.75, zorder=2)
    ax1.add_patch(pcb_xz)
    ax1.text(-19, -0.8, "Sensor PCB (1.6mm)", ha='center', va='center', fontsize=8, fontweight='bold', color='#ffffff', zorder=3)

    # 4 Flat Mounting Ears: Left Ear (X=-12, R=3.0) and Right Ear (X=+12, R=3.0), Height 2.00mm, straight Ø2.40mm hole
    for ex_c in (-12.0, 12.0):
        ear_body = patches.Rectangle((ex_c - 3.0, 0.0), 6.0, 2.00, linewidth=1.2, edgecolor='#1d3557', facecolor='#457b9d', zorder=4)
        ear_hole = patches.Rectangle((ex_c - 1.20, 0.0), 2.40, 2.00, linewidth=1.0, edgecolor='#d90429', facecolor='#ffffff', linestyle='--', zorder=5)
        ax1.add_patch(ear_body)
        ax1.add_patch(ear_hole)

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

    claw_w = patches.Polygon([(-14.0, 14.0), (-14.0, 20.5), (-12.5, 22.8), (-11.2, 22.8), (-11.5, 20.5), (-12.0, 14.0)],
                             closed=True, edgecolor='#03045e', facecolor='#1d3557', zorder=5)
    claw_e = patches.Polygon([(14.0, 14.0), (14.0, 20.5), (12.5, 22.8), (11.2, 22.8), (11.5, 20.5), (12.0, 14.0)],
                             closed=True, edgecolor='#03045e', facecolor='#1d3557', zorder=5)
    ax1.add_patch(claw_w)
    ax1.add_patch(claw_e)
    ax1.text(-13.0, 23.5, "West Claw (180°)\nTip Z=+22.80", ha='center', va='bottom', fontsize=8, fontweight='bold', color='#1d3557')
    ax1.text(13.0, 23.5, "East Claw (0°)\nTip Z=+22.80", ha='center', va='bottom', fontsize=8, fontweight='bold', color='#1d3557')

    lens_rect = patches.Rectangle((-9.0, 0.0), 18.0, 3.4, linewidth=1.2, edgecolor='#e76f51', facecolor='#f4a261', alpha=0.9, zorder=3)
    ax1.add_patch(lens_rect)
    ax1.text(0, 1.7, "LM19 Lens (Flange Z=+3.40mm)", ha='center', va='center', fontsize=7.0, fontweight='bold', color='#ffffff', zorder=4)

    ball_xz = patches.Circle((0, 18.30), 12.50, linewidth=1.5, edgecolor='#0077b6', facecolor='#caf0f8', alpha=0.45, zorder=4)
    ax1.add_patch(ball_xz)
    ax1.plot([0], [18.30], marker='+', markersize=10, color='#03045e', mew=1.5, zorder=5)
    ax1.text(0.5, 18.5, "Ball Center\nZ = +18.30 mm", ha='left', va='bottom', fontsize=8.5, fontweight='bold', color='#03045e')
    ax1.plot([-13, 13], [18.30, 18.30], linestyle=':', color='#0077b6', lw=1.2, zorder=4)

    brg_l = patches.Circle((-7.20, 7.66), 1.0, linewidth=1.2, edgecolor='#6a040f', facecolor='#d90429', zorder=6)
    brg_r = patches.Circle((7.20, 7.66), 1.0, linewidth=1.2, edgecolor='#6a040f', facecolor='#d90429', zorder=6)
    ax1.add_patch(brg_l)
    ax1.add_patch(brg_r)
    ax1.text(4.2, 8.8, "Ø2.0mm Bearing\n(Z=+7.66mm)", ha='center', va='bottom', fontsize=7.0, fontweight='bold', color='#d90429', zorder=7)

    def dim_v(z1, z2, label, x, col='#2b2d42', fs=7.5, y_text=None):
        ax1.annotate('', xy=(x, z1), xytext=(x, z2),
                     arrowprops=dict(arrowstyle='<->', color=col, lw=1.0))
        ty = (z1 + z2) / 2 if y_text is None else y_text
        ha = 'right' if x < 0 else 'left'
        dx_t = -0.4 if x < 0 else 0.4
        ax1.text(x + dx_t, ty, label, ha=ha, va='center', fontsize=fs, fontweight='bold', color=col,
                 bbox=dict(boxstyle="round,pad=0.15", fc="#ffffff", ec=col, lw=0.6, alpha=0.95))

    dim_v(2.0, 0.0, "Ear: 2.00mm", -15.8, '#1d3557', 7.5, y_text=1.0)
    dim_v(3.4, 0.0, "Lens: 3.40mm", -16.8, '#e76f51', 7.5, y_text=4.6)
    dim_v(18.30, 0.0, "Center: 18.30mm", -17.8, '#03045e', 7.5, y_text=15.0)
    dim_v(5.8, 0.0, "Ball Bot: 5.80mm", 15.8, '#0077b6', 7.5, y_text=2.9)
    dim_v(22.80, 18.30, "Claw Tip:\n+4.50mm", 15.8, '#1d3557', 7.5, y_text=20.5)
    dim_v(30.80, 0.0, "Ball Top:\n30.80mm", 17.5, '#0077b6', 7.5, y_text=28.5)

    ax1.annotate('', xy=(-12.0, -3.2), xytext=(12.0, -3.2),
                 arrowprops=dict(arrowstyle='<->', color='#1d3557', lw=1.2))
    ax1.text(0, -3.6, "Ear Pitch X: 24.00 mm", ha='center', va='top', fontsize=8.5, fontweight='bold', color='#1d3557')

    ax1.annotate('Flat Ear (Height: 2.00 mm)\nStraight Ø2.40 mm M2 Clearance Hole',
                 xy=(-12.0, 2.0), xytext=(-25.2, 8.8),
                 arrowprops=dict(facecolor='#1d3557', shrink=0.05, width=1.0, headwidth=4),
                 fontsize=7.5, fontweight='bold', color='#1d3557',
                 bbox=dict(boxstyle="round,pad=0.2", fc="#e0f2fe", ec="#1d3557", lw=0.8))

    ax1.set_title("1. Trackball Cup Cross-Section (X-Z View)\n[側面断面・正面図: 西/東爪・2.0mm平耳・光学系]", fontsize=11, fontweight='bold', pad=12)
    ax1.axis('off')

    # =========================================================================
    # PANEL 2: X-Y Top Plan View
    # =========================================================================
    ax2.set_facecolor('#fcfcfc')
    ax2.set_xlim(-28, 28)
    ax2.set_ylim(-28, 28)
    ax2.set_aspect('equal')

    ax2.plot([0, 0], [-27, 27], linestyle='-.', color='#888888', lw=1.0)
    ax2.plot([-27, 27], [0, 0], linestyle='-.', color='#888888', lw=1.0)
    ax2.text(0, 27.2, "CL-Y (North 90°)", ha='center', va='bottom', fontsize=8, color='#666666', fontweight='bold')
    ax2.text(27.2, 0, "CL-X (East 0°)", ha='left', va='center', fontsize=8, color='#666666', fontweight='bold')

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

        hole = patches.Circle((ex, ey), 1.20, linewidth=1.2, edgecolor='#d90429', facecolor='#ffffff', zorder=4)
        ax2.add_patch(hole)
        ha_align = 'left' if ex > 0 else 'right'
        va_align = 'bottom' if ey > 0 else 'top'
        ax2.text(ex + (1.6 if ex > 0 else -1.6), ey + (1.6 if ey > 0 else -1.6),
                 f"{elab}\n({ex:+.1f}, {ey:+.1f})", ha=ha_align, va=va_align, fontsize=7.5, fontweight='bold', color='#1d3557',
                 bbox=dict(boxstyle="round,pad=0.15", fc="#ffffff", ec="#1d3557", lw=0.6, alpha=0.9))

    cup_out = patches.Circle((0, 0), 14.0, linewidth=2.0, edgecolor='#1d3557', facecolor='#a8dadc', alpha=0.55, zorder=5)
    ax2.add_patch(cup_out)

    cup_in = patches.Circle((0, 0), 12.85, linewidth=1.5, edgecolor='#0077b6', facecolor='#e0f2fe', alpha=0.7, zorder=6)
    ax2.add_patch(cup_in)

    ball_top = patches.Circle((0, 0), 12.50, linewidth=1.5, edgecolor='#023e8a', facecolor='#caf0f8', alpha=0.5, linestyle='--', zorder=7)
    ax2.add_patch(ball_top)
    ax2.text(0, 0, "Ø25.0 mm Trackball\nNavigation Center", ha='center', va='center', fontsize=8, fontweight='bold', color='#03045e', zorder=8)

    peep = patches.Rectangle((-5.5, -4.0), 11.0, 8.0, linewidth=1.2, edgecolor='#e76f51', facecolor='#fcbf49', alpha=0.85, zorder=7)
    ax2.add_patch(peep)

    claw_n = patches.Rectangle((-2.25, 11.6), 4.5, 2.4, linewidth=1.5, edgecolor='#03045e', facecolor='#1d3557', zorder=9)
    ax2.add_patch(claw_n)
    ax2.text(0, 14.5, "North Claw (90°)\n[Width: 4.50mm]", ha='center', va='bottom', fontsize=8, fontweight='bold', color='#03045e')

    claw_e_top = patches.Rectangle((11.6, -2.25), 2.4, 4.5, linewidth=1.5, edgecolor='#03045e', facecolor='#1d3557', zorder=9)
    ax2.add_patch(claw_e_top)
    ax2.text(14.6, 0, "East Claw\n(0° / 360°)", ha='left', va='center', fontsize=8, fontweight='bold', color='#03045e')

    claw_w_top = patches.Rectangle((-14.0, -2.25), 2.4, 4.5, linewidth=1.5, edgecolor='#03045e', facecolor='#1d3557', zorder=9)
    ax2.add_patch(claw_w_top)
    ax2.text(-14.6, 0, "West Claw\n(180°)", ha='right', va='center', fontsize=8, fontweight='bold', color='#03045e')

    ax2.annotate('South (270°): Claw-Free (爪なし)\n• Cup body rim is below equator all around\n• Ball is naturally accessible (低リム不要・全周均一)',
                 xy=(0, -14.0), xytext=(0, -21.0),
                 arrowprops=dict(facecolor='#1d3557', shrink=0.05, width=1.0, headwidth=4),
                 fontsize=8, fontweight='bold', color='#1d3557', ha='center',
                 bbox=dict(boxstyle="round,pad=0.25", fc="#f1faee", ec="#1d3557", lw=0.8), zorder=10)

    brg_coords = [(7.20, 4.16, "#1 (30°)"), (-7.20, 4.16, "#2 (150°)"), (0.00, -8.31, "#3 (270°)")]
    orbit_c = patches.Circle((0, 0), 8.31, linewidth=0.8, edgecolor='#b7094c', facecolor='none', linestyle=':', zorder=8)
    ax2.add_patch(orbit_c)
    for bx, by, blab in brg_coords:
        b_dot = patches.Circle((bx, by), 1.0, linewidth=1.2, edgecolor='#6a040f', facecolor='#d90429', zorder=10)
        ax2.add_patch(b_dot)
        ax2.text(bx + (1.2 if bx >= 0 else -1.2), by + (1.0 if by > -5 else -1.5),
                 f"Brg {blab}", ha='left' if bx >= 0 else 'right', va='center', fontsize=7.5, fontweight='bold', color='#9d0208',
                 bbox=dict(boxstyle="round,pad=0.15", fc="#ffffff", ec="#9d0208", lw=0.6, alpha=0.9), zorder=11)

    ax2.annotate('', xy=(-12.0, 21.0), xytext=(12.0, 21.0),
                 arrowprops=dict(arrowstyle='<->', color='#1d3557', lw=1.2))
    ax2.text(0, 21.6, "Pitch X: 24.00 mm", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#1d3557',
             bbox=dict(boxstyle="round,pad=0.15", fc="#ffffff", ec="#1d3557", lw=0.6))

    ax2.annotate('', xy=(23.5, -11.3), xytext=(23.5, 11.3),
                 arrowprops=dict(arrowstyle='<->', color='#1d3557', lw=1.2))
    ax2.text(24.2, 0, "Pitch Y:\n22.60 mm", ha='left', va='center', fontsize=8.5, fontweight='bold', color='#1d3557',
             bbox=dict(boxstyle="round,pad=0.15", fc="#ffffff", ec="#1d3557", lw=0.6))

    ax2.set_title("2. Trackball Cup Top Plan View (X-Y View)\n[天井からの平面図: 4耳(Ø2.4直穴)・3保持爪・南側爪なし・3支玉]", fontsize=11, fontweight='bold', pad=12)
    ax2.axis('off')

    # =========================================================================
    # PANEL 3: Y-Z Side Elevation View
    # =========================================================================
    ax3.set_facecolor('#fcfcfc')
    ax3.set_xlim(-26, 26)
    ax3.set_ylim(-6, 36)
    ax3.set_aspect('equal')

    ax3.plot([0, 0], [-5, 35], linestyle='-.', color='#888888', lw=1.0)
    ax3.text(0, 35.2, "CL (Y=0)", ha='center', va='bottom', fontsize=8, color='#666666')

    pcb_yz = patches.Rectangle((-24, -1.6), 48, 1.6, linewidth=1.2, edgecolor='#1b4332', facecolor='#52b788', alpha=0.75, zorder=2)
    ax3.add_patch(pcb_yz)
    ax3.text(0, -0.8, "Sensor PCB (1.6mm)", ha='center', va='center', fontsize=8, fontweight='bold', color='#ffffff', zorder=3)

    for ey_c in (-11.3, 11.3):
        ear_b = patches.Rectangle((ey_c - 3.0, 0.0), 6.0, 2.00, linewidth=1.2, edgecolor='#1d3557', facecolor='#457b9d', zorder=4)
        ear_h = patches.Rectangle((ey_c - 1.20, 0.0), 2.40, 2.00, linewidth=1.0, edgecolor='#d90429', facecolor='#ffffff', linestyle='--', zorder=5)
        ax3.add_patch(ear_b)
        ax3.add_patch(ear_h)

    cup_yz_poly = patches.Polygon([
        (-14.0, 0.0), (-14.0, 14.0), (-11.8, 14.0),
        (-8.0, 5.8), (-5.5, 3.4), (5.5, 3.4), (8.0, 5.8),
        (11.8, 14.0), (11.5, 20.5), (11.2, 22.8), (12.5, 22.8), (14.0, 20.5), (14.0, 14.0), (14.0, 0.0)
    ], closed=True, edgecolor='#1d3557', facecolor='#a8dadc', alpha=0.85, lw=1.5, zorder=3)
    ax3.add_patch(cup_yz_poly)

    ax3.plot([-14.0, 14.0], [14.0, 14.0], linestyle=':', color='#1d3557', lw=1.0, zorder=4)

    claw_n_yz = patches.Polygon([(11.5, 20.5), (11.2, 22.8), (12.5, 22.8), (14.0, 20.5), (14.0, 14.0), (11.8, 14.0)],
                                closed=True, edgecolor='#03045e', facecolor='#1d3557', zorder=5)
    ax3.add_patch(claw_n_yz)
    ax3.text(13.0, 23.5, "North Claw (90°)\nTip Z=+22.80mm", ha='center', va='bottom', fontsize=8, fontweight='bold', color='#03045e')

    ball_yz = patches.Circle((0, 18.30), 12.50, linewidth=1.5, edgecolor='#0077b6', facecolor='#caf0f8', alpha=0.45, zorder=4)
    ax3.add_patch(ball_yz)
    ax3.plot([0], [18.30], marker='+', markersize=10, color='#03045e', mew=1.5, zorder=5)
    ax3.plot([-13, 13], [18.30, 18.30], linestyle=':', color='#0077b6', lw=1.2, zorder=4)

    ax3.annotate('South Side (270°): No Claw (爪なし)\n• Uniform rim height: Z = +14.00 mm\n• Entire cup is below Equator (Z = +18.30 mm)\n• Low-rim cutout NOT needed (低リム不要)',
                 xy=(-13.0, 14.0), xytext=(-24.5, 20.0),
                 arrowprops=dict(facecolor='#1d3557', shrink=0.05, width=1.0, headwidth=4),
                 fontsize=7.5, fontweight='bold', color='#1d3557',
                 bbox=dict(boxstyle="round,pad=0.25", fc="#e0f2fe", ec="#1d3557", lw=0.8), zorder=10)

    ax3.annotate('', xy=(-17.0, 14.0), xytext=(-17.0, 0.0),
                 arrowprops=dict(arrowstyle='<->', color='#1d3557', lw=1.0))
    ax3.text(-17.4, 7.0, "Uniform Rim:\n14.00 mm", ha='right', va='center', fontsize=7.5, fontweight='bold', color='#1d3557',
             bbox=dict(boxstyle="round,pad=0.15", fc="#ffffff", ec="#1d3557", lw=0.6, alpha=0.9))

    ax3.annotate('', xy=(-11.3, -3.2), xytext=(11.3, -3.2),
                 arrowprops=dict(arrowstyle='<->', color='#1d3557', lw=1.2))
    ax3.text(0, -3.6, "Ear Pitch Y: 22.60 mm", ha='center', va='top', fontsize=8.5, fontweight='bold', color='#1d3557')

    ax3.text(-11.3, 2.5, "South Ear\n(2.0mm)", ha='center', va='bottom', fontsize=7.0, fontweight='bold', color='#1d3557')
    ax3.text(11.3, 2.5, "North Ear\n(2.0mm)", ha='center', va='bottom', fontsize=7.0, fontweight='bold', color='#1d3557')

    ax3.set_title("3. Longitudinal Elevation (Y-Z View)\n[側面立面図: 南側爪なし vs 北側保持爪]", fontsize=11, fontweight='bold', pad=12)
    ax3.axis('off')

    plt.tight_layout()
    out_file = ASSETS_DIR / "trackball_cup_detail_drawing.png"
    plt.savefig(out_file, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_file}")


def generate_assembly_tool_clearance_diagram():
    """
    Generate visual assembly tool-size limit & internal routing guide
    (`docs/assets/assembly_tool_clearance_guide.png`):
      - Panel 1: TB1 / TB3 brass insert heat-set — soldering iron diameter <= Ø 6.0 mm (max Ø 6.5 mm) up to 18 mm from tip
      - Panel 2: TB1..TB4 cup screws — #0 precision screwdriver shaft <= Ø 4.5 mm (rec. Ø 3.0-3.5 mm) up to 15 mm from tip
      - Panel 3: Pre-closure checklist — tune DET magnetic ratchet screw before fastening R1..R6 + route 100 mm JST-SH slack SE
    """
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(21.5, 8.2), dpi=200)
    fig.patch.set_facecolor('#ffffff')
    fig.suptitle(
        "curcur40 組み立て時の干渉ポイントと「ここはこのサイズ以下を使ってね」工具・配線ガイド",
        fontsize=15.0, fontweight='bold', color='#1e293b', y=0.98
    )

    # =========================================================================
    # PANEL 1: TB1 / TB3 Heat-Set Insert — Soldering Iron Tip/Collar Clearance
    # True 1:1 scale in mm around TB1/TB3 bore center (X = 0)
    # =========================================================================
    ax1.set_facecolor('#f8fafc')
    ax1.set_xlim(-10.5, 16.5)
    ax1.set_ylim(-23.5, 10.5)
    ax1.set_aspect('equal')

    # Case West Wall (inner face at X = -3.2875, outer face at X = -4.7875, top rim Z = 0.00) + Boss (OD Ø6.0, top Z = -17.60)
    case_p1 = patches.Polygon(
        [
            (-4.79, -23.0), (14.5, -23.0), (14.5, -20.6),
            (3.00, -20.6), (3.00, -17.60),
            (1.425, -17.60), (1.425, -21.40), (-1.425, -21.40), (-1.425, -17.60),
            (-3.29, -17.60), (-3.29, 0.00), (-4.79, 0.00),
        ],
        closed=True, lw=1.5, ec='#334155', fc='#cbd5e1', zorder=2
    )
    ax1.add_patch(case_p1)
    ax1.text(5.2, -21.8, "右手ケース下段 (PA12・底面密閉)", ha='center', va='center', fontsize=8.0, fontweight='bold', color='#1e293b', zorder=3)
    ax1.text(-4.04, -9.0, "ケース西壁", rotation=90, ha='center', va='center', fontsize=8.0, fontweight='bold', color='#334155', zorder=3)

    # Brass insert at Z = -20.60..-17.60
    ax1.add_patch(patches.Rectangle((-1.60, -20.60), 0.55, 3.00, lw=1.0, ec='#7f5539', fc='#eab308', zorder=4))
    ax1.add_patch(patches.Rectangle((1.05, -20.60), 0.55, 3.00, lw=1.0, ec='#7f5539', fc='#eab308', zorder=4))

    # NG Ghost: Wide soldering-iron sleeve (Ø 8.2 mm -> X = ±4.10 starting 11 mm above tip -> Z = -6.60) hitting West Wall X = -3.29!
    ng_sleeve = patches.Rectangle((-4.10, -6.60), 8.20, 12.0, lw=1.8, ls='--', ec='#dc2626', fc='#fecaca', alpha=0.55, zorder=3)
    ax1.add_patch(ng_sleeve)
    ax1.plot([-3.29], [0.00], marker='X', markersize=11, color='#dc2626', mec='#ffffff', mew=1.2, zorder=8)
    ax1.annotate(
        "× NG例: 太い保護管 (Ø7〜10mm)\n西壁上フチ (Z=0) に当たって\n斜めになる・フチを溶かす!",
        xy=(-3.29, 0.00), xytext=(3.8, 3.2),
        arrowprops=dict(arrowstyle='->', color='#dc2626', lw=1.5),
        fontsize=7.8, fontweight='bold', color='#991b1b',
        bbox=dict(boxstyle="round,pad=0.28", fc="#fef2f2", ec="#dc2626", lw=1.1), zorder=9
    )

    # OK Slim Iron Tip + Shaft (Tip enters insert at Z = -18.2, conical to Ø 5.2 mm at Z = -11.0, slim Ø 5.2 mm shaft past Z = +5.0)
    ok_iron = patches.Polygon(
        [
            (-0.75, -18.3), (0.75, -18.3),
            (2.60, -11.0), (2.60, 4.8),
            (-2.60, 4.8), (-2.60, -11.0),
        ],
        closed=True, lw=1.6, ec='#15803d', fc='#bbf7d0', alpha=0.92, zorder=5
    )
    ax1.add_patch(ok_iron)
    ax1.axvline(0.0, ls='-.', color='#64748b', lw=0.9, zorder=6)
    ax1.text(0.0, -5.5, "OK 細軸こて先\n(例: Ø5.0〜5.5mm)", rotation=90, ha='center', va='center', fontsize=8.0, fontweight='bold', color='#14532d', zorder=7)

    # Dimension: Depth 17.6 mm (Z = 0.0 to -17.6)
    ax1.plot([-3.29, -9.2], [0.00, 0.00], ls=':', color='#0f172a', lw=1.0)
    ax1.plot([-1.60, -9.2], [-17.60, -17.60], ls=':', color='#0f172a', lw=1.0)
    ax1.annotate('', xy=(-8.2, 0.00), xytext=(-8.2, -17.60), arrowprops=dict(arrowstyle='<->', color='#0f172a', lw=1.4))
    ax1.text(-8.5, -8.80, "深さ\n17.6 mm", ha='right', va='center', fontsize=8.5, fontweight='bold', color='#0f172a')

    # Dimension: Radial clearance 3.29 mm -> Max Ø 6.57 mm
    ax1.annotate('', xy=(-3.29, 1.3), xytext=(0.0, 1.3), arrowprops=dict(arrowstyle='<->', color='#0369a1', lw=1.4), zorder=9)
    ax1.text(-1.65, 2.1, "半径 3.29mm", ha='center', va='bottom', fontsize=7.6, fontweight='bold', color='#0369a1',
             bbox=dict(boxstyle="round,pad=0.15", fc="#ffffff", ec="#0369a1", lw=0.7, alpha=0.95), zorder=9)

    # Green Specification Callout
    ax1.text(
        9.4, -10.8,
        "◎ ここはこのサイズ以下!\n"
        "━━━━━━━━━━━━\n"
        "先端から 18 mm まで\n"
        "太さ Ø 6.0 mm 以下\n"
        "(物理限界: Ø 6.5 mm)\n\n"
        "・TS100 / Pinecil 等の\n"
        "  ペン型細軸こて (Ø5.5)\n"
        "・長めの円錐 B型/I型こて先",
        ha='center', va='center', fontsize=8.2, fontweight='bold', color='#14532d',
        bbox=dict(boxstyle="round,pad=0.4", fc="#dcfce7", ec="#16a34a", lw=1.6), zorder=9
    )

    ax1.set_title("① TB1 / TB3 インサート熱圧入\n【はんだごて先端の太さ制限】", fontsize=11.8, fontweight='bold', color='#0f172a', pad=10)
    ax1.axis('off')

    # =========================================================================
    # PANEL 2: TB1..TB4 Cup Screws — Precision #0 Screwdriver Shaft Diameter
    # True 1:1 scale in mm around TB1..TB4 screw axis (X = 0; Cup outer wall at X = -2.48)
    # =========================================================================
    ax2.set_facecolor('#f8fafc')
    ax2.set_xlim(-11.5, 15.5)
    ax2.set_ylim(-23.5, 10.5)
    ax2.set_aspect('equal')

    # Case TB Boss + Sensor PCB (1.6mm, Z=-17.6..-16.0) + Trackball Cup Wall (X <= -2.48, Z=-16.0..-2.0) & Flat Ear (Z=-16.0..-14.0)
    boss_p2 = patches.Polygon(
        [
            (-10.5, -23.0), (13.5, -23.0), (13.5, -20.6),
            (3.00, -20.6), (3.00, -17.60),
            (1.425, -17.60), (1.425, -21.40), (-1.425, -21.40), (-1.425, -17.60),
            (-3.00, -17.60), (-3.00, -20.6), (-10.5, -20.6),
        ],
        closed=True, lw=1.4, ec='#334155', fc='#cbd5e1', zorder=2
    )
    ax2.add_patch(boss_p2)
    ax2.add_patch(patches.Rectangle((-1.60, -20.60), 0.55, 3.00, lw=1.0, ec='#7f5539', fc='#eab308', zorder=4))
    ax2.add_patch(patches.Rectangle((1.05, -20.60), 0.55, 3.00, lw=1.0, ec='#7f5539', fc='#eab308', zorder=4))

    # Sensor PCB
    ax2.add_patch(patches.Rectangle((-10.5, -17.60), 9.30, 1.60, lw=1.2, ec='#14532d', fc='#4ade80', alpha=0.85, zorder=3))
    ax2.add_patch(patches.Rectangle((1.20, -17.60), 4.80, 1.60, lw=1.2, ec='#14532d', fc='#4ade80', alpha=0.85, zorder=3))
    ax2.text(-6.2, -16.80, "TBセンサー基板", ha='center', va='center', fontsize=7.2, fontweight='bold', color='#052e16', zorder=4)

    # Trackball Cup Body Wall (X in [-10.5, -2.48], Z in [-16.00, -2.00]) + 2.00 mm Flat Ear (X in [-2.48, +3.00], Z in [-16.00, -14.00])
    cup_p2 = patches.Polygon(
        [
            (-10.5, -16.00), (-1.20, -16.00), (-1.20, -14.00),
            (-2.48, -14.00), (-2.48, -2.00), (-10.5, -2.00),
        ],
        closed=True, lw=1.5, ec='#1e3a8a', fc='#93c5fd', alpha=0.88, zorder=4
    )
    ear_r_p2 = patches.Rectangle((1.20, -16.00), 1.80, 2.00, lw=1.5, ec='#1e3a8a', fc='#93c5fd', alpha=0.88, zorder=4)
    ax2.add_patch(cup_p2)
    ax2.add_patch(ear_r_p2)
    ax2.text(-6.5, -8.5, "トラックボール\nカップ外壁\n(Ø28.0 mm)", ha='center', va='center', fontsize=8.2, fontweight='bold', color='#1e3a8a', zorder=5)

    # M2 x 6.0mm Screw
    ax2.add_patch(patches.Rectangle((-1.90, -14.00), 3.80, 1.20, lw=1.3, ec='#1e293b', fc='#64748b', zorder=6))
    ax2.add_patch(patches.Rectangle((-0.98, -20.00), 1.96, 6.00, lw=1.3, ec='#1e293b', fc='#94a3b8', zorder=5))

    # NG Ghost: Thick 4mm/6.35mm bit-holder chuck (Ø 8.0 mm -> X = ±4.00 above Z = -6.0) hitting Cup Outer Wall at (-2.48, -2.00)
    ng_chuck = patches.Rectangle((-4.00, -6.00), 8.00, 9.50, lw=1.8, ls='--', ec='#dc2626', fc='#fecaca', alpha=0.55, zorder=3)
    ax2.add_patch(ng_chuck)
    ax2.plot([-2.48], [-2.00], marker='X', markersize=11, color='#dc2626', mec='#ffffff', mew=1.2, zorder=8)
    ax2.annotate(
        "× NG例: 差替ビットホルダー\n太いチャック (Ø6.5〜10mm) が\nカップ外壁に当たって届かない!",
        xy=(-2.48, -2.00), xytext=(4.0, 3.2),
        arrowprops=dict(arrowstyle='->', color='#dc2626', lw=1.5),
        fontsize=7.6, fontweight='bold', color='#991b1b',
        bbox=dict(boxstyle="round,pad=0.26", fc="#fef2f2", ec="#dc2626", lw=1.1), zorder=9
    )

    # OK Slim #0 Precision Screwdriver Shaft (Ø 3.0 mm -> X = ±1.50 from Z = -12.80 up to +4.20, handle above Z = +4.20)
    ok_shaft = patches.Rectangle((-1.50, -12.80), 3.00, 17.00, lw=1.6, ec='#15803d', fc='#bbf7d0', alpha=0.95, zorder=7)
    ok_handle = patches.FancyBboxPatch((-3.40, 4.20), 6.80, 4.60, boxstyle="round,pad=0,rounding_size=1.0", lw=1.5, ec='#15803d', fc='#86efac', zorder=7)
    ax2.add_patch(ok_shaft)
    ax2.add_patch(ok_handle)
    ax2.axvline(0.0, ls='-.', color='#64748b', lw=0.9, zorder=8)
    ax2.text(0.0, 6.50, "精密 #0 グリップ", ha='center', va='center', fontsize=7.6, fontweight='bold', color='#14532d', zorder=8)
    ax2.text(0.0, -5.8, "細軸 Ø3.0mm", rotation=90, ha='center', va='center', fontsize=7.6, fontweight='bold', color='#14532d', zorder=8)

    # Dimensions: 12.0 mm height & 2.48 mm radial gap (Ø 4.97 mm physical max)
    ax2.annotate('', xy=(-2.48, -0.8), xytext=(0.0, -0.8), arrowprops=dict(arrowstyle='<->', color='#0369a1', lw=1.4), zorder=9)
    ax2.text(-1.24, 0.0, "半径 2.48mm", ha='center', va='bottom', fontsize=7.5, fontweight='bold', color='#0369a1',
             bbox=dict(boxstyle="round,pad=0.15", fc="#ffffff", ec="#0369a1", lw=0.7, alpha=0.95), zorder=9)

    ax2.plot([1.90, 4.8], [-14.00, -14.00], ls=':', color='#0f172a', lw=1.0)
    ax2.plot([-2.48, 4.8], [-2.00, -2.00], ls=':', color='#0f172a', lw=1.0)
    ax2.annotate('', xy=(3.8, -2.00), xytext=(3.8, -14.00), arrowprops=dict(arrowstyle='<->', color='#0f172a', lw=1.3))
    ax2.text(4.1, -8.00, "12.0 mm", ha='left', va='center', fontsize=8.0, fontweight='bold', color='#0f172a')

    ax2.text(
        9.4, -13.2,
        "◎ ここはこのサイズ以下!\n"
        "━━━━━━━━━━━━\n"
        "先端から 15 mm まで\n"
        "軸径 Ø 4.5 mm 以下\n"
        "(推奨: Ø 3.0〜3.5 mm)\n\n"
        "・単体の精密プラス\n"
        "  ドライバー (#0 / #00)\n"
        "  (差替チャック式は不可)",
        ha='center', va='center', fontsize=8.2, fontweight='bold', color='#14532d',
        bbox=dict(boxstyle="round,pad=0.4", fc="#dcfce7", ec="#16a34a", lw=1.6), zorder=9
    )

    ax2.set_title("② TB1〜TB4 カップ固定ネジ締め\n【精密ドライバー軸の太さ制限】", fontsize=11.8, fontweight='bold', color='#0f172a', pad=10)
    ax2.axis('off')

    # =========================================================================
    # PANEL 3: Pre-Closure Checklist — (A) DET Screw Timing & (B) 100mm Cable Slack
    # =========================================================================
    ax3.set_facecolor('#f8fafc')
    ax3.set_xlim(0, 100)
    ax3.set_ylim(0, 100)

    # --- Top Card (A): DET Ratchet Adjuster Screw Timing ---
    card_a = patches.FancyBboxPatch((3, 52), 94, 44, boxstyle="round,pad=0,rounding_size=3.0", lw=1.4, ec='#475569', fc='#ffffff', zorder=1)
    ax3.add_patch(card_a)
    ax3.text(50, 92, "③-A ホイールノッチ調整ネジ (DET) は「基板を閉じる前」に調整!", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#0f172a', zorder=2)

    # Mini schematic inside Card A
    ax3.add_patch(patches.Rectangle((8, 78), 52, 4.0, lw=1.2, ec='#1e3a8a', fc='#60a5fa', zorder=3))
    ax3.text(34, 80, "右メイン基板 + トッププレート (R1〜R6 で蓋)", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#ffffff', zorder=4)
    ax3.add_patch(patches.Circle((22, 71), 8.5, lw=1.4, ec='#334155', fc='#94a3b8', zorder=2))
    ax3.text(22, 71, "#01\nホイール", ha='center', va='center', fontsize=7.0, fontweight='bold', color='#ffffff', zorder=3)
    ax3.add_patch(patches.Rectangle((33, 62), 14, 11, lw=1.2, ec='#475569', fc='#cbd5e1', zorder=3))
    ax3.text(40, 69.5, "#03 南ボス", ha='center', va='center', fontsize=6.8, fontweight='bold', color='#1e293b', zorder=4)
    # DET screw + magnet
    ax3.add_patch(patches.Rectangle((31.2, 64.5), 2.5, 2.5, lw=1.0, ec='#b91c1c', fc='#ef4444', zorder=4))
    ax3.add_patch(patches.Rectangle((33.7, 64.8), 16.5, 1.9, lw=1.1, ec='#1e293b', fc='#64748b', zorder=4))
    ax3.text(52, 65.7, "← DET 調整ネジ (基板の下 Z=-11.3mm)", ha='left', va='center', fontsize=7.5, fontweight='bold', color='#b91c1c', zorder=4)

    ax3.text(
        50, 56.8,
        "◎ Phase 4〜5（R1〜R6 ネジ6本でケースへ本締めする前）に好みのノッチ強弱へ調整!\n"
        "   ※組んだ後に再調整したい時は、R1〜R6 を外して右基板を持ち上げれば回せます。",
        ha='center', va='center', fontsize=7.7, fontweight='bold', color='#14532d',
        bbox=dict(boxstyle="round,pad=0.28", fc="#dcfce7", ec="#16a34a", lw=1.2), zorder=5
    )

    # --- Bottom Card (B): 100mm JST-SH Cable Slack Routing ---
    card_b = patches.FancyBboxPatch((3, 3), 94, 45, boxstyle="round,pad=0,rounding_size=3.0", lw=1.4, ec='#475569', fc='#ffffff', zorder=1)
    ax3.add_patch(card_b)
    ax3.text(50, 44, "③-B 100mm JST-SH ケーブルの余長は「南東 (rSW8/rSW9 下)」へ逃がす!", ha='center', va='center', fontsize=9.3, fontweight='bold', color='#0f172a', zorder=2)

    # Mini top-view map inside Card B
    # North wheel danger zone
    ax3.add_patch(patches.FancyBboxPatch((8, 28), 32, 11, boxstyle="round,pad=0,rounding_size=2.0", lw=1.3, ls='--', ec='#dc2626', fc='#fef2f2', zorder=2))
    ax3.text(24, 33.5, "× 北側: #01 回転ホイール\n(余長ループを近づけない!)", ha='center', va='center', fontsize=7.3, fontweight='bold', color='#991b1b', zorder=3)

    # J1 (West) & rJ3 (Center)
    ax3.add_patch(patches.Rectangle((10, 12), 16, 11, lw=1.2, ec='#14532d', fc='#bbf7d0', zorder=3))
    ax3.text(18, 17.5, "TB基板\nJ1 (東向)", ha='center', va='center', fontsize=7.2, fontweight='bold', color='#052e16', zorder=4)

    ax3.add_patch(patches.Rectangle((36, 10), 16, 11, lw=1.2, ec='#1e3a8a', fc='#bfdbfe', zorder=3))
    ax3.text(44, 15.5, "右メイン\nrJ3 (西向)", ha='center', va='center', fontsize=7.2, fontweight='bold', color='#1e3a8a', zorder=4)

    # South-East Safe Slack Zone
    ax3.add_patch(patches.FancyBboxPatch((56, 6), 37, 34, boxstyle="round,pad=0,rounding_size=2.5", lw=1.5, ec='#16a34a', fc='#dcfce7', zorder=2))
    ax3.text(74.5, 34.5, "◎ 南東: 安全逃がし空間\n(rSW8 / rSW9 の真下)", ha='center', va='center', fontsize=7.8, fontweight='bold', color='#14532d', zorder=4)
    ax3.text(74.5, 11.2, "余長ループをここへ寄せ\nカプトンテープ等で軽く留める!", ha='center', va='center', fontsize=7.4, fontweight='bold', color='#166534',
             bbox=dict(boxstyle="round,pad=0.22", fc="#f0fdf4", ec="#16a34a", lw=0.8), zorder=8)

    # Green curved 100mm cable path looping into SE safe zone, plus red dashed NG path going North
    ax3.plot([26, 28.5, 25], [19.5, 24.5, 28.5], ls='--', lw=2.0, color='#dc2626', zorder=5)
    cx_path = [26.0, 31.0, 44.0, 62.0, 84.0, 87.5, 84.0, 60.0, 53.5, 43.0, 32.5, 32.5, 36.0]
    cy_path = [17.5, 22.8, 24.8, 26.5, 26.5, 23.0, 19.5, 19.0,  6.8,  6.8,  8.5, 15.5, 15.5]
    ax3.plot(cx_path, cy_path, lw=2.6, color='#15803d', solid_capstyle='round', solid_joinstyle='round', zorder=6)
    ax3.add_patch(patches.Rectangle((69, 24.0), 7.8, 5.0, lw=1.0, ec='#b45309', fc='#fde047', alpha=0.92, zorder=7))
    ax3.text(72.9, 26.5, "テープ", ha='center', va='center', fontsize=6.3, fontweight='bold', color='#78350f', zorder=8)

    ax3.set_title("③ ケース本締め前の確認ポイント\n【DET ノッチ調整 ＆ 100mm ケーブル配線】", fontsize=11.8, fontweight='bold', color='#0f172a', pad=10)
    ax3.axis('off')

    plt.tight_layout(rect=[0, 0, 1, 0.94])
    out_file = ASSETS_DIR / "assembly_tool_clearance_guide.png"
    plt.savefig(out_file, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_file}")


if __name__ == "__main__":
    generate_vertical_stackup_diagram()
    generate_ports_and_screws_diagram()
    generate_trackball_optical_diagram()
    generate_trackball_cup_fastening_diagram()
    generate_trackball_cup_detail_drawing()
    generate_assembly_tool_clearance_diagram()
    print("All specification diagram images updated successfully!")
