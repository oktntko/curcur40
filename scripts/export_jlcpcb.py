# -*- coding: utf-8 -*-
"""
Export JLCPCB PCB / PCBA production files for curcur40:
- 3-in-1 PCBA Panel:  pcbs/panel/jlcpcb/production_files/{GERBER,BOM,CPL}-curcur40-panel-3in1.*
- Left Main PCB:      pcbs/left/jlcpcb/production_files/{GERBER,BOM,CPL}-curcur40-left.*
- Right Main PCB:     pcbs/right/jlcpcb/production_files/{GERBER,BOM,CPL}-curcur40-right.*
- PMW3360 Sub PCB:    pcbs/pmw3360/jlcpcb/production_files/{GERBER,BOM,CPL}-curcur40-pmw3360.*
- Top Plates:         plates/pcb/jlcpcb/production_files/GERBER-plate-top-{left,right}.zip
"""
import os
import re
import csv
import json
import math
import shutil
import tempfile
import zipfile
import subprocess
from pathlib import Path
import pcbnew

WORKSPACE = Path(__file__).resolve().parent.parent
KICAD_CLI = os.path.expandvars(r"%LOCALAPPDATA%\Programs\KiCad\10.0\bin\kicad-cli.exe")

LCSC_MAP_MAIN = {
    "U4": ("W25Q128JVSIQ", "SOIC-8_5.3x5.3mm_P1.27mm", "C113767"),
    "R3": ("1k", "R_0402_1005Metric", "C11702"),
    "R6": ("1k", "R_0402_1005Metric", "C11702"),
    "U3": ("USBLC6-2SC6", "SOT-23-6", "C7519"),
    "U5": ("USBLC6-2SC6", "SOT-23-6", "C7519"),
    "ZD1": ("1N5819WS", "D_SOD-323", "C191023"),
    "U2": ("LDL1117S33R", "SOT-223-3_TabPin2", "C435835"),
    "C3": ("100n", "C_0402_1005Metric", "C1525"),
    "C4": ("100n", "C_0402_1005Metric", "C1525"),
    "C7": ("100n", "C_0402_1005Metric", "C1525"),
    "C9": ("100n", "C_0402_1005Metric", "C1525"),
    "C10": ("100n", "C_0402_1005Metric", "C1525"),
    "C12": ("100n", "C_0402_1005Metric", "C1525"),
    "C13": ("100n", "C_0402_1005Metric", "C1525"),
    "C14": ("100n", "C_0402_1005Metric", "C1525"),
    "C15": ("100n", "C_0402_1005Metric", "C1525"),
    "C17": ("1u", "C_0402_1005Metric", "C52923"),
    "C18": ("100n", "C_0402_1005Metric", "C1525"),
    "C6": ("10u", "C_0402_1005Metric", "C15525"),
    "C11": ("10u", "C_0402_1005Metric", "C15525"),
    "C1": ("27p", "C_0402_1005Metric", "C1557"),
    "C2": ("27p", "C_0402_1005Metric", "C1557"),
    "U1": ("RP2040", "QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm", "C2040"),
    "D1": ("1N4148WS", "D_SOD-323", "C2128"),
    "R7": ("10k", "R_0402_1005Metric", "C25744"),
    "R9": ("10k", "R_0402_1005Metric", "C25744"),
    "R1": ("5.1k", "R_0402_1005Metric", "C25905"),
    "R2": ("5.1k", "R_0402_1005Metric", "C25905"),
    "R8": ("5.6k", "R_0402_1005Metric", "C25908"),
    "R11": ("4.7k", "R_0402_1005Metric", "C25900"),
    "R12": ("4.7k", "R_0402_1005Metric", "C25900"),
    "J1": ("TYPE-C-31-M-13C", "TYPE-C-31-M-13C", "C2848620"),
    "J2": ("TYPE-C-31-M-13C", "TYPE-C-31-M-13C", "C2848620"),
    "J3": ("SM06B-SRSS-TB(LF)(SN)", "JST_SH_SM06B-SRSS-TB_1x06-1MP_P1.00mm_Horizontal", "C160405"),
    "U6": ("TMAG5273A1QDBVR", "SOT-23-6", "C3716049"),
    "R13": ("0", "R_0402_1005Metric", "C17168"),
    "R4": ("27", "R_0402_1005Metric", "C2909343"),
    "R5": ("27", "R_0402_1005Metric", "C2909343"),
    "R10": ("27", "R_0402_1005Metric", "C2909343"),
    "SMDSW1": ("TS-1088R-02026", "TS-1088R-02026", "C455280"),
    "SMDSW2": ("TS-1088R-02026", "TS-1088R-02026", "C455280"),
    "C5": ("1u", "C_0402_1005Metric", "C52923"),
    "C8": ("1u", "C_0402_1005Metric", "C52923"),
    "C16": ("1u", "C_0402_1005Metric", "C52923"),
    "Y1": ("12MHz 18pF", "Crystal_SMD_3225-4Pin_3.2x2.5mm", "C91749"),
}

PMW_PARTS = {
    "C1": ("4.7uF/10V", "C_0603_1608Metric", "C19666"),
    "C2": ("100nF", "C_0603_1608Metric", "C14663"),
    "C3": ("1uF", "C_0603_1608Metric", "C15849"),
    "C4": ("1uF", "C_0603_1608Metric", "C15849"),
    "J1": ("SM06B-SRSS-TB(LF)(SN)", "JST_SH_SM06B-SRSS-TB_1x06-1MP_P1.00mm_Horizontal", "C160405"),
    "R1": ("10k", "R_0603_1608Metric", "C25804"),
    "R2": ("10k", "R_0603_1608Metric", "C25804"),
    "R3": ("39R", "R_0603_1608Metric", "C23154"),
    "U2": ("TLV74318PDBVR", "SOT-23-5", "C485152"),
}


def get_part_info(ref, is_right=False, is_pmw=False, is_panel=False, custom_map=None):
    if custom_map is not None:
        return custom_map.get(ref)
    if is_panel:
        if ref.startswith("p") and ref[1:] in PMW_PARTS:
            return PMW_PARTS[ref[1:]]
        if ref.startswith("r"):
            return get_part_info(ref, is_right=True)
        return get_part_info(ref, is_right=False)
    if is_pmw:
        return PMW_PARTS.get(ref)
    if is_right:
        if ref.startswith("r"):
            base = ref[1:]
            if base in LCSC_MAP_MAIN:
                return LCSC_MAP_MAIN[base]
            if base.startswith("LED") or base.startswith("EXLED"):
                return ("YS-SK6812MINI-E", "YS-SK6812MINI-E", "C5149201")
            if base.startswith("SW") or base.startswith("EXSW"):
                return ("SW_Push", "keyswitch_choc12_hotswap_1u", "C5333465")
            return None
        elif ref in PMW_PARTS:
            return PMW_PARTS[ref]
        return None
    else:
        base = ref
        if base in LCSC_MAP_MAIN:
            return LCSC_MAP_MAIN[base]
        if base.startswith("LED") or base.startswith("EXLED"):
            return ("YS-SK6812MINI-E", "YS-SK6812MINI-E", "C5149201")
        if base.startswith("SW") or base.startswith("EXSW"):
            return ("SW_Push", "keyswitch_choc12_hotswap_1u", "C5333465")
        return None


def export_gerber_zip(pcb_path, zip_path):
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp_dir:
        subprocess.run(
            [
                KICAD_CLI,
                "pcb",
                "export",
                "gerbers",
                "--layers",
                "F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts",
                "--use-drill-file-origin",
                "-o",
                tmp_dir,
                pcb_path,
            ],
            check=True,
        )
        subprocess.run(
            [
                KICAD_CLI,
                "pcb",
                "export",
                "drill",
                "--drill-origin",
                "plot",
                "--excellon-separate-th",
                "--generate-map",
                "--map-format",
                "pdf",
                "-o",
                tmp_dir + "/",
                pcb_path,
            ],
            check=True,
        )
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for fname in sorted(os.listdir(tmp_dir)):
                zf.write(os.path.join(tmp_dir, fname), fname)


# JLCPCB 3D/DFM model rotation offsets (in degrees, added to standard bottom-side rotation (180 - krot) % 360)
# Verified against JLCPCB DFM Component Placement viewer:
JLCPCB_ROT_OFFSETS = {
    "SOIC-8_5.3x5.3mm_P1.27mm": 270.0,       # U4/rU4 (W25Q128JVSIQ, C97521/C113767): 90 deg CW in Bottom view
    "SOT-223-3_TabPin2": 180.0,              # U2/rU2 (LDL1117S33R, C435835): 180 deg in Bottom view
    "USON-10_2.5x1.0mm_P0.5mm": 270.0,       # U3/U5, rU3/rU5 (TPD4E05U06DQAR, C138714): 90 deg CW in Bottom view
    "SOT-23-5": 180.0,                       # PMW3360 U2 (TLV74318PDBVR, C485152): 180 deg in Bottom view
    "SOT-23-6": 180.0,                       # U3/U5/rU3/rU5 (USBLC6-2SC6, C7519) & rU6 (TMAG5273A1QDBVR, C3716049): 180 deg in Bottom view
}


def verify_pcb_3d_step_models(board, pcb_path, proj_name, is_pmw=False, is_panel=False):
    """
    Verify 100% 3D STEP model coverage for all non-DNP footprints (AGENTS.md Sec. 3.6).
    DO NOT add exemptions or invent dummy/approximate 3D models to bypass an NG!
    Leave NG as NG and report (Reference, Footprint, Value) to the user.
    """
    kicad_3d_dir = Path(KICAD_CLI).resolve().parent.parent / "share" / "kicad" / "3dmodels"
    proj_dir = Path(pcb_path).resolve().parent
    # Fixed exemptions ONLY for curcur40-pmw3360 (standalone or p-prefixed inside 3-in-1 panel):
    #   - JP1/pJP1: copper-bridged solder jumper trace (zero physical component)
    #   - U1/pU1:   PMW3360DM-T2QU optical sensor explicitly placed via pmw3360-lens-pcb-assembly.step
    allowed_no_step = set()
    if is_pmw:
        allowed_no_step |= {
            ("JP1", "Jumper:SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm_NumberLabels"),
            ("U1", "kbd:PMW3360DM-T2QU_16Pin"),
        }
    if is_panel:
        allowed_no_step |= {
            ("pJP1", "Jumper:SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm_NumberLabels"),
            ("pU1", "kbd:PMW3360DM-T2QU_16Pin"),
        }
    step_model_problems = []
    for fp in sorted(board.GetFootprints(), key=lambda f: f.GetReference()):
        if fp.GetAttributes() & pcbnew.FP_DNP:
            continue
        ref = fp.GetReference()
        fpid = str(fp.GetFPID().GetUniStringLibId())
        val = fp.GetValue()
        if (ref, fpid) in allowed_no_step:
            continue
        models = list(fp.Models())
        if not models:
            step_model_problems.append(f"{ref} ({fpid}, val={val}): NO 3D model assigned")
            continue
        has_valid_step = False
        for m in models:
            if hasattr(m, "m_Show") and not m.m_Show:
                step_model_problems.append(f"{ref} ({fpid}, val={val}): 3D model is hidden (m_Show=False)")
                continue
            resolved = m.m_Filename.replace("${KIPRJMOD}", str(proj_dir))
            for var in (
                "${KICAD10_3DMODEL_DIR}",
                "${KICAD9_3DMODEL_DIR}",
                "${KICAD8_3DMODEL_DIR}",
                "${KICAD7_3DMODEL_DIR}",
                "${KICAD6_3DMODEL_DIR}",
                "${KISYS3DMOD}",
            ):
                resolved = resolved.replace(var, str(kicad_3d_dir))
            rp = Path(resolved)
            if (
                rp.with_suffix(".step").exists()
                or rp.with_suffix(".stp").exists()
                or (rp.suffix.lower() in (".step", ".stp") and rp.exists())
            ):
                has_valid_step = True
            elif rp.exists():
                step_model_problems.append(
                    f"{ref} ({fpid}, val={val}): '{m.m_Filename}' has no .step/.stp for --subst-models"
                )
            else:
                step_model_problems.append(
                    f"{ref} ({fpid}, val={val}): 3D model file NOT FOUND '{m.m_Filename}'"
                )
        if not has_valid_step and not any(p.startswith(f"{ref} ") for p in step_model_problems):
            step_model_problems.append(f"{ref} ({fpid}, val={val}): no valid .step/.stp model resolved")
    assert not step_model_problems, (
        f"[{proj_name}] 3D STEP model check NG ({len(step_model_problems)} issue(s)):\n  - "
        + "\n  - ".join(step_model_problems)
        + "\nCRITICAL RULE (AGENTS.md Sec. 3.6): DO NOT invent a dummy/approximate 3D model or add to "
        "allowed_no_step on your own! Leave as NG and report (Reference, Footprint, Value) to the user."
    )


def _pt_seg_dist(px: float, py: float, x1: float, y1: float, x2: float, y2: float) -> float:
    dx, dy = x2 - x1, y2 - y1
    l2 = dx * dx + dy * dy
    if l2 <= 1e-12:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / l2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def verify_screw_hole_copper_keepouts(board, proj_name: str, is_pmw: bool = False, is_panel: bool = False):
    """
    Verify M2 screw-head (F.Cu) and brass heat-set insert (B.Cu) copper keepout zones and clearances
    around every Ø 2.40 mm Edge.Cuts mounting hole:
      - Main PCBs (left/right): F.Cu >= 2.28 mm (Ø 4.56 mm, Rule Area r=2.30 mm), B.Cu >= 1.98 mm (Ø 3.96 mm, Rule Area r=2.00 mm)
      - PMW3360 Sub-PCB:        F.Cu >= 1.98 mm (plastic cup ear side),           B.Cu >= 1.98 mm (brass insert side)
    """
    holes = []
    for d in board.GetDrawings():
        if d.GetLayer() == pcbnew.Edge_Cuts and d.GetShape() == pcbnew.SHAPE_T_CIRCLE:
            r_mm = pcbnew.ToMM(d.GetRadius())
            if 1.00 <= r_mm <= 1.50:
                c = d.GetCenter()
                holes.append((pcbnew.ToMM(c.x), pcbnew.ToMM(c.y)))
    assert holes, f"[{proj_name}] Expected Edge.Cuts M2 screw holes, found 0!"

    problems = []

    rule_zones = [z for z in board.Zones() if z.GetIsRuleArea()]
    for hx, hy in holes:
        is_pmw_hole = is_pmw or (is_panel and 7.5 <= hx <= 38.0 and 88.5 <= hy <= 118.5)
        req_radii = {
            pcbnew.F_Cu: 1.98 if is_pmw_hole else 2.28,
            pcbnew.B_Cu: 1.98,
        }
        for lid, min_r in req_radii.items():
            lname = board.GetLayerName(lid)
            matched_keepout = False
            for z in rule_zones:
                if not z.IsOnLayer(lid):
                    continue
                if not (
                    z.GetDoNotAllowTracks()
                    and z.GetDoNotAllowVias()
                    and z.GetDoNotAllowPads()
                    and z.GetDoNotAllowZoneFills()
                ):
                    continue
                bb = z.GetBoundingBox()
                zx, zy = pcbnew.ToMM(bb.GetCenter().x), pcbnew.ToMM(bb.GetCenter().y)
                zr = 0.5 * min(pcbnew.ToMM(bb.GetWidth()), pcbnew.ToMM(bb.GetHeight()))
                if math.hypot(zx - hx, zy - hy) <= 0.05 and zr >= min_r:
                    matched_keepout = True
                    break
            if not matched_keepout:
                problems.append(
                    f"Hole ({hx:.4f}, {hy:.4f}) missing {lname} Rule Area keepout (r >= {min_r:.2f} mm)"
                )

        for t in board.GetTracks():
            cls = t.GetClass()
            if cls == "PCB_TRACK":
                lid = t.GetLayer()
                if lid not in req_radii:
                    continue
                min_r = req_radii[lid]
                sx, sy = pcbnew.ToMM(t.GetStart().x), pcbnew.ToMM(t.GetStart().y)
                ex, ey = pcbnew.ToMM(t.GetEnd().x), pcbnew.ToMM(t.GetEnd().y)
                edge_d = _pt_seg_dist(hx, hy, sx, sy, ex, ey) - 0.5 * pcbnew.ToMM(t.GetWidth())
                if edge_d < min_r:
                    problems.append(
                        f"Hole ({hx:.4f}, {hy:.4f}) {board.GetLayerName(lid)} track [{t.GetNetname()}] "
                        f"at r={edge_d:.3f} mm < {min_r:.2f} mm"
                    )
            elif cls == "PCB_VIA":
                vx, vy = pcbnew.ToMM(t.GetPosition().x), pcbnew.ToMM(t.GetPosition().y)
                vr = 0.5 * pcbnew.ToMM(t.GetWidth(pcbnew.F_Cu))
                for lid, min_r in req_radii.items():
                    if t.IsOnLayer(lid):
                        edge_d = math.hypot(vx - hx, vy - hy) - vr
                        if edge_d < min_r:
                            problems.append(
                                f"Hole ({hx:.4f}, {hy:.4f}) {board.GetLayerName(lid)} via [{t.GetNetname()}] "
                                f"at r={edge_d:.3f} mm < {min_r:.2f} mm"
                            )

        for fp in board.GetFootprints():
            for pad in fp.Pads():
                if pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                    continue
                bb = pad.GetBoundingBox()
                px1, py1 = pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop())
                px2, py2 = pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom())
                dx = max(px1 - hx, 0.0, hx - px2)
                dy = max(py1 - hy, 0.0, hy - py2)
                edge_d = math.hypot(dx, dy)
                for lid, min_r in req_radii.items():
                    if pad.IsOnLayer(lid) and edge_d < min_r:
                        problems.append(
                            f"Hole ({hx:.4f}, {hy:.4f}) {board.GetLayerName(lid)} pad {fp.GetReference()}.{pad.GetNumber()} "
                            f"at r={edge_d:.3f} mm < {min_r:.2f} mm"
                        )

    assert not problems, (
        f"[{proj_name}] Screw-hole copper keepout check FAILED ({len(problems)} issue(s)):\n  - "
        + "\n  - ".join(problems)
    )


def verify_zero_via_in_pad(board, proj_name: str):
    """
    Verify 100% zero Via-in-Pad across ALL SMD pads on the board (including QFN thermal pads).
    Prevents solder wicking, tombstoning, and JLCPCB DFM 'Hole in Pad' engineering holds.
    """
    vias = []
    for t in board.GetTracks():
        if t.GetClass() == "PCB_VIA":
            p = t.GetPosition()
            vr = 0.5 * pcbnew.ToMM(t.GetWidth(pcbnew.F_Cu))
            vias.append((pcbnew.ToMM(p.x), pcbnew.ToMM(p.y), vr, t.GetNetname()))

    vip_problems = []
    for fp in board.GetFootprints():
        if fp.GetAttributes() & pcbnew.FP_DNP:
            continue
        ref = fp.GetReference()
        for pad in fp.Pads():
            if pad.GetAttribute() != pcbnew.PAD_ATTRIB_SMD:
                continue
            bb = pad.GetBoundingBox()
            x1, y1 = pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop())
            x2, y2 = pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom())
            for vx, vy, vr, vnet in vias:
                dx = max(x1 - vx, 0.0, vx - x2)
                dy = max(y1 - vy, 0.0, vy - y2)
                if math.hypot(dx, dy) < vr - 1e-4:
                    vip_problems.append(
                        f"{ref}.{pad.GetNumber()} [{pad.GetNetname()}] overlaps via ({vx:.3f}, {vy:.3f}) [{vnet}]"
                    )
    assert not vip_problems, (
        f"[{proj_name}] Via-in-Pad check FAILED ({len(vip_problems)} SMD pad overlap(s)):\n  - "
        + "\n  - ".join(vip_problems[:25])
    )


def verify_panel_mousebite_clearances(board, proj_name: str, min_clr_mm: float = 0.48):
    """
    Verify every panel mouse-bite NPTH hole (MB*) has >= min_clr_mm copper clearance
    to all tracks, vias, and pads so depaneling shear/flex stress never cracks nearby traces.
    """
    mbs = []
    other_pads = []
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref.startswith("MB"):
            p = fp.Pads()[0]
            mbs.append(
                (
                    ref,
                    pcbnew.ToMM(p.GetPosition().x),
                    pcbnew.ToMM(p.GetPosition().y),
                    0.5 * pcbnew.ToMM(p.GetDrillSize().x),
                )
            )
        else:
            for p in fp.Pads():
                if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                    continue
                bb = p.GetBoundingBox()
                other_pads.append(
                    (
                        f"{ref}.{p.GetNumber()}",
                        pcbnew.ToMM(bb.GetLeft()),
                        pcbnew.ToMM(bb.GetTop()),
                        pcbnew.ToMM(bb.GetRight()),
                        pcbnew.ToMM(bb.GetBottom()),
                    )
                )
    assert mbs, f"[{proj_name}] Expected MB* mouse-bite holes on panel, found 0!"

    mb_problems = []
    for ref, mx, my, mr in mbs:
        for t in board.GetTracks():
            cls = t.GetClass()
            if cls == "PCB_TRACK":
                sx, sy = pcbnew.ToMM(t.GetStart().x), pcbnew.ToMM(t.GetStart().y)
                ex, ey = pcbnew.ToMM(t.GetEnd().x), pcbnew.ToMM(t.GetEnd().y)
                clr = _pt_seg_dist(mx, my, sx, sy, ex, ey) - mr - 0.5 * pcbnew.ToMM(t.GetWidth())
                if clr < min_clr_mm:
                    mb_problems.append(
                        f"{ref} ({mx:.3f},{my:.3f}) -> {board.GetLayerName(t.GetLayer())} track [{t.GetNetname()}] clr={clr:.3f}mm < {min_clr_mm:.2f}mm"
                    )
            elif cls == "PCB_VIA":
                vx, vy = pcbnew.ToMM(t.GetPosition().x), pcbnew.ToMM(t.GetPosition().y)
                clr = math.hypot(mx - vx, my - vy) - mr - 0.5 * pcbnew.ToMM(t.GetWidth(pcbnew.F_Cu))
                if clr < min_clr_mm:
                    mb_problems.append(
                        f"{ref} ({mx:.3f},{my:.3f}) -> via [{t.GetNetname()}] clr={clr:.3f}mm < {min_clr_mm:.2f}mm"
                    )
        for pname, x1, y1, x2, y2 in other_pads:
            dx = max(x1 - mx, 0.0, mx - x2)
            dy = max(y1 - my, 0.0, my - y2)
            clr = math.hypot(dx, dy) - mr
            if clr < min_clr_mm:
                mb_problems.append(
                    f"{ref} ({mx:.3f},{my:.3f}) -> pad {pname} clr={clr:.3f}mm < {min_clr_mm:.2f}mm"
                )
    assert not mb_problems, (
        f"[{proj_name}] Panel mouse-bite copper clearance check FAILED ({len(mb_problems)} issue(s)):\n  - "
        + "\n  - ".join(mb_problems[:25])
    )


def verify_jlcpcb_preflight(
    pcb_path: str,
    proj_name: str,
    zip_path: str,
    is_plate: bool = False,
    is_pmw: bool = False,
    is_panel: bool = False,
    zero_erc_warn: bool = False,
    min_board_mm: float = 20.0,
    extra_forbidden_refs: set = None,
    single_side_layer: str = None,
    bom_groups: dict = None,
    cpl_rows: list = None,
):
    """
    Automated pre-order check against JLCPCB official 2-Layer FR-4 PCB & PCBA manufacturing capabilities:
      1) KiCad DRC (`--schematic-parity` for standalone PCBs) == 0 violations, 0 unconnected, 0 parity mismatches
      2) KiCad ERC on `.kicad_sch` == 0 errors (and 0 warnings on sub/eval PCBs, <=1 intentional GPIO21 warning on main PCBs)
      3) Board outline (`Edge.Cuts`) bounding box within JLCPCB single-board or Economic PCBA panel (<= 250x250 mm) limits
      4) Copper track width >= 0.127 mm (5 mil, 1oz Cu standard)
      5) Via outer diameter >= 0.45 mm, via drill >= 0.30 mm (standard 2-layer no-surcharge), annular ring >= 0.075 mm
      6) PTH drill in [0.20, 6.30] mm, NPTH drill >= 0.50 mm
      7) Gerber ZIP completeness (all 9 Gerber layers + PTH/NPTH Excellon drill files)
      8) PCBA BOM & CPL integrity (100% designator match, valid Cxxxxxx LCSC codes, DNP/THT excluded)
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        drc_json = os.path.join(tmp_dir, "drc.json")
        drc_cmd = [KICAD_CLI, "pcb", "drc", "--format", "json", "-o", drc_json]
        if not is_plate and not is_panel:
            drc_cmd.append("--schematic-parity")
        drc_cmd.append(pcb_path)
        subprocess.run(drc_cmd, check=True, stdout=subprocess.DEVNULL)
        with open(drc_json, encoding="utf-8") as f:
            drc_data = json.load(f)
        v_cnt = len(drc_data.get("violations", []))
        u_cnt = len(drc_data.get("unconnected_items", []))
        p_cnt = len(drc_data.get("schematic_parity", []))
        assert v_cnt == 0 and u_cnt == 0 and p_cnt == 0, (
            f"[{proj_name}] DRC failed: violations={v_cnt}, unconnected={u_cnt}, parity={p_cnt}"
        )

        if not is_plate and not is_panel:
            sch_path = os.path.splitext(pcb_path)[0] + ".kicad_sch"
            erc_json = os.path.join(tmp_dir, "erc.json")
            subprocess.run(
                [KICAD_CLI, "sch", "erc", "--format", "json", "-o", erc_json, sch_path],
                check=True,
                stdout=subprocess.DEVNULL,
            )
            with open(erc_json, encoding="utf-8") as f:
                erc_data = json.load(f)
            erc_errors = 0
            erc_warnings = 0
            for sheet in erc_data.get("sheets", []):
                for v in sheet.get("violations", []):
                    if v.get("Excluded", False):
                        continue
                    sev = v.get("severity", "")
                    if sev == "error":
                        erc_errors += 1
                    elif sev == "warning":
                        erc_warnings += 1
            max_warn = 0 if (is_pmw or zero_erc_warn) else 1
            assert erc_errors == 0 and erc_warnings <= max_warn, (
                f"[{proj_name}] ERC failed: errors={erc_errors}, warnings={erc_warnings} (max {max_warn})"
            )

    board = pcbnew.LoadBoard(pcb_path)
    bb = board.GetBoardEdgesBoundingBox()
    w_mm = round(pcbnew.ToMM(bb.GetWidth()), 2)
    h_mm = round(pcbnew.ToMM(bb.GetHeight()), 2)
    if is_panel:
        assert 70.0 <= w_mm <= 250.0 and 70.0 <= h_mm <= 250.0, (
            f"[{proj_name}] Panel dimensions {w_mm}x{h_mm} mm outside JLCPCB Economic PCBA [70x70, 250x250] mm limits!"
        )
    else:
        min_dim = 10.0 if is_plate else min_board_mm
        assert min_dim <= w_mm <= 400.0 and min_dim <= h_mm <= 500.0, (
            f"[{proj_name}] Board dimensions {w_mm}x{h_mm} mm outside JLCPCB [{min_dim}, 400x500] mm limits!"
        )

    min_track_w = float("inf")
    min_via_w = float("inf")
    min_via_drill = float("inf")
    min_via_ar = float("inf")

    for t in board.GetTracks():
        cls = t.GetClass()
        if cls in ("PCB_TRACK", "PCB_ARC"):
            tw = round(pcbnew.ToMM(t.GetWidth()), 4)
            if tw < min_track_w:
                min_track_w = tw
        elif cls == "PCB_VIA":
            vw = round(pcbnew.ToMM(t.GetWidth(pcbnew.F_Cu)), 4)
            vd = round(pcbnew.ToMM(t.GetDrillValue()), 4)
            ar = round(0.5 * (vw - vd), 4)
            if vw < min_via_w:
                min_via_w = vw
            if vd < min_via_drill:
                min_via_drill = vd
            if ar < min_via_ar:
                min_via_ar = ar

    if not is_plate:
        assert min_track_w >= 0.127, f"[{proj_name}] Track width {min_track_w} mm < JLCPCB 0.127 mm (5 mil) limit!"
        if min_via_w != float("inf"):
            assert min_via_w >= 0.450, f"[{proj_name}] Via diameter {min_via_w} mm < JLCPCB 0.45 mm standard limit!"
            assert min_via_drill >= 0.300, f"[{proj_name}] Via drill {min_via_drill} mm < JLCPCB 0.30 mm standard 2L limit!"
            assert min_via_ar >= 0.075, f"[{proj_name}] Via annular ring {min_via_ar} mm < JLCPCB 0.075 mm limit!"

    min_pth = float("inf")
    max_pth = 0.0
    min_npth = float("inf")
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            dx = pcbnew.ToMM(pad.GetDrillSize().x)
            dy = pcbnew.ToMM(pad.GetDrillSize().y)
            d = round(min(dx, dy) if (dx > 0 and dy > 0) else max(dx, dy), 4)
            if d > 0:
                if pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                    if d < min_npth:
                        min_npth = d
                else:
                    if d < min_pth:
                        min_pth = d
                    if d > max_pth:
                        max_pth = d

    if min_pth != float("inf"):
        assert 0.20 <= min_pth and max_pth <= 6.30, (
            f"[{proj_name}] PTH drill [{min_pth}, {max_pth}] mm outside JLCPCB [0.20, 6.30] mm limits!"
        )
    if min_npth != float("inf"):
        assert min_npth >= 0.50, f"[{proj_name}] NPTH drill {min_npth} mm < JLCPCB 0.50 mm limit!"

    if not is_plate:
        verify_pcb_3d_step_models(board, pcb_path, proj_name, is_pmw=is_pmw, is_panel=is_panel)
        verify_screw_hole_copper_keepouts(board, proj_name, is_pmw=is_pmw, is_panel=is_panel)
        verify_zero_via_in_pad(board, proj_name)
    if is_panel:
        verify_panel_mousebite_clearances(board, proj_name, min_clr_mm=0.48)

    # Verify Gerber ZIP contents
    with zipfile.ZipFile(zip_path, "r") as zf:
        znames = zf.namelist()
    required_suffixes = [
        "-F_Cu.gtl", "-B_Cu.gbl", "-F_Paste.gtp", "-B_Paste.gbp",
        "-F_Silkscreen.gto", "-B_Silkscreen.gbo", "-F_Mask.gts", "-B_Mask.gbs",
        "-Edge_Cuts.gm1", "-PTH.drl", "-NPTH.drl",
    ]
    for suf in required_suffixes:
        assert any(n.endswith(suf) for n in znames), f"[{proj_name}] Missing {suf} in {zip_path}!"

    if not is_plate and bom_groups is not None and cpl_rows is not None:
        bom_refs = set()
        for (_, _, lcsc), refs in bom_groups.items():
            assert re.match(r"^C\d+$", lcsc), f"[{proj_name}] Invalid LCSC part number: {lcsc}"
            bom_refs.update(refs)
        cpl_refs = {row[0] for row in cpl_rows}
        assert bom_refs == cpl_refs, f"[{proj_name}] BOM/CPL mismatch: {bom_refs ^ cpl_refs}"
        forbidden_dnp = {"J4", "rJ4", "rEXSW1", "U1" if is_pmw else "", "JP1"}
        if extra_forbidden_refs:
            forbidden_dnp |= set(extra_forbidden_refs)
        assert not (bom_refs & forbidden_dnp), f"[{proj_name}] DNP/THT ref found in BOM/CPL: {bom_refs & forbidden_dnp}"
        if single_side_layer is not None:
            wrong_side = [row[0] for row in cpl_rows if row[6] != single_side_layer]
            assert not wrong_side, (
                f"[{proj_name}] Expected single-sided '{single_side_layer}' PCBA, found wrong-side refs: {wrong_side}"
            )

    via_w_disp = 0.0 if (is_plate or min_via_w == float("inf")) else min_via_w
    via_d_disp = 0.0 if (is_plate or min_via_drill == float("inf")) else min_via_drill
    print(
        f"[{proj_name}] JLCPCB preflight OK: size={w_mm:.2f}x{h_mm:.2f}mm, "
        f"DRC=0, track>={0.0 if is_plate else min_track_w:.2f}mm, "
        f"via>={via_w_disp:.2f}/{via_d_disp:.2f}mm"
    )


def export_main_pcb(
    pcb_path,
    proj_name,
    is_right=False,
    is_pmw=False,
    is_panel=False,
    custom_map=None,
    zero_erc_warn=False,
    min_board_mm=20.0,
    extra_forbidden_refs=None,
    single_side_layer=None,
):
    out_dir = os.path.join(os.path.dirname(pcb_path), "jlcpcb", "production_files")
    os.makedirs(out_dir, exist_ok=True)
    zip_path = os.path.join(out_dir, f"GERBER-{proj_name}.zip")
    export_gerber_zip(pcb_path, zip_path)

    board = pcbnew.LoadBoard(pcb_path)
    aux = board.GetDesignSettings().GetAuxOrigin()
    ox, oy = pcbnew.ToMM(aux.x), pcbnew.ToMM(aux.y)

    bom_groups = {}
    cpl_rows = []
    exclude_mask = (
        pcbnew.FP_EXCLUDE_FROM_BOM
        | pcbnew.FP_EXCLUDE_FROM_POS_FILES
        | pcbnew.FP_DNP
    )

    for fp in sorted(board.GetFootprints(), key=lambda f: f.GetReference()):
        if fp.GetAttributes() & exclude_mask:
            continue
        ref = fp.GetReference()
        info = get_part_info(ref, is_right=is_right, is_pmw=is_pmw, is_panel=is_panel, custom_map=custom_map)
        if not info:
            continue
        comment, pkg, lcsc = info
        bom_groups.setdefault((comment, pkg, lcsc), []).append(ref)

        pos = fp.GetPosition()
        px_mm = pcbnew.ToMM(pos.x)
        py_mm = pcbnew.ToMM(pos.y)

        # Normalize CPL center coordinates to match JLCPCB DFM component centroids (Tasks 2-1 & 2-2):
        if pkg == "TYPE-C-31-M-13C":
            sh_pads = [p for p in fp.Pads() if p.GetNumber() == "SH"]
            if sh_pads:
                px_mm = sum(pcbnew.ToMM(p.GetPosition().x) for p in sh_pads) / len(sh_pads)
                py_mm = sum(pcbnew.ToMM(p.GetPosition().y) for p in sh_pads) / len(sh_pads)
        elif pkg in ("R_0402_1005Metric", "C_0402_1005Metric", "R_0603_1608Metric", "C_0603_1608Metric", "D_SOD-523", "D_SOD-323"):
            p1 = fp.FindPadByNumber("1")
            p2 = fp.FindPadByNumber("2")
            if p1 is not None and p2 is not None:
                px_mm = 0.5 * (pcbnew.ToMM(p1.GetPosition().x) + pcbnew.ToMM(p2.GetPosition().x))
                py_mm = 0.5 * (pcbnew.ToMM(p1.GetPosition().y) + pcbnew.ToMM(p2.GetPosition().y))

        x_mm = round(px_mm - ox, 6)
        y_mm = round(oy - py_mm, 6)
        krot = fp.GetOrientationDegrees()
        rot_offset = JLCPCB_ROT_OFFSETS.get(pkg, 0.0)
        layer = "bottom" if fp.GetLayer() == pcbnew.B_Cu else "top"
        if layer == "bottom":
            crot = round((180.0 - krot + rot_offset) % 360.0, 2)
        else:
            crot = round((krot + rot_offset) % 360.0, 2)
        if pkg in ("R_0402_1005Metric", "C_0402_1005Metric", "R_0603_1608Metric", "C_0603_1608Metric"):
            crot = round(crot % 180.0, 2)
        cpl_rows.append([ref, comment, pkg, x_mm, y_mm, crot, layer])

    bom_path = os.path.join(out_dir, f"BOM-{proj_name}.csv")
    with open(bom_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC"])
        for (comment, pkg, lcsc), refs in sorted(
            bom_groups.items(), key=lambda x: x[0][2]
        ):
            w.writerow([comment, ",".join(refs), pkg, lcsc])

    cpl_path = os.path.join(out_dir, f"CPL-{proj_name}.csv")
    with open(cpl_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            ["Designator", "Val", "Package", "Mid X", "Mid Y", "Rotation", "Layer"]
        )
        for row in cpl_rows:
            w.writerow(row)

    verify_jlcpcb_preflight(
        pcb_path,
        proj_name,
        zip_path,
        is_plate=False,
        is_pmw=is_pmw,
        is_panel=is_panel,
        zero_erc_warn=zero_erc_warn,
        min_board_mm=min_board_mm,
        extra_forbidden_refs=extra_forbidden_refs,
        single_side_layer=single_side_layer,
        bom_groups=bom_groups,
        cpl_rows=cpl_rows,
    )
    print(
        f"Exported {proj_name}: GERBER-{proj_name}.zip, {len(cpl_rows)} CPL items, {len(bom_groups)} BOM groups"
    )


def _v2i_mm(x_mm: float, y_mm: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(pcbnew.FromMM(round(x_mm, 6)), pcbnew.FromMM(round(y_mm, 6)))


def _make_rect_poly(x1: float, y1: float, x2: float, y2: float) -> pcbnew.SHAPE_POLY_SET:
    ps = pcbnew.SHAPE_POLY_SET()
    ps.NewOutline()
    ps.Append(pcbnew.FromMM(x1), pcbnew.FromMM(y1))
    ps.Append(pcbnew.FromMM(x2), pcbnew.FromMM(y1))
    ps.Append(pcbnew.FromMM(x2), pcbnew.FromMM(y2))
    ps.Append(pcbnew.FromMM(x1), pcbnew.FromMM(y2))
    return ps


def _dup_board_item(item):
    try:
        return item.Duplicate(False)
    except TypeError:
        return item.Duplicate()


def _load_transformed_subboard(pcb_path: Path, rot_deg: float, dx_mm: float, dy_mm: float, ref_prefix: str = ""):
    b = pcbnew.LoadBoard(str(pcb_path))
    if abs(rot_deg) > 1e-6:
        ang = pcbnew.EDA_ANGLE(rot_deg, pcbnew.DEGREES_T)
        origin = _v2i_mm(0.0, 0.0)
        for col in (b.GetFootprints(), b.GetTracks(), b.Zones(), b.GetDrawings()):
            for it in col:
                it.Rotate(origin, ang)
    delta = _v2i_mm(dx_mm, dy_mm)
    for fp in b.GetFootprints():
        fp.Move(delta)
        if ref_prefix:
            fp.SetReference(f"{ref_prefix}{fp.GetReference()}")
    for col in (b.GetTracks(), b.Zones(), b.GetDrawings()):
        for it in col:
            it.Move(delta)

    full_ps = pcbnew.SHAPE_POLY_SET()
    b.GetBoardPolygonOutlines(full_ps, False)
    assert full_ps.OutlineCount() == 1, f"Expected 1 outer outline in {pcb_path.name}, got {full_ps.OutlineCount()}"
    outer_ps = pcbnew.SHAPE_POLY_SET()
    outer_ps.AddOutline(full_ps.Outline(0))
    return b, outer_ps


def _is_outer_edge_drawing(drw, outer_chain: pcbnew.SHAPE_LINE_CHAIN, tol_mm: float = 0.25) -> bool:
    if drw.GetLayer() != pcbnew.Edge_Cuts or drw.GetShape() == pcbnew.SHAPE_T_CIRCLE:
        return False
    pts = [drw.GetStart(), drw.GetEnd()]
    if drw.GetShape() == pcbnew.SHAPE_T_ARC:
        pts.append(drw.GetArcMid())
    tol_iu = pcbnew.FromMM(tol_mm)
    for pt in pts:
        nearest = outer_chain.NearestPoint(pt)
        if math.hypot(pt.x - nearest.x, pt.y - nearest.y) > tol_iu:
            return False
    return True


def _append_subboard_into_panel(
    panel: pcbnew.BOARD,
    src: pcbnew.BOARD,
    outer_ps: pcbnew.SHAPE_POLY_SET,
    net_prefix: str,
):
    outer_chain = outer_ps.Outline(0)
    net_map = {0: 0}
    for netcode, netinfo in src.GetNetsByNetcode().items():
        if netcode == 0:
            continue
        ni = pcbnew.NETINFO_ITEM(panel, f"{net_prefix}:{netinfo.GetNetname()}")
        panel.Add(ni)
        net_map[netcode] = ni.GetNetCode()

    for fp in src.GetFootprints():
        fp_clone = pcbnew.Cast_to_FOOTPRINT(_dup_board_item(fp))
        panel.Add(fp_clone)
        for pad in fp_clone.Pads():
            old_nc = pad.GetNetCode()
            pad.SetNetCode(net_map.get(old_nc, 0) if old_nc in net_map else 0)

    for trk in src.GetTracks():
        t_clone = pcbnew.Cast_to_PCB_TRACK(_dup_board_item(trk))
        panel.Add(t_clone)
        t_clone.SetNetCode(net_map.get(trk.GetNetCode(), 0))

    for zn in src.Zones():
        z_clone = pcbnew.Cast_to_ZONE(_dup_board_item(zn))
        panel.Add(z_clone)
        if not z_clone.GetIsRuleArea():
            z_clone.SetNetCode(net_map.get(zn.GetNetCode(), 0))

    for drw in src.GetDrawings():
        if drw.GetLayer() == pcbnew.Edge_Cuts and _is_outer_edge_drawing(drw, outer_chain):
            continue
        panel.Add(_dup_board_item(drw))


def _add_panel_npth_hole(
    panel: pcbnew.BOARD,
    ref: str,
    x_mm: float,
    y_mm: float,
    diam_mm: float,
    zone_keepout_r_mm: float = 0.0,
):
    fp = pcbnew.FOOTPRINT(panel)
    fp.SetReference(ref)
    fp.SetValue("NPTH")
    fp.SetPosition(_v2i_mm(x_mm, y_mm))
    fp.SetAttributes(
        pcbnew.FP_THROUGH_HOLE | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES | pcbnew.FP_DNP
    )
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)

    pad = pcbnew.PAD(fp)
    pad.SetNumber("1")
    pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    pad.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
    sz = pcbnew.VECTOR2I(pcbnew.FromMM(diam_mm), pcbnew.FromMM(diam_mm))
    pad.SetSize(sz)
    pad.SetDrillSize(sz)
    pad.SetLayerSet(pad.UnplatedHoleMask())
    fp.Add(pad)

    cy = pcbnew.PCB_SHAPE(fp)
    cy.SetShape(pcbnew.SHAPE_T_CIRCLE)
    cy.SetLayer(pcbnew.F_CrtYd)
    cy.SetWidth(pcbnew.FromMM(0.05))
    cy.SetCenter(_v2i_mm(x_mm, y_mm))
    cy.SetEnd(_v2i_mm(x_mm + diam_mm * 0.5, y_mm))
    fp.Add(cy)
    panel.Add(fp)

    if zone_keepout_r_mm > 0.0:
        for lid in (pcbnew.F_Cu, pcbnew.B_Cu):
            kz = pcbnew.ZONE(panel)
            kz.SetIsRuleArea(True)
            kz.SetLayer(lid)
            kz.SetDoNotAllowTracks(True)
            kz.SetDoNotAllowVias(True)
            kz.SetDoNotAllowPads(False)  # Allow the MB* NPTH pad itself; copper pads checked by verify_panel_mousebite_clearances
            kz.SetDoNotAllowZoneFills(True)
            kz.SetDoNotAllowFootprints(False)
            kol = kz.Outline()
            kol.NewOutline()
            for k in range(24):
                ang = 2.0 * math.pi * k / 24.0
                kol.Append(
                    pcbnew.FromMM(x_mm + zone_keepout_r_mm * math.cos(ang)),
                    pcbnew.FromMM(y_mm + zone_keepout_r_mm * math.sin(ang)),
                )
            panel.Add(kz)


def _add_panel_fiducial(panel: pcbnew.BOARD, ref: str, x_mm: float, y_mm: float):
    for side_suf, cu_layer, mask_layer, crtyd_layer in [
        ("F", pcbnew.F_Cu, pcbnew.F_Mask, pcbnew.F_CrtYd),
        ("B", pcbnew.B_Cu, pcbnew.B_Mask, pcbnew.B_CrtYd),
    ]:
        fp = pcbnew.FOOTPRINT(panel)
        fp.SetReference(f"{ref}_{side_suf}")
        fp.SetValue("Fiducial_1mm_Mask2mm")
        fp.SetLayer(cu_layer)
        fp.SetPosition(_v2i_mm(x_mm, y_mm))
        fp.SetAttributes(
            pcbnew.FP_SMD | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES | pcbnew.FP_DNP
        )
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)

        pad = pcbnew.PAD(fp)
        pad.SetNumber("1")
        pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
        pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        pad.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.00), pcbnew.FromMM(1.00)))
        lset = pcbnew.LSET()
        lset.AddLayer(cu_layer)
        lset.AddLayer(mask_layer)
        pad.SetLayerSet(lset)
        pad.SetLocalSolderMaskMargin(pcbnew.FromMM(0.50))  # Ø 1.00 mm Cu / Ø 2.00 mm mask opening
        fp.Add(pad)

        cy = pcbnew.PCB_SHAPE(fp)
        cy.SetShape(pcbnew.SHAPE_T_CIRCLE)
        cy.SetLayer(crtyd_layer)
        cy.SetWidth(pcbnew.FromMM(0.05))
        cy.SetCenter(_v2i_mm(x_mm, y_mm))
        cy.SetEnd(_v2i_mm(x_mm + 1.05, y_mm))
        fp.Add(cy)
        panel.Add(fp)


def _add_chain_to_edge_cuts(panel: pcbnew.BOARD, chain: pcbnew.SHAPE_LINE_CHAIN, width_mm: float = 0.05):
    min_seg_iu = pcbnew.FromMM(0.002)  # Merge sub-2um Clipper rounding artifacts while keeping exact closed loops
    pts = []
    for i in range(chain.PointCount()):
        p = chain.CPoint(i)
        if not pts or math.hypot(p.x - pts[-1].x, p.y - pts[-1].y) >= min_seg_iu:
            pts.append(p)
    while len(pts) > 3 and math.hypot(pts[-1].x - pts[0].x, pts[-1].y - pts[0].y) < min_seg_iu:
        pts.pop()
    m = len(pts)
    for i in range(m):
        p1 = pts[i]
        p2 = pts[(i + 1) % m]
        seg = pcbnew.PCB_SHAPE(panel)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetWidth(pcbnew.FromMM(width_mm))
        seg.SetStart(p1)
        seg.SetEnd(p2)
        panel.Add(seg)


def build_and_export_panel_3in1():
    """
    Build & export the unified 3-in-1 Economic PCBA Panel (`131.00 x 207.20 mm`):
      - Combines `curcur40-left` (0 deg), `curcur40-right` (180 deg), and `curcur40-pmw3360` (0 deg, nested inside
        the combined West L-pocket with `p*` designators) onto a single bottom-side SMT panel.
      - Continuous 5.00 mm outer conveyor rails + continuous West-to-East internal H-rib stiffener.
      - 3.70 mm CNC-milled open air slots in front of all 4 mid-mount USB-C receptacles (`J1, J2, rJ1, rJ2`),
        eliminating CAM rail-blocking defects (JLCPCB issue #4).
      - 22x recessed mouse-bite tabs (4x Ø 0.55 mm NPTH @ 0.85 mm pitch, inset 0.08–0.10 mm inside nominal board edges
        with >= 0.35 mm copper zone keepout; all milled slot corners rounded to R = 0.80 mm = Ø 1.60 mm standard JLCPCB
        CNC router endmill, preserving R = 0.90 mm USB-C inner corner dogbone reliefs), eliminating L-step mouse-bite
        overhang & outer burrs (JLCPCB issue #1) and USB-C shell corner interference.
    """
    panel_dir = WORKSPACE / "pcbs" / "panel"
    panel_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(WORKSPACE / "pcbs" / "left" / "fp-lib-table", panel_dir / "fp-lib-table")
    pro_data = json.loads((WORKSPACE / "pcbs" / "left" / "curcur40-left.kicad_pro").read_text(encoding="utf-8"))
    pro_data["sheets"] = []
    (panel_dir / "curcur40-panel-3in1.kicad_pro").write_text(
        json.dumps(pro_data, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    w_pan = 131.0000
    h_pan = 207.2000

    dx_l, dy_l = 127.0625, 36.3625
    b_left, ps_left = _load_transformed_subboard(
        WORKSPACE / "pcbs" / "left" / "curcur40-left.kicad_pcb", 0.0, dx_l, dy_l
    )
    dx_r, dy_r = 127.0625, 170.8375
    b_right, ps_right = _load_transformed_subboard(
        WORKSPACE / "pcbs" / "right" / "curcur40-right.kicad_pcb", 180.0, dx_r, dy_r
    )
    dx_p, dy_p = -5.7875, 55.4625
    b_pmw, ps_pmw = _load_transformed_subboard(
        WORKSPACE / "pcbs" / "pmw3360" / "curcur40-pmw3360.kicad_pcb", 0.0, dx_p, dy_p, ref_prefix="p"
    )

    panel = pcbnew.LoadBoard(str(WORKSPACE / "pcbs" / "left" / "curcur40-left.kicad_pcb"))
    for item in list(panel.GetFootprints()) + list(panel.GetTracks()) + list(panel.Zones()) + list(panel.GetDrawings()):
        panel.Delete(item)
    panel.GetDesignSettings().SetAuxOrigin(_v2i_mm(0.0, h_pan))

    _append_subboard_into_panel(panel, b_left, ps_left, "L")
    _append_subboard_into_panel(panel, b_right, ps_right, "R")
    _append_subboard_into_panel(panel, b_pmw, ps_pmw, "P")

    outer_panel = _make_rect_poly(0.0, 0.0, w_pan, h_pan)
    outer_panel.Fillet(pcbnew.FromMM(1.50), pcbnew.FromMM(0.01))

    air_cavity = _make_rect_poly(5.00, 5.00, w_pan - 5.00, h_pan - 5.00)

    # Continuous West-to-East internal H-rib stiffener (>= 2.05 mm router kerf around PMW3360 & Thumb West edges):
    ribs = [
        _make_rect_poly(39.65, 102.10, w_pan - 4.00, 105.10),  # East Center Horizontal Rib
        _make_rect_poly(4.00, 78.10, 42.55, 85.90),            # Upper West L-Pocket Rib
        _make_rect_poly(4.00, 121.30, 42.55, 129.10),          # Lower West L-Pocket Rib
        _make_rect_poly(39.65, 78.10, 42.55, 129.10),          # Vertical Tie Rib connecting all 3 ribs!
    ]
    for r_ps in ribs:
        air_cavity.BooleanSubtract(r_ps)

    for bps in (ps_left, ps_right, ps_pmw):
        air_cavity.BooleanSubtract(bps)

    tab_w = 3.60
    mb_offsets = (-1.275, -0.425, 0.425, 1.275)
    mb_diam = 0.55

    tabs = [
        # Left Main PCB (9 tabs — 0.10 mm inset keeps breakaway inside board profile with generous >= 0.35 mm Cu margin)
        ("H_EDGE", -95.5 + dx_l, 8.7000, -1, 0.10),
        ("H_EDGE", -21.5 + dx_l, 8.7000, -1, 0.10),
        ("H_EDGE", -69.0 + dx_l, 99.1000, +1, 0.10),
        ("H_EDGE", -21.0 + dx_l, 99.1000, +1, 0.10),
        ("H_EDGE", -101.5 + dx_l, 74.9625, +1, 0.10),
        ("V_EDGE", -16.0 + dy_l, 8.0000, -1, 0.10),
        ("V_EDGE",  22.0 + dy_l, 8.0000, -1, 0.10),
        ("V_EDGE", -24.0 + dy_l, 122.3000, +1, 0.10),
        ("V_EDGE",  52.0 + dy_l, 122.3000, +1, 0.10),
        # Right Main PCB (9 tabs)
        ("H_EDGE", -96.3 + dx_r, 198.5000, +1, 0.10),
        ("H_EDGE", -22.3 + dx_r, 198.5000, +1, 0.10),
        ("H_EDGE", -74.0 + dx_r, 108.1000, -1, 0.10),
        ("H_EDGE",  -9.3 + dx_r, 108.1000, -1, 0.10),
        ("H_EDGE", -101.0 + dx_r, 132.2375, -1, 0.10),
        ("V_EDGE",  13.0 + dy_r, 8.0000, -1, 0.10),
        ("V_EDGE", -22.0 + dy_r, 8.0000, -1, 0.10),
        ("V_EDGE",  16.0 + dy_r, 122.3000, +1, 0.10),
        ("V_EDGE", -16.0 + dy_r, 122.3000, +1, 0.10),
        # PMW3360 Sensor Sub-PCB (4 tabs)
        ("H_EDGE", 27.7 + dx_p, 89.0000, -1, 0.10),
        ("H_EDGE", 17.7 + dx_p, 118.2000, +1, 0.10),
        ("V_EDGE", 41.5 + dy_p, 8.0000, -1, 0.10),
        ("V_EDGE", 53.5 + dy_p, 8.0000, -1, 0.10),
    ]

    mb_keepout_r = 0.5 * mb_diam + 0.50  # >= 0.48–0.50 mm NPTH-to-copper clearance across all tracks/vias/pads/zones!
    mb_idx = 1
    for kind, c_along, edge_v, sign, inset_mm in tabs:
        if kind == "H_EDGE":
            ya = min(edge_v - sign * 1.20, edge_v + sign * 4.50)
            yb = max(edge_v - sign * 1.20, edge_v + sign * 4.50)
            air_cavity.BooleanSubtract(_make_rect_poly(c_along - tab_w / 2.0, ya, c_along + tab_w / 2.0, yb))
            mb_y = edge_v - sign * inset_mm
            for off in mb_offsets:
                _add_panel_npth_hole(panel, f"MB{mb_idx}", c_along + off, mb_y, mb_diam, zone_keepout_r_mm=mb_keepout_r)
                mb_idx += 1
        else:
            xa = min(edge_v - sign * 1.20, edge_v + sign * 4.50)
            xb = max(edge_v - sign * 1.20, edge_v + sign * 4.50)
            air_cavity.BooleanSubtract(_make_rect_poly(xa, c_along - tab_w / 2.0, xb, c_along + tab_w / 2.0))
            mb_x = edge_v - sign * inset_mm
            for off in mb_offsets:
                _add_panel_npth_hole(panel, f"MB{mb_idx}", mb_x, c_along + off, mb_diam, zone_keepout_r_mm=mb_keepout_r)
                mb_idx += 1

    # CNC router endmill morphological opening (R = 0.80 mm => Ø 1.60 mm standard JLCPCB PCB/panel router bit;
    # rounds all tab corners smoothly while preserving R = 0.90 mm USB-C inner corner dogbone reliefs intact!)
    r_mill = pcbnew.FromMM(0.80)
    max_err = pcbnew.FromMM(0.005)
    air_cavity.Inflate(-r_mill, pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, max_err)
    air_cavity.Inflate(+r_mill, pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, max_err)

    solid_panel = pcbnew.SHAPE_POLY_SET(outer_panel)
    solid_panel.BooleanSubtract(air_cavity)
    assert solid_panel.OutlineCount() == 1, (
        f"Expected single connected 3-in-1 panel frame, got {solid_panel.OutlineCount()} islands!"
    )

    _add_chain_to_edge_cuts(panel, solid_panel.Outline(0))
    for h_idx in range(solid_panel.HoleCount(0)):
        _add_chain_to_edge_cuts(panel, solid_panel.Hole(0, h_idx))

    # 3 Asymmetric Fiducials (Ø 1.00 mm Cu / Ø 2.00 mm Mask at >= 4.20 mm from outer edges) + 4 Tooling Holes (Ø 2.00 mm)
    _add_panel_fiducial(panel, "FID1", 4.20, 4.20)
    _add_panel_fiducial(panel, "FID2", w_pan - 4.20, 4.20)
    _add_panel_fiducial(panel, "FID3", 4.20, h_pan - 4.20)
    for idx, (tx, ty) in enumerate(
        [
            (14.00, 2.50),
            (w_pan - 14.00, 2.50),
            (14.00, h_pan - 2.50),
            (w_pan - 14.00, h_pan - 2.50),
        ],
        1,
    ):
        _add_panel_npth_hole(panel, f"TH{idx}", tx, ty, 2.00)

    for lyr, mir in [(pcbnew.F_SilkS, False), (pcbnew.B_SilkS, True)]:
        txt = pcbnew.PCB_TEXT(panel)
        txt.SetText("curcur40 v1.1 3-in-1 PCBA Panel (Left + Right + PMW3360)")
        txt.SetLayer(lyr)
        txt.SetPosition(_v2i_mm(w_pan / 2.0, 2.50))
        txt.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.2), pcbnew.FromMM(1.2)))
        txt.SetTextThickness(pcbnew.FromMM(0.2))
        txt.SetMirrored(mir)
        panel.Add(txt)

    pcbnew.ZONE_FILLER(panel).Fill(panel.Zones())
    out_pcb = panel_dir / "curcur40-panel-3in1.kicad_pcb"
    panel.Save(str(out_pcb))

    export_main_pcb(
        str(out_pcb),
        "curcur40-panel-3in1",
        is_panel=True,
        extra_forbidden_refs={"pU1", "pJP1", "pR4", "pC5"},
        single_side_layer="bottom",
    )


def export_top_plates():
    plate_dir = str(WORKSPACE / "plates" / "pcb")
    out_dir = os.path.join(plate_dir, "jlcpcb", "production_files")
    os.makedirs(out_dir, exist_ok=True)
    for name in ("plate-top-left", "plate-top-right"):
        pcb_path = os.path.join(plate_dir, f"{name}.kicad_pcb")
        zip_path = os.path.join(out_dir, f"GERBER-{name}.zip")
        export_gerber_zip(pcb_path, zip_path)
        verify_jlcpcb_preflight(pcb_path, name, zip_path, is_plate=True)
        print(f"Exported Top Plate Gerber: {zip_path}")


if __name__ == "__main__":
    export_main_pcb(
        str(WORKSPACE / "pcbs" / "right" / "curcur40-right.kicad_pcb"),
        "curcur40-right",
        is_right=True,
    )
    export_main_pcb(
        str(WORKSPACE / "pcbs" / "left" / "curcur40-left.kicad_pcb"),
        "curcur40-left",
        is_right=False,
    )
    export_main_pcb(
        str(WORKSPACE / "pcbs" / "pmw3360" / "curcur40-pmw3360.kicad_pcb"),
        "curcur40-pmw3360",
        is_pmw=True,
    )
    build_and_export_panel_3in1()
    export_top_plates()
