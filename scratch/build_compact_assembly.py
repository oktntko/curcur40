import math
from pathlib import Path
from cadgen import build123d as bd

CUP_STEP = Path(r"cases/curcur40/trackball-cup.step")
PCB_STEP = Path(r"scratch/pmw3360_plan_b.step")
OUT_ASSEMBLY_STEP = Path(r"cases/curcur40/trackball-sensor-assembly.step")

def build_assembly():
    # 1. Load Trackball Cup
    cup = bd.import_step(str(CUP_STEP))
    cup.label = "trackball_cup"

    # 2. Trackball (25.00 mm diameter sphere at origin)
    ball = bd.Sphere(radius=12.50).solid()
    ball.label = "trackball_25mm"

    # 3. LM19-LSI Optical Lens
    z_ref = -14.00
    flange_th = 0.53
    neck_h = 6.18
    
    lens_flange = bd.Box(
        18.85, 21.15, flange_th,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)
    ).moved(bd.Location((0, 0, z_ref)))

    lens_neck = bd.Box(
        8.47, 16.50, neck_h,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)
    ).moved(bd.Location((0, 0, z_ref - flange_th)))

    lens_aperture_dome = bd.Cylinder(
        radius=2.50, height=0.80,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
    ).moved(bd.Location((0, 0, z_ref)))

    lens = (lens_flange + lens_neck + lens_aperture_dome).solid()
    lens.label = "lm19_lsi_lens"

    # 4. PMW3360DM-T2QU IC package
    ic_z_top = z_ref - flange_th - 1.60
    ic_body = bd.Box(
        14.20, 19.60, 3.85,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)
    ).moved(bd.Location((0, 0, ic_z_top))).solid()
    ic_body.label = "pmw3360dm_sensor_ic"

    # 5. Actual Compact Sensor PCB (imported from KiCad STEP!)
    raw_pcb = bd.import_step(str(PCB_STEP))
    pcb_bb = raw_pcb.bounding_box()
    # In KiCad step, optical center is at (145.639, -92.5258, 0) due to Y reflection
    pcb = raw_pcb.moved(bd.Location((-145.639, 92.5258, -14.53 - pcb_bb.max.Z)))
    pcb.label = "compact_sensor_pcb"

    # 6. 4x M2 Fasteners
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
