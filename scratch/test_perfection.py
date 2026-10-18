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

# 2. Add GND highway connecting north B.Cu ground plane to south B.Cu ground plane:
# Via at (148.500, 82.000)
# Track on F.Cu from (148.500, 82.000) -> (148.500, 80.300) -> (138.400, 80.300) -> (138.400, 81.200)
# Via at (138.400, 81.200) to B.Cu
# Track on B.Cu along X = 138.400 down to C3.2 via at (139.200, 102.638)
# And connect U1.8 to (148.500, 82.000) on B.Cu east of H2 along X = 151.800:
gnd_bridge = '''# GND bridge connecting north B.Cu ground (U1.8) to south B.Cu ground (C3.2, Island 0):
add_via(net_gnd, 148.500, 82.000)
add_track(net_gnd, [
    (148.500, 82.000),
    (148.500, 80.300),
    (138.400, 80.300),
    (138.400, 81.200),
], layer=pcbnew.F_Cu, width=0.20)
add_via(net_gnd, 138.400, 81.200)
add_track(net_gnd, [
    (138.400, 81.200),
    (138.400, 102.638),
    (139.200, 102.638),
], layer=pcbnew.B_Cu, width=0.25)

# Connect U1.8 to (148.500, 82.000) on B.Cu around H2:
add_track(net_gnd, [
    (150.989, 86.234),
    (151.800, 86.234),
    (151.800, 80.600),
    (148.500, 80.600),
    (148.500, 82.000),
], layer=pcbnew.B_Cu, width=0.20)
'''

code = code.replace('# 10. GND Connections', gnd_bridge + '\n# 10. GND Connections')

with open('scratch/build_perfection.py', 'w', encoding='utf-8') as f:
    f.write(code)

print('build_perfection.py updated successfully!')
