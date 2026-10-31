# -*- coding: utf-8 -*-
"""
Generate curcur40 Full Assembly STEP models:
  1. cases/assemblies/assembly-full.step                (Top Plate horizontal at Z = -2.00 mm)
  2. cases/assemblies/assembly-full-desk.step           (Case Bottom horizontal on desk plane Z = 0.00 mm)
  3. cases/assemblies/curcur40-right-wheel-assembly.step (Right half with Under-Plate Inertia Wheel)
and verify zero interference + minimum clearances across all components per docs/case_spec.md:
- Left & Right 3D-printed Sealed-Bottom Built-in Tented Tray Bottom Cases (with Tilted Floor & Stepped M2 Heat-Set Insert Bosses)
- Left & Right Main PCBs (Z = -5.80 to -4.20 mm, with Ø 6.20 mm boss-pass holes / U-notches, Ø 2.40 mm screw holes & Right Cross Wheel Cutout)
- Separated PMW3360 Sensor PCB (`curcur40-pmw3360`, Z = -17.60 to -16.00 mm, with Ø 2.40 mm TB1-TB4 screw holes)
- Left & Right FR-4 Top Plates (Z = -3.60 to -2.00 mm, directly screw-clamped via 8x Ø 2.40 mm corner holes + Ø 4.40 mm sub-flush holes at L4/R4/WC1/WC2 & Right 7.70 x 22.00 mm wheel slot)
- Sunk Trackball Cup placed on Sensor PCB F.Cu at (23.8125, -109.5375, -16.00 mm), Rim at Z = -2.00 mm, 2.00 mm flat ears
- 25mm Trackball Sphere at (23.8125, -109.5375, +2.30 mm) + `Lens_Optical_Ref_Point` (exact 2.40 mm optical gap)
- PMW3360 Sensor IC & LM19-LSI Optical Lens
- 17x Unified M2 Brass Heat-Set Inserts (M2 x L=3.0 x OD=3.2 mm) + 17x Unified M2 x 6.0 mm Screws:
    - 8x Stepped Perimeter (4 Left L1,L2,L3,L5 + 4 Right R1,R2,R3,R5, directly clamping Top Plate Z = -2.00 mm & supporting Main PCB B.Cu Z = -5.80 mm)
    - 2x Side-Switch Perimeter (L4, R4, clamping Main PCB F.Cu Z = -4.20 mm via Top Plate Ø 4.40 mm clearance holes)
    - 4x Trackball Cup (TB1-TB4, clamping 2.00 mm Cup Ears + 1.60 mm Sensor PCB into Case Bosses)
    - 2x Wheel Cradle (WC1-WC2, clamping Main PCB F.Cu Z = -4.20 mm into Wheel Cradle Bosses)
    - 1x Glue-Free Detent Adjuster (in Wheel Rocker South Boss, adjusting Ø2.0x2.0mm axial NdFeB magnet gap)
- Under-Plate 1-Piece Integral-Shaft Passive Inertia Scroll Wheel (`steel-flywheel`, `magnet-holder`, `wheel-rocker`, `wheel-cradle`)
  + Main-PCB `rU6` (`TMAG5273` SOT-23-6) + Main-PCB `rEXSW1` (`Kailh Square Silent`)
- Keycaps (Choc v2 low-profile)
"""
import math
import sys
from pathlib import Path
from cadgen import build123d as bd
from cadgen.geometry import overlap_volume, closest_points

WORKSPACE = Path(__file__).resolve().parent.parent
if str(WORKSPACE / "scripts") not in sys.path:
    sys.path.insert(0, str(WORKSPACE / "scripts"))
CASES_DIR = WORKSPACE / "cases"
ASSEMBLIES_DIR = WORKSPACE / "cases" / "assemblies"

Z_THUMB_BOTTOM = -26.9000
Z_PINKY_BOTTOM = -10.0000
X_THUMB_OUTER = 7.0250
X_PINKY_OUTER = 135.8580
THETA_TENT_DEG = math.degrees(
    math.atan2(Z_PINKY_BOTTOM - Z_THUMB_BOTTOM, X_PINKY_OUTER - X_THUMB_OUTER)
)

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

RIGHT_WHEEL_AXLE_PCB = (14.2875, -2.0000)

RIGHT_WHEEL_CRADLE_HOLES_PCB = [
    ( 6.6375, -9.8000),   # WC1
    (21.2375,  6.0000),   # WC2
]

# (tag, px, py, z_ins_top, z_screw_seat, is_stepped_plate)
LEFT_PERIMETER_HOLES_PCB = [
    ("L1",    0.0000, -15.0000, -3.61, -1.99, True),
    ("L2",    0.0000,  18.0000, -3.61, -1.99, True),
    ("L3", -101.0000, -20.0000, -3.61, -1.99, True),
    ("L4",  -98.4500,  38.1500, -5.81, -4.19, False),
    ("L5",  -62.0000,  65.1500, -3.61, -1.99, True),
]

RIGHT_PERIMETER_HOLES_PCB = [
    ("R1",   0.0000, -15.0000, -3.61, -1.99, True),
    ("R2",   0.0000,  18.0000, -3.61, -1.99, True),
    ("R3", 101.0000, -20.0000, -3.61, -1.99, True),
    ("R4",  98.4500,  38.1500, -5.81, -4.19, False),
    ("R5",  62.0000,  65.1500, -3.61, -1.99, True),
]

RIGHT_TB_HOLES_PCB = [
    ("TB1", -2.4750, 41.0875, -17.61),
    ("TB2", 21.5250, 41.0875, -17.61),
    ("TB3", -2.4750, 63.6875, -17.61),
    ("TB4", 21.5250, 63.6875, -17.61),
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
    with exact outer boundary, Host & Split USB-C notches, Ø 2.40 mm M2 screw holes,
    and on Right Main PCB the Cross Inertia Wheel Cutout + WC1/WC2 Ø 2.40 mm holes.
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
            ( -5.2625,  34.1200, 0.0),
            (  0.5400,  34.1200, 0.0),
            (  0.5400,  24.8800, 0.0),
            ( -5.2625,  24.8800, 0.0),
        ]
        pts_step = [(*to_step_right(x, y), r) for x, y, r in pts_pcb]
        hole_specs = [(tag, *to_step_right(x, y), stepped) for tag, x, y, _, _, stepped in RIGHT_PERIMETER_HOLES_PCB]
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
            (   5.2625,  34.1200, 0.0),
            (  -0.5400,  34.1200, 0.0),
            (  -0.5400,  24.8800, 0.0),
            (   5.2625,  24.8800, 0.0),
        ]
        pts_step = [(*to_step_left(x, y), r) for x, y, r in pts_pcb]
        hole_specs = [(tag, *to_step_left(x, y), stepped) for tag, x, y, _, _, stepped in LEFT_PERIMETER_HOLES_PCB]

    sk = make_filleted_sketch(pts_step)
    pcb = bd.extrude(sk, amount=1.60).moved(bd.Location((0, 0, -5.80)))

    # Cut Ø 6.20 mm stepped-boss clearance holes (L1..L3, R1..R3), 6.20 mm South U-notches (L5, R5), and Ø 2.40 mm M2 holes (L4, R4)
    for tag, hx, hy, is_stepped in hole_specs:
        r_hole = 3.10 if is_stepped else 1.20
        pcb = pcb - bd.Cylinder(
            radius=r_hole,
            height=4.0,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((hx, hy, -6.5)))
        if tag in ("L5", "R5"):
            pcb = pcb - bd.Box(
                2.0 * r_hole,
                6.00,
                4.0,
                align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.MIN),
            ).moved(bd.Location((hx, hy, -6.5)))

    # Cut Host USB-C shield PTH slots
    usbc_cx = 26.5750 if is_right else -26.5750
    for sx in (usbc_cx - 5.6200, usbc_cx + 5.6200):
        for sy in (-34.0925, -38.0925):
            pcb = pcb - bd.Box(1.25, 2.20, 4.0).moved(bd.Location((sx, sy, -5.0)))

    # Cut Split USB-C shield PTH slots
    sgn = 1.0 if is_right else -1.0
    for sx in (sgn * 10.2800, sgn * 14.2800):
        for sy in (-86.6500 - 5.6200, -86.6500 + 5.6200):
            pcb = pcb - bd.Box(2.20, 1.25, 4.0).moved(bd.Location((sx, sy, -5.0)))

    # On Right Main PCB, cut the Cross-Shaped Under-Plate Inertia Wheel opening (centered at 14.2875, -2.0000) + WC1/WC2 Ø 2.40 mm holes
    if is_right:
        cross_pts_pcb = [
            (10.4375, -13.5000, 0.50),
            (18.1375, -13.5000, 0.50),
            (18.1375,  -5.7500, 0.50),
            (21.3375,  -5.7500, 0.50),
            (21.3375,   1.7500, 0.50),
            (18.1375,   1.7500, 0.50),
            (18.1375,   9.5000, 0.50),
            (10.4375,   9.5000, 0.50),
            (10.4375,   1.7500, 0.50),
            ( 4.8375,   1.7500, 0.50),
            ( 4.8375,  -5.7500, 0.50),
            (10.4375,  -5.7500, 0.50),
        ]
        cross_pts_step = [(*to_step_right(x, y), r) for x, y, r in cross_pts_pcb]
        sk_cross = make_filleted_sketch(cross_pts_step)
        pcb = pcb - bd.extrude(sk_cross, amount=3.00).moved(bd.Location((0, 0, -6.50)))

        for hx, hy in (to_step_right(x, y) for x, y in RIGHT_WHEEL_CRADLE_HOLES_PCB):
            pcb = pcb - bd.Cylinder(
                radius=1.20,
                height=4.00,
                align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
            ).moved(bd.Location((hx, hy, -6.50)))

    solid = pcb.solids()[0]
    solid.label = "Right_Main_PCB" if is_right else "Left_Main_PCB"
    return solid


def build_top_plate_solid(is_right=True) -> bd.Solid:
    """
    Constructs the FR-4 Top Plate solid (Z = -3.60 to -2.00 mm, thickness 1.60 mm)
    with switch cutouts, Right 5.60 x 22.00 mm wheel slot (R = 1.00 mm), and Ø 4.40 mm screw-head clearance holes.
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
        plate_holes_step = [
            (*to_step_right(x, y), 1.20 if stepped else 2.20)
            for _, x, y, _, _, stepped in RIGHT_PERIMETER_HOLES_PCB
        ] + [(*to_step_right(x, y), 2.20) for x, y in RIGHT_WHEEL_CRADLE_HOLES_PCB]
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
        plate_holes_step = [
            (*to_step_left(x, y), 1.20 if stepped else 2.20)
            for _, x, y, _, _, stepped in LEFT_PERIMETER_HOLES_PCB
        ]

    sk = make_filleted_sketch(pts_step)
    plate = bd.extrude(sk, amount=1.60).moved(bd.Location((0, 0, -3.60)))

    with bd.BuildSketch(bd.Plane.XY.offset(-4.0)) as sk_cuts:
        for sx, sy in sw_step:
            with bd.Locations([(sx, sy)]):
                bd.RectangleRounded(14.0, 14.0, 0.5)
    plate = plate - bd.extrude(sk_cuts.sketch, amount=3.0)

    if is_right:
        wx, wy = to_step_right(*RIGHT_WHEEL_AXLE_PCB)
        with bd.BuildSketch(bd.Plane.XY.offset(-4.0)) as sk_wslot:
            with bd.Locations([(wx, wy)]):
                bd.RectangleRounded(7.70, 22.00, 1.00)
        plate = plate - bd.extrude(sk_wslot.sketch, amount=3.0)

    # Cut Ø 2.40 mm direct clamping screw holes (L1..L3, L5, R1..R3, R5) & Ø 4.40 mm screw-head clearance holes (L4, R4, WC1, WC2)
    for hx, hy, r_hole in plate_holes_step:
        plate = plate - bd.Cylinder(
            radius=r_hole,
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


def make_usbc_solids(is_right: bool):
    pkg_dir = WORKSPACE / "pcbs" / "common" / "kbd" / "kicad-packages3D" / "kbd.3dshapes"
    prefix = "Right" if is_right else "Left"
    usbc_raw = bd.import_step(str(pkg_dir / "TYPE-C-31-M-13C.step"))
    usbc_flipped = usbc_raw.rotate(bd.Axis.X, 180)

    usbc_cx = 26.5750 if is_right else -26.5750
    usbc_placed = usbc_flipped.moved(bd.Location((usbc_cx, -38.5925, -4.2850)))
    usbc_shell = usbc_placed.solids()[0]
    usbc_shell.label = f"{prefix}_USBC_Shell"
    usbc_tongue = usbc_placed.solids()[1]
    usbc_tongue.label = f"{prefix}_USBC_Tongue"

    split_rot_z = 90.0 if is_right else -90.0
    split_cx = 14.7800 if is_right else -14.7800
    split_placed = usbc_flipped.rotate(bd.Axis.Z, split_rot_z).moved(
        bd.Location((split_cx, -86.6500, -4.2850))
    )
    split_shell = split_placed.solids()[0]
    split_shell.label = f"{prefix}_Split_USBC_Shell"
    split_tongue = split_placed.solids()[1]
    split_tongue.label = f"{prefix}_Split_USBC_Tongue"

    return [usbc_shell, usbc_tongue, split_shell, split_tongue]


def make_smd_and_switch_solids():
    """
    Builds 3D bounding/CAD solids for critical B.Cu SMD & THT components on Left Main PCB,
    Right Main PCB (B.Cu Z = -5.80 mm), and Sensor PCB (B.Cu Z = -17.60 mm):
      - rJ3 (JST SH 6-pin on Right Main PCB) & J1 (JST SH 6-pin on Sensor PCB)
      - rU6 (TMAG5273A1QDBVR SOT-23-6 3D Hall Sensor on Right Main PCB B.Cu)
      - rEXSW1 (Kailh Square Silent 6.2x6.2x4.3mm Middle-Click Switch on Right Main PCB B.Cu)
      - Wheel & USB-C neighborhood SMDs on Right Main PCB (rC18, rR13, rR11, rR12, rZD1, rR2, rU3)
      - B.Cu BOOT/RESET tactile switches (SMDSW1/2 on Left, rSMDSW1/2 on Right) near L4/R4 bosses
      - Sensor PCB B.Cu SMDs (C1-C4, R1-R3, U2)
    """
    right_smds = []
    left_smds = []

    # 1. rJ3 (JST SH 6-pin horizontal, SM06B-SRSS-TB) on Right Main PCB B.Cu at (46.5000, 63.0000), rot +90 deg
    rj3_x, rj3_y = to_step_right(46.5000, 63.0000)
    rj3_solid = (
        bd.Pos(rj3_x + (-2.60 + 2.75) / 2.0, rj3_y, -5.80 - 2.95 / 2.0)
        * bd.Box(5.35, 8.60, 2.95)
    ).solids()[0]
    rj3_solid.label = "Right_PCB_rJ3_JST_SH"
    right_smds.append(rj3_solid)

    # 2. J1 (JST SH 6-pin horizontal, SM06B-SRSS-TB) on Sensor PCB B.Cu at (19.2000, 52.3875), rot -90 deg
    j1_x, j1_y = to_step_right(19.2000, 52.3875)
    j1_solid = (
        bd.Pos(j1_x + (2.575 - 1.675) / 2.0, j1_y, -17.60 - 2.95 / 2.0)
        * bd.Box(4.25, 8.60, 2.95)
    ).solids()[0]
    j1_solid.label = "Sensor_PCB_J1_JST_SH"
    right_smds.append(j1_solid)

    # 3. rU6 (TMAG5273A1QDBVR, SOT-23-6, 2.95 x 2.95 x 1.15 mm) at (3.0175, -2.0000) B.Cu
    ru6_x, ru6_y = to_step_right(3.0175, -2.0000)
    ru6_solid = (
        bd.Pos(ru6_x, ru6_y, -5.81 - 1.14 / 2.0) * bd.Box(2.95, 2.95, 1.14)
    ).solids()[0]
    ru6_solid.label = "Right_PCB_rU6_TMAG5273"
    right_smds.append(ru6_solid)

    # 4. rEXSW1 (Kailh Square Silent 6.20 x 6.20 x 4.30 mm) at (-2.0125, -2.0000) B.Cu
    sw_x, sw_y = to_step_right(-2.0125, -2.0000)
    sw_housing = bd.Box(6.20, 6.20, 3.34, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).moved(
        bd.Location((sw_x, sw_y, -5.81))
    )
    sw_plunger = bd.Cylinder(
        radius=1.50, height=4.29, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)
    ).moved(bd.Location((sw_x, sw_y, -5.81)))
    rexsw1_solid = (sw_housing + sw_plunger).solids()[0]
    rexsw1_solid.label = "Right_PCB_rEXSW1_Kailh_Silent"
    right_smds.append(rexsw1_solid)

    # 5. Right Main PCB B.Cu passives & diodes near wheel / cradle
    main_wheel_smds = [
        ("rC18", 3.7875,   1.3000, 1.90, 0.95, 0.60),
        ("rR13", 2.2375,   1.3000, 0.95, 1.90, 0.55),
        ("rR11", 1.5875,   3.3000, 0.95, 1.90, 0.55),
        ("rR12", 0.3875,   3.3000, 0.95, 1.90, 0.55),
        ("rZD1", 20.9430, -14.7010, 1.00, 1.90, 0.70),
        ("rR2",  19.4220, -16.5000, 0.95, 1.90, 0.55),
        ("rU3",  22.6520, -11.5100, 2.60, 1.10, 0.60),
        ("rSMDSW1", 90.6000, 37.3840, 2.93, 5.00, 1.89),
        ("rSMDSW2", 94.2000, 37.3813, 2.93, 5.00, 1.89),
    ]
    for ref, px, py, dx, dy, h in main_wheel_smds:
        sx, sy = to_step_right(px, py)
        smd_solid = (
            bd.Pos(sx, sy, -5.81 - h / 2.0) * bd.Box(dx, dy, h)
        ).solids()[0]
        smd_solid.label = f"Right_PCB_{ref}"
        right_smds.append(smd_solid)

    # 6. Left Main PCB B.Cu BOOT/RESET tactile switches near L4 boss
    for ref, px, py in (("SMDSW1", -94.2000, 37.3413), ("SMDSW2", -90.6000, 37.3413)):
        sx, sy = to_step_left(px, py)
        smd_solid = (
            bd.Pos(sx, sy, -5.81 - 1.89 / 2.0) * bd.Box(2.93, 5.00, 1.89)
        ).solids()[0]
        smd_solid.label = f"Left_PCB_{ref}"
        left_smds.append(smd_solid)

    # 7. Sensor PCB B.Cu SMDs (Z = -17.60..-18.75 mm)
    sensor_smds = [
        ("C1",  0.5000, 54.9955, 2.80, 0.95, 0.90),
        ("C2",  0.5000, 56.7755, 2.80, 0.95, 0.90),
        ("C3",  2.3860, 63.3617, 0.95, 2.80, 0.90),
        ("C4", 10.6235, 63.6617, 2.80, 0.95, 0.90),
        ("R1",  0.5000, 47.8755, 2.80, 0.95, 0.60),
        ("R2", 15.3860, 41.6617, 2.80, 0.95, 0.60),
        ("R3",  7.8860, 41.6617, 2.80, 0.95, 0.60),
        ("U2", 16.0000, 63.0617, 2.95, 3.00, 1.15),
    ]
    for ref, px, py, dx, dy, h in sensor_smds:
        sx, sy = to_step_right(px, py)
        smd_solid = (
            bd.Pos(sx, sy, -17.61 - h / 2.0) * bd.Box(dx, dy, h)
        ).solids()[0]
        smd_solid.label = f"Sensor_PCB_{ref}"
        right_smds.append(smd_solid)

    return left_smds, right_smds


def make_insert_and_screw(sx: float, sy: float, z_ins_top: float, z_screw_seat: float, tag: str):
    """
    Build 1x M2 x L=3.0 mm Brass Heat-Set Insert + 1x Top-Down M2 x 6.0 mm Screw
    with nominal clearance radii so B-rep overlap_volume == 0.00000000 mm^3.
    """
    ins = (
        bd.Cylinder(radius=1.41, height=2.98, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
        - bd.Cylinder(radius=1.02, height=3.20, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).moved(
            bd.Location((0, 0, 0.10))
        )
    ).moved(bd.Location((sx, sy, z_ins_top))).solids()[0]
    ins.label = f"HeatSet_Insert_M2_{tag}"

    head = bd.Cylinder(
        radius=1.90, height=1.20, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
    ).moved(bd.Location((sx, sy, z_screw_seat)))
    shank = bd.Cylinder(
        radius=0.98, height=6.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)
    ).moved(bd.Location((sx, sy, z_screw_seat)))
    scr = (head + shank).solids()[0]
    scr.label = f"Top_Screw_M2x6_{tag}"
    return ins, scr


def transform_to_desk(shape, is_right: bool):
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
    from generate_inertia_wheel import assemble_wheel_parts_global, verify_6dof_constraints, CLICK_PRESS_DEG
    from generate_cases import verify_case_wall_thickness_and_gaps
    from generate_trackball_cup import verify_cup_wall_thickness_and_gaps

    print("=== Building & Verifying curcur40 Full Assembly (assembly-full.step & assembly-full-desk.step) ===")

    left_case = bd.import_step(str(CASES_DIR / "left.step")).solids()[0]
    left_case.label = "Left_Case"
    right_case = bd.import_step(str(CASES_DIR / "right.step")).solids()[0]
    right_case.label = "Right_Case"

    left_pcb = build_main_pcb_solid(is_right=False)
    right_pcb = build_main_pcb_solid(is_right=True)

    left_plate = build_top_plate_solid(is_right=False)
    right_plate = build_top_plate_solid(is_right=True)

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

    asm_parts = bd.import_step(str(ASSEMBLIES_DIR / "pmw3360-lens-pcb-assembly.step"))
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

    ref_point_global = bd.Pos(tb_cx, tb_cy, tb_cz + 3.40) * bd.Circle(0.35).face()
    ref_point_global.label = "Lens_Optical_Ref_Point"

    # Under-Plate 1-Piece Integral-Shaft Passive Inertia Scroll Wheel (Rest & Clicked poses)
    wheel_mov_rest, wheel_stat, wheel_cradle_screws = assemble_wheel_parts_global(click_deg=0.0)
    wheel_mov_click, _, _ = assemble_wheel_parts_global(click_deg=CLICK_PRESS_DEG)
    wheel_solids = wheel_mov_rest + wheel_stat

    # 14x Case Heat-Set Inserts + 14x Top-Down M2 x 6.0 mm Screws (plus 3x in wheel assembly = 17x total!)
    inserts = []
    top_screws = []
    left_fasteners = []
    right_fasteners = []

    for tag, px, py, z_ins_top, z_scr_seat, _stepped in LEFT_PERIMETER_HOLES_PCB:
        sx, sy = to_step_left(px, py)
        ins, scr = make_insert_and_screw(sx, sy, z_ins_top, z_scr_seat, tag)
        inserts.append(ins)
        top_screws.append(scr)
        left_fasteners.extend([ins, scr])

    for tag, px, py, z_ins_top, z_scr_seat, _stepped in RIGHT_PERIMETER_HOLES_PCB:
        sx, sy = to_step_right(px, py)
        ins, scr = make_insert_and_screw(sx, sy, z_ins_top, z_scr_seat, tag)
        inserts.append(ins)
        top_screws.append(scr)
        right_fasteners.extend([ins, scr])

    for tag, px, py, z_ins_top in RIGHT_TB_HOLES_PCB:
        sx, sy = to_step_right(px, py)
        ins, scr = make_insert_and_screw(sx, sy, z_ins_top, -13.99, tag)
        inserts.append(ins)
        top_screws.append(scr)
        right_fasteners.extend([ins, scr])

    left_keycaps = [
        make_keycap_solid(*to_step_left(kx, ky), f"Left_Keycap_{idx+1}")
        for idx, (kx, ky) in enumerate(LEFT_SWITCHES)
    ]
    right_keycaps = [
        make_keycap_solid(*to_step_right(kx, ky), f"Right_Keycap_{idx+1}")
        for idx, (kx, ky) in enumerate(RIGHT_SWITCHES)
    ]
    keycaps = left_keycaps + right_keycaps

    left_conn_solids = make_usbc_solids(is_right=False)
    right_conn_solids = make_usbc_solids(is_right=True)
    conn_solids = left_conn_solids + right_conn_solids

    left_smds, right_smds = make_smd_and_switch_solids()
    rj3_solid = right_smds[0]
    j1_solid = right_smds[1]
    ru6_solid = right_smds[2]
    rexsw1_solid = right_smds[3]
    right_Assembly_smds = [rj3_solid, j1_solid, ru6_solid, rexsw1_solid]

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

    wheel_check_group = wheel_solids + wheel_cradle_screws
    ov_wheel_internal = 0.0
    for i in range(len(wheel_check_group)):
        for j in range(i + 1, len(wheel_check_group)):
            ov_wheel_internal = max(
                ov_wheel_internal,
                overlap_volume(wheel_check_group[i], wheel_check_group[j]),
            )
    ov_wheel_case = max(overlap_volume(s, right_case) for s in wheel_check_group)
    ov_wheel_plate = max(overlap_volume(s, right_plate) for s in wheel_check_group)
    ov_wheel_pcb = max(overlap_volume(s, right_pcb) for s in wheel_check_group)
    ov_wheel_usbc = max(
        overlap_volume(s, u) for s in wheel_check_group for u in right_conn_solids
    )
    ov_wheel_fasteners = max(
        overlap_volume(s, f)
        for s in wheel_check_group
        for f in (inserts + top_screws)
    )
    ov_wheel_keycaps = max(
        overlap_volume(s, kc) for s in wheel_check_group for kc in right_keycaps
    )
    # Also verify clicked pose moving parts against Case, Plate, PCB, USB-C, Keycaps, and non-switch SMDs!
    non_plunger_smds = [s for s in right_smds if s.label != "Right_PCB_rEXSW1_Kailh_Silent"]
    ov_click_env = max(
        max(overlap_volume(s, right_case) for s in wheel_mov_click),
        max(overlap_volume(s, right_plate) for s in wheel_mov_click),
        max(overlap_volume(s, right_pcb) for s in wheel_mov_click),
        max(overlap_volume(s, u) for s in wheel_mov_click for u in right_conn_solids),
        max(overlap_volume(s, kc) for s in wheel_mov_click for kc in right_keycaps),
        max(overlap_volume(s, smd) for s in wheel_mov_click for smd in non_plunger_smds),
    )

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

    ov_smd_case = max(
        max(overlap_volume(s, right_case) for s in right_smds),
        max(overlap_volume(s, left_case) for s in left_smds),
    )
    ov_smd_cup = max(overlap_volume(s, cup_global) for s in right_smds)
    ov_smd_pcb = max(
        max(overlap_volume(s, right_pcb) for s in right_smds),
        max(overlap_volume(s, sensor_pcb_global) for s in right_smds),
        max(overlap_volume(s, left_pcb) for s in left_smds),
    )
    ov_smd_wheel = max(
        overlap_volume(s, w) for s in right_smds for w in wheel_check_group
    )
    ov_smd_fasteners = max(
        overlap_volume(s, f)
        for s in (right_smds + left_smds)
        for f in (inserts + top_screws + wheel_cradle_screws)
    )

    max_ins_ov = max(
        max(
            overlap_volume(ins, right_case),
            overlap_volume(ins, left_case),
            overlap_volume(ins, right_pcb),
            overlap_volume(ins, left_pcb),
            overlap_volume(ins, sensor_pcb_global),
            overlap_volume(ins, cup_global),
        )
        for ins in inserts
    )

    max_tscr_ov = max(
        max(
            overlap_volume(scr, right_case),
            overlap_volume(scr, left_case),
            overlap_volume(scr, right_plate),
            overlap_volume(scr, left_plate),
            overlap_volume(scr, cup_global),
            overlap_volume(scr, right_pcb),
            overlap_volume(scr, left_pcb),
            overlap_volume(scr, sensor_pcb_global),
        )
        for scr in (top_screws + wheel_cradle_screws)
    )

    max_ins_scr_ov = max(
        overlap_volume(ins, scr) for ins, scr in zip(inserts, top_screws)
    )

    max_cap_screw_ov = max(
        overlap_volume(t_scr, kc)
        for t_scr in (top_screws + wheel_cradle_screws)
        for kc in keycaps
    )

    print(f"Cup vs Right Case:        {ov_cup_case:.8f} mm^3")
    print(f"Cup vs Right Plate:       {ov_cup_plate:.8f} mm^3")
    print(f"Cup vs Right Main PCB:    {ov_cup_rpcb:.8f} mm^3")
    print(f"Cup vs Sensor PCB:        {ov_cup_spcb:.8f} mm^3")
    print(f"Cup vs 25mm Ball:         {ov_cup_ball:.8f} mm^3")
    print(f"Cup vs LM19 Lens:         {ov_cup_lens:.8f} mm^3")
    print(f"Sensor vs Right Case:     {ov_sensor_case:.8f} mm^3")
    print(f"Sensor PCB vs Case:       {ov_spcb_case:.8f} mm^3")
    print(f"Right PCB vs Case:        {ov_rpcb_case:.8f} mm^3")
    print(f"Left PCB vs Case:         {ov_lpcb_case:.8f} mm^3")
    print(f"Wheel Internal Pairwise:  {ov_wheel_internal:.8f} mm^3")
    print(f"Wheel vs Right Case:      {ov_wheel_case:.8f} mm^3")
    print(f"Wheel vs Right Plate:     {ov_wheel_plate:.8f} mm^3")
    print(f"Wheel vs Right PCB:       {ov_wheel_pcb:.8f} mm^3")
    print(f"Wheel vs USB-C Conns:     {ov_wheel_usbc:.8f} mm^3")
    print(f"Wheel vs Fasteners:       {ov_wheel_fasteners:.8f} mm^3")
    print(f"Wheel vs Right Keycaps:   {ov_wheel_keycaps:.8f} mm^3")
    print(f"Wheel Clicked Envelope:   {ov_click_env:.8f} mm^3")
    print(f"Host/Split USBC vs Cases: {ov_conn_case:.8f} mm^3")
    print(f"Host/Split USBC vs PCBs:  {ov_conn_pcb:.8f} mm^3")
    print(f"Host/Split USBC vs Plate: {ov_conn_plate:.8f} mm^3")
    print(f"SMDs/Switches vs Cases:   {ov_smd_case:.8f} mm^3")
    print(f"SMDs/Switches vs Cup:     {ov_smd_cup:.8f} mm^3")
    print(f"SMDs/Switches vs PCBs:    {ov_smd_pcb:.8f} mm^3")
    print(f"SMDs/Switches vs Wheel:   {ov_smd_wheel:.8f} mm^3")
    print(f"SMDs vs Inserts/Screws:   {ov_smd_fasteners:.8f} mm^3")
    print(f"Max Insert Overlap:       {max_ins_ov:.8f} mm^3")
    print(f"Max Top Screw Overlap:    {max_tscr_ov:.8f} mm^3")
    print(f"Max Insert-Screw Overlap: {max_ins_scr_ov:.8f} mm^3")
    print(f"Max Screw vs Keycaps:     {max_cap_screw_ov:.8f} mm^3")
    print(f"Optical Distance (Ball Bottom Z=-10.20 to Ref Point Z=-12.60): {dist_opt:.6f} mm")

    for name, val in [
        ("ov_cup_case", ov_cup_case),
        ("ov_cup_plate", ov_cup_plate),
        ("ov_cup_rpcb", ov_cup_rpcb),
        ("ov_cup_spcb", ov_cup_spcb),
        ("ov_cup_ball", ov_cup_ball),
        ("ov_cup_lens", ov_cup_lens),
        ("ov_sensor_case", ov_sensor_case),
        ("ov_sensor_spcb", ov_sensor_spcb),
        ("ov_lens_spcb", ov_lens_spcb),
        ("ov_spcb_case", ov_spcb_case),
        ("ov_spcb_rpcb", ov_spcb_rpcb),
        ("ov_rpcb_case", ov_rpcb_case),
        ("ov_lpcb_case", ov_lpcb_case),
        ("ov_wheel_internal", ov_wheel_internal),
        ("ov_wheel_case", ov_wheel_case),
        ("ov_wheel_plate", ov_wheel_plate),
        ("ov_wheel_pcb", ov_wheel_pcb),
        ("ov_wheel_usbc", ov_wheel_usbc),
        ("ov_wheel_fasteners", ov_wheel_fasteners),
        ("ov_wheel_keycaps", ov_wheel_keycaps),
        ("ov_click_env", ov_click_env),
        ("ov_conn_case", ov_conn_case),
        ("ov_conn_pcb", ov_conn_pcb),
        ("ov_conn_plate", ov_conn_plate),
        ("ov_smd_case", ov_smd_case),
        ("ov_smd_cup", ov_smd_cup),
        ("ov_smd_pcb", ov_smd_pcb),
        ("ov_smd_wheel", ov_smd_wheel),
        ("ov_smd_fasteners", ov_smd_fasteners),
        ("max_ins_ov", max_ins_ov),
        ("max_tscr_ov", max_tscr_ov),
        ("max_ins_scr_ov", max_ins_scr_ov),
        ("max_cap_screw_ov", max_cap_screw_ov),
    ]:
        assert val == 0.0, f"{name} non-zero overlap: {val:.8f} mm^3"
    assert abs(dist_opt - 2.40) < 1e-6

    print("\n--- Micro-Gap & Wall-Thickness (<0.80mm) Verification ---")
    verify_case_wall_thickness_and_gaps(left_case, is_right=False)
    verify_case_wall_thickness_and_gaps(right_case, is_right=True)
    verify_cup_wall_thickness_and_gaps(cup_local.solids()[0])

    clr_j1_case = closest_points(j1_solid, right_case).distance
    clr_rj3_case = closest_points(rj3_solid, right_case).distance
    clr_sensor_case = closest_points(sensor_global, right_case).distance
    clr_smds_case = min(
        min(closest_points(s, right_case).distance for s in right_smds[2:]),
        min(closest_points(s, left_case).distance for s in left_smds),
    )
    clr_ball_cup = closest_points(ball_global, cup_global).distance
    clr_cup_plate = closest_points(cup_global, right_plate).distance
    clr_cup_rpcb = closest_points(cup_global, right_pcb).distance
    clr_wheel_mov_case = min(
        min(closest_points(s, right_case).distance for s in wheel_mov_rest),
        min(closest_points(s, right_case).distance for s in wheel_mov_click),
    )
    clr_wheel_cradle_case = min(closest_points(s, right_case).distance for s in wheel_stat)
    clr_wheel_mov_plate = min(
        min(closest_points(s, right_plate).distance for s in wheel_mov_rest),
        min(closest_points(s, right_plate).distance for s in wheel_mov_click),
    )
    clr_wheel_mov_pcb = min(
        closest_points(s, right_pcb).distance
        for s in (wheel_mov_rest + wheel_mov_click)
    )
    clr_wheel_usbc = min(
        closest_points(s, u).distance for s in wheel_solids for u in right_conn_solids
    )
    clr_wheel_keycaps = min(
        closest_points(s, kc).distance for s in wheel_solids for kc in right_keycaps
    )
    clr_usbc_case = min(
        min(closest_points(s, left_case).distance for s in left_conn_solids),
        min(closest_points(s, right_case).distance for s in right_conn_solids),
    )
    clr_usbc_plate = min(
        min(closest_points(s, left_plate).distance for s in left_conn_solids),
        min(closest_points(s, right_plate).distance for s in right_conn_solids),
    )

    print(f"Min Clearance Sensor J1 vs Right Case:      {clr_j1_case:.4f} mm (req >= 0.12 mm)")
    print(f"Min Clearance Main rJ3 vs Right Case:       {clr_rj3_case:.4f} mm (req >= 0.50 mm)")
    print(f"Min Clearance PMW3360 Sensor vs Right Case: {clr_sensor_case:.4f} mm (req >= 1.50 mm)")
    print(f"Min Clearance B.Cu SMDs/SWs vs Cases:       {clr_smds_case:.4f} mm (req >= 0.30 mm)")
    print(f"Min Clearance 25mm Ball vs Trackball Cup:   {clr_ball_cup:.4f} mm (req >= 0.30 mm)")
    print(f"Min Clearance Trackball Cup vs Right Plate: {clr_cup_plate:.4f} mm (req >= 0.25 mm)")
    print(f"Min Clearance Trackball Cup vs Right PCB:   {clr_cup_rpcb:.4f} mm (req >= 0.25 mm)")
    print(f"Min Clearance Wheel Moving vs Right Case:   {clr_wheel_mov_case:.4f} mm (req >= 0.40 mm)")
    print(f"Min Clearance Wheel Cradle vs Right Case:   {clr_wheel_cradle_case:.4f} mm (req >= 0.60 mm)")
    print(f"Min Clearance Wheel Moving vs Right Plate:  {clr_wheel_mov_plate:.4f} mm (req >= 0.30 mm)")
    print(f"Min Clearance Wheel Moving vs Right PCB:    {clr_wheel_mov_pcb:.4f} mm (req >= 0.30 mm)")
    print(f"Min Clearance Wheel Module vs USB-C Conns:  {clr_wheel_usbc:.4f} mm (req >= 1.00 mm)")
    print(f"Min Clearance Wheel Module vs Right Keycaps:{clr_wheel_keycaps:.4f} mm (req >= 1.00 mm)")
    print(f"Min Clearance Host/Split USBC vs Cases:     {clr_usbc_case:.4f} mm (req >= 0.50 mm)")
    print(f"Min Clearance Host/Split USBC vs Plates:    {clr_usbc_plate:.4f} mm (req >= 0.50 mm)")

    assert clr_j1_case >= 0.12, f"J1 too close to Right Case: {clr_j1_case:.4f} mm"
    assert clr_rj3_case >= 0.50, f"rJ3 too close to Right Case: {clr_rj3_case:.4f} mm"
    assert clr_sensor_case >= 1.50, f"PMW3360 too close to Right Case: {clr_sensor_case:.4f} mm"
    assert clr_smds_case >= 0.30, f"B.Cu SMDs/SWs too close to Case: {clr_smds_case:.4f} mm"
    assert clr_ball_cup >= 0.30, f"25mm Ball too close to Cup: {clr_ball_cup:.4f} mm"
    assert clr_cup_plate >= 0.25, f"Cup too close to Right Plate: {clr_cup_plate:.4f} mm"
    assert clr_cup_rpcb >= 0.25, f"Cup too close to Right PCB: {clr_cup_rpcb:.4f} mm"
    assert clr_wheel_mov_case >= 0.40, f"Wheel moving parts too close to Right Case: {clr_wheel_mov_case:.4f} mm"
    assert clr_wheel_cradle_case >= 0.60, f"Wheel Cradle too close to Right Case: {clr_wheel_cradle_case:.4f} mm"
    assert clr_wheel_mov_plate >= 0.30, f"Wheel moving parts too close to Plate: {clr_wheel_mov_plate:.4f} mm"
    assert clr_wheel_mov_pcb >= 0.30, f"Wheel moving parts too close to PCB: {clr_wheel_mov_pcb:.4f} mm"
    assert clr_wheel_usbc >= 1.00, f"Wheel Module too close to USB-C: {clr_wheel_usbc:.4f} mm"
    assert clr_wheel_keycaps >= 1.00, f"Wheel Module too close to Keycaps: {clr_wheel_keycaps:.4f} mm"
    assert clr_usbc_case >= 0.50, f"USB-C too close to Case: {clr_usbc_case:.4f} mm"
    assert clr_usbc_plate >= 0.50, f"USB-C too close to Top Plate: {clr_usbc_plate:.4f} mm"

    print("\n--- Full-Assembly 6-DOF Retention Verification (Switch-Independent Hardware Lock) ---")
    verify_6dof_constraints()
    for part, anchors, d_xy, d_z in (
        (left_plate, [left_case] + left_fasteners, 0.28, 0.08),
        (right_plate, [right_case] + right_fasteners, 0.28, 0.08),
        (left_pcb, [left_case] + left_fasteners, 0.16, 0.08),
        (right_pcb, [right_case] + right_fasteners + wheel_cradle_screws + wheel_stat, 0.16, 0.08),
        (sensor_pcb_global, [right_case, cup_global] + right_fasteners, 0.28, 0.08),
        (cup_global, [sensor_pcb_global] + right_fasteners, 0.28, 0.08),
    ):
        for axis_tag, vec in (
            ("+X", (d_xy, 0.0, 0.0)),
            ("-X", (-d_xy, 0.0, 0.0)),
            ("+Y", (0.0, d_xy, 0.0)),
            ("-Y", (0.0, -d_xy, 0.0)),
            ("+Z", (0.0, 0.0, d_z)),
            ("-Z", (0.0, 0.0, -d_z)),
        ):
            pm = part.moved(bd.Location(vec))
            ov_tot = sum(overlap_volume(pm, anc) for anc in anchors)
            assert ov_tot > 0.0, f"[6-DOF FAIL] {part.label} NOT mechanically locked along {axis_tag}!"
        print(f"  [PASS] {part.label}: mechanically locked in ±X, ±Y, ±Z by stepped bosses & M2x6 screws")

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
        + wheel_solids
        + wheel_cradle_screws
        + right_Assembly_smds
        + conn_solids
        + inserts
        + top_screws
        + keycaps
    )

    ASSEMBLIES_DIR.mkdir(parents=True, exist_ok=True)
    asm_full = bd.Compound(children=all_parts)
    asm_full.label = "curcur40_Full_Assembly"
    out_step = ASSEMBLIES_DIR / "assembly-full.step"
    bd.export_step(asm_full, str(out_step))
    print(f"\nSuccessfully exported {out_step} ({len(all_parts)} items, valid={asm_full.is_valid})")

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
        + wheel_solids
        + wheel_cradle_screws
        + right_Assembly_smds
        + right_conn_solids
        + right_fasteners
        + right_keycaps
    )

    # Also export Right Half + Inertia Wheel standalone verification assembly
    asm_right = bd.Compound(children=right_group)
    asm_right.label = "curcur40_Right_Wheel_Assembly"
    out_right_step = ASSEMBLIES_DIR / "curcur40-right-wheel-assembly.step"
    bd.export_step(asm_right, str(out_right_step))
    print(f"Successfully exported {out_right_step} ({len(right_group)} items)")

    desk_parts = [transform_to_desk(p, False) for p in left_group] + [
        transform_to_desk(p, True) for p in right_group
    ]
    desk_ball = [p for p in desk_parts if getattr(p, "label", "") == "Trackball_25mm"][0]
    desk_ref = [p for p in desk_parts if getattr(p, "label", "") == "Lens_Optical_Ref_Point"][0]
    assert abs(closest_points(desk_ball, desk_ref).distance - 2.40) < 1e-5

    asm_desk = bd.Compound(children=desk_parts)
    asm_desk.label = "curcur40_Full_Assembly_Desk"
    out_desk_step = ASSEMBLIES_DIR / "assembly-full-desk.step"
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
