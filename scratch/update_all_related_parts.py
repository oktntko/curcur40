# -*- coding: utf-8 -*-
import pcbnew
import re
from pathlib import Path

print("=== 1. UPDATING PLATE-TOP-RIGHT.KICAD_PCB ===")
p_top = Path(r"plates/curcur40/pcb/plate-top-right.kicad_pcb")
b_top = pcbnew.LoadBoard(str(p_top))
edge_id = b_top.GetLayerID("Edge.Cuts")

# Shift trackball edge from X=22.837 to X=24.837 (+2.0mm)
# Arc 1: center at (23.837, 62.562) -> (25.837, 62.562), start (23.837, 63.562) -> (25.837, 63.562), end (22.837, 62.562) -> (24.837, 62.562)
# Line 1: (22.837, 62.562) -> (22.837, 38.400) => (24.837, 62.562) -> (24.837, 38.400)
# Arc 2: center at (21.837, 38.400) -> (23.837, 38.400), start (21.837, 37.400) -> (23.837, 37.400), end (22.837, 38.400) -> (24.837, 38.400)
# Line 2: (21.837, 37.400) -> (4.862, 37.400) => (23.837, 37.400) -> (4.862, 37.400)
# Bottom line: (82.062, 63.562) -> (23.837, 63.562) => (82.062, 63.562) -> (25.837, 63.562)

for dr in b_top.GetDrawings():
    if dr.GetLayer() == edge_id:
        shape = dr.GetShapeStr()
        if shape in ["Line", "Segment"]:
            s, e = dr.GetStart(), dr.GetEnd()
            sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
            ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)
            # Vertical cutout line
            if abs(sx - 22.837) < 0.1 and abs(ex - 22.837) < 0.1:
                dr.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(24.837), s.y))
                dr.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(24.837), e.y))
                print("Shifted vertical cutout line on plate-top-right")
            # Top horizontal line
            elif abs(sy - 37.400) < 0.1 and abs(ey - 37.400) < 0.1 and (max(sx, ex) > 20.0):
                if sx > ex:
                    dr.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(23.837), s.y))
                else:
                    dr.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(23.837), e.y))
                print("Updated top horizontal line on plate-top-right")
            # Bottom horizontal line
            elif abs(sy - 63.562) < 0.1 and abs(ey - 63.562) < 0.1 and (min(sx, ex) < 25.0):
                if sx < ex:
                    dr.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(25.837), s.y))
                else:
                    dr.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(25.837), e.y))
                print("Updated bottom horizontal line on plate-top-right")
        elif shape == "Arc":
            c, s, e = dr.GetCenter(), dr.GetStart(), dr.GetEnd()
            cx_a, cy_a = pcbnew.ToMM(c.x), pcbnew.ToMM(c.y)
            if abs(cy_a - 62.562) < 0.1 and abs(cx_a - 23.837) < 0.1:
                dr.SetCenter(pcbnew.VECTOR2I(pcbnew.FromMM(25.837), pcbnew.FromMM(cy_a)))
                dr.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(25.837), s.y))
                dr.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(24.837), e.y))
                print("Shifted bottom arc on plate-top-right")
            elif abs(cy_a - 38.400) < 0.1 and abs(cx_a - 21.837) < 0.1:
                dr.SetCenter(pcbnew.VECTOR2I(pcbnew.FromMM(23.837), pcbnew.FromMM(cy_a)))
                dr.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(23.837), s.y))
                dr.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(24.837), e.y))
                print("Shifted top arc on plate-top-right")

b_top.Save(str(p_top))
print("Saved plate-top-right.kicad_pcb")

print("\n=== 2. UPDATING PLATE-BOTTOM-RIGHT.KICAD_PCB ===")
p_bot = Path(r"plates/curcur40/pcb/plate-bottom-right.kicad_pcb")
b_bot = pcbnew.LoadBoard(str(p_bot))
edge_id_bot = b_bot.GetLayerID("Edge.Cuts")

# Shift trackball rectangular cutout by +2.0 mm:
# It spans X in [2.925, 12.125] -> new X in [4.925, 14.125]
for dr in b_bot.GetDrawings():
    if dr.GetLayer() == edge_id_bot:
        shape = dr.GetShapeStr()
        if shape in ["Line", "Segment"]:
            s, e = dr.GetStart(), dr.GetEnd()
            sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
            ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)
            if 2.0 <= sx <= 13.0 and 2.0 <= ex <= 13.0 and 42.0 <= sy <= 62.0 and 42.0 <= ey <= 62.0:
                dr.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(sx + 2.0), s.y))
                dr.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(ex + 2.0), e.y))
        elif shape == "Arc":
            c, s, e = dr.GetCenter(), dr.GetStart(), dr.GetEnd()
            cx_a, cy_a = pcbnew.ToMM(c.x), pcbnew.ToMM(c.y)
            if 2.0 <= cx_a <= 13.0 and 42.0 <= cy_a <= 62.0:
                dr.SetCenter(pcbnew.VECTOR2I(pcbnew.FromMM(cx_a + 2.0), c.y))
                dr.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(pcbnew.ToMM(s.x) + 2.0), s.y))
                dr.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(pcbnew.ToMM(e.x) + 2.0), e.y))

b_bot.Save(str(p_bot))
print("Saved plate-bottom-right.kicad_pcb")

print("\n=== 3. UPDATING SVG FILES ===")
# In plate-curcur40.svg:
# Top right plate has cutout: L 162.8375,68.4000 A 1.0000,1.0000 0 0 0 161.8375,67.4000
# 162.8375 -> 164.8375 (+2.0mm), 161.8375 -> 163.8375 (+2.0mm)
svg_plate = Path(r"plates/curcur40/svg/plate-curcur40.svg")
text = svg_plate.read_text(encoding="utf-8")
text_mod = text.replace("162.8375,68.4000", "164.8375,68.4000").replace("161.8375,67.4000", "163.8375,67.4000").replace("162.8375,92.5625", "164.8375,92.5625")
svg_plate.write_text(text_mod, encoding="utf-8")
print("Updated plate-curcur40.svg")

# In foam-curcur40.svg:
svg_foam = Path(r"plates/curcur40/svg/foam-curcur40.svg")
text_f = svg_foam.read_text(encoding="utf-8")
text_f_mod = text_f.replace("162.8375,73.4000", "164.8375,73.4000").replace("161.8375,72.4000", "163.8375,72.4000").replace("162.8375,97.5625", "164.8375,97.5625")
svg_foam.write_text(text_f_mod, encoding="utf-8")
print("Updated foam-curcur40.svg")
