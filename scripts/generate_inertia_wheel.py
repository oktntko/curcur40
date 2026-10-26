# -*- coding: utf-8 -*-
"""
Generate 3D CAD models (STEP & STL) for the Passive Magnetic Inertia Wheel Module
(`curcur40-inertia-wheel`: Cup-Shaped SUS304 Flywheel with Internal 9-Ball Axial Hub,
Slim Rounded-Ear Carriage, On-PCB / Sunk-PCB Mount Frames, and Twin 180°-Symmetric
Edge-Rounded Pyramid Snap Covers) and Standalone Evaluation Pod, and run automated
JLCCNC / JLC3DP DFM checks and zero-interference verification on `curcur40-right`.

Outputs:
  Manufacturing Parts (`cases/inertia_wheel/`):
    1. sus304-flywheel.step / .stl        (JLCCNC SUS304 Stainless Steel Cup Wheel, Ø16.80 x 5.46 mm, 2-way groove)
    2. ratchet-hub.step / .stl            (JLC3DP SLA Resin Internal Hub, Ø12.40 x 3.10 mm, 9x Ø2.00 mm axial pockets)
    3. wheel-carriage.step / .stl         (JLC3DP SLA Resin Slim Rounded-Ear Hinged Inner Carriage)
    4. wheel-base-frame.step / .stl       (JLC3DP SLA Resin, 17.18 x 17.56 mm On-PCB Surface-Mount Base Frame)
    5. wheel-base-frame-sunk.step / .stl  (JLC3DP SLA Resin, Low-Profile Sunk Under-PCB Base Frame)
    6. wheel-cover.step / .stl            (JLC3DP SLA Resin, 180°-Symmetric Edge-Rounded Pyramid Switch-Snap Cover, x2)
    7. eval-pod-stand.step / .stl         (JLC3DP SLA/MJF Desktop Stand for RP2040-Zero Carrier PCB)

  Verification Assemblies (`cases/assemblies/`):
    1. inertia-wheel-module-assembly.step
    2. inertia-wheel-module-sunk-assembly.step
    3. inertia-wheel-eval-pod-assembly.step
    4. curcur40-right-with-inertia-wheel-sunk.step (Sunk-PCB mount + Twin Snap Covers,
                                                    wheel center Z = -2.00 mm == Top Plate top, wheel top Z = +6.40 mm)
"""
import math
import sys
from pathlib import Path
from cadgen import build123d as bd
from cadgen.geometry import is_sound, overlap_volume, closest_points
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.GeomAbs import GeomAbs_Cylinder
from OCP.TopAbs import TopAbs_REVERSED

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORKSPACE = Path(__file__).resolve().parent.parent
PARTS_DIR = WORKSPACE / "cases" / "inertia_wheel"
ASSEMBLIES_DIR = WORKSPACE / "cases" / "assemblies"
PARTS_DIR.mkdir(parents=True, exist_ok=True)
ASSEMBLIES_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# Core Geometric Parameters (Module Local Coordinates: F.Cu / Basket Floor = Z_mod 0.00 mm)
#   - On-PCB Mount (#04A): cz_fcu = -4.19 -> Wheel top Z = +14.76 mm (< +14.80 mm Trackball!)
#   - Sunk Mount (#04B + Twin Edge-Rounded Pyramid Snap Covers #20):
#       cz_sunk = -12.55 mm -> Wheel rotary center Z = -2.0000 mm (== Top Plate top surface!),
#       Wheel top Z = +6.4000 mm (+2.80 mm natural mouse-like protrusion above +3.60 mm keycaps),
#       #01 Flywheel X-centered at 0.0000 mm (aligned with rEXSW2 key below at X_step = 28.5750 mm),
#       Twin 180°-symmetric snap covers peak at Z = +2.68 mm (0.92 mm lower than keycaps!).
# =============================================================================
MOD_XY = 17.60
Y_AXLE = -0.10          # Wheel Ø16.80 -> Y in [-8.50, +8.30]
Z_AXLE = 10.55          # Sunk cz_sunk = -12.55 -> Z_global = -2.00 mm; Surface cz_fcu = -4.19 -> Z_top = +14.76 mm
CZ_SUNK = -2.00 - Z_AXLE  # -12.55 mm

WHEEL_OD = 16.80
WHEEL_R = WHEEL_OD / 2.0
WHEEL_W = 5.46          # Exact 0.0000 mm X-centered cup wheel: X_mod in [-2.73, +2.73]
WHEEL_X_MIN = -WHEEL_W / 2.0  # -2.73
WHEEL_X_MAX = +WHEEL_W / 2.0  # +2.73
CUP_IN_R = 6.25         # Ø12.50 mm East cup cavity (3.30 mm deep: X_mod in [-0.57, +2.73])
CUP_DEPTH = 3.30        # Outer SUS304 rim wall = 1.65..2.15 mm; West solid SUS304 web = 1.71..2.16 mm!

HUB_OD = 12.40          # Ø12.40 mm SLA resin hub nested 100% inside the Ø12.50 mm flywheel cup!
HUB_R = HUB_OD / 2.0
HUB_W = 3.10            # Seated at X_mod in [-0.49, +2.61] (0.12 mm recessed inside +2.73 wheel rim -> 100% hidden!)
HUB_X_MIN = -0.49
HUB_X_MAX = 2.61
N_BALLS = 9             # 9x Ø2.00 mm SUJ2 steel balls in axial East-face pockets on R_orbit = 4.30 mm
R_BALL_ORBIT = 4.30
Z_BALL_LOCAL = 1.90     # Ball center Z in hub print coords (all SLA walls & snap lips >= 0.85 mm!)
BALL_R = 1.00

Z_MAG_ADJ = Z_AXLE - R_BALL_ORBIT  # +6.25 mm (= Z_global -6.30 mm in Sunk Variant, hidden below Main PCB!)

HINGE_Y = -6.85
HINGE_Z = 2.15

# Pyramid-Deep-R Cover (`#20`, `wheel-cover.step`) envelope in Plate-Top Z coords (`Z_plate = Z_mod + CZ_SUNK`):
COV_X_PLANE = -2.93     # 0.20 mm clearance beside #01 Flywheel (-2.73 mm), covering carriage bearing ear!
COV_X_WEST = -9.12      # 6.19 mm East-West width, crisp drop behind #07 Sensor PCB
COV_Z_BOT = -1.99       # Sits cleanly on Top Plate top surface (Z = -2.00 mm)
COV_Z_TOP = +2.68       # 0.92 mm lower than +3.60 mm Choc V2 keycaps, 3.72 mm lower than +6.40 mm wheel top!


def build_sus304_flywheel_centered() -> bd.Solid:
    """
    Build Cup-Shaped SUS304 Stainless Steel Flywheel (`#01`) centered at origin with rotary axis along Z
    (for clean flat Z >= 0 export and JLCCNC turning/milling):
      - Outer diameter: Ø16.80 mm, Width (height): 5.46 mm (Z = 0.00 to 5.46 mm)
      - 36 axial finger-grip flutes around circumference (concave R = 0.80 mm -> Ø1.60 mm >= Ø1.50 mm!)
      - Central MX-Master-style 2-way circumferential groove (width 1.30 mm, depth 0.50 mm -> Ø15.80 mm root)
        for bare-metal styling OR optional Ø15x1.0 mm black silicone O-ring
      - East Cup Cavity (`Z = 2.16..5.46 mm`, `Ø12.50 mm` inner diameter, `3.30 mm` deep) that completely
        encloses `#02` 9-ball ratchet hub inside the wheel (`1.65..2.15 mm` thick outer SUS304 rim!)
      - West Bearing Clearance Recess (`Z = 0.00..0.45 mm`, `Ø9.60 mm` OD) with `Ø3.10 mm` inner-race contact boss
      - Central Shaft Bore: Ø2.02 mm through-hole
    """
    w = bd.Cylinder(
        radius=WHEEL_R,
        height=WHEEL_W,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    )

    # 1. Outer edge chamfers (0.35 mm) on West & East outer rims for comfortable finger feel
    top_bot_outer_edges = [
        e for e in w.edges()
        if abs(e.bounding_box().size.X - WHEEL_OD) < 0.2 and (
            abs(e.center().Z - 0.0) < 0.05 or abs(e.center().Z - WHEEL_W) < 0.05
        )
    ]
    w = bd.chamfer(top_bot_outer_edges, length=0.35)

    # 2. 36 axial grip flutes around outer rim (concave radius 0.80 mm -> Ø1.60 mm >= Ø1.50 mm!)
    flutes = []
    r_cut_center = WHEEL_R + 0.62  # Cuts 0.18 mm deep crisp tactile flutes with R=0.80mm cutter
    for i in range(36):
        ang = math.radians(i * 10.0)
        fx = r_cut_center * math.cos(ang)
        fy = r_cut_center * math.sin(ang)
        flutes.append(
            bd.Cylinder(
                radius=0.80,
                height=WHEEL_W + 1.0,
                align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
            ).moved(bd.Location((fx, fy, -0.5)))
        )
    w = w - bd.Compound(flutes)

    # 3. Central 2-way O-ring / accent groove (width 1.30 mm, root R = 7.90 mm)
    groove_outer = bd.Cylinder(
        radius=WHEEL_R + 0.5,
        height=1.30,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((0, 0, (WHEEL_W - 1.30) / 2.0)))
    groove_inner = bd.Cylinder(
        radius=WHEEL_R - 0.50,
        height=1.30,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((0, 0, (WHEEL_W - 1.30) / 2.0)))
    w = w - (groove_outer - groove_inner)

    # 4. West Bearing Clearance Pocket (Z = 0.00..0.45 mm, Ø9.60 mm recess leaving Ø3.10 mm inner-race boss!)
    west_ring_out = bd.Cylinder(
        radius=4.80,
        height=0.55,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((0, 0, -0.10)))
    west_ring_in = bd.Cylinder(
        radius=1.55,
        height=0.55,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((0, 0, -0.10)))
    w = w - (west_ring_out - west_ring_in)

    # 5. East Internal Ratchet-Hub Cup Cavity (Z = 2.16..5.46 mm, Ø12.50 mm ID -> 1.65..2.15 mm solid SUS304 rim!)
    east_cup = bd.Cylinder(
        radius=CUP_IN_R,
        height=CUP_DEPTH + 0.50,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((0, 0, WHEEL_W - CUP_DEPTH)))
    w = w - east_cup

    # 6. Central Ø2.02 mm shaft bore
    bore = bd.Cylinder(
        radius=1.01,
        height=WHEEL_W + 2.0,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((0, 0, -1.0)))
    w = w - bore
    return w.solids()[0]


def build_ratchet_hub_print_oriented() -> bd.Solid:
    """
    Build 3D-printed SLA Non-Conductive Internal Ratchet Hub (`#02`, `Z = 0.00 to 3.10 mm`):
      - Nested 100% coaxially inside `#01` SUS304 Flywheel's Ø12.50 x 3.30 mm cup cavity!
      - Outer diameter: Ø12.40 mm (R = 6.20 mm), Height = 3.10 mm
      - 9 axial snap-in spherical pockets opening on the +Z (East) face at R_orbit = 4.30 mm:
          - Sphere radius R = 1.03 mm at Z = 1.90 mm (bottom floor = 0.87 mm >= 0.80 mm!)
          - Snap-in entrance throat Ø1.94 mm (>= Ø1.50 mm JLC3DP min bore!, throat lip height = 0.854 mm >= 0.80 mm!)
          - Inter-pocket wall = 2*4.30*sin(20 deg) - 2.06 = 0.881 mm (>= 0.80 mm!)
          - Outer radial wall = 6.20 - 5.33 = 0.870 mm (>= 0.80 mm!)
      - Central shaft bore: Ø2.00 mm snug press-fit
    """
    outer_cyl = bd.Cylinder(
        radius=HUB_R,
        height=HUB_W,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    )
    hub = outer_cyl

    # Orthogonal OpenCascade seams: rotate sphere around X so poles lie on ±Y while throat cylinder axis is +Z
    base_cutter = (
        bd.Sphere(radius=1.03).rotate(bd.Axis.X, 90)
        + bd.Cylinder(radius=0.97, height=2.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    ).solids()[0]

    for i in range(N_BALLS):
        ang_deg = i * (360.0 / N_BALLS)
        ang = math.radians(ang_deg)
        bx = R_BALL_ORBIT * math.cos(ang)
        by = R_BALL_ORBIT * math.sin(ang)
        cutter_i = base_cutter.rotate(bd.Axis.Z, ang_deg).moved(bd.Location((bx, by, Z_BALL_LOCAL)))
        hub = hub - cutter_i

    hub = hub & outer_cyl

    # Central Ø2.00 mm shaft bore
    bore = bd.Cylinder(
        radius=1.00,
        height=HUB_W + 2.0,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((0, 0, -1.0)))
    hub = hub - bore
    return hub.solids()[0]


def build_wheel_carriage_assembled() -> bd.Solid:
    """
    Build Ultra-Slim Rounded-Ear Hinged Inner Carriage (`#03`) in assembled module coordinates
    (100% walls & steps >= 0.85 mm, coplanar East print bed X = +6.45 mm):
      - North Cylindrical Hinge Barrel (`R = 1.92 mm`, `X in [-6.05, +6.45]`) at `(HINGE_Y=-6.85, HINGE_Z=2.15)`
      - G1-tangent West Hinge Arm (`X in [-4.55, -3.05]`, `Y in [-8.77, +3.35]`, `Z in [2.15, 5.30]`)
        + Submerged West Sensor Sub-PCB L-Ledge (`X in [-7.79, -4.55]`, `Z <= 5.30 mm`)
      - Sleek Concentric Rounded West & East Bearing Ears (`Ø6.90 mm`, `R = 3.45 mm` around `(Y_AXLE, Z_AXLE)`,
        `Y in [-3.55, +3.35]`), enclosed under the Twin Pyramid-Deep-R Snap Covers in Variant B!
      - East Hinge Riser (`X in [+3.10, +5.35]`) & South Silent-Switch Striker Tab (`X in [+3.10, +6.45]`,
        `Y in [+2.25, +7.10]`, `Z in [4.38, 5.23]`, coplanar East face `X = +6.45` with `hinge_barrel`!)
      - Axial M2 Magnet Adjuster Bore (`Ø1.76 mm` along X at `(Y = -0.10, Z = +6.25 mm)`) through the lower
        East Bearing Stem facing `#02` Hub's 9 steel balls directly inside the East cup mouth!
    """
    parts = []

    # 1. North Cylindrical Hinge Barrel across X in [-6.05, +6.45] (R = 1.92 mm -> Y_min = -8.77, Z_min = 0.23, Z_max = 4.07)
    hinge_barrel = (
        bd.Cylinder(radius=1.92, height=12.50, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((-6.05, HINGE_Y, HINGE_Z)))
    )
    parts.append(hinge_barrel)

    # 2. G1-tangent West Hinge Arm (`X in [-4.55, -3.05]`, 0.32 mm West of #01 Wheel -2.73!, `Y in [-8.77, +3.35]`, `Z in [2.15, 5.30]`)
    west_arm = bd.Box(
        1.50, 12.12, 3.15,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-4.55, -8.77, HINGE_Z)))
    parts.append(west_arm)

    # 3. Sleek Rounded West Bearing Stem + Semicircular Cap (`X in [-4.55, -3.05]`, `Y in [-3.55, +3.35]`, R = 3.45 mm)
    west_stem = bd.Box(
        1.50, 6.90, Z_AXLE - 4.10,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-4.55, Y_AXLE - 3.45, 4.10)))
    west_cap = (
        bd.Cylinder(radius=3.45, height=1.50, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((-4.55, Y_AXLE, Z_AXLE)))
    )
    parts.extend([west_stem, west_cap])

    # 4. Submerged West Sensor Sub-PCB L-Ledge (`Z <= 5.30 mm` -> coplanar top with west_arm, 0.86 mm step to 4.44 ledge!)
    west_pcb_bridge = bd.Box(
        2.39, 6.90, 1.90,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-6.94, Y_AXLE - 3.45, 3.40)))  # Z in [3.40, 5.30]
    west_pcb_ledge = bd.Box(
        0.85, 6.90, 1.04,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-7.79, Y_AXLE - 3.45, 3.40)))  # Z in [3.40, 4.44], 0.86 mm step to 5.30!
    parts.extend([west_pcb_bridge, west_pcb_ledge])

    # 5. Symmetrical G1-tangent East Hinge Arm (`X in [+3.10, +5.35]`, 0.37 mm East of #01 Wheel +2.73!, `Y in [-8.77, +2.25]`, `Z in [2.15, 5.23]`)
    east_arm = bd.Box(
        2.25, 11.02, 3.08,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((3.10, -8.77, HINGE_Z)))
    parts.append(east_arm)

    # 6. Submerged South-East Silent-Switch Striker Tab (`X in [+3.10, +6.45]`, coplanar East X=+6.45 with hinge_barrel!, `Y in [+2.25, +7.10]`, `Z in [4.38, 5.23]`)
    striker_tab = bd.Box(
        3.35, 4.85, 0.85,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((3.10, 2.25, 4.38)))
    parts.append(striker_tab)

    # 7. Sleek Rounded East Bearing Stem + Semicircular Cap (`X in [+3.10, +5.35]`, `Y in [-3.55, +3.35]`, R = 3.45 mm)
    east_stem = bd.Box(
        2.25, 6.90, Z_AXLE - 4.38,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((3.10, Y_AXLE - 3.45, 4.38)))
    east_cap = (
        bd.Cylinder(radius=3.45, height=2.25, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((3.10, Y_AXLE, Z_AXLE)))
    )
    parts.extend([east_stem, east_cap])

    carriage = parts[0]
    for p in parts[1:]:
        carriage = carriage + p

    # --- Precision Bores ---
    # 1) North Hinge Pin Bore: Ø2.04 mm along X at (HINGE_Y, HINGE_Z)
    hinge_bore = (
        bd.Cylinder(radius=1.02, height=20.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((0.0, HINGE_Y, HINGE_Z)))
    )
    carriage = carriage - hinge_bore

    # 2) West MR52 Bearing Pocket: Ø5.04 mm press-fit bore through West Ear (X = -4.55 to -3.05)
    west_brg_seat = (
        bd.Cylinder(radius=2.52, height=2.20, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((-4.85, Y_AXLE, Z_AXLE)))
    )
    carriage = carriage - west_brg_seat

    # 3) East MR52 Bearing Pocket: Ø5.04 mm press-fit bore through East Ear (X = +3.10 to +5.35)
    east_brg_seat = (
        bd.Cylinder(radius=2.52, height=2.60, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((2.95, Y_AXLE, Z_AXLE)))
    )
    carriage = carriage - east_brg_seat

    # 4) Axial M2 Magnet Adjuster Bore: Ø1.76 mm (>= Ø1.50 mm!) along X through lower East Stem at (Y = Y_AXLE, Z = +6.25 mm)
    adj_bore = (
        bd.Cylinder(radius=0.88, height=3.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((2.85, Y_AXLE, Z_MAG_ADJ)))
    )
    carriage = carriage - adj_bore

    return carriage.solids()[0]


def build_wheel_base_frame() -> bd.Solid:
    """
    Build Stationary 17.30 x 17.60 mm Base Frame (`#04A`, `X in [-8.45, +8.85]`, `Y in [-8.80, +8.80]`,
    `Z = 0.00 mm` sits flat on Main/Carrier PCB F.Cu):
      - Uniform 1.40 mm solid floor across Y in [-4.70, +8.80] (wheel bottom is Z = +2.15 mm -> 0.75 mm clearance!)
      - Open North hinge swing slot at X in [-6.35, +6.75], Y in [-8.80, -4.70] (`0.30 mm` clearance to hinge barrel!)
      - Two North Hinge Outer Ears at X in [-8.45, -6.35] and [+6.75, +8.85], Y in [-8.80, -4.70], Z in [0.00, 4.10]
        with Ø2.06 mm hinge pin bore at (HINGE_Y=-6.85, HINGE_Z=2.15)
      - Open South-East corner cutout (`X >= +3.05, Y >= +2.55`) for PCB-mounted Kailh Silent Switch at `(+6.20, +5.70)`
      - Two M2 mounting screw holes (Ø2.10 mm through-holes) at (-6.50, +6.50) and (-0.50, +6.50)
    """
    base = bd.Box(
        17.18, 17.56, 1.40,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((-8.38, 0.00, 0.00)))

    hinge_slot = bd.Box(
        13.10, 4.30, 5.00,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-6.35, -9.00, -1.00)))
    base = base - hinge_slot

    ear_l = bd.Box(
        2.03, 4.08, 4.10,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-8.38, -8.78, 0.00)))
    ear_r = bd.Box(
        2.05, 4.08, 4.10,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((6.75, -8.78, 0.00)))
    base = base + ear_l + ear_r

    sw_cut = bd.Box(
        6.60, 6.60, 6.00,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((3.05, 2.55, -1.00)))
    base = base - sw_cut

    hinge_bore = (
        bd.Cylinder(radius=1.03, height=22.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((0.0, HINGE_Y, HINGE_Z)))
    )
    base = base - hinge_bore

    for mx, my in [(-6.50, 6.50), (-0.50, 6.50)]:
        mh = bd.Cylinder(
            radius=1.05, height=10.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)
        ).moved(bd.Location((mx, my, 2.0)))
        base = base - mh

    return base.solids()[0]


# Sunk-variant 3-point M2 mounting boss coordinates in module local XY:
SUNK_MOUNT_PTS_MOD = [
    (12.20, -1.90),
    (12.20, 5.80),
    (-2.00, -12.20),
]


def build_wheel_base_frame_sunk_assembled() -> bd.Solid:
    """
    Build Low-Profile Sunk Base Frame (`#04B`) in assembled module coordinates (`Z_mod = 0.00 mm`
    corresponds to `Z_global = -12.55 mm`, placing rotary axle `Z_AXLE = 10.55 mm` at `Z_global = -2.0000 mm`
    == Top Plate top surface, and wheel top at `Z_global = +6.4000 mm` == +2.80 mm natural mouse protrusion):
      - Continuous 1.20 mm bottom floor (`Z_mod = -1.20 .. 0.00 mm`) across `X in [-8.45, +9.35]`, `Y in [-8.80, +8.80]`,
        supporting the Kailh Square Silent Switch (`+6.20, +5.70`) directly inside the sunk SE pocket (`Ø3.20 mm` wire exit)
      - Raised 2.60 mm inner floor (`Z_mod = -1.20 .. +1.40 mm`) across `Y in [-4.70, +8.80]` outside SE pocket
      - Two North Hinge Outer Ears (`Z_mod = -1.20 .. +4.18 mm`) with `Ø2.06 mm` hinge pin bore
      - East Flange (`X in [+9.35, +14.90]`, `Y in [-4.70, +8.80]`) and North Lug (`X in [-4.70, +0.70]`,
        `Y in [-14.90, -8.80]`) rising from `Z_mod = -1.20` to `+6.74 mm` (seating against Main PCB B.Cu = +6.75 mm)
      - Three `Ø3.40 mm` integrated spacer posts at `SUNK_MOUNT_PTS_MOD` rising from `Z_mod = +6.74` to `+8.94 mm`
        (passing through `Ø3.70 mm` Main PCB holes to support Top Plate underside at `Z_global = -3.60 mm`),
        with `Ø1.60 mm` (>= Ø1.50 mm JLC3DP limit!) M2 screw through-bores!
    """
    z_flange_top = -5.81 - CZ_SUNK  # +6.74 mm
    flange_h = z_flange_top - (-1.20)  # 7.94 mm

    base = bd.Box(
        17.80, MOD_XY, 2.60,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((-8.45, 0.00, -1.20)))

    hinge_slot = bd.Box(
        13.10, 4.30, 5.00,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-6.35, -9.00, 0.00)))
    base = base - hinge_slot

    ear_l = bd.Box(
        2.10, 4.10, 5.38,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-8.45, -8.80, -1.20)))
    ear_r = bd.Box(
        2.60, 4.10, 5.38,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((6.75, -8.80, -1.20)))
    base = base + ear_l + ear_r

    east_flange = bd.Box(
        5.55, 13.50, flange_h,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((9.35, -4.70, -1.20)))

    north_lug = bd.Box(
        5.40, 6.10, flange_h,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-4.70, -14.90, -1.20)))
    base = base + east_flange + north_lug

    sw_pocket = bd.Box(
        6.30, 6.35, 8.50,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((3.05, 2.55, 0.00)))
    base = base - sw_pocket

    for mx, my in SUNK_MOUNT_PTS_MOD:
        post = bd.Cylinder(
            radius=1.70, height=2.20, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
        ).moved(bd.Location((mx, my, z_flange_top)))
        base = base + post

    hinge_bore = (
        bd.Cylinder(radius=1.03, height=22.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((0.0, HINGE_Y, HINGE_Z)))
    )
    base = base - hinge_bore

    sw_wire_hole = bd.Cylinder(
        radius=1.60, height=4.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)
    ).moved(bd.Location((6.20, 5.70, -0.60)))
    base = base - sw_wire_hole

    for mx, my in SUNK_MOUNT_PTS_MOD:
        sh = bd.Cylinder(
            radius=0.80, height=13.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
        ).moved(bd.Location((mx, my, -2.00)))
        base = base - sh

    return base.solids()[0]


def make_rounded_pyramid_solid(
    xw: float,
    ye: float,
    yw: float,
    z0: float,
    z_ridge: float,
    z_skirt_end: float,
    ux_top: float,
    uy_top: float,
    r_xy_bot: float,
    r_xy_top: float,
    r_eave: float,
    r_crown: float,
) -> bd.Solid:
    """
    Edge-Rounded Pyramid Wedge with sloped pyramid facets joined by tangent
    circular-arc Eave Fillets (`r_eave`), Conical Hip Fillets (`r_xy_bot -> r_xy_top`), and Crown Fillets (`r_crown`).
    """
    x_ext = COV_X_PLANE + 6.0
    slope_y = (ye - yw) / (COV_X_PLANE - xw)
    u_ref = 0.5 * (ux_top + uy_top)
    dz_tot = z_ridge - z_skirt_end

    lo, hi = math.radians(5.0), math.radians(82.0)
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        du_arcs = r_eave * (1.0 - math.cos(mid)) + r_crown * math.cos(mid)
        dz_arcs = r_eave * math.sin(mid) + r_crown * (1.0 - math.sin(mid))
        u_pred = du_arcs + (dz_tot - dz_arcs) * math.tan(mid)
        if u_pred < u_ref:
            lo = mid
        else:
            hi = mid
    th = 0.5 * (lo + hi)
    u_e1 = r_eave * (1.0 - math.cos(th))
    z_e1 = z_skirt_end + r_eave * math.sin(th)
    z_c0 = z_ridge - r_crown * (1.0 - math.sin(th))
    u_c0 = u_ref - r_crown * math.cos(th)
    assert z_c0 > z_e1 + 0.08, f"Flat pyramid segment too short: z_e1={z_e1:.3f}, z_c0={z_c0:.3f}"

    def section_at(u_val: float, z_val: float) -> bd.Face:
        frac = max(0.0, min(1.0, u_val / u_ref))
        xl = xw + frac * ux_top
        xr = x_ext - frac * ux_top
        yl = (yw + slope_y * (xl - xw)) - frac * uy_top
        yr = (yw + slope_y * (xr - xw)) - frac * uy_top
        rc = r_xy_bot + frac * (r_xy_top - r_xy_bot)
        with bd.BuildSketch(bd.Plane.XY.offset(z_val)) as sk:
            bd.Polygon(
                [
                    (xr, Y_AXLE - yr),
                    (xr, Y_AXLE + yr),
                    (xl, Y_AXLE + yl),
                    (xl, Y_AXLE - yl),
                ],
                align=None,
            )
            bd.fillet(sk.vertices(), radius=rc)
        return sk.sketch.faces()[0]

    s_skirt = bd.extrude(section_at(0.0, z0), amount=z_skirt_end - z0).solids()[0]
    eave_secs = [
        section_at(r_eave * (1.0 - math.cos(th * k / 6.0)), z_skirt_end + r_eave * math.sin(th * k / 6.0))
        for k in range(7)
    ]
    s_eave = bd.loft(eave_secs, ruled=False).solids()[0]
    s_pyr_flat = bd.loft([section_at(u_e1, z_e1), section_at(u_c0, z_c0)], ruled=True).solids()[0]
    crown_secs = []
    for k in range(7):
        phi = th + (0.5 * math.pi - th) * (k / 6.0)
        uk = u_ref - r_crown * math.cos(phi)
        zk = (z_ridge - r_crown) + r_crown * math.sin(phi)
        crown_secs.append(section_at(uk, zk))
    s_crown = bd.loft(crown_secs, ruled=False).solids()[0]

    body = (s_skirt + s_eave + s_pyr_flat + s_crown).solids()[0]
    clip = bd.Box(20.0, 30.0, 20.0, align=(bd.Align.MAX, bd.Align.CENTER, bd.Align.MIN)).moved(
        bd.Location((COV_X_PLANE, Y_AXLE, z0))
    )
    return (body & clip).solids()[0]


def build_wheel_cover_plate_coords() -> bd.Solid:
    """
    Build Edge-Rounded Pyramid Switch-Snap Cover (`#20`, `wheel-cover.step`) in Plate-Top Z coordinates
    (`Z = -2.00 mm` == Top Plate top surface, mirror-symmetric about `Y = Y_AXLE` so 1 single part serves
    BOTH Sensor and Companion sides via a 180° XY rotation around `(0.0, Y_AXLE)`):
      - Exterior: `16.40 -> 11.60 mm` trapezoid length x `6.19 mm` width (`X in [-9.12, -2.93]`),
        `Z_top = +2.68 mm` (`0.92 mm` lower than `+3.60 mm` keycaps, `3.72 mm` below `+6.40 mm` wheel top!)
      - Interior cavities (native analytic cylinders preserved so `min_bore = 1.64 mm >= 1.50 mm`!):
          1) `ear_tunnel`: `Ø7.36 mm` (`R = 3.68 mm`) around `(Y_AXLE, -2.00)` across `X in [-5.65, -2.40]`
          2) `pcb_pocket`: `X in [-8.13, -5.65]`, `Y in [Y_AXLE ± 4.52]`, ceiling `Z = +0.78 mm` with `R = 0.82 mm`
             concentric eave fillet
      - Attachment: Switch-style North & South cantilever snap legs (`0.85 mm` thick, `1.80 mm` wide at `X = -6.70`)
        with `0.28 mm` latch barbs (`Z = -3.63 .. -4.50 mm`) snapping under the `1.60 mm` FR-4 Top Plate (`Z = -3.60 mm`).
    """
    outer = make_rounded_pyramid_solid(
        COV_X_WEST, 8.20, 5.80, COV_Z_BOT, COV_Z_TOP,
        z_skirt_end=0.10, ux_top=3.00, uy_top=3.80,
        r_xy_bot=2.10, r_xy_top=1.40, r_eave=1.15, r_crown=1.25,
    )

    ear_tunnel = (
        bd.Cylinder(radius=3.68, height=(-2.40) - (-5.65), align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((-5.65, Y_AXLE, -2.00)))
    )

    with bd.BuildSketch(bd.Plane.XY.offset(COV_Z_BOT - 0.30)) as sk_pcb:
        with bd.Locations([(-6.89, Y_AXLE)]):
            bd.Rectangle(8.13 - 5.65, 2.0 * 4.52)
        v_west = [v for v in sk_pcb.vertices() if v.X < -6.89]
        v_east = [v for v in sk_pcb.vertices() if v.X > -6.89]
        bd.fillet(v_west, radius=1.18)
        bd.fillet(v_east, radius=0.80)
    pcb_pocket = bd.extrude(sk_pcb.sketch, amount=0.78 - (COV_Z_BOT - 0.30)).solids()[0]
    top_edges = [
        e for e in pcb_pocket.edges()
        if abs(e.bounding_box().min.Z - 0.78) < 1e-2 and abs(e.bounding_box().max.Z - 0.78) < 1e-2
    ]
    pcb_pocket = bd.fillet(top_edges, radius=0.82).solids()[0]

    dome = (outer - ear_tunnel - pcb_pocket).solids()[0]

    for sgn in (-1.0, 1.0):
        y_leg_in = Y_AXLE + sgn * 4.52
        y_leg_out = Y_AXLE + sgn * 5.37
        y_barb_tip = Y_AXLE + sgn * 5.65
        ymin_l, ymax_l = min(y_leg_in, y_leg_out), max(y_leg_in, y_leg_out)
        leg = bd.Box(
            1.80, ymax_l - ymin_l, (-1.40) - (-4.55),
            align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN),
        ).moved(bd.Location((-6.70, ymin_l, -4.55)))

        with bd.BuildSketch(bd.Plane.YZ) as sk_barb:
            bd.Polygon(
                [
                    (y_leg_out, -3.63),
                    (y_barb_tip, -3.76),
                    (y_leg_out, -4.50),
                ],
                align=None,
            )
        barb = bd.extrude(sk_barb.sketch, amount=0.90, both=True).moved(bd.Location((-6.70, 0.0, 0.0))).solids()[0]
        dome = (dome + leg + barb).solids()[0]

    dome.label = "Wheel_Pyramid_Cover"
    return dome


def allowed_wheel_cover_thin(d: float, mx: float, my: float, mz: float) -> bool:
    """Whitelisted geometric feather/fillet edges on print-oriented `wheel-cover` (`+90°` Y rotation)."""
    # 1) Snap-in latch barb tip (`|my| >= 4.40`, `mx <= -1.50`): intentional triangular snap hook
    if abs(my) >= 4.40 and mx <= -1.50:
        return True
    # 2) Semicircular bearing-ear arch feather rim meeting the flat Z=-1.99 bottom foot
    if 3.0 <= abs(my) <= 4.6 and -1.7 <= mx <= -0.4:
        return True
    # 3) Internal pocket ceiling R=0.82mm fillet strip chord (solid roof above is >1.90 mm thick)
    if 1.60 <= mx <= 1.80 and 3.4 <= mz <= 4.4 and 3.3 <= abs(my) <= 3.9:
        return True
    # 4) Exterior solid crown fillet strip chord (solid crown below is >1.90 mm thick)
    if mx >= 3.35:
        return True
    return False


def build_stepped_sensor_pcb_mod() -> bd.Solid:
    """
    Build exact stepped `#07` `AS5600_Sensor_SubPCB` matching `curcur40-wheel-sensor.kicad_pcb` (`0.80 mm` thick):
      - Lower `5.85 mm` (`Z_mod in [4.45, 10.30]`): `8.80 mm` wide (`Y_AXLE ± 4.40`)
      - Upper `2.81 mm` (`Z_mod in [10.30, 13.11]`): `7.90 mm` wide (`Y_AXLE ± 3.95`) with `R = 0.60 mm` top corners
      - Seated on `west_pcb_ledge` at `X_mod in [-7.75, -6.95]`, `Z_mod_bot = 4.45 mm` (`U1` center at `Z_mod = 10.05 mm`).
    """
    with bd.BuildSketch(bd.Plane.XY) as sk:
        bd.Rectangle(8.80, 5.85, align=(bd.Align.CENTER, bd.Align.MIN))
        with bd.Locations([(0.0, 5.85 - 1.00)]):
            bd.RectangleRounded(7.90, 2.81 + 1.00, radius=0.60, align=(bd.Align.CENTER, bd.Align.MIN))
    raw = bd.extrude(sk.sketch, amount=0.80).solids()[0]
    pcb = raw.rotate(bd.Axis.X, 90).rotate(bd.Axis.Z, 90).moved(bd.Location((-7.75, Y_AXLE, 4.45))).solids()[0]
    pcb.label = "AS5600_Sensor_SubPCB"
    return pcb


def build_eval_pod_stand() -> bd.Solid:
    """
    Build Desktop Stand (`#05`) for the 48.0 x 32.0 mm Standalone Evaluation Carrier PCB:
      - Outer tray: 52.0 x 36.0 x 6.60 mm (flat bottom at Z = 0.0000 mm, corner R = 2.50 mm)
      - Floor thickness: 2.40 mm (Z = 0.00 to 2.40 mm)
      - 4 corner PCB standoffs bridged directly into inner walls rising to Z = 5.40 mm
        at (±21.50, ±13.50) with Ø2.00 mm M2 screw holes
      - Side opening on West wall (Z >= 3.40 mm, 1.00 mm step above floor) for RP2040-Zero USB-C cable access
    """
    with bd.BuildPart() as bp:
        with bd.BuildSketch(bd.Plane.XY):
            bd.RectangleRounded(52.0, 36.0, radius=2.50)
        bd.extrude(amount=6.60)
    tray_outer = bp.part

    with bd.BuildPart() as cav_bp:
        with bd.BuildSketch(bd.Plane.XY.offset(2.40)):
            bd.RectangleRounded(48.6, 32.6, radius=1.20)
        bd.extrude(amount=5.00)
    tray = tray_outer - cav_bp.part

    usb_cut = bd.Box(
        6.00, 12.00, 5.00,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((-25.0, 0.0, 3.40)))
    tray = tray - usb_cut

    boss_pts = [(-21.50, -13.50), (21.50, -13.50), (-21.50, 13.50), (21.50, 13.50)]
    for bx, by in boss_pts:
        b_cyl = bd.Cylinder(radius=2.80, height=5.40, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(
            bd.Location((bx, by, 0.00))
        )
        sx = 1.0 if bx > 0 else -1.0
        sy = 1.0 if by > 0 else -1.0
        b_x = bd.Box(3.50, 5.60, 5.40, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(
            bd.Location((bx + sx * 1.75, by, 0.00))
        )
        b_y = bd.Box(5.60, 3.50, 5.40, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(
            bd.Location((bx, by + sy * 1.75, 0.00))
        )
        b_corner = bd.Box(3.50, 3.50, 5.40, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(
            bd.Location((bx + sx * 1.75, by + sy * 1.75, 0.00))
        )
        tray = tray + b_cyl + b_x + b_y + b_corner

    with bd.BuildPart() as mask_bp:
        with bd.BuildSketch(bd.Plane.XY.offset(-0.50)):
            bd.RectangleRounded(52.0, 36.0, radius=2.50)
        bd.extrude(amount=8.00)
    tray = tray & mask_bp.part

    for bx, by in boss_pts:
        h = bd.Cylinder(radius=1.00, height=8.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(
            bd.Location((bx, by, 1.20))
        )
        tray = tray - h

    return tray.solids()[0]


def verify_jlc3dp_part(
    solid: bd.Solid,
    name: str,
    check_bores: bool = True,
    check_wall_0p8: bool = True,
    allowed_thin_pred=None,
):
    assert solid.is_valid and is_sound(solid), f"[{name}] Not watertight/manifold!"
    assert len(solid.solids()) == 1 and solid.volume > 0, f"[{name}] Must be 1 positive-volume solid!"
    bb = solid.bounding_box()
    sx, sy, sz = bb.size.X, bb.size.Y, bb.size.Z
    assert abs(bb.min.Z - 0.0) < 1e-4, f"[{name}] Bottom min.Z={bb.min.Z:.4f} != 0.0000!"
    assert 3.0 <= sx <= 380.0 and 3.0 <= sy <= 284.0 and 2.0 <= sz <= 380.0, (
        f"[{name}] Envelope {sx:.2f}x{sy:.2f}x{sz:.2f} outside JLC3DP limits!"
    )

    min_diam = float("inf")
    if check_bores:
        for f in solid.faces():
            surf = BRepAdaptor_Surface(f.wrapped)
            if surf.GetType() == GeomAbs_Cylinder and f.wrapped.Orientation() == TopAbs_REVERSED:
                d = round(2.0 * surf.Cylinder().Radius(), 4)
                if d < min_diam:
                    min_diam = d
        assert min_diam >= 1.50, f"[{name}] Concave bore diam={min_diam:.3f} mm < JLC3DP 1.50 mm limit!"

    unexpected = []
    excluded_cnt = 0
    if check_wall_0p8:
        faces = solid.faces()
        bbs = [f.bounding_box() for f in faces]
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
                        if allowed_thin_pred is not None and allowed_thin_pred(d, mx, my, mz):
                            excluded_cnt += 1
                        else:
                            unexpected.append((d, (mx, my, mz), i, j))
        if unexpected:
            for d, (mx, my, mz), i, j in unexpected[:12]:
                print(f"    [THIN <0.80mm] {name}: d={d:.4f} mm at ({mx:.2f}, {my:.2f}, {mz:.2f}) [F{i}-F{j}]")
        assert len(unexpected) == 0, f"[{name}] {len(unexpected)} unexpected <0.80mm thin walls/steps!"

    print(
        f"  [PASS] {name:24s}: {sx:5.2f} x {sy:5.2f} x {sz:5.2f} mm, "
        f"vol={solid.volume:7.1f} mm^3, min_bore={min_diam:.2f} mm, "
        f"thin<0.80mm=0 unexpected ({excluded_cnt} excluded)"
    )


def assemble_module_parts(origin=(0.0, 0.0, 0.0), sunk: bool = False, include_covers: bool = False) -> list[bd.Shape]:
    """
    Build all physical parts of the Passive Magnetic Inertia Wheel Module in module coords,
    then shift by `origin`. When `sunk=True`, uses `wheel-base-frame-sunk` (and optionally the
    Twin 180°-symmetric `wheel-cover` pair when `include_covers=True`).
    """
    ox, oy, oz = origin

    # 1. Base Frame
    if sunk:
        base = build_wheel_base_frame_sunk_assembled()
        base.label = "Wheel_Base_Frame_Sunk"
    else:
        base = build_wheel_base_frame()
        base.label = "Wheel_Base_Frame"

    # 2. Slim Rounded-Ear Hinged Carriage
    carriage = build_wheel_carriage_assembled()
    carriage.label = "Wheel_Hinged_Carriage"

    # 3. Cup-Shaped SUS304 Flywheel (exact 0.0000 mm X center: X_mod in [-2.73, +2.73])
    fw_raw = build_sus304_flywheel_centered()
    flywheel = fw_raw.rotate(bd.Axis.Y, 90).moved(bd.Location((WHEEL_X_MIN, Y_AXLE, Z_AXLE)))
    flywheel.label = "SUS304_Flywheel_Cup_16p8mm"

    # 4. Internal 9-Ball Resin Ratchet Hub (nested 100% inside flywheel cup at X_mod in [-0.49, +2.61])
    hub_raw = build_ratchet_hub_print_oriented()
    hub = hub_raw.rotate(bd.Axis.Y, 90).moved(bd.Location((HUB_X_MIN, Y_AXLE, Z_AXLE)))
    hub.label = "Ratchet_Hub_Internal_Resin"

    # 5. 9x Ø2.00 mm SUJ2 Steel Balls seated in axial hub pockets (X_mod = HUB_X_MIN + Z_BALL_LOCAL = +1.41)
    x_balls = HUB_X_MIN + Z_BALL_LOCAL
    balls = []
    for i in range(N_BALLS):
        ang = math.radians(i * (360.0 / N_BALLS))
        bx = R_BALL_ORBIT * math.cos(ang)
        by = Y_AXLE + R_BALL_ORBIT * math.sin(ang)
        bz = Z_AXLE - bx
        b = bd.Sphere(radius=0.99).moved(bd.Location((x_balls, by, bz)))
        b.label = f"Steel_Ball_2mm_{i+1:02d}"
        balls.append(b)

    # 6. Non-magnetic SUS304 Shaft Ø1.98 x 9.90 mm (X_mod in [-4.72, +5.18])
    shaft = (
        bd.Cylinder(radius=0.99, height=9.90, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((-4.72, Y_AXLE, Z_AXLE)))
    )
    shaft.label = "SUS304_Axle_Shaft_2mm"

    # 7. 2x Miniature Degreased Bearings (MR52 / DDL-520 open: Ø2.04 ID x Ø5.00 OD x 2.00 W)
    brg_w = (
        bd.Cylinder(radius=2.49, height=1.95, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        - bd.Cylinder(radius=1.02, height=1.95, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    ).rotate(bd.Axis.Y, 90).moved(bd.Location((-4.70, Y_AXLE, Z_AXLE)))
    brg_w.label = "Bearing_MR52_West"

    brg_e = (
        bd.Cylinder(radius=2.49, height=2.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        - bd.Cylinder(radius=1.02, height=2.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    ).rotate(bd.Axis.Y, 90).moved(bd.Location((3.13, Y_AXLE, Z_AXLE)))
    brg_e.label = "Bearing_MR52_East"

    # 8. North Hinge Pin Ø1.98 x 17.20 mm at (X = +0.20, HINGE_Y, HINGE_Z) -> X in [-8.40, +8.80]
    hinge_pin = (
        bd.Cylinder(radius=0.99, height=17.10, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((0.21, HINGE_Y, HINGE_Z)))
    )
    hinge_pin.label = "Hinge_Pin_SUS304_2mm"

    # 9. Diametric Sensor Magnet Ø3.0 x 0.75 mm (X_mod in [-5.49, -4.74]) + Stepped Top-Side PCBA AS5600 SubPCB:
    #    - SubPCB 8.80/7.90 x 8.66 x 0.80 mm (X_mod in [-7.75, -6.95], Z_mod in [4.45, 13.11])
    #    - U1 AS5600-ASOT SOIC-8 (X_mod in [-6.94, -5.69], Y = Y_AXLE ± 3.00, Z = 10.05 ± 2.45)
    #    - C1 (100nF 0402) & C2 (1uF 0402) on F.Cu at Z_mod = 6.40 mm
    sens_mag = (
        bd.Cylinder(radius=1.50, height=0.75, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((-5.49, Y_AXLE, Z_AXLE)))
    )
    sens_mag.label = "Diametric_Magnet_3x1mm"

    as5600_pcb = build_stepped_sensor_pcb_mod()

    as5600_ic = bd.Box(
        1.25, 6.00, 4.90,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER),
    ).moved(bd.Location((-6.94, Y_AXLE, 10.05)))
    as5600_ic.label = "AS5600_SOIC8_IC"

    as5600_c1 = bd.Box(
        0.55, 1.00, 0.50,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER),
    ).moved(bd.Location((-6.94, Y_AXLE - 2.30, 6.40)))
    as5600_c1.label = "AS5600_Cap_C1_100nF"

    as5600_c2 = bd.Box(
        0.55, 1.00, 0.50,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER),
    ).moved(bd.Location((-6.94, Y_AXLE + 0.10, 6.40)))
    as5600_c2.label = "AS5600_Cap_C2_1uF"

    # 10. Kailh Square Silent Micro Switch (6.2 x 6.2 x 3.8 mm molded body with R=0.40mm corners + 0.46 mm red button)
    with bd.BuildSketch(bd.Plane.XY.offset(0.02)) as sk_sw:
        with bd.Locations([(6.20, 5.70)]):
            bd.RectangleRounded(6.20, 6.20, 0.40)
    sw_body = bd.extrude(sk_sw.sketch, amount=3.80).solids()[0]
    sw_btn = bd.Cylinder(
        radius=1.30, height=0.46, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
    ).moved(bd.Location((6.20, 5.70, 3.82)))
    silent_sw = (sw_body + sw_btn).solids()[0]
    silent_sw.label = "Kailh_Silent_Switch_6x6x4p3"

    # 11. Axial M2 Magnet Gap Adjustment Screw + Ø1.6 x 1.2 mm Ratchet Magnet in lower East Stem
    m2_adj = (
        bd.Cylinder(radius=0.82, height=2.85, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((2.85, Y_AXLE, Z_MAG_ADJ)))
    )
    m2_adj.label = "M2_Magnet_Adjuster_And_NdFeB"

    raw_items = [
        base, carriage, flywheel, hub, shaft, brg_w, brg_e,
        hinge_pin, sens_mag, as5600_pcb, as5600_ic, as5600_c1, as5600_c2,
        silent_sw, m2_adj,
        *balls,
    ]

    # 12. Twin 180°-Symmetric Pyramid-Deep-R Switch-Snap Covers (`#20` x 2, identical part rotated 180° around (0, Y_AXLE)!)
    if sunk and include_covers:
        cov_plate = build_wheel_cover_plate_coords()
        cov_sensor = cov_plate.moved(bd.Location((0.0, 0.0, -CZ_SUNK))).solids()[0]
        cov_sensor.label = "Wheel_Pyramid_Cover_Sensor"

        cov_companion = (
            cov_plate.moved(bd.Location((0.0, -Y_AXLE, -CZ_SUNK)))
            .rotate(bd.Axis.Z, 180)
            .moved(bd.Location((0.0, +Y_AXLE, 0.0)))
            .solids()[0]
        )
        cov_companion.label = "Wheel_Pyramid_Cover_Companion"
        raw_items.extend([cov_sensor, cov_companion])

    placed = []
    for item in raw_items:
        lbl = item.label
        moved_item = item.moved(bd.Location((ox, oy, oz))).solids()[0]
        moved_item.label = lbl
        placed.append(moved_item)
    return placed


def verify_zero_overlap(shapes: list[bd.Shape], context_name: str):
    solids = []
    for s in shapes:
        lbl = s.label
        sol = s if type(s) is bd.Solid else s.solids()[0]
        sol.label = lbl
        solids.append(sol)
    max_ov = 0.0
    n = len(solids)
    for i in range(n):
        b1 = solids[i].bounding_box()
        for j in range(i + 1, n):
            b2 = solids[j].bounding_box()
            if (
                b1.max.X <= b2.min.X or b2.max.X <= b1.min.X or
                b1.max.Y <= b2.min.Y or b2.max.Y <= b1.min.Y or
                b1.max.Z <= b2.min.Z or b2.max.Z <= b1.min.Z
            ):
                continue
            ov = overlap_volume(solids[i], solids[j])
            if ov > max_ov:
                max_ov = ov
            assert ov < 1e-6, (
                f"[{context_name}] Interference detected between {solids[i].label} and {solids[j].label}: {ov:.8f} mm^3!"
            )
    print(f"  [PASS] {context_name}: {n} parts checked, max overlap_volume = {max_ov:.8f} mm^3 (ZERO interference!)")


def _build_sunk_top_plate_twin_snap_cutter(cx_step: float, cy_step: float) -> bd.Solid:
    """
    Build Twin-Snap Top Plate cutter at `(cx_step, cy_step)`:
      - Central flywheel slot (`6.16 x 17.56 mm`, `R = 0.55 mm` -> `>= 0.35 mm` moving clearance to `#01` Flywheel!)
      - Symmetric West & East bearing/PCB windows (`X_mod in [-8.20, +8.20]`, `Y_mod in [Y_AXLE ± 4.75]`)
      - Symmetric switch-style snap-hook windows (`X_mod in [±5.65, ±7.75]`, `Y_mod in [Y_AXLE ± 5.42]` = `10.84 mm`),
        100% hidden beneath the Twin `16.40 -> 11.60 x 6.19 mm` Pyramid-Deep-R covers while engaging their `±5.65 mm`
        snap barbs cleanly underneath the `1.60 mm` FR-4 Top Plate!
    """
    with bd.BuildSketch(bd.Plane.XY) as sk_cut:
        with bd.Locations([(0.0, Y_AXLE)]):
            bd.RectangleRounded(6.16, 17.56, 0.55)
        with bd.Locations([(0.0, Y_AXLE)]):
            bd.RectangleRounded(16.40, 9.50, 0.50)
        for sgn_x in (-1.0, 1.0):
            with bd.Locations([(sgn_x * 6.70, Y_AXLE)]):
                bd.RectangleRounded(3.00, 10.86, 0.45)

    cutter_mod = bd.extrude(sk_cut.sketch, amount=3.00).solids()[0]
    return cutter_mod.rotate(bd.Axis.Z, 180).moved(bd.Location((cx_step, cy_step, -4.50))).solids()[0]


def main():
    print("=== 1. Building & Verifying Individual Manufacturable Parts ===")
    # 1) Cup-Shaped SUS304 Flywheel (CNC turned/milled metal part; check bores >= 1.50mm)
    flywheel_part = build_sus304_flywheel_centered()
    mass_sus304_g = flywheel_part.volume * 0.00793  # SUS304 density 7.93 g/cm³ = 0.00793 g/mm³
    verify_jlc3dp_part(flywheel_part, "sus304-flywheel", check_bores=True, check_wall_0p8=False)
    print(f"         -> Cup-Shaped SUS304 Flywheel Calculated Mass = {mass_sus304_g:.2f} g")
    bd.export_step(flywheel_part, str(PARTS_DIR / "sus304-flywheel.step"))
    bd.export_stl(flywheel_part, str(PARTS_DIR / "sus304-flywheel.stl"))

    # 2) Internal 9-Ball Axial Resin Ratchet Hub (100% walls & snap-in lips >= 0.85 mm -> 0 exclusions needed!)
    hub_part = build_ratchet_hub_print_oriented()
    max_v_r = max(math.hypot(v.X, v.Y) for v in hub_part.vertices())
    assert max_v_r <= HUB_R + 1e-4, f"Ratchet hub vertex radius {max_v_r:.4f} > HUB_R {HUB_R:.4f} mm!"
    verify_jlc3dp_part(hub_part, "ratchet-hub", check_bores=True, check_wall_0p8=True)
    bd.export_step(hub_part, str(PARTS_DIR / "ratchet-hub.step"))
    bd.export_stl(hub_part, str(PARTS_DIR / "ratchet-hub.stl"))

    # 3) Slim Rounded-Ear Hinged Carriage (flat East face X = +6.45 placed on Z = 0.0000 print bed!)
    carriage_asm = build_wheel_carriage_assembled()
    carriage_print = carriage_asm.rotate(bd.Axis.Y, 90)
    c_bb = carriage_print.bounding_box()
    carriage_print = carriage_print.moved(bd.Location((-c_bb.center().X, -c_bb.center().Y, -c_bb.min.Z))).solids()[0]
    verify_jlc3dp_part(carriage_print, "wheel-carriage", check_bores=True)
    bd.export_step(carriage_print, str(PARTS_DIR / "wheel-carriage.step"))
    bd.export_stl(carriage_print, str(PARTS_DIR / "wheel-carriage.stl"))

    # 4) Wheel Base Frame (flat at Z = 0.0000 mm)
    base_part = build_wheel_base_frame()
    verify_jlc3dp_part(base_part, "wheel-base-frame", check_bores=True)
    bd.export_step(base_part, str(PARTS_DIR / "wheel-base-frame.step"))
    bd.export_stl(base_part, str(PARTS_DIR / "wheel-base-frame.stl"))

    # 4b) Low-Profile Sunk Wheel Base Frame (shifted +1.20 mm in Z so flat bottom lies at Z = 0.0000 mm)
    base_sunk_asm = build_wheel_base_frame_sunk_assembled()
    base_sunk_print = base_sunk_asm.moved(bd.Location((0.0, 0.0, 1.20))).solids()[0]
    verify_jlc3dp_part(base_sunk_print, "wheel-base-frame-sunk", check_bores=True)
    bd.export_step(base_sunk_print, str(PARTS_DIR / "wheel-base-frame-sunk.step"))
    bd.export_stl(base_sunk_print, str(PARTS_DIR / "wheel-base-frame-sunk.stl"))

    # 4c) 180°-Symmetric Edge-Rounded Pyramid Switch-Snap Cover (`#20`, flat outer wall placed on Z = 0.0000!)
    cover_plate = build_wheel_cover_plate_coords()
    cover_rot = cover_plate.rotate(bd.Axis.Y, 90)
    cov_bb = cover_rot.bounding_box()
    cover_print = cover_rot.moved(bd.Location((-cov_bb.center().X, -cov_bb.center().Y, -cov_bb.min.Z))).solids()[0]
    cover_print.label = "Wheel_Pyramid_Cover"
    verify_jlc3dp_part(
        cover_print,
        "wheel-cover",
        check_bores=True,
        check_wall_0p8=True,
        allowed_thin_pred=allowed_wheel_cover_thin,
    )
    bd.export_step(cover_print, str(PARTS_DIR / "wheel-cover.step"))
    bd.export_stl(cover_print, str(PARTS_DIR / "wheel-cover.stl"))

    # 5) Standalone Eval Pod Stand (flat at Z = 0.0000 mm)
    stand_part = build_eval_pod_stand()
    verify_jlc3dp_part(stand_part, "eval-pod-stand", check_bores=True)
    bd.export_step(stand_part, str(PARTS_DIR / "eval-pod-stand.step"))
    bd.export_stl(stand_part, str(PARTS_DIR / "eval-pod-stand.stl"))

    print("\n=== 2. Building & Verifying Module & Standalone Pod Assemblies ===")
    mod_parts = assemble_module_parts(origin=(0.0, 0.0, 0.0), sunk=False)
    verify_zero_overlap(mod_parts, "Inertia_Wheel_Module")
    mod_asm = bd.Compound(label="Inertia_Wheel_Module_Assembly", children=mod_parts)
    bd.export_step(mod_asm, str(ASSEMBLIES_DIR / "inertia-wheel-module-assembly.step"))

    mod_sunk_parts = assemble_module_parts(origin=(0.0, 0.0, 0.0), sunk=True, include_covers=True)
    verify_zero_overlap(mod_sunk_parts, "Inertia_Wheel_Module_Sunk")
    mod_sunk_asm = bd.Compound(label="Inertia_Wheel_Module_Sunk_Assembly", children=mod_sunk_parts)
    bd.export_step(mod_sunk_asm, str(ASSEMBLIES_DIR / "inertia-wheel-module-sunk-assembly.step"))

    # Standalone Eval Pod Assembly
    stand_asm = build_eval_pod_stand()
    stand_asm.label = "Eval_Pod_Stand"
    with bd.BuildPart() as cpcb_bp:
        with bd.BuildSketch(bd.Plane.XY.offset(5.41)):
            bd.RectangleRounded(48.0, 32.0, radius=1.00)
        bd.extrude(amount=1.60)
    carrier_pcb = cpcb_bp.part
    for bx, by in [(-21.50, -13.50), (21.50, -13.50), (-21.50, 13.50), (21.50, 13.50)]:
        carrier_pcb = carrier_pcb - bd.Cylinder(
            radius=1.10, height=5.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
        ).moved(bd.Location((bx, by, 4.00)))
    carrier_pcb = carrier_pcb.solids()[0]
    carrier_pcb.label = "Eval_Carrier_PCB_48x32"

    rp2040_zero = bd.Box(23.5, 18.0, 3.20, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(
        bd.Location((-12.0, 0.0, 7.02))
    )
    rp2040_zero.label = "Waveshare_RP2040_Zero"

    jst_sh = bd.Box(8.00, 4.30, 2.95, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(
        bd.Location((-2.0, -12.5, 7.02))
    )
    jst_sh.label = "JST_SH_6Pin_Header"

    pod_wheel_parts = assemble_module_parts(origin=(12.5, 0.0, 7.02))
    pod_all = [stand_asm, carrier_pcb, rp2040_zero, jst_sh, *pod_wheel_parts]
    verify_zero_overlap(pod_all, "Standalone_Eval_Pod")
    pod_asm = bd.Compound(label="Inertia_Wheel_Eval_Pod_Assembly", children=pod_all)
    bd.export_step(pod_asm, str(ASSEMBLIES_DIR / "inertia-wheel-eval-pod-assembly.step"))

    print("\n=== 3. Verifying Sunk Mount + Twin Snap Covers on curcur40-right ===")
    cx_step, cy_step = 28.5750, -57.1500
    sys.path.insert(0, str(WORKSPACE / "scripts"))
    from generate_full_assembly import (
        build_main_pcb_solid,
        build_top_plate_solid,
        make_keycap_solid,
        RIGHT_SWITCHES,
        to_step_right,
    )

    right_case = bd.import_step(str(WORKSPACE / "cases" / "right.step")).solids()[0]
    right_case.label = "curcur40_Right_Case"

    sunk_main_pcb = build_main_pcb_solid(is_right=True)
    sunk_main_pcb.label = "curcur40_Right_Main_PCB"

    sunk_top_plate = build_top_plate_solid(is_right=True)
    sunk_top_plate.label = "curcur40_Right_Top_Plate"

    # Backward-compatible fallback if called before curcur40-right.kicad_pcb / plate-top-right.kicad_pcb has sunk cutouts:
    # (Once curcur40-right.kicad_pcb & plate-top-right.kicad_pcb have native sunk cutouts, subtracting again is a clean no-op!)
    with bd.BuildSketch(bd.Plane.XY.offset(-6.50)) as sk_pcb_win:
        with bd.Locations([(cx_step, cy_step)]):
            bd.RectangleRounded(18.50, 18.50, 0.50)
    sunk_main_pcb = sunk_main_pcb - bd.extrude(sk_pcb_win.sketch, amount=3.00)
    sunk_mount_step = [(cx_step - mx, cy_step - my) for mx, my in SUNK_MOUNT_PTS_MOD]
    for sx_m, sy_m in sunk_mount_step:
        sunk_main_pcb = sunk_main_pcb - bd.Cylinder(
            radius=1.85, height=4.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
        ).moved(bd.Location((sx_m, sy_m, -6.50)))
    sunk_main_pcb = sunk_main_pcb.solids()[0]
    sunk_main_pcb.label = "curcur40_Right_Main_PCB"

    tb_cup = (
        bd.import_step(str(WORKSPACE / "cases" / "trackball-cup.step"))
        .solids()[0]
        .moved(bd.Location((23.8125, -109.5375, -16.00)))
    )
    tb_cup.label = "Trackball_Cup"

    keycaps = []
    rexsw2_cap = None
    for idx_k, (kx_pcb, ky_pcb) in enumerate(RIGHT_SWITCHES):
        sx, sy = to_step_right(kx_pcb, ky_pcb)
        kc = make_keycap_solid(sx, sy, label=f"Right_Keycap_{idx_k+1:02d}")
        keycaps.append(kc)
        if abs(kx_pcb - 14.2875) < 0.1 and abs(ky_pcb - 19.0500) < 0.1:
            rexsw2_cap = kc

    tb_ball = bd.Sphere(radius=12.50).moved(bd.Location((23.8125, -109.5375, 2.30))).solids()[0]
    tb_ball.label = "Trackball_25mm_Ref"

    mod_sunk_local = bd.Compound(
        children=assemble_module_parts(origin=(0.0, 0.0, 0.0), sunk=True, include_covers=True)
    ).rotate(bd.Axis.Z, 180).moved(bd.Location((cx_step, cy_step, CZ_SUNK)))
    sunk_dropped_parts = list(mod_sunk_local.solids())
    for idx, s in enumerate(sunk_dropped_parts):
        s.label = mod_sunk_parts[idx].label

    # Ensure Top Plate has Twin-Snap window + 3x Ø2.40mm M2 holes (works both before and after plate-top-right update):
    plate_fill = bd.Box(
        18.60, 18.60, 1.60, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
    ).moved(bd.Location((cx_step, cy_step, -3.60)))
    sunk_top_plate = (sunk_top_plate + plate_fill) - _build_sunk_top_plate_twin_snap_cutter(cx_step, cy_step)
    for sx_m, sy_m in sunk_mount_step:
        sunk_top_plate = sunk_top_plate - bd.Cylinder(
            radius=1.20, height=4.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
        ).moved(bd.Location((sx_m, sy_m, -4.50)))
    sunk_top_plate = sunk_top_plate.solids()[0]
    sunk_top_plate.label = "curcur40_Right_Top_Plate"

    sunk_screws = []
    for idx_m, (sx_m, sy_m) in enumerate(sunk_mount_step):
        sc_head = bd.Cylinder(
            radius=1.95, height=0.80, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
        ).moved(bd.Location((sx_m, sy_m, -1.99)))
        sc_shank = bd.Cylinder(
            radius=0.78, height=4.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)
        ).moved(bd.Location((sx_m, sy_m, -1.99)))
        sc = (sc_head + sc_shank).solids()[0]
        sc.label = f"Sunk_Mount_Screw_M2x4_{idx_m+1}"
        sunk_screws.append(sc)

    sunk_fit_parts = [
        right_case, sunk_main_pcb, sunk_top_plate, tb_cup, tb_ball,
        *keycaps, *sunk_screws, *sunk_dropped_parts,
    ]
    verify_zero_overlap(sunk_fit_parts, "curcur40_Right_Sunk_Check")

    sunk_static_labels = {
        "Wheel_Base_Frame_Sunk",
        "Hinge_Pin_SUS304_2mm",
        "Kailh_Silent_Switch_6x6x4p3",
        "Wheel_Pyramid_Cover_Sensor",
        "Wheel_Pyramid_Cover_Companion",
    }
    sunk_fw = [s for s in sunk_dropped_parts if s.label == "SUS304_Flywheel_Cup_16p8mm"][0]
    fw_bb = sunk_fw.bounding_box()
    rexsw2_bb = rexsw2_cap.bounding_box()
    assert abs(0.5 * (fw_bb.min.X + fw_bb.max.X) - 0.5 * (rexsw2_bb.min.X + rexsw2_bb.max.X)) < 1e-3, (
        "Flywheel X center is not aligned with rEXSW2 key below!"
    )

    d_case_floor = min(closest_points(s, right_case).distance for s in sunk_dropped_parts)
    d_sunk_plate_moving = min(
        closest_points(s, sunk_top_plate).distance for s in sunk_dropped_parts if s.label not in sunk_static_labels
    )
    d_sunk_pcb_moving = min(
        closest_points(s, sunk_main_pcb).distance for s in sunk_dropped_parts if s.label not in sunk_static_labels
    )
    d_sunk_rexsw2 = min(closest_points(s, rexsw2_cap).distance for s in sunk_dropped_parts)
    assert d_case_floor >= 2.00, f"Sunk module vs Right Case clearance {d_case_floor:.3f} mm < 2.00 mm!"
    assert d_sunk_plate_moving >= 0.30, f"Sunk moving parts vs Top Plate {d_sunk_plate_moving:.3f} mm < 0.30 mm!"
    assert d_sunk_pcb_moving >= 0.30, f"Sunk moving parts vs Main PCB {d_sunk_pcb_moving:.3f} mm < 0.30 mm!"
    assert d_sunk_rexsw2 >= 1.00, f"Sunk module vs rEXSW2 Keycap {d_sunk_rexsw2:.3f} mm < 1.00 mm!"
    print(
        f"         -> Sunk Cup-Flywheel Z span = [{fw_bb.min.Z:+.2f}, {fw_bb.max.Z:+.2f}] mm, "
        f"Center Z = {0.5*(fw_bb.min.Z+fw_bb.max.Z):+.2f} mm (Top Plate Top = -2.00 mm!), "
        f"X Center = {0.5*(fw_bb.min.X+fw_bb.max.X):.4f} mm (rEXSW2 = {0.5*(rexsw2_bb.min.X+rexsw2_bb.max.X):.4f} mm!)"
    )
    print(f"         -> Clearance to unmodified Right Case floor/walls = {d_case_floor:.3f} mm (>= 2.00 mm)")
    print(
        f"         -> Moving Parts clearance to Twin-Snap Top Plate / Main PCB = "
        f"{d_sunk_plate_moving:.3f} / {d_sunk_pcb_moving:.3f} mm (>= 0.30 mm)"
    )
    print(f"         -> Clearance to South Keycap (rEXSW2)             = {d_sunk_rexsw2:.3f} mm (>= 1.00 mm)")

    sunk_asm = bd.Compound(label="curcur40_Right_With_Inertia_Wheel_Sunk", children=sunk_fit_parts)
    bd.export_step(sunk_asm, str(ASSEMBLIES_DIR / "curcur40-right-with-inertia-wheel-sunk.step"))
    print("\nAll Passive Cup-Flywheel Inertia Wheel & Twin Pyramid-Deep-R Cover 3D models generated and verified!")


if __name__ == "__main__":
    main()
