# -*- coding: utf-8 -*-
import cadgen.build123d as bd
from pathlib import Path

# Load parts
right_case = bd.import_step("cases/curcur40/right.step")
cup = bd.import_step("cases/curcur40/trackball-cup.step")
assembly_full = bd.import_step("cases/curcur40/assembly-full.step")

print("Right case bbox:", right_case.bounding_box())
print("Cup bbox:", cup.bounding_box())

# In assembly-full.step, find Cup solid (Solid 4) and Case solid (Solid 1)
solids = assembly_full.solids()
print(f"Total solids in assembly: {len(solids)}")
case_solid = solids[1]
cup_solid = solids[4]
ball_solid = solids[5]

print("Case in assembly:", case_solid.bounding_box())
print("Cup in assembly:", cup_solid.bounding_box())
print("Ball in assembly:", ball_solid.bounding_box())

# Calculate offset between trackball-cup.step and cup in assembly
# In trackball-cup.step:
# Cup center is at (0, 0), ball at (0, 0, 0).
# Cup bottom is at Z = -14.00.
# Cup top rim is at Z = -1.00.
# In assembly:
# Ball bbox: X=[9.31, 34.31], Y=[-122.04, -97.04], Z=[-5.00, 20.00]
ball_bb = ball_solid.bounding_box()
ball_center_x = (ball_bb.min.X + ball_bb.max.X) / 2
ball_center_y = (ball_bb.min.Y + ball_bb.max.Y) / 2
ball_center_z = (ball_bb.min.Z + ball_bb.max.Z) / 2
print(f"Ball center in assembly: ({ball_center_x:.4f}, {ball_center_y:.4f}, {ball_center_z:.4f})")
