"""Copy only the two supplied clarinet meshes into a static prop source scene."""
import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
source=R/'References/source/squidward_clarinet_final.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))
keep=[];report=[]
for name in ['Clarinet','ShootClarinet']:
 obj=bpy.data.objects[name];world=obj.matrix_world.copy();obj.data=obj.data.copy();obj.modifiers.clear();obj.parent=None;obj.matrix_world=world
 report.append({'name':name,'vertices':len(obj.data.vertices),'polygons':len(obj.data.polygons),'materials':[m.name for m in obj.data.materials]})
 keep.append(obj)
for obj in list(bpy.data.objects):
 if obj not in keep:bpy.data.objects.remove(obj,do_unlink=True)
bpy.data.orphans_purge(do_recursive=True)
textures=[{'name':i.name,'path':i.filepath,'packed':i.packed_file is not None,'exists':Path(bpy.path.abspath(i.filepath)).exists()} for i in bpy.data.images if i.name!='Render Result']
bpy.ops.wm.save_as_mainfile(filepath=str(R/'work/clarinets-only.blend'))
result={'source':str(source.relative_to(R)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'isolated_scene':'work/clarinets-only.blend','objects':report,'texture_inventory':textures,'excluded':'Base, EyeBags, Eyes, Pupils, Armature, WeaponController; no new Squidward geometry used','integration':'pending C02 gameplay load confirmation'}
(R/'evidence/clarinet_source.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
