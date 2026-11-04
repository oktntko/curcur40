# -*- coding: utf-8 -*-
"""
Generate curcur40 Concept B: Slide-In 5-Sided Carrying Box (`cases/carrying-box.step`, `cases/carrying-box.stl`),
Optional Snap-On Cap Lid (`cases/carrying-box-lid.step`, `cases/carrying-box-lid.stl`),
and Full Packed Verification Assembly (`cases/assemblies/carrying-box-assembly.step`).

Design Highlights (Concept B — Slide-In Holster Box with Convertible Lid):
1. 5-Sided Full-Cover Sleeve Box (`carrying-box.step` — Works 100% Standalone WITHOUT Lid):
   - Long-edge North mouth (`depth 100.65 mm`) for effortless shallow slide-in / pull-out of Right & Left halves.
   - Wedge-canceling `Rot_X(180 deg)` arrangement gives 100% parallel flat horizontal top & bottom outer faces
     (height `65.42 mm`), completely enclosing and protecting all 10 bottom rubber feet inside recessed floor/ceiling
     wells (`>= 0.55 mm` air clearance so rubber feet NEVER touch or drag during sliding!).
   - Precision PA12 C-channel perimeter rails (`0.20 mm` Z gap, `0.30 mm` X gap) support only the smooth PA12 case
     rims and outer edges for silky-smooth zero-stick sliding.
   - Central `2.25 mm` divider web separates the upper & lower compartments and integrates a `15.60 mm` wide
     non-contact Trackball Keeper U-slot (`0.58 mm` radial gap, shock lift `<= 0.73 mm`).
   - Built-in side-wall PA12 entrance click-detent catches (`~4 N` smooth snap behind the R=2.0 mm case corners)
     positively retain both keyboards in a bag WITHOUT needing a lid, paired with `36 mm` wide finger-pull cutouts.
   - All 4 `CIO-SLMG-T-C` magnetic USB-C tips remain 100% open & unobstructed along the entire slide trajectory
     (North open mouth for `rJ1`, West open slide slot for `rJ2`, East open slide slot for `J2`, South window for `J1`).
2. Optional Snap-On Cap Lid (`carrying-box-lid.step` — 2-Piece Full Box Mode):
   - Snaps flush onto the North mouth via dual mid-wall side clasps (adds `0.00 mm` to box height!), sealing the
     mouth & finger cutouts while keeping an `18.0 mm` archway open around `rJ1`'s `CIO-SLMG-T-C` magnetic tip.
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

from generate_carrying_case import (
    ASSEMBLIES_DIR,
    CASES_DIR,
    DX_LEFT,
    DY_LEFT,
    H_SEP,
    HOST_USBC_CX_R,
    RUBBER_FOOT_HEIGHT,
    SPLIT_USBC_CY_R,
    TAN_TENT,
    TB_CX,
    TB_CY,
    THETA_TENT_DEG,
    THETA_TENT_RAD,
    USBC_CENTER_Z_R,
    X_PINKY_OUTER,
    X_THUMB_OUTER,
    Y_NORTH_OUTER,
    Y_SOUTH_OUTER,
    Z_PINKY_BOTTOM,
    Z_THUMB_BOTTOM,
    _aabb_intersects,
    _aabb_min_dist,
    build_cio_magnetic_tips_in_case_pose,
    build_rubber_feet_in_case_pose,
    min_surface_clearance,
    transform_left_to_packed,
    z_case_bottom_right,
)

# Box dimensions in `asm` coordinate frame (Right rim Z = 0.00, Left rim Z = +19.50)
XY_SLIDE_GAP = 0.3000                 # >= 0.30 mm JLC3DP moving clearance
Z_SLIDE_GAP = 0.2000                  # 0.20 mm vertical rail clearance
BOX_WALL = 2.2000                     # 2.20 mm sturdy PA12 outer walls

X_IN_WEST = X_THUMB_OUTER - XY_SLIDE_GAP     # 6.7250 mm
X_OUT_WEST = X_IN_WEST - BOX_WALL            # 4.5250 mm
X_IN_EAST = X_PINKY_OUTER + XY_SLIDE_GAP     # 136.1580 mm
X_OUT_EAST = X_IN_EAST + BOX_WALL            # 138.3580 mm

Y_IN_SOUTH = Y_SOUTH_OUTER - XY_SLIDE_GAP    # -126.9500 mm
Y_OUT_SOUTH = Y_IN_SOUTH - BOX_WALL          # -129.1500 mm
Y_MOUTH = -28.5000                           # 2.3375 mm forward of -30.8375 mm for entrance detents

# Perpendicular offsets from bare angled case bottoms (become horizontal Z planes in desk pose!)
COS_TENT = math.cos(THETA_TENT_RAD)
D_RUNNER_PERP = Z_SLIDE_GAP                  # 0.20 mm perpendicular gap under bare outer case corners
D_WELL_PERP = 2.7500                         # 2.75 mm recessed floor/ceiling well (0.75 mm clear of 2.0 mm feet!)
D_OUT_PERP = 4.7500                          # 4.75 mm outer box face (2.00 mm solid top & bottom walls!)

# Central divider web & Trackball Keeper U-slot (`Z in [12.80, 15.05] mm`)
DIV_Z_MIN = 12.8000
DIV_Z_MAX = 15.0500
TB_SLOT_R = 7.8000                           # 15.60 mm wide U-slot (0.58 mm radial gap to 25mm ball)

# Finger pull cutout (`X in [62.00, 98.00]`, clear of all 10 rubber feet!)
FINGER_X_MIN = 62.0000
FINGER_X_MAX = 98.0000
FINGER_CX = 0.5 * (FINGER_X_MIN + FINGER_X_MAX)   # 80.0000 mm
FINGER_W = FINGER_X_MAX - FINGER_X_MIN            # 36.0000 mm
FINGER_Y_MIN = -44.5000                            # 16.00 mm deep scoop from Y_MOUTH = -28.50 mm


def z_bot_plane(x: float, d_perp: float) -> float:
    """Z on plane parallel to Right's outer bottom shifted downward by perpendicular distance `d_perp`."""
    return z_case_bottom_right(x) - d_perp / COS_TENT


def z_top_plane(x: float, d_perp: float) -> float:
    """Z on plane parallel to Packed Left's outer top shifted upward by perpendicular distance `d_perp`."""
    z_left_bare = (H_SEP - Z_PINKY_BOTTOM) + (x - X_THUMB_OUTER) * TAN_TENT  # +29.50 at West, +46.40 at East
    return z_left_bare + d_perp / COS_TENT


def transform_asm_to_box_desk(shape: bd.Shape) -> bd.Shape:
    """
    Rotate by `+THETA_TENT_DEG` (+7.473 deg) around Y and shift Z so `Carrying_Box` outer bottom
    rests flat on `Z = 0.0000 mm` (and outer top is flat horizontal at `Z = +65.4209 mm`).
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


def build_entrance_detent_west_right() -> tuple[bd.Solid, bd.Solid]:
    """
    Builds the Right-keyboard entrance click-detent cantilever spring arm + slot cutter on the West Thumb wall
    (`X_IN_WEST = 6.7250`, `Z in [-22.80, -14.80]`, `2.20 mm` clear below `rJ2` slot & `2.30 mm` clear above runner).
    Engages Right's R=2.00 mm NW corner at `(7.0250, -30.8375)` with 0.00 mm^3 rest overlap and positive +Y lock.
    """
    z_bot_slot = -24.8000
    z_arm_bot = -22.8000
    z_arm_top = -14.8000
    z_top_slot = -12.8000
    y_slot_root_straight = -45.5000  # Filleted by R=1.00 -> root at Y = -46.50 mm

    # Cutter isolating `Z in [-24.80, -12.80]` from `Y = -46.50` to `Y_MOUTH`
    cut_box = bd.Box(
        10.00,
        (Y_MOUTH + 2.00) - y_slot_root_straight,
        z_top_slot - z_bot_slot,
        align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((X_IN_WEST - 1.0, y_slot_root_straight, z_bot_slot)))
    root_edges = cut_box.edges().filter_by(
        lambda e: abs(e.bounding_box().size.X - 10.00) < 0.1
        and abs(e.bounding_box().min.Y - y_slot_root_straight) < 0.05
    )
    assert len(root_edges) == 2, f"Expected 2 root edges on West detent cutter, got {len(root_edges)}"
    cut_box = bd.fillet(root_edges, radius=1.00)

    # XY spring beam profile (`Z in [-22.80, -14.80]`, height 8.00 mm)
    # Tangent-cleared 0.22 mm behind Right's R=2.00 mm NW corner arc centered at `(9.0250, -32.8375)`!
    xy_pts = [
        (X_OUT_WEST, -46.8000),   # Blends 0.30 mm south of slot root into solid West wall
        (X_IN_WEST, -46.8000),
        (X_IN_WEST, -32.0000),    # 0.22 mm clear behind R=2.00 NW corner arc -> zero rattle & 0.00 mm^3 overlap!
        (8.0250, -30.7000),       # 45 deg exit ramp -> +1.00 mm positive catch behind X_THUMB_OUTER (7.0250)!
        (8.0250, -29.8000),       # 0.90 mm flat detent crest (>= 0.80 mm rule!)
        (6.5250, Y_MOUTH),        # 41 deg entry cam funnel (< 7.0250 so pushing keyboard in self-cams open!)
        (X_OUT_WEST, Y_MOUTH),    # 2.00 mm flat front tip (>= 0.80 mm!)
    ]
    with bd.BuildSketch(bd.Plane.XY.offset(z_arm_bot)) as sk_arm:
        bd.Polygon(xy_pts, align=None)
    arm_solid = bd.extrude(sk_arm.sketch, amount=z_arm_top - z_arm_bot).solids()[0]
    return arm_solid, cut_box


def build_entrance_detent_east_left() -> tuple[bd.Solid, bd.Solid]:
    """
    Exact XZ-inverted entrance click-detent on the East Thumb wall for Packed Left (`X_IN_EAST = 136.1580`,
    `Z in [+34.30, +42.30]`, `2.20 mm` clear above `J2` slot & `2.30 mm` clear below upper runner),
    at the SAME North mouth `Y` coordinates (`Y in [-46.80, -28.50]`) to engage Left's R=2.00 mm NE corner!
    """
    arm_w, cut_w = build_entrance_detent_west_right()

    # Transform `(X, Y, Z) -> (DX_LEFT - X, Y, H_SEP - Z)` (`det = +1`: Rot_Y(180) + shift `(DX_LEFT, 0, H_SEP)`)
    loc = bd.Pos(DX_LEFT, 0.0, H_SEP) * bd.Rot(0.0, 180.0, 0.0)
    return bd.Solid(arm_w.wrapped.Moved(loc.wrapped)), bd.Solid(cut_w.wrapped.Moved(loc.wrapped))


def build_carrying_box_and_lid_asm() -> tuple[bd.Solid, bd.Solid]:
    """
    Builds both:
      1. `Carrying_Box` (5-sided slide-in sleeve box with internal C-rails, central trackball keeper web,
         4 open CIO USB-C slots/windows, finger cutouts, and built-in entrance click-detents)
      2. `Carrying_Box_Lid` (flush snap-on North mouth cap with open `rJ1` CIO archway & dual side clasps)
    in the canonical `asm` coordinate system.
    """
    # 1. Outer Box Prism (`X in [X_OUT_WEST, X_OUT_EAST]`, `Y in [Y_OUT_SOUTH, Y_MOUTH]`, angled flat top & bottom)
    outer_xz = [
        (X_OUT_WEST, z_bot_plane(X_OUT_WEST, D_OUT_PERP)),
        (X_OUT_EAST, z_bot_plane(X_OUT_EAST, D_OUT_PERP)),
        (X_OUT_EAST, z_top_plane(X_OUT_EAST, D_OUT_PERP)),
        (X_OUT_WEST, z_top_plane(X_OUT_WEST, D_OUT_PERP)),
    ]
    outer_shell = extrude_xz_profile_along_y(outer_xz, Y_OUT_SOUTH, Y_MOUTH)
    # Round the 4 longitudinal Y-edges slightly? Let's check: top/bottom faces meet vertical side walls at 82.5° / 97.5°!
    # Leaving crisp or R=1.50 mm filleted longitudinal edges? R=1.50 mm feels super smooth in the hand AND in bags!
    # Wait: let's check if R=1.50 mm interferes with `X_OUT_WEST` / `X_OUT_EAST` detent tips!
    # Detent tips are at `Z in [-22.8, -14.8]` and `[+34.3, +42.3]`, which are >= 5.5 mm away from the top/bottom corners!
    long_y_edges = outer_shell.edges().filter_by(
        lambda e: abs(e.bounding_box().size.Y - (Y_MOUTH - Y_OUT_SOUTH)) < 0.2
    )
    assert len(long_y_edges) == 4, f"Expected 4 longitudinal Y-edges, got {len(long_y_edges)}"
    outer_shell = bd.fillet(long_y_edges, radius=2.00)

    # 2. Inner Lower & Upper Compartment Cavities (`Y in [Y_IN_SOUTH, Y_MOUTH + 5.0]`), leaving:
    #    - West & East C-channel rails (`0.20 mm` Z gap, `1.50..1.80 mm` X overlap)
    #    - Recessed central floor & ceiling wells (`X in [8.8250, 134.0580]`, `D_WELL_PERP = 2.75 mm` so feet float!)
    #    - Central Divider Web (`Z in [DIV_Z_MIN, DIV_Z_MAX] = [12.80, 15.05] mm`)!
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
        (X_IN_EAST, Z_SLIDE_GAP),          # +0.2000 mm lower rim ceiling
        (x_rim_e, Z_SLIDE_GAP),
        (x_rim_e, DIV_Z_MIN),              # +12.8000 mm central divider underside
        (x_rim_w, DIV_Z_MIN),
        (x_rim_w, Z_SLIDE_GAP),
        (X_IN_WEST, Z_SLIDE_GAP),
    ]
    lower_cav = extrude_xz_profile_along_y(lower_cav_xz, Y_IN_SOUTH, Y_MOUTH + 5.0)

    z_upper_rim = H_SEP - Z_SLIDE_GAP      # +19.3000 mm upper rim support shelf
    upper_cav_xz = [
        (X_IN_WEST, z_upper_rim),
        (x_rim_w, z_upper_rim),
        (x_rim_w, DIV_Z_MAX),              # +15.0500 mm central divider top
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
    upper_cav = extrude_xz_profile_along_y(upper_cav_xz, Y_IN_SOUTH, Y_MOUTH + 5.0)

    body = outer_shell - lower_cav - upper_cav

    # 3. Central Divider Web Features (`Z in [12.80, 15.05]`):
    #    a) Trackball Slide & Keeper U-Slot (`X = 23.8125 +- 7.80 mm`, semicircular end at `Y = -109.5375`)
    with bd.BuildSketch(bd.Plane.XY.offset(DIV_Z_MIN - 0.50)) as sk_tb_slot:
        with bd.Locations([(TB_CX, TB_CY)]):
            bd.Circle(TB_SLOT_R)
        y_len = (Y_MOUTH + 5.0) - TB_CY
        with bd.Locations([(TB_CX, TB_CY + 0.5 * y_len)]):
            bd.Rectangle(2.0 * TB_SLOT_R, y_len)
    tb_slot_cutter = bd.extrude(sk_tb_slot.sketch, amount=(DIV_Z_MAX - DIV_Z_MIN) + 1.00)

    #    b) Two smooth rounded lightening windows in the central divider web (`saves PA12 weight & aids depowdering`)
    with bd.BuildSketch(bd.Plane.XY.offset(DIV_Z_MIN - 0.50)) as sk_light:
        with bd.Locations([(60.00, -86.00), (106.00, -86.00)]):
            bd.RectangleRounded(34.00, 52.00, 8.00)
    light_cutter = bd.extrude(sk_light.sketch, amount=(DIV_Z_MAX - DIV_Z_MIN) + 1.00)

    body = body - tb_slot_cutter - light_cutter

    # 4. Ergonomic North Finger-Pull Cutouts (`X in [62.00, 98.00]`, `Y in [-44.50, -28.50]`) through
    #    Top Wall, Central Divider Web, and Bottom Wall (100% clear of all 10 rubber feet!)
    with bd.BuildSketch(bd.Plane.XY.offset(-40.00)) as sk_finger:
        with bd.Locations([(FINGER_CX, 0.5 * (FINGER_Y_MIN + (Y_MOUTH + 10.0)))]):
            bd.RectangleRounded(FINGER_W, (Y_MOUTH + 10.0) - FINGER_Y_MIN, 8.00)
    finger_cutter = bd.extrude(sk_finger.sketch, amount=100.00)
    body = body - finger_cutter

    # 5. Open Slots & Window for All 4 Permanent `CIO-SLMG-T-C` Magnetic USB-C Tips:
    #    - West Side Slot for Right `rJ2` (`Z in [-10.60, -1.10]`, `Y in [-95.50, Y_MOUTH + 5.0]`, R=2.50 end)
    w_slot_len = (Y_MOUTH + 5.0) - (-95.5000)
    w_slot = bd.Box(
        12.00,
        w_slot_len,
        -1.1000 - (-10.6000),
        align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((X_IN_WEST, -95.5000, -10.6000)))
    w_slot_edges = w_slot.edges().filter_by(
        lambda e: abs(e.bounding_box().size.X - 12.00) < 0.1 and e.bounding_box().min.Y < -95.40
    )
    assert len(w_slot_edges) == 2, f"Expected 2 end edges on w_slot, got {len(w_slot_edges)}"
    w_slot = bd.fillet(w_slot_edges, radius=2.50)

    #    - East Side Slot for Packed Left `J2` (`Z in [+20.60, +30.10]`, `Y in [-79.70, Y_MOUTH + 5.0]`, R=2.50 end)
    e_slot_len = (Y_MOUTH + 5.0) - (-79.7000)
    e_slot = bd.Box(
        12.00,
        e_slot_len,
        30.1000 - 20.6000,
        align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN),
    ).moved(bd.Location((X_IN_EAST, -79.7000, 20.6000)))
    e_slot_edges = e_slot.edges().filter_by(
        lambda e: abs(e.bounding_box().size.X - 12.00) < 0.1 and e.bounding_box().min.Y < -79.60
    )
    assert len(e_slot_edges) == 2, f"Expected 2 end edges on e_slot, got {len(e_slot_edges)}"
    e_slot = bd.fillet(e_slot_edges, radius=2.50)

    #    - South Back Wall Window for Packed Left `J1` (`X = 116.3080`, `Z = +25.3500`, `16.40 x 10.00 mm`, R=2.50)
    left_host_cx = DX_LEFT - HOST_USBC_CX_R          # 116.3080 mm
    left_host_cz = H_SEP - USBC_CENTER_Z_R           # +25.3500 mm
    p_south_win = bd.Plane(origin=(left_host_cx, Y_OUT_SOUTH - 1.0, left_host_cz), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
    s_win = bd.extrude(p_south_win * bd.RectangleRounded(16.40, 10.00, 2.50), amount=8.00)

    body = body - w_slot - e_slot - s_win

    # 6. Integrate Lidless Entrance Click-Detents (West for Right, East for Packed Left)
    det_arm_r, det_cut_r = build_entrance_detent_west_right()
    det_arm_l, det_cut_l = build_entrance_detent_east_left()
    body = body - det_cut_r - det_cut_l + det_arm_r + det_arm_l

    # 7. Flush Recessed Side Clasp Pockets (`Z in [3.80, 15.70]`, `Y in [-38.00, Y_MOUTH]`)
    #    on West & East outer walls for the Optional Snap-On Cap Lid (`carrying-box-lid` adds 0.00 mm width & height!)
    for is_east_p in (False, True):
        x_w = X_OUT_EAST if is_east_p else X_OUT_WEST
        in_sgn = -1.0 if is_east_p else 1.0  # inward into the 4.00 mm thick side wall
        pocket_xy = [
            (x_w - 2.00 * in_sgn, Y_MOUTH + 2.00),
            (x_w + 1.70 * in_sgn, Y_MOUTH + 2.00),
            (x_w + 1.70 * in_sgn, -34.0000),
            (x_w + 2.55 * in_sgn, -34.8500),
            (x_w + 2.55 * in_sgn, -38.0000),
            (x_w - 2.00 * in_sgn, -38.0000),
        ]
        with bd.BuildSketch(bd.Plane.XY.offset(3.8000)) as sk_pock:
            bd.Polygon(pocket_xy, align=None)
        pock_solid = bd.extrude(sk_pock.sketch, amount=15.7000 - 3.8000).solids()[0]
        # Fillet internal back vertical edge at `(x_w + 2.55 * in_sgn, -38.00)` with R=1.00 (diam 2.00 >= 1.50 mm)
        pock_back_edges = pock_solid.edges().filter_by(
            lambda e, x_target=x_w + 2.55 * in_sgn: abs(e.bounding_box().size.Z - (15.7000 - 3.8000)) < 0.1
            and abs(e.bounding_box().center().X - x_target) < 0.05
            and abs(e.bounding_box().center().Y - (-38.0000)) < 0.05
        )
        assert len(pock_back_edges) == 1, f"Expected 1 pocket back edge, got {len(pock_back_edges)}"
        pock_solid = bd.fillet(pock_back_edges, radius=1.00)
        body = body - pock_solid

    box_solids = body.solids()
    assert len(box_solids) == 1, f"Expected single solid for Carrying_Box, got {len(box_solids)}"
    box_solid = box_solids[0]
    box_solid.label = "Carrying_Box"

    # =========================================================================
    # 8. Build Optional Snap-On Cap Lid (`Carrying_Box_Lid`) at North Mouth!
    #    - Sits with `0.15 mm` axial clearance at `Y in [-28.35, -26.15]` (`2.20 mm` front cap wall)
    #    - Flush top & bottom alignment tongues (`X in [62.40, 97.60]`, `Y in [-38.50, -26.15]`) fill the
    #      North finger-pull cutouts (`0.40 mm` lateral gap) with ZERO added height!
    #    - `18.00 mm` wide open window (`X = 26.5750 +- 9.00`, `Z = -5.85 +- 5.90`) clears Right's `rJ1` CIO tip!
    #    - Dual FLUSH side snap clasps (`Z in [4.30, 15.20]`, `Y in [-37.20, -26.15]`) seat flush inside the
    #      recessed side pockets (adds `0.00 mm` to width & height, `>= 0.30 mm` clearance everywhere)!
    # =========================================================================
    y_lid_in = Y_MOUTH + 0.1500            # -28.3500 mm (0.15 mm gap from box mouth -> 0.00 mm^3 B-rep overlap!)
    y_lid_out = y_lid_in + BOX_WALL        # -26.1500 mm

    lid_xz = [
        (X_OUT_WEST, z_bot_plane(X_OUT_WEST, D_OUT_PERP)),
        (X_OUT_EAST, z_bot_plane(X_OUT_EAST, D_OUT_PERP)),
        (X_OUT_EAST, z_top_plane(X_OUT_EAST, D_OUT_PERP)),
        (X_OUT_WEST, z_top_plane(X_OUT_WEST, D_OUT_PERP)),
    ]
    lid_plate = extrude_xz_profile_along_y(lid_xz, y_lid_in, y_lid_out)
    lid_y_edges = lid_plate.edges().filter_by(
        lambda e: abs(e.bounding_box().size.Y - BOX_WALL) < 0.1
    )
    if len(lid_y_edges) == 4:
        lid_plate = bd.fillet(lid_y_edges, radius=2.00)

    # Flush Top & Bottom Finger-Cutout Plugs (`X in [62.35, 97.65]`, `Y in [-44.15, y_lid_out]`, R=7.65 rounded tip
    # matching `finger_cutter` with uniform `0.35 mm` clearance so Mode B-2 seals the finger cutouts completely!)
    plug_gap = 0.3500
    tx_min = FINGER_X_MIN + plug_gap
    tx_max = FINGER_X_MAX - plug_gap
    plug_y_min = FINGER_Y_MIN + plug_gap
    plug_r = 8.0000 - plug_gap
    with bd.BuildSketch(bd.Plane.XY.offset(-45.00)) as sk_plug_xy:
        with bd.Locations([(FINGER_CX, 0.5 * (plug_y_min + (y_lid_out + 15.0)))]):
            bd.RectangleRounded(tx_max - tx_min, (y_lid_out + 15.0) - plug_y_min, plug_r)
    plug_xy_mask = bd.extrude(sk_plug_xy.sketch, amount=110.00)

    bot_plug_xz = [
        (tx_min - 1.0, z_bot_plane(tx_min - 1.0, D_OUT_PERP)),
        (tx_max + 1.0, z_bot_plane(tx_max + 1.0, D_OUT_PERP)),
        (tx_max + 1.0, z_bot_plane(tx_max + 1.0, D_WELL_PERP + 0.25)),
        (tx_min - 1.0, z_bot_plane(tx_min - 1.0, D_WELL_PERP + 0.25)),
    ]
    top_plug_xz = [
        (tx_min - 1.0, z_top_plane(tx_min - 1.0, D_WELL_PERP + 0.25)),
        (tx_max + 1.0, z_top_plane(tx_max + 1.0, D_WELL_PERP + 0.25)),
        (tx_max + 1.0, z_top_plane(tx_max + 1.0, D_OUT_PERP)),
        (tx_min - 1.0, z_top_plane(tx_min - 1.0, D_OUT_PERP)),
    ]
    bot_plug = (extrude_xz_profile_along_y(bot_plug_xz, plug_y_min - 1.0, y_lid_out) & plug_xy_mask).solids()[0]
    top_plug = (extrude_xz_profile_along_y(top_plug_xz, plug_y_min - 1.0, y_lid_out) & plug_xy_mask).solids()[0]

    # Dual Flush Side Snap Clasps (`Z in [+4.30, +15.20]`, `10.90 mm` tall) on West & East
    clasp_solids = []
    for is_east in (False, True):
        x_wall = X_OUT_EAST if is_east else X_OUT_WEST
        in_sgn = -1.0 if is_east else 1.0  # inward into recessed side pocket
        clasp_xy = [
            (x_wall, y_lid_out),
            (x_wall, -37.2000),
            (x_wall + 1.40 * in_sgn, -37.2000),
            (x_wall + 2.20 * in_sgn, -36.4000),
            (x_wall + 2.20 * in_sgn, -35.2500),
            (x_wall + 1.40 * in_sgn, -34.4500),
            (x_wall + 1.40 * in_sgn, y_lid_out),
        ]
        with bd.BuildSketch(bd.Plane.XY.offset(4.3000)) as sk_clasp:
            bd.Polygon(clasp_xy, align=None)
        clasp_solids.append(bd.extrude(sk_clasp.sketch, amount=15.2000 - 4.3000).solids()[0])

    lid_body = lid_plate + bot_plug + top_plug + clasp_solids[0] + clasp_solids[1]

    # Cut open archway in Lid for Right's North `rJ1` `CIO-SLMG-T-C` magnetic tip (`18.00 x 11.80 mm`, R=2.00)
    p_lid_usbc = bd.Plane(origin=(HOST_USBC_CX_R, y_lid_in - 2.0, -5.8500), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
    lid_usbc_cut = bd.extrude(p_lid_usbc * bd.RectangleRounded(18.00, 11.80, 2.50), amount=10.00)
    lid_body = lid_body - lid_usbc_cut

    lid_solids = lid_body.solids()
    assert len(lid_solids) == 1, f"Expected single solid for Carrying_Box_Lid, got {len(lid_solids)}"
    lid_solid = lid_solids[0]
    lid_solid.label = "Carrying_Box_Lid"

    return box_solid, lid_solid


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


def verify_carrying_box_assembly(
    box_asm: bd.Solid,
    lid_asm: bd.Solid,
    right_solids: list[bd.Solid],
    left_packed_solids: list[bd.Solid],
    right_feet: list[bd.Solid],
    left_packed_feet: list[bd.Solid],
    right_cio_tips: list[bd.Solid],
    left_packed_cio_tips: list[bd.Solid],
) -> None:
    """
    Verifies:
      1. Zero B-rep overlap (`0.00000000 mm^3`) across `Carrying_Box`, `Carrying_Box_Lid`, all 674 solids
         of Left & Right full assemblies, all 10 rubber feet, and all 4 `CIO-SLMG-T-C` tips.
      2. Full `+Y -> -Y` slide-trajectory verification (`dy = +8, +25, +50, +80 mm` for Right & Left groups
         including rubber feet, 25mm ball, and CIO tips — zero collision with rails, walls, or divider!).
      3. Surface clearances (Rubber feet floating `>= 0.50 mm` off box floor/ceiling, 25mm ball `0.50..0.70 mm`,
         Inertia wheel `>= 1.50 mm`, 40 Keycaps `>= 0.75 mm`, 4 CIO tips `>= 1.10 mm`).
      4. Positive 6-DOF mechanical lock (`+-X, +-Y, +-Z`) inside `Carrying_Box` EVEN WITHOUT THE LID!
    """
    box_bb = box_asm.bounding_box()
    lid_bb = lid_asm.bounding_box()
    r_all = right_solids + right_feet + right_cio_tips
    l_all = left_packed_solids + left_packed_feet + left_packed_cio_tips
    all_parts = r_all + l_all

    # 1. Box vs Lid & Box/Lid vs all 688 solids
    ov_box_lid = overlap_volume(box_asm, lid_asm)
    assert ov_box_lid == 0.0, f"B-rep interference between Box & Lid: {ov_box_lid:.8f} mm^3!"

    max_ov_box = 0.0
    worst_box = ""
    max_ov_lid = 0.0
    worst_lid = ""
    for idx, s in enumerate(all_parts):
        sb = s.bounding_box()
        if _aabb_intersects(box_bb, sb):
            ov = overlap_volume(box_asm, s)
            if ov > max_ov_box:
                max_ov_box = ov
                worst_box = f"{getattr(s, 'label', '') or idx} bbox={sb}"
        if _aabb_intersects(lid_bb, sb):
            ovl = overlap_volume(lid_asm, s)
            if ovl > max_ov_lid:
                max_ov_lid = ovl
                worst_lid = f"{getattr(s, 'label', '') or idx} bbox={sb}"

    print(
        f"[carrying-box-assembly] Overlap check ({len(all_parts)} solids + Box + Lid): "
        f"Box_vs_All={max_ov_box:.8f} mm^3, Lid_vs_All={max_ov_lid:.8f} mm^3, Box_vs_Lid={ov_box_lid:.8f} mm^3"
    )
    assert max_ov_box == 0.0, f"B-rep interference with Carrying_Box: {max_ov_box:.8f} mm^3 at {worst_box}!"
    assert max_ov_lid == 0.0, f"B-rep interference with Carrying_Box_Lid: {max_ov_lid:.8f} mm^3 at {worst_lid}!"

    # 2. Slide-in trajectory verification (`dy = +10, +30, +60, +90 mm`) for key solids:
    #    Case, Top plate, 25mm Ball, Inertia wheel, all 10 Rubber feet, and all 4 CIO tips!
    right_case = max(right_solids, key=lambda s: s.volume)
    left_case_packed = max(left_packed_solids, key=lambda s: s.volume)
    ball_solid = [
        s for s in right_solids if abs(s.bounding_box().size.X - 25.0) < 0.2 and abs(s.bounding_box().max.Z - 14.80) < 0.2
    ][0]
    wheel_solid = [
        s for s in right_solids if 3.90 < s.bounding_box().max.Z < 4.30 and s.bounding_box().size.Y > 21.5
    ][0]
    right_keycaps = [
        s for s in right_solids if abs(s.bounding_box().max.Z - 3.60) < 0.15 and 17.5 < s.bounding_box().size.X < 18.5
    ]
    left_keycaps_packed = [
        s for s in left_packed_solids
        if abs(s.bounding_box().min.Z - (H_SEP - 3.60)) < 0.15 and 17.5 < s.bounding_box().size.X < 18.5
    ]

    # Note: During actual slide-in, the flexible entrance detent (`X in [4.5, 7.8]` on West, `[135.0, 138.4]` on East,
    # `Y in [-31.1, -28.5]`) deflects outward by 0.78 mm against the smooth PA12 case wall; all rigid features
    # (rubber feet, CIO tips, 25mm trackball, wheel, keycaps) MUST have 0.00000000 mm^3 overlap everywhere!
    slide_check_solids = (
        right_feet + left_packed_feet + right_cio_tips + left_packed_cio_tips
        + [ball_solid, wheel_solid] + right_keycaps + left_keycaps_packed
    )
    for dy in (10.0, 30.0, 60.0, 90.0):
        loc_y = bd.Location((0.0, dy, 0.0)).wrapped
        for s in slide_check_solids:
            ms = bd.Solid(s.wrapped.Moved(loc_y))
            if _aabb_intersects(box_bb, ms.bounding_box()):
                ov_s = overlap_volume(box_asm, ms)
                assert ov_s == 0.0, (
                    f"Slide trajectory collision at dy=+{dy} mm for {getattr(s, 'label', 'part')}: {ov_s:.6f} mm^3!"
                )

    # 3. Minimum surface clearances at seated rest pose
    all_cio_tips = right_cio_tips + left_packed_cio_tips
    clr_ball = min_surface_clearance([ball_solid], box_asm)
    clr_wheel = min_surface_clearance([wheel_solid], box_asm)
    clr_keycaps = min_surface_clearance(right_keycaps + left_keycaps_packed, box_asm)
    clr_cio_box = min_surface_clearance(all_cio_tips, box_asm)
    clr_cio_lid = min_surface_clearance(all_cio_tips, lid_asm)
    clr_feet = min_surface_clearance(right_feet + left_packed_feet, box_asm)

    print(
        f"[carrying-box-assembly] Minimum surface clearances:\n"
        f"  - Box vs All 10 Rubber Feet (Floating!): {clr_feet:.3f} mm (>= 0.50 mm, ZERO friction)\n"
        f"  - Box vs 25mm Trackball (Keeper Slot):   {clr_ball:.3f} mm (target 0.50..0.70 mm)\n"
        f"  - Box vs Inertia Wheel:                  {clr_wheel:.3f} mm (>= 1.50 mm)\n"
        f"  - Box vs All 40 Keycaps:                 {clr_keycaps:.3f} mm (>= 0.75 mm)\n"
        f"  - Box vs All 4 CIO-SLMG-T-C Tips:        {clr_cio_box:.3f} mm (>= 1.10 mm)\n"
        f"  - Lid vs North rJ1 CIO-SLMG-T-C Tip:     {clr_cio_lid:.3f} mm (>= 2.00 mm)"
    )
    assert clr_feet >= 0.50, f"Rubber feet clearance {clr_feet:.3f} mm < 0.50 mm (must float free)!"
    assert 0.50 <= clr_ball <= 0.70, f"Trackball keeper clearance {clr_ball:.3f} mm outside [0.50, 0.70] mm!"
    assert clr_wheel >= 1.50, f"Inertia wheel clearance {clr_wheel:.3f} mm < 1.50 mm!"
    assert clr_keycaps >= 0.75, f"Keycap clearance {clr_keycaps:.3f} mm < 0.75 mm!"
    assert clr_cio_box >= 1.10, f"CIO tip clearance to Box {clr_cio_box:.3f} mm < 1.10 mm!"
    assert clr_cio_lid >= 2.00, f"CIO tip clearance to Lid {clr_cio_lid:.3f} mm < 2.00 mm!"

    # 4. 6-DOF positive mechanical lock inside `Carrying_Box` ALONE (Lidless Mode 1!)
    test_dirs = [
        ("+X", (0.65, 0.0, 0.0)),
        ("-X", (-0.65, 0.0, 0.0)),
        ("+Y_Mouth_Detent", (0.0, 0.75, 0.0)),
        ("-Y_Back_Wall", (0.0, -0.65, 0.0)),
        ("+Z", (0.0, 0.0, 0.55)),
        ("-Z", (0.0, 0.0, -0.55)),
    ]
    for name, target_case in (("Right_Case", right_case), ("Left_Case_Packed", left_case_packed)):
        for d_tag, vec in test_dirs:
            shifted = bd.Solid(target_case.wrapped.Moved(bd.Location(vec).wrapped))
            ov_lock = overlap_volume(box_asm, shifted)
            assert ov_lock > 0.02, (
                f"[6-DOF FAIL] {name} is NOT locked in {d_tag} inside lidless Carrying_Box (ov={ov_lock:.5f} mm^3)!"
            )

    # Trackball shock-retention check (`+1.00 mm` lift hits central divider keeper slot!)
    ball_lifted = bd.Solid(ball_solid.wrapped.Moved(bd.Location((0.0, 0.0, 1.00)).wrapped))
    assert overlap_volume(box_asm, ball_lifted) > 0.40, "[6-DOF FAIL] Trackball Keeper U-slot failed to stop +1mm lift!"
    print("[carrying-box-assembly] 6-DOF lidless retention, full slide trajectory & CIO checks: ALL PASS!")


def main() -> None:
    print("=== Building curcur40 Concept B: Slide-In PA12 Carrying Box + Convertible Snap Lid ===")
    CASES_DIR.mkdir(parents=True, exist_ok=True)
    ASSEMBLIES_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Build `Carrying_Box` & `Carrying_Box_Lid` in `asm` pose
    box_asm, lid_asm = build_carrying_box_and_lid_asm()

    # 2. Transform `Carrying_Box` to flat horizontal desk pose (`Z = 0.0000 mm` full-area print bed!)
    box_desk = transform_asm_to_box_desk(box_asm)
    bb_box = box_desk.bounding_box()
    box_print = box_desk.moved(bd.Location((0.0, 0.0, -bb_box.min.Z)))
    box_print.label = "curcur40_carrying_box"

    # Transform `Carrying_Box_Lid` so its flat exterior cap face (`+Y` in asm) rests flat on `Z = 0.0000 mm`!
    lid_desk_oriented = transform_asm_to_box_desk(lid_asm)
    lid_flat = lid_desk_oriented.rotate(bd.Axis.X, -90.0)
    bb_lid = lid_flat.bounding_box()
    lid_print = lid_flat.moved(bd.Location((0.0, 0.0, -bb_lid.min.Z)))
    lid_print.label = "curcur40_carrying_box_lid"

    # 3. Run JLC3DP preflight & `< 0.80 mm` zero-violation checks on BOTH parts!
    verify_jlc3dp_part(box_print, "carrying-box")
    verify_jlc3dp_part(lid_print, "carrying-box-lid")

    bd.export_step(box_print, str(CASES_DIR / "carrying-box.step"))
    bd.export_stl(box_print, str(CASES_DIR / "carrying-box.stl"))
    bd.export_step(lid_print, str(CASES_DIR / "carrying-box-lid.step"))
    bd.export_stl(lid_print, str(CASES_DIR / "carrying-box-lid.stl"))
    print("Exported carrying-box.step/.stl & carrying-box-lid.step/.stl")

    # 4. Load synchronized 674-solid `assembly-full.step` & run full 690-solid verification
    full_asm_path = ASSEMBLIES_DIR / "assembly-full.step"
    print(f"Loading synchronized full keyboard solids from {full_asm_path.name}...")
    full_imported = bd.import_step(str(full_asm_path))
    all_solids = full_imported.solids()
    right_solids = [s for s in all_solids if s.bounding_box().center().X > 0.0]
    left_orig_solids = [s for s in all_solids if s.bounding_box().center().X < 0.0]

    left_packed_solids = [transform_left_to_packed(s) for s in left_orig_solids]
    right_feet = build_rubber_feet_in_case_pose(is_right=True)
    left_packed_feet = [transform_left_to_packed(f) for f in build_rubber_feet_in_case_pose(is_right=False)]
    right_cio_tips = build_cio_magnetic_tips_in_case_pose(is_right=True)
    left_packed_cio_tips = [transform_left_to_packed(t) for t in build_cio_magnetic_tips_in_case_pose(is_right=False)]

    verify_carrying_box_assembly(
        box_asm,
        lid_asm,
        right_solids,
        left_packed_solids,
        right_feet,
        left_packed_feet,
        right_cio_tips,
        left_packed_cio_tips,
    )

    # 5. Export `carrying-box-assembly.step` (Lidless open-mouth view) AND `carrying-box-with-lid-assembly.step`!
    right_grp = bd.Compound(children=right_solids + right_feet + right_cio_tips)
    right_grp.label = "Right_Keyboard_With_Feet_And_CIO_Tips"
    left_grp = bd.Compound(children=left_packed_solids + left_packed_feet + left_packed_cio_tips)
    left_grp.label = "Left_Keyboard_Packed_With_Feet_And_CIO_Tips"

    asm_lidless = transform_asm_to_box_desk(bd.Compound(children=[box_asm, right_grp, left_grp]))
    asm_lidless.label = "curcur40_carrying_box_assembly"
    bb_open = asm_lidless.bounding_box()
    print(
        f"Concept B1 (Lidless Slide-In Box) Envelope: "
        f"{bb_open.size.X:.2f} x {bb_open.size.Y:.2f} x {bb_open.size.Z:.2f} mm "
        f"(Z = [{bb_open.min.Z:.4f}, {bb_open.max.Z:.4f}] mm)"
    )

    asm_with_lid = transform_asm_to_box_desk(bd.Compound(children=[box_asm, lid_asm, right_grp, left_grp]))
    asm_with_lid.label = "curcur40_carrying_box_with_lid_assembly"
    bb_closed = asm_with_lid.bounding_box()
    print(
        f"Concept B2 (Slide-In Box + Snap Lid) Envelope: "
        f"{bb_closed.size.X:.2f} x {bb_closed.size.Y:.2f} x {bb_closed.size.Z:.2f} mm "
        f"(Z = [{bb_closed.min.Z:.4f}, {bb_closed.max.Z:.4f}] mm)"
    )

    bd.export_step(asm_lidless, str(ASSEMBLIES_DIR / "carrying-box-assembly.step"))
    bd.export_step(asm_with_lid, str(ASSEMBLIES_DIR / "carrying-box-with-lid-assembly.step"))
    print("Exported carrying-box-assembly.step & carrying-box-with-lid-assembly.step successfully!")


if __name__ == "__main__":
    main()
