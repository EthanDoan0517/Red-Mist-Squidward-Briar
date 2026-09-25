from pathlib import Path
import sys,json,collections
R=Path(__file__).resolve().parents[1];sys.path.insert(0,r'C:/Users/etqdo/Documents/maya/LtMAO/src')
from LtMAO.pyRitoFile.bin import BIN,BINHasher
from LtMAO.pyRitoFile.skn import SKN
names={}
for f in ['hashes.binfields.txt','hashes.bintypes.txt']:
 for l in (R/'work/c03-tools'/f).read_text().splitlines():
  a=l.split(' ',1)
  if len(a)==2:names[a[0]]=a[1]
def friendly(o):
 if isinstance(o,list):return [friendly(x) for x in o]
 if isinstance(o,dict):return {k:(names.get(v,v) if k in ['hash','type'] and isinstance(v,str) else friendly(v)) for k,v in o.items()}
 return o
b=BIN().read(str(R/'work/candidate-c05/Briar.wad.client/f279b76afd0f0a62.bin'))
entry=next(e for e in b.entries if e.hash=='6ac5d2e3')
(R/'work/c06/skin.json').write_text(json.dumps(friendly(json.loads(json.dumps(entry,default=lambda o:o.__json__()))),indent=2))
# Polygon winding vs exported vertex normals. Blender defaults to rendering both sides.
m=SKN().read(str(R/'work/candidate-c05/Briar.wad.client/ASSETS/Characters/Briar/Skins/Base/Briar_Base.skn'));s=m.submeshes[2];counts=collections.Counter()
for p in range(s.index_start,s.index_start+s.index_count,3):
 vs=[m.vertices[i] for i in m.indices[p:p+3]];a,b,c=[list(v.position) for v in vs];u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)];n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];dot=sum(n[i]*list(vs[0].normal)[i] for i in range(3));counts[(round(vs[0].uv.x,4),'back' if dot<0 else 'front')]+=1
print(dict(counts))
