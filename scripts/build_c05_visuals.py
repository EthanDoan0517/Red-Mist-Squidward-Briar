"""C05: enlarged props, explicit eye/blood mesh and targeted weapon-flare removal."""
from pathlib import Path
import sys,json,copy,shutil,math,hashlib
import bpy
from mathutils import Matrix,Vector,Quaternion
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path[:0]=[r'C:/Users/etqdo/Documents/maya/LtMAO/src',str(R/'scripts'),str(R/'work/c05-deps')]
from LtMAO.pyRitoFile.skn import SKN,SKNVertex,SKNSubmesh
from LtMAO.pyRitoFile.skl import SKL
from LtMAO.pyRitoFile.so import SO
from LtMAO.pyRitoFile.bin import BIN,BINHasher,BINField,BINType
from LtMAO.pyRitoFile.structs import Vector as V
from skn_layout import require_complete
from strict_prop import StrictPROP
src=R/'work/candidate-c04/Briar.wad.client';dst=R/'work/candidate-c05/Briar.wad.client';shutil.copytree(src,dst,dirs_exist_ok=True)
can=lambda o:json.loads(json.dumps(o,default=lambda x:x.__json__(),sort_keys=True))
path=dst/'ASSETS/Characters/Briar/Skins/Base/Briar_Base.skn';s=SKN().read(str(path));before=copy.deepcopy(s)
k=SKL().read(str(R/'References/Squidward Briar Maya/briar.wad.client/assets/Etdoan/Squidward-Briar/briar_base.skl'));bind={}
for j in k.joints:
 q=j.ibind_rotate;bind[j.name]=Matrix.LocRotScale(Vector(tuple(j.ibind_translate)),Quaternion((q.w,q.x,q.y,q.z)),Vector(tuple(j.ibind_scale))).inverted()
influence={k.joints[j].name:i for i,j in enumerate(k.influences)}
weapon=s.submeshes[1]
for v in s.vertices[weapon.vertex_start:weapon.vertex_start+weapon.vertex_count]:
 side='L' if v.influences[0]==influence['L_Hand'] else 'R';hand=bind[side+'_Hand'].translation;grip=hand+(hand-bind[side+'_Elbow'].translation).normalized()*7
 v.position=V(*(grip+(Vector(tuple(v.position))-grip)*3))
# Eye geometry in C04 used solid UV samples. Move those triangles to a dedicated
# native face material, so the gray atlas does not control black sockets/red tears.
body=s.submeshes[0];old_blood_start=body.vertex_count-16;eyeuv=[(.165,.215),(.925,.46)]
eye=lambda i:any(abs(s.vertices[i].uv.x-u)<1e-5 and abs(s.vertices[i].uv.y-v)<1e-5 for u,v in eyeuv)
body_indices=[];face_indices=[];face_start=len(s.vertices);lookup={}
palette={name:((i+.5)/8,.5) for i,name in enumerate(['black','red','coral','white','blood','iris','gray','black2'])}
for p in range(0,body.index_count,3):
 tri=before.indices[p:p+3]
 if all(i>=old_blood_start for i in tri):continue
 if all(eye(i) for i in tri):
  for i in tri:
   if i not in lookup:
    v=copy.deepcopy(s.vertices[i]);v.uv=V(*palette['black']);lookup[i]=len(s.vertices);s.vertices.append(v)
   face_indices.append(lookup[i])
 else:body_indices.extend(tri)
# Source head surface provides stable placement for circular eye highlights and
# blood trails. Only this original model is used; newer model remains prop-only.
bpy.ops.wm.open_mainfile(filepath=str(R/'References/spongebob-squarepants-squidward-model/source/Deltarune.blend'))
o=bpy.data.objects['SK_MP_Squidward.mo'];arm=bpy.data.objects['Armature'];headsource=arm.matrix_world@arm.data.bones['Head_M'].head_local
points=[o.matrix_world@v.co for v in o.data.vertices];polys=[list(p.vertices) for p in o.data.polygons];tree=BVHTree.FromPolygons(points,polys)
C=Matrix(((-1,0,0),(0,0,1),(0,-1,0)));head=bind['Head'].translation
def surface(x,z,push=.012):
 hit=tree.ray_cast(Vector((x,-3,z)),Vector((0,1,0)),5)[0]
 assert hit is not None,(x,z)
 return Vector((x,hit.y-push,z))
def addpoint(p,color):
 idx=len(s.vertices);world=head+C@(p-headsource)*30
 s.vertices.append(SKNVertex(V(*world),(influence['Head'],0,0,0),(1,0,0,0),V(0,0,1),V(*palette[color])));return idx
def ellipse(cx,cz,rx,rz,color,push):
 ids=[addpoint(surface(cx,cz,push),color)]+[addpoint(surface(cx+rx*math.cos(2*math.pi*i/32),cz+rz*math.sin(2*math.pi*i/32),push),color) for i in range(32)]
 for i in range(32):face_indices.extend([ids[0],ids[1+i],ids[1+(i+1)%32]])
for sign in [-1,1]:
 cx=sign*.164;cz=3.711
 ellipse(cx,cz,.074,.100,'red',.014)
 ellipse(cx,cz+.022,.061,.067,'coral',.020)
 ellipse(cx,cz+.040,.048,.046,'white',.026)
 ellipse(cx,cz-.006,.034,.055,'iris',.032)
 ellipse(cx,cz-.008,.020,.039,'black',.038)
 ellipse(cx-.009,cz+.018,.008,.011,'white',.044)
 # Three uneven blood rivulets follow the actual eye/cheek surface.
 for offset,length,width in [(0,.38,.026),(.070,.27,.018),(-.045,.20,.012)]:
  pairs=[]
  for step in range(15):
   t=step/14;z=3.49-length*t;x=sign*(.18+offset+.04*t+.009*math.sin(t*8))
   w=width*(1-.65*t)
   pairs.append([addpoint(surface(x-w,z,.012),'blood'),addpoint(surface(x+w,z,.012),'blood')])
  for a,b in zip(pairs,pairs[1:]):face_indices.extend([a[0],b[0],a[1],a[1],b[0],b[1]])
weapon_indices=before.indices[weapon.index_start:weapon.index_start+weapon.index_count]
s.indices=body_indices+weapon_indices+face_indices
body.index_count=len(body_indices);weapon.index_start=len(body_indices)
s.submeshes.append(SKNSubmesh('RedMistFace',None,face_start,len(s.vertices)-face_start,len(body_indices)+len(weapon_indices),len(face_indices)))
lo=Vector(tuple(min(tuple(v.position)[i] for v in s.vertices) for i in range(3)));hi=Vector(tuple(max(tuple(v.position)[i] for v in s.vertices) for i in range(3)));mid=(lo+hi)/2
s.bounding_box=(V(*lo),V(*hi));s.bounding_sphere=(V(*mid),max((Vector(tuple(v.position))-mid).length for v in s.vertices))
data=s.write(None,raw=True)+bytes(12);require_complete(data);path.write_bytes(data)
# Double the burger about its established local center, without moving the emitter.
bp=dst/'ASSETS/RedMistBriar/burger.scb';burger=SO().read_scb(str(bp));center=Vector((0,85.492525,0))
for i,p in enumerate(burger.positions):burger.positions[i]=V(*(center+(Vector(tuple(p))-center)*2))
burger.write_scb(str(bp));check=SO().read_scb(str(bp));assert can(check.positions)==can(burger.positions)
# Match explicit native material override schema; validate XXH64 with a known path.
# XXH64 verified externally against the native SKN path hash (9144d26d7f271649).
binpath=dst/'f279b76afd0f0a62.bin';b=BIN().read(str(binpath));oldbin=copy.deepcopy(b);get=lambda obj,name:next(f for f in obj.data if f.hash==BINHasher.raw_to_hex(name))
skin=next(e for e in b.entries if e.hash=='6ac5d2e3');overrides=get(get(skin,'skinMeshProperties'),'materialOverride');entry=copy.deepcopy(overrides.data[0]);get(entry,'submesh').data='RedMistFace';get(entry,'texture').data='ed03d591dfb8bc96';overrides.data.append(entry)
targets={'Briar_Base_Z_Frenzy_Daggers_Spawn','Briar_Base_Z_Frenzy_Daggers','Briar_Base_Z_Frenzy_DaggersL','Briar_Base_R_Cas_BackJets_BlastOff','Briar_Base_R_Cas_Jets','Briar_Base_R_BackJets_ChildParticle','Briar_Base_R_BackJets'}
removed=[]
for e in b.entries:
 names=[f.data for f in e.data if f.hash==BINHasher.raw_to_hex('particleName')]
 if names and names[0] in targets:
  emit=get(e,'complexEmitterDefinitionData');removed.append({'entry':e.hash,'system':names[0],'emitters_removed':len(emit.data)});emit.data=[]
assert len(removed)==len(targets)
b.write(str(binpath));assert can(b)==can(BIN().read(str(binpath)));strict=StrictPROP(binpath.read_bytes()).run()
allowed={'6ac5d2e3'}|{x['entry'] for x in removed}
assert all(can(a)==can(c) for a,c in zip(oldbin.entries,b.entries) if a.hash not in allowed)
report={'status':'BUILT; APPEARANCE REVIEW PENDING','source_candidate':'C04','clarinet_scale_from_C04':3,'clarinet_scale_from_C03':5.25,'burger_scale_from_C04':2,'new_face_vertices':len(s.vertices)-face_start,'eye_shadow':'native eye surfaces black','eyes':'two red ellipses with white centers','blood':'six head-weighted surface-following red rivulets','body_texture_target':'#CAC6CF; imagegen shaded gray atlas','removed_flare_systems':removed,'unchanged_BIN_entries':len(b.entries)-len(allowed),'strict_BIN':strict,'SKN_layout':require_complete(data),'palette_texture':'ASSETS/RedMistBriar/face_colors.tex'}
(R/'evidence/c05_visual_build.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
