from pathlib import Path
import re

sch = Path("pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_sch").read_text(encoding="utf-8")

# Extract the exact symbol definitions from (lib_symbols ...)
pos_lib = sch.find("(lib_symbols")
end_lib = sch.find(")\n\t(symbol\n") # end of lib_symbols

lib_text = sch[pos_lib:end_lib+1]

for sym_name in ["PMW3360_PCB:PMW3360DM-T2QU", "PMW3360_PCB:TLV74318PDBVR", "Jumper:SolderJumper_3_Open"]:
    pos = lib_text.find(f'(symbol "{sym_name}"')
    if pos == -1:
        print(f"NOT FOUND: {sym_name}")
        continue
    count, end = 0, pos
    while end < len(lib_text):
        if lib_text[end] == '(': count += 1
        elif lib_text[end] == ')':
            count -= 1
            if count == 0: break
        end += 1
    print(f"=== {sym_name} ===")
    print(lib_text[pos:pos+300])
    print(f"Length of {sym_name} definition: {end - pos} chars\n")
