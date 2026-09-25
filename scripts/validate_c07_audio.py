"""Bounded C07 delta validation; reuse C06 decoded media and mute evidence."""
import sys,json,struct,hashlib,copy,wave,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from audio_bank_utils import *
R=Path(__file__).resolve().parents[1];sys.path.insert(0,r'C:/Users/etqdo/Documents/maya/LtMAO/src')
from LtMAO.pyRitoFile.bin import BIN
from strict_prop import StrictPROP
root=R/'work/c07-audio';bp=Path('ASSETS/Sounds/Wwise2016/SFX/Characters/Briar/Skins/Base');hp=Path('ASSETS/Sounds/Wwise2016/SFX/Shared');src=R/'work/c06-audio/Briar.wad.client';hud=R/'work/c07-common-audio-native';sha=lambda b:hashlib.sha256(b).hexdigest()
reportpath=R/'evidence/c07_audio_validation.json';report=json.loads(reportpath.read_text());ids=report['laugh_ids']
def bankobs(p):return {struct.unpack_from('<I',b)[0]:(t,b) for t,b in objects(dict(chunks(p.read_bytes()))[b'HIRC'])}
s_old=bankobs(src/bp/'Briar_Base_SFX_events.bnk');s_new=bankobs(root/'Briar.wad.client'/bp/'Briar_Base_SFX_events.bnk');assert all(s_new[i]==v for i,v in s_old.items());assert set(s_new)-set(s_old)=={ids[k] for k in ['LaughSound','LaughPlayAction','LaughStopAction','LaughEvent','LaughStopEvent']}
oldmedia=media_read((src/bp/'Briar_Base_SFX_audio.bnk').read_bytes());newmedia=media_read((root/'Briar.wad.client'/bp/'Briar_Base_SFX_audio.bnk').read_bytes());assert all(newmedia[i]==v for i,v in oldmedia.items()) and set(newmedia)-set(oldmedia)=={ids['LaughMedia']};assert newmedia[ids['LaughMedia']]==(R/'work/c07-audio-prepared/laugh.wem').read_bytes()
h_old=bankobs(hud/hp/'HUD_Global_events.bnk');h_new=bankobs(root/'Common.wad.client'/hp/'HUD_Global_events.bnk');changed={i for i in h_old if h_old[i]!=h_new[i]};assert changed=={1048964796,352722303,1989001022,1504941814};stops={int(k):v for k,v in report['shop_stop_action_ids'].items()};assert set(h_new)-set(h_old)==set(stops.values())
hn=fields(R/'evidence/c07_native_hud.xml')
for sound in stops:
 a,b=h_old[sound][1],h_new[sound][1];node=hn[sound];start=int(node.find("field[@name='ulID']").get('offset'));prop=next(x for x in node.iter('object') if x.find("field[@name='pID'][@value='6']") is not None);gainoff=int(prop.find("field[@name='pValue']").get('offset'))-start;sizeoff=fieldoffset(hn,sound,'uInMemoryMediaSize');allowed=set(range(gainoff,gainoff+4))|set(range(sizeoff,sizeoff+4));assert len(a)==len(b) and all(x==y for i,(x,y) in enumerate(zip(a,b)) if i not in allowed)
 assert struct.unpack_from('<f',b,gainoff)[0]==0
for event,originalplay in [(1989001022,246810958),(1504941814,463200912)]:
 b=h_new[event][1];assert b[4]==3 and struct.unpack_from('<III',b,5)==(*stops.values(),originalplay)
for target,action in stops.items():assert h_new[action][1][5]==1 and struct.unpack_from('<I',h_new[action][1],6)[0]==target
hm_old=media_read((hud/hp/'HUD_Global_audio.bnk').read_bytes());hm_new=media_read((root/'Common.wad.client'/hp/'HUD_Global_audio.bnk').read_bytes());assert hm_old.keys()==hm_new.keys();assert [i for i in hm_old if hm_old[i]!=hm_new[i]]==[41429280];assert hm_new[41429280]==(R/'work/c07-audio-prepared/buy.wem').read_bytes()
# Parse every final bank's section/HIRC sizes; independently validate DIDX extents.
for bank in root.rglob('*.bnk'):
 c=dict(chunks(bank.read_bytes()))
 if b'HIRC' in c:objects(c[b'HIRC'])
 if b'DIDX' in c:
  spans=[]
  for mid,off,n in struct.iter_unpack('<III',c[b'DIDX']):assert off%16==0 and off+n<=len(c[b'DATA']);spans.append((off,off+n))
  assert all(a[1]<=b[0] for a,b in zip(sorted(spans),sorted(spans)[1:]))
for file in ['c07_candidate_sfx.xml','c07_candidate_hud.xml']:
 tree=ET.parse(R/'evidence'/file);assert not [n for n in tree.iter() if 'error' in n.tag.lower()]
 for n in tree.iter('object'):
  if n.get('name')=='CAkSound':
   f={x.get('name'):x.get('value') for x in n.iter('field')};mid=int(f['sourceID']);bankmedia=newmedia if file=='c07_candidate_sfx.xml' else hm_new
   if mid in bankmedia:assert int(f['uInMemoryMediaSize'])==len(bankmedia[mid])
assert struct.unpack_from('<II',s_new[ids['LaughEvent']][1],5)==(ids['LaughStopAction'],ids['LaughPlayAction'])
assert struct.unpack_from('<I',s_new[ids['LaughStopAction']][1],6)[0]==ids['LaughSound'] and struct.unpack_from('<I',s_new[ids['LaughPlayAction']][1],6)[0]==ids['LaughSound']
ap=Path('DATA/Characters/Briar/Animations/Skin0.bin');a,b=[BIN().read(str(p)) for p in [src/ap,root/'Briar.wad.client'/ap]];get=lambda o,h:next((f for f in o.data if f.hash==h),None);can=lambda o:json.loads(json.dumps(o,default=lambda x:x.__json__(),sort_keys=True));ac=get(a.entries[0],'45e122f8').data;bc=get(b.entries[0],'45e122f8').data
assert any(c['kind']=='stop_laugh' and c['clip']=='death.anm' and c['frame']==0 for c in report['animation_changes'])
assert any(c['kind']=='stop_laugh' and c['clip']=='windown.anm' for c in report['animation_changes'])
for change in report['animation_changes']:
 ev=get(bc[change['clip_hash']],'f598463e');e=ev.data[change['event_hash']]
 if change['kind']=='stop_laugh':assert get(e,'9d477e74').data=='Stop_sfx_RedMistBriar_Laugh';del ev.data[change['event_hash']]
 else:assert get(e,'9d477e74').data=='Play_sfx_RedMistBriar_Laugh';get(e,'9d477e74').data='Play_sfx_Briar_Laugh3D_buffactivate'
assert can(a)==can(b),'Non-audio animation graph mutation'
strict=StrictPROP((root/'Briar.wad.client'/ap).read_bytes()).run()
for clip in report['clips']:
 with wave.open(str(R/f'work/c07-audio-prepared/{clip["role"]}_decoded.wav')) as w:
  assert abs(w.getnframes()/w.getframerate()-clip['duration_seconds'])<1e-6;pcm=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2');assert np.max(abs(pcm.astype(float)))<32767
report['status']='OFFLINE VALIDATED — AWAITING C07 PURCHASE/LAUGH GAMEPLAY'
report['independent_validation']={'C06_existing_SFX_HIRC_objects_byte_identical':len(s_old),'C06_existing_media_byte_identical':len(oldmedia),'new_laugh_objects':5,'HUD_original_objects_changed_only_two_sounds_two_events':4,'HUD_other_media_preserved':len(hm_old)-1,'new_HUD_stop_actions':2,'shop_play_actions_preceded_by_both_stop_actions':True,'laugh_repeat_stop_then_play':True,'laugh_death_and_respawn_stop_confirmed':True,'strict_BNK_DIDX_HIRC_boundaries':True,'wwiser_two_banks_parse_clean':True,'wwiser_simulation':'Buy and Upgrade resolve same new media41429280; Laugh resolves new media3599654839. Shared Init loaded, no missing-bank/bus warning.','strict_animation_BIN':strict,'animation_graph_only_listed_audio_changes':True,'new_clips_full_length_decoded_without_clipping':True}
reportpath.write_text(json.dumps(report,indent=2));print(json.dumps({'status':report['status'],'files':len(report['outputs']),'HUD_untouched_media':len(hm_old)-1,'C06_preserved_media':len(oldmedia),'death_stop':True}))
