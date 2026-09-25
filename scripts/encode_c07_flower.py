from pathlib import Path
import sys,io,json,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[1];sys.path.insert(0,r'C:/Users/etqdo/Documents/maya/LtMAO/src')
from LtMAO.pyRitoFile.tex import TEX,TEXFormat
source=R/'work/c07/red_flower.png';im=Image.open(source).convert('RGBA').resize((512,512),Image.Resampling.LANCZOS)
assert im.getchannel('A').getextrema()==(0,255)
mips=[]
for n in reversed(range(10)):
 d=max(1,512>>n);b=io.BytesIO();im.resize((d,d),Image.Resampling.LANCZOS).save(b,format='DDS',pixel_format='DXT5');payload=b.getvalue()[128:];assert len(payload)==max(1,(d+3)//4)**2*16;mips.append(payload)
 if n==0:Image.open(io.BytesIO(b.getvalue())).save(R/'evidence/c07_flower_decoded.png')
path=R/'work/c07-textures/Briar.wad.client/ASSETS/RedMistBriar/red_flower.tex';path.parent.mkdir(parents=True,exist_ok=True);TEX(width=512,height=512,format=TEXFormat.DXT5,mipmaps=True,data=mips).write(str(path));assert TEX().read(str(path)).data==mips
(R/'evidence/c07_flower_validation.json').write_text(json.dumps({'source':str(source.relative_to(R)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'texture_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'format':'DXT5','dimensions':[512,512],'mips':10,'alpha':'preserved','reference':'References/Spongebob flower, small R hit.webp','decode_roundtrip':'PASS'},indent=2));print('Flower encoded: DXT5,512square,10mips,alpha retained')
