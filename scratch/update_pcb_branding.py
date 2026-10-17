# -*- coding: utf-8 -*-
"""
Replace corne-logo footprint on left PCB with "curcur40" silkscreen text.
Update title blocks on left and right PCBs.
"""
import pcbnew
from pathlib import Path

WORKSPACE = Path(r"c:\Users\oktnt\workspace\curcur40")

def update_left_pcb():
    pcb_path = WORKSPACE / "pcbs" / "curcur40" / "left" / "curcur40-left.kicad_pcb"
    b = pcbnew.LoadBoard(str(pcb_path))
    
    # 1. Remove footprint G*** (corne-logo-horizontal)
    fp = b.FindFootprintByReference("G***")
    if fp:
        pos = fp.GetPosition()
        gx, gy = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
        print(f"Removing G*** ({fp.GetFPIDAsString()}) at ({gx:.4f}, {gy:.4f})")
        b.Delete(fp)
    else:
        gx, gy = -90.4875, 38.98125

    # 2. Add "curcur40" text on F.SilkS
    txt = pcbnew.PCB_TEXT(b)
    txt.SetText("curcur40")
    txt.SetLayer(b.GetLayerID("F.SilkS"))
    txt.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(gx), pcbnew.FromMM(gy)))
    txt.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.6), pcbnew.FromMM(1.6)))
    txt.SetTextThickness(pcbnew.FromMM(0.25))
    txt.SetBold(True)
    txt.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
    txt.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
    b.Add(txt)
    print("Added 'curcur40' text on F.SilkS")

    # 3. Update Title Block
    tb = b.GetTitleBlock()
    tb.SetTitle("curcur40 Left")
    tb.SetCompany("curcur40")
    print(f"Updated Left Title Block: {tb.GetTitle()} / {tb.GetCompany()}")

    b.Save(str(pcb_path))
    print("Saved curcur40-left.kicad_pcb")

def update_right_pcb():
    pcb_path = WORKSPACE / "pcbs" / "curcur40" / "right" / "curcur40-right.kicad_pcb"
    b = pcbnew.LoadBoard(str(pcb_path))
    
    tb = b.GetTitleBlock()
    tb.SetTitle("curcur40 Right")
    tb.SetCompany("curcur40")
    print(f"Updated Right Title Block: {tb.GetTitle()} / {tb.GetCompany()}")

    b.Save(str(pcb_path))
    print("Saved curcur40-right.kicad_pcb")

if __name__ == "__main__":
    update_left_pcb()
    update_right_pcb()
