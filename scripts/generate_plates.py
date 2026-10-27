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

# Left perimeter mounting holes (5 holes, Ø 2.40 mm -> radius 1.20 mm)
LEFT_MOUNTING_HOLES = [
    (   0.0000, -15.0000, 1.20),
    (   0.0000,  20.0000, 1.20),
    (-101.0000, -20.0000, 1.20),
    ( -98.0000,  38.0000, 1.20),
    ( -62.0000,  64.6000, 1.20),
]

# Right perimeter mounting holes (5 holes, Ø 2.40 mm -> radius 1.20 mm, symmetric with Left)
RIGHT_MOUNTING_HOLES = [
    (  0.0000, -15.0000, 1.20),
    (  0.0000,  20.0000, 1.20),
    (101.0000, -20.0000, 1.20),
    ( 98.0000,  38.0000, 1.20),
    ( 62.0000,  64.6000, 1.20),
]

LEFT_SWITCHES = [
    # Main 3x5
    (-109.5375, -7.14375),   # SW18 (0,1)
    (-109.5375, 11.90625),   # SW17 (1,1)
    (-109.5375, 30.95625),   # SW16 (2,1)
    (-90.4875, -11.90625),   # SW13 (0,2)
    (-90.4875, 7.14375),     # SW14 (1,2)
    (-90.4875, 26.19375),    # SW15 (2,2)
    (-71.4375, -14.28750),   # SW12 (0,3)
    (-71.4375, 4.76250),     # SW11 (1,3)
    (-71.4375, 23.81250),    # SW10 (2,3)
    (-52.3875, -11.90625),   # SW5  (0,4)
    (-52.3875, 7.14375),     # SW6  (1,4)
    (-52.3875, 26.19375),    # SW7  (2,4)
    (-33.3375, -9.52500),    # SW4  (0,5)
    (-33.3375, 9.52500),     # SW3  (1,5)
    (-33.3375, 28.57500),    # SW2  (2,5)
    # Inner 2 keys
    (-14.2875, 0.00000),     # EXSW1 (0,6)
    (-14.2875, 19.05000),    # EXSW2 (1,6)
    # Thumb 4 keys
    (-71.4375, 52.38750),    # SW9   (3,3)
    (-52.3875, 52.38750),    # SW8   (3,4)
    (-33.3375, 52.38750),    # SW1   (3,5)
    (-14.2875, 52.38750),    # EXSW3 (3,6)
]

RIGHT_SWITCHES = [
    # Main 3x5
    (109.5375, -7.14375),    # rSW18 (4,1)
    (109.5375, 11.90625),    # rSW17 (5,1)
    (109.5375, 30.95625),    # rSW16 (6,1)
    (90.4875, -11.90625),    # rSW13 (4,2)
    (90.4875, 7.14375),      # rSW14 (5,2)
    (90.4875, 26.19375),     # rSW15 (6,2)
    (71.4375, -14.28750),    # rSW12 (4,3)
    (71.4375, 4.76250),      # rSW11 (5,3)
    (71.4375, 23.81250),     # rSW10 (6,3)
    (52.3875, -11.90625),    # rSW5  (4,4)
    (52.3875, 7.14375),      # rSW6  (5,4)
    (52.3875, 26.19375),     # rSW7  (6,4)
    (33.3375, -9.52500),     # rSW4  (4,5)
    (33.3375, 9.52500),      # rSW3  (5,5)
    (33.3375, 28.57500),     # rSW2  (6,5)
    # Inner 1u key
    (14.2875, 19.05000),     # rEXSW2 (5,6)
    # Thumb 3 keys
    (33.3375, 52.38750),     # rSW1  (7,5)
    (52.3875, 52.38750),     # rSW8  (7,4)
    (71.4375, 52.38750),     # rSW9  (7,3)
]

# Right Sunk Inertia Wheel 3-point M2 mounting holes (Ø 2.40 mm -> radius 1.20 mm)
RIGHT_WHEEL_HOLES = [
    ( 2.0875,  -1.9000, 1.20),
    ( 2.0875,   5.8000, 1.20),
    (16.2875, -12.2000, 1.20),
]

RIGHT_INERTIA_WHEEL = (14.2875, 0.00000)  # Sunk Passive Magnetic Inertia Wheel module center (axle at Y = -0.1000 mm)


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


def make_inertia_wheel_top_cutout(cx_mod, cy_mod):
    """
    Exact 2D closed boundary of the Sunk Inertia Wheel Twin-Snap Top Plate opening (36 vertices, identical to
    `SUNK_PLATE_OPENING_Q1` in `scripts/generate_inertia_wheel.py`, mirrored into all four quadrants
    around the axle `(cx_mod, cy_mod - 0.10)`):
      - Central flywheel slot: 6.16 x 18.16 mm (R = 0.55 mm) -> >= 0.30 mm to the wheel over the full click stroke
      - Core window: 16.40 x 8.40 mm (bearing ears, magnets, AS5600 IC swing envelope)
      - AS5600 sub-PCB swing windows: 6.65 <= |dx| <= 8.20 mm, |dy| <= 5.30 mm (R = 0.50 mm)
      - Twin snap-leg windows: 1.54 x 10.86 mm (R = 0.45 mm) at dx = ±4.62 mm (locate 1.34 mm legs at ±0.10 mm)
    """
    cx = cx_mod
    cy = cy_mod - 0.1000
    q1 = [
        (8.20, 5.30, 0.50),
        (6.65, 5.30, 0.50),
        (6.65, 4.20, 0.00),
        (5.39, 4.20, 0.00),
        (5.39, 5.43, 0.45),
        (3.85, 5.43, 0.45),
        (3.85, 4.20, 0.00),
        (3.08, 4.20, 0.00),
        (3.08, 9.08, 0.55),
    ]
    q2 = [(-u, v, r) for (u, v, r) in reversed(q1)]
    q3 = [(-u, -v, r) for (u, v, r) in q1]
    q4 = [(u, -v, r) for (u, v, r) in reversed(q1)]
    pts = [(cx + u, cy + v, r) for (u, v, r) in q1 + q2 + q3 + q4]
    return round_polygon_with_fillets(pts)


def get_left_outer_pts():
    return [
        (-119.2625, -24.51250, 1.0),  # Top-left
        (   5.4625, -24.51250, 1.0),  # Top-right (+0.20 mm from Main PCB, 0.30 mm clearance to Case inner wall)
        (   5.4625,  67.70000, 1.0),  # Bottom-right
        ( -82.6625,  67.70000, 1.0),  # Thumb bottom-left
        ( -82.6625,  41.18125, 1.0),  # Pinky step inner
        (-119.2625,  41.18125, 1.0),  # Pinky-left bottom
    ]


def get_right_outer_pts(notched_trackball=False):
    if not notched_trackball:
        return [
            ( -5.4625, -24.51250, 1.0),  # Top-left
            (119.2625, -24.51250, 1.0),  # Top-right
            (119.2625,  41.18125, 1.0),  # Pinky-right bottom
            ( 82.6625,  41.18125, 1.0),  # Pinky step inner
            ( 82.6625,  67.70000, 1.0),  # Thumb bottom-right
            ( -5.4625,  67.70000, 1.0),  # Bottom-left
        ]
    else:
        return [
            ( -5.4625, -24.51250, 1.0),  # Top-left (+0.20 mm from Main PCB, 0.30 mm clearance to Case inner wall)
            (119.2625, -24.51250, 1.0),  # Top-right
            (119.2625,  41.18125, 1.0),  # Pinky-right bottom
            ( 82.6625,  41.18125, 1.0),  # Pinky step inner
            ( 82.6625,  67.70000, 1.0),  # Thumb bottom-right
            ( 24.2000,  67.70000, 1.0),  # Notch bottom-right (aligned with Right Main PCB x = 24.2000 mm)
            ( 24.2000,  37.40000, 1.0),  # Notch top-right (aligned with Right Main PCB x = 24.2000, y = 37.4000 mm)
            ( -5.4625,  37.40000, 1.0),  # Notch top-left
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

    # 2. Right Top Plate (with Sunk Inertia Wheel twin-snap opening + 3x Ø2.40 mm M2 holes)
    right_outer_notched = round_polygon_with_fillets(get_right_outer_pts(notched_trackball=True))
    right_switch_cutouts = [make_rect_cutout(cx, cy, 14.0, 14.0, 0.5) for (cx, cy) in RIGHT_SWITCHES]
    right_cutouts = right_switch_cutouts + [
        make_inertia_wheel_top_cutout(RIGHT_INERTIA_WHEEL[0], RIGHT_INERTIA_WHEEL[1])
    ]
    right_all_holes = RIGHT_MOUNTING_HOLES + RIGHT_WHEEL_HOLES
    p_top_right = os.path.join(out_pcb_dir, "plate-top-right.kicad_pcb")
    write_plate_kicad_pcb(p_top_right, right_outer_notched, right_cutouts, right_all_holes)

    # Verify DRC on top plate PCBs using temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        for name, pcb_path in [
            ("plate-top-left", p_top_left),
            ("plate-top-right", p_top_right),
        ]:
            rpt = os.path.join(tmpdir, f"drc_{name}.json")
            subprocess.run([KICAD_CLI, "pcb", "drc", "--format", "json", "-o", rpt, pcb_path], check=True)
            print(f"Verified DRC for {name}.")

    # 3. SVGs (Top Plates & Switch Foam only)
    write_laser_svg(
        os.path.join(out_svg_dir, "plate-curcur40.svg"),
        [
            (left_outer, left_cutouts, LEFT_MOUNTING_HOLES, 130.0, 35.0),
            (right_outer_notched, right_cutouts, right_all_holes, 140.0, 35.0),
        ],
        width_mm=280.0,
        height_mm=120.0,
    )

    left_foam_holes = [(x, y, 2.0) for (x, y, _) in LEFT_MOUNTING_HOLES]
    right_foam_holes = [(x, y, 2.0) for (x, y, _) in right_all_holes]
    right_foam_cutouts = right_switch_cutouts + [
        make_rect_cutout(RIGHT_INERTIA_WHEEL[0], RIGHT_INERTIA_WHEEL[1], 18.6, 18.6, 0.5)
    ]
    write_laser_svg(
        os.path.join(out_svg_dir, "foam-curcur40.svg"),
        [
            (left_outer, left_cutouts, left_foam_holes, 130.0, 35.0),
            (right_outer_notched, right_foam_cutouts, right_foam_holes, 140.0, 35.0),
        ],
        width_mm=280.0,
        height_mm=120.0,
    )
    print("All curcur40 top plates and SVGs updated successfully!")


if __name__ == "__main__":
    main()

