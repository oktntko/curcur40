# -*- coding: utf-8 -*-
"""
Generate trackball-cup.step and trackball-cup.stl for curcur40.
Strictly adheres to docs/curcur40/case_spec.md Section 4 (Trackball & Optics).
"""
import math
import time
from pathlib import Path
from cadgen import build123d as bd
from cadgen.geometry import is_sound

WORKSPACE = Path(r"c:\Users\oktnt\workspace\curcur40")
CASES_DIR = WORKSPACE / "cases" / "curcur40"
CASES_DIR.mkdir(parents=True, exist_ok=True)

def build_trackball_cup() -> bd.Solid:
    """
    Parametric CAD model for curcur40 Trackball Cup:
    - Ball diameter: Ø 25.0 mm (R = 12.50 mm)
    - Ball center: (0, 0, 18.30 mm)
    - Navigation Surface (Ball Bottom): Z = +5.80 mm
    - Cup uniform outer rim: Z = +14.00 mm (below Equator Z = +18.30 mm)
    - Outer body radius: R = 14.00 mm (Ø 28.00 mm)
    - Inner spherical bowl radius: R = 12.85 mm (0.35 mm ball gap)
    - 4 Mounting Ears at (+/-12.00, +/-11.30 mm):
        - Thickness = 2.40 mm (Z = 0.00 to 2.40 mm)
        - Through-hole = Ø 3.50 mm (no counterbore, flat top)
        - Outer boss radius = 3.25 mm (Ø 6.50 mm)
    - 3 Retention Claws (T-shape orthogonal):
        - North 90.0 deg, West 180.0 deg, East 0.0 deg
        - Width = 4.50 mm
        - Tip height = Z = +22.80 mm (+4.50 mm above Equator)
        - Rounded dome tips & inward retention snap nubs
    - South 270.0 deg: Claw-free, uniform rim at Z = 14.00 mm (no low-rim cutout needed)
    - 3 Ceramic Bearing Balls (Ø 2.00 mm):
        - Elevation = 52.0 deg down from horizontal (Z = 7.66 mm, R_xy = 8.31 mm)
        - Azimuth = 30.0 deg, 150.0 deg, 270.0 deg
        - Pocket radius = 1.03 mm, with Ø 1.20 mm clean push-out holes
    - LM19 Lens Pocket:
        - Flange seating step at Z = +3.40 mm (Optical distance 2.40 mm)
        - Central dome ceiling at Z = +4.85 mm
        - Peephole aperture vertical wall = 1.84 mm (Z = 4.85 to 6.69 mm)
    """
    z_base = 0.00
    z_ear = 2.40
    z_rim = 14.00
    z_claw_top = 22.80
    r_outer = 14.00
    r_inner = 12.85
    z_ball_center = 18.30
    w_claw = 4.50
    th_claw = 2.40

    # 1. Main cylindrical body (clean uniform rim at Z = 14.00 mm)
    cup = bd.Cylinder(
        radius=r_outer,
        height=z_rim - z_base,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    ).moved(bd.Location((0, 0, z_base)))

    # 2. Add 4 mounting ears at (+/-12.00, +/-11.30 mm) with thickness = 2.40 mm
    ear_coords = [
        ( 12.00,  11.30),  # NE (#1)
        (-12.00,  11.30),  # NW (#2)
        (-12.00, -11.30),  # SW (#3)
        ( 12.00, -11.30),  # SE (#4)
    ]
    with bd.BuildPart() as ears_bp:
        with bd.BuildSketch(bd.Plane.XY):
            bd.Circle(radius=r_outer)
            for sx, sy in ear_coords:
                with bd.Locations([(sx, sy)]):
                    bd.Circle(radius=3.25)
                with bd.Locations([(sx / 2, sy / 2)]):
                    ang = math.degrees(math.atan2(sy, sx))
                    bd.Rectangle(math.hypot(sx, sy), 6.50, rotation=ang)
        bd.extrude(amount=z_ear)
    cup = cup + ears_bp.part

    # 3. Add 3 SLIM claw pillars rising from Z = 13.00 to 22.80 mm
    # Angles: North (90.0 deg), West (180.0 deg), East (0.0 deg)
    # Positioned flush with outer radius R = 14.00 mm
    r_claw_mid = 12.80  # outer edge at 12.80 + 1.20 = 14.00 mm
    claw_angles = (90.0, 180.0, 0.0)
    for th_deg in claw_angles:
        th_rad = math.radians(th_deg)
        cx = r_claw_mid * math.cos(th_rad)
        cy = r_claw_mid * math.sin(th_rad)
        with bd.BuildPart() as claw_bp:
            with bd.BuildSketch(bd.Plane.XY.offset(13.00)):
                with bd.Locations([(cx, cy)]):
                    bd.Rectangle(th_claw, w_claw, rotation=th_deg)
            bd.extrude(amount=z_claw_top - 13.00)
        cup = cup + claw_bp.part

    # 4. Cut bottom LM19 lens flange pocket (Z = -0.50 to 3.40 mm)
    with bd.BuildPart() as lens_pocket_bp:
        with bd.BuildSketch(bd.Plane.XY.offset(-0.50)):
            bd.RectangleRounded(19.60, 22.20, 4.00)
        bd.extrude(amount=3.90)  # Reaches Z = +3.40 mm
    cup = cup - lens_pocket_bp.part

    # 5. Cut central lens dome recess (Z = 3.40 to 4.85 mm)
    with bd.BuildPart() as dome_bp:
        with bd.BuildSketch(bd.Plane.XY.offset(3.30)):
            bd.RectangleRounded(14.00, 16.00, 3.00)
        bd.extrude(amount=1.55)  # Reaches Z = +4.85 mm
    cup = cup - dome_bp.part

    # 6. Cut central optical peephole (Z = 4.80 to 9.80 mm)
    # Opening: 8.00 x 11.00 mm (Y = +/- 5.50 mm)
    with bd.BuildPart() as peephole_bp:
        with bd.BuildSketch(bd.Plane.XY.offset(4.80)):
            bd.RectangleRounded(8.00, 11.00, 2.50)
        bd.extrude(amount=5.00)
    cup = cup - peephole_bp.part

    # 7. Cut inner spherical cavity for 25mm trackball (R = 12.85 mm, center at Z = 18.30 mm)
    cup = cup - bd.Sphere(radius=r_inner).moved(bd.Location((0, 0, z_ball_center)))

    # 8. Add 3 rounded snap nubs (ツメ) at exactly (90.0, 180.0, 0.0 deg) at Z = 19.50 mm
    for az_deg in claw_angles:
        az_rad = math.radians(az_deg)
        nx = 12.80 * math.cos(az_rad)
        ny = 12.80 * math.sin(az_rad)
        nub = bd.Sphere(radius=0.70).moved(bd.Location((nx, ny, 19.50)))
        cup = cup + nub

    # 9. Sculpt the ARCH / DOME on the top of each slim claw!
    r_arch = w_claw / 2.0  # 2.25 mm
    z_arch_axis = z_claw_top - r_arch  # 22.80 - 2.25 = 20.55 mm
    for th_deg in claw_angles:
        th_rad = math.radians(th_deg)
        cx = r_claw_mid * math.cos(th_rad)
        cy = r_claw_mid * math.sin(th_rad)
        with bd.BuildPart() as arch_bp:
            with bd.BuildSketch(bd.Plane.XY.offset(z_arch_axis)):
                with bd.Locations([(cx, cy)]):
                    bd.Rectangle(th_claw + 4.0, w_claw + 4.0, rotation=th_deg)
            bd.extrude(amount=r_arch + 1.0)

            cyl = bd.Cylinder(
                radius=r_arch,
                height=th_claw + 6.0,
                align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)
            )
            cyl = cyl.rotate(bd.Axis.Y, 90).rotate(bd.Axis.Z, th_deg)
            cyl = cyl.moved(bd.Location((cx, cy, z_arch_axis)))
            arch_bp.part = arch_bp.part - cyl
        cup = cup - arch_bp.part

    # 10. Inner smooth lead-in chamfer for easy ball snap-in
    with bd.BuildPart() as leadin:
        with bd.BuildSketch(bd.Plane.XY.offset(21.40)):
            bd.Circle(radius=11.90)
        with bd.BuildSketch(bd.Plane.XY.offset(23.00)):
            bd.Circle(radius=13.50)
        bd.loft()
    cup = cup - leadin.part

    # 11. 3x Bearing ball pockets (Ø 2.00 mm ceramic balls) & clean push-out holes
    # Azimuths: 30.0 deg (#1), 150.0 deg (#2), 270.0 deg (#3)
    # Elevation: 52.0 deg down from horizontal
    r_orbit = 13.50
    elev_rad = math.radians(52.0)
    for az_deg in (30.0, 150.0, 270.0):
        az_rad = math.radians(az_deg)
        bx = r_orbit * math.cos(elev_rad) * math.cos(az_rad)
        by = r_orbit * math.cos(elev_rad) * math.sin(az_rad)
        bz = z_ball_center - r_orbit * math.sin(elev_rad)  # 7.66 mm
        pocket = bd.Sphere(radius=1.03).moved(bd.Location((bx, by, bz)))
        cup = cup - pocket
        
        # Clean push-out hole Ø 1.20 mm going downward
        push_hole = bd.Cylinder(
            radius=0.60,
            height=10.0,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)
        ).moved(bd.Location((bx, by, bz - 3.0)))
        cup = cup - push_hole

    # 12. 4x M2 screw through-holes (Ø 3.50 mm through-hole, NO counterbore, flat top)
    for sx, sy in ear_coords:
        hole = bd.Cylinder(
            radius=1.75,
            height=10.0,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)
        ).moved(bd.Location((sx, sy, z_ear / 2)))
        cup = cup - hole

    cup_solid = cup.solids()[0]
    cup_solid.label = "Trackball_Cup"
    return cup_solid

if __name__ == "__main__":
    t0 = time.time()
    print("Building curcur40 Trackball Cup per case_spec.md Section 4...")
    cup = build_trackball_cup()
    print(f"Trackball Cup solid: valid={cup.is_valid}, sound={is_sound(cup)}, volume={cup.volume:.2f} mm^3 in {time.time() - t0:.2f}s")
    
    bbox = cup.bounding_box()
    print(f"Bounding box: X=[{bbox.min.X:.2f}, {bbox.max.X:.2f}], Y=[{bbox.min.Y:.2f}, {bbox.max.Y:.2f}], Z=[{bbox.min.Z:.2f}, {bbox.max.Z:.2f}]")

    out_step = CASES_DIR / "trackball-cup.step"
    out_stl = CASES_DIR / "trackball-cup.stl"
    bd.export_step(cup, str(out_step))
    bd.export_stl(cup, str(out_stl))
    print(f"Successfully generated:")
    print(f" - {out_step}")
    print(f" - {out_stl}")
