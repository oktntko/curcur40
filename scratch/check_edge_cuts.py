with open(r"pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pcb", "r", encoding="utf-8") as f:
    lines = f.readlines()

print("Lines mentioning Edge.Cuts:")
for i, line in enumerate(lines, 1):
    if "Edge.Cuts" in line:
        # print surrounding 5 lines
        start = max(0, i - 3)
        end = min(len(lines), i + 3)
        print(f"--- line {i} ---")
        for j in range(start, end):
            print(f"{j+1}: {lines[j].rstrip()}")
