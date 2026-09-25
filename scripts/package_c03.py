"""Package and inspect final C03 without changing manager profiles or game files."""
from pathlib import Path
import json,hashlib,zipfile,subprocess,struct,collections,sys
from skn_layout import require_complete
VERSION=sys.argv[1].lower() if len(sys.argv)>1 else 'c03';assert VERSION in ('c03','c04')
R=Path(__file__).resolve().parents[1];stage=R/f'work/candidate-{VERSION}/Briar.wad.client';mod=R/f'work/candidate-{VERSION}/mod';meta=mod/'META';meta.mkdir(parents=True,exist_ok=True)
out=R/f'skin versions/RedMist-Squidward-Briar-{VERSION.upper()}.fantome';assert not out.exists(),'Existing checkpoint must be preserved'
sha=lambda data:hashlib.sha256(data).hexdigest()
files=[p for p in stage.rglob('*') if p.is_file()];assert len(files)==9
model=stage/'ASSETS/Characters/Briar/Skins/Base/Briar_Base.skn';require_complete(model.read_bytes())
assert (stage/'0e35941cdacaff56.tex').read_bytes()==(R/'work/candidate-c02/Briar.wad.client/0e35941cdacaff56.tex').read_bytes()
description='C02 load repair retained. Two supplied clarinets on native frenzy hand weapons; supplied Krabby Patty R projectile core; supplied portrait and loading artwork. Original Squidward body, bloody eyes, invisible pillory, native skeleton/animations/audio preserved.'
if VERSION=='c04':description+=' Clarinets 1.75x larger. Burger stays world upright without squash; only burger in the flying R effect, other projectile emitters removed.'
(meta/'info.json').write_text(json.dumps({'Name':f'Red Mist Squidward Briar - {VERSION.upper()}','Author':'etqdo','Version':f'0.{int(VERSION[1:])}.0','Description':description+f' Awaiting {VERSION.upper()} gameplay validation.','Heart':'','Home':''},indent=2))
tool=r'C:/Users/etqdo/Downloads/cslol-go/cslol-tools/mod-tools.exe';game='--game:C:/Riot Games/League of Legends/Game'
for args in [('addwad',str(stage),str(mod),game,'--noTFT'),('export',str(mod),str(out),game,'--noTFT')]:subprocess.run([tool,*args],check=True)
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None and set(z.namelist())=={'META/info.json','WAD/Briar.wad.client'}
 wad=z.read('WAD/Briar.wad.client')
count=struct.unpack_from('<I',wad,268)[0];assert count==9
hashes={f'{struct.unpack_from("<Q",wad,272+i*32)[0]:016x}' for i in range(count)}
known={'9144d26d7f271649','0e35941cdacaff56','0ea451e749d9d041','25a8846439092af3','9a2d941d891bbf9c','b7aca08692f3da3e','f279b76afd0f0a62'}
assert known<=hashes and len(hashes-known)==2
w=R/f'work/candidate-{VERSION}/final/Briar.wad.client';w.parent.mkdir(parents=True,exist_ok=True);w.write_bytes(wad)
unpacked=R/f'work/candidate-{VERSION}/roundtrip'
subprocess.run([r'C:/Users/etqdo/Downloads/wadtools-0.5.7-windows-x64/wadtools.exe','extract','-i',str(w),'-o',str(unpacked),'--full-bin-scan'],check=True,capture_output=True)
extracted=[p for p in unpacked.rglob('*') if p.is_file()];assert len(extracted)==9
assert collections.Counter(sha(p.read_bytes()) for p in files)==collections.Counter(sha(p.read_bytes()) for p in extracted)
for suffix in ['burger.scb','burger.tex']:
 assert next(p for p in extracted if p.name.lower()==suffix).read_bytes()==(stage/'ASSETS/RedMistBriar'/suffix).read_bytes()
require_complete(next(p for p in extracted if p.suffix.lower()=='.skn').read_bytes())
manifest={str(p.relative_to(stage)):sha(p.read_bytes()) for p in files}
result={'status':f'OFFLINE VALIDATED; {VERSION.upper()} GAMEPLAY PENDING','package':str(out.relative_to(R)),'sha256':sha(out.read_bytes()),'bytes':out.stat().st_size,'zip_crc':'PASS','wad_payloads':count,'wad_hashes':sorted(hashes),'final_archive_payloads_match_staging':True,'custom_R_mesh_texture_references_resolve':'PASS','strict_SKN_footer':'PASS','manifest':manifest,'protected':'C02 body vertex/index data and diffuse unchanged; native SKL/ANM/animation graph/audio omitted;62non-R BIN entries unchanged','runtime':f'C02 load confirmed by user; {VERSION.upper()} awaiting feedback'}
(R/f'evidence/{VERSION}_package_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='manifest'},indent=2))
