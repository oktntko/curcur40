# -*- coding: utf-8 -*-
"""
Generate curcur40 Full Assembly STEP models:
  1. cases/assembly-full.step      (Top Plate horizontal at Z = -2.00 mm)
  2. cases/assembly-full-desk.step (Case Bottom horizontal on desk plane Z = 0.00 mm)
and verify zero interference across all components per docs/case_spec.md:
- Left & Right 3D-printed Low-Height Built-in Tented Tray Bottom Cases (with Tilted Floor & Cylindrical Bosses)
- Left & Right Main PCBs (Z = -5.80 to -4.20 mm, with Ø 3.30 mm spacer through-holes)
- Separated PMW3360 Sensor PCB (`curcur40-pmw3360`, Z = -17.60 to -16.00 mm)
- Left & Right FR-4 Top Plates (Z = -3.60 to -2.00 mm, with Ø 2.40 mm screw holes & switch cutouts)
- Sunk Trackball Cup placed on Sensor PCB F.Cu at (23.8125, -109.5375, -16.00 mm), Rim at Z = -2.00 mm (flush with Top Plate)
- 25mm Trackball Sphere at (23.8125, -109.5375, +2.30 mm) (Top at Z = +14.80 mm, +11.20 mm above Keycap top Z = +3.60 mm)
- PMW3360 Sensor IC & LM19-LSI Optical Lens
- 14x Unified M2 5.50mm Female-Female Standoffs:
    - 10x Perimeter (5 Left L1-L5 + 5 Right R1-R5, Z = -9.10 to -3.60 mm, seated under Top Plate)
    - 4x Trackball Cup (TB1-TB4, Z = -17.60 to -12.10 mm, seated on Z = -17.60 mm bosses, passing through 1.60 mm Sensor PCB and 3.90 mm into 5.50 mm Cup Ear socket)
- 14x Bottom M2x4mm Screws (head seated against counterbore ceiling z_boss_top - 2.40 mm)
- 14x Top M2x4mm Screws (4 on Trackball Cup ears Z = -10.50 mm, 10 on Top Plates Z = -2.00 mm)
- Keycaps (Choc v2 low-profile) & CKW12 Rotary Encoder
"""
import math
from pathlib import Path
from cadgen import build123d as bd
from cadgen.geometry import overlap_volume, closest_points, is_sound

WORKSPACE = Path(__file__).resolve().parent.parent
CASES_DIR = WORKSPACE / "cases"

Z_THUMB_BOTTOM = -26.9000
Z_PINKY_BOTTOM = -10.0000
X_THUMB_OUTER = 7.0250
X_PINKY_OUTER = 135.8580
THETA_TENT_DEG = math.degrees(
    math.atan2(Z_PINKY_BOTTOM - Z_THUMB_BOTTOM, X_PINKY_OUTER - X_THUMB_OUTER)
)


def z_bottom_at_x(x_abs: float) -> float:
    return Z_THUMB_BOTTOM + (Z_PINKY_BOTTOM - Z_THUMB_BOTTOM) * (
        x_abs - X_THUMB_OUTER
    ) / (X_PINKY_OUTER - X_THUMB_OUTER)


LEFT_SWITCHES = [
    (-109.5375, -7.14375),
    (-109.5375, 11.90625),
    (-109.5375, 30.95625),
    (-90.4875, -11.90625),
    (-90.4875, 7.14375),
    (-90.4875, 26.19375),
    (-71.4375, -14.28750),
    (-71.4375, 4.76250),
    (-71.4375, 23.81250),
    (-52.3875, -11.90625),
    (-52.3875, 7.14375),
    (-52.3875, 26.19375),
    (-33.3375, -9.52500),
    (-33.3375, 9.52500),
    (-33.3375, 28.57500),
    (-14.2875, 0.00000),
    (-14.2875, 19.05000),
    (-71.4375, 52.38750),
    (-52.3875, 52.38750),
    (-33.3375, 52.38750),
    (-14.2875, 52.38750),
]

RIGHT_SWITCHES = [
    (109.5375, -7.14375),
    (109.5375, 11.90625),
    (109.5375, 30.95625),
    (90.4875, -11.90625),
    (90.4875, 7.14375),
    (90.4875, 26.19375),
    (71.4375, -14.28750),
    (71.4375, 4.76250),
    (71.4375, 23.81250),
    (52.3875, -11.90625),
    (52.3875, 7.14375),
    (52.3875, 26.19375),
    (33.3375, -9.52500),
    (33.3375, 9.52500),
    (33.3375, 28.57500),
    (14.2875, 19.05000),
    (33.3375, 52.38750),
    (52.3875, 52.38750),
    (71.4375, 52.38750),
]

RIGHT_ENCODER = (14.2875, 0.00000)

LEFT_PERIMETER_HOLES_PCB = [
    (   0.0000, -15.0000),  # L1
    (   0.0000,  20.0000),  # L2
    (-101.0000, -20.0000),  # L3
    ( -98.0000,  38.0000),  # L4
    ( -62.0000,  64.6000),  # L5
]

RIGHT_PERIMETER_HOLES_PCB = [
    (  0.0000, -15.0000),  # R1
    (  0.0000,  20.0000),  # R2
    (101.0000, -20.0000),  # R3
    ( 98.0000,  38.0000),  # R4
    ( 62.0000,  64.6000),  # R5
]

RIGHT_TB_HOLES_PCB = [
    ( -2.4750,  41.0875),  # TB1
    ( 21.5250,  41.0875),  # TB2
    ( -2.4750,  63.6875),  # TB3
    ( 21.5250,  63.6875),  # TB4
]


def to_step_left(x, y):
    return (x - 14.2875, -(y + 57.1500))


def to_step_right(x, y):
    return (x + 14.2875, -(y + 57.1500))


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
                    except Exception:
                        pass
    return sk.sketch


def build_main_pcb_solid(is_right=True) -> bd.Solid:
    """
    Constructs the Main PCB solid (Z = -5.80 to -4.20 mm, thickness 1.60 mm)
    with exact outer boundary, TRRS notch, and Ø 3.30 mm spacer holes.
    On Right Main PCB, the thumb trackball section (X < 25.3125, Y > 37.3000) is separated into `curcur40-pmw3360`.
    """
    if is_right:
        pts_pcb = [
            ( -5.2625, -24.3125, 1.0),
            (  7.6175, -24.3125, 0.0),
            (  7.6175, -18.5100, 0.0),
            ( 16.8575, -18.5100, 0.0),
            ( 16.8575, -24.3125, 0.0),
            (119.0625, -24.3125, 1.0),
            (119.0625,  40.98125, 1.0),
            ( 82.4625,  40.98125, 1.0),
            ( 82.4625,  67.5000, 1.0),
            ( 23.8000,  67.5000, 1.0),
            ( 23.8000,  37.4000, 0.8),
            ( -5.2625,  37.4000, 0.8),
            ( -5.2625,  32.8000, 0.0),
            (  7.7425,  32.8000, 0.0),
            (  7.7425,  26.5000, 0.0),
            ( -5.2625,  26.5000, 0.0),
        ]
        pts_step = [(*to_step_right(x, y), r) for x, y, r in pts_pcb]
        holes_step = [to_step_right(x, y) for x, y in RIGHT_PERIMETER_HOLES_PCB]
    else:
        pts_pcb = [
            (   5.2625, -24.3125, 1.0),
            (  -7.6175, -24.3125, 0.0),
            (  -7.6175, -18.5100, 0.0),
            ( -16.8575, -18.5100, 0.0),
            ( -16.8575, -24.3125, 0.0),
            (-119.0625, -24.3125, 1.0),
            (-119.0625,  40.98125, 1.0),
            ( -82.4625,  40.98125, 1.0),
            ( -82.4625,  67.5000, 1.0),
            (   5.2625,  67.5000, 1.0),
            (   5.2625,  32.8000, 0.0),
            (  -7.7425,  32.8000, 0.0),
            (  -7.7425,  26.5000, 0.0),
            (   5.2625,  26.5000, 0.0),
        ]
        pts_step = [(*to_step_left(x, y), r) for x, y, r in pts_pcb]
        holes_step = [to_step_left(x, y) for x, y in LEFT_PERIMETER_HOLES_PCB]

    sk = make_filleted_sketch(pts_step)
    pcb = bd.extrude(sk, amount=1.60).moved(bd.Location((0, 0, -5.80)))

    # Cut Ø 3.30 mm (radius 1.65 mm) spacer through-holes
    for hx, hy in holes_step:
        pcb = pcb - bd.Cylinder(
            radius=1.65,
            height=4.0,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((hx, hy, -6.5)))

    # Cut USB-C shield PTH slots (4x SH oval holes at ±5.62 mm from J1/rJ1 center)
    usbc_cx = 26.5750 if is_right else -26.5750
    for sx in (usbc_cx - 5.6200, usbc_cx + 5.6200):
        for sy in (-34.0925, -38.0925):
            pcb = pcb - bd.Box(1.25, 2.20, 4.0).moved(bd.Location((sx, sy, -5.0)))

    solid = pcb.solids()[0]
    solid.label = "Right_Main_PCB" if is_right else "Left_Main_PCB"
    return solid


def build_top_plate_solid(is_right=True) -> bd.Solid:
    """
    Constructs the FR-4 Top Plate solid (Z = -3.60 to -2.00 mm, thickness 1.60 mm)
    with switch cutouts and Ø 2.40 mm through-holes (no counterbores).
    """
    if is_right:
        pts_plate = [
            ( -5.4625, -24.51250, 1.0),
            (119.2625, -24.51250, 1.0),
            (119.2625,  41.18125, 1.0),
            ( 82.6625,  41.18125, 1.0),
            ( 82.6625,  67.70000, 1.0),
            ( 24.2000,  67.70000, 1.0),
            ( 24.2000,  37.40000, 1.0),
            ( -5.4625,  37.40000, 1.0),
        ]
        pts_step = [(*to_step_right(x, y), r) for x, y, r in pts_plate]
        sw_step = [to_step_right(x, y) for x, y in RIGHT_SWITCHES]
        holes_step = [to_step_right(x, y) for x, y in RIGHT_PERIMETER_HOLES_PCB]
    else:
        pts_plate = [
            (   5.4625, -24.51250, 1.0),
            (-119.2625, -24.51250, 1.0),
            (-119.2625,  41.18125, 1.0),
            ( -82.6625,  41.18125, 1.0),
            ( -82.6625,  67.70000, 1.0),
            (   5.4625,  67.70000, 1.0),
        ]
        pts_step = [(*to_step_left(x, y), r) for x, y, r in pts_plate]
        sw_step = [to_step_left(x, y) for x, y in LEFT_SWITCHES]
        holes_step = [to_step_left(x, y) for x, y in LEFT_PERIMETER_HOLES_PCB]

    sk = make_filleted_sketch(pts_step)
    plate = bd.extrude(sk, amount=1.60).moved(bd.Location((0, 0, -3.60)))

    with bd.BuildSketch(bd.Plane.XY.offset(-4.0)) as sk_cuts:
        for sx, sy in sw_step:
            with bd.Locations([(sx, sy)]):
                bd.RectangleRounded(14.0, 14.0, 0.5)
        if is_right:
            ex, ey = to_step_right(*RIGHT_ENCODER)
            with bd.Locations([(ex, ey)]):
                bd.RectangleRounded(18.2, 18.2, 0.5)
    plate = plate - bd.extrude(sk_cuts.sketch, amount=3.0)

    # Cut Ø 2.40 mm (radius 1.20 mm) M2 screw through-holes (no counterbores)
    for hx, hy in holes_step:
        plate = plate - bd.Cylinder(
            radius=1.20,
            height=4.0,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((hx, hy, -4.5)))

    solid = plate.solids()[0]
    solid.label = "Right_Top_Plate" if is_right else "Left_Top_Plate"
    return solid


def make_keycap_solid(sx, sy, label="Keycap") -> bd.Solid:
    with bd.BuildSketch(bd.Plane.XY.offset(-0.80)) as sk:
        with bd.Locations([(sx, sy)]):
            bd.RectangleRounded(17.2, 16.2, 1.5)
    cap = bd.extrude(sk.sketch, amount=4.40).solids()[0]
    cap.label = label
    return cap


def make_ckw12_solids(ex, ey):
    """
    Loads the official CKW12 rotary encoder 3D models (housing, wheel, stem),
    rotates -90 deg around Z (matching original footprint 3D orientation), and
    places on F.Cu + 0.50 mm conthrough height (Z = -4.20 + 0.50 = -3.70 mm).
    """
    models_dir = WORKSPACE / "pcbs" / "common" / "kbd" / "3dmodels"
    solids = []
    for fname, label in [
        ("ckw12_housing.stp", "CKW12_Housing"),
        ("ckw12_wheel.stp", "CKW12_Wheel"),
        ("ckw12_stem.stp", "CKW12_Stem"),
    ]:
        part = bd.import_step(str(models_dir / fname))
        placed = part.moved(bd.Location((ex, ey, -3.70), (0, 0, -90)))
        for idx, s in enumerate(placed.solids()):
            s.label = label if len(placed.solids()) == 1 else f"{label}_{idx+1}"
            solids.append(s)
    return solids


def make_usbc_and_trrs_solids(is_right: bool):
    """
    Loads the official TYPE-C-31-M-13C.step (J1 / rJ1) and PJ-398A-5A.step (J2 / rJ2)
    3D models and places them at their exact mid-mount positions on Main PCB B.Cu (Z = -5.80 mm).
    """
    pkg_dir = WORKSPACE / "pcbs" / "common" / "kbd" / "kicad-packages3D" / "kbd.3dshapes"
    prefix = "Right" if is_right else "Left"
    usbc_raw = bd.import_step(str(pkg_dir / "TYPE-C-31-M-13C.step"))
    usbc_cx = 26.5750 if is_right else -26.5750
    usbc_placed = usbc_raw.rotate(bd.Axis.X, 180).moved(
        bd.Location((usbc_cx, -38.5925, -4.2850))
    )
    usbc_shell = usbc_placed.solids()[0]
    usbc_shell.label = f"{prefix}_USBC_Shell"
    usbc_tongue = usbc_placed.solids()[1]
    usbc_tongue.label = f"{prefix}_USBC_Tongue"

    trrs_raw = bd.import_step(str(pkg_dir / "PJ-398A-5A.step"))
    rot_z = -90.0 if is_right else 90.0
    trrs_cx = 6.5300 if is_right else -6.5300
    trrs_placed = (
        trrs_raw.rotate(bd.Axis.Y, 180)
        .rotate(bd.Axis.Z, rot_z)
        .moved(bd.Location((trrs_cx, -86.7963, -3.7850)))
    )
    trrs_body = trrs_placed.solids()[0]
    trrs_body.label = f"{prefix}_TRRS_Jack"

    return [usbc_shell, usbc_tongue, trrs_body]


def make_sensor_and_jst_smd_solids():
    """
    Builds 3D bounding solids for all populated B.Cu SMD components on the separated
    Sensor PCB (curcur40-pmw3360, B.Cu at Z = -17.60 mm) and rJ3 on Right Main PCB
    (B.Cu at Z = -5.80 mm) to verify 0.00000000 mm^3 overlap against right_case,
    trackball cup, PCBs, and standoffs.
    """
    solids = []
    # 1. rJ3 (JST SH 6-pin horizontal, SM06B-SRSS-TB) on Right Main PCB B.Cu at (46.5000, 63.0000), rot +90 deg
    # Footprint body + pins span local X in [-4.3, 4.3], local Y in [-2.6, 2.75], height 2.95 mm below B.Cu (Z = -5.80..-8.75 mm)
    rj3_x, rj3_y = to_step_right(46.5000, 63.0000)
    rj3_solid = (
        bd.Pos(rj3_x + (-2.60 + 2.75) / 2.0, rj3_y, -5.80 - 2.95 / 2.0)
        * bd.Box(5.35, 8.60, 2.95)
    ).solids()[0]
    rj3_solid.label = "Right_PCB_rJ3_JST_SH"
    solids.append(rj3_solid)

    # 2. J1 (JST SH 6-pin horizontal, SM06B-SRSS-TB) on Sensor PCB B.Cu at (19.2000, 52.3875), rot -90 deg
    # With rot -90 deg on B.Cu, local Y [-2.575, +1.675] maps to X_pcb [19.2 - 1.675, 19.2 + 2.575], height 2.95 mm (Z = -17.60..-20.55 mm)
    j1_x, j1_y = to_step_right(19.2000, 52.3875)
    j1_solid = (
        bd.Pos(j1_x + (2.575 - 1.675) / 2.0, j1_y, -17.60 - 2.95 / 2.0)
        * bd.Box(4.25, 8.60, 2.95)
    ).solids()[0]
    j1_solid.label = "Sensor_PCB_J1_JST_SH"
    solids.append(j1_solid)

    # 3. Sensor PCB B.Cu passive/IC SMD components (including pads + 3D body envelope, Z = -17.60..-18.70 mm)
    sensor_smds = [
        # (ref, x_pcb, y_pcb, dx_pcb, dy_pcb, height)
        ("C1", 0.5000, 54.9955, 2.80, 0.95, 0.90),
        ("C2", 0.5000, 56.7755, 2.80, 0.95, 0.90),
        ("C3", 2.3860, 63.3617, 0.95, 2.80, 0.90),
        ("C4", 10.6235, 63.6617, 2.80, 0.95, 0.90),
        ("R1", 0.5000, 47.8755, 2.80, 0.95, 0.60),
        ("R2", 15.3860, 41.6617, 2.80, 0.95, 0.60),
        ("R3", 7.8860, 41.6617, 2.80, 0.95, 0.60),
        ("U2", 16.0000, 63.0617, 2.95, 3.00, 1.15),
    ]
    for ref, px, py, dx, dy, h in sensor_smds:
        sx, sy = to_step_right(px, py)
        smd_solid = (
            bd.Pos(sx, sy, -17.60 - h / 2.0) * bd.Box(dx, dy, h)
        ).solids()[0]
        smd_solid.label = f"Sensor_PCB_{ref}"
        solids.append(smd_solid)

    return solids


def transform_to_desk(shape, is_right: bool):
    """
    Rigidly transforms a left-half or right-half shape from the Top-Plate-horizontal
    coordinate system into the Desk-horizontal coordinate system where both Left and Right
    case bottom faces lie flat on Z = 0.0000 mm.
    """
    pivot_x = X_PINKY_OUTER if is_right else -X_PINKY_OUTER
    pivot_z = Z_PINKY_BOTTOM
    rot_y = THETA_TENT_DEG if is_right else -THETA_TENT_DEG
    lbl = getattr(shape, "label", "")
    transformed = (
        shape.moved(bd.Location((-pivot_x, 0.0, -pivot_z)))
        .rotate(bd.Axis.Y, rot_y)
        .moved(bd.Location((pivot_x, 0.0, 0.0)))
    )
    if hasattr(transformed, "solids") and len(transformed.solids()) == 1 and isinstance(shape, bd.Solid):
        res = transformed.solids()[0]
    elif hasattr(transformed, "faces") and len(transformed.faces()) == 1 and isinstance(shape, bd.Face):
        res = transformed.faces()[0]
    else:
        res = transformed
    res.label = lbl
    return res


def main():
    print("=== Building & Verifying curcur40 Full Assembly (assembly-full.step & assembly-full-desk.step) ===")

    left_case = bd.import_step(str(CASES_DIR / "left.step")).solids()[0]
    left_case.label = "Left_Case"
    right_case = bd.import_step(str(CASES_DIR / "right.step")).solids()[0]
    right_case.label = "Right_Case"

    left_pcb = build_main_pcb_solid(is_right=False)
    right_pcb = build_main_pcb_solid(is_right=True)

    left_plate = build_top_plate_solid(is_right=False)
    right_plate = build_top_plate_solid(is_right=True)

    # Sunk Trackball Cup placed on separated Sensor PCB F.Cu (Z = -16.00 mm) at (23.8125, -109.5375):
    # Cup uniform rim is at Z_rel = +14.00 mm -> Z_global = -16.00 + 14.00 = -2.00 mm (flush with Top Plate top surface!)
    tb_cx, tb_cy, tb_cz = 23.8125, -109.5375, -16.0000
    cup_local = bd.import_step(str(CASES_DIR / "trackball-cup.step"))
    cup_global = cup_local.moved(bd.Location((tb_cx, tb_cy, tb_cz))).solids()[0]
    cup_global.label = "Trackball_Cup"

    ball_global = (
        bd.Sphere(radius=12.50)
        .moved(bd.Location((tb_cx, tb_cy, tb_cz + 18.30)))
        .solids()[0]
    )
    ball_global.label = "Trackball_25mm"

    # Load PMW3360 sensor, LM19 lens, and separated Sensor PCB from pmw3360-lens-pcb-assembly.step
    asm_parts = bd.import_step(str(CASES_DIR / "pmw3360-lens-pcb-assembly.step"))
    sensor_local, lens_local, sensor_pcb_local = None, None, None
    for s in asm_parts.solids():
        bb = s.bounding_box()
        if bb.min.Z < -3.5:
            sensor_local = s
        elif bb.max.Z > 3.0:
            lens_local = s
        else:
            sensor_pcb_local = s
    sensor_pcb_global = sensor_pcb_local.moved(bd.Location((tb_cx, tb_cy, tb_cz))).solids()[0]
    sensor_pcb_global.label = "PMW3360_Sensor_PCB"
    sensor_global = sensor_local.moved(bd.Location((tb_cx, tb_cy, tb_cz))).solids()[0]
    sensor_global.label = "PMW3360_Sensor"
    lens_global = lens_local.moved(bd.Location((tb_cx, tb_cy, tb_cz))).solids()[0]
    lens_global.label = "LM19_Lens"

    # Optical Distance Reference Point in global coordinates:
    # Sensor PCB F.Cu Z = -16.00 mm + 3.40 mm = -12.60 mm (2.40 mm below ball bottom Z = -10.20 mm)
    ref_point_global = bd.Pos(tb_cx, tb_cy, tb_cz + 3.40) * bd.Circle(0.35).face()
    ref_point_global.label = "Lens_Optical_Ref_Point"

    # CKW12 Rotary Encoder at rEXSW1 (14.2875, 0.0000)
    enc_x, enc_y = to_step_right(*RIGHT_ENCODER)
    ckw12_solids = make_ckw12_solids(enc_x, enc_y)

    # Create all 14x Unified 5.50mm Standoffs (10x perimeter at Z=-9.10..-3.60, 4x trackball cup at Z=-17.60..-12.10)
    left_holes_step = [to_step_left(x, y) for x, y in LEFT_PERIMETER_HOLES_PCB]
    right_perim_step = [to_step_right(x, y) for x, y in RIGHT_PERIMETER_HOLES_PCB]
    right_tb_step = [to_step_right(x, y) for x, y in RIGHT_TB_HOLES_PCB]

    standoffs = []
    bottom_screws = []
    top_screws = []

    all_holes = (
        [(x, y, "L_Perim", -9.10, -2.00, 5.50, False) for x, y in left_holes_step]
        + [(x, y, "R_Perim", -9.10, -2.00, 5.50, True) for x, y in right_perim_step]
        + [(x, y, "R_TB", -17.60, -10.50, 5.50, True) for x, y in right_tb_step]
    )

    left_fasteners = []
    right_fasteners = []

    for i, (sx, sy, tag, z_floor, z_top_seat, so_height, is_right_hole) in enumerate(all_holes):
        # M2 standoff (OD 3.0mm, ID 1.7mm, Z = z_floor to z_floor + so_height)
        so = bd.Cylinder(
            radius=1.50,
            height=so_height,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((sx, sy, z_floor))) - bd.Cylinder(
            radius=0.85,
            height=so_height + 0.50,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(
            bd.Location((sx, sy, z_floor - 0.25))
        )
        so_solid = so.solids()[0]
        so_solid.label = f"Standoff_{tag}_{i+1}"
        standoffs.append(so_solid)

        # Bottom M2x4mm screw seated against horizontal counterbore ceiling z_cb_ceil = z_floor - 2.40 mm (unified 2.40 mm clamping floor!)
        z_cb_ceil = round(z_floor - 2.40, 4)
        b_head = bd.Cylinder(
            radius=2.00,
            height=0.80,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX),
        ).moved(bd.Location((sx, sy, z_cb_ceil)))
        b_shank = bd.Cylinder(
            radius=1.00,
            height=4.00,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((sx, sy, z_cb_ceil)))
        b_scr = (b_head + b_shank).solids()[0]
        b_scr.label = f"Bottom_Screw_{tag}_{i+1}"
        bottom_screws.append(b_scr)

        # Top M2x4mm screw (head seated at z_top_seat: -2.00 mm on Top Plate or -10.50 mm on Cup Ear)
        t_head = bd.Cylinder(
            radius=2.00,
            height=0.80,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((sx, sy, z_top_seat)))
        t_shank = bd.Cylinder(
            radius=1.00,
            height=4.00,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX),
        ).moved(bd.Location((sx, sy, z_top_seat)))
        t_scr = (t_head + t_shank).solids()[0]
        t_scr.label = f"Top_Screw_{tag}_{i+1}"
        top_screws.append(t_scr)

        if is_right_hole:
            right_fasteners.extend([so_solid, b_scr, t_scr])
        else:
            left_fasteners.extend([so_solid, b_scr, t_scr])

    # Keycaps
    left_keycaps = []
    right_keycaps = []
    for idx, (kx, ky) in enumerate(LEFT_SWITCHES):
        sx, sy = to_step_left(kx, ky)
        left_keycaps.append(make_keycap_solid(sx, sy, f"Left_Keycap_{idx+1}"))
    for idx, (kx, ky) in enumerate(RIGHT_SWITCHES):
        sx, sy = to_step_right(kx, ky)
        right_keycaps.append(make_keycap_solid(sx, sy, f"Right_Keycap_{idx+1}"))
    keycaps = left_keycaps + right_keycaps

    # Mid-mount USB-C (TYPE-C-31-M-13C) & TRRS (PJ-398A-5A) connectors
    left_conn_solids = make_usbc_and_trrs_solids(is_right=False)
    right_conn_solids = make_usbc_and_trrs_solids(is_right=True)
    conn_solids = left_conn_solids + right_conn_solids

    # Run interference checks
    print("\n--- Interference Verification ---")
    ov_cup_case = overlap_volume(cup_global, right_case)
    ov_cup_plate = overlap_volume(cup_global, right_plate)
    ov_cup_rpcb = overlap_volume(cup_global, right_pcb)
    ov_cup_spcb = overlap_volume(cup_global, sensor_pcb_global)
    ov_cup_ball = overlap_volume(cup_global, ball_global)
    ov_cup_lens = overlap_volume(cup_global, lens_global)
    ov_sensor_case = overlap_volume(sensor_global, right_case)
    ov_sensor_spcb = overlap_volume(sensor_global, sensor_pcb_global)
    ov_lens_spcb = overlap_volume(lens_global, sensor_pcb_global)
    ov_spcb_case = overlap_volume(sensor_pcb_global, right_case)
    ov_spcb_rpcb = overlap_volume(sensor_pcb_global, right_pcb)
    ov_rpcb_case = overlap_volume(right_pcb, right_case)
    ov_lpcb_case = overlap_volume(left_pcb, left_case)
    dist_opt = closest_points(ball_global, ref_point_global).distance

    ov_ckw12_plate = max(overlap_volume(s, right_plate) for s in ckw12_solids)
    ov_ckw12_pcb = max(overlap_volume(s, right_pcb) for s in ckw12_solids)
    ov_ckw12_screws = max(overlap_volume(s, t_scr) for s in ckw12_solids for t_scr in top_screws)

    ov_conn_case = max(
        max(overlap_volume(s, left_case) for s in left_conn_solids),
        max(overlap_volume(s, right_case) for s in right_conn_solids),
    )
    ov_conn_pcb = max(
        max(overlap_volume(s, left_pcb) for s in left_conn_solids),
        max(overlap_volume(s, right_pcb) for s in right_conn_solids),
    )
    ov_conn_plate = max(
        max(overlap_volume(s, left_plate) for s in left_conn_solids),
        max(overlap_volume(s, right_plate) for s in right_conn_solids),
    )

    sensor_smd_solids = make_sensor_and_jst_smd_solids()
    ov_smd_case = max(overlap_volume(s, right_case) for s in sensor_smd_solids)
    ov_smd_cup = max(overlap_volume(s, cup_global) for s in sensor_smd_solids)
    ov_smd_so = max(
        overlap_volume(s, so) for s in sensor_smd_solids for so in standoffs
    )

    print(f"Cup vs Right Case:       {ov_cup_case:.8f} mm^3")
    print(f"Cup vs Right Plate:      {ov_cup_plate:.8f} mm^3")
    print(f"Cup vs Right Main PCB:   {ov_cup_rpcb:.8f} mm^3")
    print(f"Cup vs Sensor PCB:       {ov_cup_spcb:.8f} mm^3")
    print(f"Cup vs 25mm Ball:        {ov_cup_ball:.8f} mm^3")
    print(f"Cup vs LM19 Lens:        {ov_cup_lens:.8f} mm^3")
    print(f"Sensor vs Right Case:    {ov_sensor_case:.8f} mm^3")
    print(f"Sensor vs Sensor PCB:    {ov_sensor_spcb:.8f} mm^3")
    print(f"LM19 Lens vs Sensor PCB: {ov_lens_spcb:.8f} mm^3")
    print(f"Sensor PCB vs Case:      {ov_spcb_case:.8f} mm^3")
    print(f"Sensor PCB vs Main PCB:  {ov_spcb_rpcb:.8f} mm^3")
    print(f"Right PCB vs Case:       {ov_rpcb_case:.8f} mm^3")
    print(f"Left PCB vs Case:        {ov_lpcb_case:.8f} mm^3")
    print(f"CKW12 vs Right Plate:    {ov_ckw12_plate:.8f} mm^3")
    print(f"CKW12 vs Right PCB:      {ov_ckw12_pcb:.8f} mm^3")
    print(f"CKW12 vs Top Screws:     {ov_ckw12_screws:.8f} mm^3")
    print(f"USBC/TRRS vs Cases:      {ov_conn_case:.8f} mm^3")
    print(f"USBC/TRRS vs Main PCBs:  {ov_conn_pcb:.8f} mm^3")
    print(f"USBC/TRRS vs Top Plates: {ov_conn_plate:.8f} mm^3")
    print(f"Sensor/JST SMDs vs Case: {ov_smd_case:.8f} mm^3")
    print(f"Sensor/JST SMDs vs Cup:  {ov_smd_cup:.8f} mm^3")
    print(f"Sensor/JST SMDs vs SOs:  {ov_smd_so:.8f} mm^3")
    print(f"Optical Distance (Ball Bottom Z=-10.20 to Ref Point Z=-12.60): {dist_opt:.6f} mm")

    max_so_ov = 0.0
    for so in standoffs:
        max_so_ov = max(
            max_so_ov,
            overlap_volume(so, right_case),
            overlap_volume(so, left_case),
            overlap_volume(so, right_pcb),
            overlap_volume(so, left_pcb),
            overlap_volume(so, sensor_pcb_global),
            overlap_volume(so, right_plate),
            overlap_volume(so, left_plate),
            overlap_volume(so, cup_global),
        )
    print(f"Max Standoff Overlap (vs Cases, PCBs, Plates, Cup): {max_so_ov:.8f} mm^3")

    max_bscr_ov = 0.0
    for b_scr in bottom_screws:
        max_bscr_ov = max(
            max_bscr_ov,
            overlap_volume(b_scr, right_case),
            overlap_volume(b_scr, left_case),
        )
    print(f"Max Bottom Screw Overlap vs Cases:          {max_bscr_ov:.8f} mm^3")

    max_tscr_ov = 0.0
    for t_scr in top_screws:
        max_tscr_ov = max(
            max_tscr_ov,
            overlap_volume(t_scr, right_plate),
            overlap_volume(t_scr, left_plate),
            overlap_volume(t_scr, cup_global),
            overlap_volume(t_scr, right_pcb),
            overlap_volume(t_scr, left_pcb),
        )
    print(f"Max Top Screw Overlap vs Plates/Cup/PCBs:   {max_tscr_ov:.8f} mm^3")

    max_scr_pair_ov = max(
        overlap_volume(b_scr, t_scr)
        for b_scr, t_scr in zip(bottom_screws, top_screws)
    )
    print(f"Max Top vs Bottom Screw Tip Overlap:        {max_scr_pair_ov:.8f} mm^3")

    max_cap_screw_ov = 0.0
    for t_scr in top_screws:
        for kc in keycaps:
            max_cap_screw_ov = max(max_cap_screw_ov, overlap_volume(t_scr, kc))
    print(f"Max Top Screw Head Overlap vs Keycaps:      {max_cap_screw_ov:.8f} mm^3")

    assert ov_cup_case == 0.0
    assert ov_cup_plate == 0.0
    assert ov_cup_rpcb == 0.0
    assert ov_cup_spcb == 0.0
    assert ov_cup_ball == 0.0
    assert ov_cup_lens == 0.0
    assert ov_sensor_case == 0.0
    assert ov_sensor_spcb == 0.0
    assert ov_lens_spcb == 0.0
    assert ov_spcb_case == 0.0
    assert ov_spcb_rpcb == 0.0
    assert ov_rpcb_case == 0.0
    assert ov_lpcb_case == 0.0
    assert ov_ckw12_plate == 0.0
    assert ov_ckw12_pcb == 0.0
    assert ov_ckw12_screws == 0.0
    assert ov_conn_case == 0.0
    assert ov_conn_pcb == 0.0
    assert ov_conn_plate == 0.0
    assert ov_smd_case == 0.0
    assert ov_smd_cup == 0.0
    assert ov_smd_so == 0.0
    assert max_so_ov == 0.0
    assert max_bscr_ov == 0.0
    assert max_tscr_ov == 0.0
    assert max_scr_pair_ov == 0.0
    assert max_cap_screw_ov == 0.0
    assert abs(dist_opt - 2.40) < 1e-6

    # --- Micro-Gap & Minimum Clearance Verification (Assembly Parts & 3D-Printed Wall Thickness) ---
    print("\n--- Micro-Gap & Wall-Thickness (<0.80mm) Verification ---")
    from generate_cases import verify_case_wall_thickness_and_gaps
    from generate_trackball_cup import verify_cup_wall_thickness_and_gaps

    verify_case_wall_thickness_and_gaps(left_case, is_right=False)
    verify_case_wall_thickness_and_gaps(right_case, is_right=True)
    verify_cup_wall_thickness_and_gaps(cup_local.solids()[0])

    rj3_solid = sensor_smd_solids[0]
    j1_solid = sensor_smd_solids[1]
    passive_smds = sensor_smd_solids[2:]

    clr_j1_case = closest_points(j1_solid, right_case).distance
    clr_rj3_case = closest_points(rj3_solid, right_case).distance
    clr_sensor_case = closest_points(sensor_global, right_case).distance
    clr_smds_case = min(closest_points(s, right_case).distance for s in passive_smds)
    clr_smds_so = min(closest_points(s, so).distance for s in sensor_smd_solids for so in standoffs)
    clr_ball_cup = closest_points(ball_global, cup_global).distance
    clr_cup_plate = closest_points(cup_global, right_plate).distance
    clr_cup_rpcb = closest_points(cup_global, right_pcb).distance
    clr_screw_tips = min(
        closest_points(b_scr, t_scr).distance
        for b_scr, t_scr in zip(bottom_screws, top_screws)
    )

    print(f"Min Clearance Sensor J1 vs Right Case:      {clr_j1_case:.4f} mm (req >= 0.12 mm)")
    print(f"Min Clearance Main rJ3 vs Right Case:       {clr_rj3_case:.4f} mm (req >= 0.50 mm)")
    print(f"Min Clearance PMW3360 Sensor vs Right Case: {clr_sensor_case:.4f} mm (req >= 1.50 mm)")
    print(f"Min Clearance Sensor SMDs vs Right Case:    {clr_smds_case:.4f} mm (req >= 0.50 mm)")
    print(f"Min Clearance Sensor SMDs vs Standoffs:     {clr_smds_so:.4f} mm (req >= 0.80 mm)")
    print(f"Min Clearance 25mm Ball vs Trackball Cup:   {clr_ball_cup:.4f} mm (req >= 0.30 mm)")
    print(f"Min Clearance Trackball Cup vs Right Plate: {clr_cup_plate:.4f} mm (req >= 0.25 mm)")
    print(f"Min Clearance Trackball Cup vs Right PCB:   {clr_cup_rpcb:.4f} mm (req >= 0.25 mm)")
    print(f"Min Clearance Top vs Bottom Screw Tips:     {clr_screw_tips:.4f} mm (req >= 1.00 mm)")

    assert clr_j1_case >= 0.12, f"J1 too close to Right Case: {clr_j1_case:.4f} mm"
    assert clr_rj3_case >= 0.50, f"rJ3 too close to Right Case: {clr_rj3_case:.4f} mm"
    assert clr_sensor_case >= 1.50, f"PMW3360 too close to Right Case: {clr_sensor_case:.4f} mm"
    assert clr_smds_case >= 0.50, f"Sensor SMDs too close to Right Case: {clr_smds_case:.4f} mm"
    assert clr_smds_so >= 0.80, f"Sensor SMDs too close to Standoffs: {clr_smds_so:.4f} mm"
    assert clr_ball_cup >= 0.30, f"25mm Ball too close to Cup: {clr_ball_cup:.4f} mm"
    assert clr_cup_plate >= 0.25, f"Cup too close to Right Plate: {clr_cup_plate:.4f} mm"
    assert clr_cup_rpcb >= 0.25, f"Cup too close to Right PCB: {clr_cup_rpcb:.4f} mm"
    assert clr_screw_tips >= 1.00, f"Top/Bottom screws too close: {clr_screw_tips:.4f} mm"

    all_parts = (
        [
            left_case,
            right_case,
            left_pcb,
            right_pcb,
            sensor_pcb_global,
            left_plate,
            right_plate,
            cup_global,
            ball_global,
            lens_global,
            sensor_global,
            ref_point_global,
        ]
        + ckw12_solids
        + conn_solids
        + standoffs
        + bottom_screws
        + top_screws
        + keycaps
    )

    asm_full = bd.Compound(children=all_parts)
    asm_full.label = "curcur40_Full_Assembly"
    out_step = CASES_DIR / "assembly-full.step"
    bd.export_step(asm_full, str(out_step))
    print(
        f"\nSuccessfully exported {out_step} ({len(all_parts)} items, valid={asm_full.is_valid})"
    )

    # Build & export Desk-Horizontal Full Assembly (cases/assembly-full-desk.step)
    left_group = [left_case, left_pcb, left_plate] + left_conn_solids + left_fasteners + left_keycaps
    right_group = (
        [
            right_case,
            right_pcb,
            sensor_pcb_global,
            right_plate,
            cup_global,
            ball_global,
            lens_global,
            sensor_global,
            ref_point_global,
        ]
        + ckw12_solids
        + right_conn_solids
        + right_fasteners
        + right_keycaps
    )

    desk_parts = [transform_to_desk(p, False) for p in left_group] + [
        transform_to_desk(p, True) for p in right_group
    ]
    asm_desk = bd.Compound(children=desk_parts)
    asm_desk.label = "curcur40_Full_Assembly_Desk"
    out_desk_step = CASES_DIR / "assembly-full-desk.step"
    bd.export_step(asm_desk, str(out_desk_step))
    bb_desk_l = desk_parts[0].bounding_box()
    bb_desk_r = desk_parts[len(left_group)].bounding_box()
    print(
        f"Successfully exported {out_desk_step} ({len(desk_parts)} items, valid={asm_desk.is_valid}, "
        f"Left Case Z=[{bb_desk_l.min.Z:.4f}, {bb_desk_l.max.Z:.4f}], "
        f"Right Case Z=[{bb_desk_r.min.Z:.4f}, {bb_desk_r.max.Z:.4f}])"
    )


if __name__ == "__main__":
    main()
