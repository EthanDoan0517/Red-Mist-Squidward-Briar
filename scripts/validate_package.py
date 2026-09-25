from pathlib import Path
import hashlib,json,zipfile,struct,subprocess
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
package=R/'output/RedMist-Squidward-Briar-C01.fantome'
with zipfile.ZipFile(package) as z:
 assert z.testzip() is None
 assert set(z.namelist())=={'META/info.json','WAD/Briar.wad.client'},z.namelist()
 wad=z.read('WAD/Briar.wad.client')
 archivewad=R/'work/final-package/Briar.wad.client';archivewad.parent.mkdir(parents=True,exist_ok=True);archivewad.write_bytes(wad)
 assert wad[:2]==b'RW'
 count=struct.unpack_from('<I',wad,268)[0];assert count==2,count
 hashes=[f'{struct.unpack_from("<Q",wad,272+i*32)[0]:016x}' for i in range(count)]
 assert set(hashes)=={'0e35941cdacaff56','9144d26d7f271649'},hashes
subprocess.run([r'C:/Users/etqdo/Downloads/wadtools-0.5.7-windows-x64/wadtools.exe','extract','-i',str(archivewad),'-o',str(R/'work/final-roundtrip')],check=True,capture_output=True)
roundtrip=list((R/'work/final-roundtrip').rglob('*'));files=[p for p in roundtrip if p.is_file()];assert len(files)==2
for hashname,source in [('0e35941cdacaff56',R/'work/candidate-c01/Briar.wad.client/0e35941cdacaff56.tex'),('9144d26d7f271649',R/'work/redmist_model.skn')]:
 dest=next(p for p in files if p.stem==hashname);assert sha(source)==sha(dest)
result={'status':'PASS','package':str(package.relative_to(R)),'sha256':sha(package),'bytes':package.stat().st_size,'zip_crc':'PASS','wad_member_count':count,'wad_hashes':hashes,'roundtrip_payload_bytes_equal':True,'scope':'model and diffuse only; native SKL, ANM, animation graph, skin BIN, VFX, audio, HUD unchanged by omission','runtime':'NOT TESTED'}
(R/'evidence/package_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
