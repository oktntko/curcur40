import math
from pathlib import Path
import cadgen.build123d as bd

OUT_DIR = Path(r"c:\Users\oktnt\workspace\curcur40\cases\curcur40")

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
        case_holes = [
            (114.2875, -34.6500),
            ( 38.1000, -34.6500),
            (112.2875, -95.1500),
        ]
    else:
        case_holes = [
            (-114.2875, -34.6500),
            ( -38.1000, -34.6500),
            (-112.2875, -95.1500),
            ( -38.1000, -121.1500),
        ]
    for cx, cy in case_holes:
        # Through hole (Ø 2.20 mm)
        body = body - bd.Cylinder(radius=1.10, height=20.0).moved(bd.Location((cx, cy, -15.0)))
        # Bottom counterbore (Ø 4.50 mm, depth 1.80 mm from Z = -12.60 to -10.80)
        body = body - bd.Cylinder(radius=2.25, height=1.80).moved(bd.Location((cx, cy, -12.60 + 0.90)))

    # 4. USB-C port cutout (Top wall at Y = -30.8375)
    # Enlarged by one size for generous assembly clearance:
    # Dimensions: Width = 12.50 mm (+1.5mm), Height = 4.80 mm (+0.5mm), Corner radius = 1.20 mm
    # Center: Z = -6.65 mm -> Z range: [-9.05, -4.25] mm (leaves 2.35 mm solid wall below top plate)
    usb_cx = 26.5750 if is_right else -26.5750
    usb_cutter = bd.Box(12.50, 15.00, 4.80).moved(bd.Location((usb_cx, -30.8375, -6.6500)))
    edges_y = usb_cutter.edges().filter_by(lambda e: abs(e.bounding_box().size.Y - 15.00) < 0.1)
    if len(edges_y) == 4:
        usb_cutter = bd.fillet(edges_y, radius=1.20)
    body = body - usb_cutter

    # 5. TRRS port cutout (Inner side wall at X = +7.0250 / -7.0250)
    # Raised center so enlarged diameter does NOT dig into cavity floor:
    # Diameter = 6.20 mm (radius 3.10 mm)
    # Center: Z = -6.10 mm, Y = -91.8000 mm
    # -> Bottom of hole: Z = -9.20 mm (cleanly 0.20 mm above cavity floor Z = -9.40 mm, zero floor bite!)
    # -> Top of hole: Z = -3.00 mm (1.10 mm solid wall below top plate Z = -1.90 mm, plate fully hidden!)
    trrs_x = 7.0250 if is_right else -7.0250
    trrs_cutter = bd.Cylinder(radius=3.10, height=20.0).moved(bd.Location((0, 0, 0)))
    trrs_cutter = trrs_cutter.rotate(bd.Axis.Y, 90).moved(bd.Location((trrs_x, -91.8000, -6.1000)))
    body = body - trrs_cutter

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
            body = body - bd.Cylinder(radius=1.10, height=20.0).moved(bd.Location((sx, sy, -15.0)))
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
    print("ALL DONE PERFECTLY!")
