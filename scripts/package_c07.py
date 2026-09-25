"""Assemble C07 from preserved C06 plus only validated R/flower/audio overrides."""
from pathlib import Path
import sys,json,shutil,subprocess,zipfile,struct,hashlib,collections
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'work/c05-deps'),str(R/'scripts')]
import xxhash
from skn_layout import require_complete
from strict_prop import StrictPROP
root=R/'work/candidate-c07';out=R/'skin versions/RedMist-Squidward-Briar-C07.fantome';assert not out.exists()
for w in (R/'work/candidate-c06').glob('*.wad.client'):shutil.copytree(w,root/w.name,dirs_exist_ok=True)
for source in ['c07-r','c07-textures','c07-audio']:
 folder=R/'work'/source;assert folder.exists()
 for w in folder.glob('*.wad.client'):shutil.copytree(w,root/w.name,dirs_exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
meta=root/'mod/META';meta.mkdir(parents=True,exist_ok=True)
(meta/'info.json').write_text(json.dumps({'Name':'Red Mist Squidward Briar - C07','Author':'etqdo','Version':'0.7.0','Description':'Large R warning circle uses Boys Who Cry at50%alpha with stable upright ground orientation; small R target circle is glowing red SpongeBob flower. Supplied shop-purchase and laugh audio added. C06 model/eyes/props and other custom audio retained. Offline validated; gameplay pending.','Heart':'','Home':''},indent=2))
base=root/'Briar.wad.client';before=R/'work/candidate-c06/Briar.wad.client'
protected=['ASSETS/Characters/Briar/Skins/Base/Briar_Base.skn','0e35941cdacaff56.tex','0ea451e749d9d041.tex','25a8846439092af3.tex','9a2d941d891bbf9c.tex','b7aca08692f3da3e.tex','ASSETS/RedMistBriar/burger.scb','ASSETS/RedMistBriar/burger.tex','ASSETS/RedMistBriar/boys_who_cry.tex','ASSETS/RedMistBriar/face_colors.tex','ASSETS/RedMistBriar/face_bloom_mask.tex']
assert all((base/p).read_bytes()==(before/p).read_bytes() for p in protected)
tool=r'C:/Users/etqdo/Downloads/cslol-go/cslol-tools/mod-tools.exe';game='--game:C:/Riot Games/League of Legends/Game';wads=list(root.glob('*.wad.client'));counts={};manifests={}
for stage in wads:
 files=[p for p in stage.rglob('*') if p.is_file()];counts[stage.name]=len(files);manifests[stage.name]={str(p.relative_to(stage)).replace('\\','/'):sha(p.read_bytes()) for p in files}
 for p in files:
  if p.suffix=='.skn':require_complete(p.read_bytes())
  if p.suffix=='.bin':StrictPROP(p.read_bytes()).run()
 subprocess.run([tool,'addwad',str(stage),str(root/'mod'),game,'--noTFT'],check=True)
subprocess.run([tool,'export',str(root/'mod'),str(out),game,'--noTFT'],check=True)
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None and set(z.namelist())=={'META/info.json',*('WAD/'+w.name for w in wads)}
 for stage in wads:
  wad=z.read('WAD/'+stage.name);count=struct.unpack_from('<I',wad,268)[0];assert count==counts[stage.name]
  hashes={f'{struct.unpack_from("<Q",wad,272+i*32)[0]:016x}' for i in range(count)};files=[p for p in stage.rglob('*') if p.is_file()]
  expected={p.stem.lower() if len(p.stem)==16 and all(c in '0123456789abcdef' for c in p.stem.lower()) else xxhash.xxh64(str(p.relative_to(stage)).replace('\\','/').lower().encode()).hexdigest() for p in files};assert hashes==expected
  wp=root/'final'/stage.name;wp.parent.mkdir(exist_ok=True);wp.write_bytes(wad);unpacked=root/'roundtrip'/stage.name
  subprocess.run([r'C:/Users/etqdo/Downloads/wadtools-0.5.7-windows-x64/wadtools.exe','extract','-i',str(wp),'-o',str(unpacked),'--full-bin-scan'],check=True,capture_output=True)
  extracted=[p for p in unpacked.rglob('*') if p.is_file()];assert len(extracted)==count and collections.Counter(sha(p.read_bytes()) for p in files)==collections.Counter(sha(p.read_bytes()) for p in extracted)
result={'status':'OFFLINE VALIDATED; GAMEPLAY PENDING','package':str(out.relative_to(R)),'sha256':sha(out.read_bytes()),'bytes':out.stat().st_size,'wad_counts':counts,'zip_crc':'PASS','native_path_hashes':'PASS','all_final_payloads_match_staging':'PASS','strict_SKN_BIN':'PASS','protected_C06_assets_unchanged':protected,'manifests':manifests}
(R/'evidence/c07_package_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ['manifests','protected_C06_assets_unchanged']},indent=2))
