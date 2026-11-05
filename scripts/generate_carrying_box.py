# -*- coding: utf-8 -*-
"""
Generate curcur40 Official Carrying Box & Calculated Snap-Detent Lid:
Upside-Down-Reversible (`Rot_Y(180 deg)` Symmetric) Orthogonal 90-deg Rectangular Slide-In Carrying Box
(`cases/carrying-box.step`, `cases/carrying-box.stl`, `cases/carrying-box-lid.step`, `cases/carrying-box-lid.stl`)
and Full Packed Verification Assemblies (`cases/assemblies/carrying-box-with-lid-assembly.step` &
`cases/assemblies/carrying-box-assembly.step`).

Design Highlights:
1. 100% Top/Bottom Reversible (`右手トラックボール側を下にしても上にしても、箱もフタも上下逆さま関係なくスッと入る`):
   - Both `Carrying_Box` and `Carrying_Box_Lid` are mathematically exact `Rot_Y(180 deg)` symmetric solids
     around `(X_MID_DESK, Z_MID_DESK)` with ZERO height increase (`142.40 x 111.85 x 65.42 mm` closed).
   - Central divider uses a point-symmetric cranked web (`z_asm in [12.80, 15.05]` on West, smooth `20 mm`
     angled center ramp, `z_asm in [4.45, 6.70]` on East) with dual `15.60 mm` Trackball Keeper U-slots, so
     Right's 25mm trackball glides in with `0.58 mm` non-contact keeper clearance whether Right is on the
     bottom OR flipped to the top!
2. 100% Hole-Free End Walls with Dual Symmetric Internal Blind Moats (`堀`) & Backstop Shoulders:
   - South Back Wall (`Y = -133.70 mm`, `2.20 mm` solid) has NO exterior holes: keyboards stop positively
     against `Y = -126.95 mm` backstop shoulders while `J1` `CIO-SLMG-T-C` floats inside symmetric `4.55 mm`
     deep internal blind moats (`1.01 mm` axial clearance).
   - North Snap Cap Lid (`6.50 mm` cap, `Y in [-28.35, -21.85]`) likewise has NO exterior holes, with symmetric
     `4.30 mm` deep internal blind moats for `rJ1` `CIO-SLMG-T-C`.
3. Mechanically Calculated Long-Beam `26-deg` Cam-Detent Lid Latch (`verify_lid_snap_mechanics()`):
   - `L = 14.00 mm` free PA12 cantilever (`t = 1.85 mm`, `b = 9.50 mm`, `0.85 mm` inward flex clearance,
     `delta = 0.50 mm` undercut, `26-deg` shallow exit cam ramp).
   - Opening leverage exceeds eccentric lock moment by `8.61x` (`mu_crit = 1.53 >> 0.30`), giving a smooth
     straight pull-off force of `9.73 N (~0.99 kgf)`, push-to-close force of `6.35 N (~0.65 kgf)`, and root
     strain of only `0.71%` (`4.94x` safety factor below PA12 `3.5%` yield strain), paired with `1.20 mm` deep
     side finger-grip flutes.
"""
from __future__ import annotations

import math
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
CASES_DIR = WORKSPACE / "cases"
ASSEMBLIES_DIR = WORKSPACE / "cases" / "assemblies"

# Canonical keyboard outer geometry constants (`docs/case_spec.md`)
X_THUMB_OUTER = 7.0250
X_PINKY_OUTER = 135.8580
Y_NORTH_OUTER = -30.8375
Y_SOUTH_OUTER = -126.6500
Z_THUMB_BOTTOM = -26.9000
Z_PINKY_BOTTOM = -10.0000
TAN_TENT = (Z_PINKY_BOTTOM - Z_THUMB_BOTTOM) / (X_PINKY_OUTER - X_THUMB_OUTER)
THETA_TENT_RAD = math.atan(TAN_TENT)
THETA_TENT_DEG = math.degrees(THETA_TENT_RAD)

# Wedge-canceling `Rot_X(180 deg)` face-to-face stacking parameters
H_SEP = 19.5000
DX_LEFT = X_THUMB_OUTER + X_PINKY_OUTER          # +142.8830 mm
DY_LEFT = Y_NORTH_OUTER + Y_SOUTH_OUTER          # -157.4875 mm
MID_X = 0.5 * DX_LEFT                            #  +71.4415 mm
MID_Z = 0.5 * H_SEP                              #   +9.7500 mm

# USB-C port coordinates, `CIO-SLMG-T-C` tip envelope, Trackball & Rubber-Foot specs
HOST_USBC_CX_R = 26.5750
SPLIT_USBC_CY_R = -86.6500
USBC_CENTER_Z_R = -5.8500
CIO_TIP_WIDTH = 12.4000
CIO_TIP_HEIGHT = 7.0000
CIO_TIP_PROTRUSION = 3.8000
TB_CX = 23.8125
TB_CY = -109.5375
RUBBER_FOOT_RADIUS = 4.0000                      # D 8.00 mm
RUBBER_FOOT_HEIGHT = 2.0000                      # 2.00 mm height

# Internal slide clearances (in `asm` frame)
XY_SLIDE_GAP = 0.3000                            # >= 0.30 mm JLC3DP moving clearance
Z_SLIDE_GAP = 0.2000                             # 0.20 mm vertical rail clearance
BOX_WALL = 2.2000                                # 2.20 mm solid end wall thickness

X_IN_WEST = X_THUMB_OUTER - XY_SLIDE_GAP         # 6.7250 mm
X_IN_EAST = X_PINKY_OUTER + XY_SLIDE_GAP         # 136.1580 mm

# South backstop shoulder & dual internal blind moats (`堀`) — 100% hole-free South exterior wall!
Y_IN_SOUTH = Y_SOUTH_OUTER - XY_SLIDE_GAP        # -126.9500 mm (Keyboard backstop shoulder!)
Y_MOAT_SOUTH = -131.5000                         # -131.5000 mm (4.55 mm deep internal moat; 1.01 mm clear of J1 tip)
Y_OUT_SOUTH = Y_MOAT_SOUTH - BOX_WALL            # -133.7000 mm (2.20 mm solid hole-free South exterior wall)
Y_MOUTH = -28.5000                               # Box exterior depth = 105.2000 mm

# North Snap Cap Lid (`carrying-box-lid`, 6.50 mm cap) — 100% hole-free North exterior wall!
Y_LID_IN = Y_MOUTH + 0.1500                      # -28.3500 mm (0.15 mm axial seam gap -> 0.00 mm^3 overlap)
Y_LID_MOAT = -24.0500                            # -24.0500 mm (4.30 mm deep internal moat; > 2.1 mm clear of rJ1 tip)
Y_LID_OUT = Y_LID_MOAT + BOX_WALL                # -21.8500 mm (6.50 mm cap wall; 2.20 mm solid hole-free front face)

# Perpendicular offsets from bare angled case bottoms (horizontal Z planes in `box_desk`!)
COS_TENT = math.cos(THETA_TENT_RAD)
SIN_TENT = math.sin(THETA_TENT_RAD)
D_RUNNER_PERP = Z_SLIDE_GAP                      # 0.20 mm perpendicular gap under bare outer case corners
D_WELL_PERP = 2.7500                             # 2.75 mm recessed floor/ceiling well (0.75 mm clear of 2.0 mm feet!)
D_OUT_PERP = 4.7500                              # 4.75 mm outer box face (2.00 mm solid horizontal top & bottom walls!)

# Exact Orthogonal Rectangular Cuboid (`直方体`) dimensions in `box_desk` coordinates (`Z in [0, H_BOX]`)
H_BARE_BRICK = (abs(Z_THUMB_BOTTOM) + H_SEP + abs(Z_PINKY_BOTTOM)) * COS_TENT  # 55.92095 mm
H_BOX = H_BARE_BRICK + 2.0 * D_OUT_PERP                                        # 65.42095 mm
Z_MID_DESK = 0.5 * H_BOX                                                       # 32.71048 mm
X_MID_DESK = (
    X_PINKY_OUTER
    + (0.5 * DX_LEFT - X_PINKY_OUTER) * COS_TENT
    + (0.5 * H_SEP - Z_PINKY_BOTTOM) * SIN_TENT
)                                                                              # 74.55712 mm
W_BOX = 142.4000                                                               # 142.4000 mm exact cuboid width
X_BOX_WEST = X_MID_DESK - 0.5 * W_BOX                                          #  3.35712 mm
X_BOX_EAST = X_MID_DESK + 0.5 * W_BOX                                          # 145.75712 mm

# Point-Symmetric Stepped/Cranked Central Divider (`Z_asm` on West `[12.80, 15.05]`, East `[4.45, 6.70]`)
DIV_W_Z_MIN = 12.8000
DIV_W_Z_MAX = 15.0500
DIV_E_Z_MIN = H_SEP - DIV_W_Z_MAX                # 4.4500 mm (0.85 mm clear above +3.60 mm pinky keycaps!)
DIV_E_Z_MAX = H_SEP - DIV_W_Z_MIN                # 6.7000 mm
DIV_RAMP_HALF_DX = 10.0000                       # Smooth 20.00 mm ramp across X_asm in [61.4415, 81.4415]
TB_SLOT_R = 7.8000                               # 15.60 mm wide U-slot (0.58 mm radial gap to 25mm ball)

# Centered `Rot_Y(180 deg)`-Symmetric Finger-Pull Cutouts (`X_desk` centered at `X_MID_DESK`)
FINGER_CX_DESK = X_MID_DESK                      # 74.55712 mm
FINGER_W_DESK = 32.0000                          # 32.00 mm wide
FINGER_X_MIN_DESK = FINGER_CX_DESK - 0.5 * FINGER_W_DESK
FINGER_X_MAX_DESK = FINGER_CX_DESK + 0.5 * FINGER_W_DESK
FINGER_Y_MIN = -43.5000                          # 15.00 mm deep scoop from Y_MOUTH = -28.50 mm

# Calculated PA12 Lid Snap-Detent Mechanical Parameters (`verify_lid_snap_mechanics`)
SNAP_E_MPA = 1700.0                              # MJF/SLS PA12 Young's modulus (MPa = N/mm^2)
SNAP_MU = 0.30                                   # Sintered PA12-on-PA12 coefficient of friction
SNAP_YIELD_STRAIN = 0.035                        # Conservative elastic strain limit (3.5%)
SNAP_BEAM_L = 14.0000                            # 14.00 mm free cantilever length (Y = -28.35 to -42.35 mm)
SNAP_BEAM_T = 1.8500                             # 1.85 mm beam thickness (>= 0.80 mm)
SNAP_BEAM_B = 9.5000                             # 9.50 mm beam width (0.25 mm Z guide fit inside 10.00 mm socket)
SNAP_DELTA = 0.5000                              # 0.50 mm radial snap undercut engagement
SNAP_FLEX_GAP = 0.8500                           # 0.85 mm free inward flex clearance (> 0.50 mm travel!)
SNAP_ALPHA_OUT_DEG = 26.0                        # 26.0-deg shallow exit cam angle (eliminates self-locking!)
SNAP_ALPHA_IN_DEG = 20.0                         # 20.0-deg smooth push-to-close entry cam angle


def z_case_bottom_right(x: float) -> float:
    """Exact Z coordinate on Right keyboard's angled outer bottom plane at X."""
    return Z_THUMB_BOTTOM + (x - X_THUMB_OUTER) * TAN_TENT


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


def build_rubber_feet_in_case_pose(is_right: bool) -> list[bd.Solid]:
    """Builds 5 realistic D 8.0 x 2.0 mm cylindrical rubber feet on the outer tilted bottom plane."""
    sgn = 1.0 if is_right else -1.0
    foot_xy_abs = [
        (14.50, -38.50),
        (128.00, -38.50),
        (128.00, -92.50),
        (91.00, -119.00),
        (14.50, -119.00),
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
    protruding `3.80 mm` outside the case outer wall + recessed neck) for Host & Split USB-C ports.
    """
    sgn = 1.0 if is_right else -1.0
    side_tag = "Right" if is_right else "Left"

    host_cx = sgn * HOST_USBC_CX_R
    p_host = bd.Plane(origin=(host_cx, Y_NORTH_OUTER + 0.05, USBC_CENTER_Z_R), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
    host_head = bd.extrude(
        p_host * bd.RectangleRounded(CIO_TIP_WIDTH, CIO_TIP_HEIGHT, 3.20),
        amount=CIO_TIP_PROTRUSION,
    ).solids()[0]
    p_host_neck = bd.Plane(origin=(host_cx, Y_NORTH_OUTER - 1.15, USBC_CENTER_Z_R), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
    host_neck = bd.extrude(p_host_neck * bd.RectangleRounded(8.40, 2.60, 1.10), amount=1.25).solids()[0]
    host_tip = (host_head + host_neck).solids()[0]
    host_tip.label = f"{side_tag}_Host_USBC_CIO_Tip"

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
    split_neck = bd.extrude(p_split_neck * bd.RectangleRounded(8.40, 2.60, 1.10), amount=1.25).solids()[0]
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


def sym_desk_loc() -> bd.Location:
    """Exact 180-deg rotation around `(X_MID_DESK, Z_MID_DESK)` parallel to Y-axis (upside-down flip!)."""
    return bd.Pos(2.0 * X_MID_DESK, 0.0, H_BOX) * bd.Rot(0.0, 180.0, 0.0)


def flip_shape_upside_down_desk(shape: bd.Shape) -> bd.Shape:
    lbl = getattr(shape, "label", "")
    loc_w = sym_desk_loc().wrapped
    if isinstance(shape, bd.Solid):
        res = bd.Solid(shape.wrapped.Moved(loc_w))
    else:
        res = shape.moved(sym_desk_loc())
    res.label = f"{lbl}_Flipped" if lbl else ""
    return res


def z_bot_plane(x: float, d_perp: float) -> float:
    return z_case_bottom_right(x) - d_perp / COS_TENT


def z_top_plane(x: float, d_perp: float) -> float:
    z_left_bare = (H_SEP - Z_PINKY_BOTTOM) + (x - X_THUMB_OUTER) * TAN_TENT
    return z_left_bare + d_perp / COS_TENT


def asm_xz_to_desk(x_asm: float, z_asm: float) -> tuple[float, float]:
    dx = x_asm - X_PINKY_OUTER
    dz = z_asm - Z_PINKY_BOTTOM
    return (
        X_PINKY_OUTER + dx * COS_TENT + dz * SIN_TENT,
        D_OUT_PERP + dz * COS_TENT - dx * SIN_TENT,
    )


def transform_asm_to_box_desk(shape: bd.Shape) -> bd.Shape:
    lbl = getattr(shape, "label", "")
    children = getattr(shape, "children", None)
    if children:
        res = bd.Compound(children=[transform_asm_to_box_desk(ch) for ch in children])
        res.label = lbl
        return res
    loc = (
        bd.Pos(X_PINKY_OUTER, 0.0, D_OUT_PERP)
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


def extrude_xz_profile_along_y(xz_pts: list[tuple[float, float]], y_min: float, y_max: float) -> bd.Solid:
    with bd.BuildSketch(bd.Plane.XZ) as sk:
        bd.Polygon(xz_pts, align=None)
    s = bd.extrude(sk.sketch, amount=y_max - y_min, both=False)
    bb = s.bounding_box()
    return s.moved(bd.Location((0.0, 0.5 * (y_min + y_max) - bb.center().Y, 0.0))).solids()[0]


def verify_lid_snap_mechanics() -> dict[str, float]:
    """
    Analytical Euler-Bernoulli + Eccentric-Moment + Friction-Cone verification of the Lid Snap Prongs.
    Proves that pulling straight on the Lid in `+Y` cleanly deflects the prongs inward WITHOUT self-locking,
    requires ~9.7 N (~1.0 kgf) pull force, and stays nearly 5x below PA12's elastic strain limit.
    """
    ei = SNAP_E_MPA * (SNAP_BEAM_B * (SNAP_BEAM_T ** 3) / 12.0)
    ecc = 0.5 * (SNAP_BEAM_T + SNAP_DELTA)

    a_out = math.radians(SNAP_ALPHA_OUT_DEG)
    a_in = math.radians(SNAP_ALPHA_IN_DEG)

    open_term = 2.0 * SNAP_BEAM_L * (math.cos(a_out) - SNAP_MU * math.sin(a_out))
    lock_term = 3.0 * ecc * (math.sin(a_out) + SNAP_MU * math.cos(a_out))
    leverage_ratio = open_term / lock_term

    mu_crit = (2.0 * SNAP_BEAM_L * math.cos(a_out) - 3.0 * ecc * math.sin(a_out)) / (
        2.0 * SNAP_BEAM_L * math.sin(a_out) + 3.0 * ecc * math.cos(a_out)
    )

    compliance_out = (SNAP_BEAM_L ** 2) * (open_term - lock_term) / (6.0 * ei)
    n_out = SNAP_DELTA / compliance_out
    f_pull_total = 2.0 * n_out * (math.sin(a_out) + SNAP_MU * math.cos(a_out))

    open_in = 2.0 * SNAP_BEAM_L * (math.cos(a_in) - SNAP_MU * math.sin(a_in))
    lock_in = 3.0 * ecc * (math.sin(a_in) + SNAP_MU * math.cos(a_in))
    n_in = SNAP_DELTA / ((SNAP_BEAM_L ** 2) * (open_in + lock_in) / (6.0 * ei))
    f_push_total = 2.0 * n_in * (math.sin(a_in) + SNAP_MU * math.cos(a_in))

    strain_max = 1.5 * SNAP_BEAM_T * SNAP_DELTA / (SNAP_BEAM_L ** 2)
    safety_factor = SNAP_YIELD_STRAIN / strain_max

    print(
        f"[lid-snap-mechanics] L={SNAP_BEAM_L:.1f}mm, t={SNAP_BEAM_T:.2f}mm, b={SNAP_BEAM_B:.1f}mm, "
        f"delta={SNAP_DELTA:.2f}mm, alpha_out={SNAP_ALPHA_OUT_DEG:.1f} deg:\n"
        f"  - Opening vs Eccentric-Lock Leverage: {open_term:.2f} vs {lock_term:.2f} mm "
        f"(ratio = {leverage_ratio:.2f}x, mu_crit = {mu_crit:.2f} >> mu = {SNAP_MU:.2f})\n"
        f"  - Straight Pull-Off Force (2 prongs): {f_pull_total:.2f} N ({f_pull_total / 9.80665:.2f} kgf)\n"
        f"  - Push-To-Close Force (2 prongs):     {f_push_total:.2f} N ({f_push_total / 9.80665:.2f} kgf)\n"
        f"  - Max Root Bending Strain:            {strain_max * 100.0:.2f}% "
        f"(PA12 elastic limit 3.50%, safety factor = {safety_factor:.2f}x)"
    )
    assert leverage_ratio >= 5.0 and mu_crit >= 1.20, "Lid snap prong is too close to friction/eccentric self-lock!"
    assert 6.0 <= f_pull_total <= 14.0, f"Pull-off force {f_pull_total:.2f} N outside ergonomic [6, 14] N target!"
    assert 4.0 <= f_push_total <= 12.0, f"Push-on force {f_push_total:.2f} N outside ergonomic [4, 12] N target!"
    assert strain_max <= 0.012, f"Root bending strain {strain_max * 100:.2f}% > 1.20% fatigue-safe target!"
    assert SNAP_FLEX_GAP >= SNAP_DELTA + 0.25, "Insufficient inward flex clearance behind snap prong!"
    return {
        "f_pull_n": f_pull_total,
        "f_push_n": f_push_total,
        "strain_pct": strain_max * 100.0,
        "leverage_ratio": leverage_ratio,
        "mu_crit": mu_crit,
    }


def build_entrance_detents_desk() -> tuple[bd.Solid, bd.Solid, bd.Solid, bd.Solid]:
    """Symmetric West & East entrance click-detents (holds keyboards gently even while Lid is open)."""
    z_bot_slot = 7.4000
    z_arm_bot = 9.4000
    z_arm_top = 16.9000
    z_top_slot = 18.9000
    y_slot_root_straight = -50.5000

    cut_w = bd.Box(
        10.00,
        (Y_MOUTH + 2.00) - y_slot_root_straight,
        z_top_slot - z_bot_slot,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((0.00, y_slot_root_straight, z_bot_slot)))
    root_edges = cut_w.edges().filter_by(
        lambda e: abs(e.bounding_box().size.X - 10.00) < 0.1
        and abs(e.bounding_box().min.Y - y_slot_root_straight) < 0.05
    )
    assert len(root_edges) == 2
    cut_w = bd.fillet(root_edges, radius=1.00)

    xy_pts_asm = [
        (-5.0000, -51.8000),
        (X_IN_WEST, -51.8000),
        (X_IN_WEST, -32.0000),
        (8.0250, -30.7000),
        (8.0250, -29.8000),
        (6.5250, Y_MOUTH),
        (-5.0000, Y_MOUTH),
    ]
    with bd.BuildSketch(bd.Plane.XY.offset(-32.00)) as sk_arm_asm:
        bd.Polygon(xy_pts_asm, align=None)
    arm_raw_desk = transform_asm_to_box_desk(bd.extrude(sk_arm_asm.sketch, amount=28.00).solids()[0])
    arm_trim_box = bd.Box(
        15.00,
        Y_MOUTH - (-51.8000),
        z_arm_top - z_arm_bot,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((X_BOX_WEST, -51.8000, z_arm_bot)))
    arm_w = (arm_raw_desk & arm_trim_box).solids()[0]

    arm_e = flip_shape_upside_down_desk(arm_w)
    cut_e = flip_shape_upside_down_desk(cut_w)
    return arm_w, cut_w, arm_e, cut_e


def build_hidden_lid_snap_sockets_and_prongs_desk() -> tuple[bd.Solid, bd.Solid, bd.Solid, bd.Solid]:
    """
    Builds `Rot_Y(180 deg)`-symmetric concealed corner sockets (`Z_desk in [42.00, 52.00]` on West,
    `[13.42, 23.42]` on East) and calculated `L = 14.00 mm` / `26-deg` cam-detent PA12 snap prongs.
    """
    x_s_out = X_BOX_WEST + 1.8000                      # 5.1571 mm (1.80 mm solid outer West wall)
    x_p_out = x_s_out + SNAP_FLEX_GAP                  # 6.0071 mm (0.85 mm free inward flex clearance!)
    x_p_in = x_p_out + SNAP_BEAM_T                     # 7.8571 mm (1.85 mm beam thickness)
    x_s_throat = x_p_in + 0.3000                       # 8.1571 mm (0.30 mm lateral guide clearance)
    x_p_hook = x_s_throat + SNAP_DELTA                 # 8.6571 mm (0.50 mm snap undercut!)
    x_s_undercut = x_p_hook + 0.3500                   # 9.0071 mm (0.35 mm radial clearance; 2.62 mm to upper_cav!)

    tan_out = math.tan(math.radians(SNAP_ALPHA_OUT_DEG))
    tan_in = math.tan(math.radians(SNAP_ALPHA_IN_DEG))

    y_sock_throat_end = -41.5000
    y_sock_ramp_end = y_sock_throat_end - (x_s_undercut - x_s_throat) / tan_out
    y_sock_back = -48.5000

    sock_xy = [
        (x_s_out, Y_MOUTH + 1.0000),
        (x_s_throat, Y_MOUTH + 1.0000),
        (x_s_throat, y_sock_throat_end),
        (x_s_undercut, y_sock_ramp_end),
        (x_s_undercut, y_sock_back),
        (x_s_out, y_sock_back),
    ]
    z_sock_bot = 42.0000
    z_sock_h = 10.0000
    with bd.BuildSketch(bd.Plane.XY.offset(z_sock_bot)) as sk_sock:
        bd.Polygon(sock_xy, align=None)
    sock_w = bd.extrude(sk_sock.sketch, amount=z_sock_h).solids()[0]
    sock_back_edges = sock_w.edges().filter_by(
        lambda e: abs(e.bounding_box().size.Z - z_sock_h) < 0.1 and abs(e.bounding_box().center().Y - y_sock_back) < 0.05
    )
    assert len(sock_back_edges) == 2
    sock_w = bd.fillet(sock_back_edges, radius=1.00)

    hook_protrusion = x_p_hook - x_p_in
    y_prong_ramp_start = -41.1000
    y_prong_crest_start = y_prong_ramp_start - hook_protrusion / tan_out
    y_prong_crest_end = -43.8000
    y_prong_tip = y_prong_crest_end - hook_protrusion / tan_in

    prong_xy = [
        (x_p_out, Y_LID_IN + 1.5000),
        (x_p_in, Y_LID_IN + 1.5000),
        (x_p_in, y_prong_ramp_start),
        (x_p_hook, y_prong_crest_start),
        (x_p_hook, y_prong_crest_end),
        (x_p_in, y_prong_tip),
        (x_p_out, y_prong_tip),
    ]
    z_prong_bot = z_sock_bot + 0.5 * (z_sock_h - SNAP_BEAM_B)
    with bd.BuildSketch(bd.Plane.XY.offset(z_prong_bot)) as sk_prong:
        bd.Polygon(prong_xy, align=None)
    prong_w = bd.extrude(sk_prong.sketch, amount=SNAP_BEAM_B).solids()[0]

    sock_e = flip_shape_upside_down_desk(sock_w)
    prong_e = flip_shape_upside_down_desk(prong_w)
    return sock_w, sock_e, prong_w, prong_e


def build_carrying_box_and_lid_desk() -> tuple[bd.Solid, bd.Solid]:
    """
    Builds 100% `Rot_Y(180 deg)`-symmetric `Carrying_Box` and `Carrying_Box_Lid` in `box_desk` coordinates.
    """
    outer_shell = bd.Box(
        W_BOX,
        Y_MOUTH - Y_OUT_SOUTH,
        H_BOX,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((X_BOX_WEST, Y_OUT_SOUTH, 0.0)))
    long_y_edges = outer_shell.edges().filter_by(
        lambda e: abs(e.bounding_box().size.Y - (Y_MOUTH - Y_OUT_SOUTH)) < 0.2
    )
    assert len(long_y_edges) == 4
    outer_shell = bd.fillet(long_y_edges, radius=2.00)

    x_rim_w = 8.5250
    x_rim_e = DX_LEFT - x_rim_w
    x_well_w = 8.8250
    x_well_e = DX_LEFT - x_well_w
    x_ramp_w = MID_X - DIV_RAMP_HALF_DX
    x_ramp_e = MID_X + DIV_RAMP_HALF_DX

    lower_cav_xz = [
        (X_IN_WEST, z_bot_plane(X_IN_WEST, D_RUNNER_PERP)),
        (x_well_w, z_bot_plane(x_well_w, D_RUNNER_PERP)),
        (x_well_w, z_bot_plane(x_well_w, D_WELL_PERP)),
        (x_well_e, z_bot_plane(x_well_e, D_WELL_PERP)),
        (x_well_e, z_bot_plane(x_well_e, D_RUNNER_PERP)),
        (X_IN_EAST, z_bot_plane(X_IN_EAST, D_RUNNER_PERP)),
        (X_IN_EAST, Z_SLIDE_GAP),
        (x_rim_e, Z_SLIDE_GAP),
        (x_rim_e, DIV_E_Z_MIN),
        (x_ramp_e, DIV_E_Z_MIN),
        (x_ramp_w, DIV_W_Z_MIN),
        (x_rim_w, DIV_W_Z_MIN),
        (x_rim_w, Z_SLIDE_GAP),
        (X_IN_WEST, Z_SLIDE_GAP),
    ]
    lower_cav_desk = transform_asm_to_box_desk(extrude_xz_profile_along_y(lower_cav_xz, Y_IN_SOUTH, Y_MOUTH + 5.0))
    upper_cav_desk = flip_shape_upside_down_desk(lower_cav_desk)

    with bd.BuildSketch(bd.Plane.XY.offset(DIV_W_Z_MIN - 0.60)) as sk_tb_w:
        with bd.Locations([(TB_CX, TB_CY)]):
            bd.Circle(TB_SLOT_R)
        y_len = (Y_MOUTH + 5.0) - TB_CY
        with bd.Locations([(TB_CX, TB_CY + 0.5 * y_len)]):
            bd.Rectangle(2.0 * TB_SLOT_R, y_len)
    tb_slot_w_desk = transform_asm_to_box_desk(
        bd.extrude(sk_tb_w.sketch, amount=(DIV_W_Z_MAX - DIV_W_Z_MIN) + 1.20).solids()[0]
    )
    tb_slot_e_desk = flip_shape_upside_down_desk(tb_slot_w_desk)

    with bd.BuildSketch(bd.Plane.XY.offset(DIV_W_Z_MIN - 0.60)) as sk_light_w:
        with bd.Locations([(46.50, -86.00)]):
            bd.RectangleRounded(18.00, 52.00, 6.00)
    light_w_desk = transform_asm_to_box_desk(
        bd.extrude(sk_light_w.sketch, amount=(DIV_W_Z_MAX - DIV_W_Z_MIN) + 1.20).solids()[0]
    )
    light_e_desk = flip_shape_upside_down_desk(light_w_desk)

    body = outer_shell - lower_cav_desk - upper_cav_desk - tb_slot_w_desk - tb_slot_e_desk - light_w_desk - light_e_desk

    with bd.BuildSketch(bd.Plane.XY.offset(-2.00)) as sk_finger_bot:
        with bd.Locations([(FINGER_CX_DESK, 0.5 * (FINGER_Y_MIN + (Y_MOUTH + 10.0)))]):
            bd.RectangleRounded(FINGER_W_DESK, (Y_MOUTH + 10.0) - FINGER_Y_MIN, 8.00)
    finger_bot = bd.extrude(sk_finger_bot.sketch, amount=5.00).solids()[0]
    finger_top = flip_shape_upside_down_desk(finger_bot)
    body = body - finger_bot - finger_top

    w_slot = bd.Box(
        12.00,
        (Y_MOUTH + 5.0) - (-95.5000),
        30.5500 - 20.9000,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((0.00, -95.5000, 20.9000)))
    w_slot_edges = w_slot.edges().filter_by(
        lambda e: abs(e.bounding_box().size.X - 12.00) < 0.1 and e.bounding_box().min.Y < -95.40
    )
    assert len(w_slot_edges) == 2
    w_slot = bd.fillet(w_slot_edges, radius=2.50)
    e_slot = flip_shape_upside_down_desk(w_slot)

    j1_cx_desk, j1_cz_desk = asm_xz_to_desk(DX_LEFT - HOST_USBC_CX_R, H_SEP - USBC_CENTER_Z_R)
    p_south_moat = bd.Plane(origin=(j1_cx_desk, Y_MOAT_SOUTH, j1_cz_desk), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
    s_moat_1 = bd.extrude(p_south_moat * bd.RectangleRounded(17.60, 11.60, 2.50), amount=6.50).solids()[0]
    s_moat_2 = flip_shape_upside_down_desk(s_moat_1)

    body = body - w_slot - e_slot - s_moat_1 - s_moat_2

    det_arm_w, det_cut_w, det_arm_e, det_cut_e = build_entrance_detents_desk()
    sock_w, sock_e, prong_w, prong_e = build_hidden_lid_snap_sockets_and_prongs_desk()
    body = body - det_cut_w - det_cut_e + det_arm_w + det_arm_e - sock_w - sock_e

    box_solids = body.solids()
    assert len(box_solids) == 1, f"Expected single solid for Carrying_Box, got {len(box_solids)}"
    box_solid = box_solids[0]
    box_solid.label = "Carrying_Box"

    lid_cap_len = Y_LID_OUT - Y_LID_IN  # 6.5000 mm
    lid_plate = bd.Box(
        W_BOX,
        lid_cap_len,
        H_BOX,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((X_BOX_WEST, Y_LID_IN, 0.0)))
    lid_y_edges = lid_plate.edges().filter_by(lambda e: abs(e.bounding_box().size.Y - lid_cap_len) < 0.1)
    assert len(lid_y_edges) == 4
    lid_plate = bd.fillet(lid_y_edges, radius=2.00)

    y_flute_c = 0.5 * (Y_LID_IN + Y_LID_OUT)
    with bd.BuildSketch(bd.Plane.XY.offset(Z_MID_DESK - 15.0000)) as sk_flute_w:
        with bd.Locations([(X_BOX_WEST - 1.6000, y_flute_c)]):
            bd.Circle(2.8000)
    flute_w = bd.extrude(sk_flute_w.sketch, amount=30.0000).solids()[0]
    flute_e = flip_shape_upside_down_desk(flute_w)
    lid_plate = lid_plate - flute_w - flute_e

    plug_gap = 0.3500
    tx_min = FINGER_X_MIN_DESK + plug_gap
    tx_max = FINGER_X_MAX_DESK - plug_gap
    plug_y_min = FINGER_Y_MIN + plug_gap
    plug_r = 8.0000 - plug_gap
    plug_h = D_OUT_PERP - (D_WELL_PERP + 0.25)

    with bd.BuildSketch(bd.Plane.XY.offset(0.0)) as sk_bot_plug:
        with bd.Locations([(FINGER_CX_DESK, 0.5 * (plug_y_min + (Y_LID_OUT + 15.0)))]):
            bd.RectangleRounded(tx_max - tx_min, (Y_LID_OUT + 15.0) - plug_y_min, plug_r)
    plug_full_bot = bd.extrude(sk_bot_plug.sketch, amount=plug_h)
    y_clip = bd.Box(
        W_BOX,
        Y_LID_OUT - (plug_y_min - 1.0),
        H_BOX + 2.0,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((X_BOX_WEST, plug_y_min - 1.0, -1.0)))
    bot_plug = (plug_full_bot & y_clip).solids()[0]
    top_plug = flip_shape_upside_down_desk(bot_plug)

    lid_body = lid_plate + bot_plug + top_plug + prong_w + prong_e

    rj1_cx_desk, rj1_cz_desk = asm_xz_to_desk(HOST_USBC_CX_R, USBC_CENTER_Z_R)
    p_lid_moat = bd.Plane(origin=(rj1_cx_desk, Y_LID_IN - 2.0, rj1_cz_desk), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
    lid_moat_1 = bd.extrude(
        p_lid_moat * bd.RectangleRounded(18.00, 12.00, 2.50),
        amount=(Y_LID_MOAT - (Y_LID_IN - 2.0)),
    ).solids()[0]
    lid_moat_2 = flip_shape_upside_down_desk(lid_moat_1)
    lid_body = lid_body - lid_moat_1 - lid_moat_2

    lid_solids = lid_body.solids()
    assert len(lid_solids) == 1, f"Expected single solid for Carrying_Box_Lid, got {len(lid_solids)}"
    lid_solid = lid_solids[0]
    lid_solid.label = "Carrying_Box_Lid"

    return box_solid, lid_solid


def verify_cuboid_sealed_ends_and_exact_symmetry(box_desk: bd.Solid, lid_desk: bd.Solid) -> None:
    """Asserts 90-deg cuboid, 100% hole-free South & North exterior walls, AND exact `Rot_Y(180 deg)` symmetry!"""
    has_west = has_east = has_bot = has_top = has_sealed_south = False
    expected_end_area = W_BOX * H_BOX - 4.0 * (4.0 - math.pi)
    for f in box_desk.faces():
        fb = f.bounding_box()
        if fb.size.X < 1e-4 and abs(fb.min.X - X_BOX_WEST) < 1e-3 and fb.size.Y > 50.0 and fb.size.Z > 20.0:
            has_west = True
        if fb.size.X < 1e-4 and abs(fb.max.X - X_BOX_EAST) < 1e-3 and fb.size.Y > 50.0 and fb.size.Z > 20.0:
            has_east = True
        if fb.size.Z < 1e-4 and abs(fb.min.Z - 0.0) < 1e-3 and fb.size.X > 100.0 and fb.size.Y > 80.0:
            has_bot = True
        if fb.size.Z < 1e-4 and abs(fb.max.Z - H_BOX) < 1e-3 and fb.size.X > 100.0 and fb.size.Y > 80.0:
            has_top = True
        if fb.size.Y < 1e-4 and abs(fb.min.Y - Y_OUT_SOUTH) < 1e-3:
            assert abs(f.area - expected_end_area) < 0.5, (
                f"South back wall is NOT hole-free! area={f.area:.2f} != {expected_end_area:.2f}"
            )
            has_sealed_south = True
    assert has_west and has_east and has_bot and has_top and has_sealed_south

    has_sealed_lid_front = False
    for f in lid_desk.faces():
        fb = f.bounding_box()
        if fb.size.Y < 1e-4 and abs(fb.max.Y - Y_LID_OUT) < 1e-3:
            assert abs(f.area - expected_end_area) < 0.5, (
                f"North Lid front wall is NOT hole-free! area={f.area:.2f} != {expected_end_area:.2f}"
            )
            has_sealed_lid_front = True
    assert has_sealed_lid_front

    box_flipped = flip_shape_upside_down_desk(box_desk)
    lid_flipped = flip_shape_upside_down_desk(lid_desk)
    diff_box = abs(box_desk.volume - overlap_volume(box_desk, box_flipped))
    diff_lid = abs(lid_desk.volume - overlap_volume(lid_desk, lid_flipped))
    print(
        f"[symmetry-check] Rot_Y(180 deg) B-rep self-symmetry volume residual: "
        f"Box = {diff_box:.6f} mm^3, Lid = {diff_lid:.6f} mm^3"
    )
    assert diff_box < 1e-2, f"Carrying_Box is NOT Rot_Y(180 deg) symmetric (residual={diff_box:.4f} mm^3)!"
    assert diff_lid < 1e-2, f"Carrying_Box_Lid is NOT Rot_Y(180 deg) symmetric (residual={diff_lid:.4f} mm^3)!"


def verify_jlc3dp_part(print_solid: bd.Solid, tag: str) -> None:
    """Full JLC3DP MJF/SLS PA12 preflight & `< 0.80 mm` zero-violation check (0 exclusions)."""
    assert print_solid.is_valid and is_sound(print_solid), f"[{tag}] Solid is not watertight/manifold!"
    assert len(print_solid.solids()) == 1 and print_solid.volume > 0, f"[{tag}] Must be 1 positive-volume solid!"

    bb = print_solid.bounding_box()
    sx, sy, sz = bb.size.X, bb.size.Y, bb.size.Z
    assert abs(bb.min.Z - 0.0) < 1e-4, f"[{tag}] Print base min.Z={bb.min.Z:.5f} != 0.0000 mm!"
    assert 5.0 <= sx <= 380.0 and 5.0 <= sy <= 284.0 and 2.0 <= sz <= 380.0, (
        f"[{tag}] Bounding box {sx:.2f}x{sy:.2f}x{sz:.2f} mm outside JLC3DP limits!"
    )

    faces = print_solid.faces()
    min_concave_diam = float("inf")
    for f in faces:
        surf = BRepAdaptor_Surface(f.wrapped)
        if surf.GetType() == GeomAbs_Cylinder and f.wrapped.Orientation() == TopAbs_REVERSED:
            diam = round(2.0 * surf.Cylinder().Radius(), 4)
            if diam < min_concave_diam:
                min_concave_diam = diam
    if min_concave_diam < float("inf"):
        assert min_concave_diam >= 1.50, (
            f"[{tag}] Concave hole/fillet diameter {min_concave_diam:.3f} mm < JLC3DP 1.50 mm limit!"
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
        f"[{tag}] JLC3DP preflight & <0.80mm check: "
        f"bbox={sx:.2f}x{sy:.2f}x{sz:.2f}mm, volume={print_solid.volume / 1000.0:.2f}cm^3, "
        f"min_concave_diam={min_concave_diam:.2f}mm (>=1.50mm), "
        f"{len(violations)} <0.80mm violations (0 exclusions)"
    )
    if violations:
        for d, (mx, my, mz), i, j in violations[:15]:
            print(f"  VIOLATION [{tag}]: d={d:.4f} mm at ({mx:.2f}, {my:.2f}, {mz:.2f}) [F{i}-F{j}]")
    assert len(violations) == 0, f"[{tag}] Found {len(violations)} <0.80mm wall/gap violations!"


def verify_carrying_box_both_orientations(
    box_desk: bd.Solid,
    lid_desk: bd.Solid,
    right_solids_desk: list[bd.Solid],
    left_solids_desk: list[bd.Solid],
    right_feet_desk: list[bd.Solid],
    left_feet_desk: list[bd.Solid],
    right_cio_desk: list[bd.Solid],
    left_cio_desk: list[bd.Solid],
    ball_desk: bd.Solid,
    wheel_desk: bd.Solid,
    keycaps_desk: list[bd.Solid],
) -> None:
    """
    Verifies ZERO overlap across all 690 solids, full `+Y -> -Y` slide-in trajectory, surface clearances,
    AND 6-DOF lock in BOTH Pose A (Right Trackball on Bottom) AND Pose B (Right Trackball Flipped to Top)!
    """
    ov_box_lid = overlap_volume(box_desk, lid_desk)
    assert ov_box_lid == 0.0, f"B-rep interference between Box & Lid: {ov_box_lid:.8f} mm^3!"

    for pose_name, flip in (
        ("Pose_A_Trackball_Bottom", False),
        ("Pose_B_Trackball_Top_Flipped", True),
    ):
        fn = flip_shape_upside_down_desk if flip else (lambda s: s)
        r_sols = [fn(s) for s in right_solids_desk]
        l_sols = [fn(s) for s in left_solids_desk]
        r_feet = [fn(s) for s in right_feet_desk]
        l_feet = [fn(s) for s in left_feet_desk]
        r_cio = [fn(s) for s in right_cio_desk]
        l_cio = [fn(s) for s in left_cio_desk]
        b_sol = fn(ball_desk)
        w_sol = fn(wheel_desk)
        k_sols = [fn(s) for s in keycaps_desk]

        box_bb = box_desk.bounding_box()
        lid_bb = lid_desk.bounding_box()
        all_parts = r_sols + r_feet + r_cio + l_sols + l_feet + l_cio

        max_ov_box = 0.0
        max_ov_lid = 0.0
        for s in all_parts:
            sb = s.bounding_box()
            if _aabb_intersects(box_bb, sb):
                ov = overlap_volume(box_desk, s)
                if ov > max_ov_box:
                    max_ov_box = ov
            if _aabb_intersects(lid_bb, sb):
                ovl = overlap_volume(lid_desk, s)
                if ovl > max_ov_lid:
                    max_ov_lid = ovl

        print(
            f"[{pose_name}] Overlap ({len(all_parts)} solids + Box + Lid): "
            f"Box_vs_All={max_ov_box:.8f} mm^3, Lid_vs_All={max_ov_lid:.8f} mm^3"
        )
        assert max_ov_box == 0.0, f"[{pose_name}] Box overlap {max_ov_box:.8f} mm^3!"
        assert max_ov_lid == 0.0, f"[{pose_name}] Lid overlap {max_ov_lid:.8f} mm^3!"

        slide_solids = r_feet + l_feet + r_cio + l_cio + [b_sol, w_sol] + k_sols
        for dy in (10.0, 30.0, 60.0, 90.0):
            loc_y = bd.Location((0.0, dy, 0.0)).wrapped
            for s in slide_solids:
                ms = bd.Solid(s.wrapped.Moved(loc_y))
                if _aabb_intersects(box_bb, ms.bounding_box()):
                    assert overlap_volume(box_desk, ms) == 0.0, f"[{pose_name}] Slide collision at dy=+{dy} mm!"

        all_cio = r_cio + l_cio
        clr_feet = min_surface_clearance(r_feet + l_feet, box_desk)
        clr_ball = min_surface_clearance([b_sol], box_desk)
        clr_wheel = min_surface_clearance([w_sol], box_desk)
        clr_keycaps = min_surface_clearance(k_sols, box_desk)
        clr_cio_box = min_surface_clearance(all_cio, box_desk)
        clr_cio_lid = min_surface_clearance(all_cio, lid_desk)

        print(
            f"[{pose_name}] Clearances: feet={clr_feet:.3f}mm, ball={clr_ball:.3f}mm, "
            f"wheel={clr_wheel:.3f}mm, keys={clr_keycaps:.3f}mm, "
            f"cio_box={clr_cio_box:.3f}mm, cio_lid={clr_cio_lid:.3f}mm"
        )
        assert clr_feet >= 0.50
        assert 0.50 <= clr_ball <= 0.70
        assert clr_wheel >= 1.50
        assert clr_keycaps >= 0.75
        assert clr_cio_box >= 0.90
        assert clr_cio_lid >= 2.00

        r_case = max(r_sols, key=lambda s: s.volume)
        l_case = max(l_sols, key=lambda s: s.volume)
        l_j1_tip = [t for t in l_cio if "Host" in getattr(t, "label", "")][0]
        test_dirs = [
            ("+X", (0.65, 0.0, 0.0)),
            ("-X", (-0.65, 0.0, 0.0)),
            ("+Y_Mouth_Detent", (0.0, 0.75, 0.0)),
            ("-Y_Backstop_Shoulder", (0.0, -0.65, 0.0)),
            ("+Z", (0.0, 0.0, 0.55)),
            ("-Z", (0.0, 0.0, -0.55)),
        ]
        for name, target_case in (("Right_Case", r_case), ("Left_Case", l_case)):
            for d_tag, vec in test_dirs:
                shifted = bd.Solid(target_case.wrapped.Moved(bd.Location(vec).wrapped))
                assert overlap_volume(box_desk, shifted) > 0.02, f"[{pose_name}] {name} NOT locked in {d_tag}!"
        j1_pushed = bd.Solid(l_j1_tip.wrapped.Moved(bd.Location((0.0, -0.65, 0.0)).wrapped))
        assert overlap_volume(box_desk, j1_pushed) == 0.0, f"[{pose_name}] J1 tip touched moat floor!"

        lift_sgn = -1.0 if flip else 1.0
        ball_lifted = bd.Solid(
            b_sol.wrapped.Moved(bd.Location((lift_sgn * (-SIN_TENT * 1.0), 0.0, lift_sgn * (COS_TENT * 1.0))).wrapped)
        )
        assert overlap_volume(box_desk, ball_lifted) > 0.40, f"[{pose_name}] Trackball Keeper failed!"

    lid_dirs = [
        ("+X", (0.65, 0.0, 0.0)),
        ("-X", (-0.65, 0.0, 0.0)),
        ("+Y_Snap_Prongs", (0.0, 0.75, 0.0)),
        ("-Y_Mouth_Rim", (0.0, -0.35, 0.0)),
        ("+Z", (0.0, 0.0, 0.65)),
        ("-Z", (0.0, 0.0, -0.65)),
    ]
    for lid_tag, l_test in (("Lid_Normal", lid_desk), ("Lid_UpsideDown", flip_shape_upside_down_desk(lid_desk))):
        assert overlap_volume(box_desk, l_test) == 0.0
        for d_tag, vec in lid_dirs:
            lid_shifted = bd.Solid(l_test.wrapped.Moved(bd.Location(vec).wrapped))
            ov_lid_lock = overlap_volume(box_desk, lid_shifted)
            assert ov_lid_lock > 0.02, f"[6-DOF FAIL] {lid_tag} NOT locked in {d_tag} (ov={ov_lid_lock:.5f})!"

    print("[carrying-box-assembly] ALL CHECKS PASS IN BOTH NORMAL & UPSIDE-DOWN ORIENTATIONS (Box + Lid + Keyboards)!")


def main() -> None:
    print("=== Building curcur40 Official Carrying Box & Calculated Snap Lid ===")
    CASES_DIR.mkdir(parents=True, exist_ok=True)
    ASSEMBLIES_DIR.mkdir(parents=True, exist_ok=True)

    verify_lid_snap_mechanics()

    box_desk, lid_desk = build_carrying_box_and_lid_desk()
    verify_cuboid_sealed_ends_and_exact_symmetry(box_desk, lid_desk)

    bb_box = box_desk.bounding_box()
    box_print = box_desk.moved(bd.Location((0.0, 0.0, -bb_box.min.Z)))
    box_print.label = "curcur40_carrying_box"

    lid_flat = lid_desk.rotate(bd.Axis.X, -90.0)
    bb_lid = lid_flat.bounding_box()
    lid_print = lid_flat.moved(bd.Location((0.0, 0.0, -bb_lid.min.Z)))
    lid_print.label = "curcur40_carrying_box_lid"

    verify_jlc3dp_part(box_print, "carrying-box")
    verify_jlc3dp_part(lid_print, "carrying-box-lid")

    bd.export_step(box_print, str(CASES_DIR / "carrying-box.step"))
    bd.export_stl(box_print, str(CASES_DIR / "carrying-box.stl"))
    bd.export_step(lid_print, str(CASES_DIR / "carrying-box-lid.step"))
    bd.export_stl(lid_print, str(CASES_DIR / "carrying-box-lid.stl"))
    print("Exported reversible carrying-box.step/.stl & carrying-box-lid.step/.stl")

    full_asm_path = ASSEMBLIES_DIR / "assembly-full.step"
    print(f"Loading synchronized full keyboard solids from {full_asm_path.name}...")
    full_imported = bd.import_step(str(full_asm_path))
    all_solids = full_imported.solids()
    right_asm = [s for s in all_solids if s.bounding_box().center().X > 0.0]
    left_asm = [transform_left_to_packed(s) for s in all_solids if s.bounding_box().center().X < 0.0]

    ball_asm = [
        s for s in right_asm if abs(s.bounding_box().size.X - 25.0) < 0.2 and abs(s.bounding_box().max.Z - 14.80) < 0.2
    ][0]
    wheel_asm = [
        s for s in right_asm if 3.90 < s.bounding_box().max.Z < 4.30 and s.bounding_box().size.Y > 21.5
    ][0]
    r_keys_asm = [
        s for s in right_asm if abs(s.bounding_box().max.Z - 3.60) < 0.15 and 17.5 < s.bounding_box().size.X < 18.5
    ]
    l_keys_asm = [
        s for s in left_asm
        if abs(s.bounding_box().min.Z - (H_SEP - 3.60)) < 0.15 and 17.5 < s.bounding_box().size.X < 18.5
    ]

    right_solids_desk = [transform_asm_to_box_desk(s) for s in right_asm]
    left_solids_desk = [transform_asm_to_box_desk(s) for s in left_asm]
    right_feet_desk = [transform_asm_to_box_desk(f) for f in build_rubber_feet_in_case_pose(is_right=True)]
    left_feet_desk = [
        transform_asm_to_box_desk(transform_left_to_packed(f))
        for f in build_rubber_feet_in_case_pose(is_right=False)
    ]
    right_cio_desk = [transform_asm_to_box_desk(t) for t in build_cio_magnetic_tips_in_case_pose(is_right=True)]
    left_cio_desk = [
        transform_asm_to_box_desk(transform_left_to_packed(t))
        for t in build_cio_magnetic_tips_in_case_pose(is_right=False)
    ]
    ball_desk = transform_asm_to_box_desk(ball_asm)
    wheel_desk = transform_asm_to_box_desk(wheel_asm)
    keycaps_desk = [transform_asm_to_box_desk(k) for k in (r_keys_asm + l_keys_asm)]

    verify_carrying_box_both_orientations(
        box_desk,
        lid_desk,
        right_solids_desk,
        left_solids_desk,
        right_feet_desk,
        left_feet_desk,
        right_cio_desk,
        left_cio_desk,
        ball_desk,
        wheel_desk,
        keycaps_desk,
    )

    right_grp = bd.Compound(children=right_solids_desk + right_feet_desk + right_cio_desk)
    right_grp.label = "Right_Keyboard_With_Feet_And_CIO_Tips"
    left_grp = bd.Compound(children=left_solids_desk + left_feet_desk + left_cio_desk)
    left_grp.label = "Left_Keyboard_Packed_With_Feet_And_CIO_Tips"

    asm_lidless = bd.Compound(children=[box_desk, right_grp, left_grp])
    asm_lidless.label = "curcur40_carrying_box_assembly"
    bb_open = asm_lidless.bounding_box()
    print(
        f"Lid-Removed Inspection Envelope: "
        f"{bb_open.size.X:.2f} x {bb_open.size.Y:.2f} x {bb_open.size.Z:.2f} mm "
        f"(Z = [{bb_open.min.Z:.4f}, {bb_open.max.Z:.4f}] mm)"
    )
    bd.export_step(asm_lidless, str(ASSEMBLIES_DIR / "carrying-box-assembly.step"))
    assert len(bd.import_step(str(ASSEMBLIES_DIR / "carrying-box-assembly.step")).solids()) == 689

    asm_with_lid = bd.Compound(children=[box_desk, lid_desk, right_grp, left_grp])
    asm_with_lid.label = "curcur40_carrying_box_with_lid_assembly"
    bb_closed = asm_with_lid.bounding_box()
    print(
        f"Official Carrying Box (With Snap Lid) Closed Envelope: "
        f"{bb_closed.size.X:.2f} x {bb_closed.size.Y:.2f} x {bb_closed.size.Z:.2f} mm "
        f"(Z = [{bb_closed.min.Z:.4f}, {bb_closed.max.Z:.4f}] mm)"
    )
    bd.export_step(asm_with_lid, str(ASSEMBLIES_DIR / "carrying-box-with-lid-assembly.step"))
    assert len(bd.import_step(str(ASSEMBLIES_DIR / "carrying-box-with-lid-assembly.step")).solids()) == 690
    print("Exported carrying-box-with-lid-assembly.step (690 solids) & carrying-box-assembly.step (689 solids)!")


if __name__ == "__main__":
    main()
