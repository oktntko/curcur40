from pathlib import Path

sch = Path("pcbs/curcur40/right/curcur40-right.kicad_sch").read_text(encoding="utf-8")
open_parens = sch.count('(')
close_parens = sch.count(')')
print(f"Open: {open_parens}, Close: {close_parens}, Diff: {open_parens - close_parens}")
