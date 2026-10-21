import re
import os
import shutil
import uuid
from pathlib import Path

WORKSPACE = Path(r"c:\Users\oktnt\workspace\curcur40")
SCH_RIGHT_PATH = WORKSPACE / "pcbs" / "curcur40" / "right" / "curcur40-right.kicad_sch"
PCB_RIGHT_PATH = WORKSPACE / "pcbs" / "curcur40" / "right" / "curcur40-right.kicad_pcb"
SCH_PMW_PATH = WORKSPACE / "pcbs" / "curcur40" / "pmw3360" / "curcur40-pmw3360.kicad_sch"
BACKUP_DIR = WORKSPACE / "scratch" / "backup_before_sync"

def parse_blocks(b_text, tag):
    blocks = []
    idx = 0
    tag_prefix = f"({tag}"
    while True:
        pos = b_text.find(tag_prefix, idx)
        if pos == -1: break
        count, end = 0, pos
        while end < len(b_text):
            if b_text[end] == '(': count += 1
            elif b_text[end] == ')':
                count -= 1
                if count == 0: break
            end += 1
        blocks.append((pos, end+1, b_text[pos:end+1]))
        idx = end + 1
    return blocks

def sync_all():
    sch_right = (BACKUP_DIR / "curcur40-right.kicad_sch").read_text(encoding="utf-8")
    sch_pmw = SCH_PMW_PATH.read_text(encoding="utf-8")
    pcb_right = (BACKUP_DIR / "curcur40-right.kicad_pcb").read_text(encoding="utf-8")

    # 1. Add lib_symbols
    pos_lib = sch_pmw.find("(lib_symbols")
    c, end_lib = 0, pos_lib
    while end_lib < len(sch_pmw):
        if sch_pmw[end_lib] == '(': c += 1
        elif sch_pmw[end_lib] == ')':
            c -= 1
            if c == 0: break
        end_lib += 1
    pmw_lib_text = sch_pmw[pos_lib:end_lib+1]

    needed_syms = ["PMW3360_PCB:PMW3360DM-T2QU", "PMW3360_PCB:TLV74318PDBVR", "Jumper:SolderJumper_3_Open"]
    extracted_lib_syms = []
    for s_name in needed_syms:
        pos = pmw_lib_text.find(f'(symbol "{s_name}"')
        c, s_end = 0, pos
        while s_end < len(pmw_lib_text):
            if pmw_lib_text[s_end] == '(': c += 1
            elif pmw_lib_text[s_end] == ')':
                c -= 1
                if c == 0: break
            s_end += 1
        extracted_lib_syms.append(pmw_lib_text[pos:s_end+1])

    r_pos_lib = sch_right.find("(lib_symbols")
    c, r_end_lib = 0, r_pos_lib
    while r_end_lib < len(sch_right):
        if sch_right[r_end_lib] == '(': c += 1
        elif sch_right[r_end_lib] == ')':
            c -= 1
            if c == 0: break
        r_end_lib += 1

    insert_syms = []
    for s_name, s_def in zip(needed_syms, extracted_lib_syms):
        if f'(symbol "{s_name}"' not in sch_right:
            insert_syms.append("\t\t" + s_def.replace("\n", "\n\t\t"))

    if insert_syms:
        syms_text = "\n" + "\n".join(insert_syms) + "\n\t"
        sch_right = sch_right[:r_end_lib] + syms_text + sch_right[r_end_lib:]

    # 2. Remove rJ3, its wires, power symbols and old labels
    rj3_pos = sch_right.find('"rJ3"')
    if rj3_pos != -1:
        s_start = sch_right.rfind('(symbol', 0, rj3_pos)
        c, s_end = 0, s_start
        while s_end < len(sch_right):
            if sch_right[s_end] == '(': c += 1
            elif sch_right[s_end] == ')':
                c -= 1
                if c == 0: break
            s_end += 1
        sch_right = sch_right[:s_start] + sch_right[s_end+1:]

    for pwr_ref in ['"#PWR075"', '"#PWR0117"']:
        pos = sch_right.find(pwr_ref)
        if pos != -1:
            s_start = sch_right.rfind('(symbol', 0, pos)
            c, s_end = 0, s_start
            while s_end < len(sch_right):
                if sch_right[s_end] == '(': c += 1
                elif sch_right[s_end] == ')':
                    c -= 1
                    if c == 0: break
                s_end += 1
            sch_right = sch_right[:s_start] + sch_right[s_end+1:]

    wire_blocks = parse_blocks(sch_right, "wire")
    remove_spans = []
    for start, end, w in wire_blocks:
        pts = re.findall(r'\(xy\s+([\d\.\-]+)\s+([\d\.\-]+)\)', w)
        if pts:
            x1, y1 = float(pts[0][0]), float(pts[0][1])
            x2, y2 = float(pts[1][0]), float(pts[1][1])
            if 303 <= x1 <= 311 and 303 <= x2 <= 311 and 35 <= y1 <= 55 and 35 <= y2 <= 55:
                remove_spans.append((start, end))

    label_blocks = parse_blocks(sch_right, "label")
    for start, end, l in label_blocks:
        m_at = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', l)
        if m_at:
            x, y = float(m_at.group(1)), float(m_at.group(2))
            if 308 <= x <= 311 and 35 <= y <= 46:
                remove_spans.append((start, end))

    for start, end in sorted(remove_spans, key=lambda x: x[0], reverse=True):
        sch_right = sch_right[:start] + sch_right[end:]

    # 3. Helpers
    def shift_block(block_str, dx, dy):
        def at_sub(m):
            x = float(m.group(1)) + dx
            y = float(m.group(2)) + dy
            rest = m.group(3) if m.group(3) else ""
            return f"(at {x:.2f} {y:.2f}{rest})"
        res = re.sub(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)(\s+[\d\.\-]+)?\)', at_sub, block_str)

        def xy_sub(m):
            x = float(m.group(1)) + dx
            y = float(m.group(2)) + dy
            return f"(xy {x:.2f} {y:.2f})"
        res = re.sub(r'\(xy\s+([\d\.\-]+)\s+([\d\.\-]+)\)', xy_sub, res)
        return res

    def fix_instances(sym_str, ref_str):
        m_u = re.search(r'\(uuid\s+"([^"]+)"\)', sym_str)
        s_uuid = m_u.group(1) if m_u else str(uuid.uuid4())
        pos_inst = sym_str.find("(instances")
        if pos_inst == -1:
            return sym_str
        count, end_inst = 0, pos_inst
        while end_inst < len(sym_str):
            if sym_str[end_inst] == '(': count += 1
            elif sym_str[end_inst] == ')':
                count -= 1
                if count == 0: break
            end_inst += 1
        new_inst = f"""(instances
			(project "curcur40-right"
				(path "/{s_uuid}"
					(reference "{ref_str}")
					(unit 1)
				)
			)
		)"""
        return sym_str[:pos_inst] + new_inst + sym_str[end_inst+1:]

    # 4. Extract and transform PMW blocks
    pmw_body = sch_pmw[end_lib+1:]
    pmw_symbols = parse_blocks(pmw_body, "symbol")
    pmw_wires = parse_blocks(pmw_body, "wire")
    pmw_junctions = parse_blocks(pmw_body, "junction")
    pmw_noconnects = parse_blocks(pmw_body, "no_connect")

    dx1, dy1 = 170.0, 25.0
    dx2, dy2 = 265.0, 105.0

    new_symbols = []
    new_wires = []
    new_junctions = []
    new_labels = []
    new_noconnects = []

    for _, _, s in pmw_symbols:
        m_ref = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', s)
        ref = m_ref.group(1) if m_ref else ""
        if ref in ['U1', 'C1', 'C2', 'R3', 'R1', 'R2']:
            s_inst = fix_instances(s, ref)
            new_symbols.append(shift_block(s_inst, dx1, dy1))
        elif ref in ['U2', 'C3', 'C4', 'C5', 'R4']:
            s_inst = fix_instances(s, ref)
            new_symbols.append(shift_block(s_inst, dx2, dy2))
        elif ref == 'JP1':
            dx_jp, dy_jp = 241.49, 49.12
            s_inst = fix_instances(s, ref)
            new_symbols.append(shift_block(s_inst, dx_jp, dy_jp))

    for _, _, nc in pmw_noconnects:
        m_at = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', nc)
        if m_at:
            x = float(m_at.group(1))
            if 150 < x < 180:
                new_noconnects.append(shift_block(nc, dx1, dy1))

    # Wires: note condition for Block 2 is 40 <= x <= 105
    for _, _, w in pmw_wires:
        pts = re.findall(r'\(xy\s+([\d\.\-]+)\s+([\d\.\-]+)\)', w)
        if pts:
            x1, y1 = float(pts[0][0]), float(pts[0][1])
            x2, y2 = float(pts[1][0]), float(pts[1][1])
            if (130 <= x1 <= 205 and 130 <= x2 <= 205) and (45 <= y1 <= 95 and 45 <= y2 <= 95):
                new_wires.append(shift_block(w, dx1, dy1))
            elif (40 <= x1 <= 105 and 40 <= x2 <= 105) and (65 <= y1 <= 85 and 65 <= y2 <= 85):
                new_wires.append(shift_block(w, dx2, dy2))

    for _, _, j in pmw_junctions:
        m_at = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', j)
        if m_at:
            x, y = float(m_at.group(1)), float(m_at.group(2))
            if 130 <= x <= 205 and 45 <= y <= 95:
                new_junctions.append(shift_block(j, dx1, dy1))
            elif 40 <= x <= 105 and 65 <= y <= 85:
                new_junctions.append(shift_block(j, dx2, dy2))

    # Block 1 labels
    block1_labels = [
        ("SCLK", 201.93, 78.74),
        ("MOSI", 201.93, 76.20),
        ("MISO", 201.93, 73.66),
        ("NCS", 201.93, 81.28),
        ("RESET", 189.23, 66.04),
        ("MOTION", 189.23, 68.58),
        ("V_{IO}", 196.85, 49.53),
        ("V_{IO}", 151.13, 68.58),
        ("+1V8_PMW", 138.43, 64.77),
    ]

    for name, ox, oy in block1_labels:
        nx, ny = ox + dx1, oy + dy1
        new_labels.append(f"""\t(label "{name}"
		(at {nx:.2f} {ny:.2f} 0)
		(effects (font (size 1.27 1.27)) (justify left bottom))
		(uuid "{uuid.uuid4()}")
	)""")

    # Block 2 labels & power
    p3v3r_positions = [
        (41.91 + dx2, 69.85 + dy2), # (306.91, 174.85) connects to wire (306.91, 174.85) -> (314.53, 174.85)
        (385.00, 185.01),           # JP1 pin 1 power symbol
    ]
    # Wire connecting JP1 pin 1 (385.00, 182.47) to power symbol at (385.00, 185.01)
    new_wires.append(f"""\t(wire
		(pts
			(xy 385.00 182.47) (xy 385.00 185.01)
		)
		(stroke (width 0) (type default))
		(uuid "{uuid.uuid4()}")
	)""")

    # Wire connecting JP1 pin 2 (388.81, 177.39) to label V_{IO} at (391.16, 177.39)
    new_wires.append(f"""\t(wire
		(pts
			(xy 388.81 177.39) (xy 391.16 177.39)
		)
		(stroke (width 0) (type default))
		(uuid "{uuid.uuid4()}")
	)""")
    new_labels.append(f"""\t(label "V_{{IO}}"
		(at 391.16 177.39 0)
		(effects (font (size 1.27 1.27)) (justify left bottom))
		(uuid "{uuid.uuid4()}")
	)""")

    # Wire connecting JP1 pin 3 (385.00, 172.31) to label +1V8_PMW at (385.00, 169.77)
    new_wires.append(f"""\t(wire
		(pts
			(xy 385.00 172.31) (xy 385.00 169.77)
		)
		(stroke (width 0) (type default))
		(uuid "{uuid.uuid4()}")
	)""")
    new_labels.append(f"""\t(label "+1V8_PMW"
		(at 385.00 169.77 90)
		(effects (font (size 1.27 1.27)) (justify left bottom))
		(uuid "{uuid.uuid4()}")
	)""")

    # U2 output label (+1V8_PMW)
    new_labels.append(f"""\t(label "+1V8_PMW"
		(at {101.60 + dx2:.2f} {68.58 + dy2:.2f} 0)
		(effects (font (size 1.27 1.27)) (justify left bottom))
		(uuid "{uuid.uuid4()}")
	)""")

    gndr_positions = [
        (138.43 + dx1, 82.55 + dy1), # Block 1 caps
        (49.53 + dx2, 81.28 + dy2),  # C3
        (66.04 + dx2, 81.28 + dy2),  # U2
        (77.47 + dx2, 81.28 + dy2),  # C5
        (101.60 + dx2, 81.28 + dy2), # C4
    ]

    for px, py in p3v3r_positions:
        pwr_id = f"#PWR0{uuid.uuid4().hex[:4]}"
        new_symbols.append(f"""\t(symbol
		(lib_id "kbd:+3V3R")
		(at {px:.2f} {py:.2f} 270)
		(unit 1)
		(body_style 1)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(in_pos_files yes)
		(dnp no)
		(fields_autoplaced yes)
		(uuid "{uuid.uuid4()}")
		(property "Reference" "{pwr_id}"
			(at {px:.2f} {py+6.35:.2f} 0)
			(hide yes)
			(show_name no)
			(effects (font (size 1.27 1.27)))
		)
		(property "Value" "+3V3R"
			(at {px:.2f} {py+4.44:.2f} 0)
			(show_name no)
			(effects (font (size 1.27 1.27)))
		)
		(pin "1" (uuid "{uuid.uuid4()}"))
		(instances
			(project "curcur40-right"
				(path "/{uuid.uuid4()}"
					(reference "{pwr_id}")
					(unit 1)
				)
			)
		)
	)""")

    for gx, gy in gndr_positions:
        pwr_id = f"#PWR0{uuid.uuid4().hex[:4]}"
        new_symbols.append(f"""\t(symbol
		(lib_id "kbd:GNDR")
		(at {gx:.2f} {gy:.2f} 0)
		(unit 1)
		(body_style 1)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(in_pos_files yes)
		(dnp no)
		(fields_autoplaced yes)
		(uuid "{uuid.uuid4()}")
		(property "Reference" "{pwr_id}"
			(at {gx:.2f} {gy+6.35:.2f} 0)
			(hide yes)
			(show_name no)
			(effects (font (size 1.27 1.27)))
		)
		(property "Value" "GNDR"
			(at {gx:.2f} {gy+4.44:.2f} 0)
			(show_name no)
			(effects (font (size 1.27 1.27)))
		)
		(pin "1" (uuid "{uuid.uuid4()}"))
		(instances
			(project "curcur40-right"
				(path "/{uuid.uuid4()}"
					(reference "{pwr_id}")
					(unit 1)
				)
			)
		)
	)""")

    insert_block = "\n".join(new_symbols) + "\n" + "\n".join(new_wires) + "\n" + "\n".join(new_junctions) + "\n" + "\n".join(new_labels) + "\n" + "\n".join(new_noconnects) + "\n"
    pos_sheet_inst = sch_right.find("(sheet_instances")
    if pos_sheet_inst != -1:
        sch_right = sch_right[:pos_sheet_inst] + insert_block + "\n\t" + sch_right[pos_sheet_inst:]
    else:
        last_paren = sch_right.rfind(")")
        sch_right = sch_right[:last_paren] + insert_block + "\n)"

    SCH_RIGHT_PATH.write_text(sch_right, encoding="utf-8")
    print("Updated curcur40-right.kicad_sch")

    # 5. PCB updates
    for ref in ['U1', 'U2', 'JP1', 'R1', 'R2', 'R3', 'R4', 'C1', 'C2', 'C3', 'C4', 'C5']:
        pos = pcb_right.find(f'"{ref}"')
        f_start = pcb_right.rfind('(footprint', 0, pos)
        c, f_end = 0, f_start
        while f_end < len(pcb_right):
            if pcb_right[f_end] == '(': c += 1
            elif pcb_right[f_end] == ')':
                c -= 1
                if c == 0: break
            f_end += 1
        fp_text = pcb_right[f_start:f_end+1]
        fp_mod = fp_text.replace('(sheetfile "curcur40-pmw3360.kicad_sch")', '(sheetfile "curcur40-right.kicad_sch")')
        pcb_right = pcb_right[:f_start] + fp_mod + pcb_right[f_end+1:]

    # U1 pad 13 -> /NCS
    pos_u1 = pcb_right.find('"U1"')
    f_start = pcb_right.rfind('(footprint', 0, pos_u1)
    c, f_end = 0, f_start
    while f_end < len(pcb_right):
        if pcb_right[f_end] == '(': c += 1
        elif pcb_right[f_end] == ')':
            c -= 1
            if c == 0: break
        f_end += 1
    u1_fp = pcb_right[f_start:f_end+1]
    u1_fp_mod = re.sub(r'(\(pad\s+"13"[^\)]*?\(net\s+(?:\d+\s+)?)("(/CS|/NCS)")(\))', r'\1"/NCS"\4', u1_fp, flags=re.DOTALL)
    pcb_right = pcb_right[:f_start] + u1_fp_mod + pcb_right[f_end+1:]

    # U2 pins 1, 3 -> +3V3R
    pos_u2 = pcb_right.find('"U2"')
    f_start = pcb_right.rfind('(footprint', 0, pos_u2)
    c, f_end = 0, f_start
    while f_end < len(pcb_right):
        if pcb_right[f_end] == '(': c += 1
        elif pcb_right[f_end] == ')':
            c -= 1
            if c == 0: break
        f_end += 1
    u2_fp = pcb_right[f_start:f_end+1]
    u2_fp_mod = u2_fp.replace('(net "V_{IN}")', '(net "+3V3R")')
    pcb_right = pcb_right[:f_start] + u2_fp_mod + pcb_right[f_end+1:]

    # JP1 pin 1 -> +3V3R
    pos_jp1 = pcb_right.find('"JP1"')
    f_start = pcb_right.rfind('(footprint', 0, pos_jp1)
    c, f_end = 0, f_start
    while f_end < len(pcb_right):
        if pcb_right[f_end] == '(': c += 1
        elif pcb_right[f_end] == ')':
            c -= 1
            if c == 0: break
        f_end += 1
    jp1_fp = pcb_right[f_start:f_end+1]
    jp1_fp_mod = jp1_fp.replace('(net "V_{IN}")', '(net "+3V3R")')
    pcb_right = pcb_right[:f_start] + jp1_fp_mod + pcb_right[f_end+1:]

    # C3 pin 1 -> +3V3R
    pos_c3 = pcb_right.find('"C3"')
    f_start = pcb_right.rfind('(footprint', 0, pos_c3)
    c, f_end = 0, f_start
    while f_end < len(pcb_right):
        if pcb_right[f_end] == '(': c += 1
        elif pcb_right[f_end] == ')':
            c -= 1
            if c == 0: break
        f_end += 1
    c3_fp = pcb_right[f_start:f_end+1]
    c3_fp_mod = c3_fp.replace('(net "V_{IN}")', '(net "+3V3R")')
    pcb_right = pcb_right[:f_start] + c3_fp_mod + pcb_right[f_end+1:]

    pcb_right = re.sub(r'\t\(net\s+\d+\s+"(?:/CS|V_\{IN\})"\)\n?', '', pcb_right)
    PCB_RIGHT_PATH.write_text(pcb_right, encoding="utf-8")
    print("Updated curcur40-right.kicad_pcb")

if __name__ == "__main__":
    sync_all()
