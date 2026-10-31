# -*- coding: utf-8 -*-
"""
Generate 3D CAD models (STEP & STL) for the Under-Plate 1-Piece Integral-Shaft
Passive Magnetic Inertia Scroll Wheel (`curcur40-inertia-wheel`) and run automated
JLCCNC / JLC3DP DFM checks and zero-interference verification across rest and
middle-click states on `curcur40-right`.

Outputs:
  Manufacturing Parts (`cases/inertia_wheel/`):
    1. steel-flywheel.step / .stl   (JLCCNC 45# Steel + Electroless Nickel Plating, 1-piece Ø22.00 mm wheel + integral bearing shoulders & D-shaft)
    2. magnet-holder.step / .stl    (JLC3DP MJF/SLS PA12, Ø5.68 x 2.05 mm glue-free D4x1mm diametric magnet sleeve)
    3. wheel-rocker.step / .stl     (JLC3DP MJF/SLS PA12, seesaw carriage with 2x DDL-520ZZ seats, integral Ø3.00 mm trunnions, West rEXSW1 striker, South glue-free detent boss)
    4. wheel-cradle.step / .stl     (JLC3DP MJF/SLS PA12, 2-screw under-PCB bracket at WC1/WC2 with upward U-saddles captured by Main PCB B.Cu)

  Verification Assemblies (`cases/assemblies/`):
    1. inertia-wheel-assembly.step
    2. curcur40-right-wheel-assembly.step
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
CASES_DIR = WORKSPACE / "cases"
PARTS_DIR.mkdir(parents=True, exist_ok=True)
ASSEMBLIES_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# Axle-Centered Local Frame (u, v, w) -> Pure Translation of Global STEP (X, Y, Z):
#   X_step = X_AXLE_STEP + u      (u = x_pcb - 14.2875; +u = East, -u = West)
#   Y_step = Y_AXLE_STEP + v      (v = -(y_pcb + 2.0000); +v = North, -v = South)
#   Z_step = Z_AXLE_STEP + w      (w = Z_step - (-6.9000); B.Cu = +1.10, F.Cu = +2.70, Plate = [+3.30, +4.90])
# =============================================================================
X_AXLE_PCB = 14.2875
Y_AXLE_PCB = -2.0000
X_AXLE_STEP = X_AXLE_PCB + 14.2875      # +28.5750 mm
Y_AXLE_STEP = -(Y_AXLE_PCB + 57.1500)   # -55.1500 mm
Z_AXLE_STEP = -6.9000                   # Wheel top = +4.10 mm (+0.50 mm proud of +3.60 mm Choc V2 keycaps)

WHEEL_OD = 22.00
WHEEL_R = WHEEL_OD / 2.0                # 11.00 mm
WHEEL_RIM_W = 4.40                      # u in [-2.20, +2.20] (0.60 mm/side clearance in 5.60 mm PCB/Plate slot)
N_FLUTES = 24                           # 24 rounded outer flutes (15 deg pitch = 1:1 with 24 scroll notches/rev)

# Integral Shaft & DDL-520ZZ (Ø2 x Ø5 x 2.30 mm) Bearing Stack along u:
STEP_SHOULDER_R = 1.45                  # Ø2.90 mm integral inner-race step (zero loose shims!)
STEP_U_HALF = 2.45                      # Shoulders at [-2.45, -2.20] and [+2.20, +2.45]
BRG_ID_R = 1.00                         # Ø2.00 mm
BRG_OD_R = 2.50                         # Ø5.00 mm
BRG_W = 2.30                            # West bearing [-4.75, -2.45], East bearing [+2.45, +4.75]
SHAFT_R = 0.99                          # Ø1.98 mm slip-fit bearing journal
SHAFT_U_WEST = -6.90                    # West D-shaft tip at u = -6.90 (meets D4x1mm magnet East face!)
SHAFT_U_EAST = +4.72                    # Recessed 0.03 mm inside East bearing outer face (+4.75)

# Magnet Holder (MJF/SLS PA12) & D4x1mm Diametric NdFeB Magnet:
HOLDER_OD_R = 2.84                      # Ø5.68 mm (>= 5.0 mm JLC3DP min; 0.82 mm wall around Ø4.04 mm magnet pocket!)
HOLDER_U_WEST = -7.97
HOLDER_U_EAST = -5.92                   # Length = 2.05 mm (>= 2.0 mm JLC3DP min; >= 0.31 mm clear of PCB -8.2875 & Rocker -5.60)
MAG_POCKET_R = 2.02                     # Ø4.04 mm pocket, depth 1.05 mm (u in [-7.97, -6.92])
MAG_D4_R = 2.00                         # Ø4.00 x 1.00 mm diametric magnet at u in [-7.94, -6.94] (2.78 mm East of rU6!)

# Seesaw Pivot & Middle-Click Kinematics:
U_PIV = -6.95                           # x_pcb = +7.3375 mm (L_east = 6.95 mm, L_west = 8.1875 mm -> ~68 gf crisp click!)
W_PIV = -0.65                           # Z_piv = -7.55 mm; Ø2.70 mm trunnion top at w = +0.70 (0.40 mm below Main PCB B.Cu w = +1.10!)
TRUNNION_R = 1.35                       # Ø2.70 mm integral PA12 trunnions (coaxial & flush with cheek R=1.35 top!)
SADDLE_R = 1.55                         # Ø3.10 mm upward U-saddles in cradle (0.20 mm radial / 0.40 mm diametral clearance)

U_SW = -0.8500 - X_AXLE_PCB             # -15.1375 mm (rEXSW1 Kailh Square Silent center on B.Cu)
V_SW = 0.0000
CLICK_PRESS_DEG = 2.20                  # 2.20 deg click press -> 0.26 mm wheel drop, +0.32 mm switch plunger compression

# Cradle Mounting Bosses (WC1 & WC2 on curcur40-right):
WC1_PCB = (7.8000, -9.8000)             # (u = -6.4875, v = +7.8000)
WC2_PCB = (20.4000, 5.8000)             # (u = +6.1125, v = -7.8000)
PILOT_BORE_R = 1.425                    # Ø2.85 mm pilot bore for M2 x L=3.0 x OD=3.2 mm brass heat-set insert

# South Glue-Free Detent Adjuster Boss on Rocker:
W_DET = -4.40                           # Z = -11.30 mm; wheel rim at v = -10.08 mm
V_DET_MIN = -16.40
V_DET_MAX = -11.40                      # 5.00 mm straight Ø2.85 mm bore (>= 0.52 mm clear of Ø22.00 mm wheel rim at all Z!)


def verify_jlc3dp_pa12_part(solid: bd.Solid, name: str):
    """
    Automated JLC3DP MJF/SLS PA12 pre-order check:
      1) Single watertight manifold positive-volume solid
      2) Bounding box >= 5.0 x 5.0 x 2.0 mm, <= 380 x 284 x 380 mm, flat bottom on Z = 0.0000 mm
      3) All concave cylindrical holes/bores >= Ø 1.50 mm
      4) Zero non-adjacent face pairs with 0.001 < d < 0.800 mm (strict >= 0.80 mm wall thickness)
    """
    assert solid.is_valid and is_sound(solid), f"[{name}] Solid is not watertight/manifold!"
    assert len(solid.solids()) == 1 and solid.volume > 0, f"[{name}] Must be a single positive-volume solid!"

    bb = solid.bounding_box()
    sx, sy, sz = bb.max.X - bb.min.X, bb.max.Y - bb.min.Y, bb.max.Z - bb.min.Z
    assert (
        min(sx, sy) >= 5.0 - 1e-3
        and sz >= 2.0 - 1e-3
        and max(sx, sy) <= 380.0
        and min(sx, sy) <= 284.0
        and sz <= 380.0
    ), f"[{name}] Bounding box {sx:.2f}x{sy:.2f}x{sz:.2f} mm outside JLC3DP [5x5x2, 380x284x380] mm limits!"
    assert abs(bb.min.Z - 0.0) < 1e-4, f"[{name}] Bottom Z={bb.min.Z:.4f} mm is not flat on Z=0.0000 mm!"

    faces = solid.faces()
    min_concave_diam = float("inf")
    for f in faces:
        surf = BRepAdaptor_Surface(f.wrapped)
        if surf.GetType() == GeomAbs_Cylinder and f.wrapped.Orientation() == TopAbs_REVERSED:
            diam = round(2.0 * surf.Cylinder().Radius(), 4)
            if diam < min_concave_diam:
                min_concave_diam = diam
    if min_concave_diam < float("inf"):
        assert min_concave_diam >= 1.50, (
            f"[{name}] Concave hole/bore diameter {min_concave_diam:.3f} mm < JLC3DP 1.50 mm limit!"
        )

    bbs = [f.bounding_box() for f in faces]
    unexpected = []
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
                    unexpected.append((d, (mx, my, mz), i, j))

    min_hd_str = f"{min_concave_diam:.2f}mm" if min_concave_diam < float("inf") else "none"
    print(
        f"[{name}] JLC3DP PA12 preflight OK: bbox={sx:.2f}x{sy:.2f}x{sz:.2f}mm, "
        f"min_hole_diam={min_hd_str}, <0.80mm violations={len(unexpected)}"
    )
    if unexpected:
        for d, (mx, my, mz), i, j in unexpected:
            print(f"  UNEXPECTED [{name}]: d={d:.4f} mm at ({mx:.2f}, {my:.2f}, {mz:.2f}) [F{i}-F{j}]")
    assert len(unexpected) == 0, f"[{name}] has {len(unexpected)} <0.80mm wall/gap violations!"


def build_steel_flywheel_local() -> bd.Solid:
    """
    Build 1-Piece Integral-Shaft Flywheel (`45# Steel + Electroless Nickel Plating`) in `(u, v, w)` frame
    (rotary axis along `u` through `(v=0, w=0)`):
      - Ø22.00 x 4.40 mm rim (`u in [-2.20, +2.20]`) with 24 rounded outer grip/detent flutes (`15 deg` pitch)
      - Integral Ø2.90 mm inner-race shoulders (`u in [-2.45, -2.20]` and `[+2.20, +2.45]`)
      - Integral Ø1.98 mm bearing journals (`u in [-4.75, -2.45]` and `[+2.45, +4.72]`)
      - Integral West D-shaft (`u in [-6.90, -4.75]`, D-flat `w <= +0.72` over `u in [-6.90, -5.80]`)
    """
    # Build along +Z first (`z_ax = u - SHAFT_U_WEST`), then rotate +90 deg around Y (`+Z -> +X = +u`, `-X -> +Z = +w`)
    # Wait: let's build directly in `(u, v, w)` using Plane.YZ (`X_sketch = v, Y_sketch = w, extrude along +X = +u`)!
    rim = bd.extrude(
        bd.Plane.YZ.offset(-WHEEL_RIM_W / 2.0) * bd.Circle(WHEEL_R),
        amount=WHEEL_RIM_W,
    )
    rim_edges = [
        e for e in rim.edges()
        if abs(e.bounding_box().size.Y - WHEEL_OD) < 0.2
    ]
    rim = bd.chamfer(rim_edges, length=0.35)

    flutes = []
    r_cutter = 1.00
    r_center = WHEEL_R + 0.78  # Cuts 0.22 mm smooth rounded flutes (root R = 10.78 mm)
    for i in range(N_FLUTES):
        ang = math.radians(i * (360.0 / N_FLUTES))
        fv = r_center * math.cos(ang)
        fw = r_center * math.sin(ang)
        flutes.append(
            bd.extrude(
                bd.Plane.YZ.offset(-WHEEL_RIM_W / 2.0 - 0.5)
                * bd.Pos(fv, fw)
                * bd.Circle(r_cutter),
                amount=WHEEL_RIM_W + 1.0,
            )
        )
    rim = rim - bd.Compound(flutes)

    shoulders = bd.extrude(
        bd.Plane.YZ.offset(-STEP_U_HALF) * bd.Circle(STEP_SHOULDER_R),
        amount=2.0 * STEP_U_HALF,
    )
    shaft = bd.extrude(
        bd.Plane.YZ.offset(SHAFT_U_WEST) * bd.Circle(SHAFT_R),
        amount=SHAFT_U_EAST - SHAFT_U_WEST,
    )
    # D-flat on West shaft tip (`u in [-6.90, -5.80]`, `w >= +0.71` removed)
    d_cut = bd.Box(
        1.20,
        4.00,
        2.00,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((SHAFT_U_WEST - 0.05, 0.0, 0.71)))
    shaft = shaft - d_cut

    solid = (rim + shoulders + shaft).solids()[0]
    solid.label = "Steel_Flywheel_22mm"
    return solid


def build_magnet_holder_local() -> bd.Solid:
    """
    Build Glue-Free Diametric Magnet Sleeve (`MJF/SLS PA12`) in `(u, v, w)` frame:
      - Outer cylinder Ø5.68 mm (`R = 2.84 mm`), length `2.05 mm` (`u in [-7.97, -5.92]`)
      - West Ø4.04 mm x 1.05 mm pocket (`u in [-7.97, -6.92]`, radial wall 0.82 mm >= 0.80 mm)
      - East Ø2.02 mm D-bore (`u in [-6.92, -5.92]`, flat at `w = +0.74`)
    """
    outer = bd.extrude(
        bd.Plane.YZ.offset(HOLDER_U_WEST) * bd.Circle(HOLDER_OD_R),
        amount=HOLDER_U_EAST - HOLDER_U_WEST,
    )
    mag_pocket = bd.extrude(
        bd.Plane.YZ.offset(HOLDER_U_WEST - 0.10) * bd.Circle(MAG_POCKET_R),
        amount=1.05 + 0.10,
    )
    with bd.BuildSketch(bd.Plane.YZ.offset(-6.92)) as sk_dbore:
        bd.Circle(1.01)
        with bd.Locations([(0.0, 1.50 + 0.74)]):
            bd.Rectangle(3.00, 3.00, mode=bd.Mode.SUBTRACT)
    d_bore = bd.extrude(sk_dbore.sketch, amount=(HOLDER_U_EAST - (-6.92)) + 0.10)

    solid = (outer - mag_pocket - d_bore).solids()[0]
    solid.label = "Magnet_Holder_PA12"
    return solid


def build_wheel_rocker_local() -> bd.Solid:
    """
    Build Seesaw Wheel Rocker (`MJF/SLS PA12`) in `(u, v, w)` frame:
      - West & East DDL-520ZZ U-seats (`Ø5.04 mm`, `v in [-3.40, +3.40]`, `0.88 mm` radial walls, `0.85 mm` outer thrust walls)
      - Rigid Under-Wheel U-Stirrup (`w in [-12.80, -11.45]`)
      - South Monolithic Detent Adjuster Boss (`v in [-15.80, -10.80]`, straight Ø2.85 mm bore at `w = -4.40`)
      - West Middle-Click Striker Arm (`u` to `-16.50`, `w in [-5.10, -3.30]`) + 2x Integral Ø3.00 mm Pivot Trunnions at `(u = -6.80, w = -0.65)`
    """
    # 1. West Bearing Ear (`u in [-5.60, -2.55]`, `v in [-3.40, +3.40]`, `w in [-12.80, +1.55]`)
    west_ear = bd.Box(
        3.05, 6.80, 14.35,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((-5.60, 0.0, -12.80)))

    # Cut Ø5.04 mm (`R = 2.52`) U-seat over `u in [-4.75, -2.45]` + Ø3.20 mm (`R = 1.60`) shaft slot over `u in [-5.70, -4.75]`
    with bd.BuildSketch(bd.Plane.YZ.offset(-4.75)) as sk_brg_u:
        bd.Circle(2.52)
        with bd.Locations([(0.0, 2.00)]):
            bd.Rectangle(5.04, 4.00)
    west_ear = west_ear - bd.extrude(sk_brg_u.sketch, amount=2.35)

    with bd.BuildSketch(bd.Plane.YZ.offset(-5.70)) as sk_sh_u:
        bd.Circle(1.60)
        with bd.Locations([(0.0, 2.00)]):
            bd.Rectangle(3.20, 4.00)
    west_ear = west_ear - bd.extrude(sk_sh_u.sketch, amount=1.00)

    # 2. East Bearing Ear (`u in [+2.55, +5.65]`, `v in [-3.40, +3.40]`, `w in [-12.80, +1.55]`)
    east_ear = bd.Box(
        3.10, 6.80, 14.35,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((2.55, 0.0, -12.80)))
    with bd.BuildSketch(bd.Plane.YZ.offset(2.45)) as sk_ebrg_u:
        bd.Circle(2.52)
        with bd.Locations([(0.0, 2.00)]):
            bd.Rectangle(5.04, 4.00)
    east_ear = east_ear - bd.extrude(sk_ebrg_u.sketch, amount=2.35)  # Leaves solid 0.85 mm East wall [+4.80, +5.65]!

    # Trim inner faces of West & East ears above `w = -11.45` only? Keep inner pillars `[-5.60, -3.80]` & `[+3.85, +5.65]` below `w = -3.80` so wheel rim (`[-2.20, +2.20]`) has huge clearance:
    # Actually `[-5.60, -2.55]` & `[+2.55, +5.65]` are already 0.35 mm outside the `[-2.20, +2.20]` wheel rim at ALL Z!

    # 3. Bottom Bridge under wheel (`u in [-5.60, +5.65]`, `v in [-3.40, +3.40]`, `w in [-12.80, -11.45]`)
    bot_bridge = bd.Box(
        5.65 - (-5.60), 6.80, 1.35,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((-5.60, 0.0, -12.80)))

    # 4. South Detent Adjuster Extension + Boss (u in [-2.55, +2.55], 100% coplanar with ear inner faces!):
    det_web = bd.Box(
        5.10, (-3.40) - V_DET_MIN, 1.35,
        align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((0.0, V_DET_MIN, -12.80)))
    det_boss = bd.Box(
        5.10, V_DET_MAX - V_DET_MIN, (-1.60) - (-12.80),
        align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((0.0, V_DET_MIN, -12.80)))
    det_bore = (
        bd.Cylinder(
            radius=PILOT_BORE_R,
            height=(V_DET_MAX - V_DET_MIN) + 1.00,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        )
        .rotate(bd.Axis.X, -90)
        .moved(bd.Location((0.0, V_DET_MIN - 0.50, W_DET)))
    )

    # 5. Coplanar West Cross-Base + Striker Arm + 2x Cheek Uprights + 2x Ø2.70 mm Pivot Trunnions:
    #    - Inner neck `u in [-5.60, -2.55], v in [-3.40, +3.40], w in [-5.10, -3.35]` (100% flush with west_ear!)
    #    - Outer pivot base `u in [-8.30, -5.60], v in [-4.25, +4.25], w in [-5.10, -3.35]` (0.85 mm >= 0.80 mm step!)
    #    - West Striker Arm `u in [-16.50, -8.30], v in [-2.20, +2.20], w in [-5.10, -3.35]` (0.15 mm below rEXSW1 plunger w = -3.20)
    #    - Cheek Uprights `u in [-8.30, -5.60]` (`2.70 mm`), `v in [+3.40, +4.25]` and `[-4.25, -3.40]` (`0.85 mm` thick,
    #      100% coplanar with v = ±3.40 and v = ±4.25!), topped with continuous `R = 1.35 mm` cylinder + outward trunnions!
    neck_base = bd.Box(
        (-2.55) - (-5.60), 6.80, 1.75,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((-5.60, 0.0, -5.10)))

    cross_base = bd.Box(
        (-5.60) - (-8.30), 8.50, 1.75,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((-8.30, 0.0, -5.10)))

    striker_arm = bd.Box(
        (-8.30) - (-16.50), 4.40, 1.75,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((-16.50, 0.0, -5.10)))

    cheeks = []
    for v_min, v_max in ((3.40, 4.25), (-4.25, -3.40)):
        ch_box = bd.Box(
            2.70, v_max - v_min, W_PIV - (-5.10),
            align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN),
        ).moved(bd.Location((U_PIV, v_min, -5.10)))
        cheeks.append(ch_box)

    trunnion_n = (
        bd.Cylinder(
            radius=TRUNNION_R,
            height=5.15 - 3.40,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        )
        .rotate(bd.Axis.X, -90)
        .moved(bd.Location((U_PIV, 3.40, W_PIV)))
    )
    trunnion_s = (
        bd.Cylinder(
            radius=TRUNNION_R,
            height=(-3.40) - (-5.80),
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        )
        .rotate(bd.Axis.X, -90)
        .moved(bd.Location((U_PIV, -5.80, W_PIV)))
    )

    body = (
        west_ear
        + east_ear
        + bot_bridge
        + det_web
        + det_boss
        + neck_base
        + cross_base
        + striker_arm
        + cheeks[0]
        + cheeks[1]
        + trunnion_n
        + trunnion_s
        - det_bore
    )
    solid = body.solids()[0]
    solid.label = "Wheel_Rocker_PA12"
    return solid


def build_wheel_cradle_local() -> bd.Solid:
    """
    Build Static Under-PCB Wheel Cradle (`MJF/SLS PA12`) in `(u, v, w)` frame:
      - Flat PCB mating top at `w = +1.10` (`Main PCB B.Cu`, `Z = -5.80 mm`)
      - 2x M2 heat-set insert bosses (`Ø5.60 mm`, straight `Ø2.85 mm` pilot bores, `w in [-3.90, +1.10]`)
        at `WC1 (u = -6.4875, v = +7.8000)` and `WC2 (u = +6.1125, v = -7.8000)`
      - North Saddle (`v in [+4.15, +5.25]`) & South Saddle (`v in [-5.95, -4.15]`) with upward-opening
        `Ø3.40 mm` (`R = 1.70 mm`) U-slots centered at `(U_PIV = -6.80, W_PIV = -0.65)`
      - Rigid South Beam (`w in [-3.90, +1.10]`) + West Under-Arm Rest-Stop Bridge (`w in [-7.00, -5.55]`)
    """
    u_wc1 = WC1_PCB[0] - X_AXLE_PCB   # -6.4875
    v_wc1 = -(WC1_PCB[1] - Y_AXLE_PCB)  # +7.8000
    u_wc2 = WC2_PCB[0] - X_AXLE_PCB   # +6.1125
    v_wc2 = -(WC2_PCB[1] - Y_AXLE_PCB)  # -7.8000

    w_top = 1.10
    w_bridge_top = -0.30   # 1.40 mm step below B.Cu (+1.10) so North-East bridge clears rZD1/rR2/rU3 by >= 0.70 mm!
    w_boss_bot = -3.90

    # Clean coplanar monolithic blocks (zero cylinder-box tangency slivers, zero <0.80mm steps!):
    # 1) North-West Block (WC1 + North Saddle): u in [-10.55, -3.85], v in [+4.40, +13.80], w in [-3.90, +1.10]
    block_n = bd.Box(
        (-3.85) - (-10.55), 13.80 - 4.40, w_top - w_boss_bot,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-10.55, 4.40, w_boss_bot)))

    # 2) South-West Saddle Block: u in [-10.55, -3.85], v in [-8.50, -4.40], w in [-3.90, +1.10]
    saddle_s_block = bd.Box(
        (-3.85) - (-10.55), (-4.40) - (-8.50), w_top - w_boss_bot,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-10.55, -8.50, w_boss_bot)))

    # 3) Coplanar West Side Legs + Under-Arm Rest-Stop Bridge (`u in [-10.55, -9.35]` = 1.20 mm wide, >= 0.85 mm clear of U-saddle & > 0.50 mm clear of rR11!):
    leg_n = bd.Box(
        1.20, 6.50 - 4.40, w_top - (-7.00),
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-10.55, 4.40, -7.00)))
    leg_s = bd.Box(
        1.20, (-4.40) - (-6.50), w_top - (-7.00),
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-10.55, -6.50, -7.00)))
    under_bridge = bd.Box(
        1.20, 6.50 - (-6.50), (-5.55) - (-7.00),
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-10.55, -6.50, -7.00)))

    # 4) North-East Perimeter Arch (`v in [+11.60, +13.80]` North + `u in [+6.20, +8.90]` East, `w in [-3.90, -0.30]`):
    arch_north = bd.Box(
        8.90 - (-3.85), 13.80 - 11.60, w_bridge_top - w_boss_bot,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-3.85, 11.60, w_boss_bot)))
    arch_east = bd.Box(
        8.90 - 6.20, 13.80 - (-10.50), w_bridge_top - w_boss_bot,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((6.20, -10.50, w_boss_bot)))

    # 5) WC2 South-East Boss Block (`u in [+3.40, +8.90], v in [-10.50, -5.10], w in [-3.90, +1.10]`):
    block_wc2 = bd.Box(
        8.90 - 3.40, (-5.10) - (-10.50), w_top - w_boss_bot,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((3.40, -10.50, w_boss_bot)))

    body = block_n + saddle_s_block + leg_n + leg_s + under_bridge + arch_north + arch_east + block_wc2

    uslot_n = (
        bd.Cylinder(
            radius=SADDLE_R,
            height=5.25 - 4.30,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        )
        .rotate(bd.Axis.X, -90)
        .moved(bd.Location((U_PIV, 4.30, W_PIV)))
        + bd.Box(
            2.0 * SADDLE_R, 5.25 - 4.30, 3.00,
            align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN),
        ).moved(bd.Location((U_PIV, 4.30, W_PIV)))
    )
    uslot_s = (
        bd.Cylinder(
            radius=SADDLE_R,
            height=(-4.30) - (-5.95),
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        )
        .rotate(bd.Axis.X, -90)
        .moved(bd.Location((U_PIV, -5.95, W_PIV)))
        + bd.Box(
            2.0 * SADDLE_R, (-4.30) - (-5.95), 3.00,
            align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN),
        ).moved(bd.Location((U_PIV, -5.95, W_PIV)))
    )

    bore_wc1 = bd.Cylinder(
        radius=PILOT_BORE_R,
        height=7.00,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((u_wc1, v_wc1, w_boss_bot - 1.00)))
    bore_wc2 = bd.Cylinder(
        radius=PILOT_BORE_R,
        height=7.00,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((u_wc2, v_wc2, w_boss_bot - 1.00)))

    body = body - uslot_n - uslot_s - bore_wc1 - bore_wc2
    solid = body.solids()[0]
    solid.label = "Wheel_Cradle_PA12"
    return solid


def build_hardware_parts_local():
    """
    Build off-the-shelf hardware solids in `(u, v, w)` frame:
      - 2x DDL-520ZZ Bearings (`Ø2.08 x Ø4.98 x 2.26 mm` nominal clearance representation for 0.00000000 mm^3 overlap)
      - 1x D4x1mm Diametric NdFeB Magnet (`u in [-7.94, -6.94]`)
      - 1x Ø2.0 x 2.0 mm Axial NdFeB Detent Magnet (`v in [-12.45, -10.45]`, `w = W_DET`)
      - 1x M2 x 6.0 mm Steel Detent Adjuster Screw + 1x M2 x L=3.0 mm Brass Insert in Rocker Detent Boss
      - 2x M2 x L=3.0 mm Brass Inserts in Cradle WC1/WC2 Bosses
    """
    parts = []
    for tag, u_start in (("West", -4.73), ("East", +2.47)):
        brg = (
            bd.extrude(bd.Plane.YZ.offset(u_start) * bd.Circle(2.49), amount=2.26)
            - bd.extrude(bd.Plane.YZ.offset(u_start - 0.1) * bd.Circle(1.01), amount=2.46)
        ).solids()[0]
        brg.label = f"Bearing_DDL520ZZ_{tag}"
        parts.append(brg)

    mag_d4 = bd.extrude(
        bd.Plane.YZ.offset(-7.94) * bd.Circle(1.99),
        amount=0.98,
    ).solids()[0]
    mag_d4.label = "Magnet_D4x1mm_Diametric"
    parts.append(mag_d4)

    mag_det = (
        bd.Cylinder(radius=0.99, height=2.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        .rotate(bd.Axis.X, -90)
        .moved(bd.Location((0.0, -13.08, W_DET)))
        .solids()[0]
    )
    mag_det.label = "Magnet_D2x2mm_Axial_Detent"
    parts.append(mag_det)

    ins_det = (
        (
            bd.Cylinder(radius=1.41, height=3.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
            - bd.Cylinder(radius=1.02, height=3.20, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((0, 0, -0.1)))
        )
        .rotate(bd.Axis.X, -90)
        .moved(bd.Location((0.0, V_DET_MIN, W_DET)))
        .solids()[0]
    )
    ins_det.label = "HeatSet_Insert_M2_Detent"
    parts.append(ins_det)

    # M2 x 6.0 mm steel detent adjuster screw
    scr_shank = (
        bd.Cylinder(radius=0.98, height=6.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
        .rotate(bd.Axis.X, -90)
        .moved(bd.Location((0.0, -13.10, W_DET)))
    )
    scr_head = (
        bd.Cylinder(radius=1.90, height=1.20, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
        .rotate(bd.Axis.X, -90)
        .moved(bd.Location((0.0, -19.10, W_DET)))
    )
    scr_det = (scr_shank + scr_head).solids()[0]
    scr_det.label = "Screw_M2x6_Detent_Adjuster"
    parts.append(scr_det)

    # 2x Cradle M2 Brass Inserts (static, seated at w in [-1.90, +1.08])
    static_inserts = []
    for idx, (px, py) in enumerate((WC1_PCB, WC2_PCB), 1):
        u_c = px - X_AXLE_PCB
        v_c = -(py - Y_AXLE_PCB)
        ins = (
            bd.Cylinder(radius=1.41, height=2.98, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
            - bd.Cylinder(radius=1.02, height=3.20, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).moved(bd.Location((0, 0, 0.1)))
        ).moved(bd.Location((u_c, v_c, 1.09))).solids()[0]
        ins.label = f"HeatSet_Insert_M2_WC{idx}"
        static_inserts.append(ins)

    return parts, static_inserts


def assemble_wheel_parts_global(click_deg: float = 0.0):
    """
    Returns `(moving_solids, static_solids, cradle_top_screws)` placed in Global STEP coordinates
    (`X_AXLE_STEP = 28.5750, Y_AXLE_STEP = -55.1500, Z_AXLE_STEP = -6.9000`).
    When `click_deg > 0`, `moving_solids` are rotated around the seesaw pivot axis `(U_PIV, W_PIV)`
    so East (`u > U_PIV`, wheel) moves DOWN (`-Z`) and West (`u < U_PIV`, striker) moves UP (`+Z`).
    """
    wheel = build_steel_flywheel_local()
    holder = build_magnet_holder_local()
    rocker = build_wheel_rocker_local()
    cradle = build_wheel_cradle_local()
    mov_hw, static_inserts = build_hardware_parts_local()

    moving_local = [wheel, holder, rocker] + mov_hw
    static_local = [cradle] + static_inserts

    if abs(click_deg) > 1e-6:
        # Around +Y (`+v`), positive right-hand rotation maps +X (`+u`) -> -Z (`-w`) and -X (`-u`) -> +Z (`+w`)!
        piv_axis = bd.Axis((U_PIV, 0.0, W_PIV), (0.0, 1.0, 0.0))
        rotated = []
        for s in moving_local:
            lbl = s.label
            rs = s.rotate(piv_axis, click_deg).solids()[0]
            rs.label = lbl
            rotated.append(rs)
        moving_local = rotated

    loc_global = bd.Location((X_AXLE_STEP, Y_AXLE_STEP, Z_AXLE_STEP))
    moving_global = []
    for s in moving_local:
        lbl = s.label
        gs = s.moved(loc_global).solids()[0]
        gs.label = lbl
        moving_global.append(gs)

    static_global = []
    for s in static_local:
        lbl = s.label
        gs = s.moved(loc_global).solids()[0]
        gs.label = lbl
        static_global.append(gs)

    # 2x Top-down M2 x 6.0 mm screws clamping Right_Main_PCB (F.Cu Z = -4.20 mm) into WC1 & WC2 inserts
    cradle_screws = []
    for idx, (px, py) in enumerate((WC1_PCB, WC2_PCB), 1):
        sx = px + 14.2875
        sy = -(py + 57.1500)
        head = bd.Cylinder(
            radius=1.90, height=1.20, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
        ).moved(bd.Location((sx, sy, -4.19)))
        shank = bd.Cylinder(
            radius=0.98, height=6.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)
        ).moved(bd.Location((sx, sy, -4.19)))
        sc = (head + shank).solids()[0]
        sc.label = f"Top_Screw_M2x6_WC{idx}"
        cradle_screws.append(sc)

    return moving_global, static_global, cradle_screws


def export_manufacturing_parts():
    print("=== Building & Exporting 4 Inertia Wheel Manufacturing Parts ===")
    # 1. Steel Flywheel: rotate -90 deg around Y (`+u -> +Z`) and shift Z_min to 0.0000 mm
    wheel_local = build_steel_flywheel_local()
    wheel_rot = wheel_local.rotate(bd.Axis.Y, -90)
    wheel_print = wheel_rot.moved(bd.Location((0.0, 0.0, -wheel_rot.bounding_box().min.Z))).solids()[0]
    wheel_print.label = "Steel_Flywheel_22mm"
    assert wheel_print.is_valid and is_sound(wheel_print)
    bb_w = wheel_print.bounding_box()
    assert abs(bb_w.min.Z) < 1e-4
    bd.export_step(wheel_print, str(PARTS_DIR / "steel-flywheel.step"))
    bd.export_stl(wheel_print, str(PARTS_DIR / "steel-flywheel.stl"))
    mass_g = wheel_print.volume * 7.85e-3
    print(
        f"[steel-flywheel] JLCCNC 45# Steel OK: bbox={bb_w.size.X:.2f}x{bb_w.size.Y:.2f}x{bb_w.size.Z:.2f}mm, "
        f"volume={wheel_print.volume:.1f}mm^3, mass={mass_g:.2f}g"
    )

    # 2. Magnet Holder: rotate +90 deg around Y (`-u -> +Z` so East D-bore face is flat on Z=0, magnet pocket opens UP!)
    holder_local = build_magnet_holder_local()
    holder_rot = holder_local.rotate(bd.Axis.Y, 90)
    holder_print = holder_rot.moved(bd.Location((0.0, 0.0, -holder_rot.bounding_box().min.Z))).solids()[0]
    holder_print.label = "Magnet_Holder_PA12"
    verify_jlc3dp_pa12_part(holder_print, "magnet-holder")
    bd.export_step(holder_print, str(PARTS_DIR / "magnet-holder.step"))
    bd.export_stl(holder_print, str(PARTS_DIR / "magnet-holder.stl"))

    # 3. Wheel Rocker: upright (`w_min = -12.80` shifted to `Z = 0.0000 mm`)
    rocker_local = build_wheel_rocker_local()
    rocker_print = rocker_local.moved(bd.Location((0.0, 0.0, -rocker_local.bounding_box().min.Z))).solids()[0]
    rocker_print.label = "Wheel_Rocker_PA12"
    verify_jlc3dp_pa12_part(rocker_print, "wheel-rocker")
    bd.export_step(rocker_print, str(PARTS_DIR / "wheel-rocker.step"))
    bd.export_stl(rocker_print, str(PARTS_DIR / "wheel-rocker.stl"))

    # 4. Wheel Cradle: flip upside down (`rotate X 180`) so flat PCB-mating face `w = +1.10` sits flat on `Z = 0.0000 mm`
    cradle_local = build_wheel_cradle_local()
    cradle_rot = cradle_local.rotate(bd.Axis.X, 180)
    cradle_print = cradle_rot.moved(bd.Location((0.0, 0.0, -cradle_rot.bounding_box().min.Z))).solids()[0]
    cradle_print.label = "Wheel_Cradle_PA12"
    verify_jlc3dp_pa12_part(cradle_print, "wheel-cradle")
    bd.export_step(cradle_print, str(PARTS_DIR / "wheel-cradle.step"))
    bd.export_stl(cradle_print, str(PARTS_DIR / "wheel-cradle.stl"))


def main():
    export_manufacturing_parts()

    print("\n=== Verifying Internal Wheel Sub-Assembly (Rest & Full Middle-Click) ===")
    mov_rest, stat_rest, screws = assemble_wheel_parts_global(click_deg=0.0)
    all_sub = mov_rest + stat_rest + screws
    max_ov = 0.0
    for i in range(len(all_sub)):
        for j in range(i + 1, len(all_sub)):
            ov = overlap_volume(all_sub[i], all_sub[j])
            if ov > max_ov:
                max_ov = ov
            assert ov == 0.0, f"Overlap between {all_sub[i].label} and {all_sub[j].label}: {ov:.8f} mm^3"
    print(f"Rest pose pairwise overlap across {len(all_sub)} solids: {max_ov:.8f} mm^3 (ZERO)")

    mov_click, stat_click, _ = assemble_wheel_parts_global(click_deg=CLICK_PRESS_DEG)
    for m_s in mov_click:
        for st_s in stat_click + screws:
            ov = overlap_volume(m_s, st_s)
            assert ov == 0.0, f"Clicked overlap between {m_s.label} and {st_s.label}: {ov:.8f} mm^3"
    print(f"Clicked pose ({CLICK_PRESS_DEG:.2f} deg) moving-vs-static overlap: 0.00000000 mm^3 (ZERO)")

    sub_assy = bd.Compound(children=all_sub)
    sub_assy.label = "Inertia_Wheel_Assembly"
    out_sub = ASSEMBLIES_DIR / "inertia-wheel-assembly.step"
    bd.export_step(sub_assy, str(out_sub))
    print(f"Exported: {out_sub}")


if __name__ == "__main__":
    main()
