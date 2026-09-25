"""Lossless source preservation; deterministic atlas encoding and minimal mod staging."""
from pathlib import Path
import sys, io, json, shutil, hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,r'C:/Users/etqdo/Documents/maya/LtMAO/src')
from LtMAO.pyRitoFile.tex import TEX, TEXFormat
stage=ROOT/'work/candidate-c01/Briar.wad.client'
model=stage/'ASSETS/Characters/Briar/Skins/Base/Briar_Base.skn'
model.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(ROOT/'work/redmist_model.skn',model)
source=ROOT/'References/spongebob-squarepants-squidward-model/textures/T_MP_Squidward_D.001.png'
im=Image.open(source).convert('RGB').resize((1024,1024),Image.Resampling.LANCZOS)
mips=[];validation=[]
for level in reversed(range(11)):
 size=max(1,1024>>level);m=im.resize((size,size),Image.Resampling.LANCZOS);buf=io.BytesIO();m.save(buf,format='DDS',pixel_format='DXT1');raw=buf.getvalue()
 assert raw[:4]==b'DDS ' and raw[84:88]==b'DXT1'
 payload=raw[128:];expected=max(1,(size+3)//4)**2*8;assert len(payload)==expected
 decoded=Image.open(io.BytesIO(raw));decoded.load();assert decoded.size==(size,size)
 mips.append(payload);validation.append({'level':level,'size':size,'bytes':len(payload)})
 if level==0:decoded.save(ROOT/'evidence/encoded_atlas.png')
tex=TEX(width=1024,height=1024,format=TEXFormat.DXT1,mipmaps=True,data=mips)
dest=stage/'0e35941cdacaff56.tex';tex.write(str(dest));rt=TEX().read(str(dest));assert rt.data==mips
meta=ROOT/'work/candidate-c01/mod/META';meta.mkdir(parents=True,exist_ok=True)
(meta/'info.json').write_text(json.dumps({'Name':'Red Mist Squidward Briar - Model C01','Author':'etqdo','Version':'0.1.0','Description':'Model-only gameplay candidate for base Briar: supplied Squidward model, bloody eyes and no pillory mesh. Native skeleton, animations, VFX, audio and HUD inherited unchanged. Offline checks only; awaiting user gameplay feedback.','Heart':'','Home':''},indent=2))
e={'texture_source':str(source.relative_to(ROOT)),'encoding':'DXT1 opaque, 1024x1024, complete 11-level mip chain, smallest first','creative_texture_edits':False,'bloody_eyes':'native mesh UV assignment plus four head-weighted blood trails','mips':validation,'payloads':{str(p.relative_to(stage)):hashlib.sha256(p.read_bytes()).hexdigest() for p in stage.rglob('*') if p.is_file()}}
(ROOT/'evidence/texture_and_staging.json').write_text(json.dumps(e,indent=2));print(json.dumps(e,indent=2))
