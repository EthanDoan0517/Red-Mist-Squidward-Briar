from pathlib import Path
import sys,io,json,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[1];sys.path.insert(0,r'C:/Users/etqdo/Documents/maya/LtMAO/src')
from LtMAO.pyRitoFile.tex import TEX,TEXFormat
stage=R/'work/candidate-c05/Briar.wad.client'
source=R/'work/c05/body-gray-atlas.png';image=Image.open(source).convert('RGB').resize((1024,1024),Image.Resampling.LANCZOS);mips=[]
for n in reversed(range(11)):
 d=max(1,1024>>n);im=image.resize((d,d),Image.Resampling.LANCZOS);b=io.BytesIO();im.save(b,format='DDS',pixel_format='DXT1');mips.append(b.getvalue()[128:])
 if n==0:Image.open(io.BytesIO(b.getvalue())).save(R/'evidence/c05_body_decoded.png')
path=stage/'0e35941cdacaff56.tex';TEX(width=1024,height=1024,format=TEXFormat.DXT1,mipmaps=True,data=mips).write(str(path));assert TEX().read(str(path)).data==mips
# Native material lookup constants, not a painted image. Uncompressed values keep exact requested RGB.
colors=['000000','fe4e4a','ee6054','ffffff','650021','62432f','cac6cf','000000']
rgba=b''.join(bytes.fromhex(c)+b'\xff' for c in colors for _ in range(8))*8
bgra=b''.join(bytes((rgba[i+2],rgba[i+1],rgba[i],rgba[i+3])) for i in range(0,len(rgba),4))
path=stage/'ASSETS/RedMistBriar/face_colors.tex';TEX(width=64,height=8,format=TEXFormat.BGRA8,mipmaps=False,data=[bgra]).write(str(path));assert TEX().read(str(path)).data==[bgra]
Image.frombytes('RGBA',(64,8),rgba).save(R/'evidence/c05_face_palette.png')
(R/'evidence/c05_textures.json').write_text(json.dumps({'body_source':str(source.relative_to(R)),'body_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'body_format':'DXT1 1024x1024,11mips','face_format':'BGRA8 64x8 exact material constants','palette':colors,'reference':'References/ref image squidward.png','body_method':'ImageGen color-only UV atlas edit; source preserved'},indent=2))
print('C05 body and native face material encoded and roundtrip verified')
