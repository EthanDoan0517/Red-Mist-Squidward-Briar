"""Encode supplied clarinet texture and pack supplied burger material atlases."""
import sys,io,json,shutil
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1];sys.path.insert(0,r'C:/Users/etqdo/Documents/maya/LtMAO/src')
from LtMAO.pyRitoFile.tex import TEX,TEXFormat
stage=R/'work/candidate-c03/Briar.wad.client';custom=stage/'ASSETS/RedMistBriar';custom.mkdir(parents=True,exist_ok=True)
def encode(image,path,size):
 image=image.convert('RGB').resize((size,size),Image.Resampling.LANCZOS);mips=[]
 for n in reversed(range(size.bit_length())):
  dim=max(1,size>>n);im=image.resize((dim,dim),Image.Resampling.LANCZOS);b=io.BytesIO();im.save(b,format='DDS',pixel_format='DXT1');payload=b.getvalue()[128:];assert len(payload)==max(1,(dim+3)//4)**2*8;mips.append(payload)
  if n==0:Image.open(io.BytesIO(b.getvalue())).save(R/'evidence'/('c03_'+path.stem+'_decoded.png'))
 TEX(width=size,height=size,format=TEXFormat.DXT1,mipmaps=True,data=mips).write(str(path));assert TEX().read(str(path)).data==mips
 return {'path':str(path.relative_to(stage)),'dimensions':[size,size],'format':'DXT1','mip_count':len(mips),'decoded':'PASS'}
# Weapon diffuse is exclusively used by removed native pillory meshes and FrenzyDaggers.
records=[encode(Image.open(R/'References/textures/clarinet.png'),stage/'0ea451e749d9d041.tex',512)]
atlas=Image.new('RGB',(1024,1024))
names=['bottombun','cheese','lettuce','onion','patty','pickle','sesameseeds','tomato','topbun']
for tile,name in enumerate(names):
 source=Image.open(R/f'References/krabby-patty/textures/{name}_d.png').convert('RGB').resize((248,248),Image.Resampling.LANCZOS)
 cell=Image.new('RGB',(256,256));cell.paste(source,(4,4));cell.paste(source.crop((0,0,1,248)).resize((4,248)),(0,4));cell.paste(source.crop((247,0,248,248)).resize((4,248)),(252,4));cell.paste(cell.crop((0,4,256,5)).resize((256,4)),(0,0));cell.paste(cell.crop((0,251,256,252)).resize((256,4)),(0,252))
 atlas.paste(cell,((tile%4)*256,(tile//4)*256))
atlas.save(R/'work/c03-burger-atlas.png');records.append(encode(atlas,custom/'burger.tex',1024))
shutil.copy2(R/'work/candidate-c02/Briar.wad.client/0e35941cdacaff56.tex',stage/'0e35941cdacaff56.tex')
for p in (R/'work/c03-art/Briar.wad.client').glob('*'):shutil.copy2(p,stage/p.name)
(R/'evidence/c03_textures.json').write_text(json.dumps(records,indent=2));print(json.dumps(records))
