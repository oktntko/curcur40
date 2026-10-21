import pcbnew
import subprocess
import json
from pathlib import Path

# Load clean baseline from git commit 20bc8a19
BASELINE_COMMIT = "20bc8a19"
TARGET_PCB = "scratch/test_solved.kicad_pcb"
TARGET_PRO = "scratch/test_solved.kicad_pro"
REPORT_JSON = "scratch/drc_solved.json"

# Dead stubs from removed header
DEAD_STUBS = [
    "7dd8caa0-e0ec-4328-9359-e11e838afc78",
    "cca78c47-6ed6-402a-881a-9ecabf679da4",
    "de626d39-723b-4d4f-a77f-be0d6917e35e",
    "0e592887-f89b-4cbd-bd9a-1a7c0ca4d07e",
    "5434aa9a-bec4-4cf9-a5b0-2d31b9914dc3",
    "5a65bc72-1bca-4713-ab6c-fda0404686bb",
    "8e50b458-c280-4c85-a9f4-899e27803557",
    "0421ef6a-b236-49f4-9838-11a9a193e74c",
    "2f81a7ee-c63c-4164-82db-1a629d2ea3fa",
    "c036dd03-31ee-4b11-ba6d-13255176dedc",
    "e720b2c2-879b-48cc-a258-589fb75e26bf",
    "f1c48cec-dc6c-4014-a0e7-04df29c943d2",
    "3272d24a-e03b-4ef4-bc4a-cfe7b4bc7771",
    "50feb961-ce63-4319-9f53-20f34c92782e",
    "74209c90-d7cb-4a69-89c0-697b2f062ea7",
    "a207e794-754c-4f20-923f-00ab0d23be1f",
    "e41e7fc7-a5aa-48df-847e-e05ac583225f",
    "342256ce-1564-4692-bc7f-580472c86144",
    "787d6e71-65b3-4a6f-b78e-a2d7d166ecda",
    "b8ad9be3-135d-4409-8aa0-06399dcef1c0",
    "c66cee38-fa84-4961-90b4-34ffc325a265",
    "f9ff5571-2a2f-47cf-a162-b81268f1b988",
    "641eb885-feb9-470d-a712-431b092d0147",
    "c100eb31-44bd-432a-a260-686177818298",
    "dabf49da-b110-4530-a011-a731221fd294",
    "e4ad1662-dc8d-4f41-abe5-a71459cf3c58",
]

txt = subprocess.check_output(["git", "show", f"{BASELINE_COMMIT}:pcbs/curcur40/right/curcur40-right.kicad_pcb"], encoding="utf-8")

def remove_by_uuid(content, u):
    idx = content.find(u)
    if idx == -1: return content
    start = content.rfind('(segment', 0, idx)
    if start == -1: start = content.rfind('(via', 0, idx)
    if start == -1: return content
    real_start = content.rfind('\n', 0, start)
    real_start = real_start + 1 if real_start != -1 else start
    depth, end = 0, start
    while end < len(content):
        if content[end] == '(': depth += 1
        elif content[end] == ')':
            depth -= 1
            if depth == 0: break
        end += 1
    if end + 1 < len(content) and content[end+1] == '\n':
        end += 1
    return content[:real_start] + content[end+1:]

for u in DEAD_STUBS:
    txt = remove_by_uuid(txt, u)

# Copy pro file if needed
pro_src = Path("pcbs/curcur40/right/curcur40-right.kicad_pro")
Path(TARGET_PRO).write_bytes(pro_src.read_bytes())
Path(TARGET_PCB).write_text(txt, encoding="utf-8")

board = pcbnew.LoadBoard(TARGET_PCB)

# Inspect what tracks currently exist for PMW nets in the baseline
pmw_netnames = {
    "/SCLK", "/MOSI", "/MISO", "/NCS", "/CS", "/RESET", 
    "+1V8_PMW", "V_{IO}", "Net-(U1-LED_P)", "Net-(U2-NC)"
}

# Remove existing tracks/vias belonging to PMW subcircuit to route from scratch cleanly
to_remove = []
for t in board.GetTracks():
    netname = t.GetNetname()
    if netname in pmw_netnames:
        p1 = t.GetStart() if hasattr(t, 'GetStart') else t.GetPosition()
        x = pcbnew.ToMM(p1.x)
        # Keep MCU entry lines coming from X > 25
        if x < 25:
            # Check if it's the external arrival line
            if netname == "/NCS" and t.GetClass() != "PCB_VIA":
                # Check coords
                p2 = t.GetEnd()
                if pcbnew.ToMM(p2.x) >= 20.0 and pcbnew.ToMM(p1.y) <= 40.3:
                    continue
            to_remove.append(t)

print(f"Removing {len(to_remove)} existing incomplete PMW tracks for clean reroute...")
for t in to_remove:
    board.Remove(t)

board.Save(TARGET_PCB)
print("Saved stripped board.")
