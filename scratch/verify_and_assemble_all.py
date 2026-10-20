import math
from pathlib import Path
from cadgen import build123d as bd
from cadgen.geometry import overlap_volume, is_sound

WORKSPACE = Path(r"c:\Users\oktnt\workspace\curcur40")
CASES_DIR = WORKSPACE / "cases" / "curcur40"

def test_full_screw_and_spacer_stackup():
    print("=== Testing Full 5.5mm Standoff & 4mm Screw Stackup ===")
    
    right_case = bd.import_step(str(CASES_DIR / "right.step"))
    cup_local = bd.import_step(str(CASES_DIR / "trackball-cup.step"))
    asm_parts = bd.import_step(str(CASES_DIR / "pmw3360-lens-pcb-assembly.step"))

    tb_cx, tb_cy, tb_cz = 23.8125, -109.5375, -3.4000
    cup_global = cup_local.moved(bd.Location((tb_cx, tb_cy, tb_cz)))

    # Identify sensor and lens
    sensor = None
    lens = None
    for s in asm_parts.solids():
        bb = s.bounding_box()
        if bb.min.Z < -3.5:
            sensor = s
        elif bb.max.Z > 3.0:
            lens = s
    sensor_global = sensor.moved(bd.Location((tb_cx, tb_cy, tb_cz)))
    lens_global = lens.moved(bd.Location((tb_cx, tb_cy, tb_cz)))
    ball_global = bd.Sphere(radius=12.50).moved(bd.Location((tb_cx, tb_cy, tb_cz + 18.30))).solids()[0]

    # Trackball 4 screw coordinates (global)
    screw_coords_global = [
        (tb_cx - 12.00, tb_cy - 11.30),
        (tb_cx + 12.00, tb_cy - 11.30),
        (tb_cx - 12.00, tb_cy + 11.30),
        (tb_cx + 12.00, tb_cy + 11.30),
    ]

    # Create 4x M2 5.5mm Standoffs (from Z = -10.50 to -5.00 mm)
    standoffs = []
    for sx, sy in screw_coords_global:
        # Hex or cylinder standoff (OD = 4.0mm, ID = 1.6mm for M2 internal thread)
        so = bd.Cylinder(radius=2.00, height=5.50, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((sx, sy, -10.50)))
        so = so - bd.Cylinder(radius=0.85, height=6.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((sx, sy, -10.75)))
        so.solids()[0].label = f"M2_5.5mm_Standoff_{sx:.1f}_{sy:.1f}"
        standoffs.append(so.solids()[0])

    # Create 4x Bottom M2 Low-Profile Screws (head dia 4.0mm, head h 0.8mm, shank dia 2.0mm, shank len 4.0mm)
    # Head seated at counterbore floor Z = -11.60 mm.
    # Head: Z = -12.40 to -11.60 mm (0.20 mm recessed below Z = -12.60 mm case outer bottom!)
    # Shank: Z = -11.60 to -7.60 mm (penetrates 2.90 mm into spacer!)
    bottom_screws = []
    for sx, sy in screw_coords_global:
        s_head = bd.Cylinder(radius=2.00, height=0.80, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((sx, sy, -12.40)))
        s_shank = bd.Cylinder(radius=1.00, height=4.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((sx, sy, -11.60)))
        scr = (s_head + s_shank).solids()[0]
        scr.label = f"Bottom_M2x4_Screw_{sx:.1f}_{sy:.1f}"
        bottom_screws.append(scr)

    # Create 4x Top M2 Low-Profile Screws (head dia 4.0mm, head h 0.8mm, shank dia 2.0mm, shank len 4.0mm)
    # Head seated on flat cup ear top at Z = tb_cz + 1.20 = -2.20 mm.
    # Head: Z = -2.20 to -1.40 mm
    # Shank: Z = -2.20 to -6.20 mm (passes 1.2mm ear + 1.6mm PCB, penetrates 1.20 mm into spacer!)
    top_screws = []
    for sx, sy in screw_coords_global:
        s_head = bd.Cylinder(radius=2.00, height=0.80, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((sx, sy, -2.20)))
        s_shank = bd.Cylinder(radius=1.00, height=4.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).moved(bd.Location((sx, sy, -2.20)))
        scr = (s_head + s_shank).solids()[0]
        scr.label = f"Top_M2x4_Screw_{sx:.1f}_{sy:.1f}"
        top_screws.append(scr)

    # Check Clearances inside the 5.5mm Standoff between top and bottom screws
    bottom_screw_tip_z = -7.60
    top_screw_tip_z = -6.20
    clearance_gap = top_screw_tip_z - bottom_screw_tip_z
    print(f"Bottom screw tip: Z = {bottom_screw_tip_z:.2f} mm")
    print(f"Top screw tip:    Z = {top_screw_tip_z:.2f} mm")
    print(f"Clearance inside spacer between screw tips: {clearance_gap:.2f} mm (Should be > 0.5 mm)")
    assert clearance_gap > 1.0, f"Screw tips collide or gap too small: {clearance_gap}"

    # Interference checks
    print("\n--- Checking Component Interferences ---")
    case_solid = right_case.solids()[0]
    cup_solid = cup_global.solids()[0]

    print("Cup vs Case:", overlap_volume(cup_solid, case_solid))
    print("Cup vs Ball:", overlap_volume(cup_solid, ball_global))
    print("Cup vs Lens:", overlap_volume(cup_solid, lens_global))
    print("Sensor vs Case:", overlap_volume(sensor_global, case_solid))

    for i, so in enumerate(standoffs):
        print(f"Standoff {i+1} vs Case:", overlap_volume(so, case_solid))
        print(f"Standoff {i+1} vs Bottom Screw Shank:", overlap_volume(so, bottom_screws[i]))
        print(f"Standoff {i+1} vs Top Screw Shank:", overlap_volume(so, top_screws[i]))

    # Export full assembly STEP with everything!
    all_parts = [case_solid, cup_solid, ball_global, lens_global, sensor_global] + standoffs + bottom_screws + top_screws
    asm_full = bd.Compound(all_parts)
    print(f"\nAssembly Full solid count: {len(all_parts)}, valid: {asm_full.is_valid}")
    bd.export_step(asm_full, str(CASES_DIR / "assembly-full.step"))
    print(f"Successfully exported {CASES_DIR / 'assembly-full.step'}")

if __name__ == "__main__":
    test_full_screw_and_spacer_stackup()
