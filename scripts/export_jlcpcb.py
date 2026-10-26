# -*- coding: utf-8 -*-
"""
Export JLCPCB PCB / PCBA production files for curcur40:
- Left Main PCB:      pcbs/left/jlcpcb/production_files/{GERBER,BOM,CPL}-curcur40-left.*
- Right Main PCB:     pcbs/right/jlcpcb/production_files/{GERBER,BOM,CPL}-curcur40-right.*
- PMW3360 Sub PCB:    pcbs/pmw3360/jlcpcb/production_files/{GERBER,BOM,CPL}-curcur40-pmw3360.*
- Wheel Sensor PCB:   pcbs/inertia-wheel-sensor/jlcpcb/production_files/{GERBER,BOM,CPL}-curcur40-wheel-sensor.*
- Wheel Eval PCB:     pcbs/inertia-wheel-eval/jlcpcb/production_files/{GERBER,BOM,CPL}-curcur40-wheel-eval.*
- Top Plates:         plates/pcb/jlcpcb/production_files/GERBER-plate-top-{left,right}.zip
"""
import os
import re
import csv
import json
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
    "U3": ("TPD4E05U06DQAR", "USON-10_2.5x1.0mm_P0.5mm", "C138714"),
    "U5": ("TPD4E05U06DQAR", "USON-10_2.5x1.0mm_P0.5mm", "C138714"),
    "ZD1": ("RB521S30T1G", "D_SOD-523", "C145179"),
    "U2": ("NCP1117LPST33T3G", "SOT-223-3_TabPin2", "C146799"),
    "C3": ("100n", "C_0402_1005Metric", "C1525"),
    "C4": ("100n", "C_0402_1005Metric", "C1525"),
    "C7": ("100n", "C_0402_1005Metric", "C1525"),
    "C9": ("100n", "C_0402_1005Metric", "C1525"),
    "C10": ("100n", "C_0402_1005Metric", "C1525"),
    "C12": ("100n", "C_0402_1005Metric", "C1525"),
    "C13": ("100n", "C_0402_1005Metric", "C1525"),
    "C14": ("100n", "C_0402_1005Metric", "C1525"),
    "C15": ("100n", "C_0402_1005Metric", "C1525"),
    "C17": ("100n", "C_0402_1005Metric", "C1525"),
    "C18": ("100n", "C_0402_1005Metric", "C1525"),
    "C6": ("10u", "C_0402_1005Metric", "C15525"),
    "C11": ("10u", "C_0402_1005Metric", "C15525"),
    "C1": ("27p", "C_0402_1005Metric", "C1557"),
    "C2": ("27p", "C_0402_1005Metric", "C1557"),
    "U1": ("RP2040", "QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm", "C2040"),
    "D1": ("1N4148WT", "D_SOD-523", "C232841"),
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
    "J5": ("SM06B-SRSS-TB(LF)(SN)", "JST_SH_SM06B-SRSS-TB_1x06-1MP_P1.00mm_Horizontal", "C160405"),
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

WHEEL_SENSOR_PARTS = {
    "U1": ("AS5600-ASOT", "SOIC-8_3.9x4.9mm_P1.27mm", "C499458"),
    "C1": ("100nF", "C_0402_1005Metric", "C1525"),
    "C2": ("1uF", "C_0402_1005Metric", "C52923"),
}

WHEEL_EVAL_PARTS = {
    "J1": ("SM06B-SRSS-TB(LF)(SN)", "JST_SH_SM06B-SRSS-TB_1x06-1MP_P1.00mm_Horizontal", "C160405"),
    "C1": ("100nF", "C_0402_1005Metric", "C1525"),
    "R1": ("4.7k", "R_0402_1005Metric", "C25900"),
    "R2": ("4.7k", "R_0402_1005Metric", "C25900"),
}


def get_part_info(ref, is_right=False, is_pmw=False, custom_map=None):
    if custom_map is not None:
        return custom_map.get(ref)
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
    "SOIC-8_3.9x4.9mm_P1.27mm": 270.0,       # Wheel Sensor U1 (AS5600-ASOT, C499458): -90 deg in Top view
    "SOIC-8_5.3x5.3mm_P1.27mm": 270.0,       # U4/rU4 (W25Q128JVSIQ, C97521/C113767): 90 deg CW in Bottom view
    "SOT-223-3_TabPin2": 180.0,              # U2/rU2 (NCP1117LPST33T3G, C146799): 180 deg in Bottom view
    "USON-10_2.5x1.0mm_P0.5mm": 270.0,       # U3/U5, rU3/rU5 (TPD4E05U06DQAR, C138714): 90 deg CW in Bottom view
    "SOT-23-5": 180.0,                       # PMW3360 U2 (TLV74318PDBVR, C485152): 180 deg in Bottom view
}


def verify_jlcpcb_preflight(
    pcb_path: str,
    proj_name: str,
    zip_path: str,
    is_plate: bool = False,
    is_pmw: bool = False,
    zero_erc_warn: bool = False,
    min_board_mm: float = 20.0,
    extra_forbidden_refs: set = None,
    single_side_layer: str = None,
    bom_groups: dict = None,
    cpl_rows: list = None,
):
    """
    Automated pre-order check against JLCPCB official 2-Layer FR-4 PCB & PCBA manufacturing capabilities:
      1) KiCad DRC (`--schematic-parity` for PCBs) == 0 violations, 0 unconnected, 0 parity mismatches
      2) KiCad ERC on `.kicad_sch` == 0 errors (and 0 warnings on sub/eval PCBs, <=1 intentional GPIO21 warning on main PCBs)
      3) Board outline (`Edge.Cuts`) bounding box within JLCPCB single-board PCBA/PCB size limits
      4) Copper track width >= 0.127 mm (5 mil, 1oz Cu standard)
      5) Via outer diameter >= 0.45 mm, via drill >= 0.30 mm (standard 2-layer no-surcharge), annular ring >= 0.075 mm
      6) PTH drill in [0.20, 6.30] mm, NPTH drill >= 0.50 mm
      7) Gerber ZIP completeness (all 9 Gerber layers + PTH/NPTH Excellon drill files)
      8) PCBA BOM & CPL integrity (100% designator match, valid Cxxxxxx LCSC codes, DNP/THT excluded)
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        drc_json = os.path.join(tmp_dir, "drc.json")
        drc_cmd = [KICAD_CLI, "pcb", "drc", "--format", "json", "-o", drc_json]
        if not is_plate:
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

        if not is_plate:
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
    min_dim = 10.0 if is_plate else min_board_mm  # JLCPCB PCBA single-board min is 20x20 mm (bare PCB / panelized sub-PCB >= 5x5 mm)
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
        forbidden_dnp = {"J4", "rJ4", "U1" if is_pmw else "", "JP1"}
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
        info = get_part_info(ref, is_right=is_right, is_pmw=is_pmw, custom_map=custom_map)
        if not info:
            continue
        comment, pkg, lcsc = info
        bom_groups.setdefault((comment, pkg, lcsc), []).append(ref)

        pos = fp.GetPosition()
        px_mm = pcbnew.ToMM(pos.x)
        py_mm = pcbnew.ToMM(pos.y)

        x_mm = round(px_mm - ox, 6)
        y_mm = round(oy - py_mm, 6)
        krot = fp.GetOrientationDegrees()
        rot_offset = JLCPCB_ROT_OFFSETS.get(pkg, 0.0)
        layer = "bottom" if fp.GetLayer() == pcbnew.B_Cu else "top"
        if layer == "bottom":
            crot = round((180.0 - krot + rot_offset) % 360.0, 2)
        else:
            crot = round((krot + rot_offset) % 360.0, 2)
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
    export_main_pcb(
        str(WORKSPACE / "pcbs" / "inertia-wheel-sensor" / "curcur40-wheel-sensor.kicad_pcb"),
        "curcur40-wheel-sensor",
        custom_map=WHEEL_SENSOR_PARTS,
        zero_erc_warn=True,
        min_board_mm=20.0,
        extra_forbidden_refs={"J1", "MB1", "MB2"},
        single_side_layer="top",
    )
    export_main_pcb(
        str(WORKSPACE / "pcbs" / "inertia-wheel-eval" / "curcur40-wheel-eval.kicad_pcb"),
        "curcur40-wheel-eval",
        custom_map=WHEEL_EVAL_PARTS,
        zero_erc_warn=True,
        min_board_mm=20.0,
        extra_forbidden_refs={"U1", "SW1", "J2", "H1", "H2", "H3", "H4", "H5", "H6"},
        single_side_layer="top",
    )
    export_top_plates()
