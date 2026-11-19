# -*- coding: utf-8 -*-
"""
Generate curcur40 3D-printed Built-in Tented Tray Bottom Cases
(cases/left.step, left.stl, right.step, right.stl, left-desk.step, left-desk.stl, right-desk.step, right-desk.stl).
Strictly adheres to docs/case_spec.md:
- Built-in 11.80 deg Minimum-Envelope Tenting Architecture with Sealed Flat Bottom, Tilted Interior Floor & Heat-Set Insert Bosses:
    - Outer Bottom Tenting Plane (theta_tent = 11.80 deg — minimum slope enclosing the -3.00 mm sunken trackball optics & J1 plug):
        - Pinky outer edge (|X_step| = 135.8580 mm): Z_bottom = -10.0000 mm (total height 10.00 mm)
        - Thumb inner edge (|X_step| = 17.0500 mm):  Z_bottom = -34.8203 mm (total height 34.82 mm; narrowed -10.0250 mm/side)
        - 100% sealed, hole-free outer bottom face (zero bottom counterbores or through-holes)
    - Tilted Interior Floor:
        - Parallel to outer bottom plane with uniform 2.40 mm vertical (2.35 mm perpendicular) bottom wall thickness (Z_floor = Z_bottom + 2.40 mm)
        - Unbroken smooth 11.80 deg interior plane from pinky to thumb (>= 0.72 mm clearance under pinky Choc V2 sockets, >= 0.71 mm under uncut LM19-LSI lens guide pins, and >= 0.47 mm under Sensor PCB J1 SHR-06V plug with zero thin-wall relief pockets)
- Fastening & Hidden Support Specifications (Section 2 — Switch-Retained Top Plate Architecture / 案1A + 6-Point Valley Layout):
    - Top-down unified M2 x 6.0 mm screws threading into M2 brass heat-set inserts (M2 x L=3.0 mm x OD=3.2 mm):
        - Cylindrical Boss Pillars (pilot bore Ø 2.85 mm, R = 1.425 mm >= Ø 1.50 mm JLC3DP limit):
            - 12x Compact Flat-Topped Key-Valley PCB Bosses (L1..L6 on Left, R1..R6 on Right, zero outer-margin bosses):
              Ø 5.20 mm flat boss top at Z = -5.80 mm (supports & clamps Main PCB directly via M2 x 6.0 mm screws passing through Top Plate Ø 4.40 mm screw-head clearance holes; uniform 1.175 mm radial wall >= 0.80 mm, flush insert top at Z = -5.80 mm), blind bores to Z = -11.80 mm
            - 4x Trackball Bosses (TB1..TB4, 3.00 mm sunken optical stack): Ø 6.00 mm boss top Z = -20.60 mm (Sensor PCB B.Cu), blind bore 3.80 mm deep to Z = -24.40 mm
        - 3x Hidden Inner-Wall PCB Support Shelves per case (`NW_HostUSB_Shelf`, `NE_HostUSB_Shelf`, `W_SplitUSB_Shelf`):
            - Full-height vertical pilasters integrated into the North inner wall (`Y = -28.9875 mm`, flanking Host USB-C) and Inner vertical wall (`|X| = 18.5500 mm`, North of Split USB-C) from tilted interior floor up to Z = -5.80 mm (2.00 mm inward protrusion = 1.50 mm solid shelf overlap under Main PCB B.Cu) to prevent downward PCB flexing during cable insertion with zero top/exterior visibility.
- Cutouts & Ports (Section 3 — North Host USB-C + Inner-Wall Split USB-C):
    - Host USB-C opening (north wall): Width 12.00 mm x Height 6.20 mm, corner fillet R = 1.50 mm, center at X = -60.2375 mm (Left `J1`) / +57.1500 mm (Right `rJ1`), Z = -5.85 mm
    - Split USB-C opening (inner vertical wall `|X| = 17.0500 mm`): Width 12.00 mm x Height 6.20 mm, corner fillet R = 1.50 mm, center at Y = -95.9000 mm (`y_pcb = 38.7500 mm`), Z = -5.85 mm
"""
import math
import sys
import time
from pathlib import Path
from cadgen import build123d as bd
from cadgen.geometry import is_sound
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.GeomAbs import GeomAbs_Cylinder
from OCP.TopAbs import TopAbs_REVERSED

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORKSPACE = Path(__file__).resolve().parent.parent
OUT_DIR = WORKSPACE / "cases"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MAX_RUNTIME_SEC = 180.0
T0_RUN = time.monotonic()


def _check_timeout(phase: str):
    el = time.monotonic() - T0_RUN
    if el > MAX_RUNTIME_SEC:
        raise TimeoutError(f"[{phase}] Exceeded hard timeout {MAX_RUNTIME_SEC:.0f}s (elapsed={el:.1f}s)!")


THETA_TENT_DEG = 11.80
X_THUMB_OUTER = 17.0500
X_PINKY_OUTER = 135.8580
Z_PINKY_BOTTOM = -10.0000
Z_THUMB_BOTTOM = round(
    Z_PINKY_BOTTOM - (X_PINKY_OUTER - X_THUMB_OUTER) * math.tan(math.radians(THETA_TENT_DEG)),
    4,
)  # -34.8203 mm
FLOOR_THICKNESS = 2.4000

BOSS_OUTER_RADIUS = 3.0000     # Ø 6.00 mm boss pillar for Trackball bosses (TB1..TB4; 1.575 mm radial wall)
PERIM_BOSS_RADIUS = 2.6000     # Ø 5.20 mm compact flat-topped boss for all 12 key-valley PCB holes (L1..L6, R1..R6; 1.175 mm radial wall)
PILOT_BORE_RADIUS = 1.4250     # Ø 2.85 mm pilot bore for M2 x L=3.0 x OD=3.2 mm brass heat-set insert


def z_bottom_at_x(x_abs: float) -> float:
    """
    Built-in tenting outer bottom Z height at |X_step| (theta_tent = 11.80 deg):
    - |X| = 17.0500 mm (thumb inner edge):  Z = -34.8203 mm
    - |X| = 135.8580 mm (pinky outer edge): Z = -10.0000 mm
    """
    return Z_THUMB_BOTTOM + (Z_PINKY_BOTTOM - Z_THUMB_BOTTOM) * (
        x_abs - X_THUMB_OUTER
    ) / (X_PINKY_OUTER - X_THUMB_OUTER)


def get_outer_pts(is_right=True):
    if is_right:
        return [
            ( 17.0500,  -27.4875, 2.0),
            (135.8580,  -27.4875, 2.0),
            (135.8580,  -98.2500, 2.0),
            ( 99.2500,  -98.2500, 1.5),
            ( 99.2500, -121.8875, 2.0),
            ( 17.0500, -121.8875, 2.0),
        ]
    else:
        return [
            (-17.0500,  -27.4875, 2.0),
            (-135.8580,  -27.4875, 2.0),
            (-135.8580,  -98.2500, 2.0),
            (-99.2500,  -98.2500, 1.5),
            (-99.2500, -121.8875, 2.0),
            (-17.0500, -121.8875, 2.0),
        ]


def get_inner_pts(is_right=True):
    if is_right:
        return [
            ( 18.5500,  -28.9875, 1.0),
            (134.3580,  -28.9875, 1.0),
            (134.3580,  -96.7500, 1.0),
            ( 97.7500,  -96.7500, 1.0),
            ( 97.7500, -120.3875, 1.0),
            ( 18.5500, -120.3875, 1.0),
        ]
    else:
        return [
            (-18.5500,  -28.9875, 1.0),
            (-134.3580,  -28.9875, 1.0),
            (-134.3580,  -96.7500, 1.0),
            (-97.7500,  -96.7500, 1.0),
            (-97.7500, -120.3875, 1.0),
            (-18.5500, -120.3875, 1.0),
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
        blind bores: -11.80 mm (uniform 6.00 mm blind bore across all 12 bosses)
    - 4x Trackball Bosses TB1..TB4 (3.00 mm sunken optical stack):
        Ø 6.00 mm (R = 3.00 mm) boss to z_boss_top = -20.60 mm (Sensor PCB B.Cu),
        z_bore_bottom = -24.40 mm (3.80 mm blind bore), z_insert_top = -20.60 mm
    """
    if is_right:
        perim_pcb = [
            ("R1",  42.2500,  -4.5000, -5.80, -11.80, -5.80, PERIM_BOSS_RADIUS),
            ("R2", 100.5000,   0.5000, -5.80, -11.80, -5.80, PERIM_BOSS_RADIUS),
            ("R3", 100.5000,  19.5000, -5.80, -11.80, -5.80, PERIM_BOSS_RADIUS),
            ("R4",  42.2500,  14.5000, -5.80, -11.80, -5.80, PERIM_BOSS_RADIUS),
            ("R5",   9.4500,  58.5000, -5.80, -11.80, -5.80, PERIM_BOSS_RADIUS),
            ("R6",  60.5000,  35.0000, -5.80, -11.80, -5.80, PERIM_BOSS_RADIUS),
        ]
        tb_pcb = [
            ("TB1", 16.5750, 36.3250, -20.60, -24.40, -20.60, BOSS_OUTER_RADIUS),
            ("TB2", 40.5750, 36.3250, -20.60, -24.40, -20.60, BOSS_OUTER_RADIUS),
            ("TB3", 16.5750, 58.9250, -20.60, -24.40, -20.60, BOSS_OUTER_RADIUS),
            ("TB4", 40.5750, 58.9250, -20.60, -24.40, -20.60, BOSS_OUTER_RADIUS),
        ]
        return [
            (tag, x + 14.2875, -(y + 57.1500), z_top, z_bot, z_ins, r_b)
            for tag, x, y, z_top, z_bot, z_ins, r_b in (perim_pcb + tb_pcb)
        ]
    else:
        perim_pcb = [
            ("L1",  -42.2500,  -4.5000, -5.80, -11.80, -5.80, PERIM_BOSS_RADIUS),
            ("L2", -100.5000,   0.5000, -5.80, -11.80, -5.80, PERIM_BOSS_RADIUS),
            ("L3", -100.5000,  19.5000, -5.80, -11.80, -5.80, PERIM_BOSS_RADIUS),
            ("L4",  -42.2500,  14.5000, -5.80, -11.80, -5.80, PERIM_BOSS_RADIUS),
            ("L5",  -27.0000,  58.8000, -5.80, -11.80, -5.80, PERIM_BOSS_RADIUS),
            ("L6",  -60.5000,  35.0000, -5.80, -11.80, -5.80, PERIM_BOSS_RADIUS),
        ]
        return [
            (tag, x - 14.2875, -(y + 57.1500), z_top, z_bot, z_ins, r_b)
            for tag, x, y, z_top, z_bot, z_ins, r_b in perim_pcb
        ]


def build_usbc_support_pilasters(is_right: bool, z_ext_bottom: float) -> list[bd.Solid]:
    """
    Build 3 hidden inner-wall PCB support shelves (top face Z = -5.8000 mm = Main PCB B.Cu):
      1. NW_HostUSB_Shelf: North inner wall (`Y in [-30.9875, -28.2000]`), flanking Host USB-C (`J1`/`rJ1`)
      2. NE_HostUSB_Shelf: North inner wall (`Y in [-30.9875, -28.2000]`), flanking Host USB-C (`J1`/`rJ1`)
      3. W_SplitUSB_Shelf: Inner vertical wall (`|X| in [17.8000, 20.5500]`, `Y in [-81.8000, -74.6000]`),
         North of Split USB-C (`J2`/`rJ2` at `Y = -95.9000`) and clear of `Wheel_Cradle` & `rEXSW2` socket.
    Each pilaster protrudes 2.00 mm inward from the adjacent inner wall (1.50 mm solid overlap beneath Main PCB),
    maintains >= 0.95 mm step to the 12.00 mm USB-C apertures, and runs continuously down into the tilted floor
    (zero overhangs, zero undercuts, R=0.85 mm inner corners >= Ø1.50 mm JLC3DP limit).
    """
    z_shelf_top = -5.8000
    h = z_shelf_top - z_ext_bottom
    if is_right:
        specs = [
            (40.1500, 50.1500, -30.9875, -28.2000, [(40.1500, -30.9875), (50.1500, -30.9875)]),
            (64.1500, 74.1500, -30.9875, -28.2000, [(64.1500, -30.9875), (74.1500, -30.9875)]),
            (17.8000, 20.5500, -81.8000, -74.6000, [(20.5500, -81.8000), (20.5500, -74.6000)]),
        ]
    else:
        specs = [
            (-77.2000, -67.2000, -30.9875, -28.2000, [(-77.2000, -30.9875), (-67.2000, -30.9875)]),
            (-53.2000, -43.2000, -30.9875, -28.2000, [(-53.2000, -30.9875), (-43.2000, -30.9875)]),
            (-20.5500, -17.8000, -81.8000, -74.6000, [(-20.5500, -81.8000), (-20.5500, -74.6000)]),
        ]
    pilasters = []
    for xmin, xmax, ymin, ymax, target_corners in specs:
        cx = 0.5 * (xmin + xmax)
        cy = 0.5 * (ymin + ymax)
        box = bd.Box(
            xmax - xmin,
            ymax - ymin,
            h,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((cx, cy, z_ext_bottom)))
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

                    if is_top_rim:
                        excluded_count += 1
                    else:
                        unexpected.append((d, (mx, my, mz), i, j))

    _check_timeout(f"verify_case:{side_str}")
    print(
        f"[{time.monotonic()-T0_RUN:5.1f}s] [{side_str}] JLC3DP preflight & <0.80mm check: "
        f"bbox={sx:.2f}x{sy:.2f}x{sz:.2f}mm, min_hole_diam={min_concave_diam:.2f}mm (>=1.50mm), "
        f"{len(unexpected)} unexpected violations ({excluded_count} known excluded pairs)",
        flush=True,
    )
    if unexpected:
        for d, (mx, my, mz), i, j in unexpected:
            print(f"  UNEXPECTED: d={d:.4f} mm at ({mx:.2f}, {my:.2f}, {mz:.2f}) [F{i}-F{j}]", flush=True)
    assert len(unexpected) == 0, f"{side_str} case has {len(unexpected)} unexpected <0.80mm wall/gap violations!"


def build_case(is_right=True) -> bd.Solid:
    side_str = "right" if is_right else "left"
    _check_timeout(f"build_case:{side_str}:start")
    print(f"[{time.monotonic()-T0_RUN:5.1f}s] --- Building {side_str} sealed-bottom tented case with heat-set insert bosses ---", flush=True)

    z_ext_bottom = -55.00
    z_top = 0.00

    # 1. Outer solid extruded from Z = -55.00 to 0.00 mm
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
    inner_prism = bd.extrude(sk_inner, amount=58.0).moved(
        bd.Location((0, 0, z_ext_bottom))
    )

    # 3. Cut tilted interior cavity (11.80 deg unbroken smooth interior plane)
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
        floor_plane * bd.Rectangle(400.0, 400.0), amount=80.0
    )
    cavity_volume = inner_prism & tilted_cavity_halfspace
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
        # Bridge near-wall Trackball bosses TB3/TB4 (cy=-116.0750) into South inner wall (-120.3875) to eliminate narrow crevices:
        if is_right and tag in ("TB3", "TB4"):
            south_bridge = bd.Box(
                2.0 * r_boss,
                5.50,
                z_boss_top - z_ext_bottom,
                align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.MIN),
            ).moved(bd.Location((cx, cy, z_ext_bottom)))
            boss_cyl = boss_cyl + south_bridge
        boss_solids.append(boss_cyl & outer_solid)

    for b_cyl in boss_solids:
        body = body + b_cyl

    for pilaster in build_usbc_support_pilasters(is_right, z_ext_bottom):
        body = body + (pilaster & outer_solid)

    # 5. Cut angled outer bottom tenting plane (theta_tent = 11.80 deg) — 100% sealed, hole-free flat bottom!
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
    bottom_cutter = bd.extrude(tent_plane * bd.Rectangle(400.0, 400.0), amount=80.0)
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

    # 7. USB-C port cutouts (Width = 12.00 mm, Height = 6.20 mm, R = 1.50 mm, Center Z = -5.85 mm):
    #    7a. North-Wall Host USB-C (`J1` at X = -60.2375 mm on Left, `rJ1` at X = +57.1500 mm on Right)
    north_usb_cx = 57.1500 if is_right else -60.2375
    host_usb_cutter = bd.Box(12.00, 12.00, 6.20).moved(
        bd.Location((north_usb_cx, -27.4875, -5.8500))
    )
    edges_y = host_usb_cutter.edges().filter_by(
        lambda e: abs(e.bounding_box().size.Y - 12.00) < 0.1
        and abs(e.bounding_box().size.Z - 0.0) < 0.1
    )
    assert len(edges_y) == 4, f"Expected 4 Y-parallel edges on host_usb_cutter at {north_usb_cx}, got {len(edges_y)}"
    host_usb_cutter = bd.fillet(edges_y, radius=1.50)
    body = body - host_usb_cutter

    #    7b. Inner-Vertical-Wall Split USB-C (`J2`/`rJ2` at |X| = 17.0500 mm, Y = -95.9000 mm -> y_pcb = 38.7500 mm)
    inner_usb_cx = 17.0500 if is_right else -17.0500
    split_usb_cutter = bd.Box(12.00, 12.00, 6.20).moved(
        bd.Location((inner_usb_cx, -95.9000, -5.8500))
    )
    edges_x = split_usb_cutter.edges().filter_by(
        lambda e: abs(e.bounding_box().size.X - 12.00) < 0.1
        and abs(e.bounding_box().size.Z - 0.0) < 0.1
    )
    assert len(edges_x) == 4, f"Expected 4 X-parallel edges on split_usb_cutter at {inner_usb_cx}, got {len(edges_x)}"
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
        f"[{time.monotonic()-T0_RUN:5.1f}s] Exported {step_path.name} & {stl_path.name}: "
        f"bbox Z=[{bb.min.Z:.4f}, {bb.max.Z:.4f}], volume={solid.volume:.2f} mm^3",
        flush=True,
    )

    # 8. Export desk-horizontal (outer bottom flat on Z = 0.00 mm) STEP & STL
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
        f"[{time.monotonic()-T0_RUN:5.1f}s] Exported {desk_step_path.name} & {desk_stl_path.name}: "
        f"bbox Z=[{bb_desk.min.Z:.4f}, {bb_desk.max.Z:.4f}], volume={desk_solid.volume:.2f} mm^3",
        flush=True,
    )
    return solid


if __name__ == "__main__":
    build_case(is_right=False)
    build_case(is_right=True)
    print(f"[{time.monotonic()-T0_RUN:5.1f}s] All cases generated successfully!", flush=True)
