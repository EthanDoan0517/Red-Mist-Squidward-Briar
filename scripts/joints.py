import sys
sys.path.insert(0,r'C:/Users/etqdo/Documents/maya/LtMAO/src')
from LtMAO.pyRitoFile.skl import SKL
from mathutils import Matrix,Vector,Quaternion
k=SKL().read(r'References/Squidward Briar Maya/briar.wad.client/assets/Etdoan/Squidward-Briar/briar_base.skl')
for j in k.joints:
 if j.name in ['Pelvis','Head','Neck','Spine1','Spine2','L_Hip','L_KneeLower','L_Foot','L_Toe','L_Clavicle','L_Shoulder','L_Elbow','L_Hand','R_Hand']:
  q=j.ibind_rotate; m=Matrix.LocRotScale(Vector(tuple(j.ibind_translate)),Quaternion((q.w,q.x,q.y,q.z)),Vector(tuple(j.ibind_scale))).inverted();print(j.name,tuple(m.translation))
