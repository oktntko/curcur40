# -*- coding: utf-8 -*-
import cadgen.build123d as bd
from pathlib import Path

STEP_CASE = Path(r"cases/curcur40/right.step")
STL_CASE = Path(r"cases/curcur40/right.stl")
STEP_ASM = Path(r"cases/curcur40/assembly-full.step")
STEP_CUP = Path(r"cases/curcur40/trackball-cup.step")

print("--- 1. BUILDING UPDATED RIGHT CASE ---")
orig_case = bd.import_step(str(STEP_CASE))
cx, cy = 21.8125, -109.5375

# 1. Fill old cutout
old_plug = bd.Box(15, 25, 2.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((cx, cy, -11.40)))
case_filled = orig_case + old_plug

# 2. Outer extension sketch
with bd.BuildSketch() as sk_outer:
    with bd.BuildLine():
        l1 = bd.Line((7.025, -122.3125), (7.025, -126.650))
        l2 = bd.Line((7.025, -126.650), (33.850, -126.650))
        l3 = bd.Line((33.850, -126.650), (38.1875, -122.3125))
        l4 = bd.Line((38.1875, -122.3125), (7.025, -122.3125))
    bd.make_face()
    bd.fillet(sk_outer.vertices().filter_by(lambda v: abs(v.X - 7.025) < 0.1 and abs(v.Y - (-126.650)) < 0.1), radius=1.0)
    bd.fillet(sk_outer.vertices().filter_by(lambda v: abs(v.X - 33.850) < 0.1 and abs(v.Y - (-126.650)) < 0.1), radius=1.0)
    bd.fillet(sk_outer.vertices().filter_by(lambda v: abs(v.X - 38.1875) < 0.1 and abs(v.Y - (-122.3125)) < 0.1), radius=1.0)

ext = bd.extrude(sk_outer.sketch, amount=11.10).moved(bd.Location((0, 0, -11.40)))
outer_edges_top = ext.edges().filter_by(lambda e: abs(e.bounding_box().max.Z - (-0.30)) < 0.05 and e.bounding_box().min.Y < -122.32)
outer_edges_bot = ext.edges().filter_by(lambda e: abs(e.bounding_box().min.Z - (-11.40)) < 0.05 and e.bounding_box().min.Y < -122.32)
ext_filleted = bd.fillet(outer_edges_top + outer_edges_bot, radius=0.95)

# 3. Inner cavity
with bd.BuildSketch() as sk_inner:
    with bd.BuildLine():
        i1 = bd.Line((8.525, -120.8125), (8.525, -125.150))
        i2 = bd.Line((8.525, -125.150), (33.228, -125.150))
        i3 = bd.Line((33.228, -125.150), (37.565, -120.8125))
        i4 = bd.Line((37.565, -120.8125), (8.525, -120.8125))
    bd.make_face()
    bd.fillet(sk_inner.vertices().filter_by(lambda v: abs(v.X - 8.525) < 0.1 and abs(v.Y - (-125.150)) < 0.1), radius=0.8)
    bd.fillet(sk_inner.vertices().filter_by(lambda v: abs(v.X - 33.228) < 0.1 and abs(v.Y - (-125.150)) < 0.1), radius=0.8)
    bd.fillet(sk_inner.vertices().filter_by(lambda v: abs(v.X - 37.565) < 0.1 and abs(v.Y - (-120.8125)) < 0.1), radius=0.8)

inner_cavity = bd.extrude(sk_inner.sketch, amount=10.0).moved(bd.Location((0, 0, -9.40)))

# Combine
wall_ext = ext_filleted - inner_cavity
case_extended = case_filled + wall_ext

# 4. New sensor window: 23.00 x 28.00 mm, radius 2.50 mm
with bd.BuildSketch() as sk_cut:
    bd.RectangleRounded(23.00, 28.00, radius=2.50)
sensor_window = bd.extrude(sk_cut.sketch, amount=3.0).moved(bd.Location((cx, cy, -11.50)))

new_right_case = (case_extended - sensor_window).solids()[0]
print("New right case bbox:", new_right_case.bounding_box())
print("New right case is valid:", new_right_case.is_valid)

# Export right.step and right.stl
bd.export_step(new_right_case, str(STEP_CASE))
print("Exported:", STEP_CASE)
bd.export_stl(new_right_case, str(STL_CASE))
print("Exported:", STL_CASE)

print("\n--- 2. UPDATING ASSEMBLY-FULL.STEP ---")
asm_orig = bd.import_step(str(STEP_ASM))
asm_solids = asm_orig.solids()
print(f"Original assembly solids count: {len(asm_solids)}")

# In assembly:
# Solid 0: Left case
# Solid 1: Right case (replace with new_right_case)
# Solid 2: Left plate
# Solid 3: Right plate
# Solid 4: Trackball cup (replace with new cup)
# Solid 5: Trackball ball
# Solid 6..50: components

# Load perfected cup
new_cup = bd.import_step(str(STEP_CUP))
# In trackball-cup.step, cup is at origin (0, 0), ball is at (0, 0, 0).
# In assembly, ball is at (cx, cy, 7.50) = (21.8125, -109.5375, 7.5000).
new_cup_in_asm = new_cup.moved(bd.Location((cx, cy, 7.5000)))
print("New cup in assembly bbox:", new_cup_in_asm.bounding_box())

updated_solids = []
for i, s in enumerate(asm_solids):
    if i == 1:
        updated_solids.append(new_right_case)
    elif i == 4:
        updated_solids.append(new_cup_in_asm.solids()[0])
    else:
        updated_solids.append(s)

compound_asm = bd.Compound(updated_solids)
print("Updated assembly bbox:", compound_asm.bounding_box())
print("Updated assembly solids count:", len(compound_asm.solids()))

bd.export_step(compound_asm, str(STEP_ASM))
print("Exported updated assembly:", STEP_ASM)
