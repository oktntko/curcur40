# -*- coding: utf-8 -*-
"""
Generate curcur40 3D-printed Built-in Tented Tray Bottom Cases
(cases/left.step, left.stl, right.step, right.stl).
Strictly adheres to docs/case_spec.md:
- Low-Height Built-in Tenting Architecture with Tilted Interior Floor & Cylindrical Boss Pillars:
    - Outer Bottom Tenting Plane (theta_tent = 7.47 deg):
        - Pinky outer edge (|X_step| = 135.8580 mm): Z_bottom = -10.00 mm (total height 10.00 mm)
        - Thumb inner edge (|X_step| = 7.0250 mm):   Z_bottom = -26.90 mm (total height 26.90 mm)
    - Tilted Interior Floor:
        - Parallel to outer bottom plane with uniform 2.40 mm bottom wall thickness (Z_floor = Z_bottom + 2.40 mm)
        - Skimmed horizontally to Z = -8.00 mm at the pinky outer edge (|X_step| > 120.61 mm) for >= 0.40 mm switch socket clearance (preserving 2.00 to 2.40 mm bottom thickness)
        - Zero step pockets or recesses on the floor (both PMW3360 and J1 clear the smooth tilted floor naturally)
- Fastening Specifications (Section 2):
    - All 14 mounting points use unified M2 5.50 mm Female-Female Standoffs (OD Ø 3.00 mm) and M2 x 4.0 mm screws (28 pcs)
    - Cylindrical Boss Pillars (OD Ø 6.80 mm, R = 3.40 mm) rise from the tilted interior floor to support each standoff:
        - 10x Perimeter bosses (L1..L5, R1..R5): boss top Z = -9.10 mm, counterbore ceiling Z = -11.50 mm (2.40 mm clamping floor)
        - 4x Trackball bosses (TB1..TB4):        boss top Z = -17.60 mm (directly supporting Sensor PCB B.Cu and 5.50 mm standoff), counterbore ceiling Z = -20.00 mm (2.40 mm clamping floor)
    - Screw through-holes: Ø 2.40 mm (radius 1.20 mm)
    - Bottom screw head counterbores: Ø 4.60 mm (radius 2.30 mm) from angled bottom up to z_boss_top - 2.40 mm
- Cutouts & Ports (Section 3):
    - Split USB-C opening (inner thumb wall): Width 12.00 mm x Height 6.20 mm, corner fillet R = 1.50 mm, center at Y = -86.6500 mm, Z = -5.85 mm (concentric with mid-mount J2 / rJ2 TYPE-C-31-M-13C; top edge Z = -2.75 mm hides upper half of Top Plate)
    - Host USB-C opening (north wall): Width 12.00 mm x Height 6.20 mm, corner fillet R = 1.50 mm, center at X = ±26.5750 mm, Z = -5.85 mm (concentric with mid-mount J1 / rJ1 TYPE-C-31-M-13C; top edge Z = -2.75 mm hides upper half of Top Plate)
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
    Returns list of (cx, cy, z_boss_top) in STEP coordinates:
    - Perimeter holes (L1..L5, R1..R5): z_boss_top = -9.10 mm (counterbore ceiling Z = -11.50 mm, 2.40 mm floor)
    - Trackball holes (TB1..TB4):       z_boss_top = -17.60 mm (counterbore ceiling Z = -20.00 mm, 2.40 mm floor)
      All 14 holes use M2 5.50 mm Female-Female standoffs!
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
        specs += [(x + 14.2875, -(y + 57.1500), -17.60) for x, y in tb_pcb]
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
         - R3/L3 boss top step height above tilted floor (|X| ~ 118.7 mm, Y ~ -37.15 mm): 0.746 mm
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
                    is_r3_l3_step = 118.0 <= abs(mx) <= 119.5 and abs(my - (-37.15)) < 0.5 and 0.740 <= d <= 0.760

                    if is_top_rim or is_pinky_skim or is_r3_l3_step:
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
    print(f"--- Building {side_str} low-height tented case with boss pillars ---")

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

    # 2. Inner perimeter prism (extruded across full Z range to intersect with tilted floor & bosses)
    inner_pts = get_inner_pts(is_right)
    sk_inner = make_filleted_sketch(inner_pts)
    inner_prism = bd.extrude(sk_inner, amount=32.0).moved(
        bd.Location((0, 0, z_ext_bottom))
    )

    # 3. Cut tilted interior cavity:
    #    - Tilted interior floor plane is parallel to the outer bottom plane, offset upward by +2.40 mm in Z.
    #    - At the pinky outer edge (|X_step| > 119.96 mm), skimmed horizontally at Z = -8.00 mm so hotswap sockets
    #      (bottom Z = -7.60 mm) have >= 0.40 mm clearance while preserving 2.00 to 2.40 mm bottom wall thickness.
    if is_right:
        p_thumb_fl = (X_THUMB_OUTER, -80.0, Z_THUMB_BOTTOM + FLOOR_THICKNESS)
        p_pinky_fl = (X_PINKY_OUTER, -80.0, Z_PINKY_BOTTOM + FLOOR_THICKNESS)
        dx = p_pinky_fl[0] - p_thumb_fl[0]
        dz = p_pinky_fl[2] - p_thumb_fl[2]
        # Upward normal into the cavity
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

    # 4. Add Cylindrical Boss Pillars (OD Ø 6.80 mm, R = 3.40 mm) rising from tilted floor up to z_boss_top
    #    Clipped to inner_prism + outer walls (i.e., outer_solid) so bosses near walls merge cleanly without protruding outside!
    hole_specs = get_case_hole_specs(is_right)
    boss_solids = []
    for cx, cy, z_boss_top in hole_specs:
        boss_cyl = bd.Cylinder(
            radius=3.40,
            height=z_boss_top - z_ext_bottom,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((cx, cy, z_ext_bottom)))
        # Bridge near-wall bosses cleanly into adjacent inner walls to eliminate narrow un-cleanable crevices:
        # 1) South-wall bridges for R4/L4 (cy=-95.15), R5/L5 (cy=-121.75), TB3 (cy=-120.8375), TB4 (cy=-120.8375)
        if abs(cy - (-95.1500)) < 0.1 or cy < -120.0:
            south_bridge = bd.Box(
                6.80,
                5.50,
                z_boss_top - z_ext_bottom,
                align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.MIN),
            ).moved(bd.Location((cx, cy, z_ext_bottom)))
            boss_cyl = boss_cyl + south_bridge
        # 2) West-wall bridges for right-hand TB1 (11.8125, -98.2375) and TB3 (11.8125, -120.8375)
        if is_right and abs(cx - 11.8125) < 0.1:
            west_bridge = bd.Box(
                4.50,
                6.80,
                z_boss_top - z_ext_bottom,
                align=(bd.Align.MAX, bd.Align.CENTER, bd.Align.MIN),
            ).moved(bd.Location((cx, cy, z_ext_bottom)))
            boss_cyl = boss_cyl + west_bridge
        boss_solids.append(boss_cyl & outer_solid)

    for b_cyl in boss_solids:
        body = body + b_cyl

    # 4b. Add 4x Wall-Mounted Main PCB Support Ledges (North, South, Outer/Pinky, Inner/Thumb-Index)
    #     Top surface at Z = -5.80 mm (supporting Main PCB B.Cu bottom plane by 1.00 mm overlap at component-free edges),
    #     with a 0.85 mm vertical tip face and 45-deg sloped underside so no < 0.80 mm thin tip or spiky floor pillar exists.
    sgn = 1.0 if is_right else -1.0
    ledge_solids = []

    # (a) North wall ledge: |X_step| in [71.2875, 81.2875] (width 10.0 mm), Y_step from -31.8375 (inside wall) to -33.8375 (1.0 mm under PCB)
    pts_n = [(-31.8375, -5.80), (-33.8375, -5.80), (-33.8375, -6.65), (-31.8375, -8.65)]
    with bd.BuildSketch(bd.Plane.YZ) as sk_n:
        bd.Polygon(pts_n, align=None)
    ledge_n = bd.extrude(sk_n.sketch, amount=10.0 * sgn).moved(bd.Location((sgn * 71.2875, 0, 0)))
    ledge_solids.append(ledge_n & outer_solid)

    # (b) South wall ledge: |X_step| in [82.2875, 92.2875] (width 10.0 mm), Y_step from -125.6500 (inside wall) to -123.6500 (1.0 mm under PCB)
    pts_s = [(-125.6500, -5.80), (-123.6500, -5.80), (-123.6500, -6.65), (-125.6500, -8.65)]
    with bd.BuildSketch(bd.Plane.YZ) as sk_s:
        bd.Polygon(pts_s, align=None)
    ledge_s = bd.extrude(sk_s.sketch, amount=10.0 * sgn).moved(bd.Location((sgn * 82.2875, 0, 0)))
    ledge_solids.append(ledge_s & outer_solid)

    # (c) Outer (Pinky) wall ledge: Y_step in [-65.1500, -55.1500] (length 10.0 mm), |X_step| from 134.8580 (inside wall) to 132.3500 (1.0 mm under PCB)
    #     Extended down to Z = -8.50 mm so it merges completely into the tilted/skimmed floor without any 0.06 mm undercut gap.
    pts_o = [(sgn * 134.8580, -5.80), (sgn * 132.3500, -5.80), (sgn * 132.3500, -8.50), (sgn * 134.8580, -8.50)]
    with bd.BuildSketch(bd.Plane.XZ) as sk_o:
        bd.Polygon(pts_o, align=None)
    ledge_o = bd.extrude(sk_o.sketch, amount=10.0).moved(bd.Location((0, -55.1500, 0)))
    ledge_solids.append(ledge_o & outer_solid)

    # (d) Inner (Thumb/Index) wall ledge: Y_step in [-64.1500, -54.1500] (length 10.0 mm), |X_step| from 8.0250 (inside wall) to 10.0250 (1.0 mm under PCB)
    pts_i = [(sgn * 8.0250, -5.80), (sgn * 10.0250, -5.80), (sgn * 10.0250, -6.65), (sgn * 8.0250, -8.65)]
    with bd.BuildSketch(bd.Plane.XZ) as sk_i:
        bd.Polygon(pts_i, align=None)
    ledge_i = bd.extrude(sk_i.sketch, amount=10.0).moved(bd.Location((0, -54.1500, 0)))
    ledge_solids.append(ledge_i & outer_solid)

    for l_sol in ledge_solids:
        body = body + l_sol

    # 5. Cut angled outer bottom tenting plane (theta_tent = 7.47 deg):
    #    Z_bottom(|X|) = -26.90 at |X|=7.0250 mm, -10.00 at |X|=135.8580 mm
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

    # 6. Cut M2 mounting holes & deep bottom counterbores:
    #    Unified 2.40 mm solid clamping floor thickness at all 14 holes!
    #    - z_cb_ceil = z_boss_top - 2.40 mm (-11.50 mm for perimeter holes, -20.00 mm for TB1..TB4)
    #    - Ø 2.40 mm through-hole + Ø 4.60 mm deep bottom counterbore up to z_cb_ceil
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

    # 7. USB-C port cutout (Section 3.2: Width = 12.00 mm, Height = 6.20 mm, R = 1.50 mm, Center Z = -5.85 mm)
    #    Concentric with mid-mount TYPE-C-31-M-13C (center Z = -5.87 mm); top edge at Z = -2.75 mm hides upper half of Top Plate
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

    # 8. Split USB-C port cutout on inner thumb wall (Section 3.1: Width = 12.00 mm, Height = 6.20 mm, R = 1.50 mm,
    #    Center Y = -86.6500 mm, Center Z = -5.8500 mm; concentric with mid-mount J2 / rJ2 TYPE-C-31-M-13C)
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

    # 9. Reuse the exact generated solid to export desk-horizontal (outer bottom flat on Z = 0.00 mm) STEP & STL
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
