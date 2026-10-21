import pcbnew

b = pcbnew.LoadBoard("pcbs/curcur40/right/curcur40-right.kicad_pcb")

ru1 = b.FindFootprintByReference("rU1")
p1 = ru1.FindPadByNumber("1")
print("rU1 Pad 1 local solder mask margin:", p1.GetLocalSolderMaskMargin())

u2 = b.FindFootprintByReference("U2")
p1_u2 = u2.FindPadByNumber("1")
print("U2 Pad 1 local solder mask margin:", p1_u2.GetLocalSolderMaskMargin())

# Let's inspect the actual text of rU1 in kicad_pcb
with open("pcbs/curcur40/right/curcur40-right.kicad_pcb", encoding="utf-8") as f:
    txt = f.read()

def print_fp_snippet(ref):
    idx = txt.find(f'(fp_text reference "{ref}"')
    if idx == -1: return
    start = txt.rfind('(footprint', 0, idx)
    end = txt.find('(pad "1"', start)
    end_pad = txt.find('\n\t\t)', end)
    print(f"=== {ref} ===")
    print(txt[start:end_pad+5])

print_fp_snippet("rU1")
print_fp_snippet("U2")
print_fp_snippet("JP1")
