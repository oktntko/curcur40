# -*- coding: utf-8 -*-
"""
Generate curcur40 Concept B: Orthogonal Rectangular Slide-In 5-Sided Carrying Box
(`cases/carrying-box.step`, `cases/carrying-box.stl`), Optional Flush Cap Lid
(`cases/carrying-box-lid.step`, `cases/carrying-box-lid.stl`), and Full Packed Verification
Assemblies (`cases/assemblies/carrying-box-assembly.step`, `carrying-box-with-lid-assembly.step`).

Design Highlights (Concept B-1 — Orthogonal 90-deg Rectangular Cuboid Slide-In Box):
1. True 90.000-deg Orthogonal Rectangular Cuboid Exterior (`142.40 x 100.65 x 65.42 mm`):
   - Top & Bottom outer faces are horizontal (`Z = 0.00 mm` & `Z = 65.42 mm`), West & East outer walls are
     strictly vertical (`90.000 deg`, `X = 3.36 mm` & `145.76 mm`), and North/South planes are strictly vertical
     (`90.000 deg`, `Y = -28.50 mm` & `-129.15 mm`) — zero trapezoidal/parallelogram lean!
   - All 4 `CIO-SLMG-T-C` magnetic USB-C tips sit protected WITHIN the `142.40 mm` side width (`>= 1.08 mm`
     recessed inside the West/East vertical walls) while remaining 100% open & unobstructed via horizontal
     side slide slots (`rJ2`, `J2`), a horizontal South back window (`J1`), and the open North mouth (`rJ1`).
2. Zero-Friction Floating Rubber-Foot Wells & Custom C-Channel Rails:
   - Internal rails match the 7.473-deg keyboard rims (`0.20 mm` Z gap, `0.30 mm` X gap) while recessing the
     interior floor & ceiling wells by `2.75 mm`, floating all 10 rubber feet in mid-air (`0.750 mm` clearance).
   - Central `2.25 mm` divider web integrates a `15.60 mm` wide non-contact Trackball Keeper U-slot (`0.580 mm` gap).
3. Clean Exterior Lidless Retention (Mode B-1) + Zero-Mark Optional Cap Lid (Mode B-2):
   - Built-in PA12 entrance click-detent spring catches lock both keyboards in all 6 DOFs WITHOUT a lid,
     with zero unused clasp pockets on the exterior side walls.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path
from cadgen import build123d as bd
from cadgen.geometry import is_sound, overlap_volume
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.GeomAbs import GeomAbs_Cylinder
from OCP.TopAbs import TopAbs_REVERSED

WORKSPACE = Path(__file__).resolve().parent.parent
if str(WORKSPACE / "scripts") not in sys.path:
    sys.path.insert(0, str(WORKSPACE / "scripts"))

from generate_carrying_case import (
    ASSEMBLIES_DIR,
    CASES_DIR,
    DX_LEFT,
    H_SEP,
    HOST_USBC_CX_R,
    TAN_TENT,
    TB_CX,
    TB_CY,
    THETA_TENT_DEG,
    THETA_TENT_RAD,
    USBC_CENTER_Z_R,
    X_PINKY_OUTER,
    X_THUMB_OUTER,
    Y_SOUTH_OUTER,
    Z_PINKY_BOTTOM,
    Z_THUMB_BOTTOM,
    _aabb_intersects,
    build_cio_magnetic_tips_in_case_pose,
    build_rubber_feet_in_case_pose,
    min_surface_clearance,
    transform_left_to_packed,
    z_case_bottom_right,
)

# Internal slide clearances (in `asm` frame)
XY_SLIDE_GAP = 0.3000                 # >= 0.30 mm JLC3DP moving clearance
Z_SLIDE_GAP = 0.2000                  # 0.20 mm vertical rail clearance
BOX_WALL = 2.2000                     # 2.20 mm nominal back/cap wall thickness

X_IN_WEST = X_THUMB_OUTER - XY_SLIDE_GAP     # 6.7250 mm
X_IN_EAST = X_PINKY_OUTER + XY_SLIDE_GAP     # 136.1580 mm
Y_IN_SOUTH = Y_SOUTH_OUTER - XY_SLIDE_GAP    # -126.9500 mm
Y_OUT_SOUTH = Y_IN_SOUTH - BOX_WALL          # -129.1500 mm
Y_MOUTH = -28.5000                           # Depth = 100.6500 mm

# Perpendicular offsets from bare angled case bottoms (horizontal Z planes in `box_desk`!)
COS_TENT = math.cos(THETA_TENT_RAD)
SIN_TENT = math.sin(THETA_TENT_RAD)
D_RUNNER_PERP = Z_SLIDE_GAP                  # 0.20 mm perpendicular gap under bare outer case corners
D_WELL_PERP = 2.7500                         # 2.75 mm recessed floor/ceiling well (0.75 mm clear of 2.0 mm feet!)
D_OUT_PERP = 4.7500                          # 4.75 mm outer box face (2.00 mm solid horizontal top & bottom walls!)

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
X_BOX_WEST = X_MID_DESK - 0.5 * W_BOX                                          #  3.35712 mm (vertical 90-deg West wall)
X_BOX_EAST = X_MID_DESK + 0.5 * W_BOX                                          # 145.75712 mm (vertical 90-deg East wall)

# Central divider web & Trackball Keeper U-slot (`Z_asm in [12.80, 15.05] mm`)
DIV_Z_MIN = 12.8000
DIV_Z_MAX = 15.0500
TB_SLOT_R = 7.8000                           # 15.60 mm wide U-slot (0.58 mm radial gap to 25mm ball)

# Finger pull cutout in `box_desk` (`X_desk in [66.00, 102.00]`, clear of all 10 rubber feet by >= 2.84 mm!)
FINGER_X_MIN_DESK = 66.0000
FINGER_X_MAX_DESK = 102.0000
FINGER_CX_DESK = 0.5 * (FINGER_X_MIN_DESK + FINGER_X_MAX_DESK)   # 84.0000 mm
FINGER_W_DESK = FINGER_X_MAX_DESK - FINGER_X_MIN_DESK            # 36.0000 mm
FINGER_Y_MIN = -44.5000                                          # 16.00 mm deep scoop from Y_MOUTH = -28.50 mm


def z_bot_plane(x: float, d_perp: float) -> float:
    """Z on plane parallel to Right's outer bottom shifted downward by perpendicular distance `d_perp`."""
    return z_case_bottom_right(x) - d_perp / COS_TENT


def z_top_plane(x: float, d_perp: float) -> float:
    """Z on plane parallel to Packed Left's outer top shifted upward by perpendicular distance `d_perp`."""
    z_left_bare = (H_SEP - Z_PINKY_BOTTOM) + (x - X_THUMB_OUTER) * TAN_TENT
    return z_left_bare + d_perp / COS_TENT


def asm_xz_to_desk(x_asm: float, z_asm: float) -> tuple[float, float]:
    """Exact `(X_desk, Z_desk)` coordinates of an `(x_asm, z_asm)` point."""
    dx = x_asm - X_PINKY_OUTER
    dz = z_asm - Z_PINKY_BOTTOM
    return (
        X_PINKY_OUTER + dx * COS_TENT + dz * SIN_TENT,
        D_OUT_PERP + dz * COS_TENT - dx * SIN_TENT,
    )


def transform_asm_to_box_desk(shape: bd.Shape) -> bd.Shape:
    """
    Rotate by `+THETA_TENT_DEG` (+7.473 deg) around Y and shift Z so `Carrying_Box` outer bottom
    rests flat on `Z = 0.0000 mm` (and outer top is flat horizontal at `Z = +65.4210 mm`).
    """
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


def build_entrance_detents_desk() -> tuple[bd.Solid, bd.Solid, bd.Solid, bd.Solid]:
    """
    Builds orthogonal West (Right keyboard) & East (Packed Left keyboard) entrance click-detent
    spring arms and relief-slot cutters directly in `box_desk` coordinates:
      - Outer arm faces lie strictly on the vertical 90-deg box walls (`X_BOX_WEST`, `X_BOX_EAST`).
      - Top & bottom arm/slot faces are strictly horizontal (`Z_desk = const`).
      - Inner catch nose matches the 7.473-deg keyboard thumb wall (`0.22 mm` uniform rest gap, +1.00 mm lock).
    """
    z_bot_slot = 7.4000
    z_arm_bot = 9.4000
    z_arm_top = 16.9000
    z_top_slot = 18.9000
    y_slot_root_straight = -50.5000  # Filleted by R=1.00 -> root at Y = -51.50 mm (~4.5 N gentle snap!)

    # Orthogonal West slot cutter (`Z_desk in [7.40, 18.90]`, `Y in [-51.50, Y_MOUTH + 2.0]`)
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
    assert len(root_edges) == 2, f"Expected 2 root edges on West detent cutter, got {len(root_edges)}"
    cut_w = bd.fillet(root_edges, radius=1.00)

    # Inner catch nose profile in `asm` (tangent-cleared 0.22 mm behind Right's R=2.00 NW corner),
    # transformed to `box_desk` and trimmed flush to `X_BOX_WEST` & horizontal `Z_desk in [9.40, 16.90]`!
    xy_pts_asm = [
        (-5.0000, -51.8000),
        (X_IN_WEST, -51.8000),    # Coplanar with lower_cav West inner wall -> zero root step!
        (X_IN_WEST, -32.0000),    # 0.22 mm clear behind R=2.00 NW corner arc
        (8.0250, -30.7000),       # 45-deg exit ramp -> +1.00 mm positive catch behind X_THUMB_OUTER (7.0250)
        (8.0250, -29.8000),       # 0.90 mm flat detent crest (>= 0.80 mm)
        (6.5250, Y_MOUTH),        # 41-deg entry cam funnel (< 7.0250 so pushing keyboard in self-cams open)
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

    # Exact 180-deg Y-axis symmetry `(X, Y, Z) -> (2*X_MID_DESK - X, Y, H_BOX - Z)` for East (Packed Left)
    loc_sym = bd.Pos(2.0 * X_MID_DESK, 0.0, H_BOX) * bd.Rot(0.0, 180.0, 0.0)
    arm_e = bd.Solid(arm_w.wrapped.Moved(loc_sym.wrapped))
    cut_e = bd.Solid(cut_w.wrapped.Moved(loc_sym.wrapped))
    return arm_w, cut_w, arm_e, cut_e


def build_carrying_box_and_lid_desk() -> tuple[bd.Solid, bd.Solid]:
    """
    Builds both `Carrying_Box` (Concept B-1 lidless orthogonal rectangular cuboid) and
    `Carrying_Box_Lid` (Concept B-2 optional flush cap lid) directly in `box_desk` coordinates
    (`Z in [0.0000, 65.4210] mm`, all 6 outer faces mutually perpendicular at exact `90.000 deg`).
    """
    # 1. Pure 90.000-deg Orthogonal Rectangular Cuboid Outer Shell (`142.40 x 100.65 x 65.42 mm`)
    outer_shell = bd.Box(
        W_BOX,
        Y_MOUTH - Y_OUT_SOUTH,
        H_BOX,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((X_BOX_WEST, Y_OUT_SOUTH, 0.0)))
    long_y_edges = outer_shell.edges().filter_by(
        lambda e: abs(e.bounding_box().size.Y - (Y_MOUTH - Y_OUT_SOUTH)) < 0.2
    )
    assert len(long_y_edges) == 4, f"Expected 4 longitudinal Y-edges, got {len(long_y_edges)}"
    outer_shell = bd.fillet(long_y_edges, radius=2.00)

    # 2. Internal C-Channel Cavities & Central Divider Web (built in `asm` and transformed to `box_desk`)
    x_rim_w = 8.5250
    x_rim_e = 134.3580
    x_well_w = 8.8250
    x_well_e = 134.0580

    lower_cav_xz = [
        (X_IN_WEST, z_bot_plane(X_IN_WEST, D_RUNNER_PERP)),
        (x_well_w, z_bot_plane(x_well_w, D_RUNNER_PERP)),
        (x_well_w, z_bot_plane(x_well_w, D_WELL_PERP)),
        (x_well_e, z_bot_plane(x_well_e, D_WELL_PERP)),
        (x_well_e, z_bot_plane(x_well_e, D_RUNNER_PERP)),
        (X_IN_EAST, z_bot_plane(X_IN_EAST, D_RUNNER_PERP)),
        (X_IN_EAST, Z_SLIDE_GAP),
        (x_rim_e, Z_SLIDE_GAP),
        (x_rim_e, DIV_Z_MIN),
        (x_rim_w, DIV_Z_MIN),
        (x_rim_w, Z_SLIDE_GAP),
        (X_IN_WEST, Z_SLIDE_GAP),
    ]
    lower_cav_desk = transform_asm_to_box_desk(extrude_xz_profile_along_y(lower_cav_xz, Y_IN_SOUTH, Y_MOUTH + 5.0))

    z_upper_rim = H_SEP - Z_SLIDE_GAP
    upper_cav_xz = [
        (X_IN_WEST, z_upper_rim),
        (x_rim_w, z_upper_rim),
        (x_rim_w, DIV_Z_MAX),
        (x_rim_e, DIV_Z_MAX),
        (x_rim_e, z_upper_rim),
        (X_IN_EAST, z_upper_rim),
        (X_IN_EAST, z_top_plane(X_IN_EAST, D_RUNNER_PERP)),
        (x_well_e, z_top_plane(x_well_e, D_RUNNER_PERP)),
        (x_well_e, z_top_plane(x_well_e, D_WELL_PERP)),
        (x_well_w, z_top_plane(x_well_w, D_WELL_PERP)),
        (x_well_w, z_top_plane(x_well_w, D_RUNNER_PERP)),
        (X_IN_WEST, z_top_plane(X_IN_WEST, D_RUNNER_PERP)),
    ]
    upper_cav_desk = transform_asm_to_box_desk(extrude_xz_profile_along_y(upper_cav_xz, Y_IN_SOUTH, Y_MOUTH + 5.0))

    # 3. Central Divider Trackball Slide & Keeper U-Slot + Lightening Windows
    with bd.BuildSketch(bd.Plane.XY.offset(DIV_Z_MIN - 0.50)) as sk_tb_slot:
        with bd.Locations([(TB_CX, TB_CY)]):
            bd.Circle(TB_SLOT_R)
        y_len = (Y_MOUTH + 5.0) - TB_CY
        with bd.Locations([(TB_CX, TB_CY + 0.5 * y_len)]):
            bd.Rectangle(2.0 * TB_SLOT_R, y_len)
    tb_slot_desk = transform_asm_to_box_desk(
        bd.extrude(sk_tb_slot.sketch, amount=(DIV_Z_MAX - DIV_Z_MIN) + 1.00).solids()[0]
    )

    with bd.BuildSketch(bd.Plane.XY.offset(DIV_Z_MIN - 0.50)) as sk_light:
        with bd.Locations([(60.00, -86.00), (106.00, -86.00)]):
            bd.RectangleRounded(34.00, 52.00, 8.00)
    light_desk = transform_asm_to_box_desk(
        bd.extrude(sk_light.sketch, amount=(DIV_Z_MAX - DIV_Z_MIN) + 1.00).solids()[0]
    )

    body = outer_shell - lower_cav_desk - upper_cav_desk - tb_slot_desk - light_desk

    # 4. Orthogonal North Finger-Pull Cutout (`X_desk in [66.00, 102.00]`, `Y in [-44.50, -28.50]`)
    with bd.BuildSketch(bd.Plane.XY.offset(-5.00)) as sk_finger:
        with bd.Locations([(FINGER_CX_DESK, 0.5 * (FINGER_Y_MIN + (Y_MOUTH + 10.0)))]):
            bd.RectangleRounded(FINGER_W_DESK, (Y_MOUTH + 10.0) - FINGER_Y_MIN, 8.00)
    finger_cutter = bd.extrude(sk_finger.sketch, amount=H_BOX + 10.00)
    body = body - finger_cutter

    # 5. Orthogonal Open Side Slots & Back Window for All 4 Permanent `CIO-SLMG-T-C` Magnetic USB-C Tips:
    #    - West Horizontal Side Slot for Right `rJ2` (`Z_desk in [20.90, 30.55]`, `Y in [-95.50, Y_MOUTH + 5.0]`)
    w_slot = bd.Box(
        12.00,
        (Y_MOUTH + 5.0) - (-95.5000),
        30.5500 - 20.9000,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((0.00, -95.5000, 20.9000)))
    w_slot_edges = w_slot.edges().filter_by(
        lambda e: abs(e.bounding_box().size.X - 12.00) < 0.1 and e.bounding_box().min.Y < -95.40
    )
    assert len(w_slot_edges) == 2, f"Expected 2 end edges on w_slot, got {len(w_slot_edges)}"
    w_slot = bd.fillet(w_slot_edges, radius=2.50)

    #    - East Horizontal Side Slot for Packed Left `J2` (`Z_desk in [34.871, 44.521]`, `Y in [-79.70, Y_MOUTH + 5.0]`)
    e_slot = bd.Box(
        12.00,
        (Y_MOUTH + 5.0) - (-79.7000),
        30.5500 - 20.9000,
        align=(bd.Align.MAX, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((X_BOX_EAST + 3.00, -79.7000, H_BOX - 30.5500)))
    e_slot_edges = e_slot.edges().filter_by(
        lambda e: abs(e.bounding_box().size.X - 12.00) < 0.1 and e.bounding_box().min.Y < -79.60
    )
    assert len(e_slot_edges) == 2, f"Expected 2 end edges on e_slot, got {len(e_slot_edges)}"
    e_slot = bd.fillet(e_slot_edges, radius=2.50)

    #    - South Back Wall Horizontal Window for Packed Left `J1` (`17.20 x 11.20 mm`, R=2.50, 0-deg horizontal!)
    j1_cx_desk, j1_cz_desk = asm_xz_to_desk(DX_LEFT - HOST_USBC_CX_R, H_SEP - USBC_CENTER_Z_R)
    p_south_win = bd.Plane(origin=(j1_cx_desk, Y_OUT_SOUTH - 1.0, j1_cz_desk), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
    s_win = bd.extrude(p_south_win * bd.RectangleRounded(17.20, 11.20, 2.50), amount=8.00)

    body = body - w_slot - e_slot - s_win

    # 6. Integrate Orthogonal Entrance Click-Detents (West for Right, East for Packed Left — zero exterior lid marks!)
    det_arm_w, det_cut_w, det_arm_e, det_cut_e = build_entrance_detents_desk()
    body = body - det_cut_w - det_cut_e + det_arm_w + det_arm_e

    box_solids = body.solids()
    assert len(box_solids) == 1, f"Expected single solid for Carrying_Box, got {len(box_solids)}"
    box_solid = box_solids[0]
    box_solid.label = "Carrying_Box"

    # =========================================================================
    # 7. Optional Rectangular Flush Cap Lid (`Carrying_Box_Lid`, `142.40 x 65.42 mm`)
    #    - Zero marks/pockets required on `Carrying_Box`: plugs cleanly into the top & bottom
    #      finger cutouts (`0.35 mm` uniform perimeter gap) with an orthogonal `rJ1` CIO window!
    # =========================================================================
    y_lid_in = Y_MOUTH + 0.1500
    y_lid_out = y_lid_in + BOX_WALL

    lid_plate = bd.Box(
        W_BOX,
        BOX_WALL,
        H_BOX,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((X_BOX_WEST, y_lid_in, 0.0)))
    lid_y_edges = lid_plate.edges().filter_by(lambda e: abs(e.bounding_box().size.Y - BOX_WALL) < 0.1)
    assert len(lid_y_edges) == 4
    lid_plate = bd.fillet(lid_y_edges, radius=2.00)

    plug_gap = 0.3500
    tx_min = FINGER_X_MIN_DESK + plug_gap
    tx_max = FINGER_X_MAX_DESK - plug_gap
    plug_y_min = FINGER_Y_MIN + plug_gap
    plug_r = 8.0000 - plug_gap
    plug_h = D_OUT_PERP - (D_WELL_PERP + 0.25)  # 1.7500 mm

    with bd.BuildSketch(bd.Plane.XY.offset(0.0)) as sk_bot_plug:
        with bd.Locations([(FINGER_CX_DESK, 0.5 * (plug_y_min + (y_lid_out + 15.0)))]):
            bd.RectangleRounded(tx_max - tx_min, (y_lid_out + 15.0) - plug_y_min, plug_r)
    plug_full_bot = bd.extrude(sk_bot_plug.sketch, amount=plug_h)
    y_clip = bd.Box(
        W_BOX,
        y_lid_out - (plug_y_min - 1.0),
        H_BOX + 2.0,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((X_BOX_WEST, plug_y_min - 1.0, -1.0)))
    bot_plug = (plug_full_bot & y_clip).solids()[0]
    top_plug = bot_plug.moved(bd.Location((0.0, 0.0, H_BOX - plug_h)))

    lid_body = lid_plate + bot_plug + top_plug

    # Orthogonal North `rJ1` `CIO-SLMG-T-C` window (`18.00 x 12.00 mm`, R=2.50)
    rj1_cx_desk, rj1_cz_desk = asm_xz_to_desk(HOST_USBC_CX_R, USBC_CENTER_Z_R)
    p_lid_usbc = bd.Plane(origin=(rj1_cx_desk, y_lid_in - 2.0, rj1_cz_desk), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
    lid_usbc_cut = bd.extrude(p_lid_usbc * bd.RectangleRounded(18.00, 12.00, 2.50), amount=10.00)
    lid_body = lid_body - lid_usbc_cut

    lid_solids = lid_body.solids()
    assert len(lid_solids) == 1, f"Expected single solid for Carrying_Box_Lid, got {len(lid_solids)}"
    lid_solid = lid_solids[0]
    lid_solid.label = "Carrying_Box_Lid"

    return box_solid, lid_solid


def verify_orthogonal_cuboid_bounds(box_desk: bd.Solid) -> None:
    """Asserts that `Carrying_Box` is a true 90-deg orthogonal rectangular cuboid (not a trapezoid/parallelogram)."""
    bb = box_desk.bounding_box()
    # Check outer planar faces on -Z, +Z, -X, +X, -Y have exact axis-aligned normals!
    has_west = False
    has_east = False
    has_bot = False
    has_top = False
    has_south = False
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
        if fb.size.Y < 1e-4 and abs(fb.min.Y - Y_OUT_SOUTH) < 1e-3 and fb.size.X > 100.0 and fb.size.Z > 50.0:
            has_south = True
    assert has_west and has_east and has_bot and has_top and has_south, (
        f"Outer cuboid orthogonality check failed: W={has_west}, E={has_east}, B={has_bot}, T={has_top}, S={has_south}"
    )
    assert abs(bb.size.X - W_BOX) < 1e-3 and abs(bb.size.Z - H_BOX) < 1e-3, "Cuboid outer size mismatch!"


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


def verify_carrying_box_assembly_desk(
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
    """Full 690-solid zero-overlap, horizontal slide trajectory, clearance, & 6-DOF verification in `box_desk`."""
    box_bb = box_desk.bounding_box()
    lid_bb = lid_desk.bounding_box()
    all_parts = (
        right_solids_desk + right_feet_desk + right_cio_desk
        + left_solids_desk + left_feet_desk + left_cio_desk
    )

    ov_box_lid = overlap_volume(box_desk, lid_desk)
    assert ov_box_lid == 0.0, f"B-rep interference between Box & Lid: {ov_box_lid:.8f} mm^3!"

    max_ov_box = 0.0
    worst_box = ""
    max_ov_lid = 0.0
    worst_lid = ""
    for idx, s in enumerate(all_parts):
        sb = s.bounding_box()
        if _aabb_intersects(box_bb, sb):
            ov = overlap_volume(box_desk, s)
            if ov > max_ov_box:
                max_ov_box = ov
                worst_box = f"{getattr(s, 'label', '') or idx} bbox={sb}"
        if _aabb_intersects(lid_bb, sb):
            ovl = overlap_volume(lid_desk, s)
            if ovl > max_ov_lid:
                max_ov_lid = ovl
                worst_lid = f"{getattr(s, 'label', '') or idx} bbox={sb}"

    print(
        f"[carrying-box-assembly] Overlap check ({len(all_parts)} solids + Box + Lid): "
        f"Box_vs_All={max_ov_box:.8f} mm^3, Lid_vs_All={max_ov_lid:.8f} mm^3, Box_vs_Lid={ov_box_lid:.8f} mm^3"
    )
    assert max_ov_box == 0.0, f"B-rep interference with Carrying_Box: {max_ov_box:.8f} mm^3 at {worst_box}!"
    assert max_ov_lid == 0.0, f"B-rep interference with Carrying_Box_Lid: {max_ov_lid:.8f} mm^3 at {worst_lid}!"

    # Horizontal `+Y -> -Y` slide trajectory verification (`dy = +10, +30, +60, +90 mm`)
    slide_check_solids = (
        right_feet_desk + left_feet_desk + right_cio_desk + left_cio_desk
        + [ball_desk, wheel_desk] + keycaps_desk
    )
    for dy in (10.0, 30.0, 60.0, 90.0):
        loc_y = bd.Location((0.0, dy, 0.0)).wrapped
        for s in slide_check_solids:
            ms = bd.Solid(s.wrapped.Moved(loc_y))
            if _aabb_intersects(box_bb, ms.bounding_box()):
                ov_s = overlap_volume(box_desk, ms)
                assert ov_s == 0.0, (
                    f"Slide trajectory collision at dy=+{dy} mm for {getattr(s, 'label', 'part')}: {ov_s:.6f} mm^3!"
                )

    # Surface clearances at rest
    all_cio = right_cio_desk + left_cio_desk
    clr_feet = min_surface_clearance(right_feet_desk + left_feet_desk, box_desk)
    clr_ball = min_surface_clearance([ball_desk], box_desk)
    clr_wheel = min_surface_clearance([wheel_desk], box_desk)
    clr_keycaps = min_surface_clearance(keycaps_desk, box_desk)
    clr_cio_box = min_surface_clearance(all_cio, box_desk)
    clr_cio_lid = min_surface_clearance(all_cio, lid_desk)

    print(
        f"[carrying-box-assembly] Minimum surface clearances:\n"
        f"  - Box vs All 10 Rubber Feet (Floating!): {clr_feet:.3f} mm (>= 0.50 mm, ZERO friction)\n"
        f"  - Box vs 25mm Trackball (Keeper Slot):   {clr_ball:.3f} mm (target 0.50..0.70 mm)\n"
        f"  - Box vs Inertia Wheel:                  {clr_wheel:.3f} mm (>= 1.50 mm)\n"
        f"  - Box vs All 40 Keycaps:                 {clr_keycaps:.3f} mm (>= 0.75 mm)\n"
        f"  - Box vs All 4 CIO-SLMG-T-C Tips:        {clr_cio_box:.3f} mm (>= 0.90 mm)\n"
        f"  - Lid vs North rJ1 CIO-SLMG-T-C Tip:     {clr_cio_lid:.3f} mm (>= 2.00 mm)"
    )
    assert clr_feet >= 0.50, f"Rubber feet clearance {clr_feet:.3f} mm < 0.50 mm!"
    assert 0.50 <= clr_ball <= 0.70, f"Trackball keeper clearance {clr_ball:.3f} mm outside [0.50, 0.70] mm!"
    assert clr_wheel >= 1.50, f"Inertia wheel clearance {clr_wheel:.3f} mm < 1.50 mm!"
    assert clr_keycaps >= 0.75, f"Keycap clearance {clr_keycaps:.3f} mm < 0.75 mm!"
    assert clr_cio_box >= 0.90, f"CIO tip clearance to Box {clr_cio_box:.3f} mm < 0.90 mm!"
    assert clr_cio_lid >= 2.00, f"CIO tip clearance to Lid {clr_cio_lid:.3f} mm < 2.00 mm!"

    # 6-DOF positive mechanical lock inside `Carrying_Box` ALONE (Concept B-1 Lidless!)
    right_case_desk = max(right_solids_desk, key=lambda s: s.volume)
    left_case_desk = max(left_solids_desk, key=lambda s: s.volume)
    test_dirs = [
        ("+X", (0.65, 0.0, 0.0)),
        ("-X", (-0.65, 0.0, 0.0)),
        ("+Y_Mouth_Detent", (0.0, 0.75, 0.0)),
        ("-Y_Back_Wall", (0.0, -0.65, 0.0)),
        ("+Z", (0.0, 0.0, 0.55)),
        ("-Z", (0.0, 0.0, -0.55)),
    ]
    for name, target_case in (("Right_Case", right_case_desk), ("Left_Case_Packed", left_case_desk)):
        for d_tag, vec in test_dirs:
            shifted = bd.Solid(target_case.wrapped.Moved(bd.Location(vec).wrapped))
            ov_lock = overlap_volume(box_desk, shifted)
            assert ov_lock > 0.02, (
                f"[6-DOF FAIL] {name} is NOT locked in {d_tag} inside lidless Carrying_Box (ov={ov_lock:.5f} mm^3)!"
            )

    ball_lifted = bd.Solid(ball_desk.wrapped.Moved(bd.Location((-SIN_TENT * 1.0, 0.0, COS_TENT * 1.0)).wrapped))
    assert overlap_volume(box_desk, ball_lifted) > 0.40, "[6-DOF FAIL] Trackball Keeper U-slot failed to stop +1mm lift!"
    print("[carrying-box-assembly] Orthogonal 90-deg cuboid, 6-DOF lidless lock, slide & CIO checks: ALL PASS!")


def main() -> None:
    print("=== Building curcur40 Concept B-1: Orthogonal 90-deg Rectangular Slide-In PA12 Carrying Box ===")
    CASES_DIR.mkdir(parents=True, exist_ok=True)
    ASSEMBLIES_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Build `Carrying_Box` & `Carrying_Box_Lid` directly in orthogonal `box_desk` pose (`Z in [0, 65.42] mm`)
    box_desk, lid_desk = build_carrying_box_and_lid_desk()
    verify_orthogonal_cuboid_bounds(box_desk)

    bb_box = box_desk.bounding_box()
    box_print = box_desk.moved(bd.Location((0.0, 0.0, -bb_box.min.Z)))
    box_print.label = "curcur40_carrying_box"

    lid_flat = lid_desk.rotate(bd.Axis.X, -90.0)
    bb_lid = lid_flat.bounding_box()
    lid_print = lid_flat.moved(bd.Location((0.0, 0.0, -bb_lid.min.Z)))
    lid_print.label = "curcur40_carrying_box_lid"

    # 2. Run JLC3DP preflight & `< 0.80 mm` zero-violation checks on BOTH parts!
    verify_jlc3dp_part(box_print, "carrying-box")
    verify_jlc3dp_part(lid_print, "carrying-box-lid")

    bd.export_step(box_print, str(CASES_DIR / "carrying-box.step"))
    bd.export_stl(box_print, str(CASES_DIR / "carrying-box.stl"))
    bd.export_step(lid_print, str(CASES_DIR / "carrying-box-lid.step"))
    bd.export_stl(lid_print, str(CASES_DIR / "carrying-box-lid.stl"))
    print("Exported orthogonal carrying-box.step/.stl & carrying-box-lid.step/.stl")

    # 3. Load synchronized 674-solid `assembly-full.step`, transform to `box_desk`, & verify all 690 solids
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

    verify_carrying_box_assembly_desk(
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

    # 4. Export `carrying-box-assembly.step` (Concept B-1 Lidless) FIRST before re-parenting `anytree` nodes!
    right_grp = bd.Compound(children=right_solids_desk + right_feet_desk + right_cio_desk)
    right_grp.label = "Right_Keyboard_With_Feet_And_CIO_Tips"
    left_grp = bd.Compound(children=left_solids_desk + left_feet_desk + left_cio_desk)
    left_grp.label = "Left_Keyboard_Packed_With_Feet_And_CIO_Tips"

    asm_lidless = bd.Compound(children=[box_desk, right_grp, left_grp])
    asm_lidless.label = "curcur40_carrying_box_assembly"
    bb_open = asm_lidless.bounding_box()
    print(
        f"Concept B-1 (Orthogonal Lidless Slide-In Box) Envelope: "
        f"{bb_open.size.X:.2f} x {bb_open.size.Y:.2f} x {bb_open.size.Z:.2f} mm "
        f"(Z = [{bb_open.min.Z:.4f}, {bb_open.max.Z:.4f}] mm)"
    )
    bd.export_step(asm_lidless, str(ASSEMBLIES_DIR / "carrying-box-assembly.step"))
    assert len(bd.import_step(str(ASSEMBLIES_DIR / "carrying-box-assembly.step")).solids()) == 689, (
        "Exported carrying-box-assembly.step solid count mismatch!"
    )

    asm_with_lid = bd.Compound(children=[box_desk, lid_desk, right_grp, left_grp])
    asm_with_lid.label = "curcur40_carrying_box_with_lid_assembly"
    bb_closed = asm_with_lid.bounding_box()
    print(
        f"Concept B-2 (Orthogonal Slide-In Box + Cap Lid) Envelope: "
        f"{bb_closed.size.X:.2f} x {bb_closed.size.Y:.2f} x {bb_closed.size.Z:.2f} mm "
        f"(Z = [{bb_closed.min.Z:.4f}, {bb_closed.max.Z:.4f}] mm)"
    )
    bd.export_step(asm_with_lid, str(ASSEMBLIES_DIR / "carrying-box-with-lid-assembly.step"))
    assert len(bd.import_step(str(ASSEMBLIES_DIR / "carrying-box-with-lid-assembly.step")).solids()) == 690, (
        "Exported carrying-box-with-lid-assembly.step solid count mismatch!"
    )
    print("Exported orthogonal carrying-box-assembly.step (689 solids) & carrying-box-with-lid-assembly.step (690 solids)!")


if __name__ == "__main__":
    main()
