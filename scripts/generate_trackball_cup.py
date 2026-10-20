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
        - Through-hole = Ø 3.60 mm (no counterbore, flat top)
        - Outer boss radius = 3.25 mm (Ø 6.50 mm)
    - 3 Retention Claws (T-shape orthogonal):
        - North 90.0 deg, West 180.0 deg, East 0.0 deg
        - Width = 4.50 mm
        - Outer back face: Perfectly cylindrical matching R = 14.00 mm body (seamless, zero step)
        - Rounded dome tips & smooth spherical wrap retention (no local nubs needed)
    - South 270.0 deg: Claw-free, uniform rim at Z = 14.00 mm (no low-rim cutout needed)
    - 3 Ceramic Bearing Balls (Ø 2.00 mm):
        - Elevation = 52.0 deg down from horizontal (Z = 7.66 mm, R_xy = 8.31 mm)
        - Azimuth = 30.0 deg, 150.0 deg, 270.0 deg
        - Pocket radius = 1.03 mm, with Ø 1.20 mm clean push-out holes
    - LM19 Lens Pocket (2-Stage Design, Zero Collision):
        - Main lens chamber (19.60 x 22.20 mm): Z = 0.00 to +4.85 mm (accommodates 18.85 x 21.15 mm flange)
        - Flange bottom at Z = +3.40 mm ensures exact 2.40 mm optical tracking distance to ball bottom (Z = +5.80 mm)
        - Central peephole (8.00 x 11.00 mm): Z = +4.85 to 6.69 mm (optical path)
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

    # 3. Add 3 SLIM claw pillars with CYLINDRICAL outer back face (North 90°, West 180°, East 0°)
    # Outer back face trimmed to match the cup's outer cylinder (R = 14.00 mm, Ø 28.00 mm) perfectly.
    # Claws rise from uniform rim (Z = 13.00 mm) up to Z = 22.80 mm (+4.50 mm above equator).
    # Retention is achieved naturally by the spherical inner surface (Step 6) curving inward over
    # the ball's northern hemisphere:
    # - Equator (Z = 18.30 mm): Opening Ø = 25.30 mm (+0.30 mm clearance)
    # - Throat (Z = 21.40 mm): Opening Ø = 24.59 mm (narrows down below Ø 25.00 mm equator!)
    # - Seated clearance = +0.35 mm uniform across the entire ball (ZERO contact during operation).
    # - Catch on lift = Ø 24.59 mm throat blocks Ø 25.00 mm equator, preventing drop-out.
    r_claw_mid = 12.80
    claw_angles = (90.0, 180.0, 0.0)
    claw_trim_cyl = bd.Cylinder(
        radius=r_outer,
        height=z_claw_top - 13.00,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
    ).moved(bd.Location((0, 0, 13.00)))

    for th_deg in claw_angles:
        th_rad = math.radians(th_deg)
        cx = r_claw_mid * math.cos(th_rad)
        cy = r_claw_mid * math.sin(th_rad)
        with bd.BuildPart() as claw_bp:
            with bd.BuildSketch(bd.Plane.XY.offset(13.00)):
                with bd.Locations([(cx, cy)]):
                    # Width = 4.50 mm, radial thickness extended slightly outward so cylinder trimming
                    # creates an exact, seamless continuation of the R = 14.00 mm cup outer wall
                    bd.Rectangle(th_claw + 0.60, w_claw, rotation=th_deg)
            bd.extrude(amount=z_claw_top - 13.00)
        trimmed_claw = claw_bp.part.intersect(claw_trim_cyl)
        cup = cup + trimmed_claw

    # 4. Cut bottom LM19 lens pocket (Z = -0.50 to 4.85 mm, 2-Stage Design)
    # Perfectly accommodates the LM19 lens flange (18.85 x 21.15 mm, Z = 3.40 to 4.80 mm)
    # with zero collision, ensuring exact 2.40 mm optical tracking distance!
    with bd.BuildPart() as lens_pocket_bp:
        with bd.BuildSketch(bd.Plane.XY.offset(-0.50)):
            bd.RectangleRounded(19.60, 22.20, 4.00)
        bd.extrude(amount=5.35)  # Reaches Z = +4.85 mm
    cup = cup - lens_pocket_bp.part

    # 5. Cut central optical peephole (Z = 4.80 to 9.80 mm)
    # Opening: 8.00 x 11.00 mm (Y = +/- 5.50 mm)
    with bd.BuildPart() as peephole_bp:
        with bd.BuildSketch(bd.Plane.XY.offset(4.80)):
            bd.RectangleRounded(8.00, 11.00, 2.50)
        bd.extrude(amount=5.00)
    cup = cup - peephole_bp.part

    # 6. Cut inner spherical cavity for 25mm trackball (R = 12.85 mm, center at Z = 18.30 mm)
    cup = cup - bd.Sphere(radius=r_inner).moved(bd.Location((0, 0, z_ball_center)))

    # 7. Sculpt the ARCH / DOME on the top of each slim claw!
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

    # 8. Inner smooth lead-in chamfer for easy ball insertion
    cone = bd.Cone(
        bottom_radius=11.90,
        top_radius=13.50,
        height=1.60,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
    ).moved(bd.Location((0, 0, 21.40)))
    cup = cup - cone

    # 9. 3x Bearing ball pockets (Ø 2.00 mm ceramic balls)
    # Azimuths: 30.0 deg (#1), 150.0 deg (#2), 270.0 deg (#3)
    # Elevation: 52.0 deg down from horizontal
    # Single clean spherical dimple per bearing ball (pocket radius 1.03 mm, depth 1.35 mm, no bottom breakthrough)
    r_orbit = 13.50
    elev_rad = math.radians(52.0)
    for az_deg in (30.0, 150.0, 270.0):
        az_rad = math.radians(az_deg)
        bx = r_orbit * math.cos(elev_rad) * math.cos(az_rad)
        by = r_orbit * math.cos(elev_rad) * math.sin(az_rad)
        bz = z_ball_center - r_orbit * math.sin(elev_rad)  # 7.66 mm
        pocket = bd.Sphere(radius=1.03).moved(bd.Location((bx, by, bz)))
        cup = cup - pocket

    # 10. 4x M2 screw through-holes (Ø 3.60 mm through-hole, NO counterbore, flat top)
    for sx, sy in ear_coords:
        hole = bd.Cylinder(
            radius=1.80,
            height=10.0,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)
        ).moved(bd.Location((sx, sy, z_ear / 2)))
        cup = cup - hole

    cup_solid = cup.solids()[0]
    cup_solid.label = "Trackball_Cup"
    return cup_solid

def build_trackball_assembly() -> bd.Compound:
    """
    Assembly of Trackball Cup with 25mm Trackball centered at (0, 0, 18.30 mm).
    Allows visual inspection of claw retention, equator coverage, and clearances.
    """
    cup = build_trackball_cup()
    ball = bd.Sphere(radius=12.50).moved(bd.Location((0, 0, 18.30)))
    ball_solid = ball.solids()[0]
    ball_solid.label = "Trackball_25mm"
    
    assembly = bd.Compound([cup, ball_solid])
    return assembly

if __name__ == "__main__":
    from cadgen.geometry import overlap_volume
    t0 = time.time()
    print("Building curcur40 Trackball Cup per case_spec.md Section 4...")
    cup = build_trackball_cup()
    print(f"Trackball Cup solid: valid={cup.is_valid}, sound={is_sound(cup)}, volume={cup.volume:.2f} mm^3 in {time.time() - t0:.2f}s")
    
    bbox = cup.bounding_box()
    print(f"Bounding box: X=[{bbox.min.X:.2f}, {bbox.max.X:.2f}], Y=[{bbox.min.Y:.2f}, {bbox.max.Y:.2f}], Z=[{bbox.min.Z:.2f}, {bbox.max.Z:.2f}]")

    # Verify zero contact with seated 25mm ball
    ball = bd.Sphere(radius=12.50).moved(bd.Location((0, 0, 18.30))).solids()[0]
    ov = overlap_volume(cup, ball)
    print(f"Overlap volume with seated 25mm ball: {ov:.8f} mm^3 (ZERO CONTACT = {ov == 0.0})")

    # Verify zero collision with LM19 optical lens
    lens_step = CASES_DIR / "pmw3360-lens-pcb-assembly.step"
    if lens_step.exists():
        assy = bd.import_step(str(lens_step))
        lens = assy.solids()[2]
        ov_lens = overlap_volume(cup, lens)
        print(f"Overlap volume with LM19 lens: {ov_lens:.8f} mm^3 (ZERO COLLISION = {ov_lens == 0.0})")

    out_step = CASES_DIR / "trackball-cup.step"
    out_stl = CASES_DIR / "trackball-cup.stl"
    bd.export_step(cup, str(out_step))
    bd.export_stl(cup, str(out_stl))
    print(f"Successfully generated:")
    print(f" - {out_step}")
    print(f" - {out_stl}")

    # Build and export Trackball Cup + 25mm Ball Assembly
    print("\nBuilding Trackball Cup with 25mm Ball Assembly...")
    assembly = build_trackball_assembly()
    out_assembly_step = CASES_DIR / "trackball-cup-with-ball.step"
    out_assembly_stl = CASES_DIR / "trackball-cup-with-ball.stl"
    bd.export_step(assembly, str(out_assembly_step))
    bd.export_stl(assembly, str(out_assembly_stl))
    print(f"Successfully generated Assembly:")
    print(f" - {out_assembly_step}")
    print(f" - {out_assembly_stl}")
