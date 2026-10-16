# -*- coding: utf-8 -*-
"""
Generate updated right case for curcur40.
Resolves:
1. Trackball cup clearance (+2.0mm shift -> center at (23.8125, -109.5375))
2. TRRS jack L-shaped connector opening (dia 9.5mm opening + angled wall transition)
3. Double wall elimination (clean single extrusion and inner pocket cut)
4. Bottom trackball floor: accurate compact optical window (8x12mm) + 4x M2 screw mounting holes
"""
import os
import sys
import math
from pathlib import Path



import cadgen.build123d as bd

OUT_STEP = Path(r"c:\Users\oktnt\workspace\curcur40\cases\curcur40\right.step")
OUT_STL = Path(r"c:\Users\oktnt\workspace\curcur40\cases\curcur40\right.stl")

# Coordinate conversion reference:
# X_case = x_pcb + 14.2875
# Y_case = -(y_pcb + 57.1500)

def get_right_case_outer_pts():
    """
    Right case outer profile vertices (x, y, fillet_radius).
    Shifted +2.0mm for trackball and extended smoothly to front tab.
    """
    return [
        ( 16.5500,  -37.9828, 2.0),
        ( 35.6159,  -37.9828, 0.0),
        ( 35.6159,  -35.6015, 2.0),
        ( 54.6659,  -35.6015, 0.0),
        ( 54.6659,  -33.2171, 2.0),
        ( 73.7159,  -33.2171, 0.0),
        ( 73.7159,  -30.8372, 2.0),
        ( 97.7659,  -30.8372, 2.0),
        ( 97.7659,  -33.2185, 0.0),
        (116.8159,  -33.2185, 2.0),
        (116.8159,  -37.9809, 0.0),
        (135.8580,  -37.9809, 2.0),
        (135.8580, -100.1316, 2.0),
        ( 98.7500, -100.1316, 0.0),
        ( 98.7500, -122.3125, 2.0),  # Right bottom edge
        ( 40.2470, -122.3125, 0.0),  # Chamfer start
        ( 35.9100, -126.6500, 1.5),  # Front tab right corner
        (  7.0250, -126.6500, 1.5),  # Front tab left-bottom corner
        (  7.0250,  -96.0000, 1.5),  # Trackball left wall top corner
        ( 16.5500,  -93.5000, 1.0),  # TRRS connector transition corner
    ]

def get_right_case_inner_pts():
    """
    Right case inner cavity profile vertices (x, y, fillet_radius).
    Uniform 1.5000 mm wall thickness.
    """
    return [
        ( 18.0500,  -39.4828, 1.0),
        ( 37.1159,  -39.4828, 1.0),
        ( 37.1159,  -37.1015, 1.0),
        ( 56.1659,  -37.1015, 1.0),
        ( 56.1659,  -34.7171, 1.0),
        ( 75.2159,  -34.7171, 1.0),
        ( 75.2159,  -32.3372, 1.0),
        ( 96.2659,  -32.3372, 1.0),
        ( 96.2659,  -34.7185, 1.0),
        (115.3159,  -34.7185, 1.0),
        (115.3159,  -39.4809, 1.0),
        (134.3580,  -39.4809, 1.0),
        (134.3580,  -98.6316, 1.0),
        ( 97.2500,  -98.6316, 1.0),
        ( 97.2500, -120.8125, 1.0),
        ( 39.6250, -120.8125, 0.5),
        ( 35.2880, -125.1500, 1.0),
        (  8.5250, -125.1500, 1.0),
        (  8.5250,  -96.5000, 1.0),
        ( 18.0500,  -94.0000, 0.8),
    ]

def make_filleted_sketch(pts_and_radii):
    with bd.BuildSketch() as sk:
        pts = [(p[0], p[1]) for p in pts_and_radii]
        bd.Polygon(pts)
        for i, (x, y, r) in enumerate(pts_and_radii):
            if r > 0.05:
                v_target = sk.vertices().filter_by(lambda v, tx=x, ty=y: abs(v.X - tx) < 0.1 and abs(v.Y - ty) < 0.1)
                if len(v_target) > 0:
                    try:
                        bd.fillet(v_target, radius=r)
                    except Exception as e:
                        print(f"Warning: fillet failed at ({x}, {y}) r={r}: {e}")
    return sk.sketch

def build_right_case():
    print("1. Creating outer solid...")
    outer_pts = get_right_case_outer_pts()
    sk_outer = make_filleted_sketch(outer_pts)
    outer_solid = bd.extrude(sk_outer, amount=11.10).moved(bd.Location((0, 0, -11.40)))

    # Fillet outer top and bottom horizontal edges R=0.95
    print("2. Filleting top and bottom outer edges...")
    top_edges = outer_solid.edges().filter_by(lambda e: abs(e.bounding_box().min.Z - (-0.30)) < 0.05 and abs(e.bounding_box().max.Z - (-0.30)) < 0.05)
    bottom_edges = outer_solid.edges().filter_by(lambda e: abs(e.bounding_box().min.Z - (-11.40)) < 0.05 and abs(e.bounding_box().max.Z - (-11.40)) < 0.05)
    try:
        outer_solid = bd.fillet(top_edges + bottom_edges, radius=0.95)
    except Exception as e:
        print(f"Fillet top/bottom warning: {e}, falling back to top only or unfilleted.")
        try:
            outer_solid = bd.fillet(top_edges, radius=0.95)
        except Exception:
            pass

    print("3. Cutting inner cavity...")
    inner_pts = get_right_case_inner_pts()
    sk_inner = make_filleted_sketch(inner_pts)
    inner_solid = bd.extrude(sk_inner, amount=10.40).moved(bd.Location((0, 0, -9.40)))
    body = outer_solid - inner_solid

    print("4. Cutting keyboard mounting holes...")
    left_holes = [
        (-116.2050, -78.5812),
        (-116.2050, -59.5313),
        ( -57.1593, -55.9574),
        ( -57.1659, -95.2499),
    ]
    for hx, hy in left_holes:
        cx = -hx
        body = body - bd.Cylinder(radius=1.10, height=14.0).moved(bd.Location((cx, hy, -12.0)))

    print("5. Cutting USB-C port...")
    with bd.BuildSketch(bd.Plane.XZ.offset(-42.0)) as sk_usb:
        with bd.Locations([( (21.6259 + 31.5659) / 2.0, (-8.66 + -4.50) / 2.0 )]):
            bd.RectangleRounded(31.5659 - 21.6259, -4.50 - (-8.66), radius=0.8)
    usb_solid = bd.extrude(sk_usb.sketch, amount=10.0)
    body = body - usb_solid

    print("6. Cutting TRRS port (L-shaped connector compatible)...")
    # TRRS center at Y = -91.8000, Z = -6.6500.
    # We cut a generous dia 9.5 mm (radius 4.75 mm) opening along X to accommodate L-shaped TRRS plug molds.
    with bd.BuildSketch(bd.Plane.YZ.offset(10.0)) as sk_trrs:
        with bd.Locations([(-91.8000, -6.6500)]):
            bd.Circle(radius=4.75)
    trrs_solid = bd.extrude(sk_trrs.sketch, amount=12.0)
    body = body - trrs_solid

    print("7. Cutting bottom trackball optical window & 4x M2 mounting holes...")
    tb_cx, tb_cy = 23.8125, -109.5375

    # Optical window: 8.0 x 12.0 mm rounded rectangle (R = 1.50 mm)
    with bd.BuildSketch(bd.Plane.XY.offset(-12.0)) as sk_opt:
        with bd.Locations([(tb_cx, tb_cy)]):
            bd.RectangleRounded(8.00, 12.00, radius=1.50)
    opt_solid = bd.extrude(sk_opt.sketch, amount=4.0)
    body = body - opt_solid

    # 4x M2 mounting holes (dia 2.20 mm) at (+-4.50, +-10.00) relative to tb_cx, tb_cy
    tb_screws = [
        (tb_cx - 4.50, tb_cy - 10.00),
        (tb_cx + 4.50, tb_cy - 10.00),
        (tb_cx - 4.50, tb_cy + 10.00),
        (tb_cx + 4.50, tb_cy + 10.00),
    ]
    for sx, sy in tb_screws:
        body = body - bd.Cylinder(radius=1.10, height=4.0).moved(bd.Location((sx, sy, -12.0)))

    solids = body.solids()
    print(f"Result: {len(solids)} solid(s), volume = {body.volume:.2f} mm^3")
    assert len(solids) == 1, f"Expected 1 solid, got {len(solids)}"
    solid = solids[0]
    solid.label = "right_case"
    return solid

if __name__ == "__main__":
    case = build_right_case()
    print("Exporting STEP...")
    bd.export_step(case, str(OUT_STEP))
    print("Exporting STL...")
    bd.export_stl(case, str(OUT_STL))
    print("Done!")
