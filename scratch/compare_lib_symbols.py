from pathlib import Path
import re

pmw_sch = Path("pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_sch").read_text(encoding="utf-8")
right_sch = Path("pcbs/curcur40/right/curcur40-right.kicad_sch").read_text(encoding="utf-8")

def get_lib_symbols(text):
    pos = text.find("(lib_symbols")
    if pos == -1: return {}
    # find all (symbol "name" ...) inside lib_symbols
    count = 0
    end = pos
    while end < len(text):
        if text[end] == '(': count += 1
        elif text[end] == ')':
            count -= 1
            if count == 0: break
        end += 1
    lib_blk = text[pos:end+1]
    # find top-level symbols inside lib_symbols
    syms = {}
    idx = len("(lib_symbols")
    while True:
        s_pos = lib_blk.find("(symbol ", idx)
        if s_pos == -1: break
        c, s_end = 0, s_pos
        while s_end < len(lib_blk):
            if lib_blk[s_end] == '(': c += 1
            elif lib_blk[s_end] == ')':
                c -= 1
                if c == 0: break
            s_end += 1
        s_blk = lib_blk[s_pos:s_end+1]
        idx = s_end + 1
        m_name = re.match(r'\(symbol\s+\"([^\"]+)\"', s_blk)
        if m_name:
            syms[m_name.group(1)] = s_blk
    return syms

pmw_syms = get_lib_symbols(pmw_sch)
right_syms = get_lib_symbols(right_sch)

print("Symbols in PMW lib_symbols:")
for k in pmw_syms:
    in_right = k in right_syms
    print(f"  {k:40} | In right sch: {in_right}")
