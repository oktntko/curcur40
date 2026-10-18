with open('scratch/build_flawless_pmw3360_v30.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Move TP3 to (154.912, 98.500)
code = code.replace(
    '"TP3": ((138.300, 81.000), 0.0),',
    '"TP3": ((154.912, 98.500), 0.0),'
)
code = code.replace(
    'add_via(net_gnd, 138.300, 81.000)',
    'add_via(net_gnd, 154.912, 98.500)'
)

# 2. Update Reset routing to free up X = 152.0
old_reset = """# 3. /RESET: J1.8 (135.389, 84.1288) -> U1.7 (150.989, 88.0138) and R1.2 (153.088, 85.5) on F.Cu along Y = 79.8, X = 152.0
add_track(net_reset, [
    (135.389, 84.1288),
    (136.500, 84.1288),
    (136.500, 79.800),
    (152.000, 79.800),
    (152.000, 85.500),
    (153.088, 85.500), # R1.2
], layer=pcbnew.F_Cu, width=0.20)
add_track(net_reset, [
    (152.000, 85.500),
    (152.000, 88.0138),
    (150.989, 88.0138), # U1.7
], layer=pcbnew.F_Cu, width=0.20)"""

new_reset = """# 3. /RESET: J1.8 (135.389, 84.1288) -> R1.2 (153.088, 85.5) and U1.7 (150.989, 88.0138) along X = 153.088
add_track(net_reset, [
    (135.389, 84.1288),
    (136.500, 84.1288),
    (136.500, 79.800),
    (153.088, 79.800),
    (153.088, 85.500), # R1.2
    (153.088, 88.0138),
    (150.989, 88.0138), # U1.7
], layer=pcbnew.F_Cu, width=0.20)"""

code = code.replace(old_reset, new_reset)

# 3. Add GND connection for U1.8
gnd_conn = """# Connect U1.8 (150.989, 86.234) on F.Cu across to B.Cu Island 0:
add_track(net_gnd, [
    (150.989, 86.234),
    (152.000, 86.234),
    (152.000, 82.200),
    (154.000, 82.200),
], layer=pcbnew.F_Cu, width=0.25)
add_via(net_gnd, 154.000, 82.200)
"""
code = code.replace('# 10. GND Connections', gnd_conn + '\n# 10. GND Connections')

with open('scratch/build_test_gnd.py', 'w', encoding='utf-8') as f:
    f.write(code)

print('build_test_gnd.py generated successfully!')
