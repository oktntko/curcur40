# -*- coding: utf-8 -*-
import cadgen.build123d as bd
from pathlib import Path

# Load original right case
orig_case = bd.import_step(r"cases/curcur40/right.step")
print("Original right case bounding box:", orig_case.bounding_box())
print("Original volume:", orig_case.volume)

# Trackball center in case coordinates
cx, cy = 21.8125, -109.5375

# Step 1: Remove old bottom cutout by filling it with a plug
# Old cutout: X in [17.21, 26.41], Y in [-118.44, -100.64], Z in [-11.40, -9.40]
old_plug = bd.Box(
    26.41 - 17.21 + 2.0,
    -100.64 - (-118.44) + 2.0,
    2.00,
    align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
).moved(bd.Location((cx, cy, -11.40)))

# Intersect plug with bottom floor region of the case
case_floor_slice = bd.Box(150, 150, 2.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((70, -75, -11.40)))
plug_solid = old_plug.intersect(case_floor_slice)

case_filled = orig_case + plug_solid
print("Filled case volume:", case_filled.volume)

# Step 2: Extend front wall around trackball
# Original front outer wall: Y = -122.3125
# Original front inner wall: Y = -120.8125
# Extension depth: dy = 4.3375 mm
# New front outer wall: Y = -122.3125 - 4.3375 = -126.650 mm
# New front inner wall: Y = -120.8125 - 4.3375 = -125.150 mm
# Left wall: X = 7.025 (outer), X = 8.525 (inner)
# Tab X span: from X = 7.025 to X = 33.5, then 45 deg chamfer to X = 39.5 at Y = -122.3125

# Create outer extension solid (Z from -11.40 to -0.30, height = 11.10)
# Profile on XY plane:
# Start at (7.025, -122.3125) -> (7.025, -126.650) -> (33.85, -126.650) -> (38.1875, -122.3125) -> (7.025, -122.3125)
with bd.BuildSketch() as sk_outer:
    with bd.BuildLine():
        l1 = bd.Line((7.025, -122.3125), (7.025, -126.650))
        l2 = bd.Line((7.025, -126.650), (33.850, -126.650))
        l3 = bd.Line((33.850, -126.650), (38.1875, -122.3125))
        l4 = bd.Line((38.1875, -122.3125), (7.025, -122.3125))
    bd.make_face()
    # Add bottom-left fillet R=1.0 on outer corner (7.025, -126.650)
    bd.fillet(sk_outer.vertices().filter_by(lambda v: abs(v.X - 7.025) < 0.1 and abs(v.Y - (-126.650)) < 0.1), radius=1.0)
    # Add chamfer fillet R=1.0 on (33.850, -126.650)
    bd.fillet(sk_outer.vertices().filter_by(lambda v: abs(v.X - 33.850) < 0.1 and abs(v.Y - (-126.650)) < 0.1), radius=1.0)

outer_ext = bd.extrude(sk_outer.sketch, amount=11.10).moved(bd.Location((0, 0, -11.40)))

# Create inner pocket cavity (Z from -9.40 to 0.0, height = 9.40)
# Inner profile:
# (8.525, -120.8125) -> (8.525, -125.150) -> (33.228, -125.150) -> (37.565, -120.8125) -> (8.525, -120.8125)
with bd.BuildSketch() as sk_inner:
    with bd.BuildLine():
        i1 = bd.Line((8.525, -120.8125), (8.525, -125.150))
        i2 = bd.Line((8.525, -125.150), (33.228, -125.150))
        i3 = bd.Line((33.228, -125.150), (37.565, -120.8125))
        i4 = bd.Line((37.565, -120.8125), (8.525, -120.8125))
    bd.make_face()
    bd.fillet(sk_inner.vertices().filter_by(lambda v: abs(v.X - 8.525) < 0.1 and abs(v.Y - (-125.150)) < 0.1), radius=0.8)
    bd.fillet(sk_inner.vertices().filter_by(lambda v: abs(v.X - 33.228) < 0.1 and abs(v.Y - (-125.150)) < 0.1), radius=0.8)

inner_cavity = bd.extrude(sk_inner.sketch, amount=10.0).moved(bd.Location((0, 0, -9.40)))

# Wall addition = outer_ext - inner_cavity
wall_ext = outer_ext - inner_cavity
case_extended = case_filled + wall_ext
print("Case extended volume:", case_extended.volume)

# Step 3: Cut new bottom sensor window (23.00 x 28.00 mm, corner R=2.50 mm)
# Window center: (cx, cy) = (21.8125, -109.5375)
# Through floor: Z in [-11.50, -9.30]
with bd.BuildSketch() as sk_cutout:
    bd.RectangleRounded(23.00, 28.00, radius=2.50)
sensor_window = bd.extrude(sk_cutout.sketch, amount=3.0).moved(bd.Location((cx, cy, -11.50)))

case_final = case_extended - sensor_window
print("Case final volume:", case_final.volume)
print("Case final bbox:", case_final.bounding_box())
print("Solids count:", len(case_final.solids()))
print("Is valid:", case_final.is_valid())
