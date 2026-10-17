# -*- coding: utf-8 -*-
"""
Fix Right PCB:
1. Rebuild Edge.Cuts with TRRS mid-mount cutout:
   - Left boundary at x = -5.2625
   - Cutout at x in [-5.2625, 7.7425], y in [31.500, 37.800]
2. Remove 4 legacy Corne screw hole circles (r = 2.5 mm).
   Keep trackball optical aperture circle (r = 5.0 mm at (9.525, 52.3875)).
3. Add 3 new perimeter mounting holes (r = 1.1 mm) at:
   - (114.0, -20.0)
   - (2.0, -20.0)
   - (114.0, 37.0)
4. Reroute /TX cleanly around the TRRS cutout (bypassing on B.Cu at x = 10.0).
5. Refill zones and run DRC.
"""
import math
import subprocess
import pcbnew

PCB_PATH = r"pcbs\curcur40\right\curcur40-right.kicad_pcb"
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

def main():
    board = pcbnew.LoadBoard(PCB_PATH)
    nets = {net.GetNetname(): net for net in board.GetNetsByName().values()}

    # 1. Clean existing /TX tracks around rJ2 and any tracks crossing cutout
    to_delete = []
    for t in board.GetTracks():
        net = t.GetNetname()
        s, e = t.GetStart(), t.GetEnd()
        sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
        ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)

        # /TX tracks near rJ2
        if net == "/TX" and min(sx, ex) < 20.0 and 28.0 < min(sy, ey) and max(sy, ey) < 45.0:
            to_delete.append(t)

        # Delete any track segment crossing inside cutout: x in [-5.3, 7.75], y in [31.4, 37.9]
        if min(sx, ex) < 7.75 and max(sx, ex) > -5.3 and min(sy, ey) < 37.9 and max(sy, ey) > 31.4:
            if t not in to_delete:
                to_delete.append(t)

    for t in to_delete:
        board.Delete(t)
    print(f"Deleted {len(to_delete)} tracks near/inside TRRS cutout.")

    # 2. Clean drawings on Edge.Cuts (except trackball sensor circle)
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
    print(f"Removed {len(drawings_to_delete)} Edge.Cuts elements.")

    # 3. Build new Edge.Cuts with TRRS Cutout
    R = 1.0  # Corner radius

    # Top edge with USB cutout
    # Top-left corner arc from left edge (-5.2625, -24.3125+R) to top edge (-5.2625+R, -24.3125)
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

    # Left edge with TRRS Cutout:
    # 1. Lower left vertical line from bottom-left corner up to cutout bottom (y = 37.800)
    add_line(board, -5.2625, 67.500 - R, -5.2625, 37.800)
    # 2. Cutout bottom edge going east into board to x = 7.7425
    add_line(board, -5.2625, 37.800, 7.7425, 37.800)
    # 3. Cutout inner vertical edge going north to y = 31.500
    add_line(board, 7.7425, 37.800, 7.7425, 31.500)
    # 4. Cutout top edge going west back to left outline
    add_line(board, 7.7425, 31.500, -5.2625, 31.500)
    # 5. Upper left vertical line from cutout top up to top-left corner
    add_line(board, -5.2625, 31.500, -5.2625, -24.3125 + R)

    # 4. Add 3 new perimeter mounting holes (diameter 2.2 mm -> r = 1.1 mm)
    new_holes = [
        (114.0, -20.0),
        (2.0, -20.0),
        (114.0, 37.0),
    ]
    for hx, hy in new_holes:
        add_circle(board, hx, hy, 1.10)
    print("Added 3 new perimeter mounting holes.")

    # 5. Route /TX cleanly around TRRS cutout
    F_Cu = pcbnew.F_Cu
    B_Cu = pcbnew.B_Cu
    net_tx = nets["/TX"]

    # Top Pad R is at (0.7425, 30.74625)
    # Bottom Pad R is at (0.7425, 38.54625)
    # We bridge them via B.Cu corridor at x = 10.000:
    # From top Pad R (F.Cu and B.Cu):
    add_track_path(board, net_tx, F_Cu, [(0.7425, 30.74625), (10.000, 30.74625)], width=0.25)
    add_track_path(board, net_tx, B_Cu, [(0.7425, 30.74625), (10.000, 30.74625)], width=0.25)
    add_via(board, net_tx, 10.000, 30.74625, drill=0.30, size=0.50)

    # Along x = 10.000 on B.Cu from y = 30.74625 down past cutout to y = 42.4160
    add_track_path(board, net_tx, B_Cu, [(10.000, 30.74625), (10.000, 42.4160)], width=0.25)

    # Branch to bottom Pad R at (0.7425, 38.54625)
    add_track_path(board, net_tx, B_Cu, [(10.000, 38.54625), (0.7425, 38.54625)], width=0.25)
    add_track_path(board, net_tx, F_Cu, [(10.000, 38.54625), (0.7425, 38.54625)], width=0.25)
    add_via(board, net_tx, 10.000, 38.54625, drill=0.30, size=0.50)

    # Continue from (10.000, 42.4160) to (23.5750, 42.4160)
    add_track_path(board, net_tx, B_Cu, [(10.000, 42.4160), (23.5750, 42.4160)], width=0.25)

    # 6. Refill zones
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    print("Zones refilled.")

    board.Save(PCB_PATH)
    print("Saved Right PCB.")

    # Run DRC
    rpt = r"scratch\drc_right_fixed.rpt"
    res = subprocess.run([KICAD_CLI, "pcb", "drc", "-o", rpt, PCB_PATH], capture_output=True, text=True)
    with open(rpt, "r", encoding="utf-8") as f:
        drc_text = f.read()
    print("DRC Result:")
    for line in drc_text.splitlines():
        if "violations" in line or "unconnected" in line or "Error" in line:
            print(" ", line)

if __name__ == "__main__":
    main()
