with open(r"pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pcb", "r", encoding="utf-8") as f:
    lines = f.readlines()

in_u1 = False
for i, line in enumerate(lines, 1):
    if 'footprint "kbd_local:PMW3360DM-T2QU_16Pin"' in line:
        in_u1 = True
        print(f"U1 start at line {i}")
    elif in_u1:
        if line.startswith("  )") and not line.startswith("    )"):
            print(f"U1 end at line {i}")
            in_u1 = False
        elif any(k in line.lower() for k in ["zone", "keepout", "rule", "not_allowed", "fp_poly"]):
            print(f"{i}: {line.strip()[:100]}")
