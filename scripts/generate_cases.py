# -*- coding: utf-8 -*-
"""
Generate curcur40 3D-printed Tray Bottom Cases (cases/curcur40/left.step, left.stl, right.step, right.stl).
Strictly adheres to docs/curcur40/case_spec.md:
- Vertical Stackup (Section 1):
    - Top Plate (FR-4 1.60 mm): Z = 0.00 to -1.60 mm
    - Switch Gap (2.00 mm): Z = -1.60 to -3.60 mm
    - Main PCB (FR-4 1.60 mm): Z = -3.60 to -5.20 mm
    - Component Cavity (3.90 mm): Z = -5.20 to -9.10 mm
    - Case Floor (3.20 mm): Z = -9.10 (flat inner floor, no bosses) to -12.30 mm (outer bottom)
- Fastening Specifications (Section 2):
    - Screw through-holes: Ø 2.40 mm (radius 1.20 mm)
    - Bottom screw head counterbores: Ø 4.60 mm (radius 2.30 mm), depth 0.90 mm (Z = -12.30 to -11.40 mm)
    - Left Case (5 holes): L1..L5
    - Right Case (8 holes): R1..R4 (perimeter) + TB1..TB4 (trackball cup)
- Cutouts & Ports (Section 3):
    - TRRS opening (inner wall): Ø 7.50 mm (radius 3.75 mm), center at Z = -5.35 mm, Y = -91.8000 mm
      (spans Z = -9.10 to -1.60 mm -> flush with inner floor, zero floor cut, zero top plate cut)
    - USB-C opening (top wall): Width 12.50 mm x Height 6.80 mm, corner fillet R = 1.50 mm,
      center at Z = -5.10 mm (spans Z = -8.50 to -1.70 mm, 0.60 mm above inner floor, 0.10 mm below top plate)
"""
from pathlib import Path
from cadgen import build123d as bd
from cadgen.geometry import is_sound

OUT_DIR = Path(r"c:\Users\oktnt\workspace\curcur40\cases\curcur40")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def get_outer_pts(is_right=True):
    if is_right:
        return [
            (  7.0250,  -30.8375, 2.0),
            (135.8580,  -30.8375, 2.0),
            (135.8580, -100.1316, 2.0),
            ( 98.7500, -100.1316, 1.5),
            ( 98.7500, -126.6500, 2.0),
            (  7.0250, -126.6500, 2.0),
        ]
    else:
        return [
            ( -7.0250,  -30.8375, 2.0),
            (-135.8580,  -30.8375, 2.0),
            (-135.8580, -100.1316, 2.0),
            (-98.7500, -100.1316, 1.5),
            (-98.7500, -126.6500, 2.0),
            ( -7.0250, -126.6500, 2.0),
        ]


def get_inner_pts(is_right=True):
    if is_right:
        return [
            (  8.5250,  -32.3375, 1.0),
            (134.3580,  -32.3375, 1.0),
            (134.3580,  -98.6316, 1.0),
            ( 97.2500,  -98.6316, 1.0),
            ( 97.2500, -125.1500, 1.0),
            (  8.5250, -125.1500, 1.0),
        ]
    else:
        return [
            ( -8.5250,  -32.3375, 1.0),
            (-134.3580,  -32.3375, 1.0),
            (-134.3580,  -98.6316, 1.0),
            (-97.2500,  -98.6316, 1.0),
            (-97.2500, -125.1500, 1.0),
            ( -8.5250, -125.1500, 1.0),
        ]


def make_filleted_sketch(pts_and_radii):
    with bd.BuildSketch() as sk:
        pts = [(p[0], p[1]) for p in pts_and_radii]
        bd.Polygon(pts)
        for x, y, r in pts_and_radii:
            if r > 0.05:
                v_target = sk.vertices().filter_by(
                    lambda v, tx=x, ty=y: abs(v.X - tx) < 0.2 and abs(v.Y - ty) < 0.2
                )
                if len(v_target) > 0:
                    try:
                        bd.fillet(v_target, radius=r)
                    except Exception as e:
                        print(f"Warning: fillet failed at ({x}, {y}) r={r}: {e}")
    return sk.sketch


def get_case_hole_coords(is_right=True):
    """
    Returns STEP-coordinate (X_step, Y_step) centers for all M2 mounting holes
    per docs/curcur40/case_spec.md Section 2.3.
    """
    if is_right:
        # 4 perimeter holes + 4 trackball cup holes = 8 holes
        pcb_holes = [
            # Perimeter 4 holes
            (  0.0000, -15.0000),  # R1
            (  0.0000,  25.0000),  # R2
            (109.5375, -20.0000),  # R3
            ( 98.0000,  38.0000),  # R4
            # Trackball 4 holes
            ( -2.4750,  41.0875),  # TB1 (NW)
            ( 21.5250,  41.0875),  # TB2 (NE)
            ( -2.4750,  63.6875),  # TB3 (SW)
            ( 21.5250,  63.6875),  # TB4 (SE)
        ]
        return [(x + 14.2875, -(y + 57.1500)) for x, y in pcb_holes]
    else:
        # 5 perimeter holes
        pcb_holes = [
            (   0.0000, -15.0000),  # L1
            (   0.0000,  25.0000),  # L2
            (-109.5375, -20.0000),  # L3
            ( -98.0000,  38.0000),  # L4
            ( -23.8125,  64.0000),  # L5
        ]
        return [(x - 14.2875, -(y + 57.1500)) for x, y in pcb_holes]


def build_case(is_right=True) -> bd.Solid:
    side_str = "right" if is_right else "left"
    print(f"--- Building {side_str} case per case_spec.md ---")

    z_outer_bottom = -12.30
    z_inner_floor = -9.10
    z_top = 0.00
    total_height = z_top - z_outer_bottom  # 12.30 mm

    # 1. Outer solid (Z = -12.30 to 0.00 mm, total height 12.30 mm)
    outer_pts = get_outer_pts(is_right)
    sk_outer = make_filleted_sketch(outer_pts)
    outer_solid = bd.extrude(sk_outer, amount=total_height).moved(
        bd.Location((0, 0, z_outer_bottom))
    )

    # Fillet outer top (Z = 0.00) and bottom (Z = -12.30) horizontal boundary edges (R = 0.95 mm)
    top_edges = outer_solid.edges().filter_by(
        lambda e: abs(e.bounding_box().min.Z - z_top) < 0.05
        and abs(e.bounding_box().max.Z - z_top) < 0.05
    )
    bottom_edges = outer_solid.edges().filter_by(
        lambda e: abs(e.bounding_box().min.Z - z_outer_bottom) < 0.05
        and abs(e.bounding_box().max.Z - z_outer_bottom) < 0.05
    )
    try:
        outer_solid = bd.fillet(top_edges + bottom_edges, radius=0.95)
    except Exception as e:
        print(f"Warning: fillet top/bottom: {e}")

    # 2. Inner cavity (Z = -9.10 to +1.00 mm -> completely flat inner floor at Z = -9.10 mm, 3.20 mm floor thickness)
    inner_pts = get_inner_pts(is_right)
    sk_inner = make_filleted_sketch(inner_pts)
    inner_solid = bd.extrude(sk_inner, amount=10.10).moved(
        bd.Location((0, 0, z_inner_floor))
    )
    body = outer_solid - inner_solid

    # 3. M2 mounting holes (Ø 2.40 mm through-hole + Ø 4.60 mm x 0.90 mm bottom counterbore)
    # Note: Per case_spec.md Section 1.2 & 4.1, NO sensor hole/recess is cut into the case floor.
    case_holes = get_case_hole_coords(is_right)
    for cx, cy in case_holes:
        # Through hole: Ø 2.40 mm (radius 1.20 mm)
        body = body - bd.Cylinder(
            radius=1.20,
            height=20.0,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((cx, cy, -15.0)))
        # Bottom counterbore: Ø 4.60 mm (radius 2.30 mm), depth 0.90 mm (from Z = -12.30 up to -11.40 mm)
        body = body - bd.Cylinder(
            radius=2.30,
            height=1.90,  # from -13.30 to -11.40 -> exact 0.90 mm depth into Z = -12.30 bottom face
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((cx, cy, -13.30)))

    # 4. USB-C port cutout (Section 3.2: Width = 12.50 mm, Height = 6.80 mm, R = 1.50 mm, Center Z = -5.10 mm)
    # Spans Z = -8.50 mm (0.60 mm above inner floor -9.10) to Z = -1.70 mm (0.10 mm below top plate -1.60)
    usb_cx = 26.5750 if is_right else -26.5750
    usb_cutter = bd.Box(12.50, 15.00, 6.80).moved(
        bd.Location((usb_cx, -30.8375, -5.1000))
    )
    edges_y = usb_cutter.edges().filter_by(
        lambda e: abs(e.bounding_box().size.Y - 15.00) < 0.1
    )
    if len(edges_y) == 4:
        usb_cutter = bd.fillet(edges_y, radius=1.50)
    body = body - usb_cutter

    # 5. TRRS port cutout (Section 3.1: Ø 7.50 mm -> radius 3.75 mm, Center Z = -5.35 mm, Y = -91.8000 mm)
    # Spans Z = -9.10 mm (tangent to inner floor) to Z = -1.60 mm (tangent to bottom of top plate)
    trrs_x = 7.0250 if is_right else -7.0250
    trrs_cutter = (
        bd.Cylinder(radius=3.75, height=20.0)
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((trrs_x, -91.8000, -5.3500)))
    )
    body = body - trrs_cutter

    solids = body.solids()
    assert len(solids) == 1, f"Expected 1 solid for {side_str} case, got {len(solids)}"
    solid = solids[0]
    solid.label = f"{side_str}_case"
    print(
        f"{side_str} case: valid={solid.is_valid}, sound={is_sound(solid)}, volume={solid.volume:.2f} mm^3"
    )

    step_path = OUT_DIR / f"{side_str}.step"
    stl_path = OUT_DIR / f"{side_str}.stl"
    bd.export_step(solid, str(step_path))
    bd.export_stl(solid, str(stl_path))
    print(f"Exported {step_path} and {stl_path}")
    return solid


if __name__ == "__main__":
    build_case(is_right=True)
    build_case(is_right=False)
    print("Both cases generated successfully!")
