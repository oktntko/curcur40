with open('pcbs/curcur40/left/curcur40-left.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. 65f1e2cd-90da-4f7c-a910-9d559ae83bf1
old_seg1 = '''(segment
		(start -6.5425 38.62)
		(end -24.762 38.62)
		(width 0.4)
		(layer "F.Cu")
		(net "+5V")
		(uuid "65f1e2cd-90da-4f7c-a910-9d559ae83bf1")
	)'''

new_seg1 = '''(segment
		(start -6.5425 38.54625)
		(end -24.762 38.62)
		(width 0.4)
		(layer "F.Cu")
		(net "+5V")
		(uuid "65f1e2cd-90da-4f7c-a910-9d559ae83bf1")
	)'''

# 2. c8a9f606-30ad-4058-8bb4-353dffd90861
old_seg2 = '''(segment
		(start -24.832 30.596)
		(end -6.5425 30.596)
		(width 0.4)
		(layer "F.Cu")
		(net "+5V")
		(uuid "c8a9f606-30ad-4058-8bb4-353dffd90861")
	)'''

new_seg2 = '''(segment
		(start -24.832 30.596)
		(end -6.5425 30.74625)
		(width 0.4)
		(layer "F.Cu")
		(net "+5V")
		(uuid "c8a9f606-30ad-4058-8bb4-353dffd90861")
	)'''

# 3. 7948b160-acc5-4b1d-9d8b-e5b1c2f6d66b
old_seg3 = '''(segment
		(start -39.235992 41.23995)
		(end -39.9125 41.23995)
		(width 0.2032)
		(layer "F.Cu")
		(net "+5V")
		(uuid "7948b160-acc5-4b1d-9d8b-e5b1c2f6d66b")
	)'''

# Wait, let's see where 7948b160 connects.
# In scratch/inspect_endpoints.py:
# Track +5V len 13.2585: start -25.9775, 41.2400 end -39.2360, 41.2400
# Track +5V len 7.0015: start -39.2409, 41.2350 end -46.2424, 41.2350
# Track +5V len 0.0070: start -39.2360, 41.2400 end -39.2409, 41.2350
# Track +5V len 0.6765: start -39.2360, 41.2400 end -39.9125, 41.2400 -> wait!
# Why is there a 0.6765mm segment from -39.2360 to -39.9125?
# Let's check what C6 pin 1 is connected to!

assert old_seg1 in text, "old_seg1 not in text"
assert old_seg2 in text, "old_seg2 not in text"

text = text.replace(old_seg1, new_seg1)
text = text.replace(old_seg2, new_seg2)

with open('pcbs/curcur40/left/curcur40-left.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(text)

print("Replaced seg1 and seg2 successfully.")
