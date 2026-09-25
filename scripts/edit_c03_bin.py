"""Change only R projectile core visuals; all other BIN entries remain identical."""
from pathlib import Path
import sys,json,copy,hashlib
R=Path(__file__).resolve().parents[1];sys.path.insert(0,r'C:/Users/etqdo/Documents/maya/LtMAO/src')
from LtMAO.pyRitoFile.bin import BIN,BINHasher,BINType
from LtMAO.pyRitoFile.structs import Vector
get=lambda obj,name:next(f for f in obj.data if f.hash==BINHasher.raw_to_hex(name))
canonical=lambda obj:json.loads(json.dumps(obj,default=lambda o:o.__json__(),sort_keys=True))
original=BIN().read(str(R/'work/original/f279b76afd0f0a62.bin'));b=copy.deepcopy(original)
entry=next(e for e in b.entries if e.hash=='c1abf8a9');emitters=get(entry,'complexEmitterDefinitionData')
assert get(entry,'particleName').data=='Briar_Base_R_Mis'
old_emit={get(e,'emitterName').data:canonical(e) for e in emitters.data}
main=next(e for e in emitters.data if get(e,'emitterName').data=='Missile')
get(get(get(main,'primitive'),'mMesh'),'mSimpleMeshName').data='ASSETS/RedMistBriar/burger.scb'
get(main,'texture').data='ASSETS/RedMistBriar/burger.tex'
get(get(main,'birthScale0'),'constantValue').data=Vector(1,1,1)
# Remove only crystal surface overlays, leaving missile timing/trails/ground cues intact.
removed=['Missile_Fresnel','Missile_Sheen1']
emitters.data=[e for e in emitters.data if get(e,'emitterName').data not in removed]
for e in emitters.data:
 name=get(e,'emitterName').data
 if name!='Missile':assert canonical(e)==old_emit[name],name
for old,new in zip(original.entries,b.entries):
 if old.hash!='c1abf8a9':assert canonical(old)==canonical(new),old.hash
target=R/'work/candidate-c03/Briar.wad.client/f279b76afd0f0a62.bin';b.write(str(target));rt=BIN().read(str(target))
assert canonical(b)==canonical(rt),'BIN semantic roundtrip changed values'
assert b.links==original.links and b.is_patch==original.is_patch and len(b.entries)==len(original.entries)
report={'status':'PASS','native_BIN':'f279b76afd0f0a62','changed_entry':'c1abf8a9 (Briar_Base_R_Mis)','changed_core_fields':['primitive.mMesh.mSimpleMeshName','texture','birthScale0.constantValue'],'removed_core_overlays':removed,'unchanged_other_R_emitters':len(emitters.data)-1,'all_other_BIN_entries_unchanged':len(b.entries)-1,'lifetime_rate_spawn_bind_rotation_scale_curve_preserved':True,'roundtrip_semantics':'PASS','output_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'note':'Burger local geometry center matches native scaled gem center; gameplay remains required for orientation/size/readability.'}
(R/'evidence/c03_bin_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
