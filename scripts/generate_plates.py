# -*- coding: utf-8 -*-
"""
Generate curcur40 Plates (KiCad PCBs and laser-cut SVGs) according to docs/case_spec.md.
Note: Gerber ZIP generation is omitted by default per user workflow (only generated on demand).
"""
import os
import math
import subprocess
from pathlib import Path
import pcbnew

WORKSPACE = Path(__file__).resolve().parent.parent
KICAD_CLI = os.path.expandvars(r"%LOCALAPPDATA%\Programs\KiCad\10.0\bin\kicad-cli.exe")

# Left key-valley holes (Switch-Retained Top Plate 1A — 6-point outer-margin-free layout):
#   - All 6 holes L1..L6 (Ø 4.40 mm -> r = 2.20 mm): sub-flush screw-head clearance holes
#     (M2 x 6.0 mm screws clamp Left Main PCB F.Cu Z = -4.20 mm directly into Ø 5.20 mm flat case bosses; screw head top Z = -3.00 mm sits 1.00 mm below Top Plate top Z = -2.00 mm)
LEFT_MOUNTING_HOLES = [
    ( -42.2500,  -4.5000, 2.20),  # L1: Index North 4-key valley (SW3/4/5/6)
    (-100.5000,   0.5000, 2.20),  # L2: Pinky North 4-key valley (SW13/14/17/18)
    (-100.5000,  19.5000, 2.20),  # L3: Pinky South 4-key valley (SW14/15/16/17)
    ( -42.2500,  14.5000, 2.20),  # L4: Index South 4-key valley (SW2/3/6/7)
    ( -27.0000,  58.8000, 2.20),  # L5: Inner Thumb valley between SW1 & EXSW3
    ( -60.5000,  35.0000, 2.20),  # L6: Outer Thumb valley (North of SW8/SW9)
]

# Right key-valley holes (Switch-Retained Top Plate 1A — R1..R4, R6 symmetric with Left; R5 on SW thumb peninsula):
#   - All 6 holes R1..R6 (Ø 4.40 mm -> r = 2.20 mm): sub-flush screw-head clearance holes
RIGHT_MOUNTING_HOLES = [
    (  42.2500,  -4.5000, 2.20),  # R1: Index North 4-key valley (rSW3/4/5/6)
    ( 100.5000,   0.5000, 2.20),  # R2: Pinky North 4-key valley (rSW13/14/17/18)
    ( 100.5000,  19.5000, 2.20),  # R3: Pinky South 4-key valley (rSW14/15/16/17)
    (  42.2500,  14.5000, 2.20),  # R4: Index South 4-key valley (rSW2/3/6/7)
    (   9.4500,  58.5000, 2.20),  # R5: Inner Thumb South-West peninsula (centered in [4.7625, 14.1500])
    (  60.5000,  35.0000, 2.20),  # R6: Outer Thumb valley (North of rSW8/rSW9)
]

LEFT_SWITCHES = [
    # Main 3x5
    (-109.5375,  -9.52500),  # SW18 (0,1)
    (-109.5375,   9.52500),  # SW17 (1,1)
    (-109.5375,  28.57500),  # SW16 (2,1)
    ( -90.4875, -11.90625),  # SW13 (0,2)
    ( -90.4875,   7.14375),  # SW14 (1,2)
    ( -90.4875,  26.19375),  # SW15 (2,2)
    ( -71.4375, -14.28750),  # SW12 (0,3)
    ( -71.4375,   4.76250),  # SW11 (1,3)
    ( -71.4375,  23.81250),  # SW10 (2,3)
    ( -52.3875, -14.28750),  # SW5  (0,4)
    ( -52.3875,   4.76250),  # SW6  (1,4)
    ( -52.3875,  23.81250),  # SW7  (2,4)
    ( -33.3375, -14.28750),  # SW4  (0,5)
    ( -33.3375,   4.76250),  # SW3  (1,5)
    ( -33.3375,  23.81250),  # SW2  (2,5)
    # Inner 2 keys
    ( -14.2875,   4.76250),  # EXSW1 (0,6)
    ( -14.2875,  23.81250),  # EXSW2 (1,6)
    # Thumb 4 keys
    ( -71.4375,  42.86250),  # SW9   (3,3)
    ( -52.3875,  47.62500),  # SW8   (3,4)
    ( -33.3375,  47.62500),  # SW1   (3,5)
    ( -14.2875,  52.42500),  # EXSW3 (3,6) — shifted +4.80 mm South to clear inner-wall Split USB-C J2
]

RIGHT_SWITCHES = [
    # Main 3x5
    ( 109.5375,  -9.52500),  # rSW18 (4,1)
    ( 109.5375,   9.52500),  # rSW17 (5,1)
    ( 109.5375,  28.57500),  # rSW16 (6,1)
    (  90.4875, -11.90625),  # rSW13 (4,2)
    (  90.4875,   7.14375),  # rSW14 (5,2)
    (  90.4875,  26.19375),  # rSW15 (6,2)
    (  71.4375, -14.28750),  # rSW12 (4,3)
    (  71.4375,   4.76250),  # rSW11 (5,3)
    (  71.4375,  23.81250),  # rSW10 (6,3)
    (  52.3875, -14.28750),  # rSW5  (4,4)
    (  52.3875,   4.76250),  # rSW6  (5,4)
    (  52.3875,  23.81250),  # rSW7  (6,4)
    (  33.3375, -14.28750),  # rSW4  (4,5)
    (  33.3375,   4.76250),  # rSW3  (5,5)
    (  33.3375,  23.81250),  # rSW2  (6,5)
    # Inner 1u key
    (  14.2875,  23.81250),  # rEXSW2 (5,6)
    # Thumb 2 keys (rSW1 removed to accommodate inward-shifted trackball at (28.5750, 47.6250))
    (  52.3875,  47.62500),  # rSW8  (7,4)
    (  71.4375,  42.86250),  # rSW9  (7,3)
]

# Right Under-Plate Inertia Wheel 2-point cradle screw-head clearance holes (WC1: Ø 4.05 mm -> r=2.025 mm for 0.75 mm West FR-4 web; WC2: Ø 4.40 mm -> r=2.20 mm)
RIGHT_WHEEL_HOLES = [
    ( 7.3375, -5.0375, 2.025),
    (21.2375, 10.7625, 2.20),
]

RIGHT_INERTIA_WHEEL = (14.2875, 2.76250)  # Under-Plate Passive Magnetic Inertia Wheel axle center (aligned with rEXSW2 x=14.2875)
RIGHT_TRACKBALL_CIRCLE = (28.5750, 47.6250, 14.3125)  # Closed Ø 28.625 mm circular cutout (0.3125 mm uniform gap to Ø 28.00 mm cup, 1.0000 mm solid South FR-4 web)


def round_polygon_with_fillets(pts_and_radii):
    n = len(pts_and_radii)
    prims = []
    tangents = []
    for i in range(n):
        x_prev, y_prev, _ = pts_and_radii[(i - 1) % n]
        x, y, r = pts_and_radii[i]
        x_next, y_next, _ = pts_and_radii[(i + 1) % n]
        if r <= 0:
            tangents.append(((round(x, 6), round(y, 6)), None, (round(x, 6), round(y, 6))))
            continue
        dx1, dy1 = x_prev - x, y_prev - y
        l1 = math.hypot(dx1, dy1)
        u1x, u1y = dx1 / l1, dy1 / l1
        dx2, dy2 = x_next - x, y_next - y
        l2 = math.hypot(dx2, dy2)
        u2x, u2y = dx2 / l2, dy2 / l2
        p_in = (round(x + u1x * r, 6), round(y + u1y * r, 6))
        p_out = (round(x + u2x * r, 6), round(y + u2y * r, 6))
        cx = x + (u1x + u2x) * r
        cy = y + (u1y + u2y) * r
        s2 = math.sqrt(0.5)
        pm = (round(cx - (u1x + u2x) * s2 * r, 6), round(cy - (u1y + u2y) * s2 * r, 6))
        tangents.append((p_in, pm, p_out))

    for i in range(n):
        p_in, pm, p_out = tangents[i]
        if pm is not None:
            prims.append(('arc', p_in, pm, p_out))
        next_in, _, _ = tangents[(i + 1) % n]
        if math.hypot(p_out[0] - next_in[0], p_out[1] - next_in[1]) > 1e-5:
            prims.append(('line', p_out, next_in))
    return prims


def make_rect_cutout(cx, cy, w, h, r=0.5):
    x1, x2 = cx - w / 2.0, cx + w / 2.0
    y1, y2 = cy - h / 2.0, cy + h / 2.0
    pts = [
        (x1, y1, r),
        (x2, y1, r),
        (x2, y2, r),
        (x1, y2, r),
    ]
    return round_polygon_with_fillets(pts)


def make_inertia_wheel_top_cutout(cx, cy):
    """
    Clean rounded-rectangle Top Plate slot (6.55 x 22.00 mm, R = 1.00 mm, centered on wheel rim cx - 0.9250 = 13.3625 mm,
    x_pcb in [10.0875, 16.6375] / u in [-4.2000, +2.3500]) for the Ø 22.00 x 4.65 mm (`u in [-3.25, +1.40]`) wheel:
      - Symmetric 0.95 mm West / 0.95 mm East rest clearance (hiding East shaft & bearing shoulder)
      - >= 0.30 mm West clearance even at full 2.95 deg middle-click tilt!
    """
    return make_rect_cutout(cx - 0.9250, cy, 6.55, 22.00, 1.00)


def make_inertia_wheel_foam_cutout():
    """Cross-shaped switch-foam cutout matching the East-reversed Right Main PCB wheel & bearing/magnet opening."""
    pts = [
        (10.1875, -8.7375, 0.50),
        (18.1375, -8.7375, 0.50),
        (18.1375, -0.9875, 0.50),
        (23.6475, -0.9875, 0.50),
        (23.6475,  6.5125, 0.50),
        (18.1375,  6.5125, 0.50),
        (18.1375, 14.2625, 0.50),
        (10.1875, 14.2625, 0.50),
        (10.1875,  6.5125, 0.50),
        ( 6.9375,  6.5125, 0.50),
        ( 6.9375, -0.9875, 0.50),
        (10.1875, -0.9875, 0.50),
    ]
    return round_polygon_with_fillets(pts)


def get_left_outer_pts():
    return [
        (-119.2625, -27.86250, 1.0),  # Top-left (-0.20 mm from Main PCB y=-27.6625)
        (  -4.5625, -27.86250, 1.0),  # Top-right (+0.20 mm from Main PCB x=-4.7625, -10.025 mm narrower!)
        (  -4.5625,  62.93750, 1.0),  # Bottom-right
        ( -82.6625,  62.93750, 1.0),  # Thumb bottom-left
        ( -82.6625,  38.80000, 1.0),  # Pinky step inner
        (-119.2625,  38.80000, 1.0),  # Pinky-left bottom
    ]


def get_right_outer_pts(notched_trackball=False):
    if not notched_trackball:
        return [
            (  4.5625, -27.86250, 1.0),  # Top-left
            (119.2625, -27.86250, 1.0),  # Top-right
            (119.2625,  38.80000, 1.0),  # Pinky-right bottom
            ( 82.6625,  38.80000, 1.0),  # Pinky step inner
            ( 82.6625,  62.93750, 1.0),  # Thumb bottom-right
            (  4.5625,  62.93750, 1.0),  # Bottom-left
        ]
    else:
        return [
            (  4.5625, -27.86250, 1.0),  # Top-left (-0.20 mm from Main PCB x=+4.7625, -10.025 mm narrower!)
            (119.2625, -27.86250, 1.0),  # Top-right
            (119.2625,  38.80000, 1.0),  # Pinky-right bottom
            ( 82.6625,  38.80000, 1.0),  # Pinky step inner
            ( 82.6625,  62.93750, 1.0),  # Thumb bottom-right
            ( 43.2000,  62.93750, 1.0),  # U-notch bottom-east
            ( 43.2000,  32.75000, 0.8),  # U-notch top-east
            ( 13.9500,  32.75000, 0.8),  # U-notch top-west
            ( 13.9500,  62.93750, 1.0),  # U-notch bottom-west
            (  4.5625,  62.93750, 1.0),  # Bottom-left
        ]


def add_prim(board, prim):
    sh = pcbnew.PCB_SHAPE(board)
    sh.SetLayer(pcbnew.Edge_Cuts)
    sh.SetWidth(pcbnew.FromMM(0.15))
    if prim[0] == 'line':
        _, (x1, y1), (x2, y2) = prim
        sh.SetShape(pcbnew.SHAPE_T_SEGMENT)
        sh.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
        sh.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
    elif prim[0] == 'arc':
        _, (x1, y1), (xm, ym), (x2, y2) = prim
        sh.SetShape(pcbnew.SHAPE_T_ARC)
        sh.SetArcGeometry(
            pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)),
            pcbnew.VECTOR2I(pcbnew.FromMM(xm), pcbnew.FromMM(ym)),
            pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2))
        )
    board.Add(sh)


def write_plate_kicad_pcb(filepath, outer_prims, cutout_prims_list, circles):
    b = pcbnew.BOARD()
    for prim in outer_prims:
        add_prim(b, prim)
    for c_prims in cutout_prims_list:
        for prim in c_prims:
            add_prim(b, prim)
    for (cx, cy, r) in circles:
        c = pcbnew.PCB_SHAPE(b)
        c.SetShape(pcbnew.SHAPE_T_CIRCLE)
        c.SetLayer(pcbnew.Edge_Cuts)
        c.SetCenter(pcbnew.VECTOR2I(pcbnew.FromMM(cx), pcbnew.FromMM(cy)))
        c.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(cx + r), pcbnew.FromMM(cy)))
        c.SetWidth(pcbnew.FromMM(0.15))
        b.Add(c)
    b.Save(filepath)


def prims_to_svg_path(prims, ox, oy):
    d = []
    for i, prim in enumerate(prims):
        if prim[0] == 'line':
            _, (x1, y1), (x2, y2) = prim
            if i == 0:
                d.append(f"M {x1 + ox:.4f} {y1 + oy:.4f}")
            d.append(f"L {x2 + ox:.4f} {y2 + oy:.4f}")
        elif prim[0] == 'arc':
            _, (x1, y1), (xm, ym), (x2, y2) = prim
            if i == 0:
                d.append(f"M {x1 + ox:.4f} {y1 + oy:.4f}")
            r = math.hypot(x2 - x1, y2 - y1) * math.sqrt(0.5)
            cross = (xm - x1) * (y2 - y1) - (ym - y1) * (x2 - x1)
            sweep = 1 if cross < 0 else 0
            d.append(f"A {r:.4f} {r:.4f} 0 0 {sweep} {x2 + ox:.4f} {y2 + oy:.4f}")
    d.append("Z")
    return " ".join(d)


def circle_to_svg_path(cx, cy, r, ox, oy):
    x = cx + ox
    y = cy + oy
    return f"M {x - r:.4f} {y:.4f} A {r:.4f} {r:.4f} 0 1 0 {x + r:.4f} {y:.4f} A {r:.4f} {r:.4f} 0 1 0 {x - r:.4f} {y:.4f} Z"


def write_laser_svg(svg_path, items, width_mm, height_mm):
    outer_paths = []
    inner_paths = []
    for (outer_prims, cutouts_list, holes, ox, oy) in items:
        outer_paths.append(prims_to_svg_path(outer_prims, ox, oy))
        for c_prims in cutouts_list:
            inner_paths.append(prims_to_svg_path(c_prims, ox, oy))
        for (cx, cy, r) in holes:
            inner_paths.append(circle_to_svg_path(cx, cy, r, ox, oy))

    svg_lines = [
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
        f'<svg version="1.1" width="{width_mm}mm" height="{height_mm}mm" viewBox="0 0 {width_mm} {height_mm}" xmlns="http://www.w3.org/2000/svg">',
        '  <g id="CUT2" style="fill:none;stroke:#0000ff;stroke-width:0.05">',
    ]
    for p in outer_paths:
        svg_lines.append(f'    <path d="{p}" />')
    svg_lines.append('  </g>')
    svg_lines.append('  <g id="CUT1" style="fill:none;stroke:#ff0000;stroke-width:0.05">')
    for p in inner_paths:
        svg_lines.append(f'    <path d="{p}" />')
    svg_lines.append('  </g>')
    svg_lines.append('</svg>')
    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg_lines))


def main():
    import tempfile

    out_pcb_dir = str(WORKSPACE / "plates" / "pcb")
    out_svg_dir = str(WORKSPACE / "plates" / "svg")
    os.makedirs(out_pcb_dir, exist_ok=True)
    os.makedirs(out_svg_dir, exist_ok=True)

    # 1. Left Top Plate
    left_outer = round_polygon_with_fillets(get_left_outer_pts())
    left_cutouts = [make_rect_cutout(cx, cy, 14.0, 14.0, 0.5) for (cx, cy) in LEFT_SWITCHES]
    p_top_left = os.path.join(out_pcb_dir, "plate-top-left.kicad_pcb")
    write_plate_kicad_pcb(p_top_left, left_outer, left_cutouts, LEFT_MOUNTING_HOLES)

    # 2. Right Top Plate (closed Ø 28.625 mm circular trackball cutout + 7.70 x 22.00 mm wheel slot + 8x Ø 4.40 mm screw-head clearance holes)
    right_outer = round_polygon_with_fillets(get_right_outer_pts(notched_trackball=False))
    right_switch_cutouts = [make_rect_cutout(cx, cy, 14.0, 14.0, 0.5) for (cx, cy) in RIGHT_SWITCHES]
    right_cutouts = right_switch_cutouts + [
        make_inertia_wheel_top_cutout(RIGHT_INERTIA_WHEEL[0], RIGHT_INERTIA_WHEEL[1])
    ]
    right_all_holes = RIGHT_MOUNTING_HOLES + RIGHT_WHEEL_HOLES + [RIGHT_TRACKBALL_CIRCLE]
    p_top_right = os.path.join(out_pcb_dir, "plate-top-right.kicad_pcb")
    write_plate_kicad_pcb(p_top_right, right_outer, right_cutouts, right_all_holes)

    # Verify DRC on top plate PCBs using temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        for name, pcb_path in [
            ("plate-top-left", p_top_left),
            ("plate-top-right", p_top_right),
        ]:
            import json
            rpt = os.path.join(tmpdir, f"drc_{name}.json")
            subprocess.run([KICAD_CLI, "pcb", "drc", "--format", "json", "-o", rpt, pcb_path], check=True)
            drc_data = json.loads(Path(rpt).read_text(encoding="utf-8"))
            assert len(drc_data.get("violations", [])) == 0, f"{name} DRC violations: {drc_data.get('violations')}"
            print(f"Verified DRC for {name}: 0 violations.")

    # 3. SVGs (Top Plates & Switch Foam — uniform Ø 4.40 mm / r = 2.20 mm screw-head clearance holes + closed Ø 28.625 mm trackball circle)
    write_laser_svg(
        os.path.join(out_svg_dir, "plate-curcur40.svg"),
        [
            (left_outer, left_cutouts, LEFT_MOUNTING_HOLES, 130.0, 35.0),
            (right_outer, right_cutouts, right_all_holes, 140.0, 35.0),
        ],
        width_mm=280.0,
        height_mm=120.0,
    )

    left_foam_holes = [(x, y, r) for (x, y, r) in LEFT_MOUNTING_HOLES]
    # Include 2x Ø 2.80 mm (r = 1.40 mm) clearance holes for rEXSW1 THT solder joints at (22.80, -4.75) & (27.80, -4.75):
    right_foam_holes = [(x, y, r) for (x, y, r) in right_all_holes] + [
        (22.8000, -4.7500, 1.40),
        (27.8000, -4.7500, 1.40),
    ]
    right_foam_cutouts = right_switch_cutouts + [
        make_inertia_wheel_foam_cutout()
    ]
    write_laser_svg(
        os.path.join(out_svg_dir, "foam-curcur40.svg"),
        [
            (left_outer, left_cutouts, left_foam_holes, 130.0, 35.0),
            (right_outer, right_foam_cutouts, right_foam_holes, 140.0, 35.0),
        ],
        width_mm=280.0,
        height_mm=120.0,
    )
    print("All curcur40 top plates and SVGs updated successfully!")


if __name__ == "__main__":
    main()

