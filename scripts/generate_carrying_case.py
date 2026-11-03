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
- Internal Non-Contact Protection & 100% Cavity Enclosure:
    - Rim-to-rim perimeter seating ledges (Z = +0.05 mm & +19.45 mm) carry all loads through the PA12 case rims
    - Annular Trackball Keeper Halo Ring (Ø 15.60 mm ID / Ø 22.00 mm OD, Z = +12.80..+15.10 mm) holds a 0.58 mm
      non-contact gap over the 25mm ball at rest and limits shock lift to <= 0.73 mm (preventing claw pop-out
      and keeping >= 0.37 mm clearance to opposite Left `SW18` keycap even at hard stop)
    - Point-symmetric NW & SE L-cutout protective corner shields (2.00 mm thick) seal all 40 keys & inertia wheel
- One-Touch 1-Second Snap Retention & 4-Port USB-C Dust Shields (Zero Rubber-Foot Interference):
    - Thumb Split USB-C solid Toe-Lug + Dust Shield (0.90 mm catch under 1.50 mm PA12 wall bridge, >= 0.35 mm
      clear of recessed metal `TYPE-C-31-M-13C` shell)
    - North/South Host USB-C exterior flush dust-shield tabs (zero inward hook for bind-free swing-in/out)
    - Pinky 22.00 mm wide PA12 cantilever spring paddle latches (2.00 mm beam, 2.00 mm relief slots with Ø 2.00 mm
      filleted roots, 1.00 mm catch overlap under the 10.00 mm pinky wall + ergonomic thumb-release paddle)
- Automated Preflight & Full-Assembly Verification:
    - JLC3DP MJF/SLS PA12 rules: single watertight manifold solid, Z = 0.0000 mm base, concave bore >= Ø 1.50 mm,
      and ZERO `< 0.80 mm` thin-wall/micro-gap face pairs (0 exclusions)
    - Zero B-rep overlap (`0.00000000 mm^3`) across all 674 KiCad-synchronized keyboard solids + 10 rubber feet
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
THETA_TENT_RAD = math.atan2(Z_PINKY_BOTTOM - Z_THUMB_BOTTOM, X_PINKY_OUTER - X_THUMB_OUTER)
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
SKIRT_DEPTH = 2.4000      # Skirt overlap onto case walls (stops at Z = -2.40 mm, clear of -2.75 mm USB-C ports)
SHIELD_THICK = 2.0000     # 2.00 mm protective corner shields over NW & SE L-cutouts

# Trackball coordinates & Keeper Halo Ring parameters
TB_CX = 23.8125
TB_CY = -109.5375
BALL_CZ = 2.3000
BALL_RADIUS = 12.5000
HALO_R_IN = 7.8000        # Ø 15.60 mm inner bore
HALO_R_OUT = 11.0000      # Ø 22.00 mm outer ring
HALO_Z_MIN = 12.8000      # 0.58 mm radial rest gap to Ø 25.00 mm ball
HALO_Z_MAX = 15.1000      # 2.30 mm thick ring, 0.80 mm clear below Left keycaps (+15.90 mm)

# Rubber foot specification (`docs/buildguide_jp.md`: Ø 6-8 mm, thickness 1.5-2.0 mm)
RUBBER_FOOT_RADIUS = 4.0000   # Ø 8.00 mm
RUBBER_FOOT_HEIGHT = 2.0000   # 2.00 mm height


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


def get_right_Offset_pts(outward_offset: float, r_convex: float, r_concave: float) -> list[tuple[float, float, float]]:
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
        (X_STEP_R + d, Y_SOUTH_OUTER - d, r_convex),
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
    so the bottom rubber feet rest flat on `Z = 0.0000 mm` (and bare Right bottom sits at `Z = +2.0000 mm`).
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
    Builds the Right-keyboard (East `X = 135.8580 mm`, `Y in [-76.50, -54.50]`) PA12 cantilever
    spring paddle latch solid AND the relief-slot cutter that isolates the spring beam from the skirt/ledge.
    Every face segment is >= 0.85 mm wide and slot root fillets are Ø 2.00 mm (zero `< 0.80 mm` pairs).
    """
    y_center = -72.0000
    latch_w = 22.0000
    slot_w = 2.0000
    total_cut_w = latch_w + 2.0 * slot_w  # 26.00 mm: Y in [-85.00, -59.00] (clears Halo Bridge by 5.55 mm!)
    z_root = 5.0000                       # Straight slot up to +5.00 mm + R=1.00 mm top round -> +6.00 mm

    # 1. Cutter that clears the skirt & inner ledge across Y in [-85.00, -59.00] below Z = +6.00 mm,
    #    with R = 1.00 mm (Ø 2.00 mm >= Ø 1.50 mm) rounded slot tops:
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
    assert len(top_slot_edges) == 2, f"Expected 2 top X-edges on latch cutter, got {len(top_slot_edges)}"
    cut_box = bd.fillet(top_slot_edges, radius=1.00)

    # 2. Cantilever spring beam + bottom catch hook + ergonomic thumb-release paddle in XZ plane:
    #    `x_in` and `x_out` align 100.000% flush with `sk_r_in` (136.1080) and `sk_r_out` (138.1080)
    #    so zero micro-steps occur at the beam root!
    x_in = X_PINKY_OUTER + XY_FIT_GAP             # 136.1080 mm (flush with skirt inner wall)
    x_out = x_in + SKIRT_WALL                     # 138.1080 mm (flush with skirt outer wall, 2.00 mm beam)
    x_hook = X_PINKY_OUTER - 1.0000               # 134.8580 mm (1.00 mm inward catch overlap under 1.50 mm wall)
    x_ramp_bot = 135.9580                         # Entry cam ramp outer bottom (> 135.8580 so case corner self-cams!)
    x_paddle = 139.9080                           # +1.80 mm ergonomic finger release tab

    xz_pts = [
        (x_in, 6.2000),         # Blends 0.20 mm above slot root into solid 3.75 mm frame wall
        (x_out, 6.2000),
        (x_out, -7.6000),
        (x_paddle, -9.0000),    # 2.28 mm ergonomic upper bevel
        (x_paddle, -10.6000),   # 1.60 mm vertical paddle tip face
        (x_out, -10.6000),      # 1.80 mm horizontal thumb-grip ledge for effortless 1-finger release
        (x_out, -11.6800),      # 1.08 mm lower outer face (stays clear above 2.00 mm rubber-foot desk plane!)
        (x_ramp_bot, -11.6800), # 2.15 mm flat horizontal base (serves as Z=0 print bed face!)
        (x_hook, -11.2800),     # 1.17 mm angled entry cam ramp
        (x_hook, -10.4300),     # 0.85 mm vertical inner hook nose (> 0.80 mm!)
        (x_in, -10.4300),       # 1.25 mm horizontal catch shelf (0.30 mm clear below angled case bottom)
    ]
    with bd.BuildSketch(bd.Plane.XZ) as sk_arm_sym:
        bd.Polygon(xz_pts, align=None)
    arm_solid = bd.extrude(sk_arm_sym.sketch, amount=latch_w, both=False)
    arm_bb = arm_solid.bounding_box()
    arm_solid = arm_solid.moved(bd.Location((0.0, y_center - arm_bb.center().Y, 0.0)))

    return arm_solid, cut_box


def build_Retention_features_for_half(is_top_left: bool) -> tuple[list[bd.Solid], list[bd.Solid]]:
    """
    Returns `(add_solids, cut_solids)` for one keyboard half:
      - `is_top_left = False`: Bottom Right keyboard (`Z <= 0`)
      - `is_top_left = True`:  Top Left keyboard via exact point-inversion `(DX_LEFT - X, DY_LEFT - Y, H_SEP - Z)`
    Features:
      1. Split USB-C solid Toe-Lug + Dust Shield (`X = 4.775..7.925, Y = -90.65..-82.65, Z = -8.35..-3.05`)
         Plus bridges extending the outer skirt smoothly down around the lug (`Y in [-92.90, -80.40]`).
      2. Host USB-C exterior flush Dust Shield (`X = 19.575..33.575, Y = -30.5875..-28.5875, Z = -9.20..+0.50`).
      3. Pinky One-Touch Cantilever Paddle Latch + Relief Slot Cutter.
    """
    # 1. Split USB-C Dust Shield + Inward Toe-Lug (5.30 mm tall block, >= 0.355 mm clear of metal USB-C shell!)
    with bd.BuildSketch(bd.Plane.YZ.offset(4.7750)) as sk_split_shield:
        with bd.Locations([(-86.6500, -4.1750)]):
            bd.RectangleRounded(12.80, 8.35, 1.50)  # Y in [-93.05, -80.25], Z in [-8.35, 0.00]
    split_shield = bd.extrude(sk_split_shield.sketch, amount=SKIRT_WALL)  # X in [4.7750, 6.7750]

    with bd.BuildSketch(bd.Plane.YZ.offset(6.5000)) as sk_toe_lug:
        with bd.Locations([(-86.6500, -5.7000)]):
            bd.RectangleRounded(8.00, 5.30, 1.20)   # Y in [-90.65, -82.65], Z in [-8.35, -3.05]
    toe_lug = bd.extrude(sk_toe_lug.sketch, amount=1.4250)  # X up to 7.9250 mm (0.90 mm catch under PA12 bridge)

    # 2. Host USB-C Exterior Flush Dust Shield (North wall, zero inward hook so swing-in never binds)
    host_shield = bd.Box(
        14.40,
        SKIRT_WALL,
        9.40,
        align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((26.5750, Y_NORTH_OUTER + XY_FIT_GAP, -9.2000)))
    host_edges = host_shield.edges().filter_by(
        lambda e: abs(e.bounding_box().size.Y - SKIRT_WALL) < 0.1
        and e.bounding_box().max.Z < -8.00
    )
    if len(host_edges) == 2:
        host_shield = bd.fillet(host_edges, radius=1.50)

    # 3. Pinky Cantilever Paddle Latch
    latch_arm, latch_cutter = build_pinky_paddle_latch_right()

    adds = [split_shield, toe_lug, host_shield, latch_arm]
    cuts = [latch_cutter]

    if not is_top_left:
        return adds, cuts

    # Exact point-inversion `(X, Y, Z) -> (DX_LEFT - X, DY_LEFT - Y, H_SEP - Z)` via Rot_X(180) * Mirror_YZ
    # Wait: since Right's retention features are extruded prisms, we can mirror across X = MID_X and rotate 180 about X!
    def invert_solid(s: bd.Solid) -> bd.Solid:
        mir = s.mirror(bd.Plane.YZ)
        loc = bd.Pos(DX_LEFT, DY_LEFT, H_SEP) * bd.Rot(180.0, 0.0, 0.0)
        return bd.Solid(mir.wrapped.Moved(loc.wrapped))

    return [invert_solid(s) for s in adds], [invert_solid(c) for c in cuts]


def build_trackball_keeper_halo() -> bd.Solid:
    """
    Annular non-contact Trackball Keeper Halo Ring at `(23.8125, -109.5375)`, `Z in [12.80, 15.10] mm`
    (ID Ø 15.60 mm, OD Ø 22.00 mm, thickness 2.30 mm) + rigid L-corner web bridges into the West & South
    frame walls (`X <= 8.5250`, `Y <= -125.1500`).
    """
    h = HALO_Z_MAX - HALO_Z_MIN
    with bd.BuildSketch(bd.Plane.XY.offset(HALO_Z_MIN)) as sk_halo:
        with bd.Locations([(TB_CX, TB_CY)]):
            bd.Circle(HALO_R_OUT)
        # West bridge into West frame wall (`X in [6.00, TB_CX]`, width 11.0 mm)
        with bd.Locations([(0.5 * (6.00 + TB_CX), TB_CY)]):
            bd.Rectangle(TB_CX - 6.00, 11.00)
        # South bridge into South frame wall (`Y in [-127.50, TB_CY]`, width 11.0 mm)
        with bd.Locations([(TB_CX, 0.5 * (-127.50 + TB_CY))]):
            bd.Rectangle(11.00, TB_CY - (-127.50))
        # SW corner fill eliminating any narrow pocket between the two bridges and SW inner wall
        with bd.Locations([(0.5 * (6.00 + TB_CX), 0.5 * (-127.50 + TB_CY))]):
            bd.Rectangle(TB_CX - 6.00, TB_CY - (-127.50))
        # Subtract Ø 15.60 mm central bore
        with bd.Locations([(TB_CX, TB_CY)]):
            bd.Circle(HALO_R_IN, mode=bd.Mode.SUBTRACT)
    return bd.extrude(sk_halo.sketch, amount=h)


def build_carrying_frame_assembly_pose() -> bd.Solid:
    """
    Constructs the 1-piece PA12 `Carrying_Frame` in the packed assembly coordinate system
    (Right Case Rim at `Z = 0.00 mm`, Left Case Rim at `Z = +19.50 mm`).
    """
    # Polygons for Bottom Half (Right `P_R`)
    pts_r_skirt_out = get_right_Offset_pts(XY_FIT_GAP + SKIRT_WALL, r_convex=3.20, r_concave=1.50)
    pts_r_skirt_in = get_right_Offset_pts(XY_FIT_GAP, r_convex=2.25, r_concave=1.75)
    pts_r_cav = get_right_Offset_pts(-1.5000, r_convex=1.00, r_concave=1.00)

    # Polygons for Top Half (Transformed Left `P_L'`)
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
    z_se_floor_top = MID_Z + SHIELD_THICK    # +11.75 mm
    z_top_seat = H_SEP - Z_SEAT_GAP          # +19.45 mm
    z_top_skirt = H_SEP + SKIRT_DEPTH        # +21.90 mm

    # 1. Bottom Half:
    #    - Outer skirt ring (`Z = -2.40 .. +0.05`)
    bot_skirt = bd.extrude(sk_r_out, amount=z_bot_seat - z_bot_skirt).moved(
        bd.Location((0, 0, z_bot_skirt))
    ) - bd.extrude(sk_r_in, amount=z_bot_seat - z_bot_skirt + 0.20).moved(
        bd.Location((0, 0, z_bot_skirt - 0.10))
    )
    #    - Main spacer wall (`Z = +0.05 .. +9.75` across full `P_R`, + up to `+11.75` along SE step to fuse with SE floor)
    bot_spacer = bd.extrude(sk_r_out, amount=z_mid - z_bot_seat).moved(
        bd.Location((0, 0, z_bot_seat))
    ) - bd.extrude(sk_r_cav, amount=z_mid - z_bot_seat + 0.20).moved(
        bd.Location((0, 0, z_bot_seat - 0.10))
    )
    #    - NW L-cutout protective roof slab (`Z = +7.75 .. +9.75`): `sk_r_out - sk_l_cav`!
    #      Look how clean `sk_r_out - sk_l_cav` is: it fills ONLY the NW L-cutout outside `Left`'s cavity,
    #      fusing 100% flush with `Left`'s step wall (`sk_l_out - sk_l_cav`)!
    nw_shield_2d = sk_r_out - sk_l_cav
    nw_shield = bd.extrude(nw_shield_2d, amount=SHIELD_THICK).moved(
        bd.Location((0, 0, z_nw_roof_bot))
    )

    # 2. Top Half (exact point-symmetric twin!):
    #    - Outer skirt ring (`Z = +19.45 .. +21.90`)
    top_skirt = bd.extrude(sk_l_out, amount=z_top_skirt - z_top_seat).moved(
        bd.Location((0, 0, z_top_seat))
    ) - bd.extrude(sk_l_in, amount=z_top_skirt - z_top_seat + 0.20).moved(
        bd.Location((0, 0, z_top_seat - 0.10))
    )
    #    - Main spacer wall (`Z = +9.75 .. +19.45` across full `P_L'`)
    top_spacer = bd.extrude(sk_l_out, amount=z_top_seat - z_mid).moved(
        bd.Location((0, 0, z_mid))
    ) - bd.extrude(sk_l_cav, amount=z_top_seat - z_mid + 0.20).moved(
        bd.Location((0, 0, z_mid - 0.10))
    )
    #    - SE L-cutout protective floor slab (`Z = +9.75 .. +11.75`): `sk_l_out - sk_r_cav`!
    se_shield_2d = sk_l_out - sk_r_cav
    se_shield = bd.extrude(se_shield_2d, amount=SHIELD_THICK).moved(
        bd.Location((0, 0, z_mid))
    )

    body = bot_skirt + bot_spacer + nw_shield + top_skirt + top_spacer + se_shield

    # 3. Integrate Trackball Keeper Halo Ring (clipped strictly inside `sk_r_out` so outer wall stays flush)
    halo = build_trackball_keeper_halo()
    outer_clip = bd.extrude(sk_r_out, amount=30.0).moved(bd.Location((0, 0, 0.0)))
    body = body + (halo & outer_clip)

    # 4. Integrate Bottom (Right) & Top (Left) One-Touch Retention Latches + USB-C Dust Shields
    adds_r, cuts_r = build_Retention_features_for_half(is_top_left=False)
    adds_l, cuts_l = build_Retention_features_for_half(is_top_left=True)

    for c in cuts_r + cuts_l:
        body = body - c
    for a in adds_r + adds_l:
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
    Builds 5 realistic Ø 8.0 x 2.0 mm cylindrical rubber feet stuck flat onto the outer tilted
    bottom plane of `right.step` (`is_right=True`) or `left.step` (`is_right=False`), inset 6.5 mm
    inside the 5 outer corners of the case bottom.
    """
    sgn = 1.0 if is_right else -1.0
    foot_xy_abs = [
        (14.50, -38.50),    # NW thumb-north corner
        (128.00, -38.50),   # NE pinky-north corner
        (128.00, -92.50),   # SE pinky-south corner (5.86 mm inside pinky edge, clear of 1.0 mm latch hook)
        (91.00, -119.00),   # Thumb-east south corner
        (14.50, -119.00),   # SW thumb-south corner
    ]
    p_thumb = (sgn * X_THUMB_OUTER, -80.0, Z_THUMB_BOTTOM)
    p_pinky = (sgn * X_PINKY_OUTER, -80.0, Z_PINKY_BOTTOM)
    dx = p_pinky[0] - p_thumb[0]
    dz = p_pinky[2] - p_thumb[2]
    # Outer outward-pointing bottom normal (pointing roughly in -Z)
    norm_out = (dz, 0.0, -dx) if is_right else (-dz, 0.0, dx)

    feet = []
    side_tag = "Right" if is_right else "Left"
    for idx, (ax, fy) in enumerate(foot_xy_abs):
        fx = sgn * ax
        fz = Z_THUMB_BOTTOM + (Z_PINKY_BOTTOM - Z_THUMB_BOTTOM) * (ax - X_THUMB_OUTER) / (
            X_PINKY_OUTER - X_THUMB_OUTER
        )
        # Offset by 0.01 mm outward from bottom face so B-rep overlap_volume == 0.00000000
        n_len = math.hypot(norm_out[0], norm_out[2])
        ux, uz = norm_out[0] / n_len, norm_out[2] / n_len
        foot_plane = bd.Plane(origin=(fx + 0.01 * ux, fy, fz + 0.01 * uz), z_dir=(ux, 0.0, uz))
        cyl = bd.extrude(foot_plane * bd.Circle(RUBBER_FOOT_RADIUS), amount=RUBBER_FOOT_HEIGHT - 0.01).solids()[0]
        cyl.label = f"{side_tag}_Rubber_Foot_{idx + 1}"
        feet.append(cyl)
    return feet


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
) -> None:
    """
    Verifies:
      1. Zero B-rep overlap (`overlap_volume == 0.00000000 mm^3`) across `Carrying_Frame`, all 674 solids
         of Left & Right full assemblies, and all 10 rubber feet.
      2. Minimum surface clearances (Ball keeper gap, Inertia wheel, Keycaps, USB-C shells, Rubber feet).
      3. Positive 6-DOF mechanical lock (`±X, ±Y, ±Z`) of Right case, Left case, and 25mm Trackball.
    """
    frame_bb = frame_asm.bounding_box()
    all_kb_and_feet = right_solids + left_packed_solids + right_feet + left_packed_feet

    # 1. Frame vs every solid
    max_ov_frame = 0.0
    worst_label = ""
    for idx, s in enumerate(all_kb_and_feet):
        sb = s.bounding_box()
        if _aabb_intersects(frame_bb, sb):
            ov = overlap_volume(frame_asm, s)
            if ov > max_ov_frame:
                max_ov_frame = ov
                worst_label = f"{getattr(s, 'label', '') or idx} bbox={sb}"

    # 2. Right solids (+ feet) vs Left packed solids (+ feet)
    r_group = [(s, s.bounding_box()) for s in (right_solids + right_feet)]
    l_group = [(s, s.bounding_box()) for s in (left_packed_solids + left_packed_feet)]
    max_ov_rl = 0.0
    for sr, br in r_group:
        for sl, bl in l_group:
            if _aabb_intersects(br, bl):
                ov = overlap_volume(sr, sl)
                if ov > max_ov_rl:
                    max_ov_rl = ov

    print(
        f"[carrying-assembly] Overlap check ({len(all_kb_and_feet)} solids + frame): "
        f"Frame_vs_All={max_ov_frame:.8f} mm^3, Right_vs_Left={max_ov_rl:.8f} mm^3"
    )
    assert max_ov_frame == 0.0, f"B-rep interference with Carrying_Frame: {max_ov_frame:.8f} mm^3 at {worst_label}!"
    assert max_ov_rl == 0.0, f"B-rep interference between Right & Left halves: {max_ov_rl:.8f} mm^3!"

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

    usbc_solids = [
        s
        for s in right_solids
        if 39.0 < s.volume < 58.0 and -7.6 < s.bounding_box().min.Z < -7.0 and -4.5 < s.bounding_box().max.Z < -4.1
    ] + [
        s
        for s in left_packed_solids
        if 39.0 < s.volume < 58.0
        and (H_SEP + 4.1) < s.bounding_box().min.Z < (H_SEP + 4.5)
        and (H_SEP + 7.0) < s.bounding_box().max.Z < (H_SEP + 7.6)
    ]
    assert len(usbc_solids) >= 4, f"Expected >= 4 USB-C connector solids, got {len(usbc_solids)}"

    clr_ball = min_surface_clearance([ball_solid], frame_asm)
    clr_wheel = min_surface_clearance([wheel_solid], frame_asm)
    clr_keycaps = min_surface_clearance(right_keycaps + left_keycaps_packed, frame_asm)
    clr_usbc = min_surface_clearance(usbc_solids, frame_asm)
    clr_feet = min_surface_clearance(right_feet + left_packed_feet, frame_asm)
    clr_ball_to_left_cap = min_surface_clearance(left_keycaps_packed, ball_solid)

    print(
        f"[carrying-assembly] Minimum surface clearances:\n"
        f"  - Frame vs 25mm Trackball (Keeper Halo): {clr_ball:.3f} mm (target 0.50..0.70 mm)\n"
        f"  - 25mm Trackball vs Left Keycap (SW18):  {clr_ball_to_left_cap:.3f} mm (>= 1.00 mm)\n"
        f"  - Frame vs Inertia Wheel:                {clr_wheel:.3f} mm (>= 1.50 mm)\n"
        f"  - Frame vs All 40 Keycaps:               {clr_keycaps:.3f} mm (>= 0.75 mm)\n"
        f"  - Frame vs All 4 USB-C Shells:           {clr_usbc:.3f} mm (>= 0.30 mm)\n"
        f"  - Frame vs All 10 Rubber Feet:           {clr_feet:.3f} mm (>= 2.00 mm)"
    )
    assert 0.50 <= clr_ball <= 0.70, f"Trackball keeper clearance {clr_ball:.3f} mm outside [0.50, 0.70] mm!"
    assert clr_ball_to_left_cap >= 1.00, f"Ball-to-Left-keycap gap {clr_ball_to_left_cap:.3f} mm < 1.00 mm!"
    assert clr_wheel >= 1.50, f"Inertia wheel clearance {clr_wheel:.3f} mm < 1.50 mm!"
    assert clr_keycaps >= 0.75, f"Keycap clearance {clr_keycaps:.3f} mm < 0.75 mm!"
    assert clr_usbc >= 0.30, f"USB-C shell clearance {clr_usbc:.3f} mm < 0.30 mm!"
    assert clr_feet >= 2.00, f"Rubber feet clearance {clr_feet:.3f} mm < 2.00 mm!"

    # 3. 6-DOF positive mechanical lock check (`±X, ±Y, ±Z` <= 0.65 mm displacement causes solid interference)
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
    print("[carrying-assembly] 6-DOF mechanical lock & trackball shock-retention checks: ALL PASS!")


def main() -> None:
    print("=== Building curcur40 Snap-In PA12 Carrying Frame & Full Packed Assembly ===")
    CASES_DIR.mkdir(parents=True, exist_ok=True)
    ASSEMBLIES_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Build 1-piece PA12 Carrying Frame in assembly pose & shift to Z = 0.0000 mm print bed pose
    frame_asm = build_carrying_frame_assembly_pose()
    bb_asm = frame_asm.bounding_box()
    frame_print = frame_asm.moved(bd.Location((0.0, 0.0, -bb_asm.min.Z)))
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

    # 4. Run full 684-solid B-rep interference, clearance & 6-DOF retention checks
    verify_carrying_assembly(frame_asm, right_solids, left_packed_solids, right_feet, left_packed_feet)

    # 5. Export desk-level parallel brick verification assembly (`carrying-assembly.step`)
    right_grp = bd.Compound(children=right_solids + right_feet)
    right_grp.label = "Right_Keyboard_With_Feet"
    left_grp = bd.Compound(children=left_packed_solids + left_packed_feet)
    left_grp.label = "Left_Keyboard_Packed_With_Feet"

    packed_desk = transform_packed_to_desk(
        bd.Compound(children=[frame_asm, right_grp, left_grp])
    )
    packed_desk.label = "curcur40_carrying_assembly"
    bb_desk = packed_desk.bounding_box()
    print(
        f"Packed Brick Envelope (including D8x2mm rubber feet on both outer bottoms): "
        f"{bb_desk.size.X:.2f} x {bb_desk.size.Y:.2f} x {bb_desk.size.Z:.2f} mm "
        f"(Z = [{bb_desk.min.Z:.4f}, {bb_desk.max.Z:.4f}] mm)"
    )
    assert abs(bb_desk.min.Z - 0.0) < 0.05, f"Expected desk-level Z_min ~ 0.00 mm, got {bb_desk.min.Z:.4f} mm!"

    carrying_asm_path = ASSEMBLIES_DIR / "carrying-assembly.step"
    bd.export_step(packed_desk, str(carrying_asm_path))
    print(f"Exported {carrying_asm_path.name} successfully!")


if __name__ == "__main__":
    main()
