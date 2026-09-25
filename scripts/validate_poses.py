import bpy, sys, json, math, hashlib
from pathlib import Path
from mathutils import Matrix, Vector, Quaternion
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,r'C:/Users/etqdo/Documents/maya/LtMAO/src')
from LtMAO.pyRitoFile.skn import SKN
from LtMAO.pyRitoFile.skl import SKL
from LtMAO.pyRitoFile.anm import ANM
m=SKN().read(str(ROOT/'work/redmist_model.skn'))
base=ROOT/'References/Squidward Briar Maya/briar.wad.client/assets/Etdoan/Squidward-Briar'
k=SKL().read(str(base/'briar_base.skl'))
def matrix(t,r,s):return Matrix.LocRotScale(Vector(tuple(t)),Quaternion((r.w,r.x,r.y,r.z)),Vector(tuple(s)))
inverse=[matrix(j.ibind_translate,j.ibind_rotate,j.ibind_scale) for j in k.joints]
def globals_for(local):
 out={}
 def get(i):
  if i not in out:out[i]=local[i] if k.joints[i].parent<0 else get(k.joints[i].parent)@local[i]
  return out[i]
 return [get(i) for i in range(len(local))]
bind=globals_for([matrix(j.local_translate,j.local_rotate,j.local_scale) for j in k.joints])
identity_error=max(abs((g@iv)[i][j]-(i==j)) for g,iv in zip(bind,inverse) for i in range(4) for j in range(4))
finite=lambda xyz:all(math.isfinite(x) for x in xyz)
checks={
 'finite_positions':all(finite(v.position) for v in m.vertices),
 'finite_uvs':all(finite(v.uv) for v in m.vertices),
 'finite_normals':all(finite(v.normal) for v in m.vertices),
 'normal_length_max_error':max(abs(Vector(tuple(v.normal)).length-1) for v in m.vertices),
 'weight_sum_max_error':max(abs(sum(v.weights)-1) for v in m.vertices),
 'weights_nonnegative':all(w>=0 for v in m.vertices for w in v.weights),
 'influence_indices_valid':all(0<=i<len(k.influences) for v in m.vertices for i in v.influences),
 'triangle_indices_valid':len(m.indices)%3==0 and all(0<=i<len(m.vertices) for i in m.indices),
 'body_only':len(m.submeshes)==1 and m.submeshes[0].name=='Body',
 'native_bind_inverse_max_error':identity_error,
}
assert all(checks[n] for n in ['finite_positions','finite_uvs','finite_normals','weights_nonnegative','influence_indices_valid','triangle_indices_valid','body_only'])
assert checks['weight_sum_max_error']<1e-5
assert identity_error<.01  # Original Riot local/inverse data differs by 0.00334 world units.
def interpolate(track,frame,key,default):
 vals=[(t,getattr(p,key)) for t,p in sorted(track.poses.items()) if getattr(p,key) is not None]
 if not vals:return default
 left=next(((t,v) for t,v in reversed(vals) if t<=frame),vals[0]);right=next(((t,v) for t,v in vals if t>=frame),vals[-1])
 if left[0]==right[0]:return left[1]
 a=(frame-left[0])/(right[0]-left[0])
 if key=='rotate':
  x,y=left[1],right[1];q=Quaternion((x.w,x.x,x.y,x.z)).slerp(Quaternion((y.w,y.x,y.y,y.z)),a)
  from LtMAO.pyRitoFile.structs import Quaternion as Q
  return Q(q.x,q.y,q.z,q.w)
 from LtMAO.pyRitoFile.structs import Vector as V
 return V(*(Vector(tuple(left[1])).lerp(Vector(tuple(right[1])),a)))
def deform(anm,frame):
 tracks={t.joint_hash:t for t in anm.tracks};local=[]
 for j in k.joints:
  tr=tracks.get(j.hash)
  if tr:local.append(matrix(*[interpolate(tr,frame,key,default) for key,default in [('translate',j.local_translate),('rotate',j.local_rotate),('scale',j.local_scale)]]))
  else:local.append(matrix(j.local_translate,j.local_rotate,j.local_scale))
 mats=[g@iv for g,iv in zip(globals_for(local),inverse)]
 return [sum((mats[k.influences[i]]@Vector(tuple(v.position))*w for i,w in zip(v.influences,v.weights) if w),Vector()) for v in m.vertices]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'work/redmist_candidate.blend'))
obj=bpy.data.objects['RedMistSquidward'];scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=12;scene.render.resolution_x=420;scene.render.resolution_y=480
B=Matrix(((1,0,0),(0,0,-1),(0,1,0)))
poses=[]
for name in ['idle1_sway','run1','attack1','spell3_windup','spell4_cast_in']:
 anm=ANM().read(str(base/'animations'/f'{name}.anm'))
 samples=[]
 for fraction in [.2,.5,.8]:
  f=(anm.duration-1)*fraction;p=deform(anm,f)
  assert all(finite(v) for v in p)
  lo=[min(v[i] for v in p) for i in range(3)];hi=[max(v[i] for v in p) for i in range(3)]
  samples.append({'frame':f,'finite':True,'bounds':[lo,hi]})
  if fraction==.5:
   for v,point in zip(obj.data.vertices,p):v.co=B@point
   obj.data.update();center=B@Vector([(x+y)/2 for x,y in zip(lo,hi)])
   cam=scene.camera;cam.location=center+Vector((255,-470,153));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=max(260,max(y-x for x,y in zip(lo,hi))*1.3)
   scene.render.filepath=str(ROOT/f'evidence/pose_{name}.png');bpy.ops.render.render(write_still=True)
 poses.append({'animation':name,'duration_frames':anm.duration,'fps':anm.fps,'samples':samples})
report={'status':'OFFLINE STRUCTURAL AND SAMPLED NATIVE POSE VALIDATION','model_sha256':hashlib.sha256((ROOT/'work/redmist_model.skn').read_bytes()).hexdigest(),'checks':checks,'poses':poses,'limitations':'15 sampled native animation poses; five renders use source atlas, not final edited texture. Does not establish gameplay readability or collision/ability behavior.'}
(ROOT/'evidence/pose_validation.json').write_text(json.dumps(report,indent=2))
print('POSE_VALIDATION',json.dumps(checks))
