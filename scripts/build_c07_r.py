"""C07 screenshot-guided massive R warning artwork and small flower mark."""
from pathlib import Path
import sys,json,copy,hashlib
R=Path(__file__).resolve().parents[1];sys.path[:0]=[r'C:/Users/etqdo/Documents/maya/LtMAO/src',str(R/'scripts')]
from LtMAO.pyRitoFile.bin import BIN,BINHasher,BINField,BINType
from LtMAO.pyRitoFile.structs import Vector as V
from strict_prop import StrictPROP
src=R/'work/candidate-c06/Briar.wad.client/f279b76afd0f0a62.bin';out=R/'work/c07-r/Briar.wad.client/f279b76afd0f0a62.bin';out.parent.mkdir(parents=True,exist_ok=True)
b=BIN().read(str(src));before=copy.deepcopy(b)
h=BINHasher.raw_to_hex
get=lambda o,n:next(f for f in o.data if f.hash==h(n))
can=lambda o:json.loads(json.dumps(o,default=lambda x:x.__json__(),sort_keys=True))
entry=lambda key:next(e for e in b.entries if e.hash==key)
def put(o,name,typ,value,hash_type=None):
 f=next((f for f in o.data if f.hash==h(name)),None)
 if f is None:
  f=BINField(hash=h(name),type=typ,data=value);o.data.append(f)
 else:f.type=typ;f.data=value
 if hash_type is not None:f.hash_type=h(hash_type)
 return f
def value(o,name,typ,v,class_name):return put(o,name,BINType.EMBED,[BINField(hash=h('constantValue'),type=typ,data=v)],class_name)
def stable(em):
 # Source native ArbitraryQuad lies in XY; pitch90 rotates it into XZ.
 # UV +90 samples the source clockwise, making displayed art turn CCW90:
 # screenshot's floor-left becomes floor-bottom without target yaw inheritance.
 value(em,'birthRotation0',BINType.VEC3,V(90,0,0),'ValueVector3')
 value(em,'uvRotation',BINType.F32,90.,'ValueFloat')
 value(em,'birthRotationalVelocity0',BINType.VEC3,V(0,0,0),'ValueVector3')
 value(em,'rotation0',BINType.VEC3,V(0,0,0),'IntegratedValueVector3')
 for flag in ['isLocalOrientation','particleIsLocalOrientation','isDirectionOriented','hasPostRotateOrientation']:put(em,flag,BINType.FLAG,0)
 put(em,'isRotationEnabled',BINType.FLAG,1) # enables authored static plane rotation
 put(em,'isUniformScale',BINType.FLAG,1);put(em,'isGroundLayer',BINType.FLAG,1)
 put(em,'disableBackfaceCull',BINType.BOOL,True)
changes=[]
for key in ['6bbc8114','c1544e01']:
 e=entry(key);emits=get(e,'complexEmitterDefinitionData');assert len(emits.data)==1
 em=emits.data[0];get(em,'texture').data='ASSETS/RedMistBriar/red_flower.tex';get(em,'emitterName').data='RedFlower_Target'
 get(em,'blendMode').data=4 # native source-alpha additive glow; transparent source controls shape
 value(em,'birthColor',BINType.VEC4,V(1,1,1,1),'ValueColor');stable(em)
 changes.append({'entry':key,'system':get(e,'particleName').data,'emitter':'RedFlower_Target','lifetime_binding_scale_pulse':'unchanged from C06','blend':4})
e=entry('82249db2');emits=get(e,'complexEmitterDefinitionData');removed=[get(em,'emitterName').data for em in emits.data]
floor=copy.deepcopy(next(em for em in emits.data if get(em,'emitterName').data=='Blend_FLoor'))
get(floor,'texture').data='ASSETS/RedMistBriar/boys_who_cry.tex';get(floor,'emitterName').data='BoysWhoCry_LargeWarning'
value(floor,'birthColor',BINType.VEC4,V(1,1,1,.5),'ValueColor')
# Drop noise multiplication; neutralise only RGB of the existing start/end fade.
floor.data=[f for f in floor.data if f.hash not in {h('textureMult'),h('particleColorTexture')}]
color=get(floor,'Color');vals=get(get(color,'dynamics'),'values');vals.data=[V(1,1,1,v.w) for v in vals.data]
stable(floor)
# Uniform flag uses native X size; retain 500-unit base and native 0.775→1.55 pulse.
# Explicit equal dimensions also guards renderers that do not honour uniform flag.
base=get(get(floor,'birthScale0'),'constantValue');base.data=V(base.data.x,base.data.x,base.data.x)
scale=get(floor,'scale0')
for f in scale.data:
 if f.hash==h('constantValue'):f.data=V(f.data.x,f.data.x,f.data.x)
 elif f.hash==h('dynamics'):
  v=get(f,'values');v.data=[V(x.x,x.x,x.x) for x in v.data]
emits.data=[floor]
changes.append({'entry':'82249db2','system':'Briar_Base_R_warning','replaced_emitters':removed,'remaining':'BoysWhoCry_LargeWarning','base_scale':500,'peak_alpha':.5,'preserved':'rate, particleLifetime10sec, particleLinger1sec, lifetime9sec, host cleanup, bindWeight1, ground render pass, native uniform X scale curve and alpha fade'})
allowed={'82249db2','6bbc8114','c1544e01'}
assert all(can(a)==can(z) for a,z in zip(before.entries,b.entries) if a.hash not in allowed)
# Lifetime and bind contract remains byte-semantically equal per source emitter.
for key,newname,oldname in [('82249db2','BoysWhoCry_LargeWarning','Blend_FLoor'),('6bbc8114','RedFlower_Target','BoysWhoCry_Circle'),('c1544e01','RedFlower_Target','BoysWhoCry_Circle')]:
 oldentry=next(e for e in before.entries if e.hash==key)
 old=next(em for em in get(oldentry,'complexEmitterDefinitionData').data if get(em,'emitterName').data==oldname)
 new=get(entry(key),'complexEmitterDefinitionData').data[0]
 for n in ['rate','particleLifetime','particleLinger','lifetime','bindWeight','FlexShapeDefinition']:
  a=next((f for f in old.data if f.hash==h(n)),None);z=next((f for f in new.data if f.hash==h(n)),None);assert can(a)==can(z),(key,n)
b.write(str(out));assert can(b)==can(BIN().read(str(out)));strict=StrictPROP(out.read_bytes()).run()
report={'status':'OFFLINE VALIDATED; screenshot-guided mapping/orientation requires gameplay confirmation','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'strict_BIN':strict,'changed_entries':changes,'unchanged_entries':len(b.entries)-3,'mapping_evidence':'References/R hitting problem.png: Briar still travelling to marked dummy, large native edge surrounds target before arrival; R_warning owns edge meshes and ground floor. R_AoE arrival system remains unchanged.','orientation':'native ArbitraryQuad XY plane, birthRotation(90,0,0) to XZ; world emitter and particle orientation, no direction/post rotation, zero angular rates; UV+90 intended screen-CCW90 correction, floor-left to floor-bottom','color':'large artwork white tint alpha0.5 (native fades retained), small source-alpha additive red flower','preserved':'burger rotation, face shader/material, other particle systems, skeleton/animation/audio'}
(R/'evidence/c07_r_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({'output':str(out),'sha256':report['output_sha256'],'strict':strict,'changed_entries':3}))
