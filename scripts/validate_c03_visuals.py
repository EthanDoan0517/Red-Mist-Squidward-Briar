import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
R=Path(__file__).resolve().parents[1];sys.path.insert(0,r'C:/Users/etqdo/Documents/maya/LtMAO/src');sys.path.insert(0,str(R/'scripts'))
from LtMAO.pyRitoFile.skn import SKN
from LtMAO.pyRitoFile.skl import SKL
from LtMAO.pyRitoFile.anm import ANM
from LtMAO.pyRitoFile.so import SO
from LtMAO.pyRitoFile.structs import Vector as RV,Quaternion as RQ
from skn_layout import require_complete
VERSION=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'c03'
assert VERSION in ('c03','c04','c05','c06')
stage=R/f'work/candidate-{VERSION}/Briar.wad.client';path=stage/'ASSETS/Characters/Briar/Skins/Base/Briar_Base.skn';require_complete(path.read_bytes());m=SKN().read(str(path))
base=R/'References/Squidward Briar Maya/briar.wad.client/assets/Etdoan/Squidward-Briar';k=SKL().read(str(base/'briar_base.skl'))
def matrix(t,r,s):return Matrix.LocRotScale(Vector(tuple(t)),Quaternion((r.w,r.x,r.y,r.z)),Vector(tuple(s)))
inverse=[matrix(j.ibind_translate,j.ibind_rotate,j.ibind_scale) for j in k.joints]
def globals_for(local):
 out={}
 def get(i):
  if i not in out:out[i]=local[i] if k.joints[i].parent<0 else get(k.joints[i].parent)@local[i]
  return out[i]
 return [get(i) for i in range(len(local))]
def interpolate(track,frame,key,default):
 vals=[(t,getattr(p,key)) for t,p in sorted(track.poses.items()) if getattr(p,key) is not None]
 if not vals:return default
 left=next(((t,v) for t,v in reversed(vals) if t<=frame),vals[0]);right=next(((t,v) for t,v in vals if t>=frame),vals[-1])
 if left[0]==right[0]:return left[1]
 a=(frame-left[0])/(right[0]-left[0])
 if key=='rotate':
  x,y=left[1],right[1];q=Quaternion((x.w,x.x,x.y,x.z)).slerp(Quaternion((y.w,y.x,y.y,y.z)),a);return RQ(q.x,q.y,q.z,q.w)
 return RV(*(Vector(tuple(left[1])).lerp(Vector(tuple(right[1])),a)))
def deform(anm,frame):
 tracks={t.joint_hash:t for t in anm.tracks};local=[]
 for j in k.joints:
  tr=tracks.get(j.hash)
  local.append(matrix(*[interpolate(tr,frame,key,default) if tr else default for key,default in [('translate',j.local_translate),('rotate',j.local_rotate),('scale',j.local_scale)]]))
 mats=[g@iv for g,iv in zip(globals_for(local),inverse)]
 return [sum((mats[k.influences[i]]@Vector(tuple(v.position))*w for i,w in zip(v.influences,v.weights) if w),Vector()) for v in m.vertices]
assert [s.name for s in m.submeshes]==(['Body','FrenzyDaggers','RedMistFace'] if VERSION in ('c05','c06') else ['Body','FrenzyDaggers'])
assert all(abs(sum(v.weights)-1)<1e-5 and all(0<=i<len(k.influences) for i in v.influences) for v in m.vertices)
assert all(all(math.isfinite(x) for x in tuple(v.position)+tuple(v.normal)+tuple(v.uv)) for v in m.vertices)
bpy.ops.wm.open_mainfile(filepath=str(R/'work/redmist_candidate.blend'))
for obj in list(bpy.data.objects):
 if obj.type=='MESH':bpy.data.objects.remove(obj,do_unlink=True)
B=Matrix(((1,0,0),(0,0,-1),(0,1,0)))
mesh=bpy.data.meshes.new('C03');mesh.from_pydata([B@Vector(tuple(v.position)) for v in m.vertices],[],[m.indices[i:i+3] for i in range(0,len(m.indices),3)]);mesh.update()
obj=bpy.data.objects.new('SquidwardWithClarinets',mesh);bpy.context.collection.objects.link(obj)
uv=mesh.uv_layers.new()
for loop in mesh.loops:
 v=m.vertices[loop.vertex_index];uv.data[loop.index].uv=(v.uv.x,1-v.uv.y)
def material(name,texture):
 mat=bpy.data.materials.new(name);mat.use_nodes=True;node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=bpy.data.images.load(str(texture));p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.65;mat.node_tree.links.new(node.outputs['Color'],p.inputs['Base Color']);return mat
mesh.materials.append(material('Body',R/('evidence/c05_body_decoded.png' if VERSION in ('c05','c06') else 'evidence/encoded_atlas.png')));mesh.materials.append(material('Clarinets',R/'evidence/c03_0ea451e749d9d041_decoded.png'))
if VERSION in ('c05','c06'):mesh.materials.append(material('Face',R/'evidence/c05_face_palette.png'))
if VERSION=='c06':
 mat=mesh.materials[2];nodes=mat.node_tree.nodes;tex=next(n for n in nodes if n.type=='TEX_IMAGE');bsdf=nodes.get('Principled BSDF');mat.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Emission Color']);bsdf.inputs['Emission Strength'].default_value=1.5
 # Backface transparency reproduces the engine culling absent from C05 preview.
 geo=nodes.new('ShaderNodeNewGeometry');mix=nodes.new('ShaderNodeMixShader');transparent=nodes.new('ShaderNodeBsdfTransparent');output=nodes.get('Material Output');mat.node_tree.links.new(geo.outputs['Backfacing'],mix.inputs[0]);mat.node_tree.links.new(bsdf.outputs[0],mix.inputs[1]);mat.node_tree.links.new(transparent.outputs[0],mix.inputs[2]);mat.node_tree.links.new(mix.outputs[0],output.inputs['Surface'])
for polygon in mesh.polygons:
 polygon.material_index=next(i for i,s in enumerate(m.submeshes) if s.index_start<=polygon.index*3<s.index_start+s.index_count);polygon.use_smooth=True
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=20;scene.render.resolution_x=700;scene.render.resolution_y=760
report=[]
for name in ['idle_frenzy','attack1_frenzy','spell2_attack']:
 anm=ANM().read(str(base/'animations'/f'{name}.anm'));samples=[]
 for frac in [.2,.5,.8]:
  points=deform(anm,(anm.duration-1)*frac);assert all(all(math.isfinite(x) for x in p) for p in points)
  samples.append({'fraction':frac,'finite':True})
  if frac==.5:
   for v,p in zip(mesh.vertices,points):v.co=B@p
   mesh.update();lo=Vector(tuple(min(p[i] for p in points) for i in range(3)));hi=Vector(tuple(max(p[i] for p in points) for i in range(3)));center=B@((lo+hi)/2)
   cam=scene.camera;cam.location=center+Vector((230,-470,130));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=max(280,max(hi-lo)*1.35);scene.render.filepath=str(R/f'evidence/{VERSION}_{name}.png');bpy.ops.render.render(write_still=True)
   if VERSION in ('c05','c06') and name=='idle_frenzy':
    facepoints=[B@p for p in points[m.submeshes[2].vertex_start:]];fc=sum(facepoints,Vector())/len(facepoints);cam.location=fc+Vector((0,-350,35));cam.rotation_euler=(fc-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=52;scene.render.filepath=str(R/f'evidence/{VERSION}_face_closeup.png');bpy.ops.render.render(write_still=True)
 report.append({'animation':name,'samples':samples})
bpy.ops.wm.save_as_mainfile(filepath=str(R/f'work/{VERSION}-preview.blend'))
bpy.data.objects.remove(obj,do_unlink=True)
burger=SO().read_scb(str(stage/'ASSETS/RedMistBriar/burger.scb'))
me=bpy.data.meshes.new('Burger');me.from_pydata([B@Vector(tuple(v)) for v in burger.positions],[],[burger.indices[i:i+3] for i in range(0,len(burger.indices),3)]);me.update();o=bpy.data.objects.new('Burger',me);bpy.context.collection.objects.link(o);layer=me.uv_layers.new()
for li,loop in enumerate(me.loops):layer.data[li].uv=(burger.uvs[li].x,1-burger.uvs[li].y)
me.materials.append(material('BurgerAtlas',R/'evidence/c03_burger_decoded.png'))
for polygon in me.polygons:polygon.use_smooth=True
center=Vector((0,0,85.492525));cam=scene.camera;cam.location=center+Vector((130,-230,145));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=290 if VERSION in ('c05','c06') else 145;scene.render.resolution_x=700;scene.render.resolution_y=600;scene.render.filepath=str(R/f'evidence/{VERSION}_burger_preview.png');bpy.ops.render.render(write_still=True)
(R/f'evidence/{VERSION}_pose_validation.json').write_text(json.dumps({'status':'OFFLINE PASS; VISUAL REVIEW REQUIRED','model_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'weights_indices_uvs_normals_finite':True,'poses':report,'limitation':'Native animation samples and final decoded textures; game material/VFX visibility and R lifecycle require gameplay.'},indent=2))
