"""Focused C03 refinement: larger hand props and a clean, stable R burger."""
from pathlib import Path
import sys,json,hashlib,shutil,copy
from mathutils import Matrix,Vector,Quaternion
R=Path(__file__).resolve().parents[1];sys.path.insert(0,r'C:/Users/etqdo/Documents/maya/LtMAO/src');sys.path.insert(0,str(R/'scripts'))
from LtMAO.pyRitoFile.skn import SKN
from LtMAO.pyRitoFile.skl import SKL
from LtMAO.pyRitoFile.so import SO
from LtMAO.pyRitoFile.bin import BIN,BINHasher,BINField,BINType
from LtMAO.pyRitoFile.structs import Vector as V
from skn_layout import require_complete
source=R/'work/candidate-c03/Briar.wad.client';stage=R/'work/candidate-c04/Briar.wad.client'
assert not (R/'skin versions/RedMist-Squidward-Briar-C04.fantome').exists(),'Preserve delivered candidate'
shutil.copytree(source,stage,dirs_exist_ok=True)
canon=lambda o:json.loads(json.dumps(o,default=lambda x:x.__json__(),sort_keys=True))
path=stage/'ASSETS/Characters/Briar/Skins/Base/Briar_Base.skn';s=SKN().read(str(path));old=copy.deepcopy(s)
k=SKL().read(str(R/'References/Squidward Briar Maya/briar.wad.client/assets/Etdoan/Squidward-Briar/briar_base.skl'));bind={}
for j in k.joints:
 q=j.ibind_rotate;bind[j.name]=Matrix.LocRotScale(Vector(tuple(j.ibind_translate)),Quaternion((q.w,q.x,q.y,q.z)),Vector(tuple(j.ibind_scale))).inverted()
grips={}
for side in ['L','R']:
 hand=bind[side+'_Hand'].translation;elbow=bind[side+'_Elbow'].translation
 grips[k.influences.index(next(j.id for j in k.joints if j.name==side+'_Hand'))]=hand+(hand-elbow).normalized()*7
sub=next(x for x in s.submeshes if x.name=='FrenzyDaggers')
for v in s.vertices[sub.vertex_start:sub.vertex_start+sub.vertex_count]:
 assert v.weights==(1.,0.,0.,0.)
 grip=grips[v.influences[0]];v.position=V(*(grip+(Vector(tuple(v.position))-grip)*1.75))
assert canon(s.vertices[:sub.vertex_start])==canon(old.vertices[:sub.vertex_start]) and s.indices==old.indices
lo=Vector(tuple(min(tuple(v.position)[i] for v in s.vertices) for i in range(3)));hi=Vector(tuple(max(tuple(v.position)[i] for v in s.vertices) for i in range(3)));center=(lo+hi)/2
s.bounding_box=(V(*lo),V(*hi));s.bounding_sphere=(V(*center),max((Vector(tuple(v.position))-center).length for v in s.vertices))
encoded=s.write(None,raw=True)+bytes(12);require_complete(encoded);path.write_bytes(encoded)
# R entry only: retain exactly one burger emitter. No native trail/glow/smoke remains in flight.
get=lambda o,n:next(f for f in o.data if f.hash==BINHasher.raw_to_hex(n))
binpath=stage/'f279b76afd0f0a62.bin';b=BIN().read(str(binpath));previous=copy.deepcopy(b)
entry=next(e for e in b.entries if e.hash=='c1abf8a9');em=get(entry,'complexEmitterDefinitionData');main=next(e for e in em.data if get(e,'emitterName').data=='Missile')
removed=[get(e,'emitterName').data for e in em.data if e is not main];em.data=[main]
# Constant scale removes inherited gem squashing, keeping bun/layers stable.
get(main,'scale0').data=[BINField(hash=BINHasher.raw_to_hex('constantValue'),type=BINType.VEC3,data=V(1,1,1))]
# Keep the burger's authored Y-up stack parallel to world up instead of the
# native missile's local pitch/roll. Source SCB already has horizontal X/Z buns.
def setflag(name,value):
 h=BINHasher.raw_to_hex(name);field=next((f for f in main.data if f.hash==h),None)
 if field:field.data=int(value)
 else:main.data.append(BINField(hash=h,type=BINType.FLAG,data=int(value)))
setflag('isLocalOrientation',False)
setflag('isRotationEnabled',False)
for before,after in zip(previous.entries,b.entries):
 if before.hash!='c1abf8a9':assert canon(before)==canon(after)
b.write(str(binpath));assert canon(b)==canon(BIN().read(str(binpath)))
report={'status':'BUILT; OFFLINE VALIDATION PENDING','clarinet_uniform_scale':1.75,'grips_unchanged':True,'body_indices_weights_uv_normals_unchanged':True,'modified_clarinet_vertices':sub.vertex_count,'R_projectile_emitters_remaining':['Missile (burger)'],'R_projectile_emitters_removed_since_C03':removed,'R_scale':'constant (1,1,1), gem squash removed','R_orientation':'Y-up burger, X/Z-parallel buns; isLocalOrientation=false and isRotationEnabled=false; intended ground-upright appearance, inherited trajectory retained','other_BIN_entries_unchanged':62,'changed_assets':['Briar_Base.skn','f279b76afd0f0a62.bin'],'sha256':{str(p.relative_to(stage)):hashlib.sha256(p.read_bytes()).hexdigest() for p in stage.rglob('*') if p.is_file()}}
(R/'evidence/c04_build.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
