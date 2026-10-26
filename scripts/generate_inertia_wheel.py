# -*- coding: utf-8 -*-
"""
Generate 3D CAD models (STEP & STL) for the Passive Magnetic Inertia Wheel Module
(`curcur40-inertia-wheel`) and Standalone Evaluation Pod, and run automated
JLCCNC / JLC3DP DFM checks and zero-interference verification on `curcur40-right`.

Outputs:
  Manufacturing Parts (`cases/inertia_wheel/`):
    1. sus304-flywheel.step / .stl          (JLCCNC SUS304 Stainless Steel, Ø16.80 x 5.60 mm, 2-way groove)
    2. ratchet-hub-11ball.step / .stl       (JLC3DP SLA Resin, Ø12.40 x 3.75 mm, 11x Ø2.00 mm ball pockets)
    3. wheel-carriage.step / .stl           (JLC3DP SLA Resin, Unitized Hinged Inner Carriage)
    4. wheel-base-frame.step / .stl         (JLC3DP SLA Resin, 17.60 x 17.60 mm Surface-Mount Base Frame)
    5. wheel-base-frame-sunk.step / .stl    (JLC3DP SLA Resin, Low-Profile Sunk Under-PCB Base Frame)
    6. eval-pod-stand.step / .stl           (JLC3DP SLA/MJF Desktop Stand for RP2040-Zero Carrier PCB)
    7. wheel-shroud-cover-eval.step / .stl  (JLC3DP SLA/MJF Optional Mouse-Style Shroud Cover `#20A` for Eval Pod)
    8. wheel-shroud-cover-sunk.step / .stl  (JLC3DP SLA/MJF Optional Mouse-Style Shroud Cover `#20B` for Sunk Variant)

  Verification Assemblies (`cases/assemblies/`):
    1. inertia-wheel-module-assembly.step
    2. inertia-wheel-module-sunk-assembly.step
    3. inertia-wheel-eval-pod-assembly.step
    4. inertia-wheel-eval-pod-covered-assembly.step
    5. curcur40-right-with-inertia-wheel.step              (Variant A: Surface-mount, zero PCB modification)
    6. curcur40-right-with-inertia-wheel-sunk.step         (Variant B: Low-profile sunk, wheel center = keycap center Z=+1.40mm)
    7. curcur40-right-with-inertia-wheel-sunk-covered.step (Variant B + Shroud Cover `#20B`, mouse-style hidden hub/carriage)
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
# Note: curcur40 Global Z = Z_mod - 4.20 mm (since Right Main PCB F.Cu = -4.20 mm)
# =============================================================================
MOD_XY = 17.60          # Fits inside 18.00x18.00 courtyard & 18.20x18.20 Top Plate cutout (+0.30 mm gap all around)
Y_AXLE = -0.10          # Wheel Ø16.80 -> Y in [-8.50, +8.30] (passes straight through ±9.10 mm plate cutout!)
Z_AXLE = 10.30          # Global Z = +6.10 mm -> Wheel top Global Z = +14.50 mm (< +14.80 mm Trackball!)

WHEEL_OD = 16.80
WHEEL_R = WHEEL_OD / 2.0
WHEEL_W = 5.60          # X in [-3.00, +2.60]
WHEEL_X_MIN = -3.00
WHEEL_X_MAX = 2.60

HUB_OD = 12.40
HUB_R = HUB_OD / 2.0
HUB_W = 3.75            # X in [+2.65, +6.40] -> axial wall around R=1.03 pocket is 1.875 - 1.03 = 0.845 mm (>= 0.80 mm!)
HUB_X_MIN = 2.65
HUB_X_MAX = 6.40
N_BALLS = 11            # 11x Ø2.00 mm SUJ2 steel balls on R_orbit = 5.10 mm (inter-pocket wall = 0.814 mm >= 0.80 mm!)
R_BALL_ORBIT = 5.10
BALL_R = 1.00

HINGE_Y = -6.85
HINGE_Z = 2.15


def build_sus304_flywheel_centered() -> bd.Solid:
    """
    Build SUS304 Stainless Steel Flywheel centered at origin with rotary axis along Z
    (for clean flat Z >= 0 export and JLCCNC turning/milling):
      - Outer diameter: Ø16.80 mm, Height (width): 5.60 mm (Z = 0.00 to 5.60 mm)
      - 36 shallow axial finger-grip flutes around circumference (R_flute = 0.45 mm, depth 0.16 mm)
      - Central MX-Master-style 2-way circumferential groove (width 1.30 mm, depth 0.50 mm -> Ø15.80 mm root)
        for bare-metal styling OR optional Ø15x1.0 mm black silicone O-ring
      - Recessed bearing clearance pockets on both faces (Ø6.40 mm x 1.15 mm deep) with
        central Ø3.00 mm inner-race bosses (protruding to Z = 0.00 and Z = 5.60 mm)
      - Shaft bore: Ø2.02 mm through-hole
    """
    w = bd.Cylinder(
        radius=WHEEL_R,
        height=WHEEL_W,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    )

    # 1. Outer edge chamfers (0.35 mm) for comfortable finger feel
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

    # 3. Central 2-way O-ring / accent groove (Z = 2.15 to 3.45 mm, width 1.30 mm, root R = 7.90 mm)
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

    # 4. Recessed face pockets (Ø12.0 mm decorative/weight-rim pocket 0.90 mm deep, leaving thick rim + Ø3.0 mm inner-race boss!)
    for z0 in (-0.10, WHEEL_W - 0.90):
        h_cut = 1.00
        ring_out = bd.Cylinder(
            radius=5.60,
            height=h_cut,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((0, 0, z0)))
        ring_in = bd.Cylinder(
            radius=1.55,  # Ø3.10 mm central inner-race boss!
            height=h_cut,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((0, 0, z0)))
        w = w - (ring_out - ring_in)

    # 5. Central Ø2.02 mm shaft bore
    bore = bd.Cylinder(
        radius=1.01,
        height=WHEEL_W + 2.0,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((0, 0, -1.0)))
    w = w - bore
    return w.solids()[0]


def build_ratchet_hub_print_oriented() -> bd.Solid:
    """
    Build 3D-printed SLA Non-Conductive Resin Ratchet Hub (`Z = 0.00 to 3.75 mm`):
      - Outer diameter: Ø12.40 mm (R = 6.20 mm), Height = 3.75 mm
      - 11 snap-in spherical pockets at Z = 1.875 mm, R_orbit = 5.10 mm:
          - Sphere radius R = 1.03 mm (strictly inside R = 6.20 mm outer cylinder: 5.10 + 1.03 = 6.13 < 6.20 mm!)
          - Snap-in entrance throat Ø1.94 mm (>= Ø1.50 mm JLC3DP min bore!)
          - Inter-pocket wall thickness = 2*5.10*sin(16.36 deg) - 2.06 = 0.814 mm (>= 0.80 mm!)
      - Central shaft bore: Ø2.00 mm snug press-fit
    """
    outer_cyl = bd.Cylinder(
        radius=HUB_R,
        height=HUB_W,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    )
    hub = outer_cyl

    z_mid = HUB_W / 2.0
    # Build one clean single-solid pocket+throat cutter with orthogonal OpenCascade seams (Sphere poles ±Z, Cylinder axis +Y)
    base_cutter = (
        bd.Sphere(radius=1.03)
        + bd.Cylinder(radius=0.97, height=2.20, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.X, -90)
    ).solids()[0]
    for i in range(N_BALLS):
        ang_deg = i * (360.0 / N_BALLS) + 15.0
        ang = math.radians(ang_deg)
        bx = R_BALL_ORBIT * math.cos(ang)
        by = R_BALL_ORBIT * math.sin(ang)
        # Local +Y of base_cutter points radially outward when rotated by (ang_deg - 90) around Z!
        cutter_i = base_cutter.rotate(bd.Axis.Z, ang_deg - 90.0).moved(bd.Location((bx, by, z_mid)))
        hub = hub - cutter_i

    # Intersect with outer cylinder as belt-and-suspenders guard against any B-rep boolean outer cap artifact
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
    Build Unitized Hinged Inner Carriage in assembled module coordinates (100% walls & steps >= 0.85 mm):
      - North Hinge Cylindrical Barrel (`R = 1.92 mm`, `X in [-6.50, +6.45]`) at `(HINGE_Y=-6.85, HINGE_Z=2.15)`
        giving 0.90 mm wall thickness all 360 deg around the Ø2.04 mm hinge pin bore!
      - G1-tangent Left & Right Hinge Risers (`Y_min = -8.77`, `Z >= 2.15`) eliminating any tangent step/wedge!
      - West Bearing Pillar (`X in [-5.45, -3.10]`, `Y in [-5.30, +5.10]`, `Z in [4.50, 13.80]`, `Ø5.04 mm` MR52 bore)
        + West AS5600 Sensor PCB Cradle (`X in [-7.95, -5.45]`, `0.93 mm` clearance from bearing bore)
      - North-East M2 Magnet Adjuster Riser (`X in [+2.75, +6.45]`, `Y in [-8.77, -6.15]`, `Z in [2.15, 7.55]`)
        with `Ø1.76 mm` M2 screw/magnet bore at `(X = +4.525, Z = +5.65)` (all walls >= 0.895 mm!)
      - East Bearing Pillar & South Silent-Switch Striker Arm (`X in [+6.45, +8.75]`, `Z in [5.22, 13.80]`)
        with `0.90 mm` tall actuator nub (`Z = 4.32..5.22 mm`) centered over Kailh Silent switch `(+5.75, +5.75)`!
    """
    parts = []

    # 1. North Cylindrical Hinge Barrel across X in [-6.50, +6.50] (R = 1.92 mm -> Y_min = -8.77, Z_min = 0.23)
    hinge_barrel = (
        bd.Cylinder(radius=1.92, height=13.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((-6.50, HINGE_Y, HINGE_Z)))
    )
    parts.append(hinge_barrel)

    # 2. G1-tangent Left Hinge Riser (`X in [-5.45, -3.10]`, flush X with West Bearing Pillar!, `Y in [-8.77, -3.55]`, `Z in [2.15, 6.30]`)
    left_riser = bd.Box(
        2.35, 5.22, 4.15,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-5.45, -8.77, HINGE_Z)))
    parts.append(left_riser)

    # 3. West Bearing Pillar (`X in [-5.45, -3.10]`, `Y in [-5.30, +5.10]`, `Z in [4.50, 13.80]`)
    west_pillar = bd.Box(
        2.35, 10.40, 9.30,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-5.45, -5.30, 4.50)))
    parts.append(west_pillar)

    # 4. West Sensor PCB Cradle (`X in [-7.95, -5.45]`, Y arms at [-5.30, -3.55] and [+3.35, +5.10] -> >= 0.93 mm from Ø5.04 bearing bore!)
    west_pcb_bot = bd.Box(
        2.50, 10.40, 1.80,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-7.95, -5.30, 4.50)))
    west_pcb_north = bd.Box(
        2.50, 1.75, 9.30,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-7.95, -5.30, 4.50)))
    west_pcb_south = bd.Box(
        2.50, 1.75, 9.30,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-7.95, 3.35, 4.50)))
    parts.extend([west_pcb_bot, west_pcb_north, west_pcb_south])

    # 5. G1-tangent North-East M2 Magnet Adjuster Riser (`X in [+2.75, +6.50]`, `Y in [-8.77, -6.15]`, `Z in [2.15, 7.55]`)
    right_riser = bd.Box(
        3.75, 2.62, 5.40,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((2.75, -8.77, HINGE_Z)))
    parts.append(right_riser)

    # 6. East Bridge (`X in [+2.75, +8.75]`, `Y in [-8.77, -6.15]`, `Z in [5.22, 7.55]`, flush with right_riser & east_arm!)
    east_neck = bd.Box(
        6.00, 2.62, 2.33,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((2.75, -8.77, 5.22)))
    parts.append(east_neck)

    # 7. East Bearing Pillar + South Silent-Switch Striker Arm (`X in [+6.50, +8.75]`, clears Hub X_max=6.40 by 0.10 mm!)
    east_arm = bd.Box(
        2.25, 17.32, 2.33,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((6.50, -8.77, 5.22)))  # Y=[-8.77, +8.55], Z=[5.22, 7.55]
    east_pillar = bd.Box(
        2.25, 9.40, 8.58,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((6.50, -4.80, 5.22)))  # Y=[-4.80, +4.60], Z=[5.22, 13.80]
    # Solid Striker Block (`X in [+5.10, +8.75]`, `Y in [+5.10, +8.55]`, `Z in [4.32, 6.15]`):
    # Clears Hub/Balls by +0.50 mm (`hypot(5.20, 4.15) = 6.65 mm > 6.15 mm`), clears switch body (Z=3.82) by 0.50 mm,
    # and touches central red switch actuator button (`(+5.70, +5.70)`, Z=4.28) with all steps >= 0.90 mm!
    striker_block = bd.Box(
        3.65, 3.45, 1.83,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((5.10, 5.10, 4.32)))
    parts.extend([east_arm, east_pillar, striker_block])

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

    # 2) West MR52 Bearing Pocket: clean Ø5.04 mm press-fit bore straight through West Pillar (X = -5.45 to -3.10)
    west_brg_seat = (
        bd.Cylinder(radius=2.52, height=3.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((-5.60, Y_AXLE, Z_AXLE)))
    )
    carriage = carriage - west_brg_seat

    # 3) East MR52 Bearing Pocket: clean Ø5.04 mm press-fit bore straight through East Pillar (X = +6.45 to +8.75)
    east_brg_seat = (
        bd.Cylinder(radius=2.52, height=3.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((6.30, Y_AXLE, Z_AXLE)))
    )
    carriage = carriage - east_brg_seat

    # 4) North-East M2 Magnet Adjuster Bore: Ø1.76 mm (>= Ø1.50 mm!) along Y through right_riser at (X = +4.525, Z = +5.65)
    adj_bore = (
        bd.Cylinder(radius=0.88, height=5.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.X, -90)
        .moved(bd.Location((4.525, -9.00, 5.65)))
    )
    carriage = carriage - adj_bore

    return carriage.solids()[0]


def build_wheel_base_frame() -> bd.Solid:
    """
    Build Stationary 17.60 x 17.60 mm Base Frame (`Z = 0.00 mm` sits flat on Main/Carrier PCB F.Cu):
      - Uniform 1.40 mm solid floor across Y in [-4.70, +8.80] (wheel bottom is Z = +1.90 mm -> 0.50 mm clearance!)
      - Open North hinge swing slot at X in [-6.70, +6.70], Y in [-8.80, -4.70] so Hinge Barrel (Z_min = +0.23 mm) swings freely
      - Two North Hinge Outer Ears at X in [-8.80, -6.70] and [+6.70, +8.80], Y in [-8.80, -4.70], Z in [0.00, 4.10]
        with Ø2.06 mm hinge pin bore at (HINGE_Y=-6.85, HINGE_Z=2.15) (all walls 0.92..1.12 mm >= 0.80 mm!)
      - Open South-East 6.25 x 6.25 mm corner cutout (X in [+2.55, +8.80], Y in [+2.55, +8.80]) for PCB-mounted Kailh Silent Switch
      - Two M2 mounting screw holes (Ø2.10 mm through-holes) at (-6.50, +6.50) and (-0.50, +6.50) (all walls >= 1.25 mm!)
    """
    base = bd.Box(
        MOD_XY, MOD_XY, 1.40,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    )

    # Cut North Hinge Barrel clearance slot (`X in [-6.70, +6.70]`, `Y in [-9.00, -4.70]`)
    hinge_slot = bd.Box(
        13.40, 4.30, 5.00,
        align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((0.00, -9.00, -1.00)))
    base = base - hinge_slot

    # North Hinge Outer Ears (`X in [-8.80, -6.70]` & `[+6.70, +8.80]`, `Y in [-8.80, -4.70]`, `Z in [0.00, 4.10]`)
    ear_l = bd.Box(
        2.10, 4.10, 4.10,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-8.80, -8.80, 0.00)))
    ear_r = bd.Box(
        2.10, 4.10, 4.10,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((6.70, -8.80, 0.00)))
    base = base + ear_l + ear_r

    # Cut South-East corner opening for Kailh Square Silent Switch (6.0 x 6.0 mm centered at (+5.75, +5.75))
    sw_cut = bd.Box(
        6.60, 6.60, 6.00,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((2.55, 2.55, -1.00)))
    base = base - sw_cut

    # Cut Hinge Pin Bore Ø2.06 mm through both North Hinge Ears
    hinge_bore = (
        bd.Cylinder(radius=1.03, height=22.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((0.0, HINGE_Y, HINGE_Z)))
    )
    base = base - hinge_bore

    # Cut two Ø2.10 mm M2 mounting screw holes at (-6.50, +6.50) and (-0.50, +6.50)
    for mx, my in [(-6.50, 6.50), (-0.50, 6.50)]:
        mh = bd.Cylinder(
            radius=1.05, height=10.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)
        ).moved(bd.Location((mx, my, 2.0)))
        base = base - mh

    return base.solids()[0]


# Sunk-variant 3-point M2 mounting boss coordinates in module local XY:
# After 180 deg Z-rotation onto curcur40-right rEXSW1 (14.2875, 0.0000):
#   W1 (+12.20, -1.90) -> PCB dx=-12.20, dy=-1.90 (open inner-West margin, keycap-free)
#   W2 (+12.20, +5.80) -> PCB dx=-12.20, dy=+5.80 (open inner-West margin, keycap-free)
#   W3 (-2.00, -12.20) -> PCB dx=+2.00,  dy=-12.20 (open North margin, keycap-free)
SUNK_MOUNT_PTS_MOD = [
    (12.20, -1.90),
    (12.20, 5.80),
    (-2.00, -12.20),
]


def build_wheel_base_frame_sunk_assembled() -> bd.Solid:
    """
    Build Low-Profile Sunk Base Frame in assembled module coordinates (`Z_mod = 0.00 mm` corresponds
    to `Z_global = -8.90 mm`, placing rotary axle `Z_AXLE = 10.30 mm` at `Z_global = +1.40 mm` == exact
    Keycap vertical midpoint, and wheel top at `Z_global = +9.80 mm` == +6.20 mm mouse-like protrusion):
      - Continuous 1.20 mm bottom floor (`Z_mod = -1.20 .. 0.00 mm`) across 17.60 x 17.60 mm basket,
        supporting the Kailh Square Silent Switch directly inside the sunk SE pocket (`Ø3.20 mm` wire exit)
      - Raised 2.60 mm inner floor (`Z_mod = -1.20 .. +1.40 mm`) across `Y in [-4.70, +8.80]` outside SE pocket
      - Two North Hinge Outer Ears (`Z_mod = -1.20 .. +4.10 mm`) with `Ø2.06 mm` hinge pin bore
      - East Flange (`X in [+8.80, +14.90]`, `Y in [-7.70, +7.70]`) and North Lug (`X in [-4.70, +0.70]`,
        `Y in [-14.90, -8.80]`) rising from `Z_mod = -1.20` to `+3.09 mm` (seating against Main PCB B.Cu = +3.10 mm)
      - Three `Ø3.40 mm` integrated spacer posts at `SUNK_MOUNT_PTS_MOD` rising from `Z_mod = +3.09` to `+5.29 mm`
        (passing through `Ø3.70 mm` Main PCB holes to support Top Plate underside at `Z_global = -3.60 mm`),
        with `Ø1.60 mm` (>= Ø1.50 mm JLC3DP limit!) M2 screw bores!
    """
    # 1. Main 17.60 x 17.60 mm basket (`Z_mod = -1.20 .. +1.40 mm` = 2.60 mm height)
    base = bd.Box(
        MOD_XY, MOD_XY, 2.60,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((0.00, 0.00, -1.20)))

    # 2. Recess North Hinge Barrel swing slot down to `Z_mod = 0.00 mm` (leaving 1.20 mm solid bottom floor!)
    hinge_slot = bd.Box(
        13.40, 4.30, 5.00,
        align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((0.00, -9.00, 0.00)))
    base = base - hinge_slot

    # 3. North Hinge Outer Ears (`X in [-8.80, -6.70]` & `[+6.70, +8.80]`, `Y in [-8.80, -4.70]`, `Z in [-1.20, +4.10]`)
    ear_l = bd.Box(
        2.10, 4.10, 5.30,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-8.80, -8.80, -1.20)))
    ear_r = bd.Box(
        2.10, 4.10, 5.30,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((6.70, -8.80, -1.20)))
    base = base + ear_l + ear_r

    # 4. Recess South-East Switch Pocket down to `Z_mod = 0.00 mm` (supporting Kailh Silent Switch on 1.20 mm floor!)
    sw_pocket = bd.Box(
        6.25, 6.25, 5.00,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((2.55, 2.55, 0.00)))
    base = base - sw_pocket

    # 5. East Under-PCB Mounting Flange (`X in [+8.80, +14.90]`, `Y in [-4.70, +8.80]`, `Z in [-1.20, +3.09]`)
    #    Starts at Y = -4.70 (flush with ear_r South face), leaving East side of Hinge Pin Bore 100% unobstructed!
    east_flange = bd.Box(
        6.10, 13.50, 4.29,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((8.80, -4.70, -1.20)))

    # 6. North Under-PCB Mounting Lug (`X in [-4.70, +0.70]`, `Y in [-14.90, -8.80]`, `Z in [-1.20, +3.09]`)
    #    Note: X_max = +0.70 leaves clear screwdriver access along Y to M2 magnet adjuster at X = +4.525!
    north_lug = bd.Box(
        5.40, 6.10, 4.29,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-4.70, -14.90, -1.20)))
    base = base + east_flange + north_lug

    # 7. Three Ø3.40 mm integrated Top-Plate support posts (`Z_mod = +3.09 .. +5.29 mm`)
    for mx, my in SUNK_MOUNT_PTS_MOD:
        post = bd.Cylinder(
            radius=1.70, height=2.20, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
        ).moved(bd.Location((mx, my, 3.09)))
        base = base + post

    # 8. Cut Hinge Pin Bore Ø2.06 mm through both North Hinge Ears
    hinge_bore = (
        bd.Cylinder(radius=1.03, height=22.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((0.0, HINGE_Y, HINGE_Z)))
    )
    base = base - hinge_bore

    # 9. Cut Ø3.20 mm switch-pin / wire exit hole centered in SE switch floor `(5.70, 5.70)`
    sw_wire_hole = bd.Cylinder(
        radius=1.60, height=4.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)
    ).moved(bd.Location((5.70, 5.70, -0.60)))
    base = base - sw_wire_hole

    # 10. Cut Ø1.60 mm (>= Ø1.50 mm JLC3DP min bore!) M2 screw holes through the 3 mounting posts
    for mx, my in SUNK_MOUNT_PTS_MOD:
        sh = bd.Cylinder(
            radius=0.80, height=10.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)
        ).moved(bd.Location((mx, my, 2.00)))
        base = base - sh

    return base.solids()[0]


def build_eval_pod_stand() -> bd.Solid:
    """
    Build Desktop Stand for the 48.0 x 32.0 mm Standalone Evaluation Carrier PCB:
      - Outer tray: 52.0 x 36.0 x 6.60 mm (flat bottom at Z = 0.0000 mm, corner R = 2.50 mm)
      - Floor thickness: 2.40 mm (Z = 0.00 to 2.40 mm)
      - 4 corner PCB standoffs bridged directly into inner walls (zero wedge crevices!) rising to Z = 5.40 mm
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

    # USB-C cable cutout on West (-X) wall (Z = 3.40 mm -> 1.00 mm step above 2.40 mm floor!)
    usb_cut = bd.Box(
        6.00, 12.00, 5.00,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((-25.0, 0.0, 3.40)))
    tray = tray - usb_cut

    # 4 corner M2 bosses with rectangular corner bridges fused directly into the outer walls (zero narrow crevices!)
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

    # Re-mask outer perimeter so bridges never protrude outside 52.0 x 36.0 R=2.50
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


def _add_shroud_upper_shell(
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    z_bot: float,
    z_deck: float = 15.05,
) -> bd.Solid:
    """
    Build smooth rounded-corner outer hood (`R_corner = 0.85 mm`) + concentric `R = 7.70 mm`
    cylindrical hub shroud arch over `#02` 11-ball hub (before subtracting cavity & wheel slot).
    """
    cx = 0.5 * (x_min + x_max)
    cy = 0.5 * (y_min + y_max)
    with bd.BuildPart() as bp_body:
        with bd.BuildSketch(bd.Plane.XY.offset(z_bot)):
            with bd.Locations([(cx, cy)]):
                bd.RectangleRounded(x_max - x_min, y_max - y_min, radius=0.85)
        bd.extrude(amount=z_deck - z_bot)
    body = bp_body.part

    # Concentric cylindrical arch over #02 11-ball hub (`X in [+2.00, +7.80]`, R_outer = 7.70 mm < Wheel R = 8.40 mm!)
    arch_outer = (
        bd.Cylinder(radius=7.70, height=5.80, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((2.00, Y_AXLE, Z_AXLE)))
    )
    # Clip arch strictly above z_bot so it never protrudes below the cover bottom plane
    arch_clip = bd.Box(
        6.40, 18.00, 20.00,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((1.90, Y_AXLE, z_bot)))
    body = body + (arch_outer & arch_clip)
    return body.solids()[0]


def _cut_shroud_wheel_slot_and_arch_cavity(
    body: bd.Solid,
    z_bot: float,
    y_slot_min: float = -7.95,
    y_slot_max: float = 7.75,
) -> bd.Solid:
    """Cut crisp mouse-style top wheel slot (`6.30 x 15.70 mm`) and concentric R=6.75 mm hub pocket."""
    slot_box = bd.Box(
        6.30,
        y_slot_max - y_slot_min,
        25.0,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-3.35, y_slot_min, z_bot - 1.0)))
    body = body - slot_box

    # Inner concentric pocket R=6.75 mm over #02 11-ball hub (R=6.20 -> 0.55 mm radial & 0.45 mm axial clearance; 0.95 mm arch walls!)
    arch_inner = (
        bd.Cylinder(radius=6.75, height=4.40, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((2.45, Y_AXLE, Z_AXLE)))
    )
    arch_in_clip = bd.Box(
        5.20, 16.00, 20.00,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((2.40, Y_AXLE, z_bot - 1.0)))
    body = body - (arch_inner & arch_in_clip)
    return body.solids()[0]


def build_wheel_shroud_cover_sunk_assembled() -> bd.Solid:
    """
    Build Mouse-Style Shroud Cover (`#20B`) for `curcur40-right` Low-Profile Sunk Variant
    in assembled module coordinates (`Z_mod = +6.91 mm` seats directly on Top Plate `Z_global = -2.00 mm`):
      - 100% closed 4-sided perimeter walls hide `#02` 11-ball hub, `#03` carriage, `#07` sensor PCB,
        `#10` switch, and `#12` bearings from every angle, exposing ONLY `#01` SUS304 flywheel (`R=8.40 mm`,
        top `Z_global = +9.80 mm`) through a crisp `6.30 x 15.70 mm` mouse-wheel slot!
      - Fastens via the EXACT same 3 M2 mounting screws (`SUNK_MOUNT_PTS_MOD`) with 1.60 mm thick tabs
        (zero extra holes on PCB or Top Plate!).
      - Clears adjacent East & South Choc keycaps (`X_mod = -10.45`, `Y_mod = +10.45`) by 0.50 mm,
        clears all moving module parts by >= 0.35 mm, and maintains 100% walls >= 0.85 mm!
    """
    z_bot = 6.91
    z_deck = 15.05

    # 1. Closed 4-Sided Outer Hood (`X in [-9.95, +10.05]`, `Y in [-10.10, +9.95]`, `Z in [6.91, 15.05]`) + Concentric Hub Arch
    cover = _add_shroud_upper_shell(-9.95, 10.05, -10.10, 9.95, z_bot=z_bot, z_deck=z_deck)

    # 2. East Mounting Flange (`X in [+10.05, +14.60]`, `Y in [-4.50, +8.10]`, `Z in [6.91, 8.51]`) for W1 & W2
    east_tab = bd.Box(
        4.55, 12.60, 1.60,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((10.05, -4.50, z_bot)))

    # 3. North Mounting Lug (`X in [-4.60, +0.60]`, `Y in [-14.60, -10.10]`, `Z in [6.91, 8.51]`) for W3
    north_tab = bd.Box(
        5.20, 4.50, 1.60,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-4.60, -14.60, z_bot)))
    cover = cover + east_tab + north_tab

    # 4. Internal Main Cavity (`X in [-9.10, +9.15]`, `Y in [-9.20, +9.05]`, `Z in [6.00, 14.20]` -> 100% closed >=0.85 mm walls!)
    cav_main = bd.Box(
        18.25, 18.25, 14.20 - 6.00,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-9.10, -9.20, 6.00)))
    cover = cover - cav_main

    # 5. Cut Top Wheel Slot (`6.30 x 15.70 mm`) & Concentric Hub Clearance Pocket
    cover = _cut_shroud_wheel_slot_and_arch_cavity(cover, z_bot=z_bot)

    # 6. Cut 3x Ø2.40 mm M2 screw through-holes at SUNK_MOUNT_PTS_MOD
    for mx, my in SUNK_MOUNT_PTS_MOD:
        sh = bd.Cylinder(
            radius=1.20, height=6.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)
        ).moved(bd.Location((mx, my, z_bot + 0.80)))
        cover = cover - sh

    return cover.solids()[0]


def build_wheel_shroud_cover_eval() -> bd.Solid:
    """
    Build Mouse-Style Shroud Cover (`#20A`) for the Standalone Evaluation Pod (`Z_mod = 0.00 mm` on Carrier PCB):
      - Full 4-sided dust & visual shroud (`20.20 x 20.20 mm` rounded-corner body + North/South M2 mounting ears)
      - Includes Ø2.80 mm North screwdriver access port at `(X=+4.525, Z=+5.65)` for `#18` magnet tuning
        without removing the cover, and a West bottom wire exit tunnel for `#11` 4-wire sensor harness!
    """
    z_bot = 0.00
    z_deck = 15.05

    # 1. Outer Hood (`X in [-10.10, +10.10]`, `Y in [-10.20, +10.00]`, `Z in [0.00, 15.05]`) + Concentric Hub Arch
    cover = _add_shroud_upper_shell(-10.10, 10.10, -10.20, 10.00, z_bot=z_bot, z_deck=z_deck)

    # 2. North & South Mounting Ears (`X in [-2.60, +2.60]`, `Y in [-14.50, -10.20]` & `[+10.00, +14.30]`, `Z in [0.00, 1.80]`)
    ear_n = bd.Box(5.20, 4.30, 1.80, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN)).moved(bd.Location((0.0, -14.50, 0.0)))
    ear_s = bd.Box(5.20, 4.30, 1.80, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN)).moved(bd.Location((0.0, 10.00, 0.0)))
    cover = cover + ear_n + ear_s

    # 3. Internal Cavity (`X in [-9.15, +9.15]`, `Y in [-9.25, +9.05]`, `Z in [-1.00, 14.20]` -> >=0.85 mm walls & roof!)
    cav = bd.Box(
        18.30, 18.30, 15.20,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-9.15, -9.25, -1.00)))
    cover = cover - cav

    # 4. Cut Top Wheel Slot (`6.30 x 15.70 mm`) & Concentric Hub Clearance Pocket
    cover = _cut_shroud_wheel_slot_and_arch_cavity(cover, z_bot=z_bot)

    # 5. Cut Ø2.80 mm North Screwdriver Access Port aligned with M2 Magnet Adjuster `(X=+4.525, Z=+5.65)`
    adj_port = (
        bd.Cylinder(radius=1.40, height=4.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))
        .rotate(bd.Axis.X, 90)
        .moved(bd.Location((4.525, -9.70, 5.65)))
    )
    cover = cover - adj_port

    # 6. Cut West Wire Exit Arch (`Y in [-2.50, +2.50]`, `Z in [0.00, 2.80]`) for `#11` 4-wire sensor harness
    wire_box = bd.Box(3.00, 5.00, 1.80, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((-9.60, 0.0, -0.20)))
    wire_cyl = (
        bd.Cylinder(radius=2.50, height=3.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((-9.60, 0.0, 1.60)))
    )
    wire_clip = bd.Box(4.00, 6.00, 5.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((-9.60, 0.0, 0.0)))
    cover = cover - ((wire_box + wire_cyl) & wire_clip)

    # 7. Cut 2x Ø2.40 mm M2 mounting holes in North/South ears `(0.0, -12.35)` & `(0.0, +12.15)` (0.95 mm wall both sides!)
    for ey in (-12.35, 12.15):
        eh = bd.Cylinder(radius=1.20, height=5.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).moved(
            bd.Location((0.0, ey, 0.90))
        )
        cover = cover - eh

    return cover.solids()[0]


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

    # 2. Hinged Carriage
    carriage = build_wheel_carriage_assembled()
    carriage.label = "Wheel_Hinged_Carriage"

    # 3. SUS304 Flywheel (rotated so its Z [0..5.60] lies along X [-2.85..+2.75] at (Y_AXLE, Z_AXLE))
    fw_raw = build_sus304_flywheel_centered()
    flywheel = fw_raw.rotate(bd.Axis.Y, 90).moved(bd.Location((WHEEL_X_MIN, Y_AXLE, Z_AXLE)))
    flywheel.label = "SUS304_Flywheel_16p8mm"

    # 4. 11-Ball Resin Ratchet Hub (rotated so Z [0..3.55] lies along X [+2.80..+6.35])
    hub_raw = build_ratchet_hub_print_oriented()
    hub = hub_raw.rotate(bd.Axis.Y, 90).moved(bd.Location((HUB_X_MIN, Y_AXLE, Z_AXLE)))
    hub.label = "Ratchet_Hub_Resin"

    # 5. 11x Ø2.00 mm SUJ2 Steel Balls seated in hub pockets (X = HUB_X_MIN + HUB_W/2 = +4.575)
    x_balls = HUB_X_MIN + HUB_W / 2.0
    balls = []
    for i in range(N_BALLS):
        ang = math.radians(i * (360.0 / N_BALLS) + 15.0)
        # After rotating around +Y by +90 deg: local (bx, by, z_mid) -> (z_mid, by, -bx)
        by = Y_AXLE + R_BALL_ORBIT * math.sin(ang)
        bz = Z_AXLE - R_BALL_ORBIT * math.cos(ang)
        b = bd.Sphere(radius=0.99).moved(bd.Location((x_balls, by, bz)))
        b.label = f"Steel_Ball_2mm_{i+1:02d}"
        balls.append(b)

    # 6. Non-magnetic SUS316 Shaft Ø1.98 x 14.15 mm (X = -5.50 to +8.65)
    shaft = (
        bd.Cylinder(radius=0.99, height=14.15, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((-5.50, Y_AXLE, Z_AXLE)))
    )
    shaft.label = "SUS316_Axle_Shaft_2mm"

    # 7. 2x Miniature Degreased Bearings (MR52 / DDL-520: Ø2.04 ID x Ø5.00 OD)
    #    West at X = [-5.42, -3.12], East at X = [+6.47, +8.73]
    brg_w = (
        bd.Cylinder(radius=2.49, height=2.30, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        - bd.Cylinder(radius=1.02, height=2.30, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    ).rotate(bd.Axis.Y, 90).moved(bd.Location((-5.42, Y_AXLE, Z_AXLE)))
    brg_w.label = "Bearing_MR52_West"

    brg_e = (
        bd.Cylinder(radius=2.49, height=2.20, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        - bd.Cylinder(radius=1.02, height=2.20, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    ).rotate(bd.Axis.Y, 90).moved(bd.Location((6.52, Y_AXLE, Z_AXLE)))
    brg_e.label = "Bearing_MR52_East"

    # 8. North Hinge Pin Ø1.98 x 17.20 mm at (HINGE_Y, HINGE_Z)
    hinge_pin = (
        bd.Cylinder(radius=0.99, height=17.20, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((0.0, HINGE_Y, HINGE_Z)))
    )
    hinge_pin.label = "Hinge_Pin_SUS304_2mm"

    # 9. Diametric Sensor Magnet Ø3.0 x 0.95 mm (X = -6.48 to -5.53) + AS5600-ASOT IC (X = -8.14 to -6.84) + SubPCB (X = -8.75 to -8.15)
    sens_mag = (
        bd.Cylinder(radius=1.50, height=0.95, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.Y, 90)
        .moved(bd.Location((-6.48, Y_AXLE, Z_AXLE)))
    )
    sens_mag.label = "Diametric_Magnet_3x1mm"

    as5600_pcb = bd.Box(
        0.60, 8.80, 8.80,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((-8.75, Y_AXLE, 4.50)))
    as5600_pcb.label = "AS5600_Sensor_SubPCB"

    as5600_ic = bd.Box(
        1.30, 4.90, 3.90,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER),
    ).moved(bd.Location((-8.14, Y_AXLE, Z_AXLE)))
    as5600_ic.label = "AS5600_SOIC8_IC"

    # 10. Kailh Square Silent Micro Switch (6.2 x 6.2 x 3.8 mm body + 0.5 mm red button = 4.30 mm total height!) at (+5.70, +5.70)
    sw_body = bd.Box(
        6.20, 6.20, 3.80,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((5.70, 5.70, 0.02)))
    sw_btn = bd.Cylinder(
        radius=1.30, height=0.46, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
    ).moved(bd.Location((5.70, 5.70, 3.82)))  # Top at 4.28 mm, 0.04 mm preload gap to striker_block at 4.32 mm!
    silent_sw = (sw_body + sw_btn).solids()[0]
    silent_sw.label = "Kailh_Silent_Switch_6x6x4p3"

    # 11. M2 Magnet Gap Adjustment Screw + Ø1.6 x 1.2 mm Ratchet Magnet in North-East Boss (X = +4.525, Z = +5.65)
    m2_adj = (
        bd.Cylinder(radius=0.82, height=3.15, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.X, -90)
        .moved(bd.Location((4.525, -8.55, 5.65)))
    )
    m2_adj.label = "M2_Magnet_Adjuster_And_NdFeB"

    raw_items = [
        base, carriage, flywheel, hub, shaft, brg_w, brg_e,
        hinge_pin, sens_mag, as5600_pcb, as5600_ic, silent_sw, m2_adj,
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


def main():
    print("=== 1. Building & Verifying Individual Manufacturable Parts ===")
    # 1) SUS304 Flywheel (CNC turned/milled metal part; check bores >= 1.50mm, skip 3DP 0.8mm check due to 0.35mm chamfer & grip flutes)
    flywheel_part = build_sus304_flywheel_centered()
    mass_sus304_g = flywheel_part.volume * 0.00793  # SUS304 density 7.93 g/cm³ = 0.00793 g/mm³
    verify_jlc3dp_part(flywheel_part, "sus304-flywheel", check_bores=True, check_wall_0p8=False)
    print(f"         -> SUS304 Flywheel Calculated Mass = {mass_sus304_g:.2f} g")
    bd.export_step(flywheel_part, str(PARTS_DIR / "sus304-flywheel.step"))
    bd.export_stl(flywheel_part, str(PARTS_DIR / "sus304-flywheel.stl"))

    # 2) 11-Ball Resin Ratchet Hub (flat at Z = 0.00 to 3.75 mm; exclude snap-in ball retention lips at R >= 4.8mm, Z ~ 1.875mm, identical to Trackball Cup Group A!)
    hub_part = build_ratchet_hub_print_oriented()
    max_v_r = max(math.hypot(v.X, v.Y) for v in hub_part.vertices())
    assert max_v_r <= HUB_R + 1e-4, f"Ratchet hub vertex radius {max_v_r:.4f} > HUB_R {HUB_R:.4f} mm!"
    verify_jlc3dp_part(
        hub_part,
        "ratchet-hub-11ball",
        check_bores=True,
        check_wall_0p8=True,
        allowed_thin_pred=lambda d, mx, my, mz: (0.7 <= mz <= 3.05 and math.hypot(mx, my) >= 5.5 and d <= 0.70),
    )
    bd.export_step(hub_part, str(PARTS_DIR / "ratchet-hub-11ball.step"))
    bd.export_stl(hub_part, str(PARTS_DIR / "ratchet-hub-11ball.stl"))

    # 3) Unitized Hinged Carriage (shifted to Z_min = 0.0000 mm for flat SLA printing: rotate +90 around Y or shift Z?
    #    Let's check: in assembled pose Z_min = 1.40 mm; rotating so flat East face X = +8.75 lies on Z = 0.0000 print bed!)
    carriage_asm = build_wheel_carriage_assembled()
    carriage_print = carriage_asm.rotate(bd.Axis.Y, 90)
    c_bb = carriage_print.bounding_box()
    carriage_print = carriage_print.moved(bd.Location((-c_bb.center().X, -c_bb.center().Y, -c_bb.min.Z)))
    verify_jlc3dp_part(carriage_print, "wheel-carriage", check_bores=True)
    bd.export_step(carriage_print, str(PARTS_DIR / "wheel-carriage.step"))
    bd.export_stl(carriage_print, str(PARTS_DIR / "wheel-carriage.stl"))

    # 4) Wheel Base Frame (already flat at Z = 0.0000 mm!)
    base_part = build_wheel_base_frame()
    verify_jlc3dp_part(base_part, "wheel-base-frame", check_bores=True)
    bd.export_step(base_part, str(PARTS_DIR / "wheel-base-frame.step"))
    bd.export_stl(base_part, str(PARTS_DIR / "wheel-base-frame.stl"))

    # 4b) Low-Profile Sunk Wheel Base Frame (shifted +1.20 mm in Z so flat bottom lies at Z = 0.0000 mm!)
    base_sunk_asm = build_wheel_base_frame_sunk_assembled()
    base_sunk_print = base_sunk_asm.moved(bd.Location((0.0, 0.0, 1.20))).solids()[0]
    verify_jlc3dp_part(base_sunk_print, "wheel-base-frame-sunk", check_bores=True)
    bd.export_step(base_sunk_print, str(PARTS_DIR / "wheel-base-frame-sunk.step"))
    bd.export_stl(base_sunk_print, str(PARTS_DIR / "wheel-base-frame-sunk.stl"))

    # 5) Standalone Eval Pod Stand (flat at Z = 0.0000 mm!)
    stand_part = build_eval_pod_stand()
    verify_jlc3dp_part(stand_part, "eval-pod-stand", check_bores=True)
    bd.export_step(stand_part, str(PARTS_DIR / "eval-pod-stand.step"))
    bd.export_stl(stand_part, str(PARTS_DIR / "eval-pod-stand.stl"))

    # 6a) Shroud Cover for Standalone Eval Pod (flat at Z = 0.0000 mm!)
    cover_eval_part = build_wheel_shroud_cover_eval()
    verify_jlc3dp_part(cover_eval_part, "wheel-shroud-cover-eval", check_bores=True)
    bd.export_step(cover_eval_part, str(PARTS_DIR / "wheel-shroud-cover-eval.step"))
    bd.export_stl(cover_eval_part, str(PARTS_DIR / "wheel-shroud-cover-eval.stl"))

    # 6b) Shroud Cover for curcur40-right Sunk Variant (shifted -6.91 mm in Z so flat bottom lies at Z = 0.0000 mm!)
    cover_sunk_asm = build_wheel_shroud_cover_sunk_assembled()
    cover_sunk_print = cover_sunk_asm.moved(bd.Location((0.0, 0.0, -6.91))).solids()[0]
    verify_jlc3dp_part(cover_sunk_print, "wheel-shroud-cover-sunk", check_bores=True)
    bd.export_step(cover_sunk_print, str(PARTS_DIR / "wheel-shroud-cover-sunk.step"))
    bd.export_stl(cover_sunk_print, str(PARTS_DIR / "wheel-shroud-cover-sunk.stl"))

    print("\n=== 2. Building & Verifying Module & Standalone Pod Assemblies ===")
    mod_parts = assemble_module_parts(origin=(0.0, 0.0, 0.0), sunk=False)
    verify_zero_overlap(mod_parts, "Inertia_Wheel_Module")
    mod_asm = bd.Compound(label="Inertia_Wheel_Module_Assembly", children=mod_parts)
    bd.export_step(mod_asm, str(ASSEMBLIES_DIR / "inertia-wheel-module-assembly.step"))

    mod_sunk_parts = assemble_module_parts(origin=(0.0, 0.0, 0.0), sunk=True)
    verify_zero_overlap(mod_sunk_parts, "Inertia_Wheel_Module_Sunk")
    mod_sunk_asm = bd.Compound(label="Inertia_Wheel_Module_Sunk_Assembly", children=mod_sunk_parts)
    bd.export_step(mod_sunk_asm, str(ASSEMBLIES_DIR / "inertia-wheel-module-sunk-assembly.step"))

    # Standalone Eval Pod Assembly: Stand (Z=0..6.4) + Carrier PCB (42x30x1.6 at Z=5.4..7.0) + RP2040-Zero (West) + Wheel Module (East X=+8.0, Z=7.0)
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

    # RP2040-Zero oriented with USB-C facing West (-X): 23.5 mm along X ([-23.75, -0.25]), 18.0 mm along Y ([-9.0, +9.0])
    rp2040_zero = bd.Box(23.5, 18.0, 3.20, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(
        bd.Location((-12.0, 0.0, 7.02))
    )
    rp2040_zero.label = "Waveshare_RP2040_Zero"

    # JST SH 6-pin header on North edge (X=0.0, Y=-12.5 -> Y in [-14.65, -10.35], clear of RP2040-Zero & Wheel Module!)
    jst_sh = bd.Box(8.00, 4.30, 2.95, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(
        bd.Location((-2.0, -12.5, 7.02))
    )
    jst_sh.label = "JST_SH_6Pin_Header"

    pod_wheel_parts = assemble_module_parts(origin=(12.5, 0.0, 7.02))
    pod_all = [stand_asm, carrier_pcb, rp2040_zero, jst_sh, *pod_wheel_parts]
    verify_zero_overlap(pod_all, "Standalone_Eval_Pod")
    pod_asm = bd.Compound(label="Inertia_Wheel_Eval_Pod_Assembly", children=pod_all)
    bd.export_step(pod_asm, str(ASSEMBLIES_DIR / "inertia-wheel-eval-pod-assembly.step"))

    # Covered Standalone Eval Pod Assembly
    pod_cover = build_wheel_shroud_cover_eval().moved(bd.Location((12.5, 0.0, 7.03))).solids()[0]
    pod_cover.label = "Wheel_Shroud_Cover_Eval"
    pod_covered_all = [*pod_all, pod_cover]
    verify_zero_overlap(pod_covered_all, "Standalone_Eval_Pod_Covered")
    pod_moving_parts = [
        s for s in pod_wheel_parts
        if s.label not in {"Wheel_Base_Frame", "Hinge_Pin_SUS304_2mm", "Kailh_Silent_Switch_6x6x4p3"}
    ]
    d_pod_cover_mov = min(closest_points(s, pod_cover).distance for s in pod_moving_parts)
    assert d_pod_cover_mov >= 0.30, f"Eval Cover vs moving parts clearance {d_pod_cover_mov:.3f} mm < 0.30 mm!"
    print(f"         -> Eval Shroud Cover clearance to all moving parts = {d_pod_cover_mov:.3f} mm (>= 0.30 mm)")
    pod_cov_asm = bd.Compound(label="Inertia_Wheel_Eval_Pod_Covered_Assembly", children=pod_covered_all)
    bd.export_step(pod_cov_asm, str(ASSEMBLIES_DIR / "inertia-wheel-eval-pod-covered-assembly.step"))

    print("\n=== 3. Verifying Zero-Modification Drop-In Fit on curcur40-right ===")
    # Place module at rEXSW1 on curcur40-right:
    # PCB coord (14.2875, 0.0000) -> STEP coord: X_step = 14.2875 + 14.2875 = +28.5750, Y_step = -(0.0 + 57.1500) = -57.1500
    # Note: In curcur40 STEP coords, +Y_pcb (South) is -Y_step! So rotate module 180° or mirror Y?
    # Wait: in KiCad PCB coords (+X East, +Y South), rotating around Z by 0 vs 180:
    # In curcur40 STEP coords: +X_step = East (+x_pcb), +Y_step = North (-y_pcb)!
    # Our module has +X = East, -Y = North, +Y = South!
    # Wait: if +X_mod = East and -Y_mod = North, that would be left-handed unless +Y_mod = North or rotated!
    # Check right-handedness of (X_mod, Y_mod, Z_mod):
    # In standard right-handed XY (+X right/East, +Y up/North, +Z out/Top):
    # Earlier in our module code: HINGE_Y = -7.35, Silent Switch Y = +5.75!
    # In curcur40 STEP coords: North is Y_step = -48.15 (larger, LESS negative!), South (toward rEXSW2 at y_pcb=+19.05 -> Y_step=-76.20) is MORE negative Y_step!
    # So rotating the module by 180 deg around Z:
    #   - Hinge (-7.35) rotates to +7.35 -> Y_step = -57.15 + 7.35 = -49.80 (NORTH! Away from rEXSW2!)
    #   - Silent Switch (+5.75) rotates to -5.75 -> Y_step = -57.15 - 5.75 = -62.90 (SOUTH!)
    #   - Flywheel Y_AXLE (-0.50) rotates to +0.50 -> Y_step = -57.15 + 0.50 = -56.65 (shifted 0.50 mm NORTH, EXTRA clearance from rEXSW2 at Y_step = -76.20!)
    # That's a pure 180 deg rigid rotation (zero mirroring needed)!
    cx_step, cy_step, cz_fcu = 28.5750, -57.1500, -4.19  # 0.01 mm seated clearance on F.Cu (-4.20)
    mod_local = bd.Compound(children=assemble_module_parts(origin=(0.0, 0.0, 0.0))).rotate(bd.Axis.Z, 180).moved(
        bd.Location((cx_step, cy_step, cz_fcu))
    )
    dropped_parts = list(mod_local.solids())
    for idx, s in enumerate(dropped_parts):
        s.label = mod_parts[idx].label

    # Import existing curcur40-right case, Trackball Cup, exact Main PCB, exact Top Plate, and all 19 Keycaps!
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

    # Measure minimum clearance to Top Plate 18.2mm cutout (static >= 0.20 mm, moving >= 0.30 mm per JLC3DP rule!) and South keycap rEXSW2
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

    print("\n=== 4. Verifying Low-Profile Sunk Variant on curcur40-right (Wheel Center = Keycap Center Z=+1.40mm) ===")
    # Keycap spans Z = [-0.80, +3.60] -> Keycap vertical center Z = +1.40 mm!
    # Placing sunk module at cz_sunk = +1.40 - Z_AXLE (10.30) = -8.90 mm puts:
    #   - Wheel Axle Center Z = +1.40 mm (exact keycap vertical center!)
    #   - Wheel Top         Z = +9.80 mm (+6.20 mm above keycap top +3.60 mm, mouse-wheel-like profile!)
    #   - Wheel Bottom      Z = -7.00 mm (sunk cleanly through 18.2x18.2mm inner cutout in Main PCB & Top Plate!)
    #   - Sunk Base Bottom  Z = -10.10 mm (>10.4 mm clear above unmodified cases/right.step inner floor!)
    cz_sunk = 1.40 - Z_AXLE  # -8.90 mm
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

    # Build Right Top Plate with 18.50x18.50mm inner cutout + 3x Ø2.40mm M2 screw holes (outer outline 100% unchanged!)
    with bd.BuildSketch(bd.Plane.XY.offset(-4.50)) as sk_plate_win:
        with bd.Locations([(cx_step, cy_step)]):
            bd.RectangleRounded(18.50, 18.50, 0.50)
    sunk_top_plate = top_plate_ref - bd.extrude(sk_plate_win.sketch, amount=3.00)
    for sx_m, sy_m in sunk_mount_step:
        sunk_top_plate = sunk_top_plate - bd.Cylinder(
            radius=1.20, height=4.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
        ).moved(bd.Location((sx_m, sy_m, -4.50)))
    sunk_top_plate = sunk_top_plate.solids()[0]
    sunk_top_plate.label = "curcur40_Right_Top_Plate_SunkMount"

    # Add 3x standard M2 x 4.0mm top screws seated on Top Plate Z = -2.00 mm (with Ø1.58mm visualization shank inside Ø1.60mm bore)
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
    sunk_fw = [s for s in sunk_dropped_parts if s.label == "SUS304_Flywheel_16p8mm"][0]
    fw_bb = sunk_fw.bounding_box()
    d_case_floor = min(closest_points(s, right_case).distance for s in sunk_dropped_parts)
    d_sunk_plate_moving = min(closest_points(s, sunk_top_plate).distance for s in sunk_dropped_parts if s.label not in sunk_static_labels)
    d_sunk_pcb_moving = min(closest_points(s, sunk_main_pcb).distance for s in sunk_dropped_parts if s.label not in sunk_static_labels)
    d_sunk_rexsw2 = min(closest_points(s, rexsw2_cap).distance for s in sunk_dropped_parts)
    assert d_case_floor >= 2.00, f"Sunk module vs Right Case clearance {d_case_floor:.3f} mm < 2.00 mm!"
    assert d_sunk_plate_moving >= 0.30, f"Sunk moving parts vs Top Plate {d_sunk_plate_moving:.3f} mm < 0.30 mm!"
    assert d_sunk_pcb_moving >= 0.30, f"Sunk moving parts vs Main PCB {d_sunk_pcb_moving:.3f} mm < 0.30 mm!"
    assert d_sunk_rexsw2 >= 1.00, f"Sunk module vs rEXSW2 Keycap {d_sunk_rexsw2:.3f} mm < 1.00 mm!"
    print(f"         -> Sunk Flywheel Z span = [{fw_bb.min.Z:+.2f}, {fw_bb.max.Z:+.2f}] mm, Center Z = {0.5*(fw_bb.min.Z+fw_bb.max.Z):+.2f} mm (Keycap Center = +1.40 mm!)")
    print(f"         -> Clearance to unmodified Right Case floor/walls = {d_case_floor:.3f} mm")
    print(f"         -> Moving Parts clearance to Top Plate / Main PCB = {d_sunk_plate_moving:.3f} / {d_sunk_pcb_moving:.3f} mm (>= 0.30 mm)")
    print(f"         -> Clearance to South Keycap (rEXSW2)             = {d_sunk_rexsw2:.3f} mm (>= 1.00 mm)")

    sunk_asm = bd.Compound(label="curcur40_Right_With_Inertia_Wheel_Sunk", children=sunk_fit_parts)
    bd.export_step(sunk_asm, str(ASSEMBLIES_DIR / "curcur40-right-with-inertia-wheel-sunk.step"))

    print("\n=== 5. Verifying Covered Low-Profile Sunk Variant on curcur40-right ===")
    sunk_cover_placed = (
        build_wheel_shroud_cover_sunk_assembled()
        .rotate(bd.Axis.Z, 180)
        .moved(bd.Location((cx_step, cy_step, cz_sunk)))
        .solids()[0]
    )
    sunk_cover_placed.label = "Wheel_Shroud_Cover_Sunk"

    # With the 1.60 mm cover flanges seated on Top Plate (Z = -2.00 to -0.40 mm), use 3x M2 x 5.0mm top screws seated at Z = -0.39 mm!
    sunk_cov_screws = []
    for idx_m, (sx_m, sy_m) in enumerate(sunk_mount_step):
        sc_head = bd.Cylinder(
            radius=1.90, height=0.80, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
        ).moved(bd.Location((sx_m, sy_m, -0.38)))
        sc_shank = bd.Cylinder(
            radius=0.78, height=5.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)
        ).moved(bd.Location((sx_m, sy_m, -0.38)))
        sc = (sc_head + sc_shank).solids()[0]
        sc.label = f"Sunk_Cover_Screw_M2x5_{idx_m+1}"
        sunk_cov_screws.append(sc)

    sunk_covered_parts = [
        right_case, sunk_main_pcb, sunk_top_plate, tb_cup, tb_ball,
        *keycaps, sunk_cover_placed, *sunk_cov_screws, *sunk_dropped_parts,
    ]
    verify_zero_overlap(sunk_covered_parts, "curcur40_Right_Sunk_Covered_Check")

    sunk_moving = [s for s in sunk_dropped_parts if s.label not in sunk_static_labels]
    d_cov_moving = min(closest_points(s, sunk_cover_placed).distance for s in sunk_moving)
    d_cov_keycaps = min(closest_points(kc, sunk_cover_placed).distance for kc in keycaps)
    d_cov_case = closest_points(right_case, sunk_cover_placed).distance
    assert d_cov_moving >= 0.30, f"Sunk Cover vs moving parts clearance {d_cov_moving:.3f} mm < 0.30 mm!"
    assert d_cov_keycaps >= 0.30, f"Sunk Cover vs adjacent keycaps clearance {d_cov_keycaps:.3f} mm < 0.30 mm!"
    assert d_cov_case >= 1.00, f"Sunk Cover vs Right Case clearance {d_cov_case:.3f} mm < 1.00 mm!"
    print(f"         -> Sunk Shroud Cover clearance to all moving parts = {d_cov_moving:.3f} mm (>= 0.30 mm)")
    print(f"         -> Sunk Shroud Cover clearance to all 19 Keycaps   = {d_cov_keycaps:.3f} mm (>= 0.30 mm)")
    print(f"         -> Sunk Shroud Cover clearance to Right Case rim   = {d_cov_case:.3f} mm (>= 1.00 mm)")

    sunk_cov_asm = bd.Compound(label="curcur40_Right_With_Inertia_Wheel_Sunk_Covered", children=sunk_covered_parts)
    bd.export_step(sunk_cov_asm, str(ASSEMBLIES_DIR / "curcur40-right-with-inertia-wheel-sunk-covered.step"))
    print("\nAll Passive Inertia Wheel 3D models (Standard, Sunk, and Covered) generated and verified successfully!")


if __name__ == "__main__":
    main()
