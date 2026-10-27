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

# Click-swing kinematics: the `#03` carriage (with `#01` wheel, bearings, shaft, magnets and the `#07` AS5600
# sub-PCB) pivots about the North `#15` hinge pin. Per the Kailh Square Silent `6.2 x 6.2 x 4.3 mm` (`H=4.3mm`)
# mechanical drawing:
#   - Molded housing body : 6.20 x 6.20 x 3.35 mm (`Z_mod in [0.02, 3.37]`)
#   - Actuator plunger    : Ø3.00 mm (`R = 1.50 mm`), Free Position `FP = 4.30 ± 0.15 mm` (`Z_mod = 4.32 mm`),
#                           Operating Position `OP = 4.10 ± 0.20 mm`, Pre-Travel `PT = 0.20 ± 0.1 mm`
#   - Striker bottom      : `Z_mod = 4.38 mm` (`0.06 mm` nominal free gap above `FP`, actuation at `0.26 mm` / `1.12°`,
#                           deterministic full over-travel envelope to `Z_mod = 3.82 mm` = `0.50 mm` plunger compression
#                           / `2.34°` rotation).
SWITCH_BODY_H = 3.35
SWITCH_PLUNGER_R = 1.50
SWITCH_FP_H = 4.30
SWITCH_OP_H = 4.10
SWITCH_PT = 0.20
STRIKER_CORNER_YZ = (7.10, 4.38)
SWITCH_BODY_TOP_Z = 0.02 + 3.80  # Deterministic 0.50 mm plunger bottom-out envelope (Z_mod = 3.82 mm)
MOVE_CLR = 0.30         # JLC3DP moving-part clearance (>= 0.30 mm)
COV_PLAY_X = 0.10       # Cover lateral play: 1.80 mm snap legs in 2.00 mm plate windows (±0.10 mm)
COV_PLAY_Y = 0.06       # Cover longitudinal play: snap legs (Y_AXLE ± 5.37) in plate windows (Y_AXLE ± 5.43)
ENV_CLR_X = MOVE_CLR + COV_PLAY_X   # 0.40 mm X-direction cover clearance to moving parts
ENV_CLR_YZ = MOVE_CLR + COV_PLAY_Y  # 0.36 mm Y/Z-direction cover clearance to moving parts

# Pyramid-Deep-R Cover (`#20`, `wheel-cover.step`) envelope in Plate-Top Z coords (`Z_plate = Z_mod + CZ_SUNK`):
COV_X_PLANE = WHEEL_X_MIN - ENV_CLR_X  # -3.13: 0.40 mm beside #01 Flywheel (>= 0.30 mm even at max ±0.10 mm play)
COV_X_WEST = -9.30      # 6.17 mm East-West width, steep West drop behind the #07 Sensor PCB pocket
COV_Z_BOT = -1.99       # Sits cleanly on Top Plate top surface (Z = -2.00 mm)
COV_Z_TOP = +2.68       # 0.92 mm lower than +3.60 mm Choc V2 keycaps, 3.72 mm lower than +6.40 mm wheel top!
COV_SILHOUETTE_MARGIN = 0.30  # Cover side silhouette stays >= 0.30 mm inside the Ø16.80 mm wheel outline

# Snap legs (sensor-side cover, mirrored by the 180° rotation for the companion cover):
COV_LEG_X = -4.85       # Leg X center (X in [-5.75, -3.95], East of the #07 PCB swing pocket)
COV_LEG_W = 1.80        # Leg width (2.00 mm plate window [3.85, 5.85] -> ±0.10 mm lateral play)
COV_LEG_Y_IN = 4.52     # Leg inner face |Y - Y_AXLE|
COV_LEG_Y_OUT = 5.37    # Leg outer face |Y - Y_AXLE| (0.06 mm to the Y_AXLE ± 5.43 plate window edge)
COV_POCKET_HALF_W = 5.11  # |Y - Y_AXLE| of the swept #07 PCB pocket (asserted >= the swept envelope)
COV_LEG_CHAMFER = COV_LEG_Y_OUT - COV_POCKET_HALF_W  # 0.26 mm 45° outer-edge chamfers: clear the R = 0.45 mm
#                                                      window corners and start flush with the pocket side wall
COV_BARB_TIP = 5.65     # Barb tip |Y - Y_AXLE| (0.22 mm latch under the FR-4 Top Plate)
COV_BARB_W = COV_LEG_W - 2.0 * COV_LEG_CHAMFER  # 1.28 mm barb, flush with the chamfered leg outer face

# Sunk Top Plate opening, quadrant `(+u, +v)` relative to the axle `(0, Y_AXLE)` as `(u, v, corner_radius)`.
# The full outline is mirrored into all four quadrants (identical vertex list in `scripts/generate_plates.py`).
#   - Wheel slot      : |u| <= 3.04, |v| <= 9.08 (R = 0.55) -> >= 0.30 mm to the wheel over the full click stroke
#   - Core window     : |u| <= 8.20, |v| <= 4.20 (bearing ears, magnets, AS5600 IC swing envelope)
#   - #07 PCB window  : 6.65 <= |u| <= 8.20, |v| <= 5.30 (R = 0.50) -> >= 0.30 mm to the #07 PCB swing envelope
#   - Snap windows    : 3.85 <= |u| <= 5.85, |v| <= 5.43 (R = 0.45) -> locate the 1.80 mm legs at ±0.10 mm
#   - FR-4 shoulders  : inner 3.85 - 3.04 = 0.81 mm (>= 0.80 mm), outer 6.65 - 5.85 = 0.80 mm (>= 0.80 mm),
#                       concave inner corners filleted at R = 0.25 mm (zero R = 0.00 sharp corners)
SUNK_PLATE_OPENING_Q1 = [
    (8.20, 5.30, 0.50),
    (6.65, 5.30, 0.50),
    (6.65, 4.20, 0.25),
    (5.85, 4.20, 0.25),
    (5.85, 5.43, 0.45),
    (3.85, 5.43, 0.45),
    (3.85, 4.20, 0.25),
    (3.04, 4.20, 0.25),
    (3.04, 9.08, 0.55),
]


def sunk_plate_opening_full() -> list[tuple[float, float, float]]:
    """Full counter-clockwise outline `(u, v, r)` of the sunk Top Plate opening (36 vertices)."""
    q1 = SUNK_PLATE_OPENING_Q1
    q2 = [(-u, v, r) for (u, v, r) in reversed(q1)]
    q3 = [(-u, -v, r) for (u, v, r) in q1]
    q4 = [(u, -v, r) for (u, v, r) in reversed(q1)]
    return q1 + q2 + q3 + q4


def click_hinge_axis(z_offset: float = 0.0) -> bd.Axis:
    """Hinge axis of the `#03` carriage (`+X` direction) in module coords (or plate coords with `z_offset`)."""
    return bd.Axis((0.0, HINGE_Y, HINGE_Z + z_offset), (1.0, 0.0, 0.0))


def click_hard_stop_deg() -> float:
    """Press angle at which the striker tab corner bottoms out on the `#10` switch body (deterministic envelope)."""
    dy = STRIKER_CORNER_YZ[0] - HINGE_Y
    dz = STRIKER_CORNER_YZ[1] - HINGE_Z
    target = SWITCH_BODY_TOP_Z - HINGE_Z
    lo, hi = 0.0, math.radians(10.0)
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        z_rel = -dy * math.sin(mid) + dz * math.cos(mid)
        if z_rel > target:
            lo = mid
        else:
            hi = mid
    return math.degrees(0.5 * (lo + hi))


CLICK_SWEEP_DEG = round(click_hard_stop_deg() + 0.05, 2)  # ~2.34° (striker travel ~0.57 mm incl. 0.10 mm free gap)


def press_rotate(shape: bd.Shape, deg: float, z_offset: float = 0.0) -> bd.Shape:
    """Rotate a carriage-mounted shape by `deg` degrees in the press (wheel-down) direction."""
    return shape.rotate(click_hinge_axis(z_offset), -deg)


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


def build_cover_outer_plate_coords() -> bd.Solid:
    """Solid exterior of the `#20` cover (sensor side, plate coords) before the interior voids and snap legs."""
    return make_rounded_pyramid_solid(
        COV_X_WEST, 7.70, 7.00, COV_Z_BOT, COV_Z_TOP,
        z_skirt_end=-0.40, ux_top=0.90, uy_top=2.80,
        r_xy_bot=1.80, r_xy_top=1.30, r_eave=3.00, r_crown=1.40,
    )


def _press_yz(y: float, z: float, deg: float, z_offset: float = 0.0) -> tuple[float, float]:
    """Rotate a point `(y, z)` about the hinge axis by `deg` in the press (wheel-down) direction."""
    hy, hz = HINGE_Y, HINGE_Z + z_offset
    th = math.radians(deg)
    dy, dz = y - hy, z - hz
    return hy + dy * math.cos(th) + dz * math.sin(th), hz - dy * math.sin(th) + dz * math.cos(th)


def _swept_mirrored_yz_bounds(y0, y1, z0, z1, z_offset: float = 0.0) -> tuple[float, float, float, float]:
    """
    Axis-aligned YZ bounds of a rectangle swept over `[0, CLICK_SWEEP_DEG]` and mirrored about `Y = Y_AXLE`
    (the same cover part serves both sides via a 180° rotation, which mirrors the sweep direction).
    """
    pts = []
    for deg in (0.0, 0.5 * CLICK_SWEEP_DEG, CLICK_SWEEP_DEG):
        for y in (y0, y1):
            for z in (z0, z1):
                py, pz = _press_yz(y, z, deg, z_offset)
                pts.extend([(py, pz), (2.0 * Y_AXLE - py, pz)])
    ys = [p[0] for p in pts]
    zs = [p[1] for p in pts]
    return min(ys) - 0.01, max(ys) + 0.01, min(zs) - 0.01, max(zs) + 0.01


def build_cover_swing_voids_plate_coords() -> bd.Shape:
    """
    Build the interior clearance voids of the `#20` cover (sensor side, plate coords). Each moving-part envelope
    (offset by `0.30 mm` + cover play) is swept over the full click-press stroke `[0, CLICK_SWEEP_DEG]` about the
    hinge axis and mirrored about `Y = Y_AXLE` (companion side), then bounded by simple analytic shapes whose
    faces never form `< 0.80 mm` internal steps:
      1) Bearing-ear / bearing / magnet / `AS5600` SOIC-8 body tunnel: one cylinder (`R = 3.45 + 0.36 + h`) whose
         centre is lowered by `h` so it contains the ear circle AND the `3.90 x 4.90 mm` `AS5600` SOIC-8 body at rest
         AND at both mirrored bottom-out positions (crown roof unchanged), `X in [-6.61, -2.40]` (`>= 0.40 mm` axial
         clearance to the `#08` `AS5600` body at `X = -5.69`, `#16` magnet at `X = -5.49`, and companion East ear)
      2) `#07` stepped sub-PCB & SOIC-8 lead-frame envelope: `X in [-8.15, -5.75]` (`>= 0.40 mm` axial clearance to
         `#07` PCB `-6.95` and SOIC-8 gull-wing leads `-6.64`), `Y = Y_AXLE ± 5.11 mm`, `0.80 mm` ceiling chamfers
    """
    zo = CZ_SUNK
    x_pcb0 = -7.75 - ENV_CLR_X   # -8.15
    x_prof1 = -5.75              # -5.75 (coplanar with the 1.80 mm snap leg West face; clears #07 PCB & SOIC-8 leads)
    # Tunnel starts 0.86 mm West of the profile end so its end face never forms a < 0.80 mm step with it, and so
    # that it encloses the AS5600 SOIC-8 body (X in [-6.94, -5.69]) and companion East bearing ear (X <= +5.35).
    x_tun0 = x_prof1 - 0.86      # -6.61
    assert x_tun0 <= -5.69 - ENV_CLR_X and x_tun0 <= -(5.35 + ENV_CLR_X)
    # 1) Tunnel: rest centre c0 = (Y_AXLE, -2.00); bottom-out centres c1 = (Y_AXLE ± dy, -2.00 - dz)
    c1y, c1z = _press_yz(Y_AXLE, -2.00, CLICK_SWEEP_DEG, zo)
    dy, dz = abs(c1y - Y_AXLE), abs(c1z - (-2.00))
    h = (dy * dy + dz * dz) / (2.0 * dz)
    r_tun = 3.45 + ENV_CLR_YZ + h + 0.01
    tunnel = (
        bd.Cylinder(radius=r_tun, height=(-2.40) - x_tun0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((x_tun0, Y_AXLE, -2.00 - h)))
    )

    def bounds(half_y, z0_mod, z1_mod):
        return _swept_mirrored_yz_bounds(
            Y_AXLE - half_y - ENV_CLR_YZ, Y_AXLE + half_y + ENV_CLR_YZ,
            z0_mod + zo - ENV_CLR_YZ, z1_mod + zo + ENV_CLR_YZ, zo,
        )

    # 2) #07 PCB stepped envelope (relative half-widths about Y_AXLE), also enclosing SOIC-8 gull-wing leads (Y ± 3.00)
    #    while verify_tunnel checks that the 3.90 x 4.90 mm SOIC-8 body lies 100% inside `r_tun`
    lo_ya, lo_yb, _, _ = bounds(4.40, 4.45, 10.30)
    up_ya, up_yb, _, up_zt = bounds(3.95, 10.30, 13.11)
    w_pcb_req = max(Y_AXLE - lo_ya, lo_yb - Y_AXLE, Y_AXLE - up_ya, up_yb - Y_AXLE)
    assert w_pcb_req <= COV_POCKET_HALF_W, f"#07 pocket half-width {w_pcb_req:.3f} > {COV_POCKET_HALF_W:.2f} mm"
    w_pcb = COV_POCKET_HALF_W
    ic_body_ya, ic_body_yb, _, ic_zt = bounds(1.95, 10.05 - 2.45, 10.05 + 2.45)
    assert math.hypot(max(Y_AXLE - ic_body_ya, ic_body_yb - Y_AXLE), ic_zt - (-2.00 - h)) <= r_tun
    z_bot = -9.50
    c_top = 0.80  # 45° ceiling chamfers (>= 0.80 mm so side wall and ceiling never form a thin step pair)
    half = [
        (w_pcb, z_bot),
        (w_pcb, up_zt - c_top),
        (w_pcb - c_top, up_zt),
    ]
    poly = half + [(-y, z) for (y, z) in reversed(half)]
    with bd.BuildSketch(bd.Plane.YZ.offset(x_pcb0)) as sk_pcb:
        bd.Polygon([(Y_AXLE + y, z) for (y, z) in poly], align=None)
    profile_env = bd.extrude(sk_pcb.sketch, amount=x_prof1 - x_pcb0).solids()[0]
    return (tunnel + profile_env)


def build_wheel_cover_plate_coords() -> bd.Solid:
    """
    Build Edge-Rounded Pyramid Switch-Snap Cover (`#20`, `wheel-cover.step`) in Plate-Top Z coordinates
    (`Z = -2.00 mm` == Top Plate top surface, mirror-symmetric about `Y = Y_AXLE` so 1 single part serves
    BOTH Sensor and Companion sides via a 180° XY rotation around `(0.0, Y_AXLE)`):
      - Exterior: `15.40 -> 14.00 mm` trapezoid length x `6.17 mm` width (`X in [-9.30, -3.13]`),
        `Z_top = +2.68 mm` (`0.92 mm` lower than `+3.60 mm` keycaps, `3.72 mm` below `+6.40 mm` wheel top!).
        Seen along the axle, the whole cover silhouette stays `>= 0.30 mm` inside the `Ø16.80 mm` wheel outline,
        and the inner face keeps `0.40 mm` to the `#01` wheel (`>= 0.30 mm` even at the `±0.10 mm` lateral play).
      - Interior cavities: swept click-stroke envelopes of the bearing ear / magnet / `AS5600` IC / `#07` PCB
        (`build_cover_swing_voids_plate_coords`) -> `>= 0.30 mm` moving clearance from rest to switch bottom-out.
      - Attachment: Switch-style North & South cantilever snap legs (`0.85 mm` thick, `1.80 mm` wide at `X = -4.85`,
        `0.26 mm` outer-edge chamfers) located by `2.00 mm` wide plate windows (`±0.10 mm` play), with `1.28 mm` wide
        `0.28 mm` latch barbs (`Z = -3.63 .. -4.55 mm`) snapping under the `1.60 mm` FR-4 Top Plate (`Z = -3.60 mm`).
    """
    outer = build_cover_outer_plate_coords()

    dome = outer - build_cover_swing_voids_plate_coords()
    assert len(dome.solids()) == 1, "Cover dome must remain a single solid after the clearance voids!"
    dome = dome.solids()[0]

    leg_x0 = COV_LEG_X - 0.5 * COV_LEG_W
    for sgn in (-1.0, 1.0):
        y_in = Y_AXLE + sgn * COV_LEG_Y_IN
        y_out = Y_AXLE + sgn * COV_LEG_Y_OUT
        y_barb_tip = Y_AXLE + sgn * COV_BARB_TIP
        with bd.BuildSketch(bd.Plane.XY.offset(-4.55)) as sk_leg:
            with bd.Locations([(COV_LEG_X, 0.5 * (y_in + y_out))]):
                bd.Rectangle(COV_LEG_W, COV_LEG_Y_OUT - COV_LEG_Y_IN)
            outer_vs = [v for v in sk_leg.vertices() if abs(v.Y - y_out) < 1e-6]
            bd.chamfer(outer_vs, length=COV_LEG_CHAMFER)
        leg = bd.extrude(sk_leg.sketch, amount=(-1.40) - (-4.55)).solids()[0]
        assert abs(leg.bounding_box().min.X - leg_x0) < 1e-6

        with bd.BuildSketch(bd.Plane.YZ) as sk_barb:
            bd.Polygon(
                [
                    (y_out, -3.63),
                    (y_barb_tip, -3.76),
                    (y_out, -4.55),
                ],
                align=None,
            )
        barb = (
            bd.extrude(sk_barb.sketch, amount=0.5 * COV_BARB_W, both=True)
            .moved(bd.Location((COV_LEG_X, 0.0, 0.0)))
            .solids()[0]
        )
        dome = (dome + leg + barb).solids()[0]

    dome.label = "Wheel_Pyramid_Cover"
    return dome


def make_allowed_wheel_cover_thin(print_shift: tuple[float, float, float]):
    """
    Whitelist for the print-oriented `wheel-cover` (`+90°` Y rotation, then `print_shift`): only the intentional
    switch-style snap legs below the cover bottom (`Z_plate <= -1.98`, `|Y - Y_AXLE| >= 4.10`), i.e. the `0.85 mm`
    cantilever with its `0.30 mm` corner chamfers, the `0.28 mm` latch barb and the leg-root edge facing the
    bearing tunnel opening. The dome itself (exterior, swept clearance voids) has zero `< 0.80 mm` face pairs.
    """
    sx, sy, sz = print_shift

    def pred(d: float, mx: float, my: float, mz: float) -> bool:
        z_plate = mx - sx  # print X = plate Z + sx
        y_plate = my - sy  # print Y = plate Y + sy
        return z_plate <= COV_Z_BOT + 0.01 and abs(y_plate - Y_AXLE) >= 4.10

    return pred


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
    #    - U1 AS5600-ASOT SOIC-8 (JEDEC MS-012: 3.90 x 4.90 x 1.25 mm body at X_mod in [-6.94, -5.69], Y = Y_AXLE ± 1.95,
    #      plus 6.00 x 4.90 x 0.30 mm gull-wing lead frame at X_mod in [-6.94, -6.64], Z = 10.05 ± 2.45)
    #    - C1 (100nF 0402) & C2 (1uF 0402) on F.Cu at Z_mod = 6.40 mm
    sens_mag = (
        bd.Cylinder(radius=1.50, height=0.75, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((-5.49, Y_AXLE, Z_AXLE)))
    )
    sens_mag.label = "Diametric_Magnet_3x1mm"

    as5600_pcb = build_stepped_sensor_pcb_mod()

    as5600_body = bd.Box(
        1.25, 3.90, 4.90,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER),
    ).moved(bd.Location((-6.94, Y_AXLE, 10.05)))
    as5600_leads = bd.Box(
        0.30, 6.00, 4.90,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER),
    ).moved(bd.Location((-6.94, Y_AXLE, 10.05)))
    as5600_ic = (as5600_body + as5600_leads).solids()[0]
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

    # 10. Kailh Square Silent Micro Switch (`6.2 x 6.2 x 4.3 mm`, official H=4.3mm drawing:
    #     6.20 x 6.20 x 3.35 mm molded housing with R=0.40 mm corners + Ø3.00 x 0.95 mm plunger -> FP = 4.30 mm)
    with bd.BuildSketch(bd.Plane.XY.offset(0.02)) as sk_sw:
        with bd.Locations([(6.20, 5.70)]):
            bd.RectangleRounded(6.20, 6.20, 0.40)
    sw_body = bd.extrude(sk_sw.sketch, amount=SWITCH_BODY_H).solids()[0]
    sw_btn = bd.Cylinder(
        radius=SWITCH_PLUNGER_R,
        height=SWITCH_FP_H - SWITCH_BODY_H,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((6.20, 5.70, 0.02 + SWITCH_BODY_H)))
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


def verify_cover_silhouette(cover_plate: bd.Solid):
    """Seen along the axle (X), the cover must stay >= 0.30 mm inside the Ø16.80 mm wheel outline."""
    r_lim = WHEEL_R - COV_SILHOUETTE_MARGIN
    ring = (bd.Box(30.0, 40.0, 10.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(
        bd.Location((0.0, Y_AXLE, -2.00))
    ) - (
        bd.Cylinder(radius=r_lim, height=30.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((0.0, Y_AXLE, -2.00)))
    )).solids()[0]
    ov = overlap_volume(cover_plate, ring)
    assert ov < 1e-6, f"[wheel-cover] Silhouette protrudes beyond R = {r_lim:.2f} mm wheel outline ({ov:.6f} mm^3)!"
    extra = closest_points(cover_plate, ring).distance
    print(
        f"  [PASS] wheel-cover silhouette: inside the Ø{WHEEL_OD:.2f} mm wheel outline by "
        f"{COV_SILHOUETTE_MARGIN + extra:.3f} mm (>= {COV_SILHOUETTE_MARGIN:.2f} mm)"
    )


def verify_plate_opening_hidden():
    """Every plate opening outside the wheel gap must lie >= 0.30 mm inside the twin cover outlines (top view)."""
    outer = build_cover_outer_plate_coords()
    sec = outer & bd.Box(40.0, 40.0, 0.01, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(
        bd.Location((0.0, 0.0, COV_Z_BOT + 0.005))
    )
    fp_face = min(sec.faces(), key=lambda f: f.center().Z)
    fp_face = bd.Face(fp_face.outer_wire())
    fp_in = bd.offset(fp_face, amount=-MOVE_CLR)
    fp_in = fp_in.faces()[0] if hasattr(fp_in, "faces") else fp_in
    fp_in_c = fp_in.moved(bd.Location((0.0, -Y_AXLE, 0.0))).rotate(bd.Axis.Z, 180).moved(bd.Location((0.0, Y_AXLE, 0.0)))
    opening = build_sunk_plate_opening_face(fp_in.center().Z)
    # The inner (wheel-side) cover edge borders the 0.40 mm wheel gap itself, so the 0.30 mm margin applies to
    # the outer (North / South / West) cover edges only.
    gap_strip = bd.Rectangle(2.0 * (abs(COV_X_PLANE) + MOVE_CLR), 40.0).moved(
        bd.Location((0.0, Y_AXLE, fp_in.center().Z))
    )
    exposed = (opening - gap_strip) - fp_in - fp_in_c
    area = sum(f.area for f in exposed.faces()) if exposed.faces() else 0.0
    assert area < 1e-6, f"[Top Plate] {area:.6f} mm^2 of the plate opening is not hidden >= 0.30 mm under the covers!"
    print("  [PASS] Top Plate opening 100% hidden >= 0.30 mm inside the twin cover outlines (outside the wheel gap)")


def build_sunk_static_env_mod() -> list[bd.Solid]:
    """Local Top Plate (with the sunk opening) and Main PCB (18.50 mm window) solids in module coords."""
    z_plate_top = -2.00 - CZ_SUNK
    plate = bd.Box(40.0, 40.0, 1.60, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).moved(
        bd.Location((0.0, 0.0, z_plate_top))
    )
    plate = plate - bd.extrude(build_sunk_plate_opening_face(z_plate_top - 2.0), amount=4.0)
    plate = plate.solids()[0]
    plate.label = "Local_Top_Plate"
    z_pcb_top = -4.20 - CZ_SUNK
    pcb = bd.Box(40.0, 40.0, 1.60, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).moved(
        bd.Location((0.0, 0.0, z_pcb_top))
    )
    with bd.BuildSketch(bd.Plane.XY.offset(z_pcb_top - 2.0)) as sk_win:
        bd.RectangleRounded(18.50, 18.50, 0.50)
        with bd.Locations(*SUNK_MOUNT_PTS_MOD):
            bd.Circle(1.85)
    pcb = (pcb - bd.extrude(sk_win.sketch, amount=4.0)).solids()[0]
    pcb.label = "Local_Main_PCB"
    return [plate, pcb]


def verify_click_swing(mod_sunk_parts: list[bd.Shape], steps: int = 6):
    """
    Sweep the carriage-mounted parts over the full click stroke `[0, CLICK_SWEEP_DEG]` (striker bottom-out on the
    `#10` switch body) and assert:
      - Covers (nominal)                      : >= 0.30 + 0.06 mm play
      - Covers shifted by ±0.10 X / ±0.06 Y   : >= 0.30 mm
      - Local Top Plate / Main PCB            : >= 0.30 mm
      - `#04B` base frame                     : no contact (sliding hinge faces only)
    """
    static_lbl = {"Wheel_Base_Frame_Sunk", "Hinge_Pin_SUS304_2mm", "Kailh_Silent_Switch_6x6x4p3",
                  "Wheel_Pyramid_Cover_Sensor", "Wheel_Pyramid_Cover_Companion"}
    by_lbl = {p.label: p for p in mod_sunk_parts}
    moving = [p for p in mod_sunk_parts if p.label not in static_lbl
              and not p.label.startswith("Steel_Ball") and p.label != "Ratchet_Hub_Internal_Resin"]
    covers = [by_lbl["Wheel_Pyramid_Cover_Sensor"], by_lbl["Wheel_Pyramid_Cover_Companion"]]
    plate, pcb = build_sunk_static_env_mod()
    base = by_lbl["Wheel_Base_Frame_Sunk"]

    def near(a, b, tol):
        ba, bb = a.bounding_box(), b.bounding_box()
        return not (
            ba.max.X + tol < bb.min.X or bb.max.X + tol < ba.min.X or
            ba.max.Y + tol < bb.min.Y or bb.max.Y + tol < ba.min.Y or
            ba.max.Z + tol < bb.min.Z or bb.max.Z + tol < ba.min.Z
        )

    checks = []  # (static_shape, required_min, tag)
    for c in covers:
        checks.append((c, ENV_CLR_YZ - 1e-3, f"{c.label} (nominal)"))
        sx = 1.0 if c.bounding_box().center().X < 0 else -1.0  # +X toward wheel for the sensor-side cover
        for dx, dy in ((sx * COV_PLAY_X, 0.0), (0.0, COV_PLAY_Y), (0.0, -COV_PLAY_Y)):
            checks.append((c.moved(bd.Location((dx, dy, 0.0))), MOVE_CLR - 1e-3, f"{c.label} (shift {dx:+.2f},{dy:+.2f})"))
    checks.append((plate, MOVE_CLR - 1e-3, "Top Plate"))
    checks.append((pcb, MOVE_CLR - 1e-3, "Main PCB"))
    checks.append((base, 0.01, "Wheel_Base_Frame_Sunk"))

    worst = {}
    for k in range(steps + 1):
        deg = CLICK_SWEEP_DEG * k / steps
        for m in moving:
            mm = press_rotate(m, deg)
            for s, req, tag in checks:
                if not near(mm, s, 1.0):
                    continue
                d = closest_points(mm, s).distance
                key = tag
                if key not in worst or d < worst[key][0]:
                    worst[key] = (d, m.label, deg)
                assert d >= req, (
                    f"[Click Swing] {m.label} vs {tag} = {d:.3f} mm < {req:.2f} mm at {deg:.2f}° press!"
                )
    print(f"  [PASS] Click-swing sweep 0 -> {CLICK_SWEEP_DEG:.2f}° (striker bottom-out on #10 switch body):")
    for tag, (d, lbl, deg) in sorted(worst.items(), key=lambda kv: kv[1][0]):
        print(f"           min {d:.3f} mm : {tag:50s} <- {lbl} @ {deg:.2f}°")
    return worst


def build_sunk_plate_opening_face(z: float = 0.0) -> bd.Face:
    """2D sunk Top Plate opening (`sunk_plate_opening_full`) around `(0, Y_AXLE)` in module XY at height `z`."""
    pts = sunk_plate_opening_full()
    with bd.BuildSketch(bd.Plane.XY.offset(z)) as sk:
        bd.Polygon([(u, Y_AXLE + v) for (u, v, _) in pts], align=None)
        for rad in sorted({r for (_, _, r) in pts if r > 0}):
            targets = [(u, Y_AXLE + v) for (u, v, r) in pts if abs(r - rad) < 1e-9]
            verts = [
                vx for vx in sk.vertices()
                if any(abs(vx.X - tu) < 1e-6 and abs(vx.Y - tv) < 1e-6 for tu, tv in targets)
            ]
            bd.fillet(verts, radius=rad)
    return sk.sketch.faces()[0]


def _build_sunk_top_plate_twin_snap_cutter(cx_step: float, cy_step: float) -> bd.Solid:
    """
    Build Twin-Snap Top Plate cutter at `(cx_step, cy_step)` from `SUNK_PLATE_OPENING_Q1` (36-vertex outline):
      - Central flywheel slot (`6.08 x 18.16 mm`, `R = 0.55 mm`) -> `>= 0.30 mm` to `#01` over the full click stroke
      - Core window (`16.40 x 8.40 mm`, concave corners `R = 0.25 mm`) for the bearing ears, magnets and `AS5600` IC
      - `#07` PCB swing windows (`6.65 <= |X_mod| <= 8.20`, `Y_mod in [Y_AXLE ± 5.30]`, `R = 0.50 mm`)
      - Symmetric snap-leg windows (`3.85 <= |X_mod| <= 5.85` = `2.00 mm`, `Y_mod in [Y_AXLE ± 5.43]`, `R = 0.45 mm`)
        locating the `1.80 mm` legs at `±0.10 mm` with all FR-4 shoulders `>= 0.80 mm`, 100% hidden beneath the covers.
    """
    cutter_mod = bd.extrude(build_sunk_plate_opening_face(0.0), amount=3.00).solids()[0]
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
    verify_cover_silhouette(cover_plate)
    verify_plate_opening_hidden()
    cover_rot = cover_plate.rotate(bd.Axis.Y, 90)
    cov_bb = cover_rot.bounding_box()
    cov_shift = (-cov_bb.center().X, -cov_bb.center().Y, -cov_bb.min.Z)
    cover_print = cover_rot.moved(bd.Location(cov_shift)).solids()[0]
    cover_print.label = "Wheel_Pyramid_Cover"
    verify_jlc3dp_part(
        cover_print,
        "wheel-cover",
        check_bores=True,
        check_wall_0p8=True,
        allowed_thin_pred=make_allowed_wheel_cover_thin(cov_shift),
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
    verify_click_swing(mod_sunk_parts)
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
        make_sensor_and_jst_smd_solids,
        RIGHT_SWITCHES,
        to_step_right,
    )

    right_case = bd.import_step(str(WORKSPACE / "cases" / "right.step")).solids()[0]
    right_case.label = "curcur40_Right_Case"

    sunk_main_pcb = build_main_pcb_solid(is_right=True)
    sunk_main_pcb.label = "curcur40_Right_Main_PCB"

    sunk_top_plate = build_top_plate_solid(is_right=True)
    sunk_top_plate.label = "curcur40_Right_Top_Plate"

    sunk_mount_step = [(cx_step - mx, cy_step - my) for mx, my in SUNK_MOUNT_PTS_MOD]
    main_jst_headers = make_sensor_and_jst_smd_solids()[:2]  # Right_PCB_rJ3_JST_SH & Right_PCB_rJ5_JST_SH

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
        *main_jst_headers, *keycaps, *sunk_screws, *sunk_dropped_parts,
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
