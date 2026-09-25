"""Native Vorbis media replacements and isolated footstep event; no source edits."""
import sys,struct,json,hashlib,copy,subprocess,wave,io,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];sys.path.insert(0,r'C:/Users/etqdo/Documents/maya/LtMAO/src')
from LtMAO.pyRitoFile.bin import BIN,BINField,BINType,BINHasher
from LtMAO.pyRitoFile.anm import ANM
from LtMAO.pyRitoFile.helper import FNV1
T=R/'work/c05-audio-tools';P=R/'work/c05-audio-prepared';P.mkdir(exist_ok=True)
stage=R/'work/c05-audio/Briar.wad.client';bankpath=Path('ASSETS/Sounds/Wwise2016/SFX/Characters/Briar/Skins/Base')
native=R/'work/original'/bankpath;(stage/bankpath).mkdir(parents=True,exist_ok=True)
u32=lambda v:struct.pack('<I',v)
sha=lambda x:hashlib.sha256(x).hexdigest()
def chunks(raw):
 out=[];p=0
 while p<len(raw):
  tag=raw[p:p+4];n=struct.unpack_from('<I',raw,p+4)[0];assert p+8+n<=len(raw);out.append([tag,raw[p+8:p+8+n]]);p+=8+n
 assert p==len(raw);return out
def pack(parts):return b''.join(tag+u32(len(b))+b for tag,b in parts)
def objects(payload):
 count=struct.unpack_from('<I',payload)[0];p=4;out=[]
 for _ in range(count):
  kind=payload[p];n=struct.unpack_from('<I',payload,p+1)[0];data=payload[p+5:p+5+n];assert len(data)==n;out.append([kind,data]);p+=5+n
 assert p==len(payload);return out
original_events=(native/'Briar_Base_SFX_events.bnk').read_bytes();ec=chunks(original_events);hi=next(i for i,x in enumerate(ec) if x[0]==b'HIRC');objs=objects(ec[hi][1]);byid={struct.unpack_from('<I',o[1])[0]:o for o in objs}
xml=ET.parse(R/'evidence/c05_native_events.xml')
nodes={int(o.find("field[@name='ulID']").get('value')):o for o in xml.iter('object') if o.find("field[@name='ulID']") is not None}
def offset(oid,name):
 node=nodes[oid];start=int(node.find("field[@name='ulID']").get('offset'));field=next(f for f in node.iter('field') if f.get('name')==name);return int(field.get('offset'))-start
def update(oid,changes,newid=None):
 kind,raw=byid[oid];data=bytearray(raw)
 if newid:struct.pack_into('<I',data,0,newid)
 for key,value in changes.items():struct.pack_into('<I',data,offset(oid,key),value)
 return [kind,bytes(data)]
clips=[('e_release','GETOUTOFMYHOUSE, briar E.wav',None,-3,736091677,404860998),('death','Worlds smallest violin, play on death.wav',None,-9,807751399,290797096),('step','Walking squidward sound.wav',(.16,.40),-10,FNV1('RedMistBriar_Step_Media'),None)]
media={};reports=[]
for name,file,crop,peakdb,mid,soundid in clips:
 source=R/'References/Audio'/file
 with wave.open(str(source)) as w:rate=w.getframerate();arr=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,w.getnchannels()).mean(axis=1).astype(float)/32768
 if crop:arr=arr[int(crop[0]*rate):int(crop[1]*rate)]
 peak=np.max(np.abs(arr));arr*=10**(peakdb/20)/max(peak,1e-8)
 fade=min(int(.008*rate),len(arr)//4);arr[:fade]*=np.linspace(0,1,fade);arr[-fade:]*=np.linspace(1,0,fade)
 prepared=P/f'{name}_48k.wav'
 with wave.open(str(prepared),'wb') as w:w.setparams((1,2,rate,len(arr),'NONE','not compressed'));w.writeframes(np.rint(arr*32767).astype('<i2').tobytes())
 wav=P/f'{name}.wav';subprocess.run([r'C:/Users/etqdo/Downloads/LosslessCut-win-x64/resources/ffmpeg.exe','-y','-v','error','-i',str(prepared),'-ar','44100','-ac','1',str(wav)],check=True)
 wem=P/f'{name}.wem';subprocess.run([str(T/'wav2wem.exe'),'-q','4','-o',str(wem),str(wav)],check=True)
 raw=wem.read_bytes();assert raw[:4]==b'RIFF' and struct.unpack_from('<I',raw,4)[0]+8==len(raw)
 assert struct.unpack_from('<HHI',raw,20)==(65535,1,44100)
 decoded=P/f'{name}_decoded.wav';res=subprocess.run([str(T/'vgmstream/vgmstream-cli.exe'),'-o',str(decoded),str(wem)],capture_output=True,text=True,check=True)
 (R/f'evidence/c05_audio_{name}_decode.txt').write_text(res.stdout+res.stderr)
 with wave.open(str(decoded)) as w:duration=w.getnframes()/w.getframerate();assert abs(duration-len(arr)/rate)<.05
 media[mid]=raw
 if soundid:
  replacement=update(soundid,{'uInMemoryMediaSize':len(raw)});objs[objs.index(byid[soundid])]=replacement
 reports.append({'role':name,'source':str(source.relative_to(R)),'source_sha256':sha(source.read_bytes()),'crop_seconds':crop,'peak_target_dbfs':peakdb,'native_media_id':mid,'native_sound_id':soundid,'codec':'Wwise Vorbis (0xffff), mono 44100Hz; unchanged native codec plugin','decoded_duration':duration,'wem_bytes':len(raw),'wem_sha256':sha(raw)})
# New footstep event uses its own media/Sound/Action/Event. Existing W foley remains byte-identical.
ids={key:FNV1('RedMistBriar_'+key) for key in ['StepSound','StepAction','DeathStopAction']}
step_event='Play_sfx_RedMistBriar_Step';stop_event='Stop_sfx_RedMistBriar_Death'
ids['StepEvent']=FNV1(step_event);ids['DeathStopEvent']=FNV1(stop_event)
assert not (set(ids.values())&set(byid))
new_sound=update(39843996,{'sourceID':clips[2][4],'uInMemoryMediaSize':len(media[clips[2][4]]),'DirectParentID':906012877},ids['StepSound']);objs.append(new_sound)
# Action object target is a fixed native field confirmed by wwiser.
action=bytearray(byid[311803663][1]);struct.pack_into('<I',action,0,ids['StepAction']);struct.pack_into('<I',action,6,ids['StepSound']);objs.append([3,bytes(action)])
event=bytearray(byid[3087182170][1]);assert event[4]==1;struct.pack_into('<I',event,0,ids['StepEvent']);struct.pack_into('<I',event,5,ids['StepAction']);objs.append([4,bytes(event)])
stop=bytearray(byid[210751008][1]);assert stop[5]==1;struct.pack_into('<I',stop,0,ids['DeathStopAction']);struct.pack_into('<I',stop,6,441395493);objs.append([3,bytes(stop)])
se=bytearray(event);struct.pack_into('<I',se,0,ids['DeathStopEvent']);struct.pack_into('<I',se,5,ids['DeathStopAction']);objs.append([4,bytes(se)])
ec[hi][1]=u32(len(objs))+b''.join(bytes([k])+u32(len(d))+d for k,d in objs)
events_out=pack(ec);(stage/bankpath/'Briar_Base_SFX_events.bnk').write_bytes(events_out)
ac=chunks((native/'Briar_Base_SFX_audio.bnk').read_bytes());di=next(i for i,x in enumerate(ac) if x[0]==b'DIDX');da=next(i for i,x in enumerate(ac) if x[0]==b'DATA');oldmedia={mid:ac[da][1][off:off+size] for mid,off,size in struct.iter_unpack('<III',ac[di][1])};allmedia=dict(oldmedia);allmedia.update(media)
payload=bytearray();index=bytearray()
for mid,data in allmedia.items():
 payload+=bytes((-len(payload))%16);index+=struct.pack('<III',mid,len(payload),len(data));payload+=data
ac[di][1]=bytes(index);ac[da][1]=bytes(payload);audio_out=pack(ac);(stage/bankpath/'Briar_Base_SFX_audio.bnk').write_bytes(audio_out)
# Running-only short contacts. Original W audio and all original events remain untouched.
ap=Path('DATA/Characters/Briar/Animations/Skin0.bin');anim=BIN().read(str(R/'work/original'/ap));get=lambda o,h:next((f for f in o.data if f.hash==h),None)
maps=json.loads((R/'evidence/original_animation_mapping.json').read_text());reverse={Path(v).stem:k for k,v in maps.items()};changes=[]
for cliphash,clip in get(anim.entries[0],'45e122f8').data.items():
 res=get(clip,'b49f754e');resource=get(res,'0329f1d7').data if res else None;name=reverse.get(resource,'');ev=get(clip,'f598463e')
 isrespawn=ev and 'Play_sfx_Briar_Respawn3D_buffactivate' in json.dumps(ev,default=lambda o:o.__json__())
 if not name.startswith('run') and not isrespawn:continue
 if ev is None:ev=BINField(hash='f598463e',type=BINType.MAP,key_type=BINType.HASH,value_type=BINType.POINTER,data={});clip.data.append(ev)
 if isrespawn:frames=[0.];eventname=stop_event
 else:
  a=ANM().read(str(R/'References/Squidward Briar Maya/briar.wad.client/assets/Etdoan/Squidward-Briar/animations'/name));start=get(clip,'76f8ad24');end=get(clip,'bd8e2d9b');lo=float(start.data) if start else 0.;hi=float(end.data) if end else a.duration-1
  frames=[float(x) for x in np.arange(lo+5,max(lo+5,hi),15)];eventname=step_event
 for i,frame in enumerate(frames):
  key=BINHasher.raw_to_hex(f'RedMistAudio_{cliphash}_{i}');assert key not in ev.data
  ev.data[key]=BINField(type=BINType.POINTER,hash_type='9c566034',data=[BINField(hash='250cfbe1',type=BINType.F32,data=frame),BINField(hash='9d477e74',type=BINType.STRING,data=eventname),BINField(hash='d91e32ee',type=BINType.BOOL,data=False)])
 changes.append({'clip_hash':cliphash,'native_animation':name,'event':eventname,'frames':frames})
(stage/ap).parent.mkdir(parents=True,exist_ok=True);anim.write(str(stage/ap))
# Independent bank framing, DIDX spans, media byte preservation and original-object diff scope.
newobjects={struct.unpack_from('<I',d)[0]:(k,d) for k,d in objects(dict(chunks(events_out))[b'HIRC'])};changed=[i for i,(k,d) in byid.items() if newobjects[i]!=(k,d)];assert set(changed)=={404860998,290797096}
for i in changed:
 old=byid[i][1];new=newobjects[i][1];off=offset(i,'uInMemoryMediaSize');assert old[:off]==new[:off] and old[off+4:]==new[off+4:]
assert all(allmedia[i]==v for i,v in oldmedia.items() if i not in media)
report={'status':'OFFLINE BUILD; independent wwiser parse pending','clips':reports,'event_mapping':{'E':'Play_sfx_Briar_BriarEMis_missilecast (E release, not charge loop)','death':'Play_sfx_Briar_Death3D_cast','walking':step_event},'new_ids':ids,'animation_audio_additions':changes,'native_media_count':len(oldmedia),'preserved_native_media':len(oldmedia)-2,'new_media_count':1,'preserved_native_hirc_objects':len(byid)-2,'native_hirc_changes':'Only uInMemoryMediaSize for E/death sounds;5 new isolated walking/stop objects. All existing W foley unchanged.','lifecycle':'E and death one-shot; death receives explicit native stop-action at respawn; 0.24s walking contacts occur only within running clips, no looping sound and no long-clip overlap. Footstep phase is preliminary until gameplay.','outputs':{str(p.relative_to(stage)):sha(p.read_bytes()) for p in stage.rglob('*') if p.is_file()},'tool_sources':['https://github.com/pas2k/wav2wem','https://github.com/bnnm/wwiser','https://github.com/vgmstream/vgmstream'],'limits':'Engine compatibility and mix/timing await gameplay; offline independent WEM decoding is not runtime proof.'}
(R/'evidence/c05_audio_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({'media':len(media),'animation_clips':len(changes),'output_files':len(report['outputs'])}))
