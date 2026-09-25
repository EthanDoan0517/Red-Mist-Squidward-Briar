"""C06: correct eye backfaces, native two-channel eye bloom, requested clarinet scale."""
from pathlib import Path
import sys,json,copy,shutil,math
import bpy
from mathutils import Matrix,Vector,Quaternion
R=Path(__file__).resolve().parents[1];sys.path[:0]=[r'C:/Users/etqdo/Documents/maya/LtMAO/src',str(R/'scripts')]
from LtMAO.pyRitoFile.bin import BIN,BINHasher,BINField,BINType
from LtMAO.pyRitoFile.skn import SKN
from LtMAO.pyRitoFile.skl import SKL
from LtMAO.pyRitoFile.structs import Vector as V
from skn_layout import require_complete
from strict_prop import StrictPROP
stage=R/'work/candidate-c06/Briar.wad.client';shutil.copytree(R/'work/candidate-c05/Briar.wad.client',stage,dirs_exist_ok=True)
shutil.copy2(R/'work/c06-r/Briar.wad.client/f279b76afd0f0a62.bin',stage/'f279b76afd0f0a62.bin')
path=stage/'ASSETS/Characters/Briar/Skins/Base/Briar_Base.skn';m=SKN().read(str(path));old=copy.deepcopy(m)
k=SKL().read(str(R/'References/Squidward Briar Maya/briar.wad.client/assets/Etdoan/Squidward-Briar/briar_base.skl'));bind={}
for j in k.joints:
 q=j.ibind_rotate;bind[j.name]=Matrix.LocRotScale(Vector(tuple(j.ibind_translate)),Quaternion((q.w,q.x,q.y,q.z)),Vector(tuple(j.ibind_scale))).inverted()
inf={k.joints[j].name:i for i,j in enumerate(k.influences)}
w=m.submeshes[1]
for v in m.vertices[w.vertex_start:w.vertex_start+w.vertex_count]:
 side='L' if v.influences[0]==inf['L_Hand'] else 'R';hand=bind[side+'_Hand'].translation;grip=hand+(hand-bind[side+'_Elbow'].translation).normalized()*7;v.position=V(*(grip+(Vector(tuple(v.position))-grip)*(2.5/3)))
face=m.submeshes[2];fixed=0;removed=0;indices=[]
for p in range(face.index_start,face.index_start+face.index_count,3):
 tri=m.indices[p:p+3];vs=[m.vertices[i] for i in tri];a,b,c=[Vector(tuple(v.position)) for v in vs];normal=(b-a).cross(c-a);dot=normal.dot(Vector(tuple(vs[0].normal)))
 # Remove dark iris/pupil overlays, leaving bright red and white centers.
 if vs[0].uv.x==.6875 or (vs[0].uv.x==.0625 and dot<0):removed+=1;continue
 if dot<0:tri=[tri[0],tri[2],tri[1]];fixed+=1
 indices.extend(tri)
m.indices=m.indices[:face.index_start]+indices;face.index_count=len(indices)
# Place the larger white highlight centrally; tiny original catchlights remain.
for i in range(face.vertex_start,len(m.vertices)-32):
 if m.vertices[i].uv.x==.4375 and (i==face.vertex_start or m.vertices[i-1].uv.x!=.4375):
  group=m.vertices[i:i+33];extent=max(v.position.y for v in group)-min(v.position.y for v in group)
  if extent>2:
   for v in group:v.position=V(v.position.x,v.position.y-1.2,v.position.z+.12)
lo=Vector(tuple(min(tuple(v.position)[i] for v in m.vertices) for i in range(3)));hi=Vector(tuple(max(tuple(v.position)[i] for v in m.vertices) for i in range(3)));mid=(lo+hi)/2
m.bounding_box=(V(*lo),V(*hi));m.bounding_sphere=(V(*mid),max((Vector(tuple(v.position))-mid).length for v in m.vertices))
data=m.write(None,raw=True)+bytes(12);path.write_bytes(data);require_complete(data)
get=lambda o,n:next(f for f in o.data if f.hash==BINHasher.raw_to_hex(n))
bpath=stage/'f279b76afd0f0a62.bin';b=BIN().read(str(bpath));donor=BIN().read(str(R/'work/original/8c4d1d4c1b9fe68d.bin'))
mat=copy.deepcopy(next(e for e in donor.entries if e.hash=='24ca9cfe'));name='Characters/Briar/Skins/Skin0/Materials/RedMistEyes';mat.hash=BINHasher.raw_to_hex(name);get(mat,'name').data=name
hashes=json.loads((R/'work/c06/texture_hashes.json').read_text())
for s in get(mat,'samplerValues').data:get(s,'texturePath').data=hashes['face_colors.tex' if get(s,'TextureName').data=='Diffuse_Texture' else 'face_bloom_mask.tex']
values={'Fresnel_Color':(0,0,0,0),'Bloom_Color_R':(254/255,78/255,74/255,1),'Bloom_Intensity_R':(2,0,0,0),'Bloom_Color_G':(1,1,1,1),'Bloom_Intensity_G':(2.5,0,0,0),'albedoNewMin':(0,0,0,0),'albedoNewMax':(1,0,0,0)}
for p in get(mat,'paramValues').data:
 n=get(p,'name').data
 if n in values:get(p,'value').data=V(*values[n])
skin=next(e for e in b.entries if e.hash=='6ac5d2e3');overrides=get(get(skin,'skinMeshProperties'),'materialOverride')
# Clone native LINK field schema from the donor's same skinned material override.
donorskin=next(e for e in donor.entries if e.type==BINHasher.raw_to_hex('SkinCharacterDataProperties'))
nativeoverrides=get(get(donorskin,'skinMeshProperties'),'materialOverride').data
template=next(x for x in nativeoverrides if any(f.type==BINType.LINK and f.data=='24ca9cfe' for f in x.data))
link=copy.deepcopy(next(f for f in template.data if f.type==BINType.LINK and f.data=='24ca9cfe'));link.data=mat.hash
override=next(x for x in overrides.data if get(x,'submesh').data=='RedMistFace');override.data.append(link);b.entries.append(mat);b.write(str(bpath));StrictPROP(bpath.read_bytes()).run()
assert len(BIN().read(str(bpath)).entries)==64
report={'status':'BUILT; OFFLINE REVIEW PENDING','source':'C05 plus isolated C06 R BIN','clarinet_scale_from_C04':2.5,'clarinet_scale_from_C05':2.5/3,'backfacing_triangles_reversed':fixed,'dark_eye_center_triangles_removed':removed,'cause':'C05 red,white,blood overlays had inward winding; Blender double-sided preview hid the defect','material':'Native Briar Skin20 Hair_Frenzy_Fresnel_Bloom_inst adapted for RedMistFace; R/G mask isolates red/white bloom; black sockets and blood mask zero','material_hash':mat.hash,'shader_link':'720ce467 (inherited native global shader)','body_unchanged':True,'SKN':require_complete(data),'strict_BIN':StrictPROP(bpath.read_bytes()).run()}
(R/'evidence/c06_visual_build.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
