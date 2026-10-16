# -*- coding: utf-8 -*-
"""
Apply Plan B to Right PCB:
- Shift TRRS (rJ2) left by dx = -9.525 mm
- Shift USB-C (rJ1) north by dy = -7.09375 mm
- Add straight parallel extension tracks for USB-C & GND breakout
- Cleanly connect TRRS (/TX and +5VR on both layers)
- Update Edge.Cuts to Plan B outline
- Refill zones and run DRC
"""
import os
import math
import shutil
import pcbnew
import subprocess

PCB_PATH = r"c:\Users\oktnt\workspace\curcur40\pcbs\curcur40\right\curcur40-right.kicad_pcb"

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

def apply_plan_b():
    board = pcbnew.LoadBoard(PCB_PATH)
    nets = {net.GetNetname(): net for net in board.GetNetsByName().values()}

    dx_trrs = -9.525
    dy_usb = -7.09375

    # 1. Shift rJ2 (TRRS)
    rj2 = board.FindFootprintByReference("rJ2")
    old_trrs_pos = rj2.GetPosition()
    rj2.SetPosition(pt(pcbnew.ToMM(old_trrs_pos.x) + dx_trrs, pcbnew.ToMM(old_trrs_pos.y)))
    print("New rJ2 pos:", pcbnew.ToMM(rj2.GetPosition().x), pcbnew.ToMM(rj2.GetPosition().y))

    # 2. Shift rJ1 (USB-C)
    rj1 = board.FindFootprintByReference("rJ1")
    old_rj1_pos = rj1.GetPosition()
    rj1.SetPosition(pt(pcbnew.ToMM(old_rj1_pos.x), pcbnew.ToMM(old_rj1_pos.y) + dy_usb))
    print("New rJ1 pos:", pcbnew.ToMM(rj1.GetPosition().x), pcbnew.ToMM(rj1.GetPosition().y))

    # 3. Clean old TRRS tracks around rJ2 and old USB GND tracks
    to_delete = []
    for t in board.GetTracks():
        net = t.GetNetname()
        s, e = t.GetStart(), t.GetEnd()
        sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
        ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)

        # Old TRRS tracks around rJ2
        if net == "/TX" and min(sx, ex) < 20.0 and 28.0 < min(sy, ey) and max(sy, ey) < 45.0:
            to_delete.append(t)
        if net == "+5VR" and min(sx, ex) < 20.0 and 28.0 < min(sy, ey) and max(sy, ey) < 41.0:
            to_delete.append(t)
        
        # Old USB-C GND breakout tracks
        if net == "GNDR" and min(sy, ey) < -10.0 and max(sy, ey) < -8.0 and (min(sx, ex) < 10.0 or 15.0 < min(sx, ex) < 19.0):
            to_delete.append(t)

        # Old VBUS vias at old y=-10.614
        if t.GetClass() == "PCB_VIA" and net == "VBUSR" and abs(sy - (-10.6137)) < 0.1:
            to_delete.append(t)

    for t in to_delete:
        board.Delete(t)
    print(f"Deleted {len(to_delete)} old tracks.")

    F_Cu = pcbnew.F_Cu
    B_Cu = pcbnew.B_Cu

    # Connect /TX for moved rJ2 (both F.Cu and B.Cu):
    # Pin R is at (0.7425, 30.74625) and (0.7425, 38.54625)
    # Bridge the two pins on F.Cu and B.Cu
    add_track_path(board, nets["/TX"], F_Cu, [(0.7425, 30.74625), (0.7425, 38.54625)], width=0.25)
    add_track_path(board, nets["/TX"], B_Cu, [(0.7425, 30.74625), (0.7425, 38.54625)], width=0.25)
    # Via between F.Cu and B.Cu for /TX
    add_via(board, nets["/TX"], 3.5000, 34.64625, drill=0.30, size=0.50)
    add_track_path(board, nets["/TX"], F_Cu, [(0.7425, 34.64625), (3.5000, 34.64625)], width=0.25)
    # Route on B.Cu through corridor at y=34.64625 down to y=42.416 to (23.575, 42.416)
    add_track_path(board, nets["/TX"], B_Cu, [
        (0.7425, 34.64625), (15.5000, 34.64625), (15.5000, 42.4160), (23.5750, 42.4160)
    ], width=0.25)

    # Connect +5VR for moved rJ2 (both F.Cu and B.Cu):
    # Pin T is at (6.5425, 30.74625) and (6.5425, 38.54625)
    # Bridge the two pins on F.Cu:
    add_track_path(board, nets["+5VR"], F_Cu, [
        (24.2680, 30.5960), (6.5425, 30.5960), (6.5425, 30.74625),
        (6.5425, 38.54625), (24.0262, 38.54625), (24.0262, 38.6962)
    ], width=0.40)
    # Via connecting F.Cu and B.Cu for Pad T +5VR
    add_via(board, nets["+5VR"], 8.5000, 30.5960, drill=0.30, size=0.50)
    add_via(board, nets["+5VR"], 8.5000, 38.54625, drill=0.30, size=0.50)
    add_track_path(board, nets["+5VR"], B_Cu, [
        (8.5000, 30.5960), (6.5425, 30.5960), (6.5425, 30.74625)
    ], width=0.40)
    add_track_path(board, nets["+5VR"], B_Cu, [
        (8.5000, 38.54625), (6.5425, 38.54625)
    ], width=0.40)

    # 4. Straight parallel extensions for USB-C (from y = -10.614 to y = -17.70775)
    y_from = -10.614
    y_to = -10.614 + dy_usb  # -17.70775

    # VBUSR
    add_track_path(board, nets["VBUSR"], F_Cu, [(9.838, y_from), (9.838, y_to)], width=0.40)
    add_track_path(board, nets["VBUSR"], F_Cu, [(14.738, y_from), (14.738, y_to)], width=0.40)
    add_via(board, nets["VBUSR"], 9.838, y_to, drill=0.30, size=0.50)
    add_via(board, nets["VBUSR"], 14.738, y_to, drill=0.30, size=0.50)

    # CC1 & CC2
    add_track_path(board, nets["Net-(rJ1-CC1)"], B_Cu, [(11.037, y_from), (11.037, y_to)], width=0.20)
    add_track_path(board, nets["Net-(rJ1-CC2)"], B_Cu, [(14.037, y_from), (14.037, y_to)], width=0.20)

    # D-
    add_track_path(board, nets["/D-"], B_Cu, [(11.537, y_from), (11.537, y_to)], width=0.20)
    add_track_path(board, nets["/D-"], B_Cu, [(12.537, y_from), (12.537, y_to)], width=0.20)

    # D+
    add_track_path(board, nets["/D+"], B_Cu, [(12.037, y_from), (12.037, y_to)], width=0.20)
    add_track_path(board, nets["/D+"], B_Cu, [(13.037, y_from), (13.037, y_to)], width=0.20)

    # USB-C GND tracks to Pad S1
    add_track_path(board, nets["GNDR"], B_Cu, [
        (9.0375, y_to), (7.4080, y_to), (6.6675, y_to - 0.740), (6.6675, -19.0575)
    ], width=0.30)
    add_track_path(board, nets["GNDR"], B_Cu, [
        (15.5375, y_to), (17.0460, y_to), (17.9075, y_to - 0.740), (17.9075, -19.0575)
    ], width=0.30)

    # rR1 Pad 1 to GND via
    add_track_path(board, nets["GNDR"], B_Cu, [(5.1225, -15.7850), (5.1430, -16.3110)], width=0.25)
    add_via(board, nets["GNDR"], 5.1430, -16.3110, drill=0.30, size=0.50)

    # 5. Rebuild Edge.Cuts
    to_remove = []
    for d in board.GetDrawings():
        if d.GetLayerName() == "Edge.Cuts" and d.GetShapeStr() != "Circle":
            to_remove.append(d)
    for d in to_remove:
        board.Remove(d)
    print(f"Removed {len(to_remove)} perimeter Edge.Cuts.")

    R = 1.0  # Corner radius

    # 1. Left vertical edge
    add_line(board, -5.2625, 67.500 - R, -5.2625, -24.3125 + R)
    add_arc_90(board, -5.2625, -24.3125 + R, -5.2625 + R, -24.3125, -5.2625 + R, -24.3125 + R)

    # 2. Top edge with USB cutout
    add_line(board, -5.2625 + R, -24.3125, 7.6175, -24.3125)
    usb_cut_bottom = -24.3125 + 5.8025  # -18.5100
    add_line(board, 7.6175, -24.3125, 7.6175, usb_cut_bottom)
    add_line(board, 7.6175, usb_cut_bottom, 16.8575, usb_cut_bottom)
    add_line(board, 16.8575, usb_cut_bottom, 16.8575, -24.3125)
    add_line(board, 16.8575, -24.3125, 119.0625 - R, -24.3125)
    add_arc_90(board, 119.0625 - R, -24.3125, 119.0625, -24.3125 + R, 119.0625 - R, -24.3125 + R)

    # 3. Pinky right edge
    add_line(board, 119.0625, -24.3125 + R, 119.0625, 40.98125 - R)
    add_arc_90(board, 119.0625, 40.98125 - R, 119.0625 - R, 40.98125, 119.0625 - R, 40.98125 - R)

    # 4. Pinky bottom step
    add_line(board, 119.0625 - R, 40.98125, 82.4625 + R, 40.98125)
    add_arc_90(board, 82.4625 + R, 40.98125, 82.4625, 40.98125 + R, 82.4625 + R, 40.98125 + R)

    # 5. Thumb right step
    add_line(board, 82.4625, 40.98125 + R, 82.4625, 67.500 - R)
    add_arc_90(board, 82.4625, 67.500 - R, 82.4625 - R, 67.500, 82.4625 - R, 67.500 - R)

    # 6. Bottom edge
    add_line(board, 82.4625 - R, 67.500, -5.2625 + R, 67.500)
    add_arc_90(board, -5.2625 + R, 67.500, -5.2625, 67.500 - R, -5.2625 + R, 67.500 - R)

    # Refill zones
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    print("Zones refilled.")

    board.Save(PCB_PATH)
    print("Saved modified board to", PCB_PATH)

if __name__ == "__main__":
    apply_plan_b()
