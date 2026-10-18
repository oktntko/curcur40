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

# 2. Add U1.8 connection to north copper at (148.0, 83.5)
# And vertical GND highway on B.Cu along X = 138.350 from Y = 83.500 to Y = 102.638
gnd_additions = '''# Connect U1.8 to north copper:
add_track(net_gnd, [
    (150.989, 86.234),
    (150.989, 83.500),
    (148.000, 83.500),
], layer=pcbnew.F_Cu, width=0.25)
add_via(net_gnd, 148.000, 83.500)

# Connect north copper across to south copper via 138.350 highway on B.Cu:
add_track(net_gnd, [
    (148.000, 83.500),
    (138.350, 83.500),
    (138.350, 102.638),
    (139.200, 102.638), # connects to C3.2 via
], layer=pcbnew.B_Cu, width=0.25)
'''

code = code.replace('# 10. GND Connections', gnd_additions + '\n# 10. GND Connections')

with open('scratch/build_magic_highway.py', 'w', encoding='utf-8') as f:
    f.write(code)

print('build_magic_highway.py generated successfully!')
