# -*- coding: utf-8 -*-
"""
Generate 3D CAD models (STEP & STL) for the Passive Magnetic Inertia Wheel Module
(`curcur40-inertia-wheel`, Method B: Cup-Shaped SUS304 Flywheel with Internal 9-Ball Axial Hub
and Ultra-Slim Rounded-Ear Carriage) and Standalone Evaluation Pod, and run automated
JLCCNC / JLC3DP DFM checks and zero-interference verification on `curcur40-right`.

Outputs:
  Manufacturing Parts (`cases/inertia_wheel/`):
    1. sus304-flywheel.step / .stl        (JLCCNC SUS304 Stainless Steel Cup Wheel, Ø16.80 x 5.46 mm, 2-way groove)
    2. ratchet-hub.step / .stl            (JLC3DP SLA Resin Internal Hub, Ø12.40 x 3.10 mm, 9x Ø2.00 mm axial pockets)
    3. wheel-carriage.step / .stl         (JLC3DP SLA Resin Slim Rounded-Ear Hinged Inner Carriage)
    4. wheel-base-frame.step / .stl       (JLC3DP SLA Resin, 17.60 x 17.60 mm Surface-Mount Base Frame)
    5. wheel-base-frame-sunk.step / .stl  (JLC3DP SLA Resin, Low-Profile Sunk Under-PCB Base Frame)
    6. eval-pod-stand.step / .stl         (JLC3DP SLA/MJF Desktop Stand for RP2040-Zero Carrier PCB)

  Verification Assemblies (`cases/assemblies/`):
    1. inertia-wheel-module-assembly.step
    2. inertia-wheel-module-sunk-assembly.step
    3. inertia-wheel-eval-pod-assembly.step
    4. curcur40-right-with-inertia-wheel.step      (Variant A: Surface-mount, zero PCB modification)
    5. curcur40-right-with-inertia-wheel-sunk.step (Variant B: Low-profile sunk + Cross-Slot Top Plate, wheel center = keycap center Z=+1.40mm)
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
# Core Geometric Parameters (Module Local Coordinates: F.Cu = Z_mod 0.00 mm)
#   - Variant A (Surface-mount): cz_fcu = -4.19 -> Wheel top Z = +14.76 mm (< +14.80 mm Trackball!)
#   - Variant B (Low-profile Sunk): cz_sunk = -9.15 -> Wheel center Z = +1.40 mm (exact Keycap center!),
#     Wheel top Z = +9.80 mm (+6.20 mm mouse-like protrusion), Top Plate at Z_mod = [+5.55, +7.15] mm!
# =============================================================================
MOD_XY = 17.60          # Fits inside 18.00x18.00 courtyard & 18.20x18.20 Top Plate cutout (+0.30 mm gap all around)
Y_AXLE = -0.10          # Wheel Ø16.80 -> Y in [-8.50, +8.30]
Z_AXLE = 10.55          # Sunk cz_sunk = -9.15 -> Z_global = +1.40 mm; Surface cz_fcu = -4.19 -> Z_top = +14.76 mm

WHEEL_OD = 16.80
WHEEL_R = WHEEL_OD / 2.0
WHEEL_W = 5.46          # Sleek 5.46 mm mouse-proportioned cup wheel: X in [-3.18, +2.28] (nearly centered in 1U!)
WHEEL_X_MIN = -3.18
WHEEL_X_MAX = 2.28
CUP_IN_R = 6.25         # Ø12.50 mm East cup cavity (3.30 mm deep: local Z in [2.16, 5.46] -> X in [-1.02, +2.28])
CUP_DEPTH = 3.30        # Outer SUS304 rim wall = 1.65..2.15 mm; West solid SUS304 web = 1.66..2.16 mm!

HUB_OD = 12.40          # Ø12.40 mm SLA resin hub nested 100% inside the Ø12.50 mm flywheel cup!
HUB_R = HUB_OD / 2.0
HUB_W = 3.10            # Seated at X in [-0.94, +2.16] (0.12 mm recessed inside +2.28 wheel rim -> 100% hidden!)
HUB_X_MIN = -0.94
HUB_X_MAX = 2.16
N_BALLS = 9             # 9x Ø2.00 mm SUJ2 steel balls in axial East-face pockets on R_orbit = 4.30 mm (all SLA walls >= 0.85 mm!)
R_BALL_ORBIT = 4.30
Z_BALL_LOCAL = 1.90     # Ball center Z in hub print coords (bottom floor 0.87 mm, top lip 0.854 mm >= 0.80 mm!)
BALL_R = 1.00

Z_MAG_ADJ = Z_AXLE - R_BALL_ORBIT  # +6.25 mm (= Z_global -2.90 mm in Sunk Variant, hidden below Top Plate Z = -2.00 mm!)

HINGE_Y = -6.85
HINGE_Z = 2.15


def build_sus304_flywheel_centered() -> bd.Solid:
    """
    Build Cup-Shaped SUS304 Stainless Steel Flywheel (`#01`) centered at origin with rotary axis along Z
    (for clean flat Z >= 0 export and JLCCNC turning/milling):
      - Outer diameter: Ø16.80 mm, Width (height): 7.80 mm (Z = 0.00 to 7.80 mm)
      - 36 axial finger-grip flutes around circumference (concave R = 0.80 mm -> Ø1.60 mm >= Ø1.50 mm!)
      - Central MX-Master-style 2-way circumferential groove (width 1.30 mm, depth 0.50 mm -> Ø15.80 mm root)
        for bare-metal styling OR optional Ø15x1.0 mm black silicone O-ring
      - East Cup Cavity (`Z = 3.90..7.80 mm`, `Ø12.50 mm` inner diameter, `3.90 mm` deep) that completely
        encloses `#02` 9-ball ratchet hub inside the wheel (`1.65..2.15 mm` thick outer SUS304 rim!)
      - West Bearing Clearance Recess (`Z = 0.00..0.90 mm`, `Ø6.40 mm` OD) with `Ø3.10 mm` inner-race contact boss
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

    # 3. Central 2-way O-ring / accent groove (Z = 3.25 to 4.55 mm, width 1.30 mm, root R = 7.90 mm)
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
    Build 3D-printed SLA Non-Conductive Internal Ratchet Hub (`#02`, `Z = 0.00 to 3.75 mm`):
      - Nested 100% coaxially inside `#01` SUS304 Flywheel's Ø12.50 x 3.90 mm cup cavity!
      - Outer diameter: Ø12.40 mm (R = 6.20 mm), Height = 3.75 mm
      - 9 axial snap-in spherical pockets opening on the +Z (East) face at R_orbit = 4.30 mm:
          - Sphere radius R = 1.03 mm at Z = 2.55 mm (bottom floor = 1.52 mm >= 0.80 mm!)
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
    (100% walls & steps >= 0.85 mm, all frame arms submerged below Top Plate Z_mod = 5.55 mm!):
      - North Cylindrical Hinge Barrel (`R = 1.92 mm`, `X in [-6.50, +6.50]`) at `(HINGE_Y=-6.85, HINGE_Z=2.15)`
      - G1-tangent West Hinge Arm (`X in [-5.10, -2.80]`, `Y in [-8.77, +3.35]`, `Z in [2.15, 5.15]`)
        + Low-Profile West Sensor Sub-PCB L-Ledge (`X in [-8.80, -5.10]`, `Z <= 5.15 mm`, hidden below Top Plate!)
      - Sleek Concentric Rounded West & East Bearing Ears (`Ø6.90 mm`, `R = 3.45 mm` around `(Y_AXLE, Z_AXLE)`,
        `Y in [-3.55, +3.35]`) — the ONLY carriage features rising gently above the Top Plate!
      - East Hinge Riser & South Silent-Switch Striker Arm (`Z <= 5.20 mm`, hidden 0.35 mm below Top Plate!)
      - Axial M2 Magnet Adjuster Bore (`Ø1.76 mm` along X at `(Y = -0.10, Z = +6.25 mm)`) through the lower
        East Bearing Stem facing `#02` Hub's 9 steel balls directly inside the East cup mouth!
    """
    parts = []

    # 1. North Cylindrical Hinge Barrel across X in [-6.45, +6.45] (R = 1.92 mm -> Y_min = -8.77, Z_min = 0.23, Z_max = 4.07)
    hinge_barrel = (
        bd.Cylinder(radius=1.92, height=12.90, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((-6.45, HINGE_Y, HINGE_Z)))
    )
    parts.append(hinge_barrel)

    # 2. G1-tangent West Hinge Arm (`X in [-5.35, -3.50]`, `Y in [-8.77, +3.35]`, `Z in [2.15, 5.15]`)
    west_arm = bd.Box(
        1.85, 12.12, 3.00,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-5.35, -8.77, HINGE_Z)))
    parts.append(west_arm)

    # 3. Sleek Rounded West Bearing Stem + Semicircular Cap (`X in [-5.35, -3.50]`, `Y in [-3.55, +3.35]`, R = 3.45 mm)
    west_stem = bd.Box(
        1.85, 6.90, Z_AXLE - 4.10,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-5.35, Y_AXLE - 3.45, 4.10)))
    west_cap = (
        bd.Cylinder(radius=3.45, height=1.85, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((-5.35, Y_AXLE, Z_AXLE)))
    )
    parts.extend([west_stem, west_cap])

    # 4. Submerged West Sensor Sub-PCB L-Ledge (`Z <= 5.15 mm` -> 100% hidden under Top Plate Z_mod = 5.55 mm!)
    west_pcb_bridge = bd.Box(
        2.60, 6.90, 1.75,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-7.95, Y_AXLE - 3.45, 3.40)))  # Z in [3.40, 5.15]
    west_pcb_ledge = bd.Box(
        0.85, 6.90, 0.88,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-8.80, Y_AXLE - 3.45, 3.40)))  # Z in [3.40, 4.28], 0.87 mm step to 5.15!
    parts.extend([west_pcb_bridge, west_pcb_ledge])

    # 5. Symmetrical G1-tangent East Hinge Arm (`X in [+2.65, +4.90]`, 0.37 mm East of #01 Wheel +2.28!, `Y in [-8.77, +2.25]`, `Z in [2.15, 5.23]`)
    east_arm = bd.Box(
        2.25, 11.02, 3.08,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((2.65, -8.77, HINGE_Z)))
    parts.append(east_arm)

    # 6. Submerged South-East Silent-Switch Striker Tab (`X in [+2.65, +6.45]`, coplanar East X=+6.45 with hinge_barrel!, `Y in [+2.25, +7.10]`, `Z in [4.38, 5.23]`)
    striker_tab = bd.Box(
        3.80, 4.85, 0.85,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((2.65, 2.25, 4.38)))
    parts.append(striker_tab)

    # 7. Sleek Rounded East Bearing Stem + Semicircular Cap (`X in [+2.65, +4.90]`, `Y in [-3.55, +3.35]`, R = 3.45 mm)
    east_stem = bd.Box(
        2.25, 6.90, Z_AXLE - 4.38,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((2.65, Y_AXLE - 3.45, 4.38)))
    east_cap = (
        bd.Cylinder(radius=3.45, height=2.25, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((2.65, Y_AXLE, Z_AXLE)))
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

    # 2) West MR52 Bearing Pocket: Ø5.04 mm press-fit bore through West Ear (X = -5.35 to -3.50)
    west_brg_seat = (
        bd.Cylinder(radius=2.52, height=2.40, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((-5.55, Y_AXLE, Z_AXLE)))
    )
    carriage = carriage - west_brg_seat

    # 3) East MR52 Bearing Pocket: Ø5.04 mm press-fit bore through East Ear (X = +2.65 to +4.90)
    east_brg_seat = (
        bd.Cylinder(radius=2.52, height=2.60, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((2.50, Y_AXLE, Z_AXLE)))
    )
    carriage = carriage - east_brg_seat

    # 4) Axial M2 Magnet Adjuster Bore: Ø1.76 mm (>= Ø1.50 mm!) along X through lower East Stem at (Y = Y_AXLE, Z = +6.25 mm)
    adj_bore = (
        bd.Cylinder(radius=0.88, height=3.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((2.40, Y_AXLE, Z_MAG_ADJ)))
    )
    carriage = carriage - adj_bore

    return carriage.solids()[0]


def build_wheel_base_frame() -> bd.Solid:
    """
    Build Stationary 17.60 x 17.60 mm Base Frame (`#04A`, `Z = 0.00 mm` sits flat on Main/Carrier PCB F.Cu):
      - Uniform 1.40 mm solid floor across Y in [-4.70, +8.80] (wheel bottom is Z = +2.15 mm -> 0.75 mm clearance!)
      - Open North hinge swing slot at X in [-6.70, +6.70], Y in [-8.80, -4.70] so Hinge Barrel swings freely
      - Two North Hinge Outer Ears at X in [-8.80, -6.70] and [+6.70, +8.80], Y in [-8.80, -4.70], Z in [0.00, 4.10]
        with Ø2.06 mm hinge pin bore at (HINGE_Y=-6.85, HINGE_Z=2.15)
      - Open South-East corner cutout (X in [+2.55, +8.80], Y in [+2.55, +8.80]) for PCB-mounted Kailh Silent Switch
      - Two M2 mounting screw holes (Ø2.10 mm through-holes) at (-6.50, +6.50) and (-0.50, +6.50)
    """
    base = bd.Box(
        MOD_XY, MOD_XY, 1.40,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    )

    hinge_slot = bd.Box(
        13.40, 4.30, 5.00,
        align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((0.00, -9.00, -1.00)))
    base = base - hinge_slot

    ear_l = bd.Box(
        2.10, 4.10, 4.10,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-8.80, -8.80, 0.00)))
    ear_r = bd.Box(
        2.10, 4.10, 4.10,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((6.70, -8.80, 0.00)))
    base = base + ear_l + ear_r

    sw_cut = bd.Box(
        6.60, 6.60, 6.00,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((2.55, 2.55, -1.00)))
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
    Build Low-Profile Sunk Base Frame (`#04B`) in assembled module coordinates (`Z_mod = 0.00 mm` corresponds
    to `Z_global = -9.15 mm`, placing rotary axle `Z_AXLE = 10.55 mm` at `Z_global = +1.40 mm` == exact
    Keycap vertical midpoint, and wheel top at `Z_global = +9.80 mm` == +6.20 mm mouse-like protrusion):
      - Continuous 1.20 mm bottom floor (`Z_mod = -1.20 .. 0.00 mm`) across 17.60 x 17.60 mm basket,
        supporting the Kailh Square Silent Switch directly inside the sunk SE pocket (`Ø3.20 mm` wire exit)
      - Raised 2.60 mm inner floor (`Z_mod = -1.20 .. +1.40 mm`) across `Y in [-4.70, +8.80]` outside SE pocket
      - Two North Hinge Outer Ears (`Z_mod = -1.20 .. +4.18 mm`) with `Ø2.06 mm` hinge pin bore
      - East Flange (`X in [+8.80, +14.90]`, `Y in [-4.70, +8.80]`) and North Lug (`X in [-4.70, +0.70]`,
        `Y in [-14.90, -8.80]`) rising from `Z_mod = -1.20` to `+3.34 mm` (seating against Main PCB B.Cu = +3.35 mm)
      - Three `Ø3.40 mm` integrated spacer posts at `SUNK_MOUNT_PTS_MOD` rising from `Z_mod = +3.34` to `+5.54 mm`
        (passing through `Ø3.70 mm` Main PCB holes to support Top Plate underside at `Z_global = -3.60 mm`),
        with `Ø1.60 mm` (>= Ø1.50 mm JLC3DP limit!) M2 screw bores!
    """
    base = bd.Box(
        MOD_XY, MOD_XY, 2.60,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((0.00, 0.00, -1.20)))

    hinge_slot = bd.Box(
        13.40, 4.30, 5.00,
        align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((0.00, -9.00, 0.00)))
    base = base - hinge_slot

    ear_l = bd.Box(
        2.10, 4.10, 5.38,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-8.80, -8.80, -1.20)))
    ear_r = bd.Box(
        2.10, 4.10, 5.38,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((6.70, -8.80, -1.20)))
    base = base + ear_l + ear_r

    sw_pocket = bd.Box(
        6.25, 6.25, 5.00,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((2.55, 2.55, 0.00)))
    base = base - sw_pocket

    east_flange = bd.Box(
        6.10, 13.50, 4.54,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((8.80, -4.70, -1.20)))

    north_lug = bd.Box(
        5.40, 6.10, 4.54,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-4.70, -14.90, -1.20)))
    base = base + east_flange + north_lug

    for mx, my in SUNK_MOUNT_PTS_MOD:
        post = bd.Cylinder(
            radius=1.70, height=2.20, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
        ).moved(bd.Location((mx, my, 3.34)))
        base = base + post

    hinge_bore = (
        bd.Cylinder(radius=1.03, height=22.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((0.0, HINGE_Y, HINGE_Z)))
    )
    base = base - hinge_bore

    sw_wire_hole = bd.Cylinder(
        radius=1.60, height=4.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)
    ).moved(bd.Location((5.70, 5.70, -0.60)))
    base = base - sw_wire_hole

    for mx, my in SUNK_MOUNT_PTS_MOD:
        sh = bd.Cylinder(
            radius=0.80, height=10.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)
        ).moved(bd.Location((mx, my, 2.00)))
        base = base - sh

    return base.solids()[0]


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


def assemble_module_parts(origin=(0.0, 0.0, 0.0), sunk: bool = False) -> list[bd.Shape]:
    """
    Build all physical parts of the Passive Magnetic Inertia Wheel Module in module coords,
    then shift by `origin`. When `sunk=True`, uses `wheel-base-frame-sunk`.
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

    # 3. Cup-Shaped SUS304 Flywheel (rotated +90 deg around Y: local Z [0..7.80] -> X [-2.65..+5.15])
    fw_raw = build_sus304_flywheel_centered()
    flywheel = fw_raw.rotate(bd.Axis.Y, 90).moved(bd.Location((WHEEL_X_MIN, Y_AXLE, Z_AXLE)))
    flywheel.label = "SUS304_Flywheel_Cup_16p8mm"

    # 4. Internal 9-Ball Resin Ratchet Hub (nested 100% inside flywheel cup at X [+1.30..+5.05]!)
    hub_raw = build_ratchet_hub_print_oriented()
    hub = hub_raw.rotate(bd.Axis.Y, 90).moved(bd.Location((HUB_X_MIN, Y_AXLE, Z_AXLE)))
    hub.label = "Ratchet_Hub_Internal_Resin"

    # 5. 9x Ø2.00 mm SUJ2 Steel Balls seated in axial hub pockets (X = HUB_X_MIN + Z_BALL_LOCAL = +3.85)
    x_balls = HUB_X_MIN + Z_BALL_LOCAL
    balls = []
    for i in range(N_BALLS):
        ang = math.radians(i * (360.0 / N_BALLS))
        # After rotating around +Y by +90 deg: local (bx, by, z_ball) -> (z_ball, by, -bx)
        bx = R_BALL_ORBIT * math.cos(ang)
        by_loc = R_BALL_ORBIT * math.sin(ang)
        by = Y_AXLE + by_loc
        bz = Z_AXLE - bx
        b = bd.Sphere(radius=0.99).moved(bd.Location((x_balls, by, bz)))
        b.label = f"Steel_Ball_2mm_{i+1:02d}"
        balls.append(b)

    # 6. Non-magnetic SUS304 Shaft Ø1.98 x 10.20 mm (X = -5.38 to +4.82)
    shaft = (
        bd.Cylinder(radius=0.99, height=10.20, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((-5.38, Y_AXLE, Z_AXLE)))
    )
    shaft.label = "SUS304_Axle_Shaft_2mm"

    # 7. 2x Miniature Degreased Bearings (MR52 / DDL-520 open: Ø2.04 ID x Ø5.00 OD x 2.00 W)
    brg_w = (
        bd.Cylinder(radius=2.49, height=1.98, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        - bd.Cylinder(radius=1.02, height=1.98, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    ).rotate(bd.Axis.Y, 90).moved(bd.Location((-5.33, Y_AXLE, Z_AXLE)))
    brg_w.label = "Bearing_MR52_West"

    brg_e = (
        bd.Cylinder(radius=2.49, height=2.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        - bd.Cylinder(radius=1.02, height=2.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    ).rotate(bd.Axis.Y, 90).moved(bd.Location((2.68, Y_AXLE, Z_AXLE)))
    brg_e.label = "Bearing_MR52_East"

    # 8. North Hinge Pin Ø1.98 x 17.20 mm at (HINGE_Y, HINGE_Z)
    hinge_pin = (
        bd.Cylinder(radius=0.99, height=17.20, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((0.0, HINGE_Y, HINGE_Z)))
    )
    hinge_pin.label = "Hinge_Pin_SUS304_2mm"

    # 9. Diametric Sensor Magnet Ø3.0 x 0.85 mm (X = -6.25 to -5.40) + Top-Side PCBA AS5600 SubPCB:
    #    - SubPCB 8.8x8.8x0.80 mm (snapped from 22x22mm breakaway frame; X = -8.75 to -7.95, Z = 4.30 to 13.10)
    #    - U1 AS5600-ASOT SOIC-8 (X = -7.94 to -6.59, Y = Y_AXLE ± 3.00, Z = 9.90 ± 2.45)
    #    - C1 (100nF 0402) & C2 (1uF 0402) on F.Cu at Z_mod = 6.25 mm (1.10 mm above west_pcb_bridge Z=5.15!)
    sens_mag = (
        bd.Cylinder(radius=1.50, height=0.85, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((-6.25, Y_AXLE, Z_AXLE)))
    )
    sens_mag.label = "Diametric_Magnet_3x1mm"

    as5600_pcb = bd.Box(
        0.80, 8.80, 8.80,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((-8.75, Y_AXLE, 4.30)))
    as5600_pcb.label = "AS5600_Sensor_SubPCB"

    as5600_ic = bd.Box(
        1.35, 6.00, 4.90,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER),
    ).moved(bd.Location((-7.94, Y_AXLE, 9.90)))
    as5600_ic.label = "AS5600_SOIC8_IC"

    as5600_c1 = bd.Box(
        0.55, 1.00, 0.50,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER),
    ).moved(bd.Location((-7.94, Y_AXLE - 2.30, 6.25)))
    as5600_c1.label = "AS5600_Cap_C1_100nF"

    as5600_c2 = bd.Box(
        0.55, 1.00, 0.50,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER),
    ).moved(bd.Location((-7.94, Y_AXLE + 0.10, 6.25)))
    as5600_c2.label = "AS5600_Cap_C2_1uF"

    # 10. Kailh Square Silent Micro Switch (6.2 x 6.2 x 3.8 mm body + 0.46 mm red button) at (+5.70, +5.70)
    sw_body = bd.Box(
        6.20, 6.20, 3.80,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((5.70, 5.70, 0.02)))
    sw_btn = bd.Cylinder(
        radius=1.30, height=0.46, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
    ).moved(bd.Location((5.70, 5.70, 3.82)))
    silent_sw = (sw_body + sw_btn).solids()[0]
    silent_sw.label = "Kailh_Silent_Switch_6x6x4p3"

    # 11. Axial M2 Magnet Gap Adjustment Screw + Ø1.6 x 1.2 mm Ratchet Magnet in lower East Stem
    #     at (Y = Y_AXLE, Z = +6.25 mm = Z_global -2.90 mm, submerged below Top Plate!)
    m2_adj = (
        bd.Cylinder(radius=0.82, height=2.85, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((2.40, Y_AXLE, Z_MAG_ADJ)))
    )
    m2_adj.label = "M2_Magnet_Adjuster_And_NdFeB"

    raw_items = [
        base, carriage, flywheel, hub, shaft, brg_w, brg_e,
        hinge_pin, sens_mag, as5600_pcb, as5600_ic, as5600_c1, as5600_c2,
        silent_sw, m2_adj,
        *balls,
    ]

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


def _build_sunk_top_plate_cross_cutter(cx_step: float, cy_step: float) -> bd.Solid:
    """
    Build sleek Cross-Slot Top Plate cutter at `(cx_step, cy_step)` that hides all 4 corner
    mechanism zones (North Hinge Barrel/Risers, South-East Kailh Silent Switch & Striker)
    under solid FR-4 Top Plate while allowing 1-piece bottom-up insertion of the assembled module!
    """
    with bd.BuildSketch(bd.Plane.XY) as sk_w:
        with bd.Locations([(-0.45, Y_AXLE)]):
            bd.RectangleRounded(6.60, 17.80, 0.80)
    with bd.BuildSketch(bd.Plane.XY) as sk_west:
        with bd.Locations([(-5.85, Y_AXLE)]):
            bd.RectangleRounded(6.80, 9.80, 0.80)
    with bd.BuildSketch(bd.Plane.XY) as sk_east:
        with bd.Locations([(3.65, Y_AXLE)]):
            bd.RectangleRounded(4.50, 7.90, 0.80)

    cross_mod = (
        bd.extrude(sk_w.sketch, amount=3.00)
        + bd.extrude(sk_west.sketch, amount=3.00)
        + bd.extrude(sk_east.sketch, amount=3.00)
    ).solids()[0]
    return cross_mod.rotate(bd.Axis.Z, 180).moved(bd.Location((cx_step, cy_step, -4.50))).solids()[0]


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

    # 3) Slim Rounded-Ear Hinged Carriage (flat East face X = +8.75 placed on Z = 0.0000 print bed!)
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

    mod_sunk_parts = assemble_module_parts(origin=(0.0, 0.0, 0.0), sunk=True)
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
        carrier_pcb = carrier_pcb - bd.Cylinder(radius=1.10, height=5.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(
            bd.Location((bx, by, 4.00))
        )
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

    print("\n=== 3. Verifying Zero-Modification Drop-In Fit on curcur40-right (Type A) ===")
    cx_step, cy_step, cz_fcu = 28.5750, -57.1500, -4.19
    mod_local = bd.Compound(children=assemble_module_parts(origin=(0.0, 0.0, 0.0))).rotate(bd.Axis.Z, 180).moved(
        bd.Location((cx_step, cy_step, cz_fcu))
    )
    dropped_parts = list(mod_local.solids())
    for idx, s in enumerate(dropped_parts):
        s.label = mod_parts[idx].label

    sys.path.insert(0, str(WORKSPACE / "scripts"))
    from generate_full_assembly import (
        build_main_pcb_solid,
        build_top_plate_solid,
        make_keycap_solid,
        RIGHT_SWITCHES,
        to_step_right,
    )

    right_case = bd.import_step(str(WORKSPACE / "cases" / "right.step")).solids()[0]
    right_case.label = "curcur40_Right_Case_Unmodified"

    right_main_pcb = build_main_pcb_solid(is_right=True)
    right_main_pcb.label = "curcur40_Right_Main_PCB"

    top_plate_ref = build_top_plate_solid(is_right=True)
    top_plate_ref.label = "curcur40_Right_Top_Plate_Unmodified"

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

    fit_check_parts = [right_case, right_main_pcb, top_plate_ref, tb_cup, tb_ball, *keycaps, *dropped_parts]
    verify_zero_overlap(fit_check_parts, "curcur40_Right_DropIn_Check")

    static_labels = {"Wheel_Base_Frame", "Hinge_Pin_SUS304_2mm", "Kailh_Silent_Switch_6x6x4p3"}
    d_plate_static = min(closest_points(s, top_plate_ref).distance for s in dropped_parts if s.label in static_labels)
    d_plate_moving = min(closest_points(s, top_plate_ref).distance for s in dropped_parts if s.label not in static_labels)
    d_rexsw2 = min(closest_points(s, rexsw2_cap).distance for s in dropped_parts)
    assert d_plate_static >= 0.20, f"Static Base/Switch vs Top Plate clearance {d_plate_static:.4f} mm < 0.20 mm!"
    assert d_plate_moving >= 0.30, f"Moving Carriage/Wheel vs Top Plate clearance {d_plate_moving:.4f} mm < 0.30 mm!"
    assert d_rexsw2 >= 1.00, f"rEXSW2 Keycap clearance {d_rexsw2:.4f} mm < 1.00 mm!"
    print(f"         -> Static Base/Switch clearance to 18.20mm Top Plate = {d_plate_static:.3f} mm (>= 0.20 mm)")
    print(f"         -> Moving Parts clearance to 18.20mm Top Plate       = {d_plate_moving:.3f} mm (>= 0.30 mm)")
    print(f"         -> Clearance to South Keycap (rEXSW2)                = {d_rexsw2:.3f} mm (>= 1.00 mm)")

    dropin_asm = bd.Compound(label="curcur40_Right_With_Inertia_Wheel", children=fit_check_parts)
    bd.export_step(dropin_asm, str(ASSEMBLIES_DIR / "curcur40-right-with-inertia-wheel.step"))

    print("\n=== 4. Verifying Low-Profile Cup-Wheel Sunk Variant on curcur40-right (Type B) ===")
    cz_sunk = 1.40 - Z_AXLE  # -9.15 mm -> Wheel Center = +1.40 mm (exact Keycap midpoint!), Wheel Top = +9.80 mm!
    mod_sunk_local = bd.Compound(children=assemble_module_parts(origin=(0.0, 0.0, 0.0), sunk=True)).rotate(
        bd.Axis.Z, 180
    ).moved(bd.Location((cx_step, cy_step, cz_sunk)))
    sunk_dropped_parts = list(mod_sunk_local.solids())
    for idx, s in enumerate(sunk_dropped_parts):
        s.label = mod_sunk_parts[idx].label

    # Build Right Main PCB with 18.50x18.50mm inner cutout + 3x Ø3.70mm spacer holes (outer outline 100% unchanged!)
    with bd.BuildSketch(bd.Plane.XY.offset(-6.50)) as sk_pcb_win:
        with bd.Locations([(cx_step, cy_step)]):
            bd.RectangleRounded(18.50, 18.50, 0.50)
    sunk_main_pcb = right_main_pcb - bd.extrude(sk_pcb_win.sketch, amount=3.00)
    sunk_mount_step = [(cx_step - mx, cy_step - my) for mx, my in SUNK_MOUNT_PTS_MOD]
    for sx_m, sy_m in sunk_mount_step:
        sunk_main_pcb = sunk_main_pcb - bd.Cylinder(
            radius=1.85, height=4.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
        ).moved(bd.Location((sx_m, sy_m, -6.50)))
    sunk_main_pcb = sunk_main_pcb.solids()[0]
    sunk_main_pcb.label = "curcur40_Right_Main_PCB_SunkCutout"

    # Build Right Top Plate: first fill the old 18.20x18.20 square hole back into solid plate, then cut
    # the sleek Cross-Slot (`_build_sunk_top_plate_cross_cutter`) so all 4 corner mechanism zones are hidden!
    plate_fill = bd.Box(
        18.60, 18.60, 1.60, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
    ).moved(bd.Location((cx_step, cy_step, -3.60)))
    sunk_top_plate = (top_plate_ref + plate_fill) - _build_sunk_top_plate_cross_cutter(cx_step, cy_step)
    for sx_m, sy_m in sunk_mount_step:
        sunk_top_plate = sunk_top_plate - bd.Cylinder(
            radius=1.20, height=4.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
        ).moved(bd.Location((sx_m, sy_m, -4.50)))
    sunk_top_plate = sunk_top_plate.solids()[0]
    sunk_top_plate.label = "curcur40_Right_Top_Plate_SunkCrossSlot"

    sunk_screws = []
    for idx_m, (sx_m, sy_m) in enumerate(sunk_mount_step):
        sc_head = bd.Cylinder(
            radius=2.00, height=0.80, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
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

    sunk_static_labels = {"Wheel_Base_Frame_Sunk", "Hinge_Pin_SUS304_2mm", "Kailh_Silent_Switch_6x6x4p3"}
    sunk_fw = [s for s in sunk_dropped_parts if s.label == "SUS304_Flywheel_Cup_16p8mm"][0]
    fw_bb = sunk_fw.bounding_box()
    d_case_floor = min(closest_points(s, right_case).distance for s in sunk_dropped_parts)
    d_sunk_plate_moving = min(closest_points(s, sunk_top_plate).distance for s in sunk_dropped_parts if s.label not in sunk_static_labels)
    d_sunk_pcb_moving = min(closest_points(s, sunk_main_pcb).distance for s in sunk_dropped_parts if s.label not in sunk_static_labels)
    d_sunk_rexsw2 = min(closest_points(s, rexsw2_cap).distance for s in sunk_dropped_parts)
    assert d_case_floor >= 2.00, f"Sunk module vs Right Case clearance {d_case_floor:.3f} mm < 2.00 mm!"
    assert d_sunk_plate_moving >= 0.30, f"Sunk moving parts vs Top Plate {d_sunk_plate_moving:.3f} mm < 0.30 mm!"
    assert d_sunk_pcb_moving >= 0.30, f"Sunk moving parts vs Main PCB {d_sunk_pcb_moving:.3f} mm < 0.30 mm!"
    assert d_sunk_rexsw2 >= 1.00, f"Sunk module vs rEXSW2 Keycap {d_sunk_rexsw2:.3f} mm < 1.00 mm!"
    print(f"         -> Sunk Cup-Flywheel Z span = [{fw_bb.min.Z:+.2f}, {fw_bb.max.Z:+.2f}] mm, Center Z = {0.5*(fw_bb.min.Z+fw_bb.max.Z):+.2f} mm (Keycap Center = +1.40 mm!)")
    print(f"         -> Clearance to unmodified Right Case floor/walls = {d_case_floor:.3f} mm")
    print(f"         -> Moving Parts clearance to Cross-Slot Top Plate / Main PCB = {d_sunk_plate_moving:.3f} / {d_sunk_pcb_moving:.3f} mm (>= 0.30 mm)")
    print(f"         -> Clearance to South Keycap (rEXSW2)             = {d_sunk_rexsw2:.3f} mm (>= 1.00 mm)")

    sunk_asm = bd.Compound(label="curcur40_Right_With_Inertia_Wheel_Sunk", children=sunk_fit_parts)
    bd.export_step(sunk_asm, str(ASSEMBLIES_DIR / "curcur40-right-with-inertia-wheel-sunk.step"))
    print("\nAll Passive Cup-Flywheel Inertia Wheel 3D models generated and verified successfully!")


if __name__ == "__main__":
    main()
