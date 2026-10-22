# -*- coding: utf-8 -*-
"""
Generate PMW3360 + LM19-LSI optical sensor assemblies for curcur40:
1. cases/curcur40/pmw3360-lens-pcb-assembly.step
2. cases/curcur40/trackball-sensor-assembly.step

Includes the GUI-selectable lens-side optical distance reference point
(`Lens_Optical_Ref_Point`) at (0.00, 0.00, +3.40 mm), exactly 2.40 mm below
the 25mm trackball navigation surface (Z = +5.80 mm).
"""
from pathlib import Path
from cadgen import build123d as bd
from cadgen.geometry import overlap_volume, closest_points

WORKSPACE = Path(r"c:\Users\oktnt\workspace\curcur40")
CASES_DIR = WORKSPACE / "cases" / "curcur40"
OUT_SENSOR_PCB_STEP = CASES_DIR / "pmw3360-lens-pcb-assembly.step"
OUT_TRACKBALL_SENSOR_STEP = CASES_DIR / "trackball-sensor-assembly.step"

OPTICAL_REF_Z = 3.40
OPTICAL_REF_RADIUS = 0.35  # Ø 0.70 mm reference disk (both face & edge measure 2.40 mm to ball)


def make_optical_ref_point(x: float = 0.0, y: float = 0.0, z: float = OPTICAL_REF_Z) -> bd.Face:
    """
    Create a zero-thickness planar circular reference face at the exact lens-side
    optical distance reference plane (default Z = +3.4000 mm).
    """
    ref_face = bd.Pos(x, y, z) * bd.Circle(OPTICAL_REF_RADIUS).face()
    ref_face.label = "Lens_Optical_Ref_Point"
    return ref_face


def build_sensor_pcb_parts():
    """
    Build the 3 solids + 1 optical reference point for PMW3360DM-T2QU + LM19-LSI + PCB:
      Z = 0.00 mm: PCB Top Surface (F.Cu)
      Z = -1.60 mm: PCB Bottom Surface (B.Cu)
      Z = +3.40 mm: Lens Flange Bottom / Optical Distance Reference Point (2.40 mm below ball)
      Z = +5.80 mm: 25mm Trackball Bottom Surface (Navigation Surface)
    """
    # 1. Customer Supplied PCB (1.60 mm FR-4, Z in [-1.60, 0.00] mm)
    pcb_w, pcb_d, pcb_th = 32.0, 32.0, 1.60
    pin_xs = [(i - 3.5) * 1.78 for i in range(8)]
    with bd.BuildPart() as pcb_bp:
        with bd.BuildSketch(bd.Plane.XY.offset(-pcb_th)):
            bd.RectangleRounded(pcb_w, pcb_d, 2.0)
        bd.extrude(amount=pcb_th)

        # Central optical + lens-leg cutout
        with bd.BuildSketch(bd.Plane.XY.offset(-pcb_th - 0.5)):
            with bd.Locations([(0.0, 0.0)]):
                bd.RectangleRounded(17.50, 8.80, 0.50)
        bd.extrude(amount=pcb_th + 1.0, mode=bd.Mode.SUBTRACT)

        # 16 Pin Through-Holes (row pitch 10.70 mm, pin pitch 1.78 mm)
        with bd.BuildSketch(bd.Plane.XY.offset(-pcb_th - 0.5)):
            for px in pin_xs:
                with bd.Locations([(px, 5.35), (px, -5.35)]):
                    bd.Circle(radius=0.40)
        bd.extrude(amount=pcb_th + 1.0, mode=bd.Mode.SUBTRACT)

    pcb_solid = pcb_bp.part.rotate(bd.Axis.Z, 90).solids()[0]
    pcb_solid.label = "Customer_Supplied_PCB"

    # 2. PMW3360DM-T2QU Sensor IC (Mounted on B.Cu, body Z in [-4.01, -1.60] mm)
    pkg_w, pkg_d, pkg_h = 16.20, 9.10, 2.41
    with bd.BuildPart() as sensor_bp:
        with bd.BuildSketch(bd.Plane.XY.offset(-1.60 - pkg_h)):
            bd.RectangleRounded(pkg_w, pkg_d, 0.80)
        bd.extrude(amount=pkg_h)

        # Optical receptor cavity on top mating face (Z = -1.60 mm)
        with bd.BuildSketch(bd.Plane.XY.offset(-1.60 - 1.0)):
            bd.Circle(radius=1.50)
        bd.extrude(amount=1.05, mode=bd.Mode.SUBTRACT)

        # 2 Guide sockets for lens round guide posts
        with bd.BuildSketch(bd.Plane.XY.offset(-1.60 - 1.80)):
            with bd.Locations([(-8.25, -3.415), (8.25, 3.415)]):
                bd.Circle(radius=0.50)
        bd.extrude(amount=1.85, mode=bd.Mode.SUBTRACT)

        # 2 Rectangular alignment pockets for lens rectangular legs
        with bd.BuildSketch(bd.Plane.XY.offset(-1.60 - 0.80)):
            with bd.Locations([(-6.77, 3.415), (6.77, -3.415)]):
                bd.RectangleRounded(1.80, 1.20, 0.30)
        bd.extrude(amount=0.85, mode=bd.Mode.SUBTRACT)

        # 16 Metal Leads extending up through PCB to F.Cu
        for px in pin_xs:
            for py_sign, py_val in [(1, 5.35), (-1, -5.35)]:
                y_body_edge = py_sign * 4.55
                with bd.BuildSketch(bd.Plane.XZ.offset(min(y_body_edge, py_val))):
                    with bd.Locations([(px, -2.31)]):
                        bd.Rectangle(0.50, 0.25)
                bd.extrude(amount=abs(py_val - y_body_edge), mode=bd.Mode.ADD)

                with bd.BuildSketch(bd.Plane.XY.offset(-2.31)):
                    with bd.Locations([(px, py_val)]):
                        bd.Circle(radius=0.25)
                bd.extrude(amount=3.11, mode=bd.Mode.ADD)

    sensor_solid = sensor_bp.part.rotate(bd.Axis.Z, 90).solids()[0]
    sensor_solid.label = "PMW3360DM_T2QU_Sensor"

    # 3. LM19-LSI Optical Lens (Mounted on F.Cu, flange Z in [+3.40, +4.80] mm)
    with bd.BuildPart() as lens_bp:
        # Flange (21.15 x 18.85 mm, Z = +3.40 to +4.80 mm)
        with bd.BuildSketch(bd.Plane.XY.offset(3.40)):
            bd.RectangleRounded(21.15, 18.85, 7.50)
        bd.extrude(amount=1.40)

        # Central lens body on PCB top (Z = 0.00 to +3.40 mm)
        with bd.BuildSketch(bd.Plane.XY.offset(0.00)):
            bd.RectangleRounded(16.50, 8.47, 2.00)
        bd.extrude(amount=3.40, mode=bd.Mode.ADD)

        # Top optical dome (Z = +4.80 to +5.30 mm)
        with bd.BuildSketch(bd.Plane.XY.offset(4.80)):
            bd.RectangleRounded(6.0, 4.0, 1.5)
        bd.extrude(amount=0.50, mode=bd.Mode.ADD)

        # 2 Round Guide Posts extending down to Z = -3.35 mm
        with bd.BuildSketch(bd.Plane.XY.offset(-3.35)):
            with bd.Locations([(-8.25, -3.415), (8.25, 3.415)]):
                bd.Circle(radius=0.45)
        bd.extrude(amount=3.35, mode=bd.Mode.ADD)

        # 2 Rectangular Alignment Legs extending down to Z = -2.35 mm
        with bd.BuildSketch(bd.Plane.XY.offset(-2.35)):
            with bd.Locations([(-6.77, 3.415), (6.77, -3.415)]):
                bd.RectangleRounded(1.50, 1.00, 0.20)
        bd.extrude(amount=2.35, mode=bd.Mode.ADD)

        # Central Ø 0.70 mm optical sighting bore so Lens_Optical_Ref_Point at (0, 0, +3.40 mm)
        # is directly visible and selectable in 3D GUI viewers without z-fighting
        with bd.BuildSketch(bd.Plane.XY.offset(-0.10)):
            bd.Circle(radius=OPTICAL_REF_RADIUS)
        bd.extrude(amount=5.50, mode=bd.Mode.SUBTRACT)

    lens_solid = lens_bp.part.rotate(bd.Axis.Z, 90).solids()[0]
    lens_solid.label = "LM19_LSI_Lens"

    # 4. Optical Distance Reference Point at (0, 0, +3.40 mm)
    ref_point = make_optical_ref_point(0.0, 0.0, OPTICAL_REF_Z)

    return pcb_solid, sensor_solid, lens_solid, ref_point


def main():
    from generate_trackball_cup import build_trackball_cup

    pcb_solid, sensor_solid, lens_solid, ref_point = build_sensor_pcb_parts()

    # 1. Export pmw3360-lens-pcb-assembly.step
    sensor_pcb_assy = bd.Compound(children=[pcb_solid, sensor_solid, lens_solid, ref_point])
    sensor_pcb_assy.label = "PMW3360_Lens_PCB_Assembly"
    bd.export_step(sensor_pcb_assy, str(OUT_SENSOR_PCB_STEP))
    print(f"Exported: {OUT_SENSOR_PCB_STEP}")

    ov_pcb_sensor = overlap_volume(pcb_solid, sensor_solid)
    ov_pcb_lens = overlap_volume(pcb_solid, lens_solid)
    ov_lens_sensor = overlap_volume(lens_solid, sensor_solid)
    print(f"  Overlap PCB vs Sensor:  {ov_pcb_sensor:.6f} mm^3")
    print(f"  Overlap PCB vs Lens:    {ov_pcb_lens:.6f} mm^3")
    print(f"  Overlap Lens vs Sensor: {ov_lens_sensor:.6f} mm^3")
    assert ov_pcb_sensor == 0.0 and ov_pcb_lens == 0.0 and ov_lens_sensor == 0.0

    # 2. Export trackball-sensor-assembly.step (Cup + 25mm Ball + PCB + Sensor + Lens + Ref Point)
    cup_solid = build_trackball_cup()
    ball_solid = bd.Sphere(radius=12.50).moved(bd.Location((0, 0, 18.30))).solids()[0]
    ball_solid.label = "Trackball_25mm"
    ref_point_tb = make_optical_ref_point(0.0, 0.0, OPTICAL_REF_Z)

    tb_sensor_assy = bd.Compound(
        children=[cup_solid, ball_solid, pcb_solid, sensor_solid, lens_solid, ref_point_tb]
    )
    tb_sensor_assy.label = "Trackball_Sensor_Assembly"
    bd.export_step(tb_sensor_assy, str(OUT_TRACKBALL_SENSOR_STEP))
    print(f"Exported: {OUT_TRACKBALL_SENSOR_STEP}")

    ov_cup_ball = overlap_volume(cup_solid, ball_solid)
    ov_cup_lens = overlap_volume(cup_solid, lens_solid)
    dist_opt = closest_points(ball_solid, ref_point_tb).distance
    print(f"  Overlap Cup vs Ball:    {ov_cup_ball:.6f} mm^3")
    print(f"  Overlap Cup vs Lens:    {ov_cup_lens:.6f} mm^3")
    print(f"  Optical Distance (Ball Bottom Z=5.80 to Ref Point Z=3.40): {dist_opt:.6f} mm")
    assert ov_cup_ball == 0.0 and ov_cup_lens == 0.0
    assert abs(dist_opt - 2.40) < 1e-6


if __name__ == "__main__":
    main()
