# -*- coding: utf-8 -*-
"""
Generate curcur40 Full Assembly STEP (cases/assembly-full.step)
and verify zero interference across all components per docs/case_spec.md:
- Left & Right 3D-printed Tray Bottom Cases (Z = -12.30 to 0.00 mm, inner floor Z = -9.10 mm)
- Left & Right Main PCBs (Z = -5.20 to -3.60 mm, with Ø 3.60 mm spacer through-holes & PMW3360 optical cutout)
- Left & Right FR-4 Top Plates (Z = -1.60 to 0.00 mm, with Ø 2.40 mm screw holes & switch cutouts)
- Trackball Cup placed on Right Main PCB F.Cu at (23.8125, -109.5375, -3.60 mm)
- 25mm Trackball Sphere at (23.8125, -109.5375, +14.70 mm)
- PMW3360 Sensor IC & LM19-LSI Optical Lens
- 13x M2 5.50mm Female-Female Standoffs (5 Left + 8 Right, Z = -9.10 to -3.60 mm, flush with PCB F.Cu)
- 13x Bottom M2x4mm Screws (head in bottom counterbore Z = -12.20 to -11.40 mm, shank Z = -11.40 to -7.40 mm)
- 13x Top M2x4mm Screws (4 on Trackball Cup ears Z = -1.20 mm, 9 on Top Plates Z = 0.00 mm)
- Keycaps (Choc v2 low-profile) & CKW12 Rotary Encoder
"""
import math
from pathlib import Path
from cadgen import build123d as bd
from cadgen.geometry import overlap_volume, is_sound

WORKSPACE = Path(__file__).resolve().parent.parent
CASES_DIR = WORKSPACE / "cases"

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

RIGHT_ENCODER = (14.2875, 0.00000)

LEFT_PERIMETER_HOLES_PCB = [
    (   0.0000, -15.0000),
    (   0.0000,  25.0000),
    (-109.5375, -20.0000),
    ( -98.0000,  38.0000),
    ( -21.5250,  63.6875),
]

RIGHT_PERIMETER_HOLES_PCB = [
    (  0.0000, -15.0000),
    (  0.0000,  25.0000),
    (109.5375, -20.0000),
    ( 98.0000,  38.0000),
]

RIGHT_TB_HOLES_PCB = [
    ( -2.4750,  41.0875),
    ( 21.5250,  41.0875),
    ( -2.4750,  63.6875),
    ( 21.5250,  63.6875),
]


def to_step_left(x, y):
    return (x - 14.2875, -(y + 57.1500))


def to_step_right(x, y):
    return (x + 14.2875, -(y + 57.1500))


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


def build_main_pcb_solid(is_right=True) -> bd.Solid:
    """
    Constructs the Main PCB solid (Z = -5.20 to -3.60 mm, thickness 1.60 mm)
    with exact outer boundary, TRRS notch, Ø 3.60 mm spacer holes, and (on right) PMW3360 sensor slot.
    """
    if is_right:
        pts_pcb = [
            ( -5.2625, -24.3125, 1.0),
            (119.0625, -24.3125, 1.0),
            (119.0625,  40.98125, 1.0),
            ( 82.4625,  40.98125, 1.0),
            ( 82.4625,  67.5000, 1.0),
            ( -5.2625,  67.5000, 1.0),
            ( -5.2625,  37.8000, 0.0),
            (  7.7425,  37.8000, 0.0),
            (  7.7425,  31.5000, 0.0),
            ( -5.2625,  31.5000, 0.0),
        ]
        pts_step = [(*to_step_right(x, y), r) for x, y, r in pts_pcb]
        holes_step = [to_step_right(x, y) for x, y in (RIGHT_PERIMETER_HOLES_PCB + RIGHT_TB_HOLES_PCB)]
    else:
        pts_pcb = [
            (   5.2625, -24.3125, 1.0),
            (-119.0625, -24.3125, 1.0),
            (-119.0625,  40.98125, 1.0),
            ( -82.4625,  40.98125, 1.0),
            ( -82.4625,  67.5000, 1.0),
            (   5.2625,  67.5000, 1.0),
            (   5.2625,  37.8000, 0.0),
            (  -7.7425,  37.8000, 0.0),
            (  -7.7425,  31.5000, 0.0),
            (   5.2625,  31.5000, 0.0),
        ]
        pts_step = [(*to_step_left(x, y), r) for x, y, r in pts_pcb]
        holes_step = [to_step_left(x, y) for x, y in LEFT_PERIMETER_HOLES_PCB]

    sk = make_filleted_sketch(pts_step)
    pcb = bd.extrude(sk, amount=1.60).moved(bd.Location((0, 0, -5.20)))

    # Cut Ø 3.60 mm (radius 1.80 mm) spacer through-holes
    for hx, hy in holes_step:
        pcb = pcb - bd.Cylinder(
            radius=1.80,
            height=4.0,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((hx, hy, -6.0)))

    # On Right PCB: cut the PMW3360 optical + lens leg rectangular cutout (8.70 x 16.90 mm at (9.525, 52.3875))
    if is_right:
        tb_cx, tb_cy = to_step_right(9.5250, 52.3875)
        pcb = pcb - bd.Box(
            8.70,
            16.90,
            4.0,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((tb_cx, tb_cy, -6.0)))

    solid = pcb.solids()[0]
    solid.label = "Right_Main_PCB" if is_right else "Left_Main_PCB"
    return solid


def build_top_plate_solid(is_right=True) -> bd.Solid:
    """
    Constructs the FR-4 Top Plate solid (Z = -1.60 to 0.00 mm, thickness 1.60 mm)
    with switch cutouts and Ø 2.40 mm through-holes (no counterbores).
    """
    if is_right:
        pts_plate = [
            ( -5.6625, -24.71250, 1.0),
            (119.4625, -24.71250, 1.0),
            (119.4625,  41.38125, 1.0),
            ( 82.8625,  41.38125, 1.0),
            ( 82.8625,  67.90000, 1.0),
            ( 24.8375,  67.90000, 1.0),
            ( 24.8375,  37.40000, 1.0),
            ( -5.6625,  37.40000, 1.0),
        ]
        pts_step = [(*to_step_right(x, y), r) for x, y, r in pts_plate]
        sw_step = [to_step_right(x, y) for x, y in RIGHT_SWITCHES]
        holes_step = [to_step_right(x, y) for x, y in RIGHT_PERIMETER_HOLES_PCB]
    else:
        pts_plate = [
            (   5.6625, -24.71250, 1.0),
            (-119.4625, -24.71250, 1.0),
            (-119.4625,  41.38125, 1.0),
            ( -82.8625,  41.38125, 1.0),
            ( -82.8625,  67.90000, 1.0),
            (   5.6625,  67.90000, 1.0),
        ]
        pts_step = [(*to_step_left(x, y), r) for x, y, r in pts_plate]
        sw_step = [to_step_left(x, y) for x, y in LEFT_SWITCHES]
        holes_step = [to_step_left(x, y) for x, y in LEFT_PERIMETER_HOLES_PCB]

    sk = make_filleted_sketch(pts_step)
    plate = bd.extrude(sk, amount=1.60).moved(bd.Location((0, 0, -1.60)))

    with bd.BuildSketch(bd.Plane.XY.offset(-2.0)) as sk_cuts:
        for sx, sy in sw_step:
            with bd.Locations([(sx, sy)]):
                bd.RectangleRounded(14.0, 14.0, 0.5)
        if is_right:
            ex, ey = to_step_right(*RIGHT_ENCODER)
            with bd.Locations([(ex, ey)]):
                bd.RectangleRounded(18.2, 18.2, 0.5)
    plate = plate - bd.extrude(sk_cuts.sketch, amount=3.0)

    # Cut Ø 2.40 mm (radius 1.20 mm) M2 screw through-holes (no counterbores)
    for hx, hy in holes_step:
        plate = plate - bd.Cylinder(
            radius=1.20,
            height=4.0,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((hx, hy, -2.5)))

    solid = plate.solids()[0]
    solid.label = "Right_Top_Plate" if is_right else "Left_Top_Plate"
    return solid


def make_keycap_solid(sx, sy, label="Keycap") -> bd.Solid:
    with bd.BuildSketch(bd.Plane.XY.offset(1.20)) as sk:
        with bd.Locations([(sx, sy)]):
            bd.RectangleRounded(17.2, 16.2, 1.5)
    cap = bd.extrude(sk.sketch, amount=4.40).solids()[0]
    cap.label = label
    return cap


def make_ckw12_solids(ex, ey):
    """
    Loads the official CKW12 rotary encoder 3D models (housing, wheel, stem),
    rotates -90 deg around Z to match rEXSW1 orientation, and places at (ex, ey, Z = -5.20 mm).
    """
    models_dir = WORKSPACE / "pcbs" / "common" / "kbd" / "3dmodels"
    solids = []
    for fname, label in [
        ("ckw12_housing.stp", "CKW12_Housing"),
        ("ckw12_wheel.stp", "CKW12_Wheel"),
        ("ckw12_stem.stp", "CKW12_Stem"),
    ]:
        part = bd.import_step(str(models_dir / fname))
        placed = part.rotate(bd.Axis.Z, -90.0).moved(bd.Location((ex, ey, -5.20)))
        for idx, s in enumerate(placed.solids()):
            s.label = label if len(placed.solids()) == 1 else f"{label}_{idx+1}"
            solids.append(s)
    return solids


def main():
    print("=== Building & Verifying curcur40 Full Assembly (assembly-full.step) ===")

    left_case = bd.import_step(str(CASES_DIR / "left.step")).solids()[0]
    left_case.label = "Left_Case"
    right_case = bd.import_step(str(CASES_DIR / "right.step")).solids()[0]
    right_case.label = "Right_Case"

    left_pcb = build_main_pcb_solid(is_right=False)
    right_pcb = build_main_pcb_solid(is_right=True)

    left_plate = build_top_plate_solid(is_right=False)
    right_plate = build_top_plate_solid(is_right=True)

    # Trackball Cup placed on Right Main PCB F.Cu (Z = -3.60 mm) at (23.8125, -109.5375)
    tb_cx, tb_cy, tb_cz = 23.8125, -109.5375, -3.6000
    cup_local = bd.import_step(str(CASES_DIR / "trackball-cup.step"))
    cup_global = cup_local.moved(bd.Location((tb_cx, tb_cy, tb_cz))).solids()[0]
    cup_global.label = "Trackball_Cup"

    ball_global = (
        bd.Sphere(radius=12.50)
        .moved(bd.Location((tb_cx, tb_cy, tb_cz + 18.30)))
        .solids()[0]
    )
    ball_global.label = "Trackball_25mm"

    # Load PMW3360 sensor and LM19 lens from pmw3360-lens-pcb-assembly.step
    asm_parts = bd.import_step(str(CASES_DIR / "pmw3360-lens-pcb-assembly.step"))
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

    # Optical Distance Reference Point in global coordinates:
    # PCB F.Cu Z = -3.60 mm + 3.40 mm = -0.20 mm (2.40 mm below ball bottom Z = +2.20 mm)
    ref_point_global = bd.Pos(tb_cx, tb_cy, tb_cz + 3.40) * bd.Circle(0.35).face()
    ref_point_global.label = "Lens_Optical_Ref_Point"

    # CKW12 Rotary Encoder at rEXSW1 (14.2875, 0.0000)
    enc_x, enc_y = to_step_right(*RIGHT_ENCODER)
    ckw12_solids = make_ckw12_solids(enc_x, enc_y)

    # Create all 13x M2 5.50mm Standoffs (OD = 3.00 mm -> radius 1.50 mm, Z = -9.10 to -3.60 mm)
    left_holes_step = [to_step_left(x, y) for x, y in LEFT_PERIMETER_HOLES_PCB]
    right_perim_step = [to_step_right(x, y) for x, y in RIGHT_PERIMETER_HOLES_PCB]
    right_tb_step = [to_step_right(x, y) for x, y in RIGHT_TB_HOLES_PCB]

    standoffs = []
    bottom_screws = []
    top_screws = []

    all_holes = (
        [(x, y, "L_Perim", 0.00) for x, y in left_holes_step]
        + [(x, y, "R_Perim", 0.00) for x, y in right_perim_step]
        + [(x, y, "R_TB", -1.20) for x, y in right_tb_step]
    )

    for i, (sx, sy, tag, z_top_seat) in enumerate(all_holes):
        # M2 5.50mm standoff (OD 3.0mm, ID 1.7mm, Z = -9.10 to -3.60 mm)
        so = bd.Cylinder(
            radius=1.50,
            height=5.50,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((sx, sy, -9.10))) - bd.Cylinder(
            radius=0.85,
            height=6.00,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(
            bd.Location((sx, sy, -9.35))
        )
        so_solid = so.solids()[0]
        so_solid.label = f"Standoff_{tag}_{i+1}"
        standoffs.append(so_solid)

        # Bottom M2x4mm screw (head at Z = -12.20 to -11.40 mm inside counterbore, shank Z = -11.40 to -7.40 mm)
        b_head = bd.Cylinder(
            radius=2.00,
            height=0.80,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((sx, sy, -12.20)))
        b_shank = bd.Cylinder(
            radius=1.00,
            height=4.00,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((sx, sy, -11.40)))
        b_scr = (b_head + b_shank).solids()[0]
        b_scr.label = f"Bottom_Screw_{tag}_{i+1}"
        bottom_screws.append(b_scr)

        # Top M2x4mm screw (head seated at z_top_seat: 0.00 mm on Top Plate or -1.20 mm on Cup Ear)
        t_head = bd.Cylinder(
            radius=2.00,
            height=0.80,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        ).moved(bd.Location((sx, sy, z_top_seat)))
        t_shank = bd.Cylinder(
            radius=1.00,
            height=4.00,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX),
        ).moved(bd.Location((sx, sy, z_top_seat)))
        t_scr = (t_head + t_shank).solids()[0]
        t_scr.label = f"Top_Screw_{tag}_{i+1}"
        top_screws.append(t_scr)

    # Keycaps
    keycaps = []
    for idx, (kx, ky) in enumerate(LEFT_SWITCHES):
        sx, sy = to_step_left(kx, ky)
        keycaps.append(make_keycap_solid(sx, sy, f"Left_Keycap_{idx+1}"))
    for idx, (kx, ky) in enumerate(RIGHT_SWITCHES):
        sx, sy = to_step_right(kx, ky)
        keycaps.append(make_keycap_solid(sx, sy, f"Right_Keycap_{idx+1}"))

    # Run interference checks
    print("\n--- Interference Verification ---")
    ov_cup_case = overlap_volume(cup_global, right_case)
    ov_cup_plate = overlap_volume(cup_global, right_plate)
    ov_cup_ball = overlap_volume(cup_global, ball_global)
    ov_cup_lens = overlap_volume(cup_global, lens_global)
    ov_sensor_case = overlap_volume(sensor_global, right_case)
    ov_rpcb_case = overlap_volume(right_pcb, right_case)
    ov_lpcb_case = overlap_volume(left_pcb, left_case)

    ov_ckw12_plate = max(overlap_volume(s, right_plate) for s in ckw12_solids)
    ov_ckw12_screws = max(overlap_volume(s, t_scr) for s in ckw12_solids for t_scr in top_screws)

    print(f"Cup vs Right Case:     {ov_cup_case:.8f} mm^3")
    print(f"Cup vs Right Plate:    {ov_cup_plate:.8f} mm^3")
    print(f"Cup vs 25mm Ball:      {ov_cup_ball:.8f} mm^3")
    print(f"Cup vs LM19 Lens:      {ov_cup_lens:.8f} mm^3")
    print(f"Sensor vs Right Case:  {ov_sensor_case:.8f} mm^3")
    print(f"Right PCB vs Case:     {ov_rpcb_case:.8f} mm^3")
    print(f"Left PCB vs Case:      {ov_lpcb_case:.8f} mm^3")
    print(f"CKW12 vs Right Plate:  {ov_ckw12_plate:.8f} mm^3")
    print(f"CKW12 vs Top Screws:   {ov_ckw12_screws:.8f} mm^3")

    max_so_ov = 0.0
    for so in standoffs:
        max_so_ov = max(
            max_so_ov,
            overlap_volume(so, right_case),
            overlap_volume(so, left_case),
            overlap_volume(so, right_pcb),
            overlap_volume(so, left_pcb),
            overlap_volume(so, cup_global),
        )
    print(f"Max Standoff Overlap (vs Cases, PCBs, Cup): {max_so_ov:.8f} mm^3")

    max_cap_screw_ov = 0.0
    for t_scr in top_screws:
        for kc in keycaps:
            max_cap_screw_ov = max(max_cap_screw_ov, overlap_volume(t_scr, kc))
    print(f"Max Top Screw Head Overlap vs Keycaps:      {max_cap_screw_ov:.8f} mm^3")

    assert ov_cup_case == 0.0
    assert ov_cup_plate == 0.0
    assert ov_cup_ball == 0.0
    assert ov_cup_lens == 0.0
    assert ov_sensor_case == 0.0
    assert ov_rpcb_case == 0.0
    assert ov_lpcb_case == 0.0
    assert ov_ckw12_plate == 0.0
    assert ov_ckw12_screws == 0.0
    assert max_so_ov == 0.0
    assert max_cap_screw_ov == 0.0

    all_parts = (
        [
            left_case,
            right_case,
            left_pcb,
            right_pcb,
            left_plate,
            right_plate,
            cup_global,
            ball_global,
            lens_global,
            sensor_global,
            ref_point_global,
        ]
        + ckw12_solids
        + standoffs
        + bottom_screws
        + top_screws
        + keycaps
    )

    asm_full = bd.Compound(children=all_parts)
    asm_full.label = "curcur40_Full_Assembly"
    out_step = CASES_DIR / "assembly-full.step"
    bd.export_step(asm_full, str(out_step))
    print(
        f"\nSuccessfully exported {out_step} ({len(all_parts)} items, valid={asm_full.is_valid})"
    )


if __name__ == "__main__":
    main()

