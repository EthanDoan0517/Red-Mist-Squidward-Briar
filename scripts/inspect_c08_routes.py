from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,r'C:/Users/etqdo/Documents/maya/LtMAO/src')
from LtMAO.pyRitoFile.bin import BIN,BINHasher
names={}
for l in (R/'work/c03-tools/hashes.binfields.txt').read_text().splitlines():
 a=l.split(' ',1)
 if len(a)==2:names[a[0]]=a[1]
def friendly(o):
 if isinstance(o,list):return [friendly(x) for x in o]
 if isinstance(o,dict):return {k:(names.get(v,v) if k=='hash' and isinstance(v,str) else friendly(v)) for k,v in o.items()}
 return o
get=lambda o,h:next((f for f in o.data if f.hash==h),None)
mapping=json.loads((R/'evidence/original_animation_mapping.json').read_text());reverse={Path(v).stem:k for k,v in mapping.items()}
a=BIN().read(str(R/'work/candidate-c07/Briar.wad.client/DATA/Characters/Briar/Animations/Skin0.bin'));report=[]
for key,c in get(a.entries[0],'45e122f8').data.items():
 res=get(c,'b49f754e');fh=get(res,'0329f1d7').data if res and get(res,'0329f1d7') else None;name=reverse.get(fh,'')
 if 'laugh' in name or name.startswith('spell3'):
  report.append({'clip':name,'hash':key,'data':friendly(json.loads(json.dumps(c,default=lambda x:x.__json__())))})
out=R/'work/c08';out.mkdir(exist_ok=True);(out/'animation_routes.json').write_text(json.dumps(report,indent=2))
for x in report:print(x['clip'],x['hash'],[(v['hash'],v['data']) for v in x['data']['data'] if v['hash']!='mAnimationResourceData'])
