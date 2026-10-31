# -*- coding: utf-8 -*-
"""
Generate curcur40 Full Assembly STEP models:
  1. cases/assemblies/assembly-full.step                (Top Plate horizontal at Z = -2.00 mm)
  2. cases/assemblies/assembly-full-desk.step           (Case Bottom horizontal on desk plane Z = 0.00 mm)
  3. cases/assemblies/curcur40-right-wheel-assembly.step (Right half with Under-Plate Inertia Wheel)
and verify zero B-rep interference + minimum clearances across all components per docs/case_spec.md:
- Left & Right 3D-printed Sealed-Bottom Built-in Tented Tray Bottom Cases
  (with Tilted Floor & Compact Flat-Topped Ø 5.20 mm M2 Heat-Set Insert Bosses at Z = -5.80 mm)
- Direct KiCad 10.0 3D STEP Synchronization (`kicad-cli pcb export step --subst-models`):
    - `curcur40-left.kicad_pcb`    (Z = -5.80 to -4.20 mm + all 268 real 3D component solids)
    - `curcur40-right.kicad_pcb`   (Z = -5.80 to -4.20 mm + all 258 real 3D component solids)
    - `curcur40-pmw3360.kicad_pcb` (Z = -17.60 to -16.00 mm + all 9 real SMD/JST-SH solids)
- Left & Right FR-4 Top Plates (Z = -3.60 to -2.00 mm, retained via 40x Kailh Choc V2 switch snap-fit,
  with 12x Ø 4.40 mm screw-head clearance holes & Right 7.70 x 22.00 mm wheel slot)
- 40x Kailh Choc V2 Low-Profile Keyswitches (21 Left + 19 Right) + 40x Keycaps
- Sunk Trackball Cup placed on Sensor PCB F.Cu at (23.8125, -109.5375, -16.00 mm), Rim at Z = -2.00 mm, 2.00 mm flat ears
- 25mm Trackball Sphere at (23.8125, -109.5375, +2.30 mm) + `Lens_Optical_Ref_Point` (exact 2.40 mm optical gap)
- PMW3360 Sensor IC & LM19-LSI Optical Lens
- 17x Unified M2 Brass Heat-Set Inserts (M2 x L=3.0 x OD=3.2 mm) + 17x Unified M2 x 6.0 mm Screws:
    - 10x Perimeter (5 Left L1-L5 + 5 Right R1-R5, L4/R4 at (±100.50, 21.50), clamping Main PCB F.Cu Z = -4.20 mm
      into Ø 5.20 mm Case Bosses at Z = -5.80 mm; screw heads submerged inside Top Plate Ø 4.40 mm clearance holes)
    - 4x Trackball Cup (TB1-TB4, clamping 2.00 mm Cup Ears + 1.60 mm Sensor PCB into Case Bosses at Z = -17.60 mm)
    - 2x Wheel Cradle (WC1-WC2, clamping Main PCB F.Cu Z = -4.20 mm into Wheel Cradle Bosses at Z = -5.80 mm)
    - 1x Glue-Free Detent Adjuster (in Wheel Rocker South Boss, adjusting Ø 2.0x2.0 mm axial NdFeB magnet gap)
- Under-Plate 1-Piece Integral-Shaft Passive Inertia Scroll Wheel (`steel-flywheel`, `magnet-holder`, `wheel-rocker`, `wheel-cradle`)
"""
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from cadgen import build123d as bd
from cadgen.geometry import overlap_volume, closest_points

WORKSPACE = Path(__file__).resolve().parent.parent
if str(WORKSPACE / "scripts") not in sys.path:
    sys.path.insert(0, str(WORKSPACE / "scripts"))
CASES_DIR = WORKSPACE / "cases"
ASSEMBLIES_DIR = WORKSPACE / "cases" / "assemblies"
KICAD_CLI = Path(os.path.expandvars(r"%LOCALAPPDATA%\Programs\KiCad\10.0\bin\kicad-cli.exe"))

Z_THUMB_BOTTOM = -26.9000
Z_PINKY_BOTTOM = -10.0000
X_THUMB_OUTER = 7.0250
X_PINKY_OUTER = 135.8580
THETA_TENT_DEG = math.degrees(
    math.atan2(Z_PINKY_BOTTOM - Z_THUMB_BOTTOM, X_PINKY_OUTER - X_THUMB_OUTER)
)

LEFT_SWITCHES = [
    (-109.5375, -7.14375),
    (-109.5375, 11.90625),
    (-109.5375, 30.95625),
    (-90.4875, -11.90625),
    (-90.4875, 7.14375),
    (-90.4875, 26.19375),
    (-71.4375, -14.28750),
    (-71.4375, 4.76250),
    (-71.4375, 23.81250),
    (-52.3875, -11.90625),
    (-52.3875, 7.14375),
    (-52.3875, 26.19375),
    (-33.3375, -9.52500),
    (-33.3375, 9.52500),
    (-33.3375, 28.57500),
    (-14.2875, 0.00000),
    (-14.2875, 19.05000),
    (-71.4375, 52.38750),
    (-52.3875, 52.38750),
    (-33.3375, 52.38750),
    (-14.2875, 52.38750),
]

RIGHT_SWITCHES = [
    (109.5375, -7.14375),
    (109.5375, 11.90625),
    (109.5375, 30.95625),
    (90.4875, -11.90625),
    (90.4875, 7.14375),
    (90.4875, 26.19375),
    (71.4375, -14.28750),
    (71.4375, 4.76250),
    (71.4375, 23.81250),
    (52.3875, -11.90625),
    (52.3875, 7.14375),
    (52.3875, 26.19375),
    (33.3375, -9.52500),
    (33.3375, 9.52500),
    (33.3375, 28.57500),
    (14.2875, 19.05000),
    (33.3375, 52.38750),
    (52.3875, 52.38750),
    (71.4375, 52.38750),
]

RIGHT_WHEEL_AXLE_PCB = (14.2875, -2.0000)

RIGHT_WHEEL_CRADLE_HOLES_PCB = [
    ( 6.6375, -9.8000),   # WC1
    (21.2375,  6.0000),   # WC2
]

# (tag, px, py, z_ins_top, z_screw_seat) — 案1A: all 10 perimeter bosses flat Ø 5.20 mm at Z = -5.80 mm
LEFT_PERIMETER_HOLES_PCB = [
    ("L1",    0.0000, -15.0000, -5.81, -4.19),
    ("L2",    0.0000,  18.0000, -5.81, -4.19),
    ("L3", -101.0000, -20.0000, -5.81, -4.19),
    ("L4", -100.5000,  21.5000, -5.81, -4.19),
    ("L5",  -62.0000,  65.1500, -5.81, -4.19),
]

RIGHT_PERIMETER_HOLES_PCB = [
    ("R1",    0.0000, -15.0000, -5.81, -4.19),
    ("R2",    0.0000,  18.0000, -5.81, -4.19),
    ("R3",  101.0000, -20.0000, -5.81, -4.19),
    ("R4",  100.5000,  21.5000, -5.81, -4.19),
    ("R5",   62.0000,  65.1500, -5.81, -4.19),
]

RIGHT_TB_HOLES_PCB = [
    ("TB1", -2.4750, 41.0875, -17.61),
    ("TB2", 21.5250, 41.0875, -17.61),
    ("TB3", -2.4750, 63.6875, -17.61),
    ("TB4", 21.5250, 63.6875, -17.61),
]


def to_step_left(x, y):
    return (x - 14.2875, -(y + 57.1500))


def to_step_right(x, y):
    return (x + 14.2875, -(y + 57.1500))


def aabb_intersects(b1, b2, tol: float = 1e-4) -> bool:
    return not (
        b1.max.X < b2.min.X - tol
        or b2.max.X < b1.min.X - tol
        or b1.max.Y < b2.min.Y - tol
        or b2.max.Y < b1.min.Y - tol
        or b1.max.Z < b2.min.Z - tol
        or b2.max.Z < b1.min.Z - tol
    )


def fast_overlap(s1, b1, s2, b2) -> float:
    if not aabb_intersects(b1, b2):
        return 0.0
    return overlap_volume(s1, s2)


def max_group_overlap(group_a, group_b) -> float:
    if not group_a or not group_b:
        return 0.0
    bbs_a = [(s, s.bounding_box()) for s in group_a]
    bbs_b = [(s, s.bounding_box()) for s in group_b]
    mv = 0.0
    for sa, ba in bbs_a:
        for sb, bb in bbs_b:
            if aabb_intersects(ba, bb):
                ov = overlap_volume(sa, sb)
                if ov > mv:
                    mv = ov
    return mv


def make_filleted_sketch(pts_and_radii):
    with bd.BuildSketch() as sk:
        pts = [(p[0], p[1]) for p in pts_and_radii]
        bd.Polygon(pts)
        for x, y, r in pts_and_radii:
            if r > 0.05:
                v_target = sk.vertices().filter_by(
                    lambda v, tx=x, ty=y: abs(v.X - tx) < 0.2 and abs(v.Y - ty) < 0.2
                )
                if len(v_target) > 0:
                    try:
                        bd.fillet(v_target, radius=r)
                    except Exception:
                        pass
    return sk.sketch


def export_kicad_pcb_solids(
    pcb_rel_path: str,
    offset_xyz: tuple[float, float, float],
    board_label: str,
    comp_prefix: str,
):
    """
    Export a `.kicad_pcb` directly via `kicad-cli pcb export step --subst-models --no-dnp --user-origin 0x0mm`
    and translate into the Global STEP coordinate frame so PCB holes, cutouts, and 3D component models
    are 100% synchronized with KiCad.
    """
    pcb_path = WORKSPACE / pcb_rel_path
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_step = Path(tmp_dir) / f"{pcb_path.stem}.step"
        subprocess.run(
            [
                str(KICAD_CLI),
                "pcb",
                "export",
                "step",
                "--force",
                "--no-dnp",
                "--subst-models",
                "--user-origin",
                "0x0mm",
                "-o",
                str(out_step),
                str(pcb_path),
            ],
            check=True,
            capture_output=True,
        )
        imported = bd.import_step(str(out_step)).moved(bd.Location(offset_xyz))

    solids = sorted(imported.solids(), key=lambda s: s.volume, reverse=True)
    board_solid = solids[0]
    board_solid.label = board_label
    comp_solids = solids[1:]
    for idx, comp in enumerate(comp_solids):
        comp.label = f"{comp_prefix}_3D_{idx+1}"
    return board_solid, comp_solids


def build_top_plate_solid(is_right=True) -> bd.Solid:
    """
    Constructs the FR-4 Top Plate solid (Z = -3.60 to -2.00 mm, thickness 1.60 mm)
    with switch cutouts, Right 7.70 x 22.00 mm wheel slot (R = 1.00 mm),
    and uniform Ø 4.40 mm screw-head clearance holes (案1A: switch-retained plate).
    """
    if is_right:
        pts_plate = [
            ( -5.4625, -24.51250, 1.0),
            (119.2625, -24.51250, 1.0),
            (119.2625,  41.18125, 1.0),
            ( 82.6625,  41.18125, 1.0),
            ( 82.6625,  67.70000, 1.0),
            ( 24.2000,  67.70000, 1.0),
            ( 24.2000,  37.40000, 1.0),
            ( -5.4625,  37.40000, 1.0),
        ]
        pts_step = [(*to_step_right(x, y), r) for x, y, r in pts_plate]
        sw_step = [to_step_right(x, y) for x, y in RIGHT_SWITCHES]
        plate_holes_step = [
            (*to_step_right(x, y), 2.20) for _, x, y, _, _ in RIGHT_PERIMETER_HOLES_PCB
        ] + [(*to_step_right(x, y), 2.20) for x, y in RIGHT_WHEEL_CRADLE_HOLES_PCB]
    else:
        pts_plate = [
            (   5.4625, -24.51250, 1.0),
            (-119.2625, -24.51250, 1.0),
            (-119.2625,  41.18125, 1.0),
            ( -82.6625,  41.18125, 1.0),
            ( -82.6625,  67.70000, 1.0),
            (   5.4625,  67.70000, 1.0),
        ]
        pts_step = [(*to_step_left(x, y), r) for x, y, r in pts_plate]
        sw_step = [to_step_left(x, y) for x, y in LEFT_SWITCHES]
        plate_holes_step = [
            (*to_step_left(x, y), 2.20) for _, x, y, _, _ in LEFT_PERIMETER_HOLES_PCB
        ]

    sk = make_filleted_sketch(pts_step)
    plate = bd.extrude(sk, amount=1.60).moved(bd.Location((0, 0, -3.60)))

    with bd.BuildSketch(bd.Plane.XY.offset(-4.0)) as sk_cuts:
        for sx, sy in sw_step:
            with bd.Locations([(sx, sy)]):
                bd.RectangleRounded(14.0, 14.0, 0.5)
    plate = plate - bd.extrude(sk_cuts.sketch, amount=3.0)

    if is_right:
        wx, wy = to_step_right(*RIGHT_WHEEL_AXLE_PCB)
        with bd.BuildSketch(bd.Plane.XY.offset(-4.0)) as sk_wslot:
            with bd.Locations([(wx, wy)]):
                bd.RectangleRounded(7.70, 22.00, 1.00)
        plate = plate - bd.extrude(sk_wslot.sketch, amount=3.0)

    for hx, hy, r_hole in plate_holes_step:
        plate = plate - bd.Cylinder(
            radius=r_hole,
            height=4.0,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((hx, hy, -4.5)))

    solid = plate.solids()[0]
    solid.label = "Right_Top_Plate" if is_right else "Left_Top_Plate"
    return solid


def make_choc_v2_switch_solid(sx: float, sy: float, label: str) -> bd.Solid:
    """
    Constructs a Kailh Choc V2 (`CPG1353`) low-profile keyswitch housing solid:
      1. Central PCB stem boss: Ø 3.16 mm in Main PCB Ø 3.40 mm NPTH hole (Z = -5.75..-4.18 mm)
      2. Switch plate body: 13.80 x 13.80 mm in Top Plate 14.00 x 14.00 mm cutout (Z = -4.18..-1.99 mm)
      3. Upper housing flange: 14.50 x 14.50 mm above Top Plate Z = -2.00 mm (Z = -1.99..-0.90 mm)
      4. North/South snap latches: 4.40 x 14.48 mm below Top Plate Z = -3.60 mm (Z = -4.18..-3.62 mm)
    """
    stem_boss = bd.Cylinder(
        radius=1.58, height=1.57, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
    ).moved(bd.Location((sx, sy, -5.75)))
    with bd.BuildSketch(bd.Plane.XY.offset(-4.18)) as sk_body:
        with bd.Locations([(sx, sy)]):
            bd.RectangleRounded(13.80, 13.80, 0.45)
    body = bd.extrude(sk_body.sketch, amount=2.19)
    with bd.BuildSketch(bd.Plane.XY.offset(-1.99)) as sk_flange:
        with bd.Locations([(sx, sy)]):
            bd.RectangleRounded(14.50, 14.50, 0.50)
    flange = bd.extrude(sk_flange.sketch, amount=1.09)
    latch = bd.Box(
        4.40, 14.48, 0.56, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
    ).moved(bd.Location((sx, sy, -4.18)))
    sw = (stem_boss + body + flange + latch).solids()[0]
    sw.label = label
    return sw


def make_keycap_solid(sx, sy, label="Keycap") -> bd.Solid:
    with bd.BuildSketch(bd.Plane.XY.offset(-0.80)) as sk:
        with bd.Locations([(sx, sy)]):
            bd.RectangleRounded(17.2, 16.2, 1.5)
    cap = bd.extrude(sk.sketch, amount=4.40).solids()[0]
    cap.label = label
    return cap


def make_insert_and_screw(sx: float, sy: float, z_ins_top: float, z_screw_seat: float, tag: str):
    """
    Build 1x M2 x L=3.0 mm Brass Heat-Set Insert + 1x Top-Down M2 x 6.0 mm Screw
    with nominal clearance radii so B-rep overlap_volume == 0.00000000 mm^3.
    """
    ins = (
        bd.Cylinder(radius=1.41, height=2.98, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
        - bd.Cylinder(radius=1.02, height=3.20, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).moved(
            bd.Location((0, 0, 0.10))
        )
    ).moved(bd.Location((sx, sy, z_ins_top))).solids()[0]
    ins.label = f"HeatSet_Insert_M2_{tag}"

    head = bd.Cylinder(
        radius=1.90, height=1.20, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
    ).moved(bd.Location((sx, sy, z_screw_seat)))
    shank = bd.Cylinder(
        radius=0.98, height=6.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)
    ).moved(bd.Location((sx, sy, z_screw_seat)))
    scr = (head + shank).solids()[0]
    scr.label = f"Top_Screw_M2x6_{tag}"
    return ins, scr


def transform_to_desk(shape, is_right: bool):
    lbl = getattr(shape, "label", "")
    children = getattr(shape, "children", None)
    if children:
        res = bd.Compound(children=[transform_to_desk(ch, is_right) for ch in children])
        res.label = lbl
        return res
    pivot_x = X_PINKY_OUTER if is_right else -X_PINKY_OUTER
    pivot_z = Z_PINKY_BOTTOM
    rot_y = THETA_TENT_DEG if is_right else -THETA_TENT_DEG
    loc = bd.Pos(pivot_x, 0.0, 0.0) * bd.Rot(0, rot_y, 0) * bd.Pos(-pivot_x, 0.0, -pivot_z)
    moved_wrapped = shape.wrapped.Moved(loc.wrapped)
    if isinstance(shape, bd.Solid):
        res = bd.Solid(moved_wrapped)
    elif isinstance(shape, bd.Face):
        res = bd.Face(moved_wrapped)
    else:
        res = shape.moved(loc)
    res.label = lbl
    return res


def main():
    from generate_inertia_wheel import assemble_wheel_parts_global, verify_6dof_constraints, CLICK_PRESS_DEG
    from generate_cases import verify_case_wall_thickness_and_gaps
    from generate_trackball_cup import verify_cup_wall_thickness_and_gaps

    print("=== Building & Verifying curcur40 Full Assembly (Direct KiCad 3D STEP Sync + Switch-Retained Plate) ===")

    left_case = bd.import_step(str(CASES_DIR / "left.step")).solids()[0]
    left_case.label = "Left_Case"
    right_case = bd.import_step(str(CASES_DIR / "right.step")).solids()[0]
    right_case.label = "Right_Case"

    print("Exporting 3D STEP boards & SMD/THT component models directly from KiCad 10.0...")
    left_pcb, left_kicad_comps = export_kicad_pcb_solids(
        "pcbs/left/curcur40-left.kicad_pcb",
        (-14.2875, -57.1500, -5.8000),
        "Left_Main_PCB",
        "Left_PCB",
    )
    right_pcb, right_kicad_comps = export_kicad_pcb_solids(
        "pcbs/right/curcur40-right.kicad_pcb",
        (14.2875, -57.1500, -5.8000),
        "Right_Main_PCB",
        "Right_PCB",
    )
    sensor_pcb_global, pmw_kicad_comps = export_kicad_pcb_solids(
        "pcbs/pmw3360/curcur40-pmw3360.kicad_pcb",
        (14.2875, -57.1500, -17.6000),
        "PMW3360_Sensor_PCB",
        "Sensor_PCB",
    )
    print(
        f"  Loaded KiCad STEP solids: Left={1 + len(left_kicad_comps)} "
        f"(1 PCB + {len(left_kicad_comps)} comps), "
        f"Right={1 + len(right_kicad_comps)} (1 PCB + {len(right_kicad_comps)} comps), "
        f"PMW3360={1 + len(pmw_kicad_comps)} (1 PCB + {len(pmw_kicad_comps)} comps)"
    )

    # Identify key semantic KiCad component solids by global AABB position for named clearance & click checks
    sw_click_x, sw_click_y = to_step_right(-2.0125, -2.0000)
    rexsw1_plungers = [
        c
        for c in right_kicad_comps
        if math.hypot(c.bounding_box().center().X - sw_click_x, c.bounding_box().center().Y - sw_click_y) < 1.0
        and c.bounding_box().min.Z < -9.50
    ]
    assert len(rexsw1_plungers) == 1, f"Expected 1 rEXSW1 plunger in KiCad STEP, got {len(rexsw1_plungers)}"
    rexsw1_plunger = rexsw1_plungers[0]
    rexsw1_plunger.label = "Right_PCB_rEXSW1_Plunger"

    rj3_x, rj3_y = to_step_right(46.5000, 63.0000)
    rj3_solids = [
        c
        for c in right_kicad_comps
        if math.hypot(c.bounding_box().center().X - rj3_x, c.bounding_box().center().Y - rj3_y) < 4.5
        and c.bounding_box().min.Z < -7.50
    ]
    assert len(rj3_solids) >= 1, "Failed to locate rJ3 JST-SH in Right KiCad STEP"
    for idx, c in enumerate(rj3_solids):
        c.label = f"Right_PCB_rJ3_JST_SH_{idx+1}"

    j1_x, j1_y = to_step_right(19.2000, 52.3875)
    j1_solids = [
        c
        for c in pmw_kicad_comps
        if math.hypot(c.bounding_box().center().X - j1_x, c.bounding_box().center().Y - j1_y) < 4.5
        and c.bounding_box().min.Z < -19.00
    ]
    assert len(j1_solids) >= 1, "Failed to locate J1 JST-SH in PMW3360 KiCad STEP"
    for idx, c in enumerate(j1_solids):
        c.label = f"Sensor_PCB_J1_JST_SH_{idx+1}"

    def find_usbc_solids(comps, is_right: bool):
        sgn = 1.0 if is_right else -1.0
        targets = [(sgn * 26.5750, -38.5925), (sgn * 14.7800, -86.6500)]
        found = []
        for c in comps:
            bb = c.bounding_box()
            if max(bb.size.X, bb.size.Y) > 5.0:
                cx, cy = bb.center().X, bb.center().Y
                if any(math.hypot(cx - tx, cy - ty) < 4.0 for tx, ty in targets):
                    found.append(c)
        return found

    left_conn_solids = find_usbc_solids(left_kicad_comps, is_right=False)
    right_conn_solids = find_usbc_solids(right_kicad_comps, is_right=True)
    assert len(left_conn_solids) >= 2 and len(right_conn_solids) >= 2, (
        f"Expected USB-C solids in KiCad STEP, got L={len(left_conn_solids)}, R={len(right_conn_solids)}"
    )

    left_plate = build_top_plate_solid(is_right=False)
    right_plate = build_top_plate_solid(is_right=True)

    tb_cx, tb_cy, tb_cz = 23.8125, -109.5375, -16.0000
    cup_local = bd.import_step(str(CASES_DIR / "trackball-cup.step"))
    cup_global = cup_local.moved(bd.Location((tb_cx, tb_cy, tb_cz))).solids()[0]
    cup_global.label = "Trackball_Cup"

    ball_global = (
        bd.Sphere(radius=12.50)
        .moved(bd.Location((tb_cx, tb_cy, tb_cz + 18.30)))
        .solids()[0]
    )
    ball_global.label = "Trackball_25mm"

    asm_parts = bd.import_step(str(ASSEMBLIES_DIR / "pmw3360-lens-pcb-assembly.step"))
    sensor_local, lens_local = None, None
    for s in asm_parts.solids():
        bb = s.bounding_box()
        if bb.min.Z < -3.5:
            sensor_local = s
        elif bb.max.Z > 3.0:
            lens_local = s
    sensor_global = sensor_local.moved(bd.Location((tb_cx, tb_cy, tb_cz))).solids()[0]
    sensor_global.label = "PMW3360_Sensor"
    lens_global = lens_local.moved(bd.Location((tb_cx, tb_cy, tb_cz))).solids()[0]
    lens_global.label = "LM19_Lens"

    ref_point_global = bd.Pos(tb_cx, tb_cy, tb_cz + 3.40) * bd.Circle(0.35).face()
    ref_point_global.label = "Lens_Optical_Ref_Point"

    # Under-Plate 1-Piece Integral-Shaft Passive Inertia Scroll Wheel (Rest & Clicked poses)
    wheel_mov_rest, wheel_stat, wheel_cradle_screws = assemble_wheel_parts_global(click_deg=0.0)
    wheel_mov_click, _, _ = assemble_wheel_parts_global(click_deg=CLICK_PRESS_DEG)
    wheel_solids = wheel_mov_rest + wheel_stat

    # 14x Case Heat-Set Inserts + 14x Top-Down M2 x 6.0 mm Screws (plus 3x in wheel assembly = 17x total)
    inserts = []
    top_screws = []
    left_fasteners = []
    right_fasteners = []

    for tag, px, py, z_ins_top, z_scr_seat in LEFT_PERIMETER_HOLES_PCB:
        sx, sy = to_step_left(px, py)
        ins, scr = make_insert_and_screw(sx, sy, z_ins_top, z_scr_seat, tag)
        inserts.append(ins)
        top_screws.append(scr)
        left_fasteners.extend([ins, scr])

    for tag, px, py, z_ins_top, z_scr_seat in RIGHT_PERIMETER_HOLES_PCB:
        sx, sy = to_step_right(px, py)
        ins, scr = make_insert_and_screw(sx, sy, z_ins_top, z_scr_seat, tag)
        inserts.append(ins)
        top_screws.append(scr)
        right_fasteners.extend([ins, scr])

    for tag, px, py, z_ins_top in RIGHT_TB_HOLES_PCB:
        sx, sy = to_step_right(px, py)
        ins, scr = make_insert_and_screw(sx, sy, z_ins_top, -13.99, tag)
        inserts.append(ins)
        top_screws.append(scr)
        right_fasteners.extend([ins, scr])

    left_switches = [
        make_choc_v2_switch_solid(*to_step_left(kx, ky), f"Left_ChocV2_Switch_{idx+1}")
        for idx, (kx, ky) in enumerate(LEFT_SWITCHES)
    ]
    right_switches = [
        make_choc_v2_switch_solid(*to_step_right(kx, ky), f"Right_ChocV2_Switch_{idx+1}")
        for idx, (kx, ky) in enumerate(RIGHT_SWITCHES)
    ]
    all_switches = left_switches + right_switches

    left_keycaps = [
        make_keycap_solid(*to_step_left(kx, ky), f"Left_Keycap_{idx+1}")
        for idx, (kx, ky) in enumerate(LEFT_SWITCHES)
    ]
    right_keycaps = [
        make_keycap_solid(*to_step_right(kx, ky), f"Right_Keycap_{idx+1}")
        for idx, (kx, ky) in enumerate(RIGHT_SWITCHES)
    ]
    keycaps = left_keycaps + right_keycaps

    all_right_kicad_comps = right_kicad_comps + pmw_kicad_comps
    all_fasteners = inserts + top_screws + wheel_cradle_screws

    print("\n--- Interference Verification (All KiCad 3D Solids + Cases + Plates + Switches + Wheel) ---")
    ov_cup_case = overlap_volume(cup_global, right_case)
    ov_cup_plate = overlap_volume(cup_global, right_plate)
    ov_cup_rpcb = overlap_volume(cup_global, right_pcb)
    ov_cup_spcb = overlap_volume(cup_global, sensor_pcb_global)
    ov_cup_ball = overlap_volume(cup_global, ball_global)
    ov_cup_lens = overlap_volume(cup_global, lens_global)
    ov_sensor_case = overlap_volume(sensor_global, right_case)
    ov_sensor_spcb = overlap_volume(sensor_global, sensor_pcb_global)
    ov_lens_spcb = overlap_volume(lens_global, sensor_pcb_global)
    ov_spcb_case = overlap_volume(sensor_pcb_global, right_case)
    ov_spcb_rpcb = overlap_volume(sensor_pcb_global, right_pcb)
    ov_rpcb_case = overlap_volume(right_pcb, right_case)
    ov_lpcb_case = overlap_volume(left_pcb, left_case)
    dist_opt = closest_points(ball_global, ref_point_global).distance

    wheel_check_group = wheel_solids + wheel_cradle_screws
    ov_wheel_internal = 0.0
    for i in range(len(wheel_check_group)):
        for j in range(i + 1, len(wheel_check_group)):
            ov_wheel_internal = max(
                ov_wheel_internal,
                overlap_volume(wheel_check_group[i], wheel_check_group[j]),
            )
    ov_wheel_case = max_group_overlap(wheel_check_group, [right_case])
    ov_wheel_plate = max_group_overlap(wheel_check_group, [right_plate])
    ov_wheel_pcb = max_group_overlap(wheel_check_group, [right_pcb])
    ov_wheel_usbc = max_group_overlap(wheel_check_group, right_conn_solids)
    ov_wheel_fasteners = max_group_overlap(wheel_check_group, inserts + top_screws)
    ov_wheel_switches = max_group_overlap(wheel_check_group, right_switches)
    ov_wheel_keycaps = max_group_overlap(wheel_check_group, right_keycaps)

    non_plunger_right_comps = [c for c in all_right_kicad_comps if c is not rexsw1_plunger]
    ov_click_plunger = max_group_overlap(wheel_mov_click, [rexsw1_plunger])
    ov_click_env = max(
        max_group_overlap(wheel_mov_click, [right_case, right_plate, right_pcb]),
        max_group_overlap(wheel_mov_click, right_switches + right_keycaps),
        max_group_overlap(wheel_mov_click, non_plunger_right_comps),
    )

    ov_kicad_case = max(
        max_group_overlap(left_kicad_comps, [left_case]),
        max_group_overlap(all_right_kicad_comps, [right_case]),
    )
    ov_kicad_cup_opt = max_group_overlap(
        all_right_kicad_comps, [cup_global, sensor_global, lens_global]
    )
    ov_kicad_plate = max(
        max_group_overlap(left_kicad_comps, [left_plate]),
        max_group_overlap(all_right_kicad_comps, [right_plate]),
    )
    ov_kicad_wheel = max_group_overlap(all_right_kicad_comps, wheel_check_group)
    ov_kicad_fasteners = max(
        max_group_overlap(left_kicad_comps, left_fasteners),
        max_group_overlap(all_right_kicad_comps, right_fasteners + wheel_cradle_screws),
    )
    ov_kicad_switches = max(
        max_group_overlap(left_kicad_comps, left_switches),
        max_group_overlap(all_right_kicad_comps, right_switches),
    )

    ov_sw_plate_pcb_case_cap = max(
        max_group_overlap(left_switches, [left_plate, left_pcb, left_case] + left_keycaps + left_fasteners),
        max_group_overlap(
            right_switches,
            [right_plate, right_pcb, right_case, cup_global] + right_keycaps + right_fasteners + wheel_cradle_screws,
        ),
    )

    max_ins_ov = max_group_overlap(
        inserts,
        [right_case, left_case, right_pcb, left_pcb, sensor_pcb_global, cup_global, right_plate, left_plate],
    )
    max_tscr_ov = max_group_overlap(
        top_screws + wheel_cradle_screws,
        [right_case, left_case, right_plate, left_plate, cup_global, right_pcb, left_pcb, sensor_pcb_global],
    )
    max_ins_scr_ov = max(
        overlap_volume(ins, scr) for ins, scr in zip(inserts, top_screws)
    )
    max_cap_screw_ov = max_group_overlap(top_screws + wheel_cradle_screws, keycaps)

    print(f"Cup vs Right Case:         {ov_cup_case:.8f} mm^3")
    print(f"Cup vs Right Plate:        {ov_cup_plate:.8f} mm^3")
    print(f"Cup vs Right Main PCB:     {ov_cup_rpcb:.8f} mm^3")
    print(f"Cup vs Sensor PCB:         {ov_cup_spcb:.8f} mm^3")
    print(f"Cup vs 25mm Ball:          {ov_cup_ball:.8f} mm^3")
    print(f"Cup vs LM19 Lens:          {ov_cup_lens:.8f} mm^3")
    print(f"Sensor vs Right Case:      {ov_sensor_case:.8f} mm^3")
    print(f"Sensor PCB vs Case:        {ov_spcb_case:.8f} mm^3")
    print(f"Right PCB vs Case:         {ov_rpcb_case:.8f} mm^3")
    print(f"Left PCB vs Case:          {ov_lpcb_case:.8f} mm^3")
    print(f"Wheel Internal Pairwise:   {ov_wheel_internal:.8f} mm^3")
    print(f"Wheel vs Right Case:       {ov_wheel_case:.8f} mm^3")
    print(f"Wheel vs Right Plate:      {ov_wheel_plate:.8f} mm^3")
    print(f"Wheel vs Right PCB:        {ov_wheel_pcb:.8f} mm^3")
    print(f"Wheel vs USB-C Conns:      {ov_wheel_usbc:.8f} mm^3")
    print(f"Wheel vs Fasteners:        {ov_wheel_fasteners:.8f} mm^3")
    print(f"Wheel vs Right Switches:   {ov_wheel_switches:.8f} mm^3")
    print(f"Wheel vs Right Keycaps:    {ov_wheel_keycaps:.8f} mm^3")
    print(f"Wheel Clicked Envelope:    {ov_click_env:.8f} mm^3 (rEXSW1 plunger stroke={ov_click_plunger:.4f} mm^3)")
    print(f"KiCad 3D Comps vs Cases:   {ov_kicad_case:.8f} mm^3")
    print(f"KiCad 3D Comps vs Cup/Opt: {ov_kicad_cup_opt:.8f} mm^3")
    print(f"KiCad 3D Comps vs Plates:  {ov_kicad_plate:.8f} mm^3")
    print(f"KiCad 3D Comps vs Wheel:   {ov_kicad_wheel:.8f} mm^3")
    print(f"KiCad 3D Comps vs Screws:  {ov_kicad_fasteners:.8f} mm^3")
    print(f"KiCad 3D Comps vs ChocV2:  {ov_kicad_switches:.8f} mm^3")
    print(f"ChocV2 vs Plate/PCB/Caps:  {ov_sw_plate_pcb_case_cap:.8f} mm^3")
    print(f"Max Insert Overlap:        {max_ins_ov:.8f} mm^3")
    print(f"Max Top Screw Overlap:     {max_tscr_ov:.8f} mm^3")
    print(f"Max Insert-Screw Overlap:  {max_ins_scr_ov:.8f} mm^3")
    print(f"Max Screw vs Keycaps:      {max_cap_screw_ov:.8f} mm^3")
    print(f"Optical Distance (Ball Bottom Z=-10.20 to Ref Point Z=-12.60): {dist_opt:.6f} mm")

    for name, val in [
        ("ov_cup_case", ov_cup_case),
        ("ov_cup_plate", ov_cup_plate),
        ("ov_cup_rpcb", ov_cup_rpcb),
        ("ov_cup_spcb", ov_cup_spcb),
        ("ov_cup_ball", ov_cup_ball),
        ("ov_cup_lens", ov_cup_lens),
        ("ov_sensor_case", ov_sensor_case),
        ("ov_sensor_spcb", ov_sensor_spcb),
        ("ov_lens_spcb", ov_lens_spcb),
        ("ov_spcb_case", ov_spcb_case),
        ("ov_spcb_rpcb", ov_spcb_rpcb),
        ("ov_rpcb_case", ov_rpcb_case),
        ("ov_lpcb_case", ov_lpcb_case),
        ("ov_wheel_internal", ov_wheel_internal),
        ("ov_wheel_case", ov_wheel_case),
        ("ov_wheel_plate", ov_wheel_plate),
        ("ov_wheel_pcb", ov_wheel_pcb),
        ("ov_wheel_usbc", ov_wheel_usbc),
        ("ov_wheel_fasteners", ov_wheel_fasteners),
        ("ov_wheel_switches", ov_wheel_switches),
        ("ov_wheel_keycaps", ov_wheel_keycaps),
        ("ov_click_env", ov_click_env),
        ("ov_kicad_case", ov_kicad_case),
        ("ov_kicad_cup_opt", ov_kicad_cup_opt),
        ("ov_kicad_plate", ov_kicad_plate),
        ("ov_kicad_wheel", ov_kicad_wheel),
        ("ov_kicad_fasteners", ov_kicad_fasteners),
        ("ov_kicad_switches", ov_kicad_switches),
        ("ov_sw_plate_pcb_case_cap", ov_sw_plate_pcb_case_cap),
        ("max_ins_ov", max_ins_ov),
        ("max_tscr_ov", max_tscr_ov),
        ("max_ins_scr_ov", max_ins_scr_ov),
        ("max_cap_screw_ov", max_cap_screw_ov),
    ]:
        assert val == 0.0, f"{name} non-zero overlap: {val:.8f} mm^3"
    assert ov_click_plunger > 0.10, f"Wheel click failed to actuate rEXSW1 plunger: {ov_click_plunger:.6f} mm^3"
    assert abs(dist_opt - 2.40) < 1e-6

    print("\n--- Micro-Gap & Wall-Thickness (<0.80mm) Verification ---")
    verify_case_wall_thickness_and_gaps(left_case, is_right=False)
    verify_case_wall_thickness_and_gaps(right_case, is_right=True)
    verify_cup_wall_thickness_and_gaps(cup_local.solids()[0])

    clr_j1_case = min(closest_points(s, right_case).distance for s in j1_solids)
    clr_rj3_case = min(closest_points(s, right_case).distance for s in rj3_solids)
    clr_sensor_case = closest_points(sensor_global, right_case).distance

    excluded_right = set(id(s) for s in (j1_solids + rj3_solids + right_conn_solids))
    excluded_left = set(id(s) for s in left_conn_solids)
    right_smds_cmp = bd.Compound(children=[s for s in all_right_kicad_comps if id(s) not in excluded_right])
    left_smds_cmp = bd.Compound(children=[s for s in left_kicad_comps if id(s) not in excluded_left])
    clr_smds_case = min(
        closest_points(right_smds_cmp, right_case).distance,
        closest_points(left_smds_cmp, left_case).distance,
    )
    clr_ball_cup = closest_points(ball_global, cup_global).distance
    clr_cup_plate = closest_points(cup_global, right_plate).distance
    clr_cup_rpcb = closest_points(cup_global, right_pcb).distance
    clr_wheel_mov_case = min(
        min(closest_points(s, right_case).distance for s in wheel_mov_rest),
        min(closest_points(s, right_case).distance for s in wheel_mov_click),
    )
    clr_wheel_cradle_case = min(closest_points(s, right_case).distance for s in wheel_stat)
    clr_wheel_mov_plate = min(
        min(closest_points(s, right_plate).distance for s in wheel_mov_rest),
        min(closest_points(s, right_plate).distance for s in wheel_mov_click),
    )
    clr_wheel_mov_pcb = min(
        closest_points(s, right_pcb).distance
        for s in (wheel_mov_rest + wheel_mov_click)
    )
    clr_wheel_usbc = min(
        closest_points(s, u).distance for s in wheel_solids for u in right_conn_solids
    )
    clr_wheel_keycaps = min(
        closest_points(s, kc).distance for s in wheel_solids for kc in right_keycaps
    )
    clr_usbc_case = min(
        min(closest_points(s, left_case).distance for s in left_conn_solids),
        min(closest_points(s, right_case).distance for s in right_conn_solids),
    )
    clr_usbc_plate = min(
        min(closest_points(s, left_plate).distance for s in left_conn_solids),
        min(closest_points(s, right_plate).distance for s in right_conn_solids),
    )

    print(f"Min Clearance Sensor J1 vs Right Case:      {clr_j1_case:.4f} mm (req >= 0.05 mm)")
    print(f"Min Clearance Main rJ3 vs Right Case:       {clr_rj3_case:.4f} mm (req >= 0.50 mm)")
    print(f"Min Clearance PMW3360 Sensor vs Right Case: {clr_sensor_case:.4f} mm (req >= 1.50 mm)")
    print(f"Min Clearance All KiCad SMDs/SWs vs Cases:  {clr_smds_case:.4f} mm (req >= 0.30 mm)")
    print(f"Min Clearance 25mm Ball vs Trackball Cup:   {clr_ball_cup:.4f} mm (req >= 0.30 mm)")
    print(f"Min Clearance Trackball Cup vs Right Plate: {clr_cup_plate:.4f} mm (req >= 0.25 mm)")
    print(f"Min Clearance Trackball Cup vs Right PCB:   {clr_cup_rpcb:.4f} mm (req >= 0.25 mm)")
    print(f"Min Clearance Wheel Moving vs Right Case:   {clr_wheel_mov_case:.4f} mm (req >= 0.40 mm)")
    print(f"Min Clearance Wheel Cradle vs Right Case:   {clr_wheel_cradle_case:.4f} mm (req >= 0.60 mm)")
    print(f"Min Clearance Wheel Moving vs Right Plate:  {clr_wheel_mov_plate:.4f} mm (req >= 0.30 mm)")
    print(f"Min Clearance Wheel Moving vs Right PCB:    {clr_wheel_mov_pcb:.4f} mm (req >= 0.30 mm)")
    print(f"Min Clearance Wheel Module vs USB-C Conns:  {clr_wheel_usbc:.4f} mm (req >= 1.00 mm)")
    print(f"Min Clearance Wheel Module vs Right Keycaps:{clr_wheel_keycaps:.4f} mm (req >= 1.00 mm)")
    print(f"Min Clearance Host/Split USBC vs Cases:     {clr_usbc_case:.4f} mm (req >= 0.50 mm)")
    print(f"Min Clearance Host/Split USBC vs Plates:    {clr_usbc_plate:.4f} mm (req >= 0.35 mm)")

    assert clr_j1_case >= 0.05, f"J1 too close to Right Case: {clr_j1_case:.4f} mm"
    assert clr_rj3_case >= 0.50, f"rJ3 too close to Right Case: {clr_rj3_case:.4f} mm"
    assert clr_sensor_case >= 1.50, f"PMW3360 too close to Right Case: {clr_sensor_case:.4f} mm"
    assert clr_smds_case >= 0.30, f"KiCad SMDs/SWs too close to Case: {clr_smds_case:.4f} mm"
    assert clr_ball_cup >= 0.30, f"25mm Ball too close to Cup: {clr_ball_cup:.4f} mm"
    assert clr_cup_plate >= 0.25, f"Cup too close to Right Plate: {clr_cup_plate:.4f} mm"
    assert clr_cup_rpcb >= 0.25, f"Cup too close to Right PCB: {clr_cup_rpcb:.4f} mm"
    assert clr_wheel_mov_case >= 0.40, f"Wheel moving parts too close to Right Case: {clr_wheel_mov_case:.4f} mm"
    assert clr_wheel_cradle_case >= 0.60, f"Wheel Cradle too close to Right Case: {clr_wheel_cradle_case:.4f} mm"
    assert clr_wheel_mov_plate >= 0.30, f"Wheel moving parts too close to Plate: {clr_wheel_mov_plate:.4f} mm"
    assert clr_wheel_mov_pcb >= 0.30, f"Wheel moving parts too close to PCB: {clr_wheel_mov_pcb:.4f} mm"
    assert clr_wheel_usbc >= 1.00, f"Wheel Module too close to USB-C: {clr_wheel_usbc:.4f} mm"
    assert clr_wheel_keycaps >= 1.00, f"Wheel Module too close to Keycaps: {clr_wheel_keycaps:.4f} mm"
    assert clr_usbc_case >= 0.50, f"USB-C too close to Case: {clr_usbc_case:.4f} mm"
    assert clr_usbc_plate >= 0.35, f"USB-C too close to Top Plate: {clr_usbc_plate:.4f} mm"

    print("\n--- Full-Assembly 6-DOF Retention Verification (Switch-Retained Plate + Boss-Clamped PCBs) ---")
    verify_6dof_constraints()
    for part, anchors, d_xy, d_z, lock_desc in (
        (left_plate, left_switches, 0.15, 0.05, "21x Kailh Choc V2 switch snap-fit"),
        (right_plate, right_switches, 0.15, 0.05, "19x Kailh Choc V2 switch snap-fit"),
        (left_pcb, [left_case] + left_fasteners, 0.25, 0.12, "5x Ø 5.20 mm bosses & M2x6 screws"),
        (right_pcb, [right_case] + right_fasteners + wheel_cradle_screws + wheel_stat, 0.25, 0.12, "5x Ø 5.20 mm bosses + 2x cradle bosses & M2x6 screws"),
        (sensor_pcb_global, [right_case, cup_global] + right_fasteners, 0.28, 0.12, "4x TB bosses + Trackball Cup & M2x6 screws"),
        (cup_global, [sensor_pcb_global] + right_fasteners, 0.28, 0.12, "Sensor PCB + 4x TB M2x6 screws"),
    ):
        for axis_tag, vec in (
            ("+X", (d_xy, 0.0, 0.0)),
            ("-X", (-d_xy, 0.0, 0.0)),
            ("+Y", (0.0, d_xy, 0.0)),
            ("-Y", (0.0, -d_xy, 0.0)),
            ("+Z", (0.0, 0.0, d_z)),
            ("-Z", (0.0, 0.0, -d_z)),
        ):
            pm = part.moved(bd.Location(vec))
            ov_tot = max_group_overlap([pm], anchors)
            assert ov_tot > 0.0, f"[6-DOF FAIL] {part.label} NOT mechanically locked along {axis_tag}!"
        print(f"  [PASS] {part.label}: mechanically locked in ±X, ±Y, ±Z by {lock_desc}")

    left_kicad_grp = bd.Compound(children=left_kicad_comps)
    left_kicad_grp.label = "Left_PCB_KiCad_3D_Components"
    right_kicad_grp = bd.Compound(children=right_kicad_comps)
    right_kicad_grp.label = "Right_PCB_KiCad_3D_Components"
    pmw_kicad_grp = bd.Compound(children=pmw_kicad_comps)
    pmw_kicad_grp.label = "Sensor_PCB_KiCad_3D_Components"
    left_sw_grp = bd.Compound(children=left_switches)
    left_sw_grp.label = "Left_Choc_V2_Switches"
    right_sw_grp = bd.Compound(children=right_switches)
    right_sw_grp.label = "Right_Choc_V2_Switches"

    all_parts = (
        [
            left_case,
            right_case,
            left_pcb,
            right_pcb,
            sensor_pcb_global,
            left_kicad_grp,
            right_kicad_grp,
            pmw_kicad_grp,
            left_plate,
            right_plate,
            left_sw_grp,
            right_sw_grp,
            cup_global,
            ball_global,
            lens_global,
            sensor_global,
            ref_point_global,
        ]
        + wheel_solids
        + wheel_cradle_screws
        + inserts
        + top_screws
        + keycaps
    )

    ASSEMBLIES_DIR.mkdir(parents=True, exist_ok=True)
    asm_full = bd.Compound(children=all_parts)
    asm_full.label = "curcur40_Full_Assembly"
    out_step = ASSEMBLIES_DIR / "assembly-full.step"
    bd.export_step(asm_full, str(out_step))
    total_solids = len(asm_full.solids())
    print(
        f"\nSuccessfully exported {out_step} ({len(all_parts)} top-level groups, "
        f"{total_solids} solids + 1 optical ref face, valid={asm_full.is_valid})"
    )

    left_group = [left_case, left_pcb, left_kicad_grp, left_plate, left_sw_grp] + left_fasteners + left_keycaps
    right_group = (
        [
            right_case,
            right_pcb,
            sensor_pcb_global,
            right_kicad_grp,
            pmw_kicad_grp,
            right_plate,
            right_sw_grp,
            cup_global,
            ball_global,
            lens_global,
            sensor_global,
            ref_point_global,
        ]
        + wheel_solids
        + wheel_cradle_screws
        + right_fasteners
        + right_keycaps
    )

    # Also export Right Half + Inertia Wheel standalone verification assembly
    asm_right = bd.Compound(children=right_group)
    asm_right.label = "curcur40_Right_Wheel_Assembly"
    out_right_step = ASSEMBLIES_DIR / "curcur40-right-wheel-assembly.step"
    bd.export_step(asm_right, str(out_right_step))
    print(
        f"Successfully exported {out_right_step} ({len(right_group)} top-level groups, "
        f"{len(asm_right.solids())} solids + 1 optical ref face)"
    )

    desk_parts = [transform_to_desk(p, False) for p in left_group] + [
        transform_to_desk(p, True) for p in right_group
    ]
    desk_ball = [p for p in desk_parts if getattr(p, "label", "") == "Trackball_25mm"][0]
    desk_ref = [p for p in desk_parts if getattr(p, "label", "") == "Lens_Optical_Ref_Point"][0]
    assert abs(closest_points(desk_ball, desk_ref).distance - 2.40) < 1e-5

    asm_desk = bd.Compound(children=desk_parts)
    asm_desk.label = "curcur40_Full_Assembly_Desk"
    out_desk_step = ASSEMBLIES_DIR / "assembly-full-desk.step"
    bd.export_step(asm_desk, str(out_desk_step))
    bb_desk_l = desk_parts[0].bounding_box()
    bb_desk_r = desk_parts[len(left_group)].bounding_box()
    print(
        f"Successfully exported {out_desk_step} ({len(desk_parts)} top-level groups, "
        f"{len(asm_desk.solids())} solids + 1 optical ref face, valid={asm_desk.is_valid}, "
        f"Left Case Z=[{bb_desk_l.min.Z:.4f}, {bb_desk_l.max.Z:.4f}], "
        f"Right Case Z=[{bb_desk_r.min.Z:.4f}, {bb_desk_r.max.Z:.4f}])"
    )


if __name__ == "__main__":
    main()
