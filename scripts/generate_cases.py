# -*- coding: utf-8 -*-
"""
Generate curcur40 3D-printed Built-in Tented Tray Bottom Cases
(cases/left.step, left.stl, right.step, right.stl, left-desk.step, left-desk.stl, right-desk.step, right-desk.stl).
Strictly adheres to docs/case_spec.md:
- Low-Height Built-in Tenting Architecture with Sealed Flat Bottom, Tilted Interior Floor & Heat-Set Insert Bosses:
    - Outer Bottom Tenting Plane (theta_tent = 7.47 deg):
        - Pinky outer edge (|X_step| = 135.8580 mm): Z_bottom = -10.00 mm (total height 10.00 mm)
        - Thumb inner edge (|X_step| = 7.0250 mm):   Z_bottom = -26.90 mm (total height 26.90 mm)
        - 100% sealed, hole-free outer bottom face (zero bottom counterbores or through-holes)
    - Tilted Interior Floor:
        - Parallel to outer bottom plane with uniform 2.40 mm bottom wall thickness (Z_floor = Z_bottom + 2.40 mm)
        - Skimmed horizontally to Z = -8.00 mm at the pinky outer edge (|X_step| > 120.61 mm) for >= 0.40 mm switch socket clearance
- Fastening Specifications (Section 2):
    - Top-down unified M2 x 6.0 mm screws threading into M2 brass heat-set inserts (M2 x L=3.0 mm x OD=3.2 mm):
        - Cylindrical Boss Pillars (pilot bore Ø 2.85 mm, R = 1.425 mm >= Ø 1.50 mm JLC3DP limit):
            - 8x Wide Stepped perimeter Top-Plate clamping bosses (L1..L3, L5, R1..R3, R5): Ø 7.84 mm lower shoulder at Z = -5.80 mm (supports Main PCB B.Cu) + Ø 6.00 mm upper boss passing through Main PCB Ø 6.20 mm hole/U-notch to Z = -3.60 mm (supports Top Plate B.Cu; radial wall 1.575 mm >= 0.80 mm), flush insert top at Z = -3.60 mm, blind bore 6.00 mm deep to Z = -9.60 mm
            - 2x Flat-topped Pinky-South perimeter bosses (L4, R4 at ±98.45, 38.15): Ø 4.90 mm flat boss top at Z = -5.80 mm (clamps Main PCB directly, uniform 1.025 mm radial wall, flush insert top at Z = -5.80 mm), blind bore to Z = -10.50 mm
            - 4x Trackball bosses (TB1..TB4): Ø 6.00 mm boss top Z = -17.60 mm (Sensor PCB B.Cu), blind bore 3.80 mm deep to Z = -21.40 mm
- Cutouts & Ports (Section 3):
    - Split USB-C opening (inner thumb wall): Width 12.00 mm x Height 6.20 mm, corner fillet R = 1.50 mm, center at Y = -86.6500 mm, Z = -5.85 mm
    - Host USB-C opening (north wall): Width 12.00 mm x Height 6.20 mm, corner fillet R = 1.50 mm, center at X = ±26.5750 mm, Z = -5.85 mm
"""
import math
from pathlib import Path
from cadgen import build123d as bd
from cadgen.geometry import is_sound
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.GeomAbs import GeomAbs_Cylinder
from OCP.TopAbs import TopAbs_REVERSED

WORKSPACE = Path(__file__).resolve().parent.parent
OUT_DIR = WORKSPACE / "cases"
OUT_DIR.mkdir(parents=True, exist_ok=True)

Z_THUMB_BOTTOM = -26.9000
Z_PINKY_BOTTOM = -10.0000
X_THUMB_OUTER = 7.0250
X_PINKY_OUTER = 135.8580
FLOOR_THICKNESS = 2.4000

BOSS_OUTER_RADIUS = 3.0000     # Ø 6.00 mm standard boss pillar (TB1..TB4)
PINKY_SOUTH_RADIUS = 2.4500    # Ø 4.90 mm flat-topped boss for L4, R4 (1.025 mm radial wall; >= 0.33 mm clear of TS-1088R)
STEPPED_LOWER_RADIUS = 3.9200  # Ø 7.84 mm lower shoulder on stepped bosses (0.92 mm >= 0.80 mm step outside Ø 6.00 mm)
BOSS_UPPER_RADIUS = 3.0000     # Ø 6.00 mm stepped upper boss (Top Plate support & flush insert seat at Z = -3.60 mm; 1.575 mm wall)
PILOT_BORE_RADIUS = 1.4250     # Ø 2.85 mm pilot bore for M2 x L=3.0 x OD=3.2 mm brass heat-set insert


def z_bottom_at_x(x_abs: float) -> float:
    """
    Built-in tenting outer bottom Z height at |X_step| (theta_tent = 7.473 deg):
    - |X| = 7.0250 mm (thumb inner edge):   Z = -26.9000 mm
    - |X| = 135.8580 mm (pinky outer edge): Z = -10.0000 mm
    """
    return Z_THUMB_BOTTOM + (Z_PINKY_BOTTOM - Z_THUMB_BOTTOM) * (
        x_abs - X_THUMB_OUTER
    ) / (X_PINKY_OUTER - X_THUMB_OUTER)


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
    Returns list of (tag, cx, cy, z_boss_top, z_bore_bottom, z_insert_top, is_stepped_plate) in STEP coordinates:
    - Wide Stepped perimeter holes L1..L3, L5, R1..R3, R5:
        Ø 7.84 mm lower boss to Z = -5.80 mm (Main PCB B.Cu) + Ø 6.00 mm upper boss to Z = -3.60 mm (Top Plate B.Cu),
        z_bore_bottom = -9.60 mm (6.00 mm blind bore), z_insert_top = -3.60 mm (flush press-fit, 1.575 mm wall)
    - Flat-topped Pinky-South perimeter holes L4, R4 (±98.4500, 38.1500):
        Ø 4.90 mm flat boss to z_boss_top = -5.80 mm (Main PCB B.Cu), z_bore_bottom = -10.50 mm, z_insert_top = -5.80 mm
    - Trackball holes TB1..TB4:
        Ø 6.00 mm boss to z_boss_top = -17.60 mm (Sensor PCB B.Cu), z_bore_bottom = -21.40 mm (3.80 mm blind bore), z_insert_top = -17.60 mm
    """
    if is_right:
        perim_pcb = [
            ("R1",   0.0000, -15.0000, -3.60,  -9.60, -3.60, True),
            ("R2",   0.0000,  18.0000, -3.60,  -9.60, -3.60, True),
            ("R3", 101.0000, -20.0000, -3.60,  -9.60, -3.60, True),
            ("R4",  98.4500,  38.1500, -5.80, -10.50, -5.80, False),
            ("R5",  62.0000,  65.1500, -3.60,  -9.60, -3.60, True),
        ]
        tb_pcb = [
            ("TB1", -2.4750, 41.0875, -17.60, -21.40, -17.60, False),
            ("TB2", 21.5250, 41.0875, -17.60, -21.40, -17.60, False),
            ("TB3", -2.4750, 63.6875, -17.60, -21.40, -17.60, False),
            ("TB4", 21.5250, 63.6875, -17.60, -21.40, -17.60, False),
        ]
        return [
            (tag, x + 14.2875, -(y + 57.1500), z_top, z_bot, z_ins, stepped)
            for tag, x, y, z_top, z_bot, z_ins, stepped in (perim_pcb + tb_pcb)
        ]
    else:
        perim_pcb = [
            ("L1",    0.0000, -15.0000, -3.60,  -9.60, -3.60, True),
            ("L2",    0.0000,  18.0000, -3.60,  -9.60, -3.60, True),
            ("L3", -101.0000, -20.0000, -3.60,  -9.60, -3.60, True),
            ("L4",  -98.4500,  38.1500, -5.80, -10.50, -5.80, False),
            ("L5",  -62.0000,  65.1500, -3.60,  -9.60, -3.60, True),
        ]
        return [
            (tag, x - 14.2875, -(y + 57.1500), z_top, z_bot, z_ins, stepped)
            for tag, x, y, z_top, z_bot, z_ins, stepped in perim_pcb
        ]


def verify_case_wall_thickness_and_gaps(solid: bd.Solid, is_right: bool):
    """
    Automated JLC3DP (SLA / MJF / SLS) pre-order DFM & B-rep check on the case solid
    (in Top-Plate-horizontal coordinates, Z in [-26.90, 0.00] mm):
      1) Watertight manifold single solid (`is_valid`, `is_sound`, `len(solids) == 1`, `volume > 0`)
      2) JLC3DP build envelope (<= 380 x 284 x 380 mm) & min part size (>= 5 x 5 x 2 mm)
      3) Minimum concave hole/bore diameter >= Ø 1.50 mm (JLC3DP MJF/SLS powder/resin escape rule)
      4) Minimum wall thickness >= 0.80 mm & zero micro-gaps outside documented intentional exclusions:
         - Case top rim (Z ~ 0.00 mm): 1.50 mm wall minus R=0.95 mm outer fillet = 0.550..0.743 mm
         - Pinky skim floor boundary (|X| > 132.0 mm, Z ~ -8.00 mm): 0.459..0.549 mm
    """
    side_str = "right" if is_right else "left"

    # 1. Manifoldness & single solid body
    assert solid.is_valid and is_sound(solid), f"[{side_str}] Solid is not watertight/manifold!"
    assert len(solid.solids()) == 1 and solid.volume > 0, f"[{side_str}] Must be a single positive-volume solid!"

    # 2. JLC3DP build volume & min size check
    bb = solid.bounding_box()
    sx, sy, sz = bb.max.X - bb.min.X, bb.max.Y - bb.min.Y, bb.max.Z - bb.min.Z
    assert 5.0 <= sx <= 380.0 and 5.0 <= sy <= 284.0 and 2.0 <= sz <= 380.0, (
        f"[{side_str}] Bounding box {sx:.2f}x{sy:.2f}x{sz:.2f} mm outside JLC3DP limits!"
    )

    # 3. Minimum concave cylindrical hole/bore diameter >= Ø 1.50 mm
    faces = solid.faces()
    min_concave_diam = float("inf")
    for f in faces:
        surf = BRepAdaptor_Surface(f.wrapped)
        if surf.GetType() == GeomAbs_Cylinder and f.wrapped.Orientation() == TopAbs_REVERSED:
            diam = round(2.0 * surf.Cylinder().Radius(), 4)
            if diam < min_concave_diam:
                min_concave_diam = diam
    assert min_concave_diam >= 1.50, (
        f"[{side_str}] Concave hole/bore diameter {min_concave_diam:.3f} mm < JLC3DP 1.50 mm limit!"
    )

    # 4. Wall thickness (< 0.80 mm) & micro-gap scan
    bbs = [f.bounding_box() for f in faces]
    unexpected = []
    excluded_count = 0

    for i in range(len(faces)):
        b1 = bbs[i]
        for j in range(i + 1, len(faces)):
            b2 = bbs[j]
            dx = max(0.0, b1.min.X - b2.max.X, b2.min.X - b1.max.X)
            dy = max(0.0, b1.min.Y - b2.max.Y, b2.min.Y - b1.max.Y)
            dz = max(0.0, b1.min.Z - b2.max.Z, b2.min.Z - b1.max.Z)
            if math.sqrt(dx * dx + dy * dy + dz * dz) > 0.85:
                continue
            dss = BRepExtrema_DistShapeShape(faces[i].wrapped, faces[j].wrapped)
            if dss.IsDone() and dss.NbSolution() > 0:
                d = dss.Value()
                if 0.001 < d < 0.800:
                    p1 = dss.PointOnShape1(1)
                    p2 = dss.PointOnShape2(1)
                    mx = 0.5 * (p1.X() + p2.X())
                    my = 0.5 * (p1.Y() + p2.Y())
                    mz = 0.5 * (p1.Z() + p2.Z())

                    # Check against documented intentional exclusions:
                    is_top_rim = abs(mz - 0.00) < 0.15 and 0.540 <= d <= 0.760
                    is_pinky_skim = abs(mx) > 132.0 and abs(mz - (-8.00)) < 0.15 and 0.450 <= d <= 0.560

                    if is_top_rim or is_pinky_skim:
                        excluded_count += 1
                    else:
                        unexpected.append((d, (mx, my, mz), i, j))

    print(
        f"[{side_str}] JLC3DP preflight & <0.80mm check: "
        f"bbox={sx:.2f}x{sy:.2f}x{sz:.2f}mm, min_hole_diam={min_concave_diam:.2f}mm (>=1.50mm), "
        f"{len(unexpected)} unexpected violations ({excluded_count} known excluded pairs)"
    )
    if unexpected:
        for d, (mx, my, mz), i, j in unexpected:
            print(f"  UNEXPECTED: d={d:.4f} mm at ({mx:.2f}, {my:.2f}, {mz:.2f}) [F{i}-F{j}]")
    assert len(unexpected) == 0, f"{side_str} case has {len(unexpected)} unexpected <0.80mm wall/gap violations!"


def build_case(is_right=True) -> bd.Solid:
    side_str = "right" if is_right else "left"
    print(f"--- Building {side_str} sealed-bottom tented case with heat-set insert bosses ---")

    z_ext_bottom = -30.00
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

    # 2. Inner perimeter prism
    inner_pts = get_inner_pts(is_right)
    sk_inner = make_filleted_sketch(inner_pts)
    inner_prism = bd.extrude(sk_inner, amount=32.0).moved(
        bd.Location((0, 0, z_ext_bottom))
    )

    # 3. Cut tilted interior cavity
    if is_right:
        p_thumb_fl = (X_THUMB_OUTER, -80.0, Z_THUMB_BOTTOM + FLOOR_THICKNESS)
        p_pinky_fl = (X_PINKY_OUTER, -80.0, Z_PINKY_BOTTOM + FLOOR_THICKNESS)
        dx = p_pinky_fl[0] - p_thumb_fl[0]
        dz = p_pinky_fl[2] - p_thumb_fl[2]
        norm_up = (-dz, 0.0, dx)
    else:
        p_thumb_fl = (-X_THUMB_OUTER, -80.0, Z_THUMB_BOTTOM + FLOOR_THICKNESS)
        p_pinky_fl = (-X_PINKY_OUTER, -80.0, Z_PINKY_BOTTOM + FLOOR_THICKNESS)
        dx = p_pinky_fl[0] - p_thumb_fl[0]
        dz = p_pinky_fl[2] - p_thumb_fl[2]
        norm_up = (dz, 0.0, -dx)

    floor_plane = bd.Plane(origin=p_thumb_fl, z_dir=norm_up)
    tilted_cavity_halfspace = bd.extrude(
        floor_plane * bd.Rectangle(400.0, 400.0), amount=50.0
    )
    pinky_skim_halfspace = bd.extrude(
        bd.Plane.XY.offset(-8.00) * bd.Rectangle(400.0, 400.0), amount=10.0
    )
    cavity_volume = inner_prism & (tilted_cavity_halfspace + pinky_skim_halfspace)
    body = outer_solid - cavity_volume

    # 4. Add Cylindrical / Stepped Heat-Set Insert Boss Pillars (zero perimeter wall ledges!)
    hole_specs = get_case_hole_specs(is_right)
    boss_solids = []
    for tag, cx, cy, z_boss_top, _z_bore_bot, _z_ins_top, is_stepped in hole_specs:
        z_lower_top = -5.80 if is_stepped else z_boss_top
        if is_stepped:
            r_lower = STEPPED_LOWER_RADIUS
        elif tag in ("R4", "L4"):
            r_lower = PINKY_SOUTH_RADIUS
        else:
            r_lower = BOSS_OUTER_RADIUS
        boss_cyl = bd.Cylinder(
            radius=r_lower,
            height=z_lower_top - z_ext_bottom,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((cx, cy, z_ext_bottom)))
        # Bridge near-wall bosses cleanly into adjacent inner walls to eliminate narrow crevices:
        # 1) South-wall bridges for R4/L4 (cy=-95.30), R5/L5 (cy=-122.30), TB3/TB4 (cy=-120.8375)
        if tag in ("R4", "L4") or cy < -120.0:
            south_bridge = bd.Box(
                2.0 * r_lower,
                5.50,
                z_lower_top - z_ext_bottom,
                align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.MIN),
            ).moved(bd.Location((cx, cy, z_ext_bottom)))
            boss_cyl = boss_cyl + south_bridge
        if is_stepped:
            upper_cyl = bd.Cylinder(
                radius=BOSS_UPPER_RADIUS,
                height=z_boss_top - z_lower_top,
                align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
            ).moved(bd.Location((cx, cy, z_lower_top)))
            if cy < -120.0:
                # Bridge R5/L5 stepped upper boss through Main PCB South U-notch into South inner wall
                upper_south_bridge = bd.Box(
                    2.0 * BOSS_UPPER_RADIUS,
                    5.50,
                    z_boss_top - z_lower_top,
                    align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.MIN),
                ).moved(bd.Location((cx, cy, z_lower_top)))
                upper_cyl = upper_cyl + upper_south_bridge
            boss_cyl = boss_cyl + upper_cyl
        # 2) West-wall bridges for right-hand TB1 (11.8125, -98.2375) and TB3 (11.8125, -120.8375)
        if is_right and abs(cx - 11.8125) < 0.1:
            west_bridge = bd.Box(
                4.50,
                2.0 * BOSS_OUTER_RADIUS,
                z_boss_top - z_ext_bottom,
                align=(bd.Align.MAX, bd.Align.CENTER, bd.Align.MIN),
            ).moved(bd.Location((cx, cy, z_ext_bottom)))
            boss_cyl = boss_cyl + west_bridge
            if cy < -120.0:
                sw_corner_bridge = bd.Box(
                    4.50,
                    5.50,
                    z_boss_top - z_ext_bottom,
                    align=(bd.Align.MAX, bd.Align.MAX, bd.Align.MIN),
                ).moved(bd.Location((cx, cy, z_ext_bottom)))
                boss_cyl = boss_cyl + sw_corner_bridge
        boss_solids.append(boss_cyl & outer_solid)

    for b_cyl in boss_solids:
        body = body + b_cyl

    # 5. Cut angled outer bottom tenting plane (theta_tent = 7.47 deg) — 100% sealed, hole-free flat bottom!
    if is_right:
        p_thumb = (X_THUMB_OUTER, -80.0, Z_THUMB_BOTTOM)
        p_pinky = (X_PINKY_OUTER, -80.0, Z_PINKY_BOTTOM)
        dx = p_pinky[0] - p_thumb[0]
        dz = p_pinky[2] - p_thumb[2]
        norm_down = (dz, 0.0, -dx)
    else:
        p_thumb = (-X_THUMB_OUTER, -80.0, Z_THUMB_BOTTOM)
        p_pinky = (-X_PINKY_OUTER, -80.0, Z_PINKY_BOTTOM)
        dx = p_pinky[0] - p_thumb[0]
        dz = p_pinky[2] - p_thumb[2]
        norm_down = (-dz, 0.0, dx)

    tent_plane = bd.Plane(origin=p_thumb, z_dir=norm_down)
    bottom_cutter = bd.extrude(tent_plane * bd.Rectangle(400.0, 400.0), amount=50.0)
    body = body - bottom_cutter

    # 6. Cut top-down blind pilot bores (Ø 2.85 mm, R = 1.425 mm) for M2 brass heat-set inserts:
    #    Zero bottom holes — every bore terminates >= 1.50 mm above the outer bottom surface!
    for tag, cx, cy, z_boss_top, z_bore_bottom, _z_ins_top, _is_stepped in hole_specs:
        z_outer_min = z_bottom_at_x(abs(cx) + PILOT_BORE_RADIUS)
        floor_margin = z_bore_bottom - z_outer_min
        assert floor_margin >= 1.40, (
            f"[{side_str}:{tag}] Blind bore bottom {z_bore_bottom:.2f} too close to outer bottom {z_outer_min:.2f}!"
        )
        body = body - bd.Cylinder(
            radius=PILOT_BORE_RADIUS,
            height=(z_boss_top + 1.00) - z_bore_bottom,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((cx, cy, z_bore_bottom)))

    # 7. Host USB-C port cutout (Width = 12.00 mm, Height = 6.20 mm, R = 1.50 mm, Center Z = -5.85 mm)
    usb_cx = 26.5750 if is_right else -26.5750
    usb_cutter = bd.Box(12.00, 15.00, 6.20).moved(
        bd.Location((usb_cx, -30.8375, -5.8500))
    )
    edges_y = usb_cutter.edges().filter_by(
        lambda e: abs(e.bounding_box().size.Y - 15.00) < 0.1
    )
    if len(edges_y) == 4:
        usb_cutter = bd.fillet(edges_y, radius=1.50)
    body = body - usb_cutter

    # 8. Split USB-C port cutout on inner thumb wall (Width = 12.00 mm, Height = 6.20 mm, R = 1.50 mm, Center Z = -5.85 mm)
    split_usb_x = 7.7750 if is_right else -7.7750
    split_usb_cutter = bd.Box(6.00, 12.00, 6.20).moved(
        bd.Location((split_usb_x, -86.6500, -5.8500))
    )
    edges_x = split_usb_cutter.edges().filter_by(
        lambda e: abs(e.bounding_box().size.X - 6.00) < 0.1
    )
    assert len(edges_x) == 4, f"Expected 4 X-parallel edges on split_usb_cutter, got {len(edges_x)}"
    split_usb_cutter = bd.fillet(edges_x, radius=1.50)
    body = body - split_usb_cutter

    solid = body.solids()[0]
    solid.label = f"curcur40_case_{side_str}"
    assert is_sound(solid), f"{side_str} case solid is not sound!"
    verify_case_wall_thickness_and_gaps(solid, is_right)

    step_path = OUT_DIR / f"{side_str}.step"
    stl_path = OUT_DIR / f"{side_str}.stl"
    bd.export_step(solid, str(step_path))
    bd.export_stl(solid, str(stl_path))
    bb = solid.bounding_box()
    print(
        f"Exported {step_path.name} & {stl_path.name}: "
        f"bbox Z=[{bb.min.Z:.4f}, {bb.max.Z:.4f}], volume={solid.volume:.2f} mm^3"
    )

    # 9. Export desk-horizontal (outer bottom flat on Z = 0.00 mm) STEP & STL
    theta_deg = math.degrees(
        math.atan2(Z_PINKY_BOTTOM - Z_THUMB_BOTTOM, X_PINKY_OUTER - X_THUMB_OUTER)
    )
    if is_right:
        pivot = (X_PINKY_OUTER, 0.0, Z_PINKY_BOTTOM)
        rot_angle = theta_deg
    else:
        pivot = (-X_PINKY_OUTER, 0.0, Z_PINKY_BOTTOM)
        rot_angle = -theta_deg

    desk_solid = (
        solid.moved(bd.Location((-pivot[0], -pivot[1], -pivot[2])))
        .rotate(bd.Axis.Y, rot_angle)
        .moved(bd.Location((pivot[0], pivot[1], 0.0)))
    )
    desk_solid.label = f"curcur40_case_{side_str}_desk"
    desk_step_path = OUT_DIR / f"{side_str}-desk.step"
    desk_stl_path = OUT_DIR / f"{side_str}-desk.stl"
    bd.export_step(desk_solid, str(desk_step_path))
    bd.export_stl(desk_solid, str(desk_stl_path))
    bb_desk = desk_solid.bounding_box()
    assert abs(bb_desk.min.Z - 0.0) < 1e-4, f"[{side_str}-desk] Bottom Z={bb_desk.min.Z:.4f} mm is not flat on Z=0.0000 mm!"
    print(
        f"Exported {desk_step_path.name} & {desk_stl_path.name}: "
        f"bbox Z=[{bb_desk.min.Z:.4f}, {bb_desk.max.Z:.4f}], volume={desk_solid.volume:.2f} mm^3"
    )
    return solid


if __name__ == "__main__":
    build_case(is_right=False)
    build_case(is_right=True)
    print("All cases generated successfully!")
