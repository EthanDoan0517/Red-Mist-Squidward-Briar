from pathlib import Path
for p in Path('work/original').glob('*.bin'):
 d=p.read_bytes()
 if b'Briar_Base_R_warning' in d and p.name!='f279b76afd0f0a62.bin':print(p.name)
