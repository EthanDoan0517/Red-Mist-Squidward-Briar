"""C06 isolated R spin and post-hit target artwork; C05 input immutable."""
from pathlib import Path
import sys,json,copy,hashlib
R=Path(__file__).resolve().parents[1]
sys.path[:0]=[r'C:/Users/etqdo/Documents/maya/LtMAO/src',str(R/'scripts')]
from LtMAO.pyRitoFile.bin import BIN,BINHasher,BINField,BINType
from LtMAO.pyRitoFile.structs import Vector as V
from strict_prop import StrictPROP
src=R/'work/candidate-c05/Briar.wad.client/f279b76afd0f0a62.bin'
out=R/'work/c06-r/Briar.wad.client/f279b76afd0f0a62.bin';out.parent.mkdir(parents=True,exist_ok=True)
b=BIN().read(str(src));before=copy.deepcopy(b)
get=lambda o,n:next(f for f in o.data if f.hash==BINHasher.raw_to_hex(n))
can=lambda o:json.loads(json.dumps(o,default=lambda v:v.__json__(),sort_keys=True))
entry=lambda h:next(e for e in b.entries if e.hash==h)
missile=get(entry('c1abf8a9'),'complexEmitterDefinitionData').data[0]
get(missile,'isRotationEnabled').data=1
rotation=get(missile,'rotation0');values=get(get(rotation,'dynamics'),'values');assert len(values.data)==1;values.data=[V(0,180,0)]
assert get(missile,'isLocalOrientation').data==0
changes=[]
for h,marker in [('6bbc8114','Marker4'),('c1544e01','Marker')]:
 e=entry(h);emits=get(e,'complexEmitterDefinitionData');oldnames=[get(em,'emitterName').data for em in emits.data]
 em=copy.deepcopy(next(em for em in emits.data if get(em,'emitterName').data==marker));old=copy.deepcopy(em)
 get(em,'emitterName').data='BoysWhoCry_Circle'
 get(em,'texture').data='ASSETS/RedMistBriar/boys_who_cry.tex'
 # Preserve native alpha blend, ground-quad orientation and target-size binding.
 assert get(em,'blendMode').data==1 and get(em,'isGroundLayer').data==1
 color=next((f for f in em.data if f.hash==BINHasher.raw_to_hex('birthColor')),None)
 if color is None:
  template=next(em for em in get(entry('6bbc8114'),'complexEmitterDefinitionData').data if get(em,'emitterName').data in ['Marker4','BoysWhoCry_Circle'])
  color=copy.deepcopy(get(template,'birthColor'));em.data.append(color)
 color.data=[BINField(hash=BINHasher.raw_to_hex('constantValue'),type=BINType.VEC4,data=V(1,1,1,1))]
 # Both quad dimensions equal; retains native gentle pulse and enemy-size scaling.
 get(get(em,'birthScale0'),'constantValue').data=V(125,125,1)
 emits.data=[em]
 mutable={BINHasher.raw_to_hex(n) for n in ['emitterName','texture','birthColor','birthScale0']}
 assert {f.hash:can(f) for f in old.data if f.hash not in mutable}=={f.hash:can(f) for f in em.data if f.hash not in mutable}
 changes.append({'entry':h,'particle':get(e,'particleName').data,'source_emitter':marker,'removed_emitters':oldnames,'remaining':'BoysWhoCry_Circle','native_lifetime_binding_orientation_preserved':True})
b.write(str(out));assert can(b)==can(BIN().read(str(out)))
allowed={'c1abf8a9','6bbc8114','c1544e01'}
assert all(can(a)==can(z) for a,z in zip(before.entries,b.entries) if a.hash not in allowed)
oldmis=get(next(e for e in before.entries if e.hash=='c1abf8a9'),'complexEmitterDefinitionData').data[0]
mut={BINHasher.raw_to_hex(n) for n in ['rotation0','isRotationEnabled']}
assert {f.hash:can(f) for f in oldmis.data if f.hash not in mut}=={f.hash:can(f) for f in missile.data if f.hash not in mut}
report={'status':'OFFLINE VALIDATED; runtime timing and target appearance unconfirmed','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'strict_BIN':StrictPROP(out.read_bytes()).run(),'changed_entries':sorted(allowed),'unchanged_entries':len(b.entries)-len(allowed),'burger_spin':{'axis':'Y (vertical)','degrees_per_second':180,'period_seconds':2,'mechanism':'existing IntegratedValueVector3 rotation0 single constant dynamics sample, isRotationEnabled=1','preserved':'world orientation, trajectory, spawn offset, lifetime, scale, burger mesh and texture'},'post_hit_target_circle':changes,'art_texture':'ASSETS/RedMistBriar/boys_who_cry.tex','art_tint':[1,1,1,1],'blend_mode':1,'preserved_other_R':'warning before arrival, arrival burst, impact, all other systems','schema_source':'https://wiki.divineskins.gg/en/docs/lol/vfx-bins/bin-dictionary','schema_provenance':'DAKA primary reverse-engineered engine registered class layout checked patch16.16; Units degrees/second, Y up, blend1 SRC_ALPHA/INV_SRC_ALPHA. Native birthRotation0 uses90 degrees and source rotation0 is already IntegratedValueVector3.'}
(R/'evidence/c06_r_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({'output':str(out),'entries_changed':3,'strict_BIN':report['strict_BIN'],'sha256':report['output_sha256']}))
