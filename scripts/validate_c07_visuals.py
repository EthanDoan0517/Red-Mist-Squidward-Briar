"""Independent expected-value audit; no regeneration of unchanged model/poses."""
from pathlib import Path
import sys,json,hashlib,math
R=Path(__file__).resolve().parents[1];sys.path[:0]=[r'C:/Users/etqdo/Documents/maya/LtMAO/src',str(R/'scripts')]
from LtMAO.pyRitoFile.bin import BIN,BINHasher
from LtMAO.pyRitoFile.tex import TEX,TEXFormat
from strict_prop import StrictPROP
h=BINHasher.raw_to_hex;get=lambda o,n:next(f for f in o.data if f.hash==h(n));can=lambda o:json.loads(json.dumps(o,default=lambda x:x.__json__(),sort_keys=True))
src=R/'work/candidate-c06/Briar.wad.client/f279b76afd0f0a62.bin';dst=R/'work/c07-r/Briar.wad.client/f279b76afd0f0a62.bin';old=BIN().read(str(src));b=BIN().read(str(dst))
assert len(b.entries)==len(old.entries)==64
changed=[a.hash for a,z in zip(old.entries,b.entries) if can(a)!=can(z)];assert set(changed)=={'82249db2','6bbc8114','c1544e01'}
records=[]
for key in changed:
 e=next(e for e in b.entries if e.hash==key);ems=get(e,'complexEmitterDefinitionData').data;assert len(ems)==1;em=ems[0]
 assert tuple(get(get(em,'birthRotation0'),'constantValue').data)==(90,0,0)
 assert get(get(em,'uvRotation'),'constantValue').data==90
 for n in ['isLocalOrientation','particleIsLocalOrientation','isDirectionOriented','hasPostRotateOrientation']:assert get(em,n).data==0
 for n in ['rotation0','birthRotationalVelocity0']:assert tuple(get(get(em,n),'constantValue').data)==(0,0,0)
 assert get(em,'isGroundLayer').data==1 and get(em,'isUniformScale').data==1
 if key=='82249db2':
  assert get(em,'texture').data=='ASSETS/RedMistBriar/boys_who_cry.tex' and get(em,'blendMode').data==1
  assert tuple(get(get(em,'birthColor'),'constantValue').data)==(1,1,1,.5)
  fade=get(get(get(em,'Color'),'dynamics'),'values').data;assert max(v.w for v in fade)==1 and all(tuple(v)[:3]==(1,1,1) for v in fade)
  assert not any(f.hash in [h('textureMult'),h('particleColorTexture')] for f in em.data)
 else:assert get(em,'texture').data=='ASSETS/RedMistBriar/red_flower.tex' and get(em,'blendMode').data==4
 records.append({'system':get(e,'particleName').data,'texture':get(em,'texture').data,'orientation':'XZ ground; fixed UV90; no inherited yaw/spin'})
p=R/'work/c07-textures/Briar.wad.client/ASSETS/RedMistBriar/red_flower.tex';t=TEX().read(str(p));assert t.format==TEXFormat.DXT5 and t.width==t.height==512 and len(t.data)==10
for n,d in enumerate(reversed(t.data)):
 size=max(1,512>>n);assert len(d)==max(1,(size+3)//4)**2*16
report={'status':'OFFLINE PASS; runtime orientation/presentation pending','bin_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'strict':StrictPROP(dst.read_bytes()).run(),'changed_entries':changed,'unchanged_entries':61,'large_peak_opacity':.5,'flower':'512squareDXT5,10mips,additive','systems':records,'reuse':'C06 model,geometry,weights,eyes,props,body/HUD/othertextures unchanged; no repeat pose renders required','mapping':'User supplied screenshot R hitting problem.png identifies large warning during Briar approach'}
(R/'evidence/c07_independent_visual_validation.json').write_text(json.dumps(report,indent=2));print('PASS:3scoped entries,50%large alpha,stableground orientation,flower,61entries unchanged')
