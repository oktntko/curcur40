# -*- coding: utf-8 -*-
"""
Generate curcur40 1-Piece Snap-In PA12 Carrying Frame (`cases/carrying-frame.step`, `cases/carrying-frame.stl`)
and Full Packed Verification Assembly (`cases/assemblies/carrying-assembly.step`).

Strictly adheres to `docs/case_spec.md` Section 6 & `AGENTS.md` Section 4:
- Wedge-Canceling Face-to-Face Architecture (`Rot_X(180 deg)`):
    - Right keyboard (`right.step`) at canonical bottom pose (Rim Z = 0.00 mm, tenting 7.473 deg)
    - Left keyboard (`left.step`) rotated 180 deg about X-axis + translated (+142.8830, -157.4875, +19.5000) mm
    - Left & Right 7.473 deg built-in tenting planes become 100% mathematically parallel (55.92 mm bare brick
      thickness, 59.92 mm uniform total thickness including 2.00 mm rubber feet on both outer bottoms)
- All 4 USB-C Ports 100% Open for Permanent Magnetic USB-C Tips (`CIO-SLMG-T-C`, ~12.3 x 7.0 mm):
    - Wide 18.00 mm open U-notches (up to the seating plane Z = +0.05 / +19.45 mm, R = 1.00 mm arch corners)
      at all 4 USB-C locations (Right `rJ1`/`rJ2` & Left `J1`/`J2`)
    - Zero dust shutters or port-interior lugs: allows straight-in vertical push-to-lock and pull-to-release
      with all 4 `CIO-SLMG-T-C` magnetic tips permanently installed (>= 2.30 mm clearance all around)
- Symmetric Dual One-Touch Cantilever Paddle Latches (Thumb + Pinky on Both Halves, Zero Rubber-Foot Interference):
    - Push straight in from above/below to self-cam & snap-lock; pull both paddles (~1 mm) to release
    - Pinky 20.00 mm wide PA12 cantilever paddle latch (`Y in [-82.00, -62.00]` on Right)
    - Thumb 20.00 mm wide PA12 cantilever paddle latch + local side-skirt support apron (`Y in [-65.00, -45.00]`
      on Right, 12.65 mm clear north of Split USB-C U-notch) matching Pinky spring stiffness (~10-11 N/mm)
    - Latch bases are coplanar with the 7.473 deg brick plane (0.35 mm clear inside the 2.00 mm rubber-foot plane),
      so `carrying-frame.step` sits flat on Z = 0.0000 mm at all 4 latch corners with 59.22 mm print height
- Internal Non-Contact Protection & 100% Cavity Enclosure:
    - Rim-to-rim perimeter seating ledges (Z = +0.05 mm & +19.45 mm) carry all loads through the PA12 case rims
    - Annular Trackball Keeper Halo Ring (D 15.60 mm ID / D 22.00 mm OD, Z = +12.80..+15.10 mm) holds a 0.58 mm
      non-contact gap over the 25mm ball at rest and limits shock lift to <= 0.73 mm
    - Point-symmetric NW & SE L-cutout protective corner shields (2.00 mm thick) seal all 40 keys & inertia wheel
- Automated Preflight & Full-Assembly Verification:
    - JLC3DP MJF/SLS PA12 rules: single watertight manifold solid, Z = 0.0000 mm base, concave bore >= D 1.50 mm,
      and ZERO `< 0.80 mm` thin-wall/micro-gap face pairs (0 exclusions)
    - Zero B-rep overlap (`0.00000000 mm^3`) across all 674 KiCad-synchronized keyboard solids + 10 rubber feet
      + 4 `CIO-SLMG-T-C` magnetic USB-C tips (both at rest and along straight vertical entry/exit!)
    - Exact surface clearance & 6-DOF mechanical retention assertions
"""
from __future__ import annotations

import math
import sys
from pathlib import Path
from cadgen import build123d as bd
from cadgen.geometry import is_sound, overlap_volume
from OCP.BRep import BRep_Builder
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.GeomAbs import GeomAbs_Cylinder
from OCP.TopAbs import TopAbs_REVERSED
from OCP.TopoDS import TopoDS_Compound

WORKSPACE = Path(__file__).resolve().parent.parent
if str(WORKSPACE / "scripts") not in sys.path:
    sys.path.insert(0, str(WORKSPACE / "scripts"))

CASES_DIR = WORKSPACE / "cases"
ASSEMBLIES_DIR = WORKSPACE / "cases" / "assemblies"

# Canonical geometry constants (matching `scripts/generate_cases.py` & `docs/case_spec.md` Sec. 6)
X_THUMB_OUTER = 7.0250
X_PINKY_OUTER = 135.8580
Y_NORTH_OUTER = -30.8375
Y_SOUTH_OUTER = -126.6500
X_STEP_R = 98.7500
Y_STEP_R = -100.1316

Z_THUMB_BOTTOM = -26.9000
Z_PINKY_BOTTOM = -10.0000
TAN_TENT = (Z_PINKY_BOTTOM - Z_THUMB_BOTTOM) / (X_PINKY_OUTER - X_THUMB_OUTER)
THETA_TENT_RAD = math.atan(TAN_TENT)
THETA_TENT_DEG = math.degrees(THETA_TENT_RAD)

# Wedge-canceling `Rot_X(180 deg)` transformation parameters
H_SEP = 19.5000
DX_LEFT = X_THUMB_OUTER + X_PINKY_OUTER      # +142.8830 mm
DY_LEFT = Y_NORTH_OUTER + Y_SOUTH_OUTER      # -157.4875 mm
MID_X = 0.5 * DX_LEFT                        #  +71.4415 mm
MID_Y = 0.5 * DY_LEFT                        #  -78.74375 mm
MID_Z = 0.5 * H_SEP                          #   +9.7500 mm

# Frame clearances & wall thicknesses
Z_SEAT_GAP = 0.0500       # Nominal 0.05 mm B-rep seating air film at Z = +0.05 mm and +19.45 mm
XY_FIT_GAP = 0.2500       # Static perimeter fit clearance (>= 0.20 mm JLC3DP rule)
SKIRT_WALL = 2.0000       # 2.00 mm outer skirt wall thickness
SKIRT_DEPTH = 2.4000      # Skirt overlap onto case walls (Z = -2.40 mm on Right, +21.90 mm on Left)
SHIELD_THICK = 2.0000     # 2.00 mm protective corner shields over NW & SE L-cutouts

# USB-C port centers & open U-notch width for permanent `CIO-SLMG-T-C` (~12.3 x 7.0 mm) magnetic tips
HOST_USBC_CX_R = 26.5750
SPLIT_USBC_CY_R = -86.6500
USBC_CENTER_Z_R = -5.8500
USBC_NOTCH_WIDTH = 18.0000    # +-9.00 mm around port center (>= 2.80 mm side clearance for 12.3 mm CIO tip)

# CIO-SLMG-T-C magnetic USB-C tip verification envelope (`~12.3 x 7.0 mm` head, protruding `3.80 mm` outside case)
CIO_TIP_WIDTH = 12.4000
CIO_TIP_HEIGHT = 7.0000
CIO_TIP_PROTRUSION = 3.8000

# Trackball coordinates & Keeper Halo Ring parameters
TB_CX = 23.8125
TB_CY = -109.5375
BALL_CZ = 2.3000
BALL_RADIUS = 12.5000
HALO_R_IN = 7.8000        # D 15.60 mm inner bore
HALO_R_OUT = 11.0000      # D 22.00 mm outer ring
HALO_Z_MIN = 12.8000      # 0.58 mm radial rest gap to D 25.00 mm ball
HALO_Z_MAX = 15.1000      # 2.30 mm thick ring, 0.80 mm clear below Left keycaps (+15.90 mm)

# Rubber foot specification (`docs/buildguide_jp.md`: D 6-8 mm, thickness 1.5-2.0 mm)
RUBBER_FOOT_RADIUS = 4.0000   # D 8.00 mm
RUBBER_FOOT_HEIGHT = 2.0000   # 2.00 mm height
LATCH_BASE_PERP_OFFSET = 1.6500  # Coplanar latch base offset (0.35 mm clear inside 2.00 mm rubber-foot plane)


def z_case_bottom_right(x: float) -> float:
    """Exact Z coordinate on Right keyboard's angled outer bottom plane at X."""
    return Z_THUMB_BOTTOM + (x - X_THUMB_OUTER) * TAN_TENT


def z_latch_base_right(x: float) -> float:
    """Coplanar latch base line parallel to Right's outer bottom (`Z_desk = +0.3500 mm` flat horizontal!)."""
    return z_case_bottom_right(x) - LATCH_BASE_PERP_OFFSET / math.cos(THETA_TENT_RAD)


def make_filleted_sketch(pts_and_radii: list[tuple[float, float, float]]) -> bd.Sketch:
    with bd.BuildSketch() as sk:
        pts = [(p[0], p[1]) for p in pts_and_radii]
        bd.Polygon(pts)
        for x, y, r in pts_and_radii:
            if r > 0.05:
                v_target = sk.vertices().filter_by(
                    lambda v, tx=x, ty=y: abs(v.X - tx) < 0.2 and abs(v.Y - ty) < 0.2
                )
                if len(v_target) > 0:
                    bd.fillet(v_target, radius=r)
    return sk.sketch


def get_right_offset_pts(outward_offset: float, r_convex: float, r_concave: float) -> list[tuple[float, float, float]]:
    """
    Polygon for Right keyboard outer perimeter expanded outward by `outward_offset` mm.
    (`outward_offset = -1.50` reproduces `get_inner_pts(True)`).
    """
    d = outward_offset
    return [
        (X_THUMB_OUTER - d, Y_NORTH_OUTER + d, r_convex),
        (X_PINKY_OUTER + d, Y_NORTH_OUTER + d, r_convex),
        (X_PINKY_OUTER + d, Y_STEP_R - d, r_convex),
        (X_STEP_R + d, Y_STEP_R - d, r_concave),
        (X_STEP_R + d, Y_STEP_R - d if False else Y_SOUTH_OUTER - d, r_convex),
        (X_THUMB_OUTER - d, Y_SOUTH_OUTER - d, r_convex),
    ]


def invert_pts_for_left_top(pts_and_radii: list[tuple[float, float, float]]) -> list[tuple[float, float, float]]:
    """Point-invert 2D polygon `(X, Y) -> (DX_LEFT - X, DY_LEFT - Y)` for Transformed Left (`P_L'`)."""
    return [(DX_LEFT - x, DY_LEFT - y, r) for x, y, r in pts_and_radii]


def transform_left_to_packed(shape: bd.Shape) -> bd.Shape:
    """
    Rigid 3D transformation (`det = +1`) placing a Left keyboard solid (`left.step` frame)
    face-to-face onto the Right keyboard via `Rot_X(180 deg)` + `(DX_LEFT, DY_LEFT, H_SEP)`.
    """
    lbl = getattr(shape, "label", "")
    loc = bd.Pos(DX_LEFT, DY_LEFT, H_SEP) * bd.Rot(180.0, 0.0, 0.0)
    moved_wrapped = shape.wrapped.Moved(loc.wrapped)
    if isinstance(shape, bd.Solid):
        res = bd.Solid(moved_wrapped)
    elif isinstance(shape, bd.Face):
        res = bd.Face(moved_wrapped)
    else:
        res = shape.moved(loc)
    res.label = lbl
    return res


def transform_packed_to_desk(shape: bd.Shape) -> bd.Shape:
    """
    Rotate the packed parallel brick by `+THETA_TENT_DEG` (+7.473 deg) around Y and shift in Z
    so the bottom rubber feet rest flat on `Z = 0.0000 mm` (bare Right bottom sits at `Z = +2.0000 mm`,
    and both Thumb & Pinky bottom latch bases sit coplanar at `Z = +0.3500 mm`).
    """
    lbl = getattr(shape, "label", "")
    children = getattr(shape, "children", None)
    if children:
        res = bd.Compound(children=[transform_packed_to_desk(ch) for ch in children])
        res.label = lbl
        return res
    loc = (
        bd.Pos(X_PINKY_OUTER, 0.0, RUBBER_FOOT_HEIGHT)
        * bd.Rot(0.0, THETA_TENT_DEG, 0.0)
        * bd.Pos(-X_PINKY_OUTER, 0.0, -Z_PINKY_BOTTOM)
    )
    moved_wrapped = shape.wrapped.Moved(loc.wrapped)
    if isinstance(shape, bd.Solid):
        res = bd.Solid(moved_wrapped)
    elif isinstance(shape, bd.Face):
        res = bd.Face(moved_wrapped)
    else:
        res = shape.moved(loc)
    res.label = lbl
    return res


def build_pinky_paddle_latch_right() -> tuple[bd.Solid, bd.Solid]:
    """
    Builds the Right-keyboard Pinky (East `X = 135.8580 mm`, `Y in [-82.00, -62.00]`) PA12 cantilever
    spring paddle latch solid AND its relief-slot cutter (`Y in [-84.00, -60.00]`).
    Bottom outer face lies on `z_latch_base_right(X)` so it becomes horizontal `Z = 0.0000 mm` in desk pose.
    """
    y_center = -72.0000
    latch_w = 20.0000
    slot_w = 2.0000
    total_cut_w = latch_w + 2.0 * slot_w  # 24.00 mm: Y in [-84.00, -60.00]
    z_root = 5.0000                       # Straight slot up to +5.00 mm + R=1.00 mm top round -> +6.00 mm

    cut_box = bd.Box(
        12.00,
        total_cut_w,
        z_root - (-15.00),
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((137.00, y_center, -15.00)))
    top_slot_edges = cut_box.edges().filter_by(
        lambda e: abs(e.bounding_box().size.X - 12.00) < 0.1
        and abs(e.bounding_box().min.Z - z_root) < 0.05
    )
    assert len(top_slot_edges) == 2, f"Expected 2 top X-edges on pinky latch cutter, got {len(top_slot_edges)}"
    cut_box = bd.fillet(top_slot_edges, radius=1.00)

    x_in = X_PINKY_OUTER + XY_FIT_GAP             # 136.1080 mm (flush with skirt inner wall)
    x_out = x_in + SKIRT_WALL                     # 138.1080 mm (flush with skirt outer wall, 2.00 mm beam)
    x_hook = X_PINKY_OUTER - 1.0000               # 134.8580 mm (1.00 mm inward catch overlap under 1.50 mm wall)
    x_ramp_bot = 135.9800                         # > 135.8580 so straight vertical push-in self-cams open!
    x_paddle = x_out + 1.4000                     # +1.40 mm ergonomic finger release tab (139.5080 mm)

    xz_pts = [
        (x_in, 6.2000),                           # Blends 0.20 mm above slot root into solid frame wall
        (x_out, 6.2000),
        (x_out, -7.6000),
        (x_paddle, -8.8000),                      # 1.84 mm ergonomic upper bevel
        (x_paddle, -10.4000),                     # 1.60 mm vertical paddle tip face
        (x_out, -10.4000),                        # 1.40 mm horizontal finger-grip release ledge
        (x_out, z_latch_base_right(x_out)),       # ~ -11.369 mm (>= 0.96 mm vertical outer lower face)
        (x_ramp_bot, z_latch_base_right(x_ramp_bot)),  # ~ -11.648 mm (coplanar desk-horizontal print base!)
        (x_hook, -11.3000),                       # 1.18 mm angled entry cam ramp
        (x_hook, -10.4300),                       # 0.87 mm vertical inner hook nose (> 0.80 mm!)
        (x_in, -10.4300),                         # 1.25 mm horizontal catch shelf (0.30 mm clear below case)
    ]
    with bd.BuildSketch(bd.Plane.XZ) as sk_arm:
        bd.Polygon(xz_pts, align=None)
    arm_solid = bd.extrude(sk_arm.sketch, amount=latch_w, both=False)
    arm_bb = arm_solid.bounding_box()
    arm_solid = arm_solid.moved(bd.Location((0.0, y_center - arm_bb.center().Y, 0.0)))

    return arm_solid, cut_box


def build_thumb_paddle_latch_right() -> tuple[bd.Solid, bd.Solid, bd.Solid]:
    """
    Builds the Right-keyboard Thumb (West `X = 7.0250 mm`, `Y in [-65.00, -45.00]`, 12.65 mm clear north
    of the Split USB-C U-notch) PA12 support apron, cantilever spring paddle latch, and relief-slot cutter.
    - Support apron (`Y in [-73.00, -37.00]`, `Z in [-10.00, +0.05]`) brings the slot ceiling to `Z = -7.50 mm`,
      giving a 19.75 mm free cantilever length that matches the Pinky latch spring stiffness (~10-11 N/mm).
    - Bottom outer face lies on `z_latch_base_right(X)` so BOTH Thumb & Pinky latch bases sit flat on Z = 0.0000 mm!
    """
    y_center = -55.0000
    latch_w = 20.0000
    slot_w = 2.0000
    total_cut_w = latch_w + 2.0 * slot_w  # 24.00 mm: Y in [-67.00, -43.00]
    apron_w = 36.0000                     # Y in [-73.00, -37.00] (6.00 mm solid wings on each side!)
    z_apron_bot = -10.5000                # Leaves 2.00 mm straight wall below -8.50 mm slot fillet bottom!
    z_slot_top_straight = -7.5000         # Filleted by R=1.00 mm -> rounds from -7.50 down to -8.50 mm!

    x_in = X_THUMB_OUTER - XY_FIT_GAP     # 6.7750 mm (100% flush with straight West face of `sk_r_in`)
    x_out = x_in - SKIRT_WALL             # 4.7750 mm (100% flush with straight West face of `sk_r_out`)
    x_hook = X_THUMB_OUTER + 1.0000       # 8.0250 mm (1.00 mm inward catch overlap under 1.50 mm Thumb wall)
    x_ramp_bot = 6.9000                   # < 7.0250 so straight vertical push-in self-cams open!
    x_paddle = x_out - 1.4000             # -1.40 mm ergonomic finger release tab (3.3750 mm)

    # 1. Flush West Side-Skirt Support Apron (`X in [4.7750, 6.7750]`, `Y in [-73.00, -37.00]`, `Z in [-10.50, 0.00]`)
    apron_box = bd.Box(
        SKIRT_WALL,
        apron_w,
        0.0000 - z_apron_bot,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((x_out, y_center, z_apron_bot)))
    apron_bot_edges = apron_box.edges().filter_by(
        lambda e: abs(e.bounding_box().size.X - SKIRT_WALL) < 0.1
        and abs(e.bounding_box().max.Z - z_apron_bot) < 0.05
    )
    assert len(apron_bot_edges) == 2, f"Expected 2 bottom X-edges on thumb apron, got {len(apron_bot_edges)}"
    apron_solid = bd.fillet(apron_bot_edges, radius=1.50)

    # 2. Relief-slot cutter (`Y in [-67.00, -43.00]`, top at `Z = -7.50 mm` with D 2.00 mm rounded slot roots)
    cut_box = bd.Box(
        12.00,
        total_cut_w,
        z_slot_top_straight - (-35.00),
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((5.80, y_center, -35.00)))
    top_slot_edges = cut_box.edges().filter_by(
        lambda e: abs(e.bounding_box().size.X - 12.00) < 0.1
        and abs(e.bounding_box().min.Z - z_slot_top_straight) < 0.05
    )
    assert len(top_slot_edges) == 2, f"Expected 2 top X-edges on thumb latch cutter, got {len(top_slot_edges)}"
    cut_box = bd.fillet(top_slot_edges, radius=1.00)

    # 3. Thumb Cantilever Spring Paddle Latch (`Y in [-65.00, -45.00]`)
    xz_pts = [
        (x_in, -7.3000),                          # Blends 0.20 mm above -7.50 mm slot ceiling into West skirt
        (x_out, -7.3000),
        (x_out, -25.0500),
        (x_paddle, -26.2500),                     # 1.84 mm ergonomic upper bevel
        (x_paddle, -27.8500),                     # 1.60 mm vertical paddle tip face
        (x_out, -27.8500),                        # 1.40 mm horizontal finger-grip release ledge
        (x_out, z_latch_base_right(x_out)),       # ~ -28.859 mm (1.01 mm vertical outer lower face)
        (x_ramp_bot, z_latch_base_right(x_ramp_bot)),  # ~ -28.581 mm (coplanar desk-horizontal print base!)
        (x_hook, -28.1200),                       # 1.22 mm angled entry cam ramp
        (x_hook, -27.2500),                       # 0.87 mm vertical inner hook nose (> 0.80 mm!)
        (x_in, -27.2500),                         # 1.25 mm horizontal catch shelf (0.35 mm clear below -26.90 mm)
    ]
    with bd.BuildSketch(bd.Plane.XZ) as sk_arm:
        bd.Polygon(xz_pts, align=None)
    arm_solid = bd.extrude(sk_arm.sketch, amount=latch_w, both=False)
    arm_bb = arm_solid.bounding_box()
    arm_solid = arm_solid.moved(bd.Location((0.0, y_center - arm_bb.center().Y, 0.0)))

    return apron_solid, arm_solid, cut_box


def build_usbc_open_notch_cutters_right() -> list[bd.Solid]:
    """
    Builds 18.00 mm wide open U-notch cutters for Right's two USB-C ports (`rJ1` on North, `rJ2` on West)
    extending up to `Z_SEAT_GAP` (+0.0500 mm) with R = 1.00 mm (D 2.00 mm) smooth tangent arch corners,
    so `CIO-SLMG-T-C` magnetic USB-C tips (~12.3 x 7.0 mm) remain 100% uncovered and pass straight in/out.
    """
    z_bot = -15.0000
    z_straight_top = Z_SEAT_GAP  # +0.0500 mm; filleted by R=1.00 mm -> rounds from +0.05 down to -0.95 mm!

    # 1. Host USB-C (`rJ1`) open notch on North skirt (`X = 26.5750 +- 9.00 mm`)
    host_cut = bd.Box(
        USBC_NOTCH_WIDTH,
        12.00,
        z_straight_top - z_bot,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((HOST_USBC_CX_R, Y_NORTH_OUTER, z_bot)))
    host_edges = host_cut.edges().filter_by(
        lambda e: abs(e.bounding_box().size.Y - 12.00) < 0.1
        and abs(e.bounding_box().min.Z - z_straight_top) < 0.05
    )
    assert len(host_edges) == 2, f"Expected 2 top Y-edges on host_cut, got {len(host_edges)}"
    host_cut = bd.fillet(host_edges, radius=1.00)

    # 2. Split USB-C (`rJ2`) open notch on West skirt (`Y = -86.6500 +- 9.00 mm`)
    split_cut = bd.Box(
        12.00,
        USBC_NOTCH_WIDTH,
        z_straight_top - z_bot,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((X_THUMB_OUTER, SPLIT_USBC_CY_R, z_bot)))
    split_edges = split_cut.edges().filter_by(
        lambda e: abs(e.bounding_box().size.X - 12.00) < 0.1
        and abs(e.bounding_box().min.Z - z_straight_top) < 0.05
    )
    assert len(split_edges) == 2, f"Expected 2 top X-edges on split_cut, got {len(split_edges)}"
    split_cut = bd.fillet(split_edges, radius=1.00)

    return [host_cut, split_cut]


def build_features_for_half(is_top_left: bool) -> tuple[list[bd.Solid], list[bd.Solid], list[bd.Solid]]:
    """
    Returns `(pre_cut_adds, cuts, post_cut_adds)` for one keyboard half:
      - `pre_cut_adds`: Thumb support apron (added BEFORE cutting relief slots)
      - `cuts`:         Pinky latch slot + Thumb latch slot + 2 Open USB-C U-notches
      - `post_cut_adds`: Pinky paddle latch arm + Thumb paddle latch arm (added AFTER cutting slots)
    """
    pinky_arm, pinky_cut = build_pinky_paddle_latch_right()
    thumb_apron, thumb_arm, thumb_cut = build_thumb_paddle_latch_right()
    usbc_cuts = build_usbc_open_notch_cutters_right()

    pre_adds = [thumb_apron]
    cuts = [pinky_cut, thumb_cut] + usbc_cuts
    post_adds = [pinky_arm, thumb_arm]

    if not is_top_left:
        return pre_adds, cuts, post_adds

    def invert_solid(s: bd.Solid) -> bd.Solid:
        mir = s.mirror(bd.Plane.YZ)
        loc = bd.Pos(DX_LEFT, DY_LEFT, H_SEP) * bd.Rot(180.0, 0.0, 0.0)
        return bd.Solid(mir.wrapped.Moved(loc.wrapped))

    return (
        [invert_solid(s) for s in pre_adds],
        [invert_solid(c) for c in cuts],
        [invert_solid(a) for a in post_adds],
    )


def build_trackball_keeper_halo() -> bd.Solid:
    """
    Annular non-contact Trackball Keeper Halo Ring at `(23.8125, -109.5375)`, `Z in [12.80, 15.10] mm`
    (ID D 15.60 mm, OD D 22.00 mm, thickness 2.30 mm) + rigid L-corner web bridges into the West & South
    frame walls (`X <= 8.5250`, `Y <= -125.1500`).
    """
    h = HALO_Z_MAX - HALO_Z_MIN
    with bd.BuildSketch(bd.Plane.XY.offset(HALO_Z_MIN)) as sk_halo:
        with bd.Locations([(TB_CX, TB_CY)]):
            bd.Circle(HALO_R_OUT)
        with bd.Locations([(0.5 * (6.00 + TB_CX), TB_CY)]):
            bd.Rectangle(TB_CX - 6.00, 11.00)
        with bd.Locations([(TB_CX, 0.5 * (-127.50 + TB_CY))]):
            bd.Rectangle(11.00, TB_CY - (-127.50))
        with bd.Locations([(0.5 * (6.00 + TB_CX), 0.5 * (-127.50 + TB_CY))]):
            bd.Rectangle(TB_CX - 6.00, TB_CY - (-127.50))
        with bd.Locations([(TB_CX, TB_CY)]):
            bd.Circle(HALO_R_IN, mode=bd.Mode.SUBTRACT)
    return bd.extrude(sk_halo.sketch, amount=h)


def build_carrying_frame_assembly_pose() -> bd.Solid:
    """
    Constructs the 1-piece PA12 `Carrying_Frame` in the packed assembly coordinate system
    (Right Case Rim at `Z = 0.00 mm`, Left Case Rim at `Z = +19.50 mm`).
    """
    pts_r_skirt_out = get_right_offset_pts(XY_FIT_GAP + SKIRT_WALL, r_convex=3.20, r_concave=1.50)
    pts_r_skirt_in = get_right_offset_pts(XY_FIT_GAP, r_convex=2.25, r_concave=1.75)
    pts_r_cav = get_right_offset_pts(-1.5000, r_convex=1.00, r_concave=1.00)

    pts_l_skirt_out = invert_pts_for_left_top(pts_r_skirt_out)
    pts_l_skirt_in = invert_pts_for_left_top(pts_r_skirt_in)
    pts_l_cav = invert_pts_for_left_top(pts_r_cav)

    sk_r_out = make_filleted_sketch(pts_r_skirt_out)
    sk_r_in = make_filleted_sketch(pts_r_skirt_in)
    sk_r_cav = make_filleted_sketch(pts_r_cav)

    sk_l_out = make_filleted_sketch(pts_l_skirt_out)
    sk_l_in = make_filleted_sketch(pts_l_skirt_in)
    sk_l_cav = make_filleted_sketch(pts_l_cav)

    z_bot_skirt = -SKIRT_DEPTH               # -2.40 mm
    z_bot_seat = Z_SEAT_GAP                  # +0.05 mm
    z_nw_roof_bot = MID_Z - SHIELD_THICK     # +7.75 mm
    z_mid = MID_Z                            # +9.75 mm
    z_top_seat = H_SEP - Z_SEAT_GAP          # +19.45 mm
    z_top_skirt = H_SEP + SKIRT_DEPTH        # +21.90 mm

    # 1. Bottom Half (Right `P_R` + NW L-cutout shield)
    bot_skirt = bd.extrude(sk_r_out, amount=z_bot_seat - z_bot_skirt).moved(
        bd.Location((0, 0, z_bot_skirt))
    ) - bd.extrude(sk_r_in, amount=z_bot_seat - z_bot_skirt + 0.20).moved(
        bd.Location((0, 0, z_bot_skirt - 0.10))
    )
    bot_spacer = bd.extrude(sk_r_out, amount=z_mid - z_bot_seat).moved(
        bd.Location((0, 0, z_bot_seat))
    ) - bd.extrude(sk_r_cav, amount=z_mid - z_bot_seat + 0.20).moved(
        bd.Location((0, 0, z_bot_seat - 0.10))
    )
    nw_shield = bd.extrude(sk_r_out - sk_l_cav, amount=SHIELD_THICK).moved(
        bd.Location((0, 0, z_nw_roof_bot))
    )

    # 2. Top Half (Transformed Left `P_L'` + SE L-cutout shield)
    top_skirt = bd.extrude(sk_l_out, amount=z_top_skirt - z_top_seat).moved(
        bd.Location((0, 0, z_top_seat))
    ) - bd.extrude(sk_l_in, amount=z_top_skirt - z_top_seat + 0.20).moved(
        bd.Location((0, 0, z_top_seat - 0.10))
    )
    top_spacer = bd.extrude(sk_l_out, amount=z_top_seat - z_mid).moved(
        bd.Location((0, 0, z_mid))
    ) - bd.extrude(sk_l_cav, amount=z_top_seat - z_mid + 0.20).moved(
        bd.Location((0, 0, z_mid - 0.10))
    )
    se_shield = bd.extrude(sk_l_out - sk_r_cav, amount=SHIELD_THICK).moved(
        bd.Location((0, 0, z_mid))
    )

    body = bot_skirt + bot_spacer + nw_shield + top_skirt + top_spacer + se_shield

    # 3. Integrate Trackball Keeper Halo Ring
    halo = build_trackball_keeper_halo()
    outer_clip = bd.extrude(sk_r_out, amount=30.0).moved(bd.Location((0, 0, 0.0)))
    body = body + (halo & outer_clip)

    # 4. Integrate Dual Paddle Latches (Thumb + Pinky) & 4 Open USB-C U-Notches
    pre_r, cuts_r, post_r = build_features_for_half(is_top_left=False)
    pre_l, cuts_l, post_l = build_features_for_half(is_top_left=True)

    for p in pre_r + pre_l:
        body = body + p
    for c in cuts_r + cuts_l:
        body = body - c
    for a in post_r + post_l:
        body = body + a

    solids = body.solids()
    assert len(solids) == 1, f"Expected single solid for Carrying_Frame, got {len(solids)}"
    frame_solid = solids[0]
    frame_solid.label = "Carrying_Frame"
    return frame_solid


def verify_jlc3dp_carrying_frame(print_solid: bd.Solid) -> None:
    """
    Full JLC3DP MJF/SLS PA12 preflight & `< 0.80 mm` thin-wall / micro-gap check on `carrying-frame`
    (with ZERO exemptions allowed!).
    """
    assert print_solid.is_valid and is_sound(print_solid), "[carrying-frame] Solid is not watertight/manifold!"
    assert len(print_solid.solids()) == 1 and print_solid.volume > 0, "[carrying-frame] Must be 1 positive-volume solid!"

    bb = print_solid.bounding_box()
    sx, sy, sz = bb.size.X, bb.size.Y, bb.size.Z
    assert abs(bb.min.Z - 0.0) < 1e-4, f"[carrying-frame] Print base min.Z={bb.min.Z:.5f} != 0.0000 mm!"
    assert 5.0 <= sx <= 380.0 and 5.0 <= sy <= 284.0 and 2.0 <= sz <= 380.0, (
        f"[carrying-frame] Bounding box {sx:.2f}x{sy:.2f}x{sz:.2f} mm outside JLC3DP limits!"
    )

    faces = print_solid.faces()
    min_concave_diam = float("inf")
    for f in faces:
        surf = BRepAdaptor_Surface(f.wrapped)
        if surf.GetType() == GeomAbs_Cylinder and f.wrapped.Orientation() == TopAbs_REVERSED:
            diam = round(2.0 * surf.Cylinder().Radius(), 4)
            if diam < min_concave_diam:
                min_concave_diam = diam
    assert min_concave_diam >= 1.50, (
        f"[carrying-frame] Concave hole/fillet diameter {min_concave_diam:.3f} mm < JLC3DP 1.50 mm limit!"
    )

    bbs = [f.bounding_box() for f in faces]
    violations = []
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
                    violations.append((d, (mx, my, mz), i, j))

    print(
        f"[carrying-frame] JLC3DP preflight & <0.80mm check: "
        f"bbox={sx:.2f}x{sy:.2f}x{sz:.2f}mm, volume={print_solid.volume / 1000.0:.2f}cm^3, "
        f"min_concave_diam={min_concave_diam:.2f}mm (>=1.50mm), "
        f"{len(violations)} <0.80mm violations (0 exclusions)"
    )
    if violations:
        for d, (mx, my, mz), i, j in violations[:15]:
            print(f"  VIOLATION: d={d:.4f} mm at ({mx:.2f}, {my:.2f}, {mz:.2f}) [F{i}-F{j}]")
    assert len(violations) == 0, f"[carrying-frame] Found {len(violations)} <0.80mm wall/gap violations!"


def build_rubber_feet_in_case_pose(is_right: bool) -> list[bd.Solid]:
    """
    Builds 5 realistic D 8.0 x 2.0 mm cylindrical rubber feet stuck flat onto the outer tilted
    bottom plane of `right.step` (`is_right=True`) or `left.step` (`is_right=False`), inset >= 6.5 mm
    inside the 5 outer corners of the case bottom.
    """
    sgn = 1.0 if is_right else -1.0
    foot_xy_abs = [
        (14.50, -38.50),    # NW thumb-north corner
        (128.00, -38.50),   # NE pinky-north corner
        (128.00, -92.50),   # SE pinky-south corner
        (91.00, -119.00),   # Thumb-east south corner
        (14.50, -119.00),   # SW thumb-south corner
    ]
    p_thumb = (sgn * X_THUMB_OUTER, -80.0, Z_THUMB_BOTTOM)
    p_pinky = (sgn * X_PINKY_OUTER, -80.0, Z_PINKY_BOTTOM)
    dx = p_pinky[0] - p_thumb[0]
    dz = p_pinky[2] - p_thumb[2]
    norm_out = (dz, 0.0, -dx) if is_right else (-dz, 0.0, dx)

    feet = []
    side_tag = "Right" if is_right else "Left"
    for idx, (ax, fy) in enumerate(foot_xy_abs):
        fx = sgn * ax
        fz = z_case_bottom_right(ax)
        n_len = math.hypot(norm_out[0], norm_out[2])
        ux, uz = norm_out[0] / n_len, norm_out[2] / n_len
        foot_plane = bd.Plane(origin=(fx + 0.01 * ux, fy, fz + 0.01 * uz), z_dir=(ux, 0.0, uz))
        cyl = bd.extrude(foot_plane * bd.Circle(RUBBER_FOOT_RADIUS), amount=RUBBER_FOOT_HEIGHT - 0.01).solids()[0]
        cyl.label = f"{side_tag}_Rubber_Foot_{idx + 1}"
        feet.append(cyl)
    return feet


def build_cio_magnetic_tips_in_case_pose(is_right: bool) -> list[bd.Solid]:
    """
    Builds realistic `CIO-SLMG-T-C` magnetic USB-C adapter tips (`12.40 x 7.00 mm` stadium head,
    protruding `3.80 mm` outside the case outer wall + recessed neck toward the USB-C port) for both
    Host USB-C (`J1`/`rJ1`) and Split USB-C (`J2`/`rJ2`), with a 0.05 mm air gap to the unmodified case
    and metal USB-C receptacle so B-rep overlap_volume == 0.00000000 mm^3.
    """
    sgn = 1.0 if is_right else -1.0
    side_tag = "Right" if is_right else "Left"

    # 1. Host USB-C (`rJ1` / `J1`) on North wall (`Y_NORTH_OUTER = -30.8375`, protruding in `+Y`)
    host_cx = sgn * HOST_USBC_CX_R
    p_host = bd.Plane(origin=(host_cx, Y_NORTH_OUTER + 0.05, USBC_CENTER_Z_R), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
    host_head = bd.extrude(
        p_host * bd.RectangleRounded(CIO_TIP_WIDTH, CIO_TIP_HEIGHT, 3.20),
        amount=CIO_TIP_PROTRUSION,
    ).solids()[0]
    p_host_neck = bd.Plane(origin=(host_cx, Y_NORTH_OUTER - 1.15, USBC_CENTER_Z_R), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
    host_neck = bd.extrude(
        p_host_neck * bd.RectangleRounded(8.40, 2.60, 1.10),
        amount=1.25,
    ).solids()[0]
    host_tip = (host_head + host_neck).solids()[0]
    host_tip.label = f"{side_tag}_Host_USBC_CIO_Tip"

    # 2. Split USB-C (`rJ2` / `J2`) on Thumb wall (`|X| = 7.0250`, protruding outward in `-X` for Right / `+X` for Left)
    split_x_wall = sgn * X_THUMB_OUTER
    out_x = -1.0 if is_right else 1.0
    p_split = bd.Plane(
        origin=(split_x_wall + 0.05 * out_x, SPLIT_USBC_CY_R, USBC_CENTER_Z_R),
        x_dir=(0, 1, 0),
        z_dir=(out_x, 0, 0),
    )
    split_head = bd.extrude(
        p_split * bd.RectangleRounded(CIO_TIP_WIDTH, CIO_TIP_HEIGHT, 3.20),
        amount=CIO_TIP_PROTRUSION,
    ).solids()[0]
    p_split_neck = bd.Plane(
        origin=(split_x_wall - 1.15 * out_x, SPLIT_USBC_CY_R, USBC_CENTER_Z_R),
        x_dir=(0, 1, 0),
        z_dir=(out_x, 0, 0),
    )
    split_neck = bd.extrude(
        p_split_neck * bd.RectangleRounded(8.40, 2.60, 1.10),
        amount=1.25,
    ).solids()[0]
    split_tip = (split_head + split_neck).solids()[0]
    split_tip.label = f"{side_tag}_Split_USBC_CIO_Tip"

    return [host_tip, split_tip]


def _aabb_intersects(b1, b2, tol: float = 1e-4) -> bool:
    return not (
        b1.max.X < b2.min.X - tol
        or b2.max.X < b1.min.X - tol
        or b1.max.Y < b2.min.Y - tol
        or b2.max.Y < b1.min.Y - tol
        or b1.max.Z < b2.min.Z - tol
        or b2.max.Z < b1.min.Z - tol
    )


def _aabb_min_dist(b1, b2) -> float:
    dx = max(0.0, b1.min.X - b2.max.X, b2.min.X - b1.max.X)
    dy = max(0.0, b1.min.Y - b2.max.Y, b2.min.Y - b1.max.Y)
    dz = max(0.0, b1.min.Z - b2.max.Z, b2.min.Z - b1.max.Z)
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def min_surface_clearance(solids_list: list[bd.Solid], target_solid: bd.Solid) -> float:
    target_faces = [(f.wrapped, f.bounding_box()) for f in target_solid.faces()]
    best = float("inf")
    builder = BRep_Builder()
    for s in solids_list:
        sb = s.bounding_box()
        if _aabb_min_dist(sb, target_solid.bounding_box()) >= best:
            continue
        cand_tfaces = [fw for fw, fb in target_faces if _aabb_min_dist(sb, fb) < best]
        if not cand_tfaces:
            continue
        cmp_s = TopoDS_Compound()
        builder.MakeCompound(cmp_s)
        for sf in s.faces():
            builder.Add(cmp_s, sf.wrapped)
        cmp_t = TopoDS_Compound()
        builder.MakeCompound(cmp_t)
        for tfw in cand_tfaces:
            builder.Add(cmp_t, tfw)
        dss = BRepExtrema_DistShapeShape(cmp_s, cmp_t)
        if dss.IsDone() and dss.NbSolution() > 0:
            d = dss.Value()
            if d < best:
                best = d
    return best


def verify_carrying_assembly(
    frame_asm: bd.Solid,
    right_solids: list[bd.Solid],
    left_packed_solids: list[bd.Solid],
    right_feet: list[bd.Solid],
    left_packed_feet: list[bd.Solid],
    right_cio_tips: list[bd.Solid],
    left_packed_cio_tips: list[bd.Solid],
) -> None:
    """
    Verifies:
      1. Zero B-rep overlap (`overlap_volume == 0.00000000 mm^3`) across `Carrying_Frame`, all 674 solids
         of Left & Right full assemblies, all 10 rubber feet, and all 4 `CIO-SLMG-T-C` magnetic USB-C tips.
      2. Unobstructed straight-in vertical entry/exit path for all 4 `CIO-SLMG-T-C` tips (`0.00000000 mm^3`
         overlap with `Carrying_Frame` along the entire straight-in insertion travel).
      3. Minimum surface clearances (Ball keeper gap, Inertia wheel, Keycaps, CIO USB-C tips, Rubber feet).
      4. Positive 6-DOF mechanical lock (`+-X, +-Y, +-Z`) of Right case, Left case, and 25mm Trackball.
    """
    frame_bb = frame_asm.bounding_box()
    r_extra = right_feet + right_cio_tips
    l_extra = left_packed_feet + left_packed_cio_tips
    all_kb_and_acc = right_solids + left_packed_solids + r_extra + l_extra

    # 1. Frame vs every solid
    max_ov_frame = 0.0
    worst_label = ""
    for idx, s in enumerate(all_kb_and_acc):
        sb = s.bounding_box()
        if _aabb_intersects(frame_bb, sb):
            ov = overlap_volume(frame_asm, s)
            if ov > max_ov_frame:
                max_ov_frame = ov
                worst_label = f"{getattr(s, 'label', '') or idx} bbox={sb}"

    # 2. CIO tips vs own keyboard solids & Right group vs Left group
    max_ov_cio_self = 0.0
    for tip_list, kb_list in ((right_cio_tips, right_solids), (left_packed_cio_tips, left_packed_solids)):
        for tip in tip_list:
            tb = tip.bounding_box()
            for ks in kb_list:
                if _aabb_intersects(tb, ks.bounding_box()):
                    ov = overlap_volume(tip, ks)
                    if ov > max_ov_cio_self:
                        max_ov_cio_self = ov

    r_group = [(s, s.bounding_box()) for s in (right_solids + r_extra)]
    l_group = [(s, s.bounding_box()) for s in (left_packed_solids + l_extra)]
    max_ov_rl = 0.0
    for sr, br in r_group:
        for sl, bl in l_group:
            if _aabb_intersects(br, bl):
                ov = overlap_volume(sr, sl)
                if ov > max_ov_rl:
                    max_ov_rl = ov

    print(
        f"[carrying-assembly] Overlap check ({len(all_kb_and_acc)} solids + frame): "
        f"Frame_vs_All={max_ov_frame:.8f} mm^3, CIO_vs_KB={max_ov_cio_self:.8f} mm^3, "
        f"Right_vs_Left={max_ov_rl:.8f} mm^3"
    )
    assert max_ov_frame == 0.0, f"B-rep interference with Carrying_Frame: {max_ov_frame:.8f} mm^3 at {worst_label}!"
    assert max_ov_cio_self == 0.0, f"B-rep interference between CIO tips & KB: {max_ov_cio_self:.8f} mm^3!"
    assert max_ov_rl == 0.0, f"B-rep interference between Right & Left halves: {max_ov_rl:.8f} mm^3!"

    # 3. Straight-in vertical entry/exit path check for all 4 plugged-in `CIO-SLMG-T-C` tips
    for dz in (-1.5, -4.0, -10.0, -20.0):
        for r_tip in right_cio_tips:
            moved_tip = bd.Solid(r_tip.wrapped.Moved(bd.Location((0.0, 0.0, dz)).wrapped))
            if _aabb_intersects(frame_bb, moved_tip.bounding_box()):
                assert overlap_volume(frame_asm, moved_tip) == 0.0, (
                    f"Right CIO tip {r_tip.label} collides with Carrying_Frame at dz={dz} mm during straight push-in!"
                )
    for dz in (1.5, 4.0, 10.0, 20.0):
        for l_tip in left_packed_cio_tips:
            moved_tip = bd.Solid(l_tip.wrapped.Moved(bd.Location((0.0, 0.0, dz)).wrapped))
            if _aabb_intersects(frame_bb, moved_tip.bounding_box()):
                assert overlap_volume(frame_asm, moved_tip) == 0.0, (
                    f"Left CIO tip {l_tip.label} collides with Carrying_Frame at dz=+{dz} mm during straight push-in!"
                )

    # Identify semantic solids from geometry in assembly coordinates
    right_case = max(right_solids, key=lambda s: s.volume)
    left_case_packed = max(left_packed_solids, key=lambda s: s.volume)
    ball_candidates = [
        s
        for s in right_solids
        if abs(s.bounding_box().size.X - 25.0) < 0.2 and abs(s.bounding_box().max.Z - 14.80) < 0.2
    ]
    assert len(ball_candidates) == 1, f"Expected 1 Trackball_25mm solid, got {len(ball_candidates)}"
    ball_solid = ball_candidates[0]

    wheel_candidates = [
        s for s in right_solids if 3.90 < s.bounding_box().max.Z < 4.30 and s.bounding_box().size.Y > 21.5
    ]
    assert len(wheel_candidates) == 1, f"Expected 1 Steel_Flywheel solid, got {len(wheel_candidates)}"
    wheel_solid = wheel_candidates[0]

    right_keycaps = [
        s for s in right_solids if abs(s.bounding_box().max.Z - 3.60) < 0.15 and 17.5 < s.bounding_box().size.X < 18.5
    ]
    left_keycaps_packed = [
        s
        for s in left_packed_solids
        if abs(s.bounding_box().min.Z - (H_SEP - 3.60)) < 0.15 and 17.5 < s.bounding_box().size.X < 18.5
    ]
    assert len(right_keycaps) == 19 and len(left_keycaps_packed) == 21, (
        f"Expected 19 Right + 21 Left keycaps, got R={len(right_keycaps)}, L={len(left_keycaps_packed)}"
    )

    all_cio_tips = right_cio_tips + left_packed_cio_tips
    clr_ball = min_surface_clearance([ball_solid], frame_asm)
    clr_wheel = min_surface_clearance([wheel_solid], frame_asm)
    clr_keycaps = min_surface_clearance(right_keycaps + left_keycaps_packed, frame_asm)
    clr_cio_tips = min_surface_clearance(all_cio_tips, frame_asm)
    clr_feet = min_surface_clearance(right_feet + left_packed_feet, frame_asm)
    clr_ball_to_left_cap = min_surface_clearance(left_keycaps_packed, ball_solid)

    print(
        f"[carrying-assembly] Minimum surface clearances:\n"
        f"  - Frame vs 25mm Trackball (Keeper Halo): {clr_ball:.3f} mm (target 0.50..0.70 mm)\n"
        f"  - 25mm Trackball vs Left Keycap (SW18):  {clr_ball_to_left_cap:.3f} mm (>= 1.00 mm)\n"
        f"  - Frame vs Inertia Wheel:                {clr_wheel:.3f} mm (>= 1.50 mm)\n"
        f"  - Frame vs All 40 Keycaps:               {clr_keycaps:.3f} mm (>= 0.75 mm)\n"
        f"  - Frame vs All 4 CIO-SLMG-T-C Tips:      {clr_cio_tips:.3f} mm (>= 1.50 mm, 100% open)\n"
        f"  - Frame vs All 10 Rubber Feet:           {clr_feet:.3f} mm (>= 2.00 mm)"
    )
    assert 0.50 <= clr_ball <= 0.70, f"Trackball keeper clearance {clr_ball:.3f} mm outside [0.50, 0.70] mm!"
    assert clr_ball_to_left_cap >= 1.00, f"Ball-to-Left-keycap gap {clr_ball_to_left_cap:.3f} mm < 1.00 mm!"
    assert clr_wheel >= 1.50, f"Inertia wheel clearance {clr_wheel:.3f} mm < 1.50 mm!"
    assert clr_keycaps >= 0.75, f"Keycap clearance {clr_keycaps:.3f} mm < 0.75 mm!"
    assert clr_cio_tips >= 1.50, f"CIO-SLMG-T-C tip clearance {clr_cio_tips:.3f} mm < 1.50 mm!"
    assert clr_feet >= 2.00, f"Rubber feet clearance {clr_feet:.3f} mm < 2.00 mm!"

    # 4. 6-DOF positive mechanical lock check (`+-X, +-Y, +-Z` <= 0.65 mm displacement causes solid interference)
    test_dirs = [
        ("+X", (0.65, 0.0, 0.0)),
        ("-X", (-0.65, 0.0, 0.0)),
        ("+Y", (0.0, 0.65, 0.0)),
        ("-Y", (0.0, -0.65, 0.0)),
        ("+Z", (0.0, 0.0, 0.65)),
        ("-Z", (0.0, 0.0, -0.65)),
    ]
    for name, target_case in (("Right_Case", right_case), ("Left_Case_Packed", left_case_packed)):
        for d_tag, vec in test_dirs:
            shifted = bd.Solid(target_case.wrapped.Moved(bd.Location(vec).wrapped))
            ov_lock = overlap_volume(frame_asm, shifted)
            assert ov_lock > 0.05, (
                f"[6-DOF FAIL] {name} is NOT positively locked in {d_tag} (overlap={ov_lock:.5f} mm^3 at 0.65 mm)!"
            )

    # Trackball shock-retention check: lifting ball by +1.00 mm (well below +3.10 mm cup escape) hits Halo Ring!
    ball_lifted = bd.Solid(ball_solid.wrapped.Moved(bd.Location((0.0, 0.0, 1.00)).wrapped))
    ov_ball_stop = overlap_volume(frame_asm, ball_lifted)
    assert ov_ball_stop > 0.50, f"[6-DOF FAIL] Trackball Halo Ring failed to stop +1.00 mm ball lift ({ov_ball_stop:.4f})!"
    print("[carrying-assembly] 6-DOF mechanical lock, straight-in CIO tip entry & shock-retention checks: ALL PASS!")


def main() -> None:
    print("=== Building curcur40 Dual-Latch Open-USB PA12 Carrying Frame & Full Packed Assembly ===")
    CASES_DIR.mkdir(parents=True, exist_ok=True)
    ASSEMBLIES_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Build 1-piece PA12 Carrying Frame in assembly pose & transform to brick-horizontal Z = 0.0000 mm print pose
    frame_asm = build_carrying_frame_assembly_pose()
    frame_desk_raw = transform_packed_to_desk(frame_asm)
    bb_raw = frame_desk_raw.bounding_box()
    frame_print = frame_desk_raw.moved(bd.Location((0.0, 0.0, -bb_raw.min.Z)))
    frame_print.label = "curcur40_carrying_frame"

    # 2. Run JLC3DP preflight & `< 0.80 mm` zero-violation check on `frame_print`
    verify_jlc3dp_carrying_frame(frame_print)

    frame_step_path = CASES_DIR / "carrying-frame.step"
    frame_stl_path = CASES_DIR / "carrying-frame.stl"
    bd.export_step(frame_print, str(frame_step_path))
    bd.export_stl(frame_print, str(frame_stl_path))
    print(f"Exported {frame_step_path.name} & {frame_stl_path.name}")

    # 3. Load synchronized 674-solid `assembly-full.step` (rebuilding if missing)
    full_asm_path = ASSEMBLIES_DIR / "assembly-full.step"
    if not full_asm_path.exists():
        import generate_full_assembly
        generate_full_assembly.main()

    print(f"Loading synchronized full keyboard solids from {full_asm_path.name}...")
    full_imported = bd.import_step(str(full_asm_path))
    all_solids = full_imported.solids()
    right_solids = [s for s in all_solids if s.bounding_box().center().X > 0.0]
    left_orig_solids = [s for s in all_solids if s.bounding_box().center().X < 0.0]
    assert len(right_solids) > 300 and len(left_orig_solids) > 300, (
        f"Unexpected solid split from assembly-full.step: R={len(right_solids)}, L={len(left_orig_solids)}"
    )

    left_packed_solids = [transform_left_to_packed(s) for s in left_orig_solids]
    right_feet = build_rubber_feet_in_case_pose(is_right=True)
    left_packed_feet = [transform_left_to_packed(f) for f in build_rubber_feet_in_case_pose(is_right=False)]
    right_cio_tips = build_cio_magnetic_tips_in_case_pose(is_right=True)
    left_packed_cio_tips = [transform_left_to_packed(t) for t in build_cio_magnetic_tips_in_case_pose(is_right=False)]

    # 4. Run full 688-solid B-rep interference, straight-in CIO path, clearance & 6-DOF retention checks
    verify_carrying_assembly(
        frame_asm,
        right_solids,
        left_packed_solids,
        right_feet,
        left_packed_feet,
        right_cio_tips,
        left_packed_cio_tips,
    )

    # 5. Export desk-level parallel brick verification assembly (`carrying-assembly.step`)
    right_grp = bd.Compound(children=right_solids + right_feet + right_cio_tips)
    right_grp.label = "Right_Keyboard_With_Feet_And_CIO_Tips"
    left_grp = bd.Compound(children=left_packed_solids + left_packed_feet + left_packed_cio_tips)
    left_grp.label = "Left_Keyboard_Packed_With_Feet_And_CIO_Tips"

    packed_desk = transform_packed_to_desk(
        bd.Compound(children=[frame_asm, right_grp, left_grp])
    )
    packed_desk.label = "curcur40_carrying_assembly"
    bb_desk = packed_desk.bounding_box()
    print(
        f"Packed Brick Envelope (including D8x2mm rubber feet & 4 CIO-SLMG-T-C magnetic tips): "
        f"{bb_desk.size.X:.2f} x {bb_desk.size.Y:.2f} x {bb_desk.size.Z:.2f} mm "
        f"(Z = [{bb_desk.min.Z:.4f}, {bb_desk.max.Z:.4f}] mm)"
    )
    assert abs(bb_desk.min.Z - 0.0) < 0.05, f"Expected desk-level Z_min ~ 0.00 mm, got {bb_desk.min.Z:.4f} mm!"

    carrying_asm_path = ASSEMBLIES_DIR / "carrying-assembly.step"
    bd.export_step(packed_desk, str(carrying_asm_path))
    print(f"Exported {carrying_asm_path.name} successfully!")


if __name__ == "__main__":
    main()
