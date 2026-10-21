import pcbnew

pcb_pmw = pcbnew.LoadBoard("scratch/pmw3360_pcb_b9043a22.kicad_pcb")
pcb_right = pcbnew.LoadBoard("pcbs/curcur40/right/curcur40-right.kicad_pcb")

fps = ["U1", "U2", "JP1", "R1", "R2", "R3", "R4", "C1", "C2", "C3", "C4", "C5"]

u1_p = pcb_pmw.FindFootprintByReference("U1").GetPosition()
u1_r = pcb_right.FindFootprintByReference("U1").GetPosition()

all_pass = True
max_err = 0.0

for ref in fps:
    fp_p = pcb_pmw.FindFootprintByReference(ref)
    fp_r = pcb_right.FindFootprintByReference(ref)
    for pad_p in fp_p.Pads():
        num = pad_p.GetNumber()
        pad_r = fp_r.FindPadByNumber(num)
        if not pad_r:
            print(f"ERROR: {ref} Pad {num} not found in Right")
            all_pass = False
            continue
        pos_p = pad_p.GetPosition()
        pos_r = pad_r.GetPosition()

        # Transform:
        # X_right = X_u1_r - (X_p - X_u1_p)
        # Y_right = Y_u1_r + (Y_p - Y_u1_p)
        calc_x = pcbnew.ToMM(u1_r.x) - (pcbnew.ToMM(pos_p.x) - pcbnew.ToMM(u1_p.x))
        calc_y = pcbnew.ToMM(u1_r.y) + (pcbnew.ToMM(pos_p.y) - pcbnew.ToMM(u1_p.y))

        actual_x = pcbnew.ToMM(pos_r.x)
        actual_y = pcbnew.ToMM(pos_r.y)

        err_x = abs(calc_x - actual_x)
        err_y = abs(calc_y - actual_y)
        max_err = max(max_err, err_x, err_y)
        if err_x > 0.001 or err_y > 0.001:
            print(f"MISMATCH {ref} Pad {num}: calc=({calc_x:.4f}, {calc_y:.4f}) vs actual=({actual_x:.4f}, {actual_y:.4f}) err=({err_x:.4f}, {err_y:.4f})")
            all_pass = False

print(f"All pads match: {all_pass}, Max error: {max_err:.6f} mm")
