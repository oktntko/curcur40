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

# 2. Add U1.8 connection on F.Cu at Y = 83.850 (clears H2 by 0.373mm!)
# Then via to B.Cu at (138.350, 83.850) (clears H1 by > 1.5mm!)
# Then vertical highway down X = 138.350 on B.Cu to C3.2 (clears MISO by 0.85mm and LED_P by 0.85mm!)
gnd_additions = '''# Connect U1.8 across to west side on F.Cu (clears H2 by 0.373mm):
add_track(net_gnd, [
    (150.989, 86.234),
    (150.989, 83.850),
    (138.350, 83.850),
], layer=pcbnew.F_Cu, width=0.20)
add_via(net_gnd, 138.350, 83.850)

# Connect down west corridor on B.Cu straight into C3.2:
add_track(net_gnd, [
    (138.350, 83.850),
    (138.350, 102.638),
    (139.200, 102.638),
], layer=pcbnew.B_Cu, width=0.25)
'''

code = code.replace('# 10. GND Connections', gnd_additions + '\n# 10. GND Connections')

with open('scratch/build_magic_highway_v2.py', 'w', encoding='utf-8') as f:
    f.write(code)

print('build_magic_highway_v2.py generated successfully!')
