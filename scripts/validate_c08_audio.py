"""Independent byte delta, native playlist, XML schema and WPK extent audit."""
import struct,json,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
from audio_bank_utils import *
R=Path(__file__).resolve().parents[1];D=R/'work/c08-audio';report=json.loads((R/'evidence/c08_audio_validation.json').read_text())
def bank(p):return {struct.unpack_from('<I',b)[0]:(t,b) for t,b in objects(dict(chunks(p.read_bytes()))[b'HIRC'])}
def wpk(p):
 b=p.read_bytes();assert b[:8]==b'r3d2\1\0\0\0';n=struct.unpack_from('<I',b,8)[0];out={};spans=[]
 for off in struct.unpack_from('<'+str(n)+'I',b,12):
  pos,size,chars=struct.unpack_from('<III',b,off);name=b[off+12:off+12+chars*2].decode('utf-16-le');mid=int(name.removesuffix('.wem'));assert pos+size<=len(b) and mid not in out;out[mid]=b[pos:pos+size];spans.append((pos,pos+size))
 assert sorted(spans)==spans and all(a[1]==c[0] for a,c in zip(spans,spans[1:])) and spans[-1][1]==len(b);return out
bp=Path('ASSETS/Sounds/Wwise2016/SFX/Characters/Briar/Skins/Base');hp=Path('ASSETS/Sounds/Wwise2016/SFX/Shared')
delta={}
for label,old,new,allowed in [
 ('sfx',R/'work/c07-audio/Briar.wad.client'/bp/'Briar_Base_SFX_events.bnk',D/'Briar.wad.client'/bp/'Briar_Base_SFX_events.bnk',{26936025,375044477,2023201858}),
 ('hud',R/'work/c07-audio/Common.wad.client'/hp/'HUD_Global_events.bnk',D/'Common.wad.client'/hp/'HUD_Global_events.bnk',set(map(int,report['purchase']))|set(report['purchase'].values())),
 ('voice',R/'work/c06-audio/Briar.en_US.wad.client/0bf1d74ba8e576a0.bnk',D/'Briar.en_US.wad.client/0bf1d74ba8e576a0.bnk',set(report['restored_voice_events'])|set(map(int,report['slots']))),
]:
 a,b=bank(old),bank(new);assert a.keys()==b.keys();changed={k for k in a if a[k]!=b[k]};assert changed<=allowed;delta[label]=sorted(changed)
 if label=='sfx':
  assert struct.unpack_from('<I',b[26936025][1],6)[0]==261100005;assert b[375044477][1]==u32(375044477)+b'\1'+u32(210751008)
  for oid in [4235614119,2990483768,1727772221,4288349277,414678710,1472003245]:assert a[oid]==b[oid]
 if label=='hud':
  for e,act in report['purchase'].items():assert b[int(e)][1]==u32(int(e))+b'\1'+u32(act) and struct.unpack_from('<I',b[act][1],6)[0]==1048964796
 if label=='voice':
  native=bank(R/'work/original-voice/0bf1d74ba8e576a0.bnk')
  for e in report['restored_voice_events']:assert b[e]==native[e]
  assert sum(t==4 and x[4]!=0 for t,x in b.values())==4
  for oid in [747847522,92383177,936266281,26817330,681473590]:assert b[oid]==native[oid]
for wad,rel in [('Briar.wad.client',bp/'Briar_Base_SFX_audio.bnk'),('Common.wad.client',hp/'HUD_Global_audio.bnk')]:assert (D/wad/rel).read_bytes()==(R/'work/c07-audio'/wad/rel).read_bytes()
a=wpk(R/'work/c06-audio/Briar.en_US.wad.client/d3bb103ed206538d.wpk');b=wpk(D/'Briar.en_US.wad.client/d3bb103ed206538d.wpk');assert a.keys()==b.keys();changed={k for k in a if a[k]!=b[k]};assert changed=={v[0] for v in report['slots'].values()}
for sid,(mid,key) in report['slots'].items():
 p=R/('work/c07-audio-prepared/laugh.wem' if key=='future' else f'work/c08-audio-prepared/{key}.wem');assert b[mid]==p.read_bytes()
xml=ET.parse(R/'evidence/c08_candidate_banks.xml');assert not list(xml.iter('error'));nodes=fields(R/'evidence/c08_candidate_banks.xml')
assert next(f for f in nodes[1048964796].iter('field') if f.get('name')=='u16MaxNumInstance').get('value')=='1'
assert next(f for f in nodes[681473590].iter('field') if f.get('name')=='u16MaxNumInstance').get('value')=='1'
# Persist exact playlist fields; default equal weighting must be confirmed, not inferred.
pools={}
for oid in [92383177,936266281,26817330]:
 pools[oid]=[(f.get('name'),f.get('value')) for f in nodes[oid].iter('field') if 'weight' in (f.get('name') or '').lower() or 'playlist' in (f.get('name') or '').lower() or f.get('name') in ['ulID','ulNumChilds','ulNumPlaylistItem']]
report.update(status='PASS — OFFLINE; GAMEPLAY PENDING',independent_checks={'exact_changed_objects':delta,'WPK_media_count':len(b),'WPK_changed_media':sorted(changed),'unselected_voice_media_unchanged':len(b)-len(changed),'SFX_HUD_media_banks_unchanged':True,'working_death_steps_objects_unchanged':True,'native_VO_parent_cap':1,'purchase_Sound_cap':1,'wwiser_schema_no_errors':True,'native_playlist_fields':pools})
(R/'evidence/c08_audio_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({'status':report['status'],'changed_objects':{k:len(v) for k,v in delta.items()},'voice_media':len(changed),'pool_fields':pools}))
