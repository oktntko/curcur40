import math
from pathlib import Path
from cadgen import build123d as bd
from cadgen.geometry import is_sound, overlap_volume

WORKSPACE = Path(r"c:\Users\oktnt\workspace\curcur40")
CASES_DIR = WORKSPACE / "cases" / "curcur40"

# ==============================================================================
# 1. Trackball Cup with 120-Degree Claws & 1.20mm Flat Mounting Ears
# ==============================================================================
def make_trackball_cup() -> bd.Solid:
    """
    Trackball Cup (25mm ball) with:
    - 3x 120-degree Retaining Claws at 90.0, 210.0, 330.0 deg (rising to Z = 20.20 mm).
    - Snap nubs at Z = 19.50 mm (R = 13.14 mm).
    - Clean rim at Z = 14.00 mm (leaving ample ball exposure).
    - LM19-LSI lens pocket (Z = -0.50 to 4.85 mm, 19.60 x 22.20 mm).
    - Optical peephole (Z = 4.80 to 8.00 mm, 9.00 x 11.00 mm).
    - 3x Ceramic bearing pockets (Ø2.00 mm balls at elevation 52 deg, azim 90, 210, 330 deg).
    - 4x Mounting Ears at (+/-12.00, +/-11.30 mm):
        * Height / thickness = exactly 1.20 mm (Z = 0.00 to 1.20 mm)
        * NO counterbore (completely flat top surface)
        * Ø2.30 mm through-holes for M2 screws
    """
    z_base = 0.00
    z_rim = 14.00
    z_claw_top = 20.20
    r_outer = 14.00
    r_inner = 12.85
    z_ball_center = 18.30
    ear_th = 1.20  # Flat ear thickness: 1.20 mm

    # 1. Main cylindrical body
    cup = bd.Cylinder(
        radius=r_outer,
        height=z_rim - z_base,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
    ).moved(bd.Location((0, 0, z_base)))

    # 2. Add 4 mounting ears at (+/-12.00, +/-11.30 mm) with thickness = 1.20 mm
    ear_coords = [
        (-12.00, -11.30),
        ( 12.00, -11.30),
        (-12.00,  11.30),
        ( 12.00,  11.30),
    ]
    with bd.BuildPart() as ears_bp:
        with bd.BuildSketch(bd.Plane.XY.offset(0.00)):
            bd.Circle(radius=r_outer)
            for sx, sy in ear_coords:
                with bd.Locations([(sx, sy)]):
                    bd.Circle(radius=2.40)
                with bd.Locations([(sx / 2, sy / 2)]):
                    ang = math.degrees(math.atan2(sy, sx))
                    bd.Rectangle(math.hypot(sx, sy), 4.80, rotation=ang)
        bd.extrude(amount=ear_th)
    cup = cup + ears_bp.part

    # 3. Add 3 claw pillars at 120 deg (90.0, 210.0, 330.0 deg)
    w_claw = 4.20
    th_claw = 2.40
    for th_deg in (90.0, 210.0, 330.0):
        th_rad = math.radians(th_deg)
        with bd.BuildPart() as claw_bp:
            with bd.BuildSketch(bd.Plane.XY.offset(13.00)):
                with bd.Locations([(13.50 * math.cos(th_rad), 13.50 * math.sin(th_rad))]):
                    bd.Rectangle(th_claw, w_claw, rotation=th_deg)
            bd.extrude(amount=z_claw_top - 13.00)
        cup = cup + claw_bp.part

    # 4. Lens pocket (Z = -0.50 to 4.85 mm)
    with bd.BuildPart() as lens_pocket_bp:
        with bd.BuildSketch(bd.Plane.XY.offset(-0.50)):
            bd.RectangleRounded(19.60, 22.20, 7.50)
        bd.extrude(amount=5.35)
    cup = cup - lens_pocket_bp.part

    # 5. Peephole (Z = 4.80 to 8.00 mm)
    with bd.BuildPart() as peephole_bp:
        with bd.BuildSketch(bd.Plane.XY.offset(4.80)):
            bd.RectangleRounded(9.00, 11.00, 3.00)
        bd.extrude(amount=5.00)
    cup = cup - peephole_bp.part

    # 6. Inner spherical cavity
    cup = cup - bd.Sphere(radius=r_inner).moved(bd.Location((0, 0, z_ball_center)))

    # 7. Claws arch / dome
    r_arch = w_claw / 2.0
    z_arch_axis = z_claw_top - r_arch
    for th_deg in (90.0, 210.0, 330.0):
        th_rad = math.radians(th_deg)
        with bd.BuildPart() as arch_bp:
            with bd.BuildSketch(bd.Plane.XY.offset(z_arch_axis)):
                with bd.Locations([(13.50 * math.cos(th_rad), 13.50 * math.sin(th_rad))]):
                    bd.Rectangle(th_claw + 2.0, w_claw + 4.0, rotation=th_deg)
            bd.extrude(amount=r_arch + 1.0)
            cyl = bd.Cylinder(radius=r_arch, height=th_claw + 6.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))
            cyl = cyl.rotate(bd.Axis.Y, 90).rotate(bd.Axis.Z, th_deg)
            cyl = cyl.moved(bd.Location((13.50 * math.cos(th_rad), 13.50 * math.sin(th_rad), z_arch_axis)))
            arch_bp.part = arch_bp.part - cyl
        cup = cup - arch_bp.part

    # 8. Snap nubs at (90.0, 210.0, 330.0 deg)
    for az_deg in (90.0, 210.0, 330.0):
        az_rad = math.radians(az_deg)
        r_nub = 13.14
        z_nub = 19.50
        nx = r_nub * math.cos(az_rad)
        ny = r_nub * math.sin(az_rad)
        nub = bd.Sphere(radius=0.70).moved(bd.Location((nx, ny, z_nub)))
        cup = cup + nub

    # 9. Inner lead-in chamfer
    with bd.BuildPart() as leadin:
        with bd.BuildSketch(bd.Plane.XY.offset(19.30)):
            bd.Circle(radius=12.20)
        with bd.BuildSketch(bd.Plane.XY.offset(20.40)):
            bd.Circle(radius=13.60)
        bd.loft()
    cup = cup - leadin.part

    # 10. Trim outer cylinder
    with bd.BuildPart() as trim_bp:
        with bd.BuildSketch(bd.Plane.XY.offset(-1.0)):
            bd.Circle(radius=30.0)
            bd.Circle(radius=r_outer, mode=bd.Mode.SUBTRACT)
        bd.extrude(amount=25.0)
    cup = cup - trim_bp.part

    # 11. Rim bevel
    with bd.BuildPart() as rim_bevel:
        with bd.BuildSketch(bd.Plane.XY.offset(13.20)):
            bd.Circle(radius=11.80)
        with bd.BuildSketch(bd.Plane.XY.offset(14.20)):
            bd.Circle(radius=13.20)
        bd.loft()
    cup = cup - rim_bevel.part

    # 12. 3x Bearing pockets
    r_orbit = 13.50
    elev_rad = math.radians(52.0)
    for az_deg in (90.0, 210.0, 330.0):
        az_rad = math.radians(az_deg)
        bx = r_orbit * math.sin(elev_rad) * math.cos(az_rad)
        by = r_orbit * math.sin(elev_rad) * math.sin(az_rad)
        bz = z_ball_center - r_orbit * math.cos(elev_rad)
        pocket = bd.Sphere(radius=1.03).moved(bd.Location((bx, by, bz)))
        cup = cup - pocket

    # 13. 4x M2 through holes (dia 2.30 mm, NO counterbore!)
    for sx, sy in ear_coords:
        cup = cup - bd.Cylinder(radius=1.15, height=5.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((sx, sy, -1.0)))

    solid = cup.solids()[0]
    solid.label = "Trackball_Cup"
    return solid


# ==============================================================================
# 2. Right Case with 5.5mm Spacer Bosses & 1.0mm Deep Bottom Counterbores
# ==============================================================================
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

def build_right_case() -> bd.Solid:
    print("--- Building Right Case ---")
    outer_pts = get_outer_pts(True)
    sk_outer = make_filleted_sketch(outer_pts)
    outer_solid = bd.extrude(sk_outer, amount=12.30).moved(bd.Location((0, 0, -12.60)))

    top_edges = outer_solid.edges().filter_by(lambda e: abs(e.bounding_box().min.Z - (-0.30)) < 0.05 and abs(e.bounding_box().max.Z - (-0.30)) < 0.05)
    bottom_edges = outer_solid.edges().filter_by(lambda e: abs(e.bounding_box().min.Z - (-12.60)) < 0.05 and abs(e.bounding_box().max.Z - (-12.60)) < 0.05)
    try:
        outer_solid = bd.fillet(top_edges + bottom_edges, radius=0.95)
    except Exception:
        try:
            outer_solid = bd.fillet(top_edges, radius=0.95)
        except Exception:
            pass

    # Inner cavity (Z = -9.40 to +1.00)
    inner_pts = get_inner_pts(True)
    sk_inner = make_filleted_sketch(inner_pts)
    inner_solid = bd.extrude(sk_inner, amount=10.40).moved(bd.Location((0, 0, -9.40)))
    body = outer_solid - inner_solid

    # Perimeter Standoff Bosses and Holes
    case_holes = [
        (114.2875, -34.6500),
        ( 38.1000, -34.6500),
        (112.2875, -95.1500),
    ]
    for cx, cy in case_holes:
        boss = bd.Cylinder(
            radius=3.00,
            height=2.20,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((cx, cy, -9.60)))
        body = body + boss

        body = body - bd.Cylinder(
            radius=1.15,
            height=20.0,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((cx, cy, -15.0)))
        body = body - bd.Cylinder(
            radius=2.25,
            height=1.00,  # 1.00 mm deep counterbore for 0.8mm screw head
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((cx, cy, -12.80)))

    # USB-C port cutout
    usb_cutter = bd.Box(11.50, 15.00, 6.50).moved(bd.Location((26.5750, -30.8375, -4.2500)))
    edges_y = usb_cutter.edges().filter_by(lambda e: abs(e.bounding_box().size.Y - 15.00) < 0.1)
    if len(edges_y) == 4:
        usb_cutter = bd.fillet(edges_y, radius=1.50)
    body = body - usb_cutter

    # TRRS port cutout
    trrs_cutter = bd.Cylinder(radius=3.00, height=20.0).rotate(bd.Axis.Y, 90).moved(bd.Location((7.0250, -91.8000, -4.2500)))
    body = body - trrs_cutter

    # Trackball Sensor Pocket & 4x M2 5.5mm Spacer Bosses
    tb_cx, tb_cy = 23.8125, -109.5375

    # 1. Carve sensor component pocket from Z = -11.90 to -8.90 mm
    with bd.BuildPart() as recess_bp:
        with bd.BuildSketch(bd.Plane.XY.offset(-11.90)):
            with bd.Locations([(tb_cx, tb_cy)]):
                bd.RectangleRounded(28.50, 29.00, 2.20)
        bd.extrude(amount=3.00)
    body = body - recess_bp.part

    # 2. Add 4x M2 Spacer-Support Bosses
    # PCB bottom is at Z = -5.00 mm. Spacer is 5.50 mm length.
    # Therefore boss top (spacer seat) is at: Z = -5.00 - 5.50 = -10.50 mm!
    # Boss rises from Z = -12.00 up to Z = -10.50 mm (height = 1.50 mm, radius = 2.75 mm / dia 5.50 mm).
    tb_screws = [
        (tb_cx - 12.00, tb_cy - 11.30),
        (tb_cx + 12.00, tb_cy - 11.30),
        (tb_cx - 12.00, tb_cy + 11.30),
        (tb_cx + 12.00, tb_cy + 11.30),
    ]
    for sx, sy in tb_screws:
        tb_boss = bd.Cylinder(
            radius=2.75,
            height=1.50,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((sx, sy, -12.00)))
        body = body + tb_boss

    # 3. Drill 4x M2 through-holes (Ø2.30 mm) and bottom counterbores (Ø4.50 mm)
    # Counterbore: from Z = -12.60 to -11.60 mm (depth 1.00 mm, leaving 1.10 mm seat thickness to -10.50 mm).
    # Thread engagement into 5.5mm spacer = 4.00 mm - 1.10 mm = 2.90 mm!
    for sx, sy in tb_screws:
        body = body - bd.Cylinder(
            radius=1.15,
            height=20.0,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((sx, sy, -15.0)))
        body = body - bd.Cylinder(
            radius=2.25,
            height=1.20,  # from -12.80 to -11.60 mm (depth = 1.00 mm below -12.60 mm bottom)
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((sx, sy, -12.80)))

    solid = body.solids()[0]
    solid.label = "right_case"
    return solid

if __name__ == "__main__":
    print("=== Building Trackball Cup ===")
    cup = make_trackball_cup()
    print(f"Cup valid={cup.is_valid}, sound={is_sound(cup)}, volume={cup.volume:.2f} mm^3")
    bd.export_step(cup, str(CASES_DIR / "trackball-cup.step"))
    bd.export_stl(cup, str(CASES_DIR / "trackball-cup.stl"))

    print("\n=== Building Right Case ===")
    case = build_right_case()
    print(f"Right Case valid={case.is_valid}, sound={is_sound(case)}, volume={case.volume:.2f} mm^3")
    bd.export_step(case, str(CASES_DIR / "right.step"))
    bd.export_stl(case, str(CASES_DIR / "right.stl"))
    print("\nDone exporting STEP and STL files!")
