with open('pcbs/curcur40/left/curcur40-left.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

def remove_segment_by_uuid(content, u):
    target = f'uuid "{u}"'
    idx = content.find(target)
    if idx == -1:
        print(f"UUID {u} not found")
        return content
    start = content.rfind('\n\t(segment', 0, idx)
    end = content.find('\n\t)', idx)
    if start != -1 and end != -1:
        # include the trailing newline
        cut_end = end + len('\n\t)')
        if cut_end < len(content) and content[cut_end] == '\n':
            cut_end += 1
        print(f"Removed segment {u}")
        return content[:start] + content[cut_end:]
    return content

for u in ['7948b160-acc5-4b1d-9d8b-e5b1c2f6d66b', '0861c061-bd36-48be-8fe3-08e9fcb91427']:
    text = remove_segment_by_uuid(text, u)

with open('pcbs/curcur40/left/curcur40-left.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved left PCB successfully.")
