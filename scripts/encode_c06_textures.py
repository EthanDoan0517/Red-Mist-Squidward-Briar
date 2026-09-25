from pathlib import Path
import sys,io,json,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[1];sys.path[:0]=[r'C:/Users/etqdo/Documents/maya/LtMAO/src',str(R/'work/c05-deps')]
import xxhash
from LtMAO.pyRitoFile.tex import TEX,TEXFormat
stage=R/'work/c06-textures/ASSETS/RedMistBriar';stage.mkdir(parents=True,exist_ok=True)
im=Image.open(R/'work/c06/boys_who_cry.png').convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS)
assert im.getchannel('A').getextrema()==(0,255),'Must retain actual transparent circle'
mips=[]
for n in reversed(range(11)):
 d=max(1,1024>>n);b=io.BytesIO();im.resize((d,d),Image.Resampling.LANCZOS).save(b,format='DDS',pixel_format='DXT5');mips.append(b.getvalue()[128:])
 if n==0:Image.open(io.BytesIO(b.getvalue())).save(R/'evidence/c06_circle_decoded.png')
path=stage/'boys_who_cry.tex';TEX(width=1024,height=1024,format=TEXFormat.DXT5,mipmaps=True,data=mips).write(str(path));assert TEX().read(str(path)).data==mips
# Exact native shader mask constants mapped to C05 face palette slots.
colors=['000000','ff0000','ff0000','00ff00','000000','000000','000000','000000']
rgba=b''.join(bytes.fromhex(c)+b'\xff' for c in colors for _ in range(8))*8
bgra=b''.join(bytes((rgba[i+2],rgba[i+1],rgba[i],rgba[i+3])) for i in range(0,len(rgba),4))
path=stage/'face_bloom_mask.tex';TEX(width=64,height=8,format=TEXFormat.BGRA8,mipmaps=False,data=[bgra]).write(str(path));assert TEX().read(str(path)).data==[bgra]
hashes={n:xxhash.xxh64(('assets/redmistbriar/'+n).encode()).hexdigest() for n in ['face_colors.tex','face_bloom_mask.tex','boys_who_cry.tex']};(R/'work/c06/texture_hashes.json').write_text(json.dumps(hashes,indent=2))
(R/'evidence/c06_textures.json').write_text(json.dumps({'background':'two supplied frames reconstructed with ImageGen, Squidward removed; circle alpha retained','circle_format':'DXT5 1024x1024,11mips','mask_format':'BGRA8 64x8','mask_channels':'R=red/coral eye swatches,G=white eye swatch,black/blood=0','texture_hashes':hashes},indent=2));print(hashes)
