"""Append supplied clarinets to C02 and export supplied burger as an R particle mesh."""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
R=Path(__file__).resolve().parents[1];sys.path.insert(0,r'C:/Users/etqdo/Documents/maya/LtMAO/src');sys.path.insert(0,str(R/'scripts'))
from LtMAO.pyRitoFile.skn import SKN,SKNVertex,SKNSubmesh
from LtMAO.pyRitoFile.skl import SKL
from LtMAO.pyRitoFile.so import SO,SOFlag
from LtMAO.pyRitoFile.structs import Vector as V
from skn_layout import require_complete
stage=R/'work/candidate-c03/Briar.wad.client';stage.mkdir(parents=True,exist_ok=True)
custom=stage/'ASSETS/RedMistBriar';custom.mkdir(parents=True,exist_ok=True)
base=R/'References/Squidward Briar Maya/briar.wad.client/assets/Etdoan/Squidward-Briar'
source=R/'work/candidate-c02/Briar.wad.client/ASSETS/Characters/Briar/Skins/Base/Briar_Base.skn'
raw=source.read_bytes();require_complete(raw);skin=SKN().read(raw,raw=True);original_v=len(skin.vertices);original_i=len(skin.indices)
k=SKL().read(str(base/'briar_base.skl'));bind={}
for j in k.joints:
 q=j.ibind_rotate;bind[j.name]=Matrix.LocRotScale(Vector(tuple(j.ibind_translate)),Quaternion((q.w,q.x,q.y,q.z)),Vector(tuple(j.ibind_scale))).inverted()
influence={k.joints[j].name:i for i,j in enumerate(k.influences)}
bpy.ops.wm.open_mainfile(filepath=str(R/'References/source/squidward_clarinet_final.blend'))
prop=bpy.data.objects['Clarinet'];mesh=prop.data;mesh.calc_loop_triangles();uv=mesh.uv_layers.active.data
for side in ['L','R']:
 hand=bind[side+'_Hand'].translation;elbow=bind[side+'_Elbow'].translation;grip=hand+(hand-elbow).normalized()*7
 lookup={}
 for tri in mesh.loop_triangles:
  if 'Outline' in mesh.materials[tri.material_index].name:continue
  for li in tri.loops:
   vi=mesh.loops[li].vertex_index;t=tuple(uv[li].uv);key=(vi,t)
   if key not in lookup:
    p=mesh.vertices[vi].co.copy();p.z+=1.5
    # Instrument longitudinal axis follows bind-world +Y; all motion follows Hand.
    pt=grip+Vector((p.x,p.z,-p.y))*8
    n=mesh.vertices[vi].normal;normal=Vector((n.x,n.z,-n.y)).normalized()
    lookup[key]=len(skin.vertices)
    skin.vertices.append(SKNVertex(V(*pt),(influence[side+'_Hand'],0,0,0),(1,0,0,0),V(*normal),V(t[0],1-t[1])))
   skin.indices.append(lookup[key])
skin.submeshes.append(SKNSubmesh('FrenzyDaggers',None,original_v,len(skin.vertices)-original_v,original_i,len(skin.indices)-original_i))
lo=Vector(tuple(min(tuple(v.position)[i] for v in skin.vertices) for i in range(3)));hi=Vector(tuple(max(tuple(v.position)[i] for v in skin.vertices) for i in range(3)));center=(lo+hi)/2
skin.bounding_box=(V(*lo),V(*hi));skin.bounding_sphere=(V(*center),max((Vector(tuple(v.position))-center).length for v in skin.vertices))
encoded=skin.write(None,raw=True)+bytes(12);require_complete(encoded);dest=stage/'ASSETS/Characters/Briar/Skins/Base/Briar_Base.skn';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(encoded)
# Prove existing body vertices and indices were untouched, irrespective of header changes.
before=SKN().read(raw,raw=True);after=SKN().read(encoded,raw=True)
canon=lambda x:json.dumps(x,default=lambda o:o.__json__(),sort_keys=True)
assert canon(before.vertices)==canon(after.vertices[:original_v]) and before.indices==after.indices[:original_i]
assert all(abs(sum(v.weights)-1)<1e-5 for v in after.vertices)
report={'body_vertices_preserved':original_v,'added_clarinet_vertices':len(skin.vertices)-original_v,'added_triangles':(len(skin.indices)-original_i)//3,'submeshes':[s.name for s in skin.submeshes],'clarinet_source':'References/source/squidward_clarinet_final.blend: Clarinet mesh only, duplicated once; outline hull omitted','joints':['L_Hand','R_Hand'],'visibility':'FrenzyDaggers native visibility; hidden initially, shown in frenzy (W and native R berserk)','SKN_sha256':hashlib.sha256(encoded).hexdigest()}
# Original burger meshes only; no replacement Squidward object is imported.
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(R/'References/krabby-patty/source/Krabby Patty.fbx'))
parts=sorted([o for o in bpy.data.objects if o.type=='MESH'],key=lambda o:o.name)
points=[o.matrix_world@v.co for o in parts for v in o.data.vertices];lo=Vector(tuple(min(p[i] for p in points) for i in range(3)));hi=Vector(tuple(max(p[i] for p in points) for i in range(3)));center=(lo+hi)/2
# Native missile gem reaches ~100 units wide after birthScale; aim 100-unit burger.
scale=100/max(hi.x-lo.x,hi.y-lo.y)
texnames=['bottombun','cheese','lettuce','onion','patty','pickle','sesameseeds','tomato','topbun']
def tile_for(name):
 n=name.lower().replace(' ','').replace('_','').replace('tomtato','tomato')
 return next(i for i,t in enumerate(texnames) if n.startswith(t))
positions=[];indices=[];uvs=[]
for o in parts:
 me=o.data;me.calc_loop_triangles();baseindex=len(positions);tile=tile_for(o.name);tx=tile%4;ty=tile//4
 # Preserve native core center: gem's bind center Y17.098505 * birthScale Y5.
 positions.extend(V((p.x-center.x)*scale,(p.z-center.z)*scale+85.492525,(p.y-center.y)*scale) for p in (o.matrix_world@v.co for v in me.vertices))
 for tri in me.loop_triangles:
  for li in reversed(tri.loops):
   vi=me.loops[li].vertex_index;uv0=me.uv_layers.active.data[li].uv
   indices.append(baseindex+vi)
   # Atlas cells have four pixels edge padding, preventing mip bleed.
   u=(tx*256+4+uv0.x*248)/1024;v=(ty*256+4+(1-uv0.y)*248)/1024
   uvs.append(V(u,v))
burger=SO(flags=SOFlag.HasLocalOriginLocatorAndPivot,positions=positions,indices=indices,uvs=uvs,central=V(0,0,0),material='RedMistBurger')
burger.write_scb(str(custom/'burger.scb'));loaded=SO().read_scb(str(custom/'burger.scb'))
assert len(loaded.positions)==len(positions) and loaded.indices==indices
assert all(0<=i<len(positions) for i in indices)
# Strict SCB layout: fixed header + vertex stream + central + per-face records.
expected=180+12*len(positions)+12+(len(indices)//3)*100
assert (custom/'burger.scb').stat().st_size==expected
(R/'work/c03-burger_mesh.json').write_text(json.dumps({'positions':[list(v) for v in positions],'indices':indices,'uvs':[list(v) for v in uvs]}))
report['burger']={'source_parts':[o.name for o in parts],'vertices':len(positions),'triangles':len(indices)//3,'width':100,'atlas_tiles':texnames,'SCB_bytes':expected,'SCB_roundtrip':'PASS'}
(R/'evidence/c03_props_build.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
