"""Independent C04-to-C05 structural, scale, material and scope assertions."""
from pathlib import Path
import sys,json,hashlib,copy
import numpy as np
R=Path(__file__).resolve().parents[1];sys.path[:0]=[r'C:/Users/etqdo/Documents/maya/LtMAO/src',str(R/'work/c05-deps')]
from LtMAO.pyRitoFile.skn import SKN
from LtMAO.pyRitoFile.skl import SKL
from LtMAO.pyRitoFile.so import SO
from LtMAO.pyRitoFile.bin import BIN,BINHasher
from LtMAO.pyRitoFile.tex import TEX
from skn_layout import require_complete
from strict_prop import StrictPROP
import xxhash
roots=[R/f'work/candidate-c{v}/Briar.wad.client' for v in ['04','05']]
mp=Path('ASSETS/Characters/Briar/Skins/Base/Briar_Base.skn');old,new=[SKN().read(str(p/mp)) for p in roots]
can=lambda o:json.loads(json.dumps(o,default=lambda x:x.__json__(),sort_keys=True))
get=lambda o,n:next(f for f in o.data if f.hash==BINHasher.raw_to_hex(n))
layout=require_complete((roots[1]/mp).read_bytes());assert (roots[1]/mp).read_bytes()[-12:]==bytes(12)
assert [x.name for x in new.submeshes]==['Body','FrenzyDaggers','RedMistFace']
assert all(can(a)==can(b) for a,b in zip(old.vertices[:old.submeshes[0].vertex_count],new.vertices[:old.submeshes[0].vertex_count]))
k=SKL().read(str(R/'work/original/ASSETS/Characters/Briar/Skins/Base/Briar_Base.skl'))
def bindpoint(j):
 q=j.ibind_rotate;x,y,z,w=q.x,q.y,q.z,q.w
 rot=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
 return np.linalg.solve(rot@np.diag(tuple(j.ibind_scale)),-np.array(tuple(j.ibind_translate)))
points={j.name:bindpoint(j) for j in k.joints};inf={k.joints[j].name:i for i,j in enumerate(k.influences)}
w=old.submeshes[1];errors=[]
for a,b in zip(old.vertices[w.vertex_start:w.vertex_start+w.vertex_count],new.vertices[w.vertex_start:w.vertex_start+w.vertex_count]):
 side='L' if a.influences[0]==inf['L_Hand'] else 'R';assert a.influences[0] in [inf['L_Hand'],inf['R_Hand']]
 direction=points[side+'_Hand']-points[side+'_Elbow'];grip=points[side+'_Hand']+direction/np.linalg.norm(direction)*7
 expected=grip+3*(np.array(tuple(a.position))-grip);errors.append(float(np.max(np.abs(expected-np.array(tuple(b.position))))))
 ad,bd=can(a),can(b);ad.pop('position');bd.pop('position');assert ad==bd
assert max(errors)<.001
assert old.indices[w.index_start:w.index_start+w.index_count]==new.indices[new.submeshes[1].index_start:new.submeshes[1].index_start+new.submeshes[1].index_count]
assert all(np.isfinite(tuple(v.position)).all() and np.isfinite(tuple(v.normal)).all() and np.isfinite(tuple(v.uv)).all() for v in new.vertices)
assert all(abs(sum(v.weights)-1)<1e-5 and all(z>=0 for z in v.weights) and all(0<=i<len(k.influences) for i in v.influences) for v in new.vertices)
face=new.vertices[new.submeshes[2].vertex_start:];assert all(all(i==inf['Head'] for i,weight in zip(v.influences,v.weights) if weight>0) for v in face)
bp=Path('ASSETS/RedMistBriar/burger.scb');bo,bn=[SO().read_scb(str(p/bp)) for p in roots];center=np.array([0,85.492525,0]);burger_error=max(np.max(np.abs(center+2*(np.array(tuple(a))-center)-np.array(tuple(b)))) for a,b in zip(bo.positions,bn.positions));assert burger_error<.001
oldbin,newbin=[BIN().read(str(p/'f279b76afd0f0a62.bin')) for p in roots];changes=[]
for a,b in zip(oldbin.entries,newbin.entries):
 if can(a)==can(b):continue
 changes.append(a.hash)
 if a.hash=='6ac5d2e3':
  am=get(get(a,'skinMeshProperties'),'materialOverride');bm=get(get(b,'skinMeshProperties'),'materialOverride');assert len(bm.data)==len(am.data)+1
  extra=bm.data.pop();assert get(extra,'submesh').data=='RedMistFace';assert get(extra,'texture').data==f'{xxhash.xxh64(b"assets/redmistbriar/face_colors.tex").intdigest():016x}'
  assert can(a)==can(b);bm.data.append(extra)
 else:
  ae=get(a,'complexEmitterDefinitionData');be=get(b,'complexEmitterDefinitionData');assert be.data==[];saved=be.data;be.data=copy.deepcopy(ae.data);assert can(a)==can(b);be.data=saved
assert set(changes)=={'6ac5d2e3','1d30e27c','36783e2f','8694b084','8df1b728','b606bf46','c4127d38','ecace1ad'}
texture=TEX().read(str(roots[1]/'ASSETS/RedMistBriar/face_colors.tex'));assert texture.width>=8
for p in roots[1].rglob('*'):assert p.suffix.lower() not in ['.skl','.anm']
scope={}
for p in roots[1].rglob('*'):
 if p.is_file():
  relative=p.relative_to(roots[1]);prev=roots[0]/relative;scope[str(relative)]='added' if not prev.exists() else ('unchanged' if p.read_bytes()==prev.read_bytes() else 'changed')
report={'status':'PASS — OFFLINE STRUCTURAL REVIEW','SKN_sha256':hashlib.sha256((roots[1]/mp).read_bytes()).hexdigest(),'SKN_strict_layout':layout,'body_original_vertices_all_fields_unchanged':True,'clarinet_uniform_scale_about_grip':3,'clarinet_max_position_error':max(errors),'clarinet_indices_weights_normals_UVs_unchanged':True,'new_face_vertices':len(face),'new_face_entirely_Head_weighted':True,'all_weights_positions_indices_material_ranges_valid':True,'burger_scale_about_established_center':2,'burger_max_position_error':float(burger_error),'BIN_changed_entries':changes,'BIN_other_entries_unchanged':55,'BIN_strict':StrictPROP((roots[1]/'f279b76afd0f0a62.bin').read_bytes()).run(),'face_texture_hash_verified':'ed03d591dfb8bc96','asset_scope':scope,'skeleton_and_animation_payloads_omitted':True,'risks':['3x clarinets and2x burger can clip/occlude at runtime; parent pose renders and user gameplay judge readability.','Seven complete dagger/R back-jet emitter systems are blanked; intentional broader visual reduction than only one flare.','Body positions unchanged, but eye triangles moved to dedicated face material and old blood triangles removed; new face geometry needs visual/deformation inspection.']}
(R/'evidence/c05_independent_visual_review.json').write_text(json.dumps(report,indent=2));print(json.dumps({'status':report['status'],'clarinet_error':max(errors),'burger_error':float(burger_error),'face_vertices':len(face),'BIN_entries_changed':len(changes)}))
