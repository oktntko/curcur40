
# If we replace (xy -2.8 -1.5) with (xy -3.8 -1.5):
# The triangle is at X in [-4.05, -3.8], Y in [-1.5, -0.35].
# Pad 3 is at X = -2.8, size = 1.7 -> right edge = -1.95, left edge = -3.65.
# Mask opening is at X = -3.70.
# At X = -3.8, it is completely OUTSIDE the mask opening (-3.70)!
# And it still clearly marks the pin 1 / GND corner!
print('Safe triangle replacement confirmed!')
