import math
from pathlib import Path
from cadgen import build123d as bd

CUP_STEP = Path(r"cases/curcur40/trackball-cup.step")
OUT_ASSEMBLY_STEP = Path(r"cases/curcur40/trackball-sensor-assembly.step")

def build_assembly():
    # 1. Load Trackball Cup
    cup = bd.import_step(str(CUP_STEP))
    cup.label = "trackball_cup"

    # 2. Trackball (25.00 mm diameter sphere at origin)
    ball = bd.Sphere(radius=12.50).solid()
    ball.label = "trackball_25mm"

    # 3. LM19-LSI Optical Lens (per PixArt datasheet Fig. 6)
    # The flat top of the flange is the Lens Sitting / Reference Plane.
    # It sits against the bottom face of the trackball cup at z = -14.00 mm.
    z_ref = -14.00
    flange_th = 0.53
    neck_h = 6.18  # overall height 6.71 - flange 0.53
    
    lens_flange = bd.Box(
        18.85, 21.15, flange_th,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)
    ).moved(bd.Location((0, 0, z_ref)))

    # Lens optical neck passing through PCB cutout to IC
    lens_neck = bd.Box(
        8.47, 16.50, neck_h,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)
    ).moved(bd.Location((0, 0, z_ref - flange_th)))

    # Lens optical elements (central dome / cone looking up through cup aperture)
    lens_aperture_dome = bd.Cylinder(
        radius=2.50, height=0.80,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
    ).moved(bd.Location((0, 0, z_ref)))

    lens = (lens_flange + lens_neck + lens_aperture_dome).solid()
    lens.label = "lm19_lsi_lens"

    # 4. PMW3360DM-T2QU IC package (per datasheet Fig. 4)
    # Body: 14.20 x 19.60 mm, height 3.85 mm
    ic_z_top = z_ref - flange_th - 1.60  # sits under PCB
    ic_body = bd.Box(
        14.20, 19.60, 3.85,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)
    ).moved(bd.Location((0, 0, ic_z_top))).solid()
    ic_body.label = "pmw3360dm_sensor_ic"

    # 5. Sensor PCB (curcur40-pmw3360 envelope)
    # Thickness 1.60 mm, sits between lens flange and IC
    pcb_z_top = z_ref - flange_th
    pcb_w = 23.0
    pcb_l = 28.0
    pcb_th = 1.60
    pcb = bd.Box(
        pcb_w, pcb_l, pcb_th,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)
    ).moved(bd.Location((0, 0, pcb_z_top)))

    # Aperture in PCB for lens neck (8.47 x 16.50 mm -> cutout 9.60 x 18.00 mm)
    pcb_neck_cut = bd.Box(
        9.60, 18.00, pcb_th + 1.0,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)
    ).moved(bd.Location((0, 0, pcb_z_top - pcb_th / 2)))
    pcb = pcb - pcb_neck_cut

    # 4x M2 mounting holes in PCB aligning with cup
    for sx, sy in [(-4.50, -9.60), (4.50, -9.60), (-4.50, 9.60), (4.50, 9.60)]:
        hole = bd.Cylinder(
            radius=1.10, height=pcb_th + 1.0,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)
        ).moved(bd.Location((sx, sy, pcb_z_top - pcb_th / 2)))
        pcb = pcb - hole
    pcb = pcb.solid()
    pcb.label = "pmw3360_sensor_pcb"

    # 6. Fasteners: 4x M2 screws (head dia 3.80 mm, head h 1.40 mm, shaft dia 2.0 mm, length 8.0 mm)
    screws = []
    for sx, sy in [(-4.50, -9.60), (4.50, -9.60), (-4.50, 9.60), (4.50, 9.60)]:
        s_head = bd.Cylinder(
            radius=1.90, height=1.40,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
        ).moved(bd.Location((sx, sy, -11.90)))
        s_shaft = bd.Cylinder(
            radius=1.00, height=7.00,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)
        ).moved(bd.Location((sx, sy, -11.90)))
        screw = (s_head + s_shaft).solid()
        screw.label = f"m2_screw_{sx}_{sy}"
        screws.append(screw)

    assembly = bd.Compound([cup, ball, lens, ic_body, pcb] + screws)
    print("Assembly valid:", assembly.is_valid)
    bd.export_step(assembly, str(OUT_ASSEMBLY_STEP))
    print(f"Exported assembly to: {OUT_ASSEMBLY_STEP}")

if __name__ == "__main__":
    build_assembly()
