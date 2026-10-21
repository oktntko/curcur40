from pathlib import Path
import re

pcb = Path("pcbs/curcur40/right/curcur40-right.kicad_pcb").read_text(encoding="utf-8")

# Check all nets declared at the top of pcb
print("=== Nets in curcur40-right.kicad_pcb ===")
for m in re.finditer(r'\(net\s+(\d+)\s+\"([^\"]+)\"\)', pcb):
    net_id, net_name = m.group(1), m.group(2)
    if any(k in net_name.lower() for k in ['cs', 'ncs', 'spi', 'miso', 'mosi', 'sclk', 'reset', 'motion', '1v8', 'vin', 'vio', 'v_']):
        print(f"  net {net_id:3}: '{net_name}'")

# Check where /NCS and /CS connect
print("\n=== Check pads with /CS and /NCS ===")
for m in re.finditer(r'\(pad\s+\"([^\"]+)\"[^)]*\(net\s+\d+\s+\"([^\"]*CS[^\"]*)\"\)', pcb):
    print(m.group(0))
