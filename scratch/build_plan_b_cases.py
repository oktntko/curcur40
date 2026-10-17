# -*- coding: utf-8 -*-
"""
Generate Plan B Cases for curcur40 (Right and Left).
"""
import math
from pathlib import Path
import cadgen.build123d as bd

OUT_DIR = Path(r"c:\Users\oktnt\workspace\curcur40\cases\curcur40")

def get_outer_pts(is_right=True):
    # Corner fillets: 2.0 mm on external corners, 1.5 mm on inner step corners
    if is_right:
        return [
            (  7.0250,  -30.8375, 2.0),  # Top-left
            (135.8580,  -30.8375, 2.0),  # Top-right
            (135.8580, -100.1316, 2.0),  # Pinky-right bottom
            ( 98.7500, -100.1316, 1.5),  # Pinky step inner
            ( 98.7500, -126.6500, 2.0),  # Thumb bottom-right
            (  7.0250, -126.6500, 2.0),  # Bottom-left
        ]
    else:
        return [
            ( -7.0250,  -30.8375, 2.0),  # Top-right
            (-135.8580,  -30.8375, 2.0),  # Top-left
            (-135.8580, -100.1316, 2.0),  # Pinky-left bottom
            (-98.7500, -100.1316, 1.5),  # Pinky step inner
            (-98.7500, -126.6500, 2.0),  # Thumb bottom-left
            ( -7.0250, -126.6500, 2.0),  # Bottom-right
        ]

def get_inner_pts(is_right=True):
    # 1.5 mm uniform inset from outer wall
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
        for i, (x, y, r) in enumerate(pts_and_radii):
            if r > 0.05:
                v_target = sk.vertices().filter_by(lambda v, tx=x, ty=y: abs(v.X - tx) < 0.2 and abs(v.Y - ty) < 0.2)
                if len(v_target) > 0:
                    try:
                        bd.fillet(v_target, radius=r)
                    except Exception as e:
                        print(f"Warning: fillet failed at ({x}, {y}) r={r}: {e}")
    return sk.sketch

def build_case(is_right=True):
    side_str = "right" if is_right else "left"
    print(f"--- Building {side_str} case ---")

    # 1. Outer solid (Z = -12.60 to -0.30, 3.20mm solid floor)
    outer_pts = get_outer_pts(is_right)
    sk_outer = make_filleted_sketch(outer_pts)
    outer_solid = bd.extrude(sk_outer, amount=12.30).moved(bd.Location((0, 0, -12.60)))

    # Fillet outer top and bottom horizontal boundary edges (R=0.95 mm)
    top_edges = outer_solid.edges().filter_by(lambda e: abs(e.bounding_box().min.Z - (-0.30)) < 0.05 and abs(e.bounding_box().max.Z - (-0.30)) < 0.05)
    bottom_edges = outer_solid.edges().filter_by(lambda e: abs(e.bounding_box().min.Z - (-12.60)) < 0.05 and abs(e.bounding_box().max.Z - (-12.60)) < 0.05)
    try:
        outer_solid = bd.fillet(top_edges + bottom_edges, radius=0.95)
    except Exception as e:
        print(f"Warning: fillet top/bottom: {e}")
        try:
            outer_solid = bd.fillet(top_edges, radius=0.95)
        except Exception:
            pass

    # 2. Inner cavity (Z = -9.40 to +1.00)
    inner_pts = get_inner_pts(is_right)
    sk_inner = make_filleted_sketch(inner_pts)
    inner_solid = bd.extrude(sk_inner, amount=10.40).moved(bd.Location((0, 0, -9.40)))
    body = outer_solid - inner_solid

    # 3. Perimeter M2 mounting holes with bottom counterbores
    if is_right:
        # Right Case: Hole 1 (top-right), Hole 2 (top-left), Hole 3 (pinky right)
        case_holes = [
            (100.0000 + 14.2875, -(-22.5000 + 57.1500)),   # (114.2875, -34.6500)
            ( 23.8125 + 14.2875, -(-22.5000 + 57.1500)),   # ( 38.1000, -34.6500)
            ( 98.0000 + 14.2875, -( 38.0000 + 57.1500)),   # (112.2875, -95.1500)
        ]
    else:
        # Left Case: Hole 1 (top-left), Hole 2 (top-right), Hole 3 (pinky left), Hole 4 (thumb front)
        case_holes = [
            (-100.0000 - 14.2875, -(-22.5000 + 57.1500)),  # (-114.2875, -34.6500)
            ( -23.8125 - 14.2875, -(-22.5000 + 57.1500)),  # ( -38.1000, -34.6500)
            ( -98.0000 - 14.2875, -( 38.0000 + 57.1500)),  # (-112.2875, -95.1500)
            ( -23.8125 - 14.2875, -( 64.0000 + 57.1500)),  # ( -38.1000, -121.1500)
        ]
    for cx, cy in case_holes:
        # Through hole (Ø 2.20 mm)
        body = body - bd.Cylinder(radius=1.10, height=20.0).moved(bd.Location((cx, cy, -15.0)))
        # Bottom counterbore (Ø 4.50 mm, depth 1.80 mm from Z = -12.60 to -10.80)
        body = body - bd.Cylinder(radius=2.25, height=1.80).moved(bd.Location((cx, cy, -12.60 + 0.90)))

    # 4. USB-C port cutout
    # rJ1 at x_pcb = 12.2875 -> X_case = 26.5750 mm (Right), -26.5750 mm (Left)
    usb_cx = 26.5750 if is_right else -26.5750
    with bd.BuildSketch(bd.Plane.XZ.offset(-35.0)) as sk_usb:
        with bd.Locations([(usb_cx, (-8.66 + -4.50) / 2.0)]):
            bd.RectangleRounded(10.00, -4.50 - (-8.66), radius=0.8)
    usb_solid = bd.extrude(sk_usb.sketch, amount=10.0)
    body = body - usb_solid

    # 5. TRRS port cutout
    # rJ2 at X_case = 9.0300 (Right), -9.0300 (Left), Y = -91.8000, Z = -6.6500
    trrs_x = 0.0 if is_right else -15.0
    with bd.BuildSketch(bd.Plane.YZ.offset(trrs_x)) as sk_trrs:
        with bd.Locations([(-91.8000, -6.6500)]):
            bd.Circle(radius=2.75)
    trrs_solid = bd.extrude(sk_trrs.sketch, amount=15.0)
    body = body - trrs_solid

    # 6. Right Case Trackball Optical Window & 4x M2 Mounting Holes with counterbores
    if is_right:
        tb_cx, tb_cy = 23.8125, -109.5375
        with bd.BuildSketch(bd.Plane.XY.offset(-15.0)) as sk_opt:
            with bd.Locations([(tb_cx, tb_cy)]):
                bd.RectangleRounded(8.00, 12.00, radius=1.50)
        opt_solid = bd.extrude(sk_opt.sketch, amount=8.0)
        body = body - opt_solid

        tb_screws = [
            (tb_cx - 4.50, tb_cy - 10.00),
            (tb_cx + 4.50, tb_cy - 10.00),
            (tb_cx - 4.50, tb_cy + 10.00),
            (tb_cx + 4.50, tb_cy + 10.00),
        ]
        for sx, sy in tb_screws:
            # Through hole (Ø 2.20 mm)
            body = body - bd.Cylinder(radius=1.10, height=20.0).moved(bd.Location((sx, sy, -15.0)))
            # Bottom counterbore (Ø 4.50 mm, depth 1.80 mm)
            body = body - bd.Cylinder(radius=2.25, height=1.80).moved(bd.Location((sx, sy, -12.60 + 0.90)))

    solids = body.solids()
    print(f"{side_str} case: {len(solids)} solid(s), volume = {body.volume:.2f} mm^3")
    assert len(solids) == 1
    solid = solids[0]
    solid.label = f"{side_str}_case"

    step_path = OUT_DIR / f"{side_str}.step"
    stl_path = OUT_DIR / f"{side_str}.stl"
    print(f"Exporting {step_path}...")
    bd.export_step(solid, str(step_path))
    print(f"Exporting {stl_path}...")
    bd.export_stl(solid, str(stl_path))
    return solid

if __name__ == "__main__":
    build_case(is_right=True)
    build_case(is_right=False)
    print("Done generating both cases!")
