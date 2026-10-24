# -*- coding: utf-8 -*-
"""
Export JLCPCB PCB / PCBA production files for curcur40:
- Left Main PCB:    pcbs/left/jlcpcb/production_files/{GERBER,BOM,CPL}-curcur40-left.*
- Right Main PCB:   pcbs/right/jlcpcb/production_files/{GERBER,BOM,CPL}-curcur40-right.*
- PMW3360 Sub PCB:  pcbs/pmw3360/jlcpcb/production_files/{GERBER,BOM,CPL}-curcur40-pmw3360.*
- Top Plates:       plates/pcb/jlcpcb/production_files/GERBER-plate-top-{left,right}.zip
"""
import os
import csv
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
    "J2": ("TRS", "PJ-398A-5A_PJ-399B-6A", "C128994"),
    "U3": ("TPD4E05U06DQAR", "USON-10_2.5x1.0mm_P0.5mm", "C138714"),
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
    "J1": ("TYPE-C-31-M-13C", "TYPE-C-31-M-13C", "C2848620"),
    "J3": ("SM06B-SRSS-TB(LF)(SN)", "JST_SH_SM06B-SRSS-TB_1x06-1MP_P1.00mm_Horizontal", "C160405"),
    "R4": ("27", "R_0402_1005Metric", "C2909343"),
    "R5": ("27", "R_0402_1005Metric", "C2909343"),
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


def get_part_info(ref, is_right=False, is_pmw=False):
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
                if ref == "rEXSW1":
                    return None
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


def export_main_pcb(pcb_path, proj_name, is_right=False, is_pmw=False):
    out_dir = os.path.join(os.path.dirname(pcb_path), "jlcpcb", "production_files")
    os.makedirs(out_dir, exist_ok=True)
    export_gerber_zip(pcb_path, os.path.join(out_dir, f"GERBER-{proj_name}.zip"))

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
        info = get_part_info(ref, is_right=is_right, is_pmw=is_pmw)
        if not info:
            continue
        comment, pkg, lcsc = info
        bom_groups.setdefault((comment, pkg, lcsc), []).append(ref)

        pos = fp.GetPosition()
        x_mm = round(pcbnew.ToMM(pos.x) - ox, 6)
        y_mm = round(oy - pcbnew.ToMM(pos.y), 6)
        krot = fp.GetOrientationDegrees()
        crot = round((180.0 - krot) % 360.0, 2)
        layer = "bottom" if fp.GetLayer() == pcbnew.B_Cu else "top"
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
    export_top_plates()
