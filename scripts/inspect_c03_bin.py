import sys,json
from pathlib import Path
sys.path.insert(0,r'C:/Users/etqdo/Documents/maya/LtMAO/src')
from LtMAO.pyRitoFile.bin import BIN
R=Path.cwd();b=BIN().read(str(R/'work/original/f279b76afd0f0a62.bin'))
tables={p.name:dict(l.split(' ',1) for l in p.read_text().splitlines() if ' ' in l) for p in (R/'work/c03-tools').glob('*.txt')};b.un_hash(tables)
def enc(o):return o.__json__()
for e in b.entries:
 names=[f.data for f in e.data if isinstance(f.data,str)]
 if 'Briar_Base_R_Mis' in names:
  (R/'evidence/c03_r_missile.json').write_text(json.dumps(e,default=enc,indent=2));print('R_ENTRY',e.hash)
  emits=next(f for f in e.data if f.hash=='complexEmitterDefinitionData')
  for i,em in enumerate(emits.data):
   print(i,[(f.hash,f.data) for f in em.data if f.type.name in ['STRING','U8','FLAG','BOOL','I16']])
for e in b.entries:
 for f in e.data:
  if f.hash=='skinMeshProperties':
   (R/'evidence/c03_skinmesh.json').write_text(json.dumps(f,default=enc,indent=2));print('SKIN_ENTRY',e.hash)
try:
 import xxhash;print('XXHASH_AVAILABLE')
except:pass
