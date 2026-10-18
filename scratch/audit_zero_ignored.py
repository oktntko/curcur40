import json
import subprocess
import copy

def audit_board(name, pcb_path, pro_path):
    print(f"\n==========================================")
    print(f"AUDITING: {name}")
    print(f"==========================================")
    
    with open(pro_path, 'r', encoding='utf-8') as f:
        pro = json.load(f)
    
    # Save a temporary strict pro file where ALL rules are at least 'warning'
    strict_pro = copy.deepcopy(pro)
    severities = strict_pro.get('board', {}).get('design_settings', {}).get('rule_severities', {})
    for k in list(severities.keys()):
        if severities[k] == 'ignore':
            severities[k] = 'warning'
    
    temp_pro = pcb_path.replace('.kicad_pcb', '-audit.kicad_pro')
    temp_pcb = pcb_path.replace('.kicad_pcb', '-audit.kicad_pcb')
    with open(temp_pro, 'w', encoding='utf-8') as f:
        json.dump(strict_pro, f, indent=2, ensure_ascii=False)
    
    import shutil
    shutil.copy(pcb_path, temp_pcb)
    
    cmd = [
        r'C:\Users\oktnt\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe',
        'pcb', 'drc',
        '--severity-all',
        '--schematic-parity',
        '--format', 'json',
        '-o', f'scratch/{name}_full_audit.json',
        temp_pcb
    ]
    subprocess.run(cmd, check=True)
    
    import os
    os.remove(temp_pro)
    os.remove(temp_pcb)
    
    with open(f'scratch/{name}_full_audit.json', 'r', encoding='utf-8') as f:
        d = json.load(f)
    
    violations = d.get('violations', [])
    parity = d.get('schematic_parity', [])
    unconnected = d.get('unconnected_items', [])
    
    print(f"Unconnected items: {len(unconnected)}")
    print(f"Total DRC Violations: {len(violations)}")
    print(f"Total Schematic Parity Items: {len(parity)}")
    
    # Group by type
    v_by_type = {}
    for v in violations:
        t = v.get('type', 'unknown')
        v_by_type.setdefault(t, []).append(v)
    
    print("\n--- DRC Violations by Type ---")
    for t, v_list in sorted(v_by_type.items(), key=lambda x: -len(x[1])):
        print(f"  [{t}]: {len(v_list)} items")
    
    p_by_type = {}
    for p in parity:
        t = p.get('type', 'unknown')
        p_by_type.setdefault(t, []).append(p)
    
    print("\n--- Schematic Parity by Type ---")
    for t, p_list in sorted(p_by_type.items(), key=lambda x: -len(x[1])):
        print(f"  [{t}]: {len(p_list)} items")
    
    return v_by_type, p_by_type

audit_board('Left', 'pcbs/curcur40/left/curcur40-left.kicad_pcb', 'pcbs/curcur40/left/curcur40-left.kicad_pro')
audit_board('Right', 'pcbs/curcur40/right/curcur40-right.kicad_pcb', 'pcbs/curcur40/right/curcur40-right.kicad_pro')
audit_board('PMW3360', 'pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pcb', 'pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pro')
