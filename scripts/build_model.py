"""Blender background: source rig adaptation to an unchanged native Briar skeleton."""
import bpy, sys, json, math
from pathlib import Path
from collections import defaultdict
from mathutils import Matrix, Vector, Quaternion
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,r'C:/Users/etqdo/Documents/maya/LtMAO/src')
from LtMAO.pyRitoFile.skn import SKN, SKNVertex, SKNSubmesh, SKNVertexType
from LtMAO.pyRitoFile.skl import SKL
from LtMAO.pyRitoFile.structs import Vector as RV
base=ROOT/'References/Squidward Briar Maya/briar.wad.client/assets/Etdoan/Squidward-Briar'
k=SKL().read(str(base/'briar_base.skl'))
joints={j.name:j for j in k.joints}
bind={}
for j in k.joints:
 q=j.ibind_rotate
 bind[j.name]=Matrix.LocRotScale(Vector(tuple(j.ibind_translate)),Quaternion((q.w,q.x,q.y,q.z)),Vector(tuple(j.ibind_scale))).inverted()
pos={n:m.translation for n,m in bind.items()}
inf={k.joints[idx].name:i for i,idx in enumerate(k.influences)}
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'References/spongebob-squarepants-squidward-model/source/Deltarune.blend'))
o=bpy.data.objects['SK_MP_Squidward.mo']; a=bpy.data.objects['Armature']
src={b.name:a.matrix_world@b.head_local for b in a.data.bones}
C=Matrix(((-1,0,0),(0,0,1),(0,-1,0)))
def globalfit(p):
 z=p.z
 anchors=[(0,0),(1.34,109.56),(1.596,119.104),(1.848,121.514),(2.097,128.008),(2.467,146.397),(2.606,154.03),(3.1,165.553),(4.63,211.45)]
 for (s0,t0),(s1,t1) in zip(anchors,anchors[1:]):
  if z<=s1: y=t0+(z-s0)*(t1-t0)/(s1-s0);break
 else:y=211.45+(z-4.63)*30
 return Vector((-p.x*32,y,-p.y*32+2))
def segment(p,s0,s1,t0,t1,width=32):
 d=s1-s0;e=t1-t0; u=d.normalized();v=e.normalized();q=(C@u).rotation_difference(v)
 t=(p-s0).dot(u)/d.length
 return t0+e*t+q@(C@((p-s0)-u*((p-s0).dot(u))))*width
def adapt(p,n):
 side=n[-1] if n.endswith(('_L','_R')) else None
 if n.startswith(('jt_','Nose','Head')):
  return pos['Head']+C@(p-src['Head_M'])*30,'Head'
 if n.startswith('Neck'):
  return segment(p,src['Neck1_M'],src['Head_M'],pos['Neck'],pos['Head'],30),'Neck'
 if side and n.startswith(('Scapula','Shoulder','Elbow','Wrist','MiddleFinger','WeaponAux')):
  if n.startswith('Scapula'): return globalfit(p),side+'_Clavicle'
  if n.startswith('Shoulder'):
   return segment(p,src['Shoulder_'+side],src['Elbow_'+side],pos[side+'_Shoulder'],pos[side+'_Elbow']),side+'_Shoulder'
  if n.startswith('Elbow'):
   return segment(p,src['Elbow_'+side],src['Wrist_'+side],pos[side+'_Elbow'],pos[side+'_Hand']),side+'_Elbow'
  direction=(pos[side+'_Hand']-pos[side+'_Elbow']).normalized();source=(C@(src['Wrist_'+side]-src['Elbow_'+side])).normalized();rot=source.rotation_difference(direction)
  return pos[side+'_Hand']+rot@(C@(p-src['Wrist_'+side]))*32,side+'_Hand'
 if side and n.startswith(('Hip','Knee','Ankle','Ball','Toes')):
  leg='1' if '1' in n else '2'; offset=Vector((0,0,4 if leg=='1' else -4))
  if n.startswith('Hip'): return segment(p,src['Hip'+leg+'_'+side],src['Knee'+leg+'_'+side],pos[side+'_Hip']+offset,pos[side+'_KneeLower']+offset),side+'_Hip'
  if n.startswith('Knee'):return segment(p,src['Knee'+leg+'_'+side],src['Ankle'+leg+'_'+side],pos[side+'_KneeLower']+offset,pos[side+'_Foot']+offset),side+'_KneeLower'
  return pos[side+'_Foot']+offset+C@(p-src['Ankle'+leg+'_'+side])*32,side+'_Foot'
 mapping={'Main':'Pelvis','Pelvis_M':'Pelvis','Spine1_M':'Spine1','Spine2_M':'Spine2','Spine3_M':'Spine2','Chest_M':'Spine2'}
 return globalfit(p),mapping.get(n,'Pelvis')
positions=[];weights=[];eyes=set();pupils=set()
for v in o.data.vertices:
 p=o.matrix_world@v.co; pp=Vector();ww=defaultdict(float);total=0
 for g in v.groups:
  if g.weight<1e-8:continue
  name=o.vertex_groups[g.group].name; pt,j=adapt(p,name);pp+=pt*g.weight;ww[j]+=g.weight;total+=g.weight
  if name.startswith('jt_Eye_') and g.weight>.2:eyes.add(v.index)
  if name.startswith('jt_Pupil_') and g.weight>.2:pupils.add(v.index)
 positions.append(pp/total if total else globalfit(p))
 ws=sorted(ww.items(),key=lambda x:-x[1])[:4];s=sum(w for _,w in ws);weights.append([(inf[n],w/s) for n,w in ws])
o.data.calc_loop_triangles();uv=o.data.uv_layers.active.data
verts=[];indices=[];lookup={};red_uv=(.165,.785);black_uv=(.925,.54)
for tri in o.data.loop_triangles:
 for li in reversed(tri.loops):
  vi=o.data.loops[li].vertex_index; t=tuple(uv[li].uv)
  if vi in eyes:t=red_uv
  if vi in pupils:t=black_uv
  key=(vi,t)
  if key not in lookup:
   lookup[key]=len(verts);ws=weights[vi];idx=[x[0] for x in ws]+[0]*(4-len(ws));w=[x[1] for x in ws]+[0]*(4-len(ws))
   verts.append(SKNVertex(RV(*positions[vi]),idx,w,RV(0,1,0),RV(t[0],1-t[1])))
  indices.append(lookup[key])
# Small native mesh blood trails attached rigidly to the unchanged Head joint.
for sign in [-1,1]:
 for offset,length in [(0,.36),(.075,.22)]:
  p0=Vector((sign*(.17+offset),-.53,3.48));p1=Vector((sign*(.19+offset),-.50,3.48-length));width=.023
  start=len(verts)
  for p in [p0+Vector((-width,0,0)),p0+Vector((width,0,0)),p1+Vector((width*.3,-.018,0)),p1+Vector((-width*.3,-.018,0))]:
   pt=pos['Head']+C@(p-src['Head_M'])*30
   verts.append(SKNVertex(RV(*pt),(inf['Head'],0,0,0),(1,0,0,0),RV(0,0,1),RV(red_uv[0],1-red_uv[1])))
  indices.extend([start,start+2,start+1,start,start+3,start+2])
# Recompute smooth normals on actual fitted/exported triangles.
norm=[Vector() for _ in verts]
for i in range(0,len(indices),3):
 ids=indices[i:i+3];p=[Vector(tuple(verts[j].position)) for j in ids];n=(p[1]-p[0]).cross(p[2]-p[0])
 for j in ids:norm[j]+=n
for v,n in zip(verts,norm):v.normal=RV(*(n.normalized() if n.length else Vector((0,1,0))))
s=SKN(version=4.1,flags=0,vertex_type=SKNVertexType.BASIC,vertex_size=52,vertices=verts,indices=indices,submeshes=[SKNSubmesh('Body',None,0,len(verts),0,len(indices))])
lo=Vector(tuple(min(tuple(v.position)[i] for v in verts) for i in range(3)));hi=Vector(tuple(max(tuple(v.position)[i] for v in verts) for i in range(3)));center=(lo+hi)/2
s.bounding_box=(RV(*lo),RV(*hi));s.bounding_sphere=(RV(*center),max((Vector(tuple(v.position))-center).length for v in verts))
# pyRitoFile omits the mandatory 12-byte v4 footer. Guard independently.
sys.path.insert(0,str(ROOT/'scripts'))
from skn_layout import require_complete
encoded=s.write(None,raw=True)+bytes(12)
require_complete(encoded)
(ROOT/'work/redmist_model.skn').write_bytes(encoded)
data={'vertices':len(verts),'triangles':len(indices)//3,'eye_vertices':len(eyes),'pupil_vertices':len(pupils),'bounds':[list(lo),list(hi)],'skeleton':'source bytes unchanged','submeshes':['Body'],'pillory':'no shackle/crystal/dagger/head-swap geometry exported','method':'source skin weights mapped to native Briar bind joints; four tentacle legs map to two native leg chains','red_uv':red_uv,'black_uv':black_uv}
(ROOT/'evidence/model_build.json').write_text(json.dumps(data,indent=2))
# Exported-mesh preview in Blender coordinates, with unmodified source atlas.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
B=Matrix(((1,0,0),(0,0,-1),(0,1,0)))
mesh=bpy.data.meshes.new('ExportedCandidate');mesh.from_pydata([B@Vector(tuple(v.position)) for v in verts],[],[indices[i:i+3] for i in range(0,len(indices),3)]);mesh.update()
obj=bpy.data.objects.new('RedMistSquidward',mesh);bpy.context.collection.objects.link(obj)
layer=mesh.uv_layers.new()
for loop in mesh.loops:
 v=verts[loop.vertex_index];layer.data[loop.index].uv=(v.uv.x,1-v.uv.y)
mat=bpy.data.materials.new('SourceAtlas');mat.use_nodes=True
tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'References/spongebob-squarepants-squidward-model/textures/T_MP_Squidward_D.001.png'));bsdf=mat.node_tree.nodes.get('Principled BSDF');mat.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color']);bsdf.inputs['Roughness'].default_value=.8;obj.data.materials.append(mat)
for p in mesh.polygons:p.use_smooth=True
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24
scene.world.color=(.3,.3,.3)
for loc,power,size in [((160,-240,320),1500000,200),((-150,-100,210),800000,170)]:
 bpy.ops.object.light_add(type='AREA',location=loc);light=bpy.context.object;light.data.energy=power;light.data.shape='DISK';light.data.size=size;light.rotation_euler=(Vector((0,0,120))-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(255,-470,265));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,112))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=260;scene.camera=cam
scene.render.resolution_x=800;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.filepath=str(ROOT/'evidence/model_preview.png');scene.view_settings.view_transform='Standard'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'work/redmist_candidate.blend'))
bpy.ops.render.render(write_still=True)
print('MODEL_BUILD',json.dumps(data))
