# -*- coding: utf-8 -*-
import pcbnew
import json

board = pcbnew.LoadBoard(r"scratch/test_right_pcb.kicad_pcb")

data = {
    "tracks": [],
    "vias": [],
    "drawings": [],
    "holes": [],
    "fps": []
}

edge_id = board.GetLayerID("Edge.Cuts")
f_cu = board.GetLayerID("F.Cu")
b_cu = board.GetLayerID("B.Cu")

for dr in board.GetDrawings():
    if dr.GetLayer() == edge_id:
        shape = dr.GetShapeStr()
        if shape in ["Line", "Segment"]:
            s, e = dr.GetStart(), dr.GetEnd()
            data["drawings"].append({
                "type": "line",
                "start": [pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)],
                "end": [pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)],
            })
        elif shape == "Arc":
            c, s, e = dr.GetCenter(), dr.GetStart(), dr.GetEnd()
            data["drawings"].append({
                "type": "arc",
                "center": [pcbnew.ToMM(c.x), pcbnew.ToMM(c.y)],
                "radius": pcbnew.ToMM(dr.GetRadius())
            })
        elif shape == "Circle":
            c = dr.GetCenter()
            data["drawings"].append({
                "type": "circle",
                "center": [pcbnew.ToMM(c.x), pcbnew.ToMM(c.y)],
                "radius": pcbnew.ToMM(dr.GetRadius())
            })

for tr in board.GetTracks():
    if tr.GetClass() == "PCB_TRACK":
        s, e = tr.GetStart(), tr.GetEnd()
        data["tracks"].append({
            "net": tr.GetNetname(),
            "layer": "F.Cu" if tr.GetLayer() == f_cu else "B.Cu",
            "start": [pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)],
            "end": [pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)],
            "width": pcbnew.ToMM(tr.GetWidth())
        })
    elif tr.GetClass() == "PCB_VIA":
        p = tr.GetPosition()
        data["vias"].append([pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)])

for fp in board.GetFootprints():
    ref = fp.GetReference()
    pos = fp.GetPosition()
    px, py = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
    data["fps"].append({"ref": ref, "pos": [px, py]})
    for pad in fp.Pads():
        pp = pad.GetPosition()
        dr = pcbnew.ToMM(pad.GetDrillSize().x)
        if dr > 0:
            data["holes"].append({
                "ref": ref,
                "pos": [pcbnew.ToMM(pp.x), pcbnew.ToMM(pp.y)],
                "drill": dr
            })

with open("scratch/pcb_plot_data.json", "w") as f:
    json.dump(data, f)
print("Dumped PCB plot data to scratch/pcb_plot_data.json")
