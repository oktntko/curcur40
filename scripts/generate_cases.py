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
        - Right Case local JST-SH `J1` (`SM06B-SRSS-TB` + mated `SHR-06V-S-B` + wire exit) relief pocket:
          15.50 x 11.60 mm (R = 1.50 mm) centered at (38.2500, -109.5375) mm (X in [30.50, 46.00], Y in [-115.3375, -103.7375]),
          parallel to outer bottom with exact 1.40 mm solid remaining bottom wall thickness (100% sealed exterior)
- Fastening & Hidden Support Specifications (Section 2 — Switch-Retained Top Plate Architecture / 案1A + 6-Point Valley Layout):
    - Top-down unified M2 x 6.0 mm screws threading into M2 brass heat-set inserts (M2 x L=3.0 mm x OD=3.2 mm):
        - Cylindrical Boss Pillars (pilot bore Ø 2.85 mm, R = 1.425 mm >= Ø 1.50 mm JLC3DP limit):
            - 12x Compact Flat-Topped Key-Valley PCB Bosses (L1..L6 on Left, R1..R6 on Right, 100% L-R symmetric, zero outer-margin bosses):
              Ø 5.20 mm flat boss top at Z = -5.80 mm (supports & clamps Main PCB directly via M2 x 6.0 mm screws passing through Top Plate Ø 4.40 mm screw-head clearance holes; uniform 1.175 mm radial wall >= 0.80 mm, flush insert top at Z = -5.80 mm), blind bores to Z = -11.80 mm (L1,L4,L5,L6,R1,R4,R5,R6) and -11.00 mm (L2,L3,R2,R3)
            - 4x Trackball Bosses (TB1..TB4): Ø 6.00 mm boss top Z = -17.60 mm (Sensor PCB B.Cu), blind bore 3.80 mm deep to Z = -21.40 mm
        - 3x Symmetric Hidden Inner-Wall PCB Support Shelves per case (`NW_HostUSB_Shelf`, `NE_HostUSB_Shelf`, `W_SplitUSB_Shelf`):
            - Full-height vertical pilasters integrated into North & Inner-West walls from tilted interior floor up to Z = -5.80 mm (2.00 mm inward protrusion = 1.50 mm solid shelf overlap under Main PCB B.Cu), preventing downward PCB flexing during Host/Split USB-C cable insertion with zero top/exterior visibility.
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
J1_POCKET_WALL_THICKNESS = 1.4000  # Exact 1.40 mm perpendicular solid bottom wall under Right Sensor PCB J1 + SHR-06V-S-B

BOSS_OUTER_RADIUS = 3.0000     # Ø 6.00 mm boss pillar for Trackball bosses (TB1..TB4; 1.575 mm radial wall)
PERIM_BOSS_RADIUS = 2.6000     # Ø 5.20 mm compact flat-topped boss for all 12 key-valley PCB holes (L1..L6, R1..R6; 1.175 mm radial wall)
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
    Returns list of (tag, cx, cy, z_boss_top, z_bore_bottom, z_insert_top, r_boss) in STEP coordinates:
    - 12x Compact Flat-Topped Key-Valley PCB Bosses L1..L6, R1..R6 (100% L-R symmetric):
        Ø 5.20 mm (R = 2.60 mm, 1.175 mm radial wall) flat boss to z_boss_top = -5.80 mm (Main PCB B.Cu),
        z_insert_top = -5.80 mm (flush press-fit, zero stepped upper shelf),
        blind bores: -11.80 mm (L1, L4, L5, L6, R1, R4, R5, R6), -11.00 mm (L2, L3, R2, R3 at ±100.5000)
    - 4x Trackball Bosses TB1..TB4:
        Ø 6.00 mm (R = 3.00 mm) boss to z_boss_top = -17.60 mm (Sensor PCB B.Cu),
        z_bore_bottom = -21.40 mm (3.80 mm blind bore), z_insert_top = -17.60 mm
    """
    if is_right:
        perim_pcb = [
            ("R1",  42.2500,   0.0000, -5.80, -11.80, -5.80, PERIM_BOSS_RADIUS),
            ("R2", 100.5000,   2.5000, -5.80, -11.00, -5.80, PERIM_BOSS_RADIUS),
            ("R3", 100.5000,  21.5000, -5.80, -11.00, -5.80, PERIM_BOSS_RADIUS),
            ("R4",  21.5000,  29.2500, -5.80, -11.80, -5.80, PERIM_BOSS_RADIUS),
            ("R5",  34.5000,  42.0000, -5.80, -11.80, -5.80, PERIM_BOSS_RADIUS),
            ("R6",  60.5000,  42.5000, -5.80, -11.80, -5.80, PERIM_BOSS_RADIUS),
        ]
        tb_pcb = [
            ("TB1", -2.4750, 41.0875, -17.60, -21.40, -17.60, BOSS_OUTER_RADIUS),
            ("TB2", 21.5250, 41.0875, -17.60, -21.40, -17.60, BOSS_OUTER_RADIUS),
            ("TB3", -2.4750, 63.6875, -17.60, -21.40, -17.60, BOSS_OUTER_RADIUS),
            ("TB4", 21.5250, 63.6875, -17.60, -21.40, -17.60, BOSS_OUTER_RADIUS),
        ]
        return [
            (tag, x + 14.2875, -(y + 57.1500), z_top, z_bot, z_ins, r_b)
            for tag, x, y, z_top, z_bot, z_ins, r_b in (perim_pcb + tb_pcb)
        ]
    else:
        perim_pcb = [
            ("L1",  -42.2500,   0.0000, -5.80, -11.80, -5.80, PERIM_BOSS_RADIUS),
            ("L2", -100.5000,   2.5000, -5.80, -11.00, -5.80, PERIM_BOSS_RADIUS),
            ("L3", -100.5000,  21.5000, -5.80, -11.00, -5.80, PERIM_BOSS_RADIUS),
            ("L4",  -21.5000,  29.2500, -5.80, -11.80, -5.80, PERIM_BOSS_RADIUS),
            ("L5",  -34.5000,  42.0000, -5.80, -11.80, -5.80, PERIM_BOSS_RADIUS),
            ("L6",  -60.5000,  42.5000, -5.80, -11.80, -5.80, PERIM_BOSS_RADIUS),
        ]
        return [
            (tag, x - 14.2875, -(y + 57.1500), z_top, z_bot, z_ins, r_b)
            for tag, x, y, z_top, z_bot, z_ins, r_b in perim_pcb
        ]


def build_usbc_support_pilasters(is_right: bool, z_ext_bottom: float) -> list[bd.Solid]:
    """
    Build 3 symmetric hidden inner-wall PCB support shelves (top face Z = -5.8000 mm = Main PCB B.Cu)
    flanking Host USB-C (J1/rJ1) on the North inner wall and Split USB-C (J2/rJ2) on the Inner-West wall:
      1. NW_HostUSB_Shelf: |X| in [7.8000, 18.5000],  Y in [-34.3375, -31.6000] (fills NW corner + West of J1/rJ1)
      2. NE_HostUSB_Shelf: |X| in [34.6500, 44.6500], Y in [-34.3375, -31.6000] (East of J1/rJ1)
      3. W_SplitUSB_Shelf: |X| in [7.8000, 10.5250],  Y in [-78.5000, -64.5000] (North of J2/rJ2)
    Each pilaster protrudes 2.00 mm inward from the case inner wall (1.50 mm solid overlap beneath Main PCB)
    and runs continuously down into the tilted floor (zero overhangs, zero undercuts, R=0.85 mm inner corners).
    """
    z_shelf_top = -5.8000
    h = z_shelf_top - z_ext_bottom
    sgn = 1.0 if is_right else -1.0
    specs = [
        # (xa_abs, xb_abs, ymin, ymax, inner_corner_pts_abs)
        (7.8000, 18.5000, -34.3375, -31.6000, [(18.5000, -34.3375)]),
        (34.6500, 44.6500, -34.3375, -31.6000, [(34.6500, -34.3375), (44.6500, -34.3375)]),
        (7.8000, 10.5250, -78.5000, -64.5000, [(10.5250, -78.5000), (10.5250, -64.5000)]),
    ]
    pilasters = []
    for xa, xb, ymin, ymax, corners_abs in specs:
        xmin = min(sgn * xa, sgn * xb)
        xmax = max(sgn * xa, sgn * xb)
        cx = 0.5 * (xmin + xmax)
        cy = 0.5 * (ymin + ymax)
        box = bd.Box(
            xmax - xmin,
            ymax - ymin,
            h,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((cx, cy, z_ext_bottom)))
        target_corners = [(sgn * kx, ky) for kx, ky in corners_abs]
        vedges = box.edges().filter_by(
            lambda e, tcs=target_corners: abs(e.bounding_box().size.Z - h) < 0.05
            and any(
                abs(e.bounding_box().center().X - tx) < 0.05
                and abs(e.bounding_box().center().Y - ty) < 0.05
                for tx, ty in tcs
            )
        )
        if len(vedges) > 0:
            box = bd.fillet(vedges, radius=0.85)
        pilasters.append(box)
    return pilasters


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
    if is_right:
        # Local interior relief pocket under Sensor PCB J1 (`SM06B-SRSS-TB` + mated `SHR-06V-S-B` housing + wire exit bend):
        # X in [30.5000, 46.0000] (15.50 mm), Y in [-115.3375, -103.7375] (11.60 mm, 2.50 mm clear of TB2/TB4 Ø 6.00 mm bosses),
        # R = 1.50 mm corners (Ø 3.00 mm >= Ø 1.50 mm JLC3DP limit), 1.4000 mm exact perpendicular solid remaining wall thickness.
        theta_rad = math.atan2(
            Z_PINKY_BOTTOM - Z_THUMB_BOTTOM, X_PINKY_OUTER - X_THUMB_OUTER
        )
        dz_j1_pocket_wall = J1_POCKET_WALL_THICKNESS / math.cos(theta_rad)
        p_thumb_pkt = (X_THUMB_OUTER, -80.0, Z_THUMB_BOTTOM + dz_j1_pocket_wall)
        j1_pkt_plane = bd.Plane(origin=p_thumb_pkt, z_dir=norm_up)
        j1_pkt_halfspace = bd.extrude(
            j1_pkt_plane * bd.Rectangle(400.0, 400.0), amount=50.0
        )
        with bd.BuildSketch(bd.Plane.XY.offset(z_ext_bottom)) as sk_j1_pkt:
            with bd.Locations([(38.2500, -109.5375)]):
                bd.RectangleRounded(15.50, 11.60, 1.50)
        j1_pkt_prism = bd.extrude(sk_j1_pkt.sketch, amount=30.0)
        cavity_volume = cavity_volume + (j1_pkt_prism & j1_pkt_halfspace)
    body = outer_solid - cavity_volume

    # 4. Add Compact Flat-Topped Cylindrical Heat-Set Insert Boss Pillars + Hidden USB-C Inner-Wall Support Shelves
    hole_specs = get_case_hole_specs(is_right)
    boss_solids = []
    for tag, cx, cy, z_boss_top, _z_bore_bot, _z_ins_top, r_boss in hole_specs:
        boss_cyl = bd.Cylinder(
            radius=r_boss,
            height=z_boss_top - z_ext_bottom,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((cx, cy, z_ext_bottom)))
        # Bridge near-wall Trackball bosses cleanly into adjacent inner walls to eliminate narrow crevices:
        # 1) South-wall bridges for TB3/TB4 (cy=-120.8375)
        if cy < -120.0:
            south_bridge = bd.Box(
                2.0 * r_boss,
                5.50,
                z_boss_top - z_ext_bottom,
                align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.MIN),
            ).moved(bd.Location((cx, cy, z_ext_bottom)))
            boss_cyl = boss_cyl + south_bridge
        # 2) West-wall bridges for right-hand TB1 (11.8125, -98.2375) and TB3 (11.8125, -120.8375)
        if is_right and abs(cx - 11.8125) < 0.1:
            west_bridge = bd.Box(
                4.50,
                2.0 * r_boss,
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

    for pilaster in build_usbc_support_pilasters(is_right, z_ext_bottom):
        body = body + (pilaster & outer_solid)

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
    for tag, cx, cy, z_boss_top, z_bore_bottom, _z_ins_top, _r_boss in hole_specs:
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
