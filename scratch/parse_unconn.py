from pathlib import Path
rpt = Path(r"c:\Users\oktnt\workspace\curcur40\scratch\drc_clean_pmw.rpt").read_text(encoding='utf-8')
lines = rpt.splitlines()
items = []
curr = []
for l in lines:
    if '[unconnected_items]' in l:
        if curr: items.append('\n'.join(curr))
        curr = [l]
    elif curr and (l.startswith('    ') or l.startswith('@')):
        curr.append(l)
if curr: items.append('\n'.join(curr))
print(f"Total: {len(items)}")
for i, it in enumerate(items):
    print(f"=== {i+1} ===")
    print(it)
