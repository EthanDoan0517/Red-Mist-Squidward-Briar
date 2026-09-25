"""Independent strict PROP byte walk plus narrowly scoped semantic comparison."""
import struct,json,sys,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
from strict_prop import StrictPROP
sys.path.insert(0,r'C:/Users/etqdo/Documents/maya/LtMAO/src')
from LtMAO.pyRitoFile.bin import BIN,BINHasher
can=lambda v:json.loads(json.dumps(v,default=lambda o:o.__json__(),sort_keys=True))
get=lambda o,n:next(f for f in o.data if f.hash==BINHasher.raw_to_hex(n))
paths=[R/'work/original/f279b76afd0f0a62.bin',R/'work/candidate-c03/Briar.wad.client/f279b76afd0f0a62.bin']
strict=[StrictPROP(p.read_bytes()).run() for p in paths]
old,new=[BIN().read(str(p)) for p in paths]
assert old.links==new.links and old.version==new.version and old.is_patch==new.is_patch
o={e.hash:e for e in old.entries};n={e.hash:e for e in new.entries};assert o.keys()==n.keys()
changed=[h for h in o if can(o[h])!=can(n[h])];assert changed==['c1abf8a9']
assert [(x.hash,can(x)) for x in o[changed[0]].data if x.hash!=BINHasher.raw_to_hex('complexEmitterDefinitionData')]==[(x.hash,can(x)) for x in n[changed[0]].data if x.hash!=BINHasher.raw_to_hex('complexEmitterDefinitionData')]
old_e={get(e,'emitterName').data:e for e in get(o[changed[0]],'complexEmitterDefinitionData').data}
new_e={get(e,'emitterName').data:e for e in get(n[changed[0]],'complexEmitterDefinitionData').data}
removed=sorted(set(old_e)-set(new_e));assert removed==['Missile_Fresnel','Missile_Sheen1']
assert all(can(v)==can(old_e[k]) for k,v in new_e.items() if k!='Missile')
def diff(a,b,path=''):
 if type(a)!=type(b):return [path]
 if isinstance(a,dict):return sum((diff(a[k],b[k],path+'/'+k) for k in a),[]) if a.keys()==b.keys() else [path]
 if isinstance(a,list):return sum((diff(x,y,path+'/'+str(i)) for i,(x,y) in enumerate(zip(a,b))),[]) if len(a)==len(b) else [path]
 return [] if a==b else [path]
field_diffs=[]
for a,b in zip(old_e['Missile'].data,new_e['Missile'].data):
 if can(a)!=can(b):field_diffs.append({'field_hash':a.hash,'changed_paths':diff(can(a),can(b))})
allowed={BINHasher.raw_to_hex(s) for s in ['primitive','texture','birthScale0']};assert {d['field_hash'] for d in field_diffs}==allowed
assert get(get(get(new_e['Missile'],'primitive'),'mMesh'),'mSimpleMeshName').data=='ASSETS/RedMistBriar/burger.scb'
assert get(new_e['Missile'],'texture').data=='ASSETS/RedMistBriar/burger.tex'
assert tuple(get(get(new_e['Missile'],'birthScale0'),'constantValue').data)==(1.,1.,1.)
animation=BIN().read(str(R/'work/original/DATA/Characters/Briar/Animations/Skin0.bin'))
maps=json.loads((R/'evidence/original_animation_mapping.json').read_text());reverse={Path(v).stem:k for k,v in maps.items()}
f=lambda obj,h:next((z for z in obj.data if z.hash==h),None)
clips=f(animation.entries[0],'45e122f8').data
visibility=[]
for ch,clip in clips.items():
 events=f(clip,'f598463e');resource=f(clip,'b49f754e')
 if not events:continue
 for event_hash,event in events.data.items():
  if '8ae1ae3e' in json.dumps(can(event)):
   file=f(resource,'0329f1d7').data if resource else None
   visibility.append({'clip_hash':ch,'animation_file_hash':file,'animation_name':reverse.get(file),'event_hash':event_hash,'event':can(event)})
report={'status':'PASS','original_strict_walk':strict[0],'candidate_strict_walk':strict[1],'candidate_sha256':hashlib.sha256(paths[1].read_bytes()).hexdigest(),'unchanged_entry_count':len(o)-1,'only_changed_entry':changed,'removed_emitters':removed,'unchanged_R_emitters':len(new_e)-1,'core_field_diffs':field_diffs,'native_frenzydaggers_visibility_events':visibility,'limitations':'Offline byte/semantic inspection and native event inheritance; gameplay visibility timing and VFX appearance still require user test.'}
report['native_visibility_interpretation']={'6d4d42d0':'mShowSubmeshList (verified FNV1a name hash)','bb41a45b':'mHideSubmeshList (verified FNV1a name hash)','confirmed':'FrenzyDaggers hidden initially in native skin definition; graph explicitly shows during spell2_attack (W recast) and spell3_windup_frenzy (E while frenzy).','not_proven_by_graph_alone':'Initial W activation and R berserk visibility may be controlled by native gameplay scripts. Preserving submesh name inherits native behavior but exact W/R appearance must be gameplay-tested.'}
(R/'evidence/c03_independent_review.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
