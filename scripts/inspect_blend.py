import bpy,json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath=str(Path('References/spongebob-squarepants-squidward-model/source/Deltarune.blend').resolve()))
o=bpy.data.objects['SK_MP_Squidward.mo']; a=bpy.data.objects['Armature']
print('OBJECT',o.matrix_world, 'BOUNDS',[(min((o.matrix_world@v.co)[i] for v in o.data.vertices),max((o.matrix_world@v.co)[i] for v in o.data.vertices)) for i in range(3)])
print('BONES',[(b.name,tuple(a.matrix_world@b.head_local),tuple(a.matrix_world@b.tail_local)) for b in a.data.bones]); print('GROUPS',[g.name for g in o.vertex_groups]); print('MATS',[m.name for m in o.data.materials])
print('POSE',[(p.name,tuple(p.rotation_quaternion)) for p in a.pose.bones if p.rotation_quaternion.angle>0.01])
