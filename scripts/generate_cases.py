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
    - Built-in Tenting Outer Bottom Plane (theta_tent = 5.233 deg):
        - Pinky outer edge (|X_step| = 135.8580 mm): Z_bottom = -12.30 mm (total height 12.30 mm)
        - Thumb inner edge (|X_step| = 7.0250 mm):   Z_bottom = -24.10 mm (total height 24.10 mm, +11.80 mm lift)
- Fastening Specifications (Section 2):
    - 14x M2 mounting bosses (5 Left perimeter L1..L5, 5 Right perimeter R1..R5, 4 Right trackball TB1..TB4)
    - Screw through-holes: Ø 2.40 mm (radius 1.20 mm)
    - Bottom screw head counterbores: Ø 4.60 mm (radius 2.30 mm), horizontal flat seating face at Z_bottom(|X|) + 1.15 mm
- Cutouts & Ports (Section 3):
    - TRRS opening (inner wall): Ø 7.50 mm (radius 3.75 mm), center at Z = -5.35 mm, Y = -91.8000 mm
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
    Built-in tenting outer bottom Z height at |X_step|:
    - |X| = 7.0250 mm (thumb inner edge):  Z = -24.1000 mm
    - |X| = 135.8580 mm (pinky outer edge): Z = -12.3000 mm
    """
    return -24.10 + 11.80 * (x_abs - 7.0250) / (135.8580 - 7.0250)


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
    - Perimeter holes (L1..L5, R1..R5): z_boss_top = -9.10 mm (supports 5.50 mm standoff up to Top Plate bottom Z = -3.60 mm)
    - Trackball holes (TB1..TB4):       z_boss_top = -20.90 mm (supports 6.00 mm standoff up to Z = -14.90 mm inside Cup ear)
    """
    if is_right:
        perim_pcb = [
            (  0.0000, -15.0000),  # R1
            (  0.0000,  25.0000),  # R2
            (109.5375, -20.0000),  # R3
            ( 98.0000,  38.0000),  # R4
            ( 33.3375,  64.3000),  # R5 (Thumb perimeter hole)
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
            (   0.0000,  25.0000),  # L2
            (-109.5375, -20.0000),  # L3
            ( -98.0000,  38.0000),  # L4
            ( -33.3375,  64.3000),  # L5 (Mirror-symmetric to R5)
        ]
        return [(x - 14.2875, -(y + 57.1500), -9.10) for x, y in perim_pcb]


def build_case(is_right=True) -> bd.Solid:
    side_str = "right" if is_right else "left"
    print(f"--- Building {side_str} built-in tented case per case_spec.md ---")

    z_ext_bottom = -26.00
    z_inner_floor = -9.10
    z_top = 0.00

    # 1. Outer solid extruded from Z = -26.00 to 0.00 mm
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

    # Cut angled bottom tenting plane (theta_tent = 5.233 deg):
    # Z_bottom(|X|) = -24.10 at |X|=7.0250 mm, -12.30 at |X|=135.8580 mm
    if is_right:
        p_thumb = (7.0250, -80.0, -24.10)
        p_pinky = (135.8580, -80.0, -12.30)
        dx = p_pinky[0] - p_thumb[0]
        dz = p_pinky[2] - p_thumb[2]
        # Downward normal: (+dz, 0, -dx)
        norm = (dz, 0.0, -dx)
    else:
        p_thumb = (-7.0250, -80.0, -24.10)
        p_pinky = (-135.8580, -80.0, -12.30)
        dx = p_pinky[0] - p_thumb[0]  # negative
        dz = p_pinky[2] - p_thumb[2]  # positive
        # Downward normal: (-dz, 0, +dx)
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

    # 3. On Right Case: Sunk Trackball Sensor PCB & JST SH Harness Cavity (Z = -20.90 to -9.00 mm)
    # Sensor PCB (curcur40-pmw3360) spans X_step in [9.0250, 38.6000], Y_step in [-124.6500, -95.4500], Z in [-17.60, -16.00]
    # J1 connector on B.Cu faces +X (East), and harness routes East to rJ3 at X_step = 59.2875, Y_step = -119.5625.
    if is_right:
        # 3a. Main sunk sensor bay under the Trackball Cup & Sensor PCB (X = 8.5250 to 44.5000, Y = -125.1500 to -94.8000, Z = -20.90 to -9.00)
        with bd.BuildSketch(bd.Plane.XY.offset(-20.90)) as sk_bay:
            with bd.Locations([(26.5125, -109.9750)]):
                bd.RectangleRounded(35.9750, 30.3500, 1.0)
        sensor_bay = bd.extrude(sk_bay.sketch, amount=11.90)

        # 3b. JST SH cable routing channel extending East from X = 40.00 to 65.50, Y = -125.15 to -108.00, Z = -16.50 to -9.00
        # Preserves >= 3.20 mm bottom floor everywhere while giving a generous 7.5 mm tall x 17.15 mm wide tunnel for the 6-pin harness
        with bd.BuildSketch(bd.Plane.XY.offset(-16.50)) as sk_chan:
            with bd.Locations([(52.7500, -116.5750)]):
                bd.RectangleRounded(25.5000, 17.1500, 2.0)
        cable_chan = bd.extrude(sk_chan.sketch, amount=7.50)

        # Subtract bay & channel, keeping a Ø 6.40 mm solid boss pillar around R5 (47.6250, -121.4500) up to Z = -9.10 mm
        r5_boss = bd.Cylinder(
            radius=3.20,
            height=15.0,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX),
        ).moved(bd.Location((47.6250, -121.4500, -9.10)))
        body = body - (sensor_bay + cable_chan - r5_boss)

    # 4. M2 mounting holes (Ø 2.40 mm through-hole + Ø 4.60 mm horizontal counterbore)
    hole_specs = get_case_hole_specs(is_right)
    for cx, cy, z_boss_top in hole_specs:
        zb = z_bottom_at_x(abs(cx))
        # Flat horizontal counterbore ceiling at zb + 1.15 mm:
        # At the shallowest (pinky) edge of the Ø 4.60 mm counterbore (|X| + 2.30 mm),
        # the outer bottom surface is at zb + 2.30 * tan(5.233°) = zb + 0.21 mm,
        # so the 0.80 mm tall M2 screw head (seated at zb + 1.15 mm -> bottom at zb + 0.35 mm)
        # is 100% recessed below the angled bottom surface while leaving >= 2.05 mm solid floor clamping thickness!
        z_cb_ceil = round(zb + 1.15, 4)

        # Through hole: Ø 2.40 mm (radius 1.20 mm)
        body = body - bd.Cylinder(
            radius=1.20,
            height=30.0,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((cx, cy, -28.0)))

        # Bottom counterbore: Ø 4.60 mm (radius 2.30 mm) from Z = -28.0 up to z_cb_ceil
        body = body - bd.Cylinder(
            radius=2.30,
            height=z_cb_ceil - (-28.0),
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((cx, cy, -28.0)))

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

    # 6. TRRS port cutout (Section 3.1: Ø 7.50 mm -> radius 3.75 mm, Center Z = -5.35 mm, Y = -91.8000 mm)
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
    print("Both built-in tented cases generated successfully!")
