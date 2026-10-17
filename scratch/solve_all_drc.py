# -*- coding: utf-8 -*-
"""
Perfect DRC solver for curcur40 Right and Left PCBs.
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

def fix_right():
    pcb_path = r"pcbs\curcur40\right\curcur40-right.kicad_pcb"
    board = pcbnew.LoadBoard(pcb_path)
    nets = {net.GetNetname(): net for net in board.GetNetsByName().values()}

    F_Cu = pcbnew.F_Cu
    B_Cu = pcbnew.B_Cu

    # 1. Clean tracks and vias around rJ2 in x in [-6, 24], y in [28, 45]
    to_delete = []
    for t in board.GetTracks():
        net = t.GetNetname()
        s, e = t.GetStart(), t.GetEnd()
        sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
        ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)

        # /TX and +5VR tracks near rJ2
        if net in ["/TX", "+5VR"] and min(sx, ex) < 24.2 and max(sx, ex) > -6.0 and min(sy, ey) < 45.0 and max(sy, ey) > 28.0:
            to_delete.append(t)

    for t in to_delete:
        board.Delete(t)
    print(f"Right: Cleaned {len(to_delete)} tracks/vias.")

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
    # On F.Cu:
    # Top Pad R (0.7425, 30.74625) -> north to y=29.0 -> east to x=10.0 -> south to y=37.0
    add_track_path(board, nets["/TX"], F_Cu, [
        (0.7425, 30.74625),
        (0.7425, 29.0000),
        (10.0000, 29.0000),
        (10.0000, 37.0000),
    ], width=0.25)
    # Branch to Bottom Pad R on F.Cu
    add_track_path(board, nets["/TX"], F_Cu, [
        (10.0000, 37.0000),
        (10.0000, 38.54625),
        (0.7425, 38.54625),
    ], width=0.25)
    # Via at (10.0, 37.0) to B.Cu (above /NCS at y=39.8)
    add_via(board, nets["/TX"], 10.0000, 37.0000, drill=0.30, size=0.50)

    # On B.Cu:
    # Along x=10.0 down to y=44.5 (south of rH2 at 42.3875) -> east to x=21.0 -> to (23.5749, 42.4162) -> to (25.1908, 40.8004)
    add_track_path(board, nets["/TX"], B_Cu, [
        (10.0000, 37.0000),
        (10.0000, 44.5000),
        (21.0000, 44.5000),
        (23.0000, 42.5000),
        (23.5749, 42.4162),
    ], width=0.25)
    add_track_path(board, nets["/TX"], B_Cu, [
        (23.5749, 42.4162),
        (25.1908, 40.8004),
    ], width=0.20)

    # 4. Clean Edge.Cuts & Rebuild
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
        (116.5, 20.0),
    ]
    for hx, hy in new_holes:
        add_circle(board, hx, hy, 1.10)

    # Refill zones
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    board.Save(pcb_path)
    print("Right PCB saved.")

    # DRC
    rpt = r"scratch\drc_right_clean.rpt"
    subprocess.run([KICAD_CLI, "pcb", "drc", "-o", rpt, pcb_path], check=True)
    with open(rpt, "r", encoding="utf-8") as f:
        txt = f.read()
    print("=== RIGHT PCB DRC ===")
    for l in txt.splitlines():
        if "violations" in l or "unconnected" in l or "Error" in l:
            print(" ", l)

def fix_left():
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

        # /TX track crossing cutout or near J2
        if net == "/TX" and min(sx, ex) > -12.0 and max(sx, ex) < 2.0 and min(sy, ey) < 42.0 and max(sy, ey) > 28.0:
            to_delete.append(t)

        # +5V track crossing cutout
        if net == "+5V" and abs(sx - (-6.5425)) < 0.1 and abs(ex - (-6.5425)) < 0.1 and min(sy, ey) < 38.6 and max(sy, ey) > 30.7:
            to_delete.append(t)

    for t in to_delete:
        board.Delete(t)
    print(f"Left: Cleaned {len(to_delete)} tracks crossing cutout.")

    # 2. Bridge /TX around TRRS cutout cleanly on B.Cu:
    # J2 is at x = +5.2575. Cutout extends west to x = -7.7425.
    # Top Pad R is at (-0.7425, 30.74625), bottom Pad R is at (-0.7425, 38.54625).
    # All on B.Cu:
    # Top Pad R -> north to y=29.0 -> west to x=-10.0 -> south to y=40.0 -> east to (-6.1000, 40.0) -> to bottom Pad R
    add_track_path(board, nets["/TX"], B_Cu, [
        (-0.7425, 30.74625),
        (-0.7425, 29.0000),
        (-10.0000, 29.0000),
        (-10.0000, 40.0000),
        (-6.1000, 40.0000),
        (-0.7425, 40.0000),
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
        (-116.5, 20.0),
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
    rpt = r"scratch\drc_left_clean.rpt"
    subprocess.run([KICAD_CLI, "pcb", "drc", "-o", rpt, pcb_path], check=True)
    with open(rpt, "r", encoding="utf-8") as f:
        txt = f.read()
    print("=== LEFT PCB DRC ===")
    for l in txt.splitlines():
        if "violations" in l or "unconnected" in l or "Error" in l:
            print(" ", l)

if __name__ == "__main__":
    fix_right()
    fix_left()
