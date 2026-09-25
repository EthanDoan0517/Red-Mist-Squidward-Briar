"""Independent C06 geometry/material/texture scope review; no candidate edits."""
from pathlib import Path
import sys,json,hashlib,copy,struct
import numpy as np
R=Path(__file__).resolve().parents[1];sys.path[:0]=[r'C:/Users/etqdo/Documents/maya/LtMAO/src',str(R/'work/c05-deps')]
from LtMAO.pyRitoFile.skn import SKN
from LtMAO.pyRitoFile.skl import SKL
from LtMAO.pyRitoFile.bin import BIN,BINHasher,BINType
from LtMAO.pyRitoFile.tex import TEX
from skn_layout import require_complete
from strict_prop import StrictPROP
import xxhash
oldroot=R/'work/candidate-c05/Briar.wad.client';root=R/'work/candidate-c06/Briar.wad.client';mp=Path('ASSETS/Characters/Briar/Skins/Base/Briar_Base.skn')
a,b=[SKN().read(str(p/mp)) for p in [oldroot,root]];can=lambda o:json.loads(json.dumps(o,default=lambda x:x.__json__(),sort_keys=True))
get=lambda o,n:next(f for f in o.data if f.hash==BINHasher.raw_to_hex(n))
layout=require_complete((root/mp).read_bytes());assert (root/mp).read_bytes()[-12:]==bytes(12)
assert len(a.vertices)==len(b.vertices) and [s.name for s in a.submeshes]==[s.name for s in b.submeshes]
assert [can(v) for v in a.vertices[:a.submeshes[0].vertex_count]]==[can(v) for v in b.vertices[:b.submeshes[0].vertex_count]]
face=a.submeshes[2];expected=[];removed=0;reversed_count=0
for p in range(face.index_start,face.index_start+face.index_count,3):
 tri=a.indices[p:p+3];v=[a.vertices[i] for i in tri];x,y,z=[np.array(tuple(i.position)) for i in v];dot=np.dot(np.cross(y-x,z-x),np.array(tuple(v[0].normal)))
 if v[0].uv.x==.6875 or (v[0].uv.x==.0625 and dot<0):removed+=1;continue
 if dot<0:tri=[tri[0],tri[2],tri[1]];reversed_count+=1
 expected.extend(tri)
assert b.indices[:face.index_start]==a.indices[:face.index_start] and b.indices[face.index_start:]==expected
dots=[]
for p in range(face.index_start,len(b.indices),3):
 v=[b.vertices[i] for i in b.indices[p:p+3]];x,y,z=[np.array(tuple(i.position)) for i in v];dots.append(float(np.dot(np.cross(y-x,z-x),np.array(tuple(v[0].normal)))))
assert min(dots)>=-1e-7
face_moves=[]
for i in range(face.vertex_start,len(b.vertices)):
 av,bv=a.vertices[i],b.vertices[i];aa,bb=can(av),can(bv);aa.pop('position');bb.pop('position');assert aa==bb
 delta=np.array(tuple(bv.position))-np.array(tuple(av.position))
 if np.max(abs(delta))>1e-7:
  assert av.uv.x==.4375 and np.max(abs(delta-np.array([0,-1.2,.12])))<1e-4;face_moves.append(i)
assert len(face_moves)==66
k=SKL().read(str(R/'work/original/ASSETS/Characters/Briar/Skins/Base/Briar_Base.skl'))
def bindpoint(j):
 q=j.ibind_rotate;x,y,z,w=q.x,q.y,q.z,q.w;rot=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
 return np.linalg.solve(rot@np.diag(tuple(j.ibind_scale)),-np.array(tuple(j.ibind_translate)))
points={j.name:bindpoint(j) for j in k.joints};inf={k.joints[j].name:i for i,j in enumerate(k.influences)};w=a.submeshes[1];errors=[]
for av,bv in zip(a.vertices[w.vertex_start:w.vertex_start+w.vertex_count],b.vertices[w.vertex_start:w.vertex_start+w.vertex_count]):
 side='L' if av.influences[0]==inf['L_Hand'] else 'R';d=points[side+'_Hand']-points[side+'_Elbow'];grip=points[side+'_Hand']+d/np.linalg.norm(d)*7;errors.append(float(np.max(abs(grip+(np.array(tuple(av.position))-grip)*(2.5/3)-np.array(tuple(bv.position))))))
 aa,bb=can(av),can(bv);aa.pop('position');bb.pop('position');assert aa==bb
assert max(errors)<1e-4
assert all(np.isfinite(tuple(v.position)).all() and abs(sum(v.weights)-1)<1e-5 and all(0<=i<len(k.influences) for i in v.influences) for v in b.vertices)
burger=Path('ASSETS/RedMistBriar/burger.scb');assert (root/burger).read_bytes()==(oldroot/burger).read_bytes()
baseline=BIN().read(str(R/'work/c06-r/Briar.wad.client/f279b76afd0f0a62.bin'));out=BIN().read(str(root/'f279b76afd0f0a62.bin'));donor=BIN().read(str(R/'work/original/8c4d1d4c1b9fe68d.bin'));assert out.links==baseline.links
bm={e.hash:e for e in baseline.entries};om={e.hash:e for e in out.entries};assert set(om)-set(bm)=={'cef99b89'};assert [h for h in bm if can(bm[h])!=can(om[h])]==['6ac5d2e3']
skin=om['6ac5d2e3'];over=get(get(skin,'skinMeshProperties'),'materialOverride');faceover=next(x for x in over.data if get(x,'submesh').data=='RedMistFace');link=next(f for f in faceover.data if f.type==BINType.LINK);assert link.data=='cef99b89'
donorskin=next(e for e in donor.entries if e.type==BINHasher.raw_to_hex('SkinCharacterDataProperties'));native=get(get(donorskin,'skinMeshProperties'),'materialOverride');donorlink=next(f for entry in native.data for f in entry.data if f.type==BINType.LINK and f.data=='24ca9cfe');assert link.hash==donorlink.hash
faceover.data.remove(link);assert can(skin)==can(bm['6ac5d2e3']);faceover.data.append(link)
mat=om['cef99b89'];dm=next(e for e in donor.entries if e.hash=='24ca9cfe');allowed={BINHasher.raw_to_hex(n) for n in ['name','paramValues','samplerValues']};assert {f.hash:can(f) for f in mat.data if f.hash not in allowed}=={f.hash:can(f) for f in dm.data if f.hash not in allowed}
samplers={get(s,'TextureName').data:get(s,'texturePath').data for s in get(mat,'samplerValues').data};assert samplers=={'Diffuse_Texture':'ed03d591dfb8bc96','Mask_Texture':'a91a374647d853f0'}
params={get(p,'name').data:tuple(get(p,'value').data) for p in get(mat,'paramValues').data};assert params['Fresnel_Color']==(0,0,0,0) and params['Bloom_Intensity_R'][0]==2 and params['Bloom_Intensity_G'][0]==2.5
dp={get(p,'name').data:tuple(get(p,'value').data) for p in get(dm,'paramValues').data};assert params.keys()==dp.keys();mutable={'Fresnel_Color','Bloom_Color_R','Bloom_Intensity_R','Bloom_Color_G','Bloom_Intensity_G','albedoNewMin','albedoNewMax'};assert all(params[n]==dp[n] for n in dp if n not in mutable)
assert xxhash.xxh64(b'assets/redmistbriar/face_bloom_mask.tex').hexdigest()==samplers['Mask_Texture'] and xxhash.xxh64(b'assets/redmistbriar/face_colors.tex').hexdigest()==samplers['Diffuse_Texture']
def refs(value,typ):
 d=can(value);out=[]
 def walk(x):
  if isinstance(x,dict):
   if x.get('type')==typ:out.append(x['data'])
   for v in x.values():walk(v)
  elif isinstance(x,list):
   for v in x:walk(v)
 walk(d);return out
assert refs(mat,'LINK')==['720ce467']
texroot=R/'work/c06-textures/ASSETS/RedMistBriar';mask=TEX().read(str(texroot/'face_bloom_mask.tex'));assert (mask.width,mask.height,mask.format.name,mask.mipmaps)==(64,8,'BGRA8',False)
pixels=np.frombuffer(mask.data[0],dtype=np.uint8).reshape(8,64,4);assert len(mask.data[0])==64*8*4
for slot,rgba in enumerate([(0,0,0,255),(0,0,255,255),(0,0,255,255),(0,255,0,255),(0,0,0,255),(0,0,0,255),(0,0,0,255),(0,0,0,255)]):assert np.all(pixels[:,slot*8:(slot+1)*8,:]==rgba)
circle=TEX().read(str(texroot/'boys_who_cry.tex'));assert (circle.width,circle.height,circle.format.name,circle.mipmaps)==(1024,1024,'DXT5',True) and len(circle.data)==11
for i,payload in zip(reversed(range(11)),circle.data):assert len(payload)==max(1,((1024>>i)+3)//4)**2*16
texture_staged={p.name:(root/'ASSETS/RedMistBriar'/p.name).exists() and (root/'ASSETS/RedMistBriar'/p.name).read_bytes()==p.read_bytes() for p in texroot.glob('*.tex')}
report={'status':'OFFLINE STRUCTURAL PASS; global shader/bloom appearance requires gameplay','SKN_sha256':hashlib.sha256((root/mp).read_bytes()).hexdigest(),'SKN':layout,'original_body_vertices_and_indices_unchanged':True,'clarinet_scale_C05':2.5/3,'clarinet_scale_error':max(errors),'burger_mesh_unchanged_from_C05':True,'winding_reversed':reversed_count,'dark_center_triangles_removed':removed,'surviving_face_triangle_min_normal_dot':min(dots),'surviving_face_triangles_frontfacing_vs_vertex_normals':True,'white_center_vertices_shifted':len(face_moves),'C06_R_BIN_preserved_except_skin_material_override':True,'native_material_LINK_schema_matches_donor':True,'material_inherits_native_techniques_switches_macros_states':True,'material_dependency_links':['720ce467'],'donor_Skin20_assets_or_animation_links_not_added':True,'samplers':samplers,'mask_slots_verified':True,'circle_mips_verified':True,'texture_staging':texture_staged,'strict_BIN':StrictPROP((root/'f279b76afd0f0a62.bin').read_bytes()).run(),'risks':['Shader720ce467 remains the donor native global link; engine-global shader availability and bloom behavior not independently proven by these champion assets.','Donor material techniques/state switches remain native, including USE_RIM/INVERTED_FRESNEL; zero Fresnel_Color suppresses intended rim contribution but runtime behavior must be checked.','Corrected winding passes geometry/normal agreement; self-occlusion and glow intensity need runtime screenshots.']}
(R/'evidence/c06_independent_review.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:report[k] for k in ['status','winding_reversed','dark_center_triangles_removed','surviving_face_triangle_min_normal_dot','white_center_vertices_shifted','texture_staging']}))
