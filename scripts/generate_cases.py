# -*- coding: utf-8 -*-
"""
Generate curcur40 3D-printed Built-in Tented Tray Bottom Cases
(cases/left.step, left.stl, right.step, right.stl).
Strictly adheres to docs/case_spec.md:
- Vertical Stackup (Section 1):
    - Case Rim Top: Z = 0.00 mm
    - Top Plate (FR-4 1.60 mm): Z = -2.00 to -3.60 mm
    - Switch Gap (0.60 mm): Z = -3.60 to -4.20 mm
    - Main PCB (FR-4 1.60 mm): Z = -4.20 to -5.80 mm
    - Main Component Cavity (3.30 mm): Z = -5.80 to -9.10 mm
    - Sunk Trackball Cup Rim: Z = -2.00 mm (flush with Top Plate top surface)
    - Sunk Sensor PCB (curcur40-pmw3360, FR-4 1.60 mm): Z = -16.00 to -17.60 mm
    - Sunk Sensor Cavity (3.30 mm): Z = -17.60 to -20.90 mm
    - Built-in Tenting Outer Bottom Plane (theta_tent = 8.00 deg):
        - Pinky outer edge (|X_step| = 135.8580 mm): Z_bottom = -10.50 mm (total height 10.50 mm)
        - Thumb inner edge (|X_step| = 7.0250 mm):   Z_bottom = -28.60 mm (total height 28.60 mm, +18.10 mm lift)
- Fastening Specifications (Section 2):
    - 14x M2 mounting holes (5 Left perimeter L1..L5, 5 Right perimeter R1..R5, 4 Right trackball TB1..TB4)
    - Unified 2.40 mm solid clamping floor thickness at all 14 holes:
        - Perimeter holes (L1..L5, R1..R5): standoff top seat Z = -9.10 mm, counterbore ceiling Z = -11.50 mm
        - Trackball holes (TB1..TB4):       standoff top seat Z = -20.90 mm, counterbore ceiling Z = -23.30 mm
    - Screw through-holes: Ø 2.40 mm (radius 1.20 mm)
    - Bottom screw head counterbores: Ø 4.60 mm (radius 2.30 mm) from angled bottom up to z_boss_top - 2.40 mm
- Cutouts & Ports (Section 3):
    - TRRS opening (inner wall): Ø 7.50 mm (radius 3.75 mm), center at Z = -5.35 mm, Y = -86.8000 mm
    - USB-C opening (top wall): Width 12.50 mm x Height 6.80 mm, corner fillet R = 1.50 mm, center at Z = -5.10 mm
"""
import math
from pathlib import Path
from cadgen import build123d as bd
from cadgen.geometry import is_sound

WORKSPACE = Path(__file__).resolve().parent.parent
OUT_DIR = WORKSPACE / "cases"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def z_bottom_at_x(x_abs: float) -> float:
    """
    Built-in tenting outer bottom Z height at |X_step| (theta_tent = 8.00 deg):
    - |X| = 7.0250 mm (thumb inner edge):  Z = -28.6000 mm
    - |X| = 135.8580 mm (pinky outer edge): Z = -10.5000 mm
    """
    return -28.60 + 18.10 * (x_abs - 7.0250) / (135.8580 - 7.0250)


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


def get_case_hole_specs(is_right=True):
    """
    Returns list of (cx, cy, z_boss_top) in STEP coordinates:
    - Perimeter holes (L1..L5, R1..R5): z_boss_top = -9.10 mm (counterbore ceiling Z = -11.50 mm, 2.40 mm floor)
    - Trackball holes (TB1..TB4):       z_boss_top = -20.90 mm (counterbore ceiling Z = -23.30 mm, 2.40 mm floor)
    """
    if is_right:
        perim_pcb = [
            (  0.0000, -15.0000),  # R1
            (  0.0000,  20.0000),  # R2
            (101.0000, -20.0000),  # R3
            ( 98.0000,  38.0000),  # R4
            ( 62.0000,  64.6000),  # R5
        ]
        tb_pcb = [
            ( -2.4750,  41.0875),  # TB1 (NW)
            ( 21.5250,  41.0875),  # TB2 (NE)
            ( -2.4750,  63.6875),  # TB3 (SW)
            ( 21.5250,  63.6875),  # TB4 (SE)
        ]
        specs = [(x + 14.2875, -(y + 57.1500), -9.10) for x, y in perim_pcb]
        specs += [(x + 14.2875, -(y + 57.1500), -20.90) for x, y in tb_pcb]
        return specs
    else:
        perim_pcb = [
            (   0.0000, -15.0000),  # L1
            (   0.0000,  20.0000),  # L2
            (-101.0000, -20.0000),  # L3
            ( -98.0000,  38.0000),  # L4
            ( -62.0000,  64.6000),  # L5
        ]
        return [(x - 14.2875, -(y + 57.1500), -9.10) for x, y in perim_pcb]


def build_case(is_right=True) -> bd.Solid:
    side_str = "right" if is_right else "left"
    print(f"--- Building {side_str} built-in tented case per case_spec.md ---")

    z_ext_bottom = -30.00
    z_inner_floor = -9.10
    z_top = 0.00

    # 1. Outer solid extruded from Z = -30.00 to 0.00 mm
    outer_pts = get_outer_pts(is_right)
    sk_outer = make_filleted_sketch(outer_pts)
    outer_solid = bd.extrude(sk_outer, amount=z_top - z_ext_bottom).moved(
        bd.Location((0, 0, z_ext_bottom))
    )

    # Fillet outer top (Z = 0.00) horizontal boundary edges (R = 0.95 mm)
    top_edges = outer_solid.edges().filter_by(
        lambda e: abs(e.bounding_box().min.Z - z_top) < 0.05
        and abs(e.bounding_box().max.Z - z_top) < 0.05
    )
    try:
        outer_solid = bd.fillet(top_edges, radius=0.95)
    except Exception as e:
        print(f"Warning: fillet top: {e}")

    # Cut angled bottom tenting plane (theta_tent = 8.00 deg):
    # Z_bottom(|X|) = -28.60 at |X|=7.0250 mm, -10.50 at |X|=135.8580 mm
    if is_right:
        p_thumb = (7.0250, -80.0, -28.60)
        p_pinky = (135.8580, -80.0, -10.50)
        dx = p_pinky[0] - p_thumb[0]
        dz = p_pinky[2] - p_thumb[2]
        norm = (dz, 0.0, -dx)
    else:
        p_thumb = (-7.0250, -80.0, -28.60)
        p_pinky = (-135.8580, -80.0, -10.50)
        dx = p_pinky[0] - p_thumb[0]
        dz = p_pinky[2] - p_thumb[2]
        norm = (-dz, 0.0, dx)

    tent_plane = bd.Plane(origin=p_thumb, z_dir=norm)
    bottom_cutter = bd.extrude(tent_plane * bd.Rectangle(400.0, 400.0), amount=50.0)
    outer_solid = outer_solid - bottom_cutter

    # 2. Main inner cavity (Z = -9.10 to +1.00 mm)
    inner_pts = get_inner_pts(is_right)
    sk_inner = make_filleted_sketch(inner_pts)
    inner_solid = bd.extrude(sk_inner, amount=10.10).moved(
        bd.Location((0, 0, z_inner_floor))
    )
    body = outer_solid - inner_solid

    # 3. On Right Case: Sunk Trackball Sensor PCB & JST SH Harness Cavity
    # Sensor PCB (curcur40-pmw3360) spans X_step in [9.0250, 38.6000], Y_step in [-124.6500, -95.4500], Z in [-17.60, -16.00]
    # J1 connector on B.Cu faces +X (East) at X_step = 34.4875, Y_step = -109.5375, and rJ3 on Main PCB B.Cu faces -X (West) at X_step = 56.2875, Y_step = -119.7500.
    if is_right:
        # 3a. Main sunk sensor bay strictly under the Trackball Cup & Sensor PCB (X = 8.5250 to 39.2000, Y = -125.1500 to -94.8000, Z = -20.90 to -9.00)
        # At X = 39.2000, z_bottom_at_x(39.2000) = -24.08 mm, preserving >= 3.18 mm solid bottom floor everywhere (zero bottom breakthrough!)
        with bd.BuildSketch(bd.Plane.XY.offset(-20.90)) as sk_bay:
            with bd.Locations([(23.8625, -109.9750)]):
                bd.RectangleRounded(30.6750, 30.3500, 1.0)
        sensor_bay = bd.extrude(sk_bay.sketch, amount=11.90)

        # 3b. JST SH cable routing channel extending East from X = 38.00 to 60.00, Y = -125.15 to -104.00, Z = -17.50 to -9.00
        # Leaves R5 (X = 76.2875, Y = -121.7500) on the normal Z = -9.10 mm floor and preserves >= 3.66 mm bottom floor everywhere!
        with bd.BuildSketch(bd.Plane.XY.offset(-17.50)) as sk_chan:
            with bd.Locations([(49.0000, -114.5750)]):
                bd.RectangleRounded(22.0000, 21.1500, 2.0)
        cable_chan = bd.extrude(sk_chan.sketch, amount=8.50)

        body = body - (sensor_bay + cable_chan)

    # 4. M2 mounting holes: unified 2.40 mm solid clamping floor thickness at all 14 holes!
    #    - z_cb_ceil = z_boss_top - 2.40 mm (-11.50 mm for perimeter holes, -23.30 mm for TB1..TB4)
    #    - Ø 2.40 mm through-hole + Ø 4.60 mm deep bottom counterbore up to z_cb_ceil
    hole_specs = get_case_hole_specs(is_right)
    for cx, cy, z_boss_top in hole_specs:
        z_cb_ceil = round(z_boss_top - 2.40, 4)

        # Through hole: Ø 2.40 mm (radius 1.20 mm)
        body = body - bd.Cylinder(
            radius=1.20,
            height=35.0,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((cx, cy, -32.0)))

        # Bottom counterbore: Ø 4.60 mm (radius 2.30 mm) from Z = -32.0 up to z_cb_ceil
        body = body - bd.Cylinder(
            radius=2.30,
            height=z_cb_ceil - (-32.0),
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((cx, cy, -32.0)))

    # 5. USB-C port cutout (Section 3.2: Width = 12.50 mm, Height = 6.80 mm, R = 1.50 mm, Center Z = -5.10 mm)
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

    # 6. TRRS port cutout (Section 3.1: Ø 7.50 mm -> radius 3.75 mm, Center Z = -5.35 mm, Y = -86.8000 mm)
    trrs_x = 7.0250 if is_right else -7.0250
    trrs_cutter = (
        bd.Cylinder(radius=3.75, height=20.0)
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((trrs_x, -86.8000, -5.3500)))
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
    print("Both built-in tented cases generated successfully!")
