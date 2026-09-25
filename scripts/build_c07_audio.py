"""Full supplied purchase/laugh clips; preserve C06 audio and mute baseline."""
import sys,json,wave,hashlib,subprocess,copy,struct
from pathlib import Path
import numpy as np
from audio_bank_utils import *
R=Path(__file__).resolve().parents[1];sys.path.insert(0,r'C:/Users/etqdo/Documents/maya/LtMAO/src')
from LtMAO.pyRitoFile.bin import BIN,BINField,BINType,BINHasher
from LtMAO.pyRitoFile.helper import FNV1
from strict_prop import StrictPROP
root=R/'work/c07-audio';stage=root/'Briar.wad.client';common=root/'Common.wad.client';P=R/'work/c07-audio-prepared';P.mkdir(exist_ok=True);T=R/'work/c05-audio-tools'
bp=Path('ASSETS/Sounds/Wwise2016/SFX/Characters/Briar/Skins/Base');hp=Path('ASSETS/Sounds/Wwise2016/SFX/Shared');(stage/bp).mkdir(parents=True,exist_ok=True);(common/hp).mkdir(parents=True,exist_ok=True)
src=R/'work/c06-audio/Briar.wad.client';hud=R/'work/c07-common-audio-native';sha=lambda b:hashlib.sha256(b).hexdigest();audio={};records=[]
for name,file,channels in [('buy','becauseimalloutofmoney, whenever you buy something from the shop.wav',2),('laugh','fuuuutureeee, play during briar laugh.wav',1)]:
 source=R/'References/Audio'/file
 with wave.open(str(source)) as w:rate=w.getframerate();arr=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,w.getnchannels()).astype(float)/32768
 if channels==1:arr=arr.mean(axis=1,keepdims=True)
 arr*=10**(-6/20)/max(np.max(abs(arr)),1e-8);fade=min(int(rate*.008),len(arr)//4);arr[:fade]*=np.linspace(0,1,fade)[:,None];arr[-fade:]*=np.linspace(1,0,fade)[:,None]
 wav=P/f'{name}_48k.wav'
 with wave.open(str(wav),'wb') as w:w.setparams((channels,2,rate,len(arr),'NONE','not compressed'));w.writeframes(np.rint(arr*32767).astype('<i2').tobytes())
 converted=P/f'{name}.wav';subprocess.run([r'C:/Users/etqdo/Downloads/LosslessCut-win-x64/resources/ffmpeg.exe','-v','error','-y','-i',str(wav),'-ar','44100','-ac',str(channels),str(converted)],check=True)
 wem=P/f'{name}.wem';subprocess.run([str(T/'wav2wem.exe'),'-q','4','-o',str(wem),str(converted)],check=True);audio[name]=wem.read_bytes()
 decoded=P/f'{name}_decoded.wav';p=subprocess.run([str(T/'vgmstream/vgmstream-cli.exe'),'-o',str(decoded),str(wem)],check=True,capture_output=True,text=True);(R/f'evidence/c07_{name}_decode.txt').write_text(p.stdout+p.stderr)
 with wave.open(str(decoded)) as w:
  duration=w.getnframes()/w.getframerate();assert abs(duration-len(arr)/rate)<.02 and w.getnchannels()==channels;pcm=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2');assert not np.any(pcm==-32768)
 records.append({'role':name,'source':str(source.relative_to(R)),'source_sha256':sha(source.read_bytes()),'full_clip_preserved':True,'duration_seconds':duration,'channels':channels,'rate':44100,'Wwise_Vorbis_sha256':sha(audio[name]),'decoded_peak_dbfs':float(20*np.log10(np.max(abs(pcm.astype(float)))/32768))})
# Clone from previously verified direct custom path; isolated normal-gain Laugh.
bc=chunks((src/bp/'Briar_Base_SFX_events.bnk').read_bytes());hi=next(i for i,p in enumerate(bc) if p[0]==b'HIRC');obs=objects(bc[hi][1]);original={struct.unpack_from('<I',b)[0]:(t,b) for t,b in obs};nodes=fields(R/'evidence/c06_candidate_sfx.xml')
ids={n:FNV1('RedMistBriar_'+n) for n in ['LaughSound','LaughPlayAction','LaughStopAction','LaughMedia']};ids['LaughEvent']=FNV1('Play_sfx_RedMistBriar_Laugh');ids['LaughStopEvent']=FNV1('Stop_sfx_RedMistBriar_Laugh');assert not(set(ids.values())&set(original))
sound=bytearray(original[1727772221][1]);struct.pack_into('<I',sound,0,ids['LaughSound']);struct.pack_into('<I',sound,fieldoffset(nodes,1727772221,'sourceID'),ids['LaughMedia']);struct.pack_into('<I',sound,fieldoffset(nodes,1727772221,'uInMemoryMediaSize'),len(audio['laugh']));obs.append([2,bytes(sound)])
play=bytearray(original[2990483768][1]);struct.pack_into('<I',play,0,ids['LaughPlayAction']);struct.pack_into('<I',play,6,ids['LaughSound']);obs.append([3,bytes(play)])
stop_template=original[3211854510][1];stop=bytearray(stop_template);struct.pack_into('<I',stop,0,ids['LaughStopAction']);struct.pack_into('<I',stop,6,ids['LaughSound']);obs.append([3,bytes(stop)])
obs.append([4,u32(ids['LaughEvent'])+bytes([2])+u32(ids['LaughStopAction'])+u32(ids['LaughPlayAction'])]);obs.append([4,u32(ids['LaughStopEvent'])+bytes([1])+u32(ids['LaughStopAction'])])
bc[hi][1]=packobj(obs);(stage/bp/'Briar_Base_SFX_events.bnk').write_bytes(pack(bc));(stage/bp/'Briar_Base_SFX_audio.bnk').write_bytes(media_write((src/bp/'Briar_Base_SFX_audio.bnk').read_bytes(),{ids['LaughMedia']:audio['laugh']}))
# Shared Buy AND Upgrade use same native media; no other consumer uses this slot.
hc=chunks((hud/hp/'HUD_Global_events.bnk').read_bytes());hhi=next(i for i,p in enumerate(hc) if p[0]==b'HIRC');hobs=objects(hc[hhi][1]);hbefore=copy.deepcopy(hobs);hnodes=fields(R/'evidence/c07_native_hud.xml');shopstops={oid:FNV1(f'RedMistShop_Stop_{oid}') for oid in [1048964796,352722303]};shopgains=[]
for oid,newid in shopstops.items():
 action=bytearray(stop_template);struct.pack_into('<I',action,0,newid);struct.pack_into('<I',action,6,oid);hobs.append([3,bytes(action)])
for i,(typ,b) in enumerate(hobs):
 oid=struct.unpack_from('<I',b)[0]
 if oid in shopstops:
  data=bytearray(b);struct.pack_into('<I',data,fieldoffset(hnodes,oid,'uInMemoryMediaSize'),len(audio['buy']))
  node=hnodes[oid];start=int(node.find("field[@name='ulID']").get('offset'))
  prop=next(x for x in node.iter('object') if x.find("field[@name='pID'][@value='6']") is not None);pv=prop.find("field[@name='pValue']");shopgains.append({'sound':oid,'old_MakeUpGain':float(pv.get('value')),'new_MakeUpGain':0});struct.pack_into('<f',data,int(pv.get('offset'))-start,0.);hobs[i]=[typ,bytes(data)]
 if oid in [1989001022,1504941814]:
  assert b[4]==1 and len(b)==9;hobs[i]=[4,b[:4]+bytes([3])+b''.join(u32(v) for v in shopstops.values())+b[5:]]
hc[hhi][1]=packobj(hobs);(common/hp/'HUD_Global_events.bnk').write_bytes(pack(hc));(common/hp/'HUD_Global_audio.bnk').write_bytes(media_write((hud/hp/'HUD_Global_audio.bnk').read_bytes(),{41429280:audio['buy']}))
# Native laugh start now triggers custom event; repeat stops previous copy. Running,
# death and respawn explicitly stop the long laugh; standing still allows full clip.
ap=Path('DATA/Characters/Briar/Animations/Skin0.bin');anim=BIN().read(str(src/ap));get=lambda o,h:next((f for f in o.data if f.hash==h),None);mapping=json.loads((R/'evidence/original_animation_mapping.json').read_text());reverse={Path(v).stem:k for k,v in mapping.items()};changes=[]
for ch,c in get(anim.entries[0],'45e122f8').data.items():
 res=get(c,'b49f754e');fh=get(res,'0329f1d7').data if res else None;name=reverse.get(fh,'');events=get(c,'f598463e')
 if events:
  for eh,e in list(events.data.items()):
   event=get(e,'9d477e74')
   if event and event.data=='Play_sfx_Briar_Laugh3D_buffactivate':event.data='Play_sfx_RedMistBriar_Laugh';changes.append({'kind':'laugh_start','clip':name,'clip_hash':ch,'event_hash':eh})
 stop_needed=name.startswith('run') or name=='death.anm' or (events and 'Stop_sfx_RedMistBriar_Death' in json.dumps(events,default=lambda o:o.__json__()))
 if stop_needed:
  if not events:events=BINField(hash='f598463e',type=BINType.MAP,key_type=BINType.HASH,value_type=BINType.POINTER,data={});c.data.append(events)
  lo=get(c,'76f8ad24');frame=float(lo.data) if lo else 0.;key=BINHasher.raw_to_hex('RedMistStopLaugh_'+ch);assert key not in events.data;events.data[key]=BINField(type=BINType.POINTER,hash_type='9c566034',data=[BINField(hash='250cfbe1',type=BINType.F32,data=frame),BINField(hash='9d477e74',type=BINType.STRING,data='Stop_sfx_RedMistBriar_Laugh'),BINField(hash='d91e32ee',type=BINType.BOOL,data=False)]);changes.append({'kind':'stop_laugh','clip':name,'clip_hash':ch,'event_hash':key,'frame':frame})
assert len([c for c in changes if c['kind']=='laugh_start'])==1;(stage/ap).parent.mkdir(parents=True,exist_ok=True);anim.write(str(stage/ap));strict=StrictPROP((stage/ap).read_bytes()).run()
report={'status':'BUILT; INDEPENDENT VALIDATION PENDING','clips':records,'laugh_ids':ids,'animation_changes':changes,'shop_event_mapping':{'Play_sfx_hud_Store_Buy':{'event':1989001022,'action':246810958,'sound':1048964796,'media':41429280},'Play_sfx_hud_Store_Upgrade':{'event':1504941814,'action':463200912,'sound':352722303,'media':41429280}},'shop_stop_action_ids':shopstops,'shop_sound_gains':shopgains,'shop_hook_evidence':'Native Common.wad.client da13882526b44deb.bin explicitly declares Store_Buy and Store_Upgrade; HUD_Global banks resolve both and only these Sounds to media41429280.','scope':'Common.wad.client shared HUD store buy/upgrade changes apply to ANY champion while this mod is enabled. Sell/undo/open/close and all other HUD sounds unchanged.','preserved':'All C06 SFX/VO silences, E, steps,death bytes and native ANM motion unchanged; en_US voiceWAD inherited by parent merge.','lifecycle':'Shop actions stop both previous buy/upgrade Sounds before playing new purchase; native instance limit1 retained. Laugh event stopprevious thenplay; run/death/respawn stoplaugh; full14.694s plays if uninterrupted, no loop.','strict_animation_BIN':strict,'outputs':{str(p.relative_to(root)):sha(p.read_bytes()) for p in root.rglob('*') if p.is_file()},'gameplay_gate':'Confirm each successful purchase (component,completeditem,consumable,upgrade),rapidbuys,repeatedlaugh,run/deathinterruption,mix. Native event hooks are offline verified; runtime ordering/audibility not yet verified.'}
(R/'evidence/c07_audio_validation.json').write_text(json.dumps(report,indent=2));(R/'evidence/c07_audio_replacement_map.json').write_text(json.dumps({'inherits':'evidence/c06_audio_replacement_map.json','shop':report['shop_event_mapping'],'laugh':ids,'clips':records},indent=2));print(json.dumps({'files':len(report['outputs']),'laugh':ids,'shop_stops':shopstops}))
