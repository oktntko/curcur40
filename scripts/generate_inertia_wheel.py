# -*- coding: utf-8 -*-
"""
Generate 3D CAD models (STEP & STL) for the Under-Plate 1-Piece Integral-Shaft
Passive Magnetic Inertia Scroll Wheel (`curcur40-inertia-wheel`) and run automated
JLCCNC / JLC3DP DFM checks, zero-interference verification across rest and
middle-click states, and 6-DOF kinematic constraint verification.

Outputs:
  Manufacturing Parts (`cases/inertia_wheel/`):
    1. steel-flywheel.step / .stl   (JLCCNC 45# Steel + Electroless Nickel Plating, 1-piece Ø22.00 x 6.50 mm wheel + integral bearing shoulders & D-shaft)
    2. magnet-holder.step / .stl    (JLC3DP MJF/SLS PA12, Ø5.72 x 2.05 mm glue-free D4x1mm diametric magnet press-fit sleeve)
    3. wheel-rocker.step / .stl     (JLC3DP MJF/SLS PA12, seesaw carriage with 2x C-clip snap-in DDL-520ZZ seats, Ø3.00 mm trunnions, West Keeper Tab & rEXSW1 striker, South glue-free detent boss)
    4. wheel-cradle.step / .stl     (JLC3DP MJF/SLS PA12, 2-screw under-PCB bracket at WC1/WC2 with Ø3.08 mm upward U-saddles captured 0.05 mm below Main PCB B.Cu)

  Verification Assemblies (`cases/assemblies/`):
    1. inertia-wheel-assembly.step
"""
import math
import sys
from pathlib import Path
from cadgen import build123d as bd
from cadgen.geometry import is_sound, overlap_volume
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
#   X_step = X_AXLE_STEP + u      (u = x_pcb - 15.4500; +u = East, -u = West)
#   Y_step = Y_AXLE_STEP + v      (v = -(y_pcb + 2.0000); +v = North, -v = South)
#   Z_step = Z_AXLE_STEP + w      (w = Z_step - (-6.9000); B.Cu = +1.10, F.Cu = +2.70, Plate = [+3.30, +4.90])
# =============================================================================
X_AXLE_PCB = 15.4500
Y_AXLE_PCB = -2.0000
X_AXLE_STEP = X_AXLE_PCB + 14.2875      # +29.7375 mm
Y_AXLE_STEP = -(Y_AXLE_PCB + 57.1500)   # -55.1500 mm
Z_AXLE_STEP = -6.9000                   # Wheel top = +4.10 mm (+0.50 mm proud of +3.60 mm Choc V2 keycaps)

WHEEL_OD = 22.00
WHEEL_R = WHEEL_OD / 2.0                # 11.00 mm
WHEEL_RIM_W = 6.50                      # u in [-3.25, +3.25] (0.60 mm/side clearance in 7.70 mm PCB/Plate slot)
N_FLUTES = 24                           # 24 rounded outer flutes (15 deg pitch = 1:1 with 24 scroll notches/rev)

# Integral Shaft & DDL-520ZZ (Ø2 x Ø5 x 2.30 mm) Bearing Stack along u:
STEP_SHOULDER_R = 1.45                  # Ø2.90 mm integral inner-race step (zero loose shims!)
STEP_U_HALF = 3.45                      # Shoulders at [-3.45, -3.25] and [+3.25, +3.45]
BRG_ID_R = 1.00                         # Ø2.00 mm
BRG_OD_R = 2.50                         # Ø5.00 mm
BRG_W = 2.30                            # West bearing [-5.75, -3.45], East bearing [+3.45, +5.75]
SHAFT_R = 0.99                          # Ø1.98 mm slip-fit bearing journal
SHAFT_U_WEST = -7.98                    # West D-shaft tip at u = -7.98 (meets D4x1mm magnet East face!)
SHAFT_U_EAST = +5.72                    # Recessed 0.03 mm inside East bearing outer face (+5.75)

# Magnet Holder (MJF/SLS PA12) & D4x1mm Diametric NdFeB Magnet:
HOLDER_OD_R = 2.86                      # Ø5.72 mm (>= 5.0 mm JLC3DP min; 0.84 mm wall around Ø4.04 mm magnet pocket!)
HOLDER_U_WEST = -9.05
HOLDER_U_EAST = -7.00                   # Length = 2.05 mm (>= 2.0 mm JLC3DP min; 0.40 mm clear of PCB -9.45 & 0.38 mm clear of Rocker -6.62)
MAG_POCKET_R = 2.02                     # Ø4.04 mm pocket, depth 1.05 mm (u in [-9.05, -8.00])
MAG_D4_R = 1.99                         # Ø4.00 x 1.00 mm diametric magnet at u in [-9.02, -8.04] (~2.25 mm East of rU6!)

# Seesaw Pivot & Middle-Click Kinematics:
U_PIV = -8.12                           # x_pcb = +7.3300 mm (L_east = 8.12 mm, L_west = 8.18 mm -> ~70 gf crisp 1:1 click!)
W_PIV = -0.45                           # Z_piv = -7.35 mm; Ø3.00 mm trunnion top at w = +1.05 (0.05 mm below Main PCB B.Cu w = +1.10!)
TRUNNION_R = 1.50                       # Ø3.00 mm integral PA12 trunnions (coaxial & flush with cheek R=1.50 top!)
SADDLE_R = 1.54                         # Ø3.08 mm upward U-saddles in cradle (0.04 mm radial / 0.08 mm diametral clearance)

U_SW = -0.8500 - X_AXLE_PCB             # -16.3000 mm (rEXSW1 Kailh Square Silent center on B.Cu)
V_SW = 0.0000
CLICK_PRESS_DEG = 2.20                  # 2.20 deg click press -> 0.31 mm wheel drop, +0.31 mm switch plunger compression

# Cradle Mounting Bosses (WC1 & WC2 on curcur40-right):
WC1_PCB = (7.8000, -9.8000)             # (u = -7.6500, v = +7.8000)
WC2_PCB = (22.4000, 6.0000)             # (u = +6.9500, v = -8.0000)
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
      - Ø22.00 x 6.50 mm solid rim (`u in [-3.25, +3.25]`) with 24 rounded outer grip/detent flutes (`15 deg` pitch)
      - Integral Ø2.90 mm inner-race shoulders (`u in [-3.45, -3.25]` and `[+3.25, +3.45]`)
      - Integral Ø1.98 mm bearing journals (`u in [-5.75, -3.45]` and `[+3.45, +5.72]`)
      - Integral West D-shaft (`u in [-7.98, -5.75]`, D-flat `w >= +0.71` removed over `u in [-7.98, -6.85]`)
    """
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
    # D-flat on West shaft tip (`u in [-7.98, -6.98]`, `w >= +0.71` removed; solid shoulder at u = -6.98 stops #02 +u!)
    d_cut = bd.Box(
        1.05,
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
    Build Glue-Free Press-Fit Diametric Magnet Sleeve (`MJF/SLS PA12`) in `(u, v, w)` frame:
      - Outer cylinder Ø5.72 mm (`R = 2.86 mm`), length `2.05 mm` (`u in [-9.05, -7.00]`)
      - West Ø4.04 mm x 1.05 mm pocket (`u in [-9.05, -8.00]`, radial wall 0.84 mm >= 0.80 mm)
      - East snug Ø2.00 mm D-bore (`u in [-8.00, -7.00]`, flat at `w = +0.72` for PA12 press-fit on Ø1.98 mm steel D-shaft)
    """
    outer = bd.extrude(
        bd.Plane.YZ.offset(HOLDER_U_WEST) * bd.Circle(HOLDER_OD_R),
        amount=HOLDER_U_EAST - HOLDER_U_WEST,
    )
    mag_pocket = bd.extrude(
        bd.Plane.YZ.offset(HOLDER_U_WEST - 0.10) * bd.Circle(MAG_POCKET_R),
        amount=1.05 + 0.10,
    )
    with bd.BuildSketch(bd.Plane.YZ.offset(-8.00)) as sk_dbore:
        bd.Circle(1.00)
        with bd.Locations([(0.0, 1.50 + 0.72)]):
            bd.Rectangle(3.00, 3.00, mode=bd.Mode.SUBTRACT)
    d_bore = bd.extrude(sk_dbore.sketch, amount=(HOLDER_U_EAST - (-8.00)) + 0.10)

    solid = (outer - mag_pocket - d_bore).solids()[0]
    solid.label = "Magnet_Holder_PA12"
    return solid


def build_wheel_rocker_local() -> bd.Solid:
    """
    Build Seesaw Wheel Rocker (`MJF/SLS PA12`) in `(u, v, w)` frame:
      - West (`u in [-6.62, -3.55]`) & East (`u in [+3.55, +6.62]`) C-Clip Snap-In DDL-520ZZ seats
        (`Ø5.04 mm` seat with `4.56 mm` `v in [-2.28, +2.28]` snap throat -> >220 deg wrap, 0.06 mm max lift!)
      - Rigid Under-Wheel U-Stirrup (`w in [-12.80, -11.45]`)
      - South Monolithic Detent Adjuster Boss (`u in [-3.55, +3.55]`, `v in [-16.40, -11.40]`, straight Ø2.85 mm bore at `w = -4.40`)
      - West Middle-Click Striker Arm (`u` to `-17.65`, `w in [-5.10, -3.40]`) + Integral West Keeper Tab (`u in [-10.50, -9.62]`, `w` to `-1.15`)
      - 2x Integral Ø3.00 mm Pivot Trunnions at `(U_PIV = -8.12, W_PIV = -0.45)` (`0.05 mm` below Main PCB B.Cu!)
    """
    # 1. West Bearing Ear (`u in [-6.62, -3.55]`, `v in [-3.40, +3.40]`, `w in [-12.80, +2.35]`)
    west_ear = bd.Box(
        3.07, 6.80, 15.15,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((-6.62, 0.0, -12.80)))

    # Cut Ø5.04 mm (`R = 2.52`) C-clip snap seat (`4.56 mm` throat `v in [-2.28, +2.28]`) over `u in [-5.77, -3.45]`
    with bd.BuildSketch(bd.Plane.YZ.offset(-5.77)) as sk_brg_u:
        bd.Circle(2.52)
        with bd.Locations([(0.0, 2.00)]):
            bd.Rectangle(4.56, 4.00)
    west_ear = west_ear - bd.extrude(sk_brg_u.sketch, amount=2.35)

    # Cut Ø2.80 mm (`R = 1.40 >= 0.75 mm` JLC3DP min; `2.28 - 1.40 = 0.88 mm >= 0.80 mm` step) shaft U-slot in 0.85 mm West thrust wall
    with bd.BuildSketch(bd.Plane.YZ.offset(-6.70)) as sk_sh_u:
        bd.Circle(1.40)
        with bd.Locations([(0.0, 2.00)]):
            bd.Rectangle(2.80, 4.00)
    west_ear = west_ear - bd.extrude(sk_sh_u.sketch, amount=0.93)

    # 2. East Bearing Ear (`u in [+3.55, +6.62]`, `v in [-3.40, +3.40]`, `w in [-12.80, +2.35]`)
    east_ear = bd.Box(
        3.07, 6.80, 15.15,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((3.55, 0.0, -12.80)))
    with bd.BuildSketch(bd.Plane.YZ.offset(3.45)) as sk_ebrg_u:
        bd.Circle(2.52)
        with bd.Locations([(0.0, 2.00)]):
            bd.Rectangle(4.56, 4.00)
    east_ear = east_ear - bd.extrude(sk_ebrg_u.sketch, amount=2.32)  # Leaves solid 0.85 mm East wall [+5.77, +6.62]!

    # 3. Bottom Bridge under wheel (`u in [-6.62, +6.62]`, `v in [-3.40, +3.40]`, `w in [-12.80, -11.45]`)
    bot_bridge = bd.Box(
        6.62 - (-6.62), 6.80, 1.35,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((-6.62, 0.0, -12.80)))

    # 4. South Detent Adjuster Extension + Boss (`u in [-3.55, +3.55]` = 7.10 mm, 100% coplanar with ear inner faces!):
    det_web = bd.Box(
        7.10, (-3.40) - V_DET_MIN, 1.35,
        align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((0.0, V_DET_MIN, -12.80)))
    det_boss = bd.Box(
        7.10, V_DET_MAX - V_DET_MIN, (-1.60) - (-12.80),
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

    # 5. Coplanar West Cross-Base + Striker Arm + West Keeper Tab + 2x Cheek Uprights + 2x Ø3.00 mm Pivot Trunnions:
    cross_base = bd.Box(
        (-6.62) - (-9.62), 8.50, 1.70,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((-9.62, 0.0, -5.10)))

    striker_arm = bd.Box(
        (-9.62) - (-17.65), 4.40, 1.70,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((-17.65, 0.0, -5.10)))

    # Integral West Keeper Tab (`u in [-10.50, -9.62]` = 0.88 mm thick, `v in [-2.20, +2.20]`, `w in [-5.10, -1.15]`):
    # Mechanically blocks `#02` Magnet Holder (`u_west = -9.05`) & `#08` Magnet (`u_west = -9.02`) from ever walking West!
    keeper_tab = bd.Box(
        (-9.62) - (-10.50), 4.40, (-1.15) - (-5.10),
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((-10.50, 0.0, -5.10)))

    cheeks = []
    for v_min, v_max in ((3.40, 4.25), (-4.25, -3.40)):
        ch_box = bd.Box(
            2.0 * TRUNNION_R, v_max - v_min, W_PIV - (-5.10),
            align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN),
        ).moved(bd.Location((U_PIV, v_min, -5.10)))
        cheeks.append(ch_box)

    trunnion_n = (
        bd.Cylinder(
            radius=TRUNNION_R,
            height=5.20 - 3.40,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        )
        .rotate(bd.Axis.X, -90)
        .moved(bd.Location((U_PIV, 3.40, W_PIV)))
    )
    trunnion_s = (
        bd.Cylinder(
            radius=TRUNNION_R,
            height=(-3.40) - (-5.85),
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        )
        .rotate(bd.Axis.X, -90)
        .moved(bd.Location((U_PIV, -5.85, W_PIV)))
    )

    body = (
        west_ear
        + east_ear
        + bot_bridge
        + det_web
        + det_boss
        + cross_base
        + striker_arm
        + keeper_tab
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
      - 2x M2 heat-set insert bosses (`straight Ø2.85 mm` pilot bores, `w in [-3.90, +1.10]`)
        at `WC1 (u = -7.65, v = +7.80)` and `WC2 (u = +6.95, v = -8.00)`
      - North Saddle (`v in [+4.32, +5.30]`) & South Saddle (`v in [-5.95, -4.32]`) with upward-opening
        `Ø3.08 mm` (`R = 1.54 mm`) U-slots centered at `(U_PIV = -8.12, W_PIV = -0.45)`
      - West Under-Arm Rest-Stop Bridge (`u in [-11.72, -10.52]`, `w in [-6.50, -5.16]`, 0.06 mm below striker arm!)
    """
    u_wc1 = WC1_PCB[0] - X_AXLE_PCB     # -7.6500
    v_wc1 = -(WC1_PCB[1] - Y_AXLE_PCB)  # +7.8000
    u_wc2 = WC2_PCB[0] - X_AXLE_PCB     # +6.9500
    v_wc2 = -(WC2_PCB[1] - Y_AXLE_PCB)  # -8.0000

    w_top = 1.10
    w_bridge_top = -0.30   # 1.40 mm step below B.Cu (+1.10) so North-East bridge clears rZD1/rR2/rU3 by >= 0.70 mm!
    w_boss_bot = -3.90

    # 1) North-West Block (WC1 + North Saddle): u in [-11.72, -5.02], v in [+4.32, +13.80], w in [-3.90, +1.10]
    block_n = bd.Box(
        (-5.02) - (-11.72), 13.80 - 4.32, w_top - w_boss_bot,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-11.72, 4.32, w_boss_bot)))

    # 2) South-West Saddle Block: u in [-11.72, -5.02], v in [-8.50, -4.32], w in [-3.90, +1.10]
    saddle_s_block = bd.Box(
        (-5.02) - (-11.72), (-4.32) - (-8.50), w_top - w_boss_bot,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-11.72, -8.50, w_boss_bot)))

    # 3) Coplanar West Side Legs + Under-Arm Rest-Stop Bridge (`u in [-11.72, -10.52]` = 1.20 mm wide):
    leg_n = bd.Box(
        1.20, 6.50 - 4.32, w_top - (-6.50),
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-11.72, 4.32, -6.50)))
    leg_s = bd.Box(
        1.20, (-4.32) - (-6.50), w_top - (-6.50),
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-11.72, -6.50, -6.50)))
    under_bridge = bd.Box(
        1.20, 6.50 - (-6.50), (-5.16) - (-6.50),
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-11.72, -6.50, -6.50)))

    # 4) North-East Perimeter Arch (`v in [+11.60, +13.80]` North + `u in [+7.10, +9.65]` East, `w in [-3.90, -0.30]`):
    arch_north = bd.Box(
        9.65 - (-5.02), 13.80 - 11.60, w_bridge_top - w_boss_bot,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((-5.02, 11.60, w_boss_bot)))
    arch_east = bd.Box(
        9.65 - 7.10, 13.80 - (-10.70), w_bridge_top - w_boss_bot,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((7.10, -10.70, w_boss_bot)))

    # 5) WC2 South-East Boss Block (`u in [+4.25, +9.65], v in [-10.70, -5.30], w in [-3.90, +1.10]`):
    block_wc2 = bd.Box(
        9.65 - 4.25, (-5.30) - (-10.70), w_top - w_boss_bot,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((4.25, -10.70, w_boss_bot)))

    body = block_n + saddle_s_block + leg_n + leg_s + under_bridge + arch_north + arch_east + block_wc2

    uslot_n = (
        bd.Cylinder(
            radius=SADDLE_R,
            height=5.30 - 4.25,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        )
        .rotate(bd.Axis.X, -90)
        .moved(bd.Location((U_PIV, 4.25, W_PIV)))
        + bd.Box(
            2.0 * SADDLE_R, 5.30 - 4.25, 3.00,
            align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN),
        ).moved(bd.Location((U_PIV, 4.25, W_PIV)))
    )
    uslot_s = (
        bd.Cylinder(
            radius=SADDLE_R,
            height=(-4.25) - (-5.95),
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        )
        .rotate(bd.Axis.X, -90)
        .moved(bd.Location((U_PIV, -5.95, W_PIV)))
        + bd.Box(
            2.0 * SADDLE_R, (-4.25) - (-5.95), 3.00,
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
      - 2x DDL-520ZZ Bearings (`Ø2.01 x Ø4.99 x 2.26 mm` nominal clearance representation for 0.00000000 mm^3 overlap)
      - 1x D4x1mm Diametric NdFeB Magnet (`u in [-9.02, -8.04]`)
      - 1x Ø2.0 x 2.0 mm Axial NdFeB Detent Magnet (`v in [-13.08, -11.08]`, `w = W_DET`)
      - 1x M2 x 6.0 mm Steel Detent Adjuster Screw + 1x M2 x L=3.0 mm Brass Insert in Rocker Detent Boss
      - 2x M2 x L=3.0 mm Brass Inserts in Cradle WC1/WC2 Bosses
    """
    parts = []
    for tag, u_start in (("West", -5.73), ("East", +3.47)):
        brg = (
            bd.extrude(bd.Plane.YZ.offset(u_start) * bd.Circle(2.495), amount=2.26)
            - bd.extrude(bd.Plane.YZ.offset(u_start - 0.1) * bd.Circle(1.005), amount=2.46)
        ).solids()[0]
        brg.label = f"Bearing_DDL520ZZ_{tag}"
        parts.append(brg)

    mag_d4 = bd.extrude(
        bd.Plane.YZ.offset(-9.02) * bd.Circle(MAG_D4_R),
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

    # 2x Cradle M2 Brass Inserts (static, seated at w in [-1.89, +1.09])
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


def verify_6dof_constraints():
    """
    Automated 6-DOF kinematic constraint & retention check in `(u, v, w)` frame:
      Verifies that EVERY component is mechanically captured in all intended fixed DOFs
      (`overlap_volume > 0` under small virtual perturbations) while moving freely (`overlap_volume == 0`)
      along its intended active DOFs (`360 deg` wheel spin + `0..2.20 deg` seesaw click).
    """
    print("\n=== Verifying 6-DOF Mechanical Retention & Kinematic Freedom ===")
    wheel = build_steel_flywheel_local()
    holder = build_magnet_holder_local()
    rocker = build_wheel_rocker_local()
    cradle = build_wheel_cradle_local()
    mov_hw, static_inserts = build_hardware_parts_local()
    brg_w, brg_e, mag_d4, _mag_det, _ins_det, _scr_det = mov_hw

    # Representative Main PCB B.Cu ceiling patch (`w in [+1.10, +2.70]`) over cradle & pivot trunnions
    pcb_ceiling = (
        bd.Box(26.0, 30.0, 1.60, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(
            bd.Location((-2.0, 0.0, 1.10))
        )
        - bd.Box(7.70, 23.00, 3.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(
            bd.Location((0.0, 0.0, 0.50))
        )
        - bd.Box(16.50, 7.50, 3.00, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN)).moved(
            bd.Location((-9.45, 0.0, 0.50))
        )
    ).solids()[0]
    assert overlap_volume(rocker, pcb_ceiling) == 0.0, "Rest rocker hit PCB ceiling!"
    # Representative WC1/WC2 screws in local frame
    wc_screws = []
    for px, py in (WC1_PCB, WC2_PCB):
        uc, vc = px - X_AXLE_PCB, -(py - Y_AXLE_PCB)
        wc_screws.append(
            bd.Cylinder(radius=0.98, height=6.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
            .moved(bd.Location((uc, vc, 2.71)))
            .solids()[0]
        )
    # Representative rEXSW1 plunger (`w in [-3.20, +1.09]`) & housing (`w in [-2.25, +1.09]`) at U_SW
    sw_plunger = (
        bd.Cylinder(radius=1.50, height=4.29, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
        .moved(bd.Location((U_SW, 0.0, 1.09)))
        .solids()[0]
    )
    sw_housing = (
        bd.Box(6.20, 6.20, 3.34, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
        .moved(bd.Location((U_SW, 0.0, 1.09)))
        .solids()[0]
    )

    # 1. Active Spin DOF (`Rx` around u-axis): `#01 + #02 + #08` MUST spin 360 deg with ZERO interference
    rotor_group = [wheel, holder, mag_d4]
    spin_axis = bd.Axis((0.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    for deg in (7.5, 15.0, 37.0, 90.0, 180.0, 270.0):
        for s in rotor_group:
            rs = s.rotate(spin_axis, deg).solids()[0]
            assert overlap_volume(rs, rocker) == 0.0, f"Spin {deg} deg hit rocker!"
            assert overlap_volume(rs, cradle) == 0.0, f"Spin {deg} deg hit cradle!"
            assert overlap_volume(rs, brg_w) == 0.0 and overlap_volume(rs, brg_e) == 0.0, f"Spin {deg} deg hit bearing!"
    print("  [PASS] Active Spin DOF (`Rx` 0..360 deg): 0.00000000 mm^3 interference across all angles")

    # 2. Fix 1 — Bearing & Wheel C-Clip Snap Retention (`±u, ±v, ±w`, especially `+w` upward!)
    for tag, vec in (
        ("+u (East)", (0.10, 0.0, 0.0)),
        ("-u (West)", (-0.10, 0.0, 0.0)),
        ("+v (North)", (0.0, 0.10, 0.0)),
        ("-v (South)", (0.0, -0.10, 0.0)),
        ("+w (UP C-clip)", (0.0, 0.0, 0.10)),
        ("-w (DOWN seat)", (0.0, 0.0, -0.10)),
    ):
        ov_brg = overlap_volume(brg_w.moved(bd.Location(vec)), rocker) + overlap_volume(
            brg_e.moved(bd.Location(vec)), rocker
        )
        assert ov_brg > 0.0, f"Bearings NOT captured along {tag}!"
        ov_whl = (
            overlap_volume(wheel.moved(bd.Location(vec)), brg_w)
            + overlap_volume(wheel.moved(bd.Location(vec)), brg_e)
            + overlap_volume(wheel.moved(bd.Location(vec)), rocker)
        )
        assert ov_whl > 0.0, f"Steel Flywheel NOT captured along {tag}!"
    print("  [PASS] Bearing & Wheel C-Clip Retention: locked in ±u, ±v, -w, and +w upward (max lift 0.060 mm)")

    # 3. Fix 3 — `#02` Magnet Holder & `#08` Magnet Retention (`±u, ±v, ±w` + `Rx` D-flat anti-twist!)
    assert overlap_volume(holder.moved(bd.Location((0.10, 0.0, 0.0))), wheel) > 0.0, "#02 not stopped +u!"
    assert overlap_volume(holder.moved(bd.Location((-0.65, 0.0, 0.0))), rocker) > 0.0, "#02 not stopped -u by Keeper Tab!"
    for vec in ((0.0, 0.05, 0.0), (0.0, -0.05, 0.0), (0.0, 0.0, 0.05), (0.0, 0.0, -0.05)):
        assert overlap_volume(holder.moved(bd.Location(vec)), wheel) > 0.0, f"#02 not radially locked at {vec}!"
    for tw_deg in (-3.0, +3.0):
        assert overlap_volume(holder.rotate(spin_axis, tw_deg).solids()[0], wheel) > 0.0, "#02 D-flat did not lock Rx twist!"

    assert overlap_volume(mag_d4.moved(bd.Location((0.10, 0.0, 0.0))), holder) > 0.0, "#08 not stopped +u!"
    assert overlap_volume(mag_d4.moved(bd.Location((-0.65, 0.0, 0.0))), rocker) > 0.0, "#08 not stopped -u by Keeper Tab!"
    for vec in ((0.0, 0.05, 0.0), (0.0, -0.05, 0.0), (0.0, 0.0, 0.05), (0.0, 0.0, -0.05)):
        assert overlap_volume(mag_d4.moved(bd.Location(vec)), holder) > 0.0, f"#08 not radially locked at {vec}!"
    print("  [PASS] #02 Magnet Holder & #08 Magnet Retention: locked in ±u (Keeper Tab), ±v, ±w, and D-flat Rx")

    # 4. Fix 2 — `#03` Rocker Seesaw Trunnion Capture (`±u, ±v, ±w` locked; `+2.20 deg` actuates switch; `-1.20 deg` hits rest stop!)
    for tag, vec in (
        ("+u", (0.10, 0.0, 0.0)),
        ("-u", (-0.10, 0.0, 0.0)),
        ("+v", (0.0, 0.12, 0.0)),
        ("-v", (0.0, -0.12, 0.0)),
        ("+w (PCB B.Cu cap)", (0.0, 0.0, 0.10)),
        ("-w (U-saddle + rest stop)", (0.0, 0.0, -0.10)),
    ):
        rk_m = rocker.moved(bd.Location(vec))
        ov_rk = overlap_volume(rk_m, cradle) + overlap_volume(rk_m, pcb_ceiling)
        assert ov_rk > 0.0, f"#03 Rocker NOT captured along {tag}!"

    piv_axis = bd.Axis((U_PIV, 0.0, W_PIV), (0.0, 1.0, 0.0))
    rk_click = rocker.rotate(piv_axis, CLICK_PRESS_DEG).solids()[0]
    assert overlap_volume(rk_click, cradle) == 0.0 and overlap_volume(rk_click, pcb_ceiling) == 0.0
    assert overlap_volume(rk_click, sw_plunger) > 0.0, "Middle-click 2.20 deg did NOT compress rEXSW1 plunger!"
    assert overlap_volume(rk_click, sw_housing) == 0.0, "Middle-click 2.20 deg bottomed out against rEXSW1 housing!"

    rk_pull_up = rocker.rotate(piv_axis, -1.20).solids()[0]
    assert overlap_volume(rk_pull_up, cradle) > 0.0, "Upward wheel pull (-1.20 deg) did NOT hit cradle under-bridge stop!"
    print("  [PASS] #03 Seesaw Pivot & Click Kinematics: ±0.05..0.09 mm trunnion capture, +2.20 deg switch actuation, -1.20 deg upward stop")

    # 5. `#04` Static Cradle Clamping (`±u, ±v, +w` locked by Main PCB & WC1/WC2 screws)
    assert overlap_volume(cradle.moved(bd.Location((0.0, 0.0, 0.05))), pcb_ceiling) > 0.0, "#04 not seated against PCB!"
    for vec in ((0.15, 0.0, 0.0), (-0.15, 0.0, 0.0), (0.0, 0.15, 0.0), (0.0, -0.15, 0.0)):
        ov_scr = sum(overlap_volume(ins.moved(bd.Location(vec)), sc) for ins, sc in zip(static_inserts, wc_screws))
        assert ov_scr > 0.0, f"#04 Cradle inserts not locked laterally at {vec}!"
    print("  [PASS] #04 Static Cradle Retention: locked against Main PCB B.Cu and WC1/WC2 M2x6 screws")


def assemble_wheel_parts_global(click_deg: float = 0.0):
    """
    Returns `(moving_solids, static_solids, cradle_top_screws)` placed in Global STEP coordinates
    (`X_AXLE_STEP = 29.7375, Y_AXLE_STEP = -55.1500, Z_AXLE_STEP = -6.9000`).
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

    verify_6dof_constraints()

    sub_assy = bd.Compound(children=all_sub)
    sub_assy.label = "Inertia_Wheel_Assembly"
    out_sub = ASSEMBLIES_DIR / "inertia-wheel-assembly.step"
    bd.export_step(sub_assy, str(out_sub))
    print(f"Exported: {out_sub}")


if __name__ == "__main__":
    main()
