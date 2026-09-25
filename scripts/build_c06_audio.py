"""Silence base Briar's native SFX/en_US VO; retain isolated custom audio slots."""
import sys,struct,json,wave,subprocess,hashlib,copy,xml.etree.ElementTree as ET
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path[:0]=[r'C:/Users/etqdo/Documents/maya/LtMAO/src',str(R/'work/c05-deps')]
from LtMAO.pyRitoFile.bin import BIN,BINField,BINType,BINHasher
from LtMAO.pyRitoFile.helper import FNV1
from LtMAO.pyRitoFile.wpk import WPK
from strict_prop import StrictPROP
P=R/'work/c06-audio-prepared';P.mkdir(exist_ok=True);T=R/'work/c05-audio-tools'
root=R/'work/c06-audio';stage=root/'Briar.wad.client';locale=root/'Briar.en_US.wad.client';locale.mkdir(parents=True,exist_ok=True)
bp=Path('ASSETS/Sounds/Wwise2016/SFX/Characters/Briar/Skins/Base');(stage/bp).mkdir(parents=True,exist_ok=True)
src=R/'work/c05-audio/Briar.wad.client';u32=lambda v:struct.pack('<I',v);sha=lambda b:hashlib.sha256(b).hexdigest()
def chunks(raw):
 out=[];p=0
 while p<len(raw):
  tag=raw[p:p+4];n=struct.unpack_from('<I',raw,p+4)[0];assert p+8+n<=len(raw);out.append([tag,raw[p+8:p+8+n]]);p+=8+n
 assert p==len(raw);return out
pack=lambda parts:b''.join(t+u32(len(b))+b for t,b in parts)
def objects(data):
 count=struct.unpack_from('<I',data)[0];p=4;out=[]
 for _ in range(count):
  typ=data[p];n=struct.unpack_from('<I',data,p+1)[0];b=data[p+5:p+5+n];assert len(b)==n;out.append([typ,b]);p+=5+n
 assert p==len(data);return out
packobj=lambda obs:u32(len(obs))+b''.join(bytes([t])+u32(len(b))+b for t,b in obs)
def fields(xmlpath):
 tree=ET.parse(xmlpath);return {int(o.find("field[@name='ulID']").get('value')):o for o in tree.iter('object') if o.find("field[@name='ulID']") is not None}
def fieldoffset(nodes,oid,name):
 n=nodes[oid];start=int(n.find("field[@name='ulID']").get('offset'));return int(next(f for f in n.iter('field') if f.get('name')==name).get('offset'))-start
silwav=P/'silence.wav'
with wave.open(str(silwav),'wb') as w:w.setparams((1,2,44100,4410,'NONE','not compressed'));w.writeframes(bytes(8820))
silwem=P/'silence.wem'
subprocess.run([str(T/'wav2wem.exe'),'-q','4','-o',str(silwem),str(silwav)],check=True);silence=silwem.read_bytes()
dec=P/'silence_decoded.wav';subprocess.run([str(T/'vgmstream/vgmstream-cli.exe'),'-o',str(dec),str(silwem)],check=True,stdout=subprocess.DEVNULL)
with wave.open(str(dec)) as w:assert not any(w.readframes(w.getnframes()))
custom={736091677:(R/'work/c05-audio-prepared/e_release.wem').read_bytes(),1477413201:(R/'work/c05-audio-prepared/step.wem').read_bytes()}
deathmedia=FNV1('RedMistBriar_Death_Media');custom[deathmedia]=(R/'work/c05-audio-prepared/death.wem').read_bytes()
# All native SFX IDs retain compatibility but carry silence, except custom E's existing slot.
ac=chunks((src/bp/'Briar_Base_SFX_audio.bnk').read_bytes());di=next(i for i,x in enumerate(ac) if x[0]==b'DIDX');da=next(i for i,x in enumerate(ac) if x[0]==b'DATA');oldmedia={mid:ac[da][1][off:off+n] for mid,off,n in struct.iter_unpack('<III',ac[di][1])};media={mid:custom.get(mid,silence) for mid in oldmedia};media.update(custom)
data=bytearray();index=bytearray()
for mid,b in media.items():data+=bytes((-len(data))%16);index+=struct.pack('<III',mid,len(data),len(b));data+=b
ac[di][1]=bytes(index);ac[da][1]=bytes(data);(stage/bp/'Briar_Base_SFX_audio.bnk').write_bytes(pack(ac))
ec=chunks((src/bp/'Briar_Base_SFX_events.bnk').read_bytes());hi=next(i for i,x in enumerate(ec) if x[0]==b'HIRC');obs=objects(ec[hi][1]);nodes=fields(R/'evidence/c05_candidate_events.xml');original={struct.unpack_from('<I',b)[0]:(t,b) for t,b in obs};maprecords=[]
for i,(typ,b) in enumerate(obs):
 oid=struct.unpack_from('<I',b)[0]
 if typ!=2:continue
 off=fieldoffset(nodes,oid,'sourceID');mid=struct.unpack_from('<I',b,off)[0]
 if mid in media:
  copyb=bytearray(b);struct.pack_into('<I',copyb,fieldoffset(nodes,oid,'uInMemoryMediaSize'),len(media[mid]));obs[i]=[typ,bytes(copyb)];maprecords.append({'sound_id':oid,'media_id':mid,'state':'custom_E' if mid==736091677 else 'custom_step' if mid==1477413201 else 'silent_native'})
ids={n:FNV1('RedMistBriar_'+n) for n in ['DeathSound','DeathPlayAction']};eventname='Play_sfx_RedMistBriar_Death';ids['DeathEvent']=FNV1(eventname);assert not(set(ids.values())&set(original))
# C05 footstep's zero-gain direct Sound path bypasses native death's -20dB container.
sound=bytearray(original[1472003245][1]);struct.pack_into('<I',sound,0,ids['DeathSound']);struct.pack_into('<I',sound,fieldoffset(nodes,1472003245,'sourceID'),deathmedia);struct.pack_into('<I',sound,fieldoffset(nodes,1472003245,'uInMemoryMediaSize'),len(custom[deathmedia]));obs.append([2,bytes(sound)])
action=bytearray(original[414678710][1]);struct.pack_into('<I',action,0,ids['DeathPlayAction']);struct.pack_into('<I',action,6,ids['DeathSound']);obs.append([3,bytes(action)])
event=bytearray(original[4288349277][1]);struct.pack_into('<I',event,0,ids['DeathEvent']);struct.pack_into('<I',event,5,ids['DeathPlayAction']);obs.append([4,bytes(event)])
for i,(typ,b) in enumerate(obs):
 if struct.unpack_from('<I',b)[0]==3211854510:
  stop=bytearray(b);struct.pack_into('<I',stop,6,ids['DeathSound']);obs[i]=[typ,bytes(stop)]
ec[hi][1]=packobj(obs);(stage/bp/'Briar_Base_SFX_events.bnk').write_bytes(pack(ec))
# Replace death's original animation sound event with explicit custom event at frame1.
ap=Path('DATA/Characters/Briar/Animations/Skin0.bin');anim=BIN().read(str(src/ap));get=lambda o,h:next((f for f in o.data if f.hash==h),None);death_changed=[]
for ch,c in get(anim.entries[0],'45e122f8').data.items():
 ev=get(c,'f598463e')
 if not ev:continue
 for eh,e in ev.data.items():
  name=get(e,'9d477e74')
  if name and name.data=='Play_sfx_Briar_Death3D_cast':
   name.data=eventname;time=get(e,'250cfbe1')
   if time:time.data=1.
   else:e.data.insert(0,BINField(hash='250cfbe1',type=BINType.F32,data=1.))
   death_changed.append({'animation_clip_hash':ch,'animation_event_hash':eh,'new_event':eventname,'frame':1})
assert len(death_changed)==1;(stage/ap).parent.mkdir(parents=True,exist_ok=True);anim.write(str(stage/ap));strict=StrictPROP((stage/ap).read_bytes()).run()
# Base en_US voice: silence every streamed media ID and disable native voice Event actions.
vp=R/'work/original-voice';wpk=WPK().read(str(vp/'d3bb103ed206538d.wpk'));vraw=(vp/'d3bb103ed206538d.wpk').read_bytes();vwems={int(w.id):silence for w in wpk.wems}
out=bytearray(vraw[:8]+u32(len(wpk.wems))+bytes(4*len(wpk.wems)));slots=[]
for i,w in enumerate(wpk.wems):
 struct.pack_into('<I',out,12+i*4,len(out));name=(str(w.id)+'.wem');slots.append(len(out));out+=u32(0)+u32(len(silence))+u32(len(name))+name.encode('utf-16-le')
for off in slots:
 struct.pack_into('<I',out,off,len(out));out+=silence
wout=locale/'d3bb103ed206538d.wpk';wout.write_bytes(out);rt=WPK().read(str(wout));assert [w.id for w in rt.wems]==[w.id for w in wpk.wems] and all(out[w.offset:w.offset+w.size]==silence for w in rt.wems)
vc=chunks((vp/'0bf1d74ba8e576a0.bnk').read_bytes());vhi=next(i for i,x in enumerate(vc) if x[0]==b'HIRC');vobs=objects(vc[vhi][1]);vnodes=fields(R/'evidence/c06_native_voice.xml');vevents=[];vvoice=[]
for i,(typ,b) in enumerate(vobs):
 oid=struct.unpack_from('<I',b)[0]
 if typ==4:vevents.append({'event_id':oid,'native_action_count':b[4]});vobs[i]=[typ,b[:4]+b'\0']
 if typ==2:
  off=fieldoffset(vnodes,oid,'sourceID');mid=struct.unpack_from('<I',b,off)[0];assert mid in vwems
  data=bytearray(b);struct.pack_into('<I',data,fieldoffset(vnodes,oid,'uInMemoryMediaSize'),len(silence));vobs[i]=[typ,bytes(data)];vvoice.append({'sound_id':oid,'media_id':mid,'state':'silent_native_voice'})
vc[vhi][1]=packobj(vobs);(locale/'0bf1d74ba8e576a0.bnk').write_bytes(pack(vc))
# Native voice audio bank contains only header/no media; unchanged, omitted.
assert (vp/'d662bd01aeaf4d7b.bnk').stat().st_size==48
replacement={'custom':{'E':{'event':'Play_sfx_Briar_BriarEMis_missilecast','media_id':736091677},'walking':{'event':'Play_sfx_RedMistBriar_Step','media_id':1477413201},'death':{'event':eventname,'media_id':deathmedia,**ids}},'native_sfx':maprecords,'native_voice':vvoice,'disabled_voice_events':vevents,'future_replacement':'Choose native event/media IDs here; replace silent media and restore the native voice Event action list when enabling a VO slot. Original banks remain work/original and work/original-voice.'}
(R/'evidence/c06_audio_replacement_map.json').write_text(json.dumps(replacement,indent=2))
report={'status':'BUILT — INDEPENDENT VALIDATION PENDING','C05_death_finding':'Native death container441395493 has MakeUpGain=-20dB, confirmed by wwiser. Plausible inaudibility contributor, not runtime-confirmed sole cause. C06 bypasses container and explicitly routes death animation frame1 to direct custom Sound.','native_SFX_media_silenced':len([i for i in oldmedia if i not in custom]),'native_VO_media_silenced':len(vwems),'native_VO_events_disabled':len(vevents),'custom_media':3,'death_route':death_changed,'death_ids':ids,'death_media':deathmedia,'death_stop':'Existing C05 respawn Stop event retargeted to new custom DeathSound.9.6second one-shot, no loop.','strict_animation_BIN':strict,'silent_wem_sha256':sha(silence),'silence_decodes_exact_zero':True,'coverage':'Active base Briar SFX and installed en_US base voice. Other skins/locales and shared map/items/summoner/UI/global sounds are outside these Briar-owned banks.','replacement_map':'evidence/c06_audio_replacement_map.json','outputs':{str(p.relative_to(root)):sha(p.read_bytes()) for p in root.rglob('*') if p.is_file()},'limits':'Custom death audibility and all muted triggers require gameplay; isolated decoding/graph validation is not an in-game result.'}
(R/'evidence/c06_audio_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({'SFX_silent':report['native_SFX_media_silenced'],'VO_silent':len(vwems),'VO_events_disabled':len(vevents),'outputs':len(report['outputs'])}))
