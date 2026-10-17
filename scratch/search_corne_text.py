# -*- coding: utf-8 -*-
"""
Search for "corne", "foostan", "crkbd", "chocolate" in PCBs and schematics.
"""
import glob
import re
from pathlib import Path
import pcbnew

WORKSPACE = Path(r"c:\Users\oktnt\workspace\curcur40")
PATTERNS = ["corne", "foostan", "crkbd", "chocolate", "kosuke"]

def search_pcbs():
    print("==================================================")
    print("SEARCHING PCBS FOR CORNE / FOOSTAN / AUTHOR TEXT")
    print("==================================================")
    for pcb_path in (
        list(WORKSPACE.glob("pcbs/curcur40/**/*.kicad_pcb")) +
        list(WORKSPACE.glob("plates/curcur40/**/*.kicad_pcb"))
    ):
        rel = pcb_path.relative_to(WORKSPACE)
        b = pcbnew.LoadBoard(str(pcb_path))
        found = []

        # Drawings / text items on board
        for dr in b.GetDrawings():
            if hasattr(dr, "GetText"):
                txt = dr.GetText()
                if any(p in txt.lower() for p in PATTERNS):
                    layer = b.GetLayerName(dr.GetLayer())
                    pos = dr.GetPosition()
                    found.append(f"[Board Text] '{txt}' on layer {layer} at ({pcbnew.ToMM(pos.x):.2f}, {pcbnew.ToMM(pos.y):.2f})")

        # Footprints text or graphics
        for fp in b.GetFootprints():
            ref = fp.GetReference()
            val = fp.GetValue()
            if any(p in val.lower() for p in PATTERNS):
                found.append(f"[Footprint {ref} Value] '{val}'")
            for item in fp.GraphicalItems():
                if hasattr(item, "GetText"):
                    txt = item.GetText()
                    if any(p in txt.lower() for p in PATTERNS):
                        layer = b.GetLayerName(item.GetLayer())
                        pos = item.GetPosition()
                        found.append(f"[Footprint {ref} GraphicText] '{txt}' on layer {layer} at ({pcbnew.ToMM(pos.x):.2f}, {pcbnew.ToMM(pos.y):.2f})")

        # Title block
        tb = b.GetTitleBlock()
        for idx, f in enumerate([tb.GetTitle(), tb.GetCompany(), tb.GetComment(0), tb.GetComment(1), tb.GetComment(2), tb.GetComment(3)]):
            if f and any(p in f.lower() for p in PATTERNS):
                found.append(f"[Title Block] field {idx}: '{f}'")

        if found:
            print(f"\n--- {rel} ---")
            for item in found:
                print(f"  * {item}")

def search_text_files():
    print("\n==================================================")
    print("SEARCHING SCHEMATICS AND PROJECT FILES")
    print("==================================================")
    exts = ["*.kicad_sch", "*.kicad_pro", "*.kicad_pcb"]
    files = []
    for ext in exts:
        files.extend(list(WORKSPACE.glob(f"pcbs/curcur40/**/{ext}")))
        files.extend(list(WORKSPACE.glob(f"plates/curcur40/**/{ext}")))

    for f in sorted(set(files)):
        rel = f.relative_to(WORKSPACE)
        content = f.read_text(encoding="utf-8", errors="ignore")
        matches = []
        for line_num, line in enumerate(content.splitlines(), 1):
            # Exclude fp-lib-table paths or library symbol names if they are just paths
            for p in PATTERNS:
                if p in line.lower():
                    # clean display
                    l_str = line.strip()
                    if len(l_str) > 100:
                        l_str = l_str[:97] + "..."
                    matches.append((line_num, p, l_str))
        if matches:
            print(f"\n--- {rel} ({len(matches)} match(es)) ---")
            for l_num, p, l_str in matches[:15]:
                print(f"  Line {l_num:5d} [{p}]: {l_str}")
            if len(matches) > 15:
                print(f"  ... and {len(matches) - 15} more matches.")

if __name__ == "__main__":
    search_pcbs()
    search_text_files()
