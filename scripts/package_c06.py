"""C06 two-WAD package with exact path hashes and re-extracted payload equality."""
from pathlib import Path
import sys,shutil,hashlib,json,zipfile,subprocess,struct,collections
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'work/c05-deps'),str(R/'scripts')]
import xxhash
from skn_layout import require_complete
from strict_prop import StrictPROP
root=R/'work/candidate-c06';out=R/'skin versions/RedMist-Squidward-Briar-C06.fantome';assert not out.exists(),'Preserve delivered checkpoints'
for wad in (R/'work/c06-audio').glob('*.wad.client'):
 shutil.copytree(wad,root/wad.name,dirs_exist_ok=True)
shutil.copytree(R/'work/c06-textures',root/'Briar.wad.client',dirs_exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
meta=root/'mod/META';meta.mkdir(parents=True,exist_ok=True)
(meta/'info.json').write_text(json.dumps({'Name':'Red Mist Squidward Briar - C06','Author':'etqdo','Version':'0.6.0','Description':'Corrected outward eye geometry and native red/white bloom. Clarinets2.5x C04. Burger spins once/2sec, stays level. Boys Who Cry circular post-hit R target backdrop. Native base Briar SFX and en_US VO silenced; custom E/steps/death retained, explicit death trigger and respawn stop. Offline validated; gameplay feedback pending.','Heart':'','Home':''},indent=2))
tool=r'C:/Users/etqdo/Downloads/cslol-go/cslol-tools/mod-tools.exe';game='--game:C:/Riot Games/League of Legends/Game';wads=list(root.glob('*.wad.client'));assert len(wads)==2
manifests={};counts={}
for stage in wads:
 files=[p for p in stage.rglob('*') if p.is_file()];counts[stage.name]=len(files)
 for p in files:
  if p.suffix=='.skn':require_complete(p.read_bytes())
  if p.suffix=='.bin':StrictPROP(p.read_bytes()).run()
 manifests[stage.name]={str(p.relative_to(stage)).replace('\\','/'):sha(p.read_bytes()) for p in files}
 subprocess.run([tool,'addwad',str(stage),str(root/'mod'),game,'--noTFT'],check=True)
assert counts=={'Briar.wad.client':15,'Briar.en_US.wad.client':2} or counts=={'Briar.en_US.wad.client':2,'Briar.wad.client':15}
subprocess.run([tool,'export',str(root/'mod'),str(out),game,'--noTFT'],check=True)
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None and set(z.namelist())=={'META/info.json',*('WAD/'+w.name for w in wads)}
 for stage in wads:
  wad=z.read('WAD/'+stage.name);count=struct.unpack_from('<I',wad,268)[0];assert count==counts[stage.name]
  hashes={f'{struct.unpack_from("<Q",wad,272+i*32)[0]:016x}' for i in range(count)}
  files=[p for p in stage.rglob('*') if p.is_file()]
  expected={p.stem.lower() if len(p.stem)==16 and all(c in '0123456789abcdef' for c in p.stem.lower()) else xxhash.xxh64(str(p.relative_to(stage)).replace('\\','/').lower().encode()).hexdigest() for p in files};assert hashes==expected
  wp=root/'final'/stage.name;wp.parent.mkdir(exist_ok=True);wp.write_bytes(wad);unpacked=root/'roundtrip'/stage.name
  subprocess.run([r'C:/Users/etqdo/Downloads/wadtools-0.5.7-windows-x64/wadtools.exe','extract','-i',str(wp),'-o',str(unpacked),'--full-bin-scan'],check=True,capture_output=True)
  extracted=[p for p in unpacked.rglob('*') if p.is_file()];assert len(extracted)==count
  assert collections.Counter(sha(p.read_bytes()) for p in files)==collections.Counter(sha(p.read_bytes()) for p in extracted)
result={'status':'OFFLINE VALIDATED; C06 GAMEPLAY PENDING','package':str(out.relative_to(R)),'sha256':sha(out.read_bytes()),'bytes':out.stat().st_size,'wad_counts':counts,'zip_crc':'PASS','native_path_hashes':'PASS','all_final_payloads_match_staging':'PASS','strict_SKN_BIN':'PASS','manifests':manifests,'runtime':'User reported C05 black eyes and inaudible death. C06 contains targeted fixes, not yet runtime confirmed.'}
(R/'evidence/c06_package_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='manifests'},indent=2))
