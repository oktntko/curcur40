# -*- coding: utf-8 -*-
"""
Perfect update and DRC verification for both Right and Left PCBs.
- Restore TRRS mid-mount cutouts on Edge.Cuts
- Remove all legacy Corne switch-matrix mounting holes
- Add new perimeter mounting holes:
  Right (3 holes): (+114.0, -20.0), (+2.0, -20.0), (+114.3, +37.0)
  Left (4 holes):  (-114.0, -20.0), (-2.0, -20.0), (-114.3, +37.0), (-2.0, +64.0)
- Cleanly route /TX on F.Cu around the TRRS cutout
- Refill copper zones and verify 0 DRC violations and 0 unconnected pads on both boards!
"""
import math
import subprocess
import pcbnew

KICAD_CLI = r"C:\Users\oktnt\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe"

def mm(val):
    return pcbnew.FromMM(float(val))

def pt(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))

def add_track_path(board, net_item, layer, pts, width=0.25):
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        if abs(x1 - x2) < 1e-5 and abs(y1 - y2) < 1e-5:
            continue
        t = pcbnew.PCB_TRACK(board)
        t.SetLayer(layer)
        t.SetStart(pt(x1, y1))
        t.SetEnd(pt(x2, y2))
        t.SetWidth(mm(width))
        board.Add(t)
        t.SetNet(net_item)

def add_via(board, net_item, x, y, drill=0.30, size=0.50):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pt(x, y))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetDrill(mm(drill))
    v.SetWidth(mm(size))
    board.Add(v)
    v.SetNet(net_item)

def add_line(board, x1, y1, x2, y2, layer=pcbnew.Edge_Cuts, width=0.10):
    sh = pcbnew.PCB_SHAPE(board)
    sh.SetShape(pcbnew.SHAPE_T_SEGMENT)
    sh.SetLayer(layer)
    sh.SetStart(pt(x1, y1))
    sh.SetEnd(pt(x2, y2))
    sh.SetWidth(mm(width))
    board.Add(sh)

def add_arc_90(board, x1, y1, x2, y2, cx, cy, layer=pcbnew.Edge_Cuts, width=0.10):
    sh = pcbnew.PCB_SHAPE(board)
    sh.SetShape(pcbnew.SHAPE_T_ARC)
    sh.SetLayer(layer)
    ang1 = math.atan2(y1 - cy, x1 - cx)
    ang2 = math.atan2(y2 - cy, x2 - cx)
    diff = (ang2 - ang1 + math.pi) % (2 * math.pi) - math.pi
    mid_ang = ang1 + diff / 2.0
    r = math.hypot(x1 - cx, y1 - cy)
    mx = cx + r * math.cos(mid_ang)
    my = cy + r * math.sin(mid_ang)
    sh.SetArcGeometry(pt(x1, y1), pt(mx, my), pt(x2, y2))
    sh.SetWidth(mm(width))
    board.Add(sh)

def add_circle(board, cx, cy, r, layer=pcbnew.Edge_Cuts, width=0.10):
    c = pcbnew.PCB_SHAPE(board)
    c.SetShape(pcbnew.SHAPE_T_CIRCLE)
    c.SetLayer(layer)
    c.SetCenter(pt(cx, cy))
    c.SetEnd(pt(cx + r, cy))
    c.SetWidth(mm(width))
    board.Add(c)

def update_right_pcb():
    pcb_path = r"pcbs\curcur40\right\curcur40-right.kicad_pcb"
    board = pcbnew.LoadBoard(pcb_path)
    nets = {net.GetNetname(): net for net in board.GetNetsByName().values()}

    F_Cu = pcbnew.F_Cu
    B_Cu = pcbnew.B_Cu

    # 1. Clean tracks and vias around rJ2 in x in [-6, 26], y in [28, 44]
    to_delete = []
    for t in board.GetTracks():
        net = t.GetNetname()
        s, e = t.GetStart(), t.GetEnd()
        sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
        ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)

        if net in ["/TX", "+5VR"] and min(sx, ex) < 26.0 and max(sx, ex) > -6.0 and min(sy, ey) < 44.0 and max(sy, ey) > 28.0:
            to_delete.append(t)

        # Move the GNDR via near (112.5625, 36.82625)
        if net == "GNDR" and abs(sx - 112.5625) < 0.2 and abs(sy - 36.82625) < 0.2:
            to_delete.append(t)

    for t in to_delete:
        board.Delete(t)
    print(f"Right: Deleted {len(to_delete)} tracks/vias.")

    # Re-add GNDR via shifted west to x = 111.5625 (connected to rSW16 Pad 2 at 112.6375)
    add_via(board, nets["GNDR"], 111.5625, 36.82625, drill=0.30, size=0.50)
    add_track_path(board, nets["GNDR"], B_Cu, [(112.6375, 36.85625), (111.5625, 36.82625)], width=0.25)

    # 2. Re-wire +5VR
    # Top Pad T (B.Cu) at (6.5425, 30.74625) -> (8.5000, 30.5960) -> via -> (24.2675, 30.5963)
    add_track_path(board, nets["+5VR"], B_Cu, [(6.5425, 30.74625), (8.5000, 30.5960)], width=0.40)
    add_via(board, nets["+5VR"], 8.5000, 30.5960, drill=0.30, size=0.50)
    add_track_path(board, nets["+5VR"], F_Cu, [(8.5000, 30.5960), (24.2675, 30.5963)], width=0.40)

    # Bottom Pad T (B.Cu) at (6.5425, 38.54625) -> (8.5000, 38.6962) -> via -> (24.0262, 38.6962)
    add_track_path(board, nets["+5VR"], B_Cu, [(6.5425, 38.54625), (8.5000, 38.6962)], width=0.40)
    add_via(board, nets["+5VR"], 8.5000, 38.6962, drill=0.30, size=0.50)
    add_track_path(board, nets["+5VR"], F_Cu, [(8.5000, 38.6962), (24.0262, 38.6962)], width=0.40)

    # 3. Re-wire /TX
    # Top Pad R (0.7425, 30.74625) bridges to Bottom Pad R (0.7425, 38.54625) via F.Cu bypass
    # Cutout ends at x = 7.7425. We route east to x = 9.4000 at y = 30.74625, down to y = 38.54625, and back west.
    add_track_path(board, nets["/TX"], F_Cu, [
        (0.7425, 30.74625),
        (9.4000, 30.74625),
        (9.4000, 38.54625),
        (0.7425, 38.54625),
    ], width=0.25)

    # Connect to the rest of /TX circuit:
    # From Bottom Pad R (0.7425, 38.54625), via or track:
    # Route on F.Cu to (15.5000, 38.54625) -> (15.5000, 42.4160), via to B.Cu -> (23.5749, 42.4162) -> (25.1908, 40.8004)
    add_track_path(board, nets["/TX"], F_Cu, [
        (9.4000, 38.54625),
        (15.5000, 38.54625),
        (15.5000, 42.4160),
    ], width=0.25)
    add_via(board, nets["/TX"], 15.5000, 42.4160, drill=0.30, size=0.50)
    add_track_path(board, nets["/TX"], B_Cu, [
        (15.5000, 42.4160),
        (23.5749, 42.4162),
        (25.1908, 40.8004),
    ], width=0.25)

    # 4. Clean and rebuild Edge.Cuts
    drawings_to_delete = []
    for d in board.GetDrawings():
        if d.GetLayerName() == "Edge.Cuts":
            if d.GetShapeStr() == "Circle":
                pos = d.GetPosition()
                px, py = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
                # Keep optical window at (9.525, 52.3875)
                if abs(px - 9.525) < 0.1 and abs(py - 52.3875) < 0.1:
                    continue
            drawings_to_delete.append(d)

    for d in drawings_to_delete:
        board.Remove(d)

    R = 1.0  # Corner radius

    # Top edge with USB cutout
    add_arc_90(board, -5.2625, -24.3125 + R, -5.2625 + R, -24.3125, -5.2625 + R, -24.3125 + R)
    add_line(board, -5.2625 + R, -24.3125, 7.6175, -24.3125)
    usb_cut_bottom = -24.3125 + 5.8025  # -18.5100
    add_line(board, 7.6175, -24.3125, 7.6175, usb_cut_bottom)
    add_line(board, 7.6175, usb_cut_bottom, 16.8575, usb_cut_bottom)
    add_line(board, 16.8575, usb_cut_bottom, 16.8575, -24.3125)
    add_line(board, 16.8575, -24.3125, 119.0625 - R, -24.3125)
    add_arc_90(board, 119.0625 - R, -24.3125, 119.0625, -24.3125 + R, 119.0625 - R, -24.3125 + R)

    # Pinky right edge
    add_line(board, 119.0625, -24.3125 + R, 119.0625, 40.98125 - R)
    add_arc_90(board, 119.0625, 40.98125 - R, 119.0625 - R, 40.98125, 119.0625 - R, 40.98125 - R)

    # Pinky bottom step
    add_line(board, 119.0625 - R, 40.98125, 82.4625 + R, 40.98125)
    add_arc_90(board, 82.4625 + R, 40.98125, 82.4625, 40.98125 + R, 82.4625 + R, 40.98125 + R)

    # Thumb right step
    add_line(board, 82.4625, 40.98125 + R, 82.4625, 67.500 - R)
    add_arc_90(board, 82.4625, 67.500 - R, 82.4625 - R, 67.500, 82.4625 - R, 67.500 - R)

    # Bottom edge
    add_line(board, 82.4625 - R, 67.500, -5.2625 + R, 67.500)
    add_arc_90(board, -5.2625 + R, 67.500, -5.2625, 67.500 - R, -5.2625 + R, 67.500 - R)

    # Left edge with TRRS Cutout
    add_line(board, -5.2625, 67.500 - R, -5.2625, 37.800)
    add_line(board, -5.2625, 37.800, 7.7425, 37.800)
    add_line(board, 7.7425, 37.800, 7.7425, 31.500)
    add_line(board, 7.7425, 31.500, -5.2625, 31.500)
    add_line(board, -5.2625, 31.500, -5.2625, -24.3125 + R)

    # 3 new perimeter mounting holes (diameter 2.2 mm -> r = 1.1 mm)
    new_holes = [
        (114.0, -20.0),
        (2.0, -20.0),
        (114.3, 37.0),
    ]
    for hx, hy in new_holes:
        add_circle(board, hx, hy, 1.10)

    # Refill zones
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    board.Save(pcb_path)
    print("Right PCB saved.")

    # DRC
    rpt = r"scratch\drc_right_final.rpt"
    subprocess.run([KICAD_CLI, "pcb", "drc", "-o", rpt, pcb_path], check=True)
    with open(rpt, "r", encoding="utf-8") as f:
        txt = f.read()
    print("=== RIGHT PCB DRC ===")
    for l in txt.splitlines():
        if "violations" in l or "unconnected" in l or "Error" in l:
            print(" ", l)

def update_left_pcb():
    pcb_path = r"pcbs\curcur40\left\curcur40-left.kicad_pcb"
    board = pcbnew.LoadBoard(pcb_path)
    nets = {net.GetNetname(): net for net in board.GetNetsByName().values()}

    F_Cu = pcbnew.F_Cu
    B_Cu = pcbnew.B_Cu

    # 1. Clean tracks and vias around J2 in x in [-12, 6], y in [28, 44]
    to_delete = []
    for t in board.GetTracks():
        net = t.GetNetname()
        s, e = t.GetStart(), t.GetEnd()
        sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
        ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)

        # /TX track crossing cutout
        if net == "/TX" and min(sx, ex) > -2.0 and max(sx, ex) < 2.0 and min(sy, ey) < 38.6 and max(sy, ey) > 30.7:
            to_delete.append(t)

        # +5V track crossing cutout
        if net == "+5V" and abs(sx - (-6.5425)) < 0.1 and abs(ex - (-6.5425)) < 0.1 and min(sy, ey) < 38.6 and max(sy, ey) > 30.7:
            to_delete.append(t)

    for t in to_delete:
        board.Delete(t)
    print(f"Left: Deleted {len(to_delete)} tracks crossing cutout.")

    # 2. Bridge /TX around TRRS cutout on F.Cu:
    # J2 is at x = +5.2575. Cutout extends west to x = -7.7425.
    # Top Pad R is at (-0.7425, 30.74625), bottom Pad R is at (-0.7425, 38.54625).
    # Route west on F.Cu to x = -9.4000 at y = 30.74625, down to y = 38.54625, and back east to bottom Pad R.
    add_track_path(board, nets["/TX"], F_Cu, [
        (-0.7425, 30.74625),
        (-9.4000, 30.74625),
        (-9.4000, 38.54625),
        (-0.7425, 38.54625),
    ], width=0.25)

    # 3. Clean and rebuild Edge.Cuts
    drawings_to_delete = []
    for d in board.GetDrawings():
        if d.GetLayerName() == "Edge.Cuts":
            drawings_to_delete.append(d)

    for d in drawings_to_delete:
        board.Remove(d)

    R = 1.0  # Corner radius

    # Top edge with USB cutout
    add_arc_90(board, -119.0625, -24.3125 + R, -119.0625 + R, -24.3125, -119.0625 + R, -24.3125 + R)
    add_line(board, -119.0625 + R, -24.3125, -16.8575, -24.3125)
    usb_cut_bottom = -24.3125 + 5.8025  # -18.5100
    add_line(board, -16.8575, -24.3125, -16.8575, usb_cut_bottom)
    add_line(board, -16.8575, usb_cut_bottom, -7.6175, usb_cut_bottom)
    add_line(board, -7.6175, usb_cut_bottom, -7.6175, -24.3125)
    add_line(board, -7.6175, -24.3125, 5.2625 - R, -24.3125)
    add_arc_90(board, 5.2625 - R, -24.3125, 5.2625, -24.3125 + R, 5.2625 - R, -24.3125 + R)

    # Right edge with TRRS Cutout
    add_line(board, 5.2625, -24.3125 + R, 5.2625, 31.500)
    add_line(board, 5.2625, 31.500, -7.7425, 31.500)
    add_line(board, -7.7425, 31.500, -7.7425, 37.800)
    add_line(board, -7.7425, 37.800, 5.2625, 37.800)
    add_line(board, 5.2625, 37.800, 5.2625, 67.500 - R)
    add_arc_90(board, 5.2625, 67.500 - R, 5.2625 - R, 67.500, 5.2625 - R, 67.500 - R)

    # Bottom edge
    add_line(board, 5.2625 - R, 67.500, -82.4625 + R, 67.500)
    add_arc_90(board, -82.4625 + R, 67.500, -82.4625, 67.500 - R, -82.4625 + R, 67.500 - R)

    # Thumb left step
    add_line(board, -82.4625, 67.500 - R, -82.4625, 40.98125 + R)
    add_arc_90(board, -82.4625, 40.98125 + R, -82.4625 - R, 40.98125, -82.4625 - R, 40.98125 + R)

    # Pinky bottom step
    add_line(board, -82.4625 - R, 40.98125, -119.0625 + R, 40.98125)
    add_arc_90(board, -119.0625 + R, 40.98125, -119.0625, 40.98125 - R, -119.0625 + R, 40.98125 - R)

    # Pinky left edge
    add_line(board, -119.0625, 40.98125 - R, -119.0625, -24.3125 + R)

    # 4 new perimeter mounting holes (diameter 2.2 mm -> r = 1.1 mm)
    new_holes = [
        (-114.0, -20.0),
        (-2.0, -20.0),
        (-114.3, 37.0),
        (-2.0, 64.0),
    ]
    for hx, hy in new_holes:
        add_circle(board, hx, hy, 1.10)

    # Refill zones
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    board.Save(pcb_path)
    print("Left PCB saved.")

    # DRC
    rpt = r"scratch\drc_left_final.rpt"
    subprocess.run([KICAD_CLI, "pcb", "drc", "-o", rpt, pcb_path], check=True)
    with open(rpt, "r", encoding="utf-8") as f:
        txt = f.read()
    print("=== LEFT PCB DRC ===")
    for l in txt.splitlines():
        if "violations" in l or "unconnected" in l or "Error" in l:
            print(" ", l)

if __name__ == "__main__":
    update_right_pcb()
    update_left_pcb()
