import pcbnew

# Load v30 base
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

# 2. In VDD: do NOT connect U1.4 on B.Cu! Connect U1.4 on F.Cu!
# Old VDD routing:
old_vdd = '''# VDD highway north on B.Cu along X = 152.4:
add_track(net_vdd, [
    (151.600, 101.200),
    (152.400, 100.400),
    (152.400, 93.354),
], layer=pcbnew.B_Cu, width=0.25)
# Connect to U1.4 directly on B.Cu (U1 is TH!) and to JP1.3 on F.Cu
add_track(net_vdd, [(152.400, 93.354), (150.989, 93.354)], layer=pcbnew.B_Cu, width=0.25)
add_via(net_vdd, 152.400, 93.354)
add_track(net_vdd, [
    (152.400, 93.354),
    (153.889, 93.354),
    (153.889, 91.584), # JP1.3 on F.Cu
], layer=pcbnew.F_Cu, width=0.25)

# Continue VDD north on B.Cu along X = 152.4 to Y = 80.8 -> across to X = 147.2 -> via to F.Cu at (147.2, 81.8) (TP2)
add_track(net_vdd, [
    (152.400, 93.354),
    (152.400, 80.800),
    (147.200, 80.800),
    (147.200, 81.800), # TP2
], layer=pcbnew.B_Cu, width=0.25)
add_via(net_vdd, 147.200, 81.800)
# Connect to R3.1 on F.Cu:
add_track(net_vdd, [
    (147.200, 81.800),
    (147.200, 80.800),
    (143.088, 80.800),
    (143.088, 81.800), # R3.1
], layer=pcbnew.F_Cu, width=0.25)'''

new_vdd = '''# VDD highway north on B.Cu along X = 152.4:
add_track(net_vdd, [
    (151.600, 101.200),
    (152.400, 100.400),
    (152.400, 93.354),
], layer=pcbnew.B_Cu, width=0.25)
# Via to F.Cu at (152.400, 93.354), connect to U1.4 on F.Cu and JP1.3 on F.Cu! (NO B.Cu horizontal track to U1.4!)
add_via(net_vdd, 152.400, 93.354)
add_track(net_vdd, [(152.400, 93.354), (150.989, 93.354)], layer=pcbnew.F_Cu, width=0.25) # U1.4 on F.Cu
add_track(net_vdd, [
    (152.400, 93.354),
    (153.889, 93.354),
    (153.889, 91.584), # JP1.3 on F.Cu
], layer=pcbnew.F_Cu, width=0.25)

# Continue VDD north on B.Cu along X = 152.4 to Y = 79.200 (north of GND zone!) -> across to X = 147.2 -> via to F.Cu
add_track(net_vdd, [
    (152.400, 93.354),
    (152.400, 79.200),
    (147.200, 79.200),
    (147.200, 81.800), # TP2 on F.Cu
], layer=pcbnew.B_Cu, width=0.25)
add_via(net_vdd, 147.200, 81.800)
# Connect to R3.1 on F.Cu:
add_track(net_vdd, [
    (147.200, 81.800),
    (147.200, 80.800),
    (143.088, 80.800),
    (143.088, 81.800), # R3.1
], layer=pcbnew.F_Cu, width=0.25)'''

code = code.replace(old_vdd, new_vdd)

with open('scratch/build_test_doors.py', 'w', encoding='utf-8') as f:
    f.write(code)

print('build_test_doors.py generated!')
