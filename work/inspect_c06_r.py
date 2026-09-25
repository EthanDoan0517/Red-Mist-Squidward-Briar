import sys,json
from pathlib import Path
sys.path.insert(0,r'C:/Users/etqdo/Documents/maya/LtMAO/src')
from LtMAO.pyRitoFile.bin import BIN
R=Path.cwd(); b=BIN().read(str(R/'work/candidate-c05/Briar.wad.client/f279b76afd0f0a62.bin'));tables={p.name:dict(l.split(' ',1) for l in p.read_text().splitlines() if ' ' in l) for p in (R/'work/c03-tools').glob('*.txt')};b.un_hash(tables)
out=[]
for e in b.entries:
 names=[f.data for f in e.data if f.hash=='particleName']
 if names and '_R_' in names[0]:
  out.append(e)
  print(e.hash,names[0],[(f.data) for em in next(f.data for f in e.data if f.hash=='complexEmitterDefinitionData') for f in em.data if f.hash=='emitterName'])
(R/'evidence/c06_R_native_inspect.json').write_text(json.dumps(out,default=lambda o:o.__json__(),indent=2))
