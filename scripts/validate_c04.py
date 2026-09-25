from pathlib import Path
import sys,json,hashlib
from strict_prop import StrictPROP
from skn_layout import require_complete
R=Path(__file__).resolve().parents[1];sys.path.insert(0,r'C:/Users/etqdo/Documents/maya/LtMAO/src')
from LtMAO.pyRitoFile.bin import BIN,BINHasher
from LtMAO.pyRitoFile.skn import SKN
source=R/'work/candidate-c03/Briar.wad.client';stage=R/'work/candidate-c04/Briar.wad.client'
can=lambda o:json.loads(json.dumps(o,default=lambda x:x.__json__(),sort_keys=True))
get=lambda o,n:next(f for f in o.data if f.hash==BINHasher.raw_to_hex(n))
changed=[str(p.relative_to(stage)).replace('\\','/') for p in stage.rglob('*') if p.is_file() and p.read_bytes()!=(source/p.relative_to(stage)).read_bytes()]
assert sorted(changed)==sorted(['ASSETS/Characters/Briar/Skins/Base/Briar_Base.skn','f279b76afd0f0a62.bin'])
mp=stage/'ASSETS/Characters/Briar/Skins/Base/Briar_Base.skn';layout=require_complete(mp.read_bytes());old=SKN().read(str(source/mp.relative_to(stage)));new=SKN().read(str(mp))
assert old.indices==new.indices and can(old.submeshes)==can(new.submeshes)
sub=next(s for s in new.submeshes if s.name=='FrenzyDaggers');count=0
for i,(a,b) in enumerate(zip(old.vertices,new.vertices)):
 x,y=can(a),can(b)
 if i>=sub.vertex_start:
  assert x.pop('position')!=y.pop('position');count+=1
 assert x==y
bp=stage/'f279b76afd0f0a62.bin';strict=StrictPROP(bp.read_bytes()).run();a=BIN().read(str(source/bp.name));b=BIN().read(str(bp));entry='c1abf8a9'
assert a.links==b.links and len(a.entries)==len(b.entries)
for x,y in zip(a.entries,b.entries):
 if x.hash!=entry:assert can(x)==can(y)
x=next(e for e in a.entries if e.hash==entry);y=next(e for e in b.entries if e.hash==entry)
emkey=BINHasher.raw_to_hex('complexEmitterDefinitionData')
assert can([f for f in x.data if f.hash!=emkey])==can([f for f in y.data if f.hash!=emkey])
oldmain=next(e for e in get(x,'complexEmitterDefinitionData').data if get(e,'emitterName').data=='Missile')
em=get(y,'complexEmitterDefinitionData').data;assert len(em)==1;main=em[0]
changed_fields={BINHasher.raw_to_hex(n) for n in ['scale0','isRotationEnabled','isLocalOrientation']}
assert can([f for f in oldmain.data if f.hash not in changed_fields])==can([f for f in main.data if f.hash not in changed_fields])
assert get(main,'isLocalOrientation').data==0 and get(main,'isRotationEnabled').data==0
assert tuple(get(get(main,'scale0'),'constantValue').data)==(1,1,1)
assert get(get(get(main,'primitive'),'mMesh'),'mSimpleMeshName').data=='ASSETS/RedMistBriar/burger.scb'
report={'status':'OFFLINE PASS','only_changed_assets':changed,'modified_clarinet_positions':count,'all_body_vertices_indices_materials_weights_uvs_normals_unchanged':True,'textures_artwork_burger_mesh_unchanged':True,'SKN_layout':layout,'BIN_strict_sizes':strict,'R_projectile_emitter_count':1,'orientation':'World orientation, rotation disabled; authored bun is X/Z-horizontal and stack Y-up','scale':'constant, no squash','unchanged_other_BIN_entries':62,'main_timing_binding_position_texture_mesh_preserved':True,'runtime_limit':'Actual engine world orientation and R cleanup require gameplay feedback','model_sha256':hashlib.sha256(mp.read_bytes()).hexdigest(),'bin_sha256':hashlib.sha256(bp.read_bytes()).hexdigest()}
(R/'evidence/c04_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
