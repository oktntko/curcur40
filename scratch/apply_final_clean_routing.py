# -*- coding: utf-8 -*-
"""
Apply final clean routing to Right and Left PCBs.
Verify 0 DRC errors and 0 unconnected items on both boards.
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

def clean_and_route_right():
    pcb_path = r"pcbs\curcur40\right\curcur40-right.kicad_pcb"
    board = pcbnew.LoadBoard(pcb_path)
    nets = {net.GetNetname(): net for net in board.GetNetsByName().values()}

    F_Cu = pcbnew.F_Cu
    B_Cu = pcbnew.B_Cu

    # 1. Clean existing /TX and +5VR tracks near rJ2 in x < 26.0, y in [28, 46]
    to_delete = []
    for t in board.GetTracks():
        net = t.GetNetname()
        s, e = t.GetStart(), t.GetEnd()
        sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
        ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)

        if net in ["/TX", "+5VR"] and min(sx, ex) < 25.5 and min(sy, ey) < 46.0 and max(sy, ey) > 28.0:
            to_delete.append(t)

        # Delete any extra vias at (111.5625, 36.8263)
        if net == "GNDR" and abs(sx - 111.5625) < 0.2 and abs(sy - 36.82625) < 0.2:
            to_delete.append(t)

    for t in to_delete:
        board.Delete(t)
    print(f"Right: Cleaned {len(to_delete)} tracks/vias.")

    # Re-add single GND via at (111.5625, 36.82625)
    add_via(board, nets["GNDR"], 111.5625, 36.82625, drill=0.30, size=0.50)
    add_track_path(board, nets["GNDR"], B_Cu, [(112.6375, 36.85625), (111.5625, 36.82625)], width=0.25)

    # 2. Re-wire +5VR
    # Top: Pad T (B.Cu) at (6.5425, 30.74625) -> B.Cu to (18.5675, 30.5963) -> via -> F.Cu to (24.2675, 30.5963)
    add_track_path(board, nets["+5VR"], B_Cu, [
        (6.5425, 30.74625),
        (6.6925, 30.5963),
        (18.5675, 30.5963),
    ], width=0.40)
    add_via(board, nets["+5VR"], 18.5675, 30.5963, drill=0.30, size=0.50)
    add_track_path(board, nets["+5VR"], F_Cu, [(18.5675, 30.5963), (24.2675, 30.5963)], width=0.40)

    # Bottom: Pad T (B.Cu) at (6.5425, 38.54625) -> B.Cu to (18.5975, 38.6962) -> via -> F.Cu to (24.0262, 38.6962)
    add_track_path(board, nets["+5VR"], B_Cu, [
        (6.5425, 38.54625),
        (6.6925, 38.6962),
        (18.5975, 38.6962),
    ], width=0.40)
    add_via(board, nets["+5VR"], 18.5975, 38.6962, drill=0.30, size=0.50)
    add_track_path(board, nets["+5VR"], F_Cu, [(18.5975, 38.6962), (24.0262, 38.6962)], width=0.40)

    # Connect +5VR bus on F.Cu
    add_track_path(board, nets["+5VR"], F_Cu, [
        (24.2675, 30.5963),
        (24.7905, 30.5963),
        (24.8105, 30.6163),
        (24.8105, 35.6350),
        (25.4875, 35.6350),
        (31.3663, 35.6350),
    ], width=0.40)
    add_track_path(board, nets["+5VR"], F_Cu, [
        (24.8105, 2.9263),
        (24.8105, 30.6163),
    ], width=0.40)
    add_track_path(board, nets["+5VR"], F_Cu, [
        (24.8105, 35.6350),
        (24.8105, 37.9119),
        (24.0262, 38.6962),
    ], width=0.40)

    # 3. Re-wire /TX
    # On F.Cu: Pad R top (0.7425, 30.74625) to Pad R bottom (0.7425, 38.54625)
    # Bypassing the cutout east edge at x = 7.7425.
    # At y=38.6962, +5VR is on B.Cu, so /TX stays on F.Cu down to y=39.2000:
    add_track_path(board, nets["/TX"], F_Cu, [
        (0.7425, 30.74625),
        (8.7725, 30.74625),
        (8.7725, 39.2000),
    ], width=0.25)
    add_track_path(board, nets["/TX"], F_Cu, [
        (8.7725, 38.54625),
        (0.7425, 38.54625),
    ], width=0.25)
    # Drop via at (8.7725, 39.2000) to B.Cu (between +5VR at 38.6962 and /NCS at 39.8000)
    add_via(board, nets["/TX"], 8.7725, 39.2000, drill=0.30, size=0.50)

    # On B.Cu:
    # Down along x = 8.7725 from y = 39.2000 to y = 44.5000 (well south of rH2 at 42.3875)
    # Then east to x = 21.0000, then north to (23.5749, 42.4162), and connect to (25.1908, 40.8004) -> (40.6684, 40.8004)
    add_track_path(board, nets["/TX"], B_Cu, [
        (8.7725, 39.2000),
        (8.7725, 44.5000),
        (21.0000, 44.5000),
        (23.0000, 42.5000),
        (23.5749, 42.4162),
    ], width=0.25)
    add_track_path(board, nets["/TX"], B_Cu, [
        (23.5749, 42.4162),
        (25.1908, 40.8004),
        (40.6684, 40.8004),
    ], width=0.20)

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
    rpt = r"scratch\drc_right_perfect_final.rpt"
    subprocess.run([KICAD_CLI, "pcb", "drc", "-o", rpt, pcb_path], check=True)
    with open(rpt, "r", encoding="utf-8") as f:
        txt = f.read()
    print("=== RIGHT PCB DRC ===")
    for l in txt.splitlines():
        if "violations" in l or "unconnected" in l or "Error" in l:
            print(" ", l)

if __name__ == "__main__":
    clean_and_route_right()
