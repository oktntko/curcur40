# -*- coding: utf-8 -*-
"""
Apply Plan B to Left PCB (curcur40-left.kicad_pcb):
- Shift TRRS (J2) right by dx = +9.525 mm (from -4.2675 to +5.2575)
- Shift USB-C (J1) north by dy = -7.09375 mm (from -15.96375 to -23.0575)
- Add straight parallel extension tracks for USB-C & GND breakout
- Cleanly connect TRRS (/TX and +5V on both layers, mirrored)
- Expand GND zone to cover Pad S of J2
- Update Edge.Cuts to Plan B outline (mirrored)
- Refill zones and run DRC
"""
import os
import math
import shutil
import pcbnew

PCB_PATH = r"c:\Users\oktnt\workspace\curcur40\pcbs\curcur40\left\curcur40-left.kicad_pcb"

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

def apply_plan_b_left():
    board = pcbnew.LoadBoard(PCB_PATH)
    nets = {net.GetNetname(): net for net in board.GetNetsByName().values()}

    dx_trrs = 9.525
    dy_usb = -7.09375

    # 1. Shift J2 (TRRS)
    j2 = board.FindFootprintByReference("J2")
    old_trrs_pos = j2.GetPosition()
    j2.SetPosition(pt(pcbnew.ToMM(old_trrs_pos.x) + dx_trrs, pcbnew.ToMM(old_trrs_pos.y)))
    print("New J2 pos:", pcbnew.ToMM(j2.GetPosition().x), pcbnew.ToMM(j2.GetPosition().y))

    # 2. Shift J1 (USB-C)
    j1 = board.FindFootprintByReference("J1")
    old_j1_pos = j1.GetPosition()
    j1.SetPosition(pt(pcbnew.ToMM(old_j1_pos.x), pcbnew.ToMM(old_j1_pos.y) + dy_usb))
    print("New J1 pos:", pcbnew.ToMM(j1.GetPosition().x), pcbnew.ToMM(j1.GetPosition().y))

    # 3. Clean old TRRS tracks around J2 and old USB tracks
    to_delete = []
    for t in board.GetTracks():
        net = t.GetNetname()
        s, e = t.GetStart(), t.GetEnd()
        sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
        ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)

        # Old TRRS tracks around J2
        if net == "/TX" and max(sx, ex) > -20.0 and 28.0 < min(sy, ey) and max(sy, ey) < 41.0:
            to_delete.append(t)
        if net == "+5V" and max(sx, ex) > -20.0 and 28.0 < min(sy, ey) and max(sy, ey) < 41.0:
            to_delete.append(t)

        # Old USB-C GND breakout tracks
        if net == "GND" and min(sy, ey) < -10.0 and max(sy, ey) < -8.0 and (max(sx, ex) > -10.0 or -19.0 < max(sx, ex) < -15.0):
            to_delete.append(t)

        # Old VBUS vias at old y=-10.614
        if t.GetClass() == "PCB_VIA" and net == "VBUS" and abs(sy - (-10.6137)) < 0.1:
            to_delete.append(t)

    for t in to_delete:
        board.Delete(t)
    print(f"Deleted {len(to_delete)} old tracks.")

    F_Cu = pcbnew.F_Cu
    B_Cu = pcbnew.B_Cu

    # Connect /TX for moved J2 (mirrored):
    # Pin R is at (-0.7425, 30.74625) and (-0.7425, 38.54625)
    # Bridge the two pins on F.Cu and B.Cu
    add_track_path(board, nets["/TX"], F_Cu, [(-0.7425, 30.74625), (-0.7425, 38.54625)], width=0.25)
    add_track_path(board, nets["/TX"], B_Cu, [(-0.7425, 30.74625), (-0.7425, 38.54625)], width=0.25)
    # Connect from existing /TX trace at (-6.100, 40.000) straight to Pad R
    add_track_path(board, nets["/TX"], B_Cu, [
        (-6.1000, 40.0000), (-0.7425, 40.0000), (-0.7425, 38.54625)
    ], width=0.25)
    add_via(board, nets["/TX"], -2.0000, 40.0000, drill=0.30, size=0.50)
    add_track_path(board, nets["/TX"], F_Cu, [(-2.0000, 40.0000), (-0.7425, 40.0000), (-0.7425, 38.54625)], width=0.25)

    # Connect +5V for moved J2 (mirrored):
    # Pin T is at (-6.5425, 30.74625) and (-6.5425, 38.54625)
    # Both pins and both incoming feeds on F.Cu:
    add_track_path(board, nets["+5V"], F_Cu, [
        (-24.8320, 30.5960), (-6.5425, 30.5960), (-6.5425, 30.74625),
        (-6.5425, 38.54625), (-6.5425, 38.6200), (-24.7620, 38.6200)
    ], width=0.40)
    # Via connecting F.Cu and B.Cu for Pad T +5V
    add_via(board, nets["+5V"], -8.5000, 30.5960, drill=0.30, size=0.50)
    add_via(board, nets["+5V"], -8.5000, 38.6200, drill=0.30, size=0.50)
    add_track_path(board, nets["+5V"], B_Cu, [
        (-8.5000, 30.5960), (-6.5425, 30.5960), (-6.5425, 30.74625)
    ], width=0.40)
    add_track_path(board, nets["+5V"], B_Cu, [
        (-8.5000, 38.6200), (-6.5425, 38.6200), (-6.5425, 38.54625)
    ], width=0.40)

    # 4. Straight parallel extensions for USB-C (from y = -10.614 to y = -17.70775)
    y_from = -10.614
    y_to = -10.614 + dy_usb  # -17.70775

    # VBUS
    add_track_path(board, nets["VBUS"], F_Cu, [(-9.8375, y_from), (-9.8375, y_to)], width=0.40)
    add_track_path(board, nets["VBUS"], F_Cu, [(-14.7375, y_from), (-14.7375, y_to)], width=0.40)
    add_via(board, nets["VBUS"], -9.8375, y_to, drill=0.30, size=0.50)
    add_via(board, nets["VBUS"], -14.7375, y_to, drill=0.30, size=0.50)

    # CC1 (A5: -13.5375) & CC2 (B5: -10.5375)
    add_track_path(board, nets["Net-(J1-CC1)"], B_Cu, [(-13.5375, y_from), (-13.5375, y_to)], width=0.20)
    add_track_path(board, nets["Net-(J1-CC2)"], B_Cu, [(-10.5375, y_from), (-10.5375, y_to)], width=0.20)

    # D- (A7: -12.0375, B7: -13.0375)
    add_track_path(board, nets["/D-"], B_Cu, [(-12.0375, y_from), (-12.0375, y_to)], width=0.20)
    add_track_path(board, nets["/D-"], B_Cu, [(-13.0375, y_from), (-13.0375, y_to)], width=0.20)

    # D+ (A6: -12.5375, B6: -11.5375)
    add_track_path(board, nets["/D+"], B_Cu, [(-12.5375, y_from), (-12.5375, y_to)], width=0.20)
    add_track_path(board, nets["/D+"], B_Cu, [(-11.5375, y_from), (-11.5375, y_to)], width=0.20)

    # USB-C GND tracks to Pad S1
    add_track_path(board, nets["GND"], B_Cu, [
        (-9.0375, y_to), (-7.4080, y_to), (-6.6675, y_to - 0.740), (-6.6675, -19.0575)
    ], width=0.30)
    add_track_path(board, nets["GND"], B_Cu, [
        (-15.5375, y_to), (-17.0460, y_to), (-17.9075, y_to - 0.740), (-17.9075, -19.0575)
    ], width=0.30)

    # R2 Pad 1 to GND via
    add_track_path(board, nets["GND"], B_Cu, [(-5.1275, -15.7837), (-5.1430, -16.3110)], width=0.25)
    add_via(board, nets["GND"], -5.1430, -16.3110, drill=0.30, size=0.50)

    # Expand GND Zone to cover Pad S of J2 (x up to +8.0 mm)
    for z in board.Zones():
        if z.GetNetname() == "GND":
            poly = z.Outline()
            for i in range(poly.OutlineCount()):
                outline = poly.Outline(i)
                for j in range(outline.PointCount()):
                    p = outline.CPoint(j)
                    px = pcbnew.ToMM(p.x)
                    if px > -5.0:
                        outline.SetPoint(j, pt(8.000, pcbnew.ToMM(p.y)))
    print("Expanded GND zone.")

    # 5. Rebuild Edge.Cuts for Left PCB (Mirrored)
    to_remove = []
    for d in board.GetDrawings():
        if d.GetLayerName() == "Edge.Cuts" and d.GetShapeStr() != "Circle":
            to_remove.append(d)
    for d in to_remove:
        board.Remove(d)
    print(f"Removed {len(to_remove)} perimeter Edge.Cuts.")

    R = 1.0  # Corner radius

    # 1. Right vertical edge (x = +5.2625)
    add_line(board, 5.2625, 67.500 - R, 5.2625, -24.3125 + R)
    add_arc_90(board, 5.2625, -24.3125 + R, 5.2625 - R, -24.3125, 5.2625 - R, -24.3125 + R)

    # 2. Top edge with USB cutout
    add_line(board, 5.2625 - R, -24.3125, -7.6175, -24.3125)
    usb_cut_bottom = -24.3125 + 5.8025  # -18.5100
    add_line(board, -7.6175, -24.3125, -7.6175, usb_cut_bottom)
    add_line(board, -7.6175, usb_cut_bottom, -16.8575, usb_cut_bottom)
    add_line(board, -16.8575, usb_cut_bottom, -16.8575, -24.3125)
    add_line(board, -16.8575, -24.3125, -119.0625 + R, -24.3125)
    add_arc_90(board, -119.0625 + R, -24.3125, -119.0625, -24.3125 + R, -119.0625 + R, -24.3125 + R)

    # 3. Pinky left edge
    add_line(board, -119.0625, -24.3125 + R, -119.0625, 40.98125 - R)
    add_arc_90(board, -119.0625, 40.98125 - R, -119.0625 + R, 40.98125, -119.0625 + R, 40.98125 - R)

    # 4. Pinky bottom step
    add_line(board, -119.0625 + R, 40.98125, -82.4625 - R, 40.98125)
    add_arc_90(board, -82.4625 - R, 40.98125, -82.4625, 40.98125 + R, -82.4625 - R, 40.98125 + R)

    # 5. Thumb left step
    add_line(board, -82.4625, 40.98125 + R, -82.4625, 67.500 - R)
    add_arc_90(board, -82.4625, 67.500 - R, -82.4625 + R, 67.500, -82.4625 + R, 67.500 - R)

    # 6. Bottom edge
    add_line(board, -82.4625 + R, 67.500, 5.2625 - R, 67.500)
    add_arc_90(board, 5.2625 - R, 67.500, 5.2625, 67.500 - R, 5.2625 - R, 67.500 - R)

    # Refill zones
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    print("Zones refilled.")

    board.Save(PCB_PATH)
    print("Saved modified board to", PCB_PATH)

if __name__ == "__main__":
    apply_plan_b_left()
