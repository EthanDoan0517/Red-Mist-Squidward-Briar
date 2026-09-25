"""Supplied-art-only HUD and loading crops, native TEX dimensions/formats."""
from pathlib import Path
import sys, io, json, hashlib
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,r'C:/Users/etqdo/Documents/maya/LtMAO/src')
from LtMAO.pyRitoFile.tex import TEX
source=ROOT/'References/reference image, splash art and portrait icon.webp'
art=Image.open(source).convert('RGB')
stage=ROOT/'work/c03-art/Briar.wad.client';stage.mkdir(parents=True,exist_ok=True)
evidence=ROOT/'evidence'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def decode(t):
 buf=io.BytesIO();Image.new('RGBA' if t.format.name=='DXT5' else 'RGB',(t.width,t.height)).save(buf,format='DDS',pixel_format=t.format.name)
 out=Image.open(io.BytesIO(buf.getvalue()[:128]+t.data[0]));out.load();return out
records=[]
specs=[('portrait_square','9a2d941d891bbf9c',(442,135,802,495),'hud/briar_square_0.tex'),('portrait_circle','b7aca08692f3da3e',(408,115,828,535),'hud/briar_circle_0.tex'),('loading','25a8846439092af3',(454,0,788,607),'briarloadscreen_0.tex')]
for label,target,crop,reference in specs:
 original=ROOT/'work/original'/f'{target}.tex';native=TEX().read(str(original))
 supplied=ROOT/'References/Squidward Briar Maya/briar.wad.client/assets/Etdoan/Squidward-Briar'/reference
 assert sha(original)==sha(supplied)
 assert not native.mipmaps
 image=art.crop(crop).resize((native.width,native.height),Image.Resampling.LANCZOS)
 alpha=None
 if native.format.name=='DXT5':
  alpha=decode(native).getchannel('A');image=image.convert('RGBA');image.putalpha(alpha)
 buf=io.BytesIO();image.save(buf,format='DDS',pixel_format=native.format.name);dds=buf.getvalue()
 decoded=Image.open(io.BytesIO(dds));decoded.load()
 payload=dds[128:];expected=((native.width+3)//4)*((native.height+3)//4)*(16 if native.format.name=='DXT5' else 8)
 assert len(payload)==expected==len(native.data[0])
 encoded=TEX(width=native.width,height=native.height,format=native.format,mipmaps=False,data=[payload]);dest=stage/f'{target}.tex';encoded.write(str(dest))
 check=TEX().read(str(dest));assert check.data[0]==payload and (check.width,check.height)==decoded.size
 assert dest.stat().st_size==original.stat().st_size
 preview=evidence/f'c03_art_{label}.png';decoded.save(preview)
 records.append({'role':label,'source_crop_xyxy':crop,'native_hash':target,'native_reference_match':reference,'native_sha256':sha(original),'output_sha256':sha(dest),'output':str(dest.relative_to(ROOT)),'dimensions':[native.width,native.height],'format':native.format.name,'mips':1,'bytes':dest.stat().st_size,'decoded_preview':str(preview.relative_to(ROOT)),'native_alpha_mask_preserved_before_DXT5_encoding':alpha is not None})
board=Image.new('RGB',(630,600),(30,30,30));draw=ImageDraw.Draw(board)
for label,x,y in [('portrait_square',330,55),('portrait_circle',480,55),('loading',10,30)]:
 im=Image.open(evidence/f'c03_art_{label}.png');board.paste(im,(x,y),im.getchannel('A') if im.mode=='RGBA' else None);draw.text((x,y-20),label,fill='white')
draw.text((330,240),'Supplied image crops only',fill='white');draw.text((330,260),'Native dimensions / formats',fill='white')
board.save(evidence/'c03_art_contact_sheet.png')
report={'status':'OFFLINE VALIDATED','source':str(source.relative_to(ROOT)),'source_sha256':sha(source),'source_dimensions':list(art.size),'processing':'Crop and Lanczos resize supplied artwork; native circular portrait alpha mask retained; DDS DXT encoding wrapped in native TEX. No generated/repainted content.','assets':records,'limits':'Native HUD and loading appearance requires user gameplay/loading feedback. Original supplied artwork has intentionally soft/video-source detail; no sharpening or invented detail applied.'}
(evidence/'c03_art_validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'assets':len(records),'status':report['status'],'output':str(stage)}))
