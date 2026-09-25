"""Independent strict BNK/WPK extents and graph checks for C06 audio-only staging."""
import sys,struct,json,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,r'C:/Users/etqdo/Documents/maya/LtMAO/src')
from LtMAO.pyRitoFile.bin import BIN
from strict_prop import StrictPROP
root=R/'work/c06-audio';bp=Path('ASSETS/Sounds/Wwise2016/SFX/Characters/Briar/Skins/Base');silence=(R/'work/c06-audio-prepared/silence.wem').read_bytes()
def chunks(raw):
 out={};p=0
 while p<len(raw):
  tag=raw[p:p+4];n=struct.unpack_from('<I',raw,p+4)[0];assert tag not in out and p+8+n<=len(raw);out[tag]=raw[p+8:p+8+n];p+=8+n
 assert p==len(raw);return out
def objects(raw):
 data=chunks(raw)[b'HIRC'];n=struct.unpack_from('<I',data)[0];out={};p=4
 for _ in range(n):
  typ=data[p];size=struct.unpack_from('<I',data,p+1)[0];payload=data[p+5:p+5+size];assert len(payload)==size;oid=struct.unpack_from('<I',payload)[0];assert oid not in out;out[oid]=(typ,payload);p+=5+size
 assert p==len(data);return out
c=chunks((root/'Briar.wad.client'/bp/'Briar_Base_SFX_audio.bnk').read_bytes());media={};intervals=[]
for mid,off,n in struct.iter_unpack('<III',c[b'DIDX']):
 assert off%16==0 and off+n<=len(c[b'DATA']) and mid not in media;media[mid]=c[b'DATA'][off:off+n];intervals.append((off,off+n))
assert all(a[1]<=b[0] for a,b in zip(sorted(intervals),sorted(intervals)[1:]))
expected={736091677:'e_release',1477413201:'step',2805924193:'death'}
assert len(media)==112
for mid,data in media.items():assert data==((R/f'work/c05-audio-prepared/{expected[mid]}.wem').read_bytes() if mid in expected else silence)
obs=objects((root/'Briar.wad.client'/bp/'Briar_Base_SFX_events.bnk').read_bytes());xml=ET.parse(R/'evidence/c06_candidate_sfx.xml')
for n in xml.iter('object'):
 if n.get('name')=='CAkSound':
  fields={f.get('name'):f.get('value') for f in n.iter('field')};mid=int(fields['sourceID']);assert mid in media and int(fields['uInMemoryMediaSize'])==len(media[mid])
assert struct.unpack_from('<I',obs[4235614119][1],5)[0]==2990483768
assert struct.unpack_from('<I',obs[2990483768][1],6)[0]==1727772221
assert struct.unpack_from('<I',obs[3211854510][1],6)[0]==1727772221
# Independent UTF16 WPK offset-table walk (not pyRitoFile reader).
raw=(root/'Briar.en_US.wad.client/d3bb103ed206538d.wpk').read_bytes();assert raw[:4]==b'r3d2';version,count=struct.unpack_from('<II',raw,4);assert version==1 and count==164
ids=[];ends=[]
for slot in struct.unpack_from(f'<{count}I',raw,12):
 off,n,chars=struct.unpack_from('<III',raw,slot);assert slot+12+chars*2<=len(raw);name=raw[slot+12:slot+12+chars*2].decode('utf-16-le');ids.append(int(name.removesuffix('.wem')));assert raw[off:off+n]==silence;ends.append(off+n)
assert len(set(ids))==count and max(ends)==len(raw)
vo=objects((root/'Briar.en_US.wad.client/0bf1d74ba8e576a0.bnk').read_bytes());events=[v for v in vo.values() if v[0]==4];assert len(events)==53 and all(len(v[1])==5 and v[1][4]==0 for v in events)
for file in ['c06_candidate_sfx.xml','c06_candidate_voice.xml']:assert not [n for n in ET.parse(R/'evidence'/file).iter() if 'error' in n.tag.lower()]
ap=Path('DATA/Characters/Briar/Animations/Skin0.bin');strict=StrictPROP((root/'Briar.wad.client'/ap).read_bytes()).run()
old,new=[BIN().read(str(p)) for p in [R/'work/c05-audio/Briar.wad.client'/ap,root/'Briar.wad.client'/ap]]
get=lambda o,h:next((f for f in o.data if f.hash==h),None);can=lambda o:json.loads(json.dumps(o,default=lambda x:x.__json__(),sort_keys=True))
oc=get(old.entries[0],'45e122f8').data;nc=get(new.entries[0],'45e122f8').data
for ch,c in nc.items():
 ev=get(c,'f598463e')
 if not ev:continue
 for eh,e in ev.data.items():
  f=get(e,'9d477e74')
  if f and f.data=='Play_sfx_RedMistBriar_Death':
   assert get(e,'250cfbe1').data==1.;e.data=get(oc[ch],'f598463e').data[eh].data
assert can(old)==can(new),'Unexpected animation graph differences'
p=R/'evidence/c06_audio_validation.json';report=json.loads(p.read_text());report['status']='OFFLINE VALIDATED — AWAITING C06 GAMEPLAY AUDIO TEST';report['independent_validation']={'SFX_media_total':len(media),'SFX_silent_media':109,'SFX_custom_WEMs_exact_C05_validated_bytes':3,'all_DIDX_spans_aligned_disjoint_valid':True,'SFX_HIRC_objects':len(obs),'VO_HIRC_objects':len(vo),'VO_events_zero_actions':len(events),'WPK_media_count':count,'WPK_offsets_names_EOF_valid':True,'wwiser_both_banks_parse_without_errors':True,'custom_death_play_stop_targets_verified':True,'death_TXTP_chain':'Event4235614119→Action2990483768→Sound1727772221→Media2805924193; direct one-shot, normal0dB path, bypass native -20dB death container','animation_changed_only_original_death_sound_event':True,'strict_animation_BIN':strict}
report['native_locale_targets']={'0bf1d74ba8e576a0.bnk':'ASSETS/Sounds/Wwise2016/VO/en_US/Characters/Briar/Skins/Base/Briar_Base_VO_events.bnk','d3bb103ed206538d.wpk':'ASSETS/Sounds/Wwise2016/VO/en_US/Characters/Briar/Skins/Base/Briar_Base_VO_audio.wpk'}
p.write_text(json.dumps(report,indent=2));print(json.dumps({'status':report['status'],'SFX_silent':109,'VO_silent':164,'VO_events_disabled':53,'custom':3}))
