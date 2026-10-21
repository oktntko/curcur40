import subprocess
import re

res = subprocess.run(["git", "diff", "a1f63483~1", "a1f63483", "--", "pcbs/curcur40/right/curcur40-right.kicad_pcb"], capture_output=True, text=True)
lines = res.stdout.splitlines()

added_segs = []
for i, l in enumerate(lines):
    if l.startswith('+') and '(segment' in l:
        # read the next lines of this segment
        seg_lines = [l]
        j = i + 1
        while j < len(lines) and not lines[j].startswith('+') and not lines[j].startswith(' ') and not lines[j].startswith('-'):
            pass
        # look ahead in lines
        blk = []
        for k in range(i, min(i+10, len(lines))):
            if lines[k].startswith('+'):
                blk.append(lines[k][1:].strip())
        blk_text = " ".join(blk)
        m_net = re.search(r'\(net\s+\"([^\"]+)\"\)', blk_text)
        net = m_net.group(1) if m_net else "?"
        m_start = re.search(r'\(start\s+([\d\.\-]+)\s+([\d\.\-]+)\)', blk_text)
        m_end = re.search(r'\(end\s+([\d\.\-]+)\s+([\d\.\-]+)\)', blk_text)
        m_layer = re.search(r'\(layer\s+\"([^\"]+)\"\)', blk_text)
        s = (m_start.group(1), m_start.group(2)) if m_start else ("", "")
        e = (m_end.group(1), m_end.group(2)) if m_end else ("", "")
        layer = m_layer.group(1) if m_layer else ""
        added_segs.append((net, layer, s, e))

print(f"Total added segments parsed: {len(added_segs)}")
nets_count = {}
for net, layer, s, e in added_segs:
    nets_count[net] = nets_count.get(net, 0) + 1
print("Added segments by net:")
for n, c in sorted(nets_count.items()):
    print(f"  {n:20}: {c} segments")

# Print some of each
for n in nets_count:
    example = [x for x in added_segs if x[0] == n][0]
    print(f"  Example {n}: {example[1]} from {example[2]} to {example[3]}")
