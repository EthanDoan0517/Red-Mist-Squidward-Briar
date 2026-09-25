"""C01->C02: append only the missing native SKN footer and rebuild in isolation."""
from pathlib import Path
import hashlib,json,zipfile,subprocess,sys
from skn_layout import inspect,require_complete
R=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
old=R/'skin versions/RedMist-Squidward-Briar-C01.fantome'
assert sha(old.read_bytes())=='094ac00f3d5dbdc09caf7414acf85d69db134fadd8cb25058effc453699dc6cf'
src=R/'work/final-roundtrip/9144d26d7f271649.skn'
if not src.exists():src=R/'work/redmist_model.skn'
before=src.read_bytes();before_info=inspect(before)
assert before_info['footer_bytes']==0 and before_info['version']=='4.1'
native=(R/'References/Squidward Briar Maya/briar.wad.client/assets/Etdoan/Squidward-Briar/briar_base.skn').read_bytes()
require_complete(native)
footer=native[-12:];assert footer==bytes(12)
after=before+footer;after_info=require_complete(after);assert after[:-12]==before
stage=R/'work/candidate-c02/Briar.wad.client';model=stage/'ASSETS/Characters/Briar/Skins/Base/Briar_Base.skn';model.parent.mkdir(parents=True,exist_ok=True);model.write_bytes(after)
texture=(R/'work/candidate-c01/Briar.wad.client/0e35941cdacaff56.tex').read_bytes();(stage/'0e35941cdacaff56.tex').write_bytes(texture)
mod=R/'work/candidate-c02/mod';meta=mod/'META';meta.mkdir(parents=True,exist_ok=True)
(meta/'info.json').write_text(json.dumps({'Name':'Red Mist Squidward Briar - C02 load repair','Author':'etqdo','Version':'0.2.0','Description':'C01 load repair: restore required 12-byte SKN footer. Geometry, eyes, texture, invisible pillory and original animations/VFX unchanged. No clarinets yet. Awaiting runtime confirmation.','Heart':'','Home':''},indent=2))
tool=r'C:/Users/etqdo/Downloads/cslol-go/cslol-tools/mod-tools.exe';game='--game:C:/Riot Games/League of Legends/Game';out=R/'skin versions/RedMist-Squidward-Briar-C02.fantome'
assert not out.exists(),'Preserve existing C02; version changed candidates separately'
for args in [('addwad',str(stage),str(mod),game,'--noTFT'),('export',str(mod),str(out),game,'--noTFT')]:subprocess.run([tool,*args],check=True)
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None and set(z.namelist())=={'META/info.json','WAD/Briar.wad.client'}
 wad=z.read('WAD/Briar.wad.client')
import struct
assert struct.unpack_from('<I',wad,268)[0]==2
hashes={f'{struct.unpack_from("<Q",wad,272+i*32)[0]:016x}' for i in range(2)};assert hashes=={'0e35941cdacaff56','9144d26d7f271649'}
w=R/'work/candidate-c02/final/Briar.wad.client';w.parent.mkdir(parents=True,exist_ok=True);w.write_bytes(wad)
unpacked=R/'work/candidate-c02/roundtrip'
subprocess.run([r'C:/Users/etqdo/Downloads/wadtools-0.5.7-windows-x64/wadtools.exe','extract','-i',str(w),'-o',str(unpacked),'--no-bin-paths'],check=True,capture_output=True)
files=list(unpacked.glob('*'));assert len(files)==2
for h,data in [('9144d26d7f271649',after),('0e35941cdacaff56',texture)]:assert next(p for p in files if p.stem==h).read_bytes()==data
result={'status':'OFFLINE PASS; RUNTIME PENDING','diagnosis':'C01 SKN v4.1 lacks mandatory 12-byte end tab; permissive writer and reader omitted it','source':'https://github.com/LeagueToolkit/league-toolkit/blob/main/crates/ltk_mesh/src/skinned/mod.rs','C01':before_info,'C02':after_info,'native_footer':footer.hex(),'changed_bytes':'append 12 zero bytes only','geometry_weights_uv_normals_unchanged':True,'texture_unchanged':True,'reused_pose_evidence':'evidence/pose_validation.json applies to byte-identical geometry payload','package_crc_and_roundtrip':'PASS','package_sha256':sha(out.read_bytes()),'model_sha256':sha(after),'package_bytes':out.stat().st_size,'package':str(out.relative_to(R))}
(R/'evidence/c02_repair_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
