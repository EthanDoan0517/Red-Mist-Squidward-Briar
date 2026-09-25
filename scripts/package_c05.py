"""Merge verified C05 audio and visuals; preserve prior gameplay candidates."""
from pathlib import Path
import sys,shutil,hashlib,json,zipfile,subprocess,struct,collections
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'work/c05-deps'),str(R/'scripts')]
import xxhash
from skn_layout import require_complete
from strict_prop import StrictPROP
stage=R/'work/candidate-c05/Briar.wad.client'
for p in (R/'work/c05-audio/Briar.wad.client').rglob('*'):
 if p.is_file():
  dst=stage/p.relative_to(R/'work/c05-audio/Briar.wad.client');assert not dst.exists();dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
files=[p for p in stage.rglob('*') if p.is_file()];assert len(files)==13
sha=lambda b:hashlib.sha256(b).hexdigest()
manifest={str(p.relative_to(stage)).replace('\\','/'):sha(p.read_bytes()) for p in files}
for p in files:
 if p.suffix=='.skn':require_complete(p.read_bytes())
 if p.suffix=='.bin':StrictPROP(p.read_bytes()).run()
mod=stage.parent/'mod';meta=mod/'META';meta.mkdir(parents=True,exist_ok=True)
(meta/'info.json').write_text(json.dumps({'Name':'Red Mist Squidward Briar - C05','Author':'etqdo','Version':'0.5.0','Description':'Clarinets 3x C04; burger 2x C04, level and isolated. Removed frenzy dagger and R jet flares. Reference-based black/red/white eyes with burgundy tears; gray body. Supplied E, footstep and death sounds. Original skeleton and motion retained; portrait and loading art retained. Offline validated; C05 gameplay pending.','Heart':'','Home':''},indent=2))
out=R/'skin versions/RedMist-Squidward-Briar-C05.fantome';assert not out.exists()
tool=r'C:/Users/etqdo/Downloads/cslol-go/cslol-tools/mod-tools.exe';game='--game:C:/Riot Games/League of Legends/Game'
for args in [('addwad',str(stage),str(mod),game,'--noTFT'),('export',str(mod),str(out),game,'--noTFT')]:subprocess.run([tool,*args],check=True)
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None and set(z.namelist())=={'META/info.json','WAD/Briar.wad.client'};wad=z.read('WAD/Briar.wad.client')
count=struct.unpack_from('<I',wad,268)[0];assert count==len(files)
hashes={f'{struct.unpack_from("<Q",wad,272+i*32)[0]:016x}' for i in range(count)}
expected={p.stem.lower() if len(p.stem)==16 and all(c in '0123456789abcdef' for c in p.stem.lower()) else xxhash.xxh64(str(p.relative_to(stage)).replace('\\','/').lower().encode()).hexdigest() for p in files}
assert hashes==expected
w=stage.parent/'final/Briar.wad.client';w.parent.mkdir(parents=True,exist_ok=True);w.write_bytes(wad)
unpacked=stage.parent/'roundtrip';subprocess.run([r'C:/Users/etqdo/Downloads/wadtools-0.5.7-windows-x64/wadtools.exe','extract','-i',str(w),'-o',str(unpacked),'--full-bin-scan'],check=True,capture_output=True)
extracted=[p for p in unpacked.rglob('*') if p.is_file()];assert len(extracted)==len(files)
assert collections.Counter(sha(p.read_bytes()) for p in files)==collections.Counter(sha(p.read_bytes()) for p in extracted)
result={'status':'OFFLINE VALIDATED; GAMEPLAY PENDING','package':str(out.relative_to(R)),'sha256':sha(out.read_bytes()),'bytes':out.stat().st_size,'wad_payloads':count,'zip_crc':'PASS','native_path_hashes':'PASS','extracted_payload_equality':'PASS','strict_SKN_footer_and_BIN_sizes':'PASS','manifest':manifest,'runtime':'C02 load user confirmed; C05 not tested'}
(R/'evidence/c05_package_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='manifest'},indent=2))
