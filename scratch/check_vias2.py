
# Let us check how many YS-SK6812MINI-E footprints are on the board:
import pcbnew
b = pcbnew.LoadBoard('pcbs/curcur40/left/curcur40-left.kicad_pcb')
leds = [fp for fp in b.GetFootprints() if 'SK6812' in fp.GetFPIDAsString() or fp.GetReference().startswith('LED') or fp.GetReference().startswith('EXLED')]
print(f'Total LEDs on Left PCB: {len(leds)}')
# The triangle silkscreen (pin 1 / GND indicator) has a vertex at (-2.8, -1.5).
# Pad 3 (GND) is at (-2.8, -0.7), size (1.7, 0.825).
# Solder mask opening for Pad 3 extends to Y = -0.7 - 0.4125 - 0.05 = -1.1625 mm.
# The triangle silk reaches Y = -1.5 mm, so it overlaps the mask aperture by 0.3375 mm!
# If we shrink or pull back that triangle by 0.40 mm (from -1.5 to -1.10, or adjust the triangle so it does not touch the pad mask):
# Or move the triangle slightly outside the mask, silk_over_copper is 100% eliminated for ALL LEDs!
