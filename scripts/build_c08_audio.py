"""C08 native event repairs and sparse native VO pools. Sources remain immutable."""
import sys,struct,json,wave,subprocess,hashlib,shutil
from pathlib import Path
import numpy as np
from audio_bank_utils import *
R=Path(__file__).resolve().parents[1];sys.path.insert(0,r'C:/Users/etqdo/Documents/maya/LtMAO/src')
from LtMAO.pyRitoFile.wpk import WPK
from LtMAO.pyRitoFile.bin import BIN
from strict_prop import StrictPROP
P=R/'work/c08-audio-prepared';P.mkdir(exist_ok=True);D=R/'work/c08-audio';T=R/'work/c05-audio-tools'
bp=Path('ASSETS/Sounds/Wwise2016/SFX/Characters/Briar/Skins/Base');hp=Path('ASSETS/Sounds/Wwise2016/SFX/Shared')
sha=lambda b:hashlib.sha256(b).hexdigest()
def save(rel,b):
 p=D/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
def bank(p):
 c=chunks(p.read_bytes());i=next(i for i,x in enumerate(c) if x[0]==b'HIRC');o=objects(c[i][1]);return c,i,{struct.unpack_from('<I',b)[0]:[t,b] for t,b in o}
def bankbytes(c,i,o):c[i][1]=packobj(list(o.values()));return pack(c)
def target(o,action,target):
 t,b=o[action];a=bytearray(b);struct.pack_into('<I',a,6,target);o[action]=[t,bytes(a)]
audio={'future':(R/'work/c07-audio-prepared/laugh.wem').read_bytes()};records=[]
for key,name in [('move','Squidward laugh 1.wav'),('scream0','Squidward scream .wav'),('scream1','squidward scream 1.wav'),('scream3','Squidward scream 3.wav')]:
 source=R/'References/Audio'/name
 with wave.open(str(source)) as w:rate=w.getframerate();a=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,w.getnchannels()).mean(axis=1)/32768
 a*=10**(-6/20)/max(np.max(abs(a)),1e-8);fade=int(rate*.008);a[:fade]*=np.linspace(0,1,fade);a[-fade:]*=np.linspace(1,0,fade)
 wav=P/(key+'_source.wav')
 with wave.open(str(wav),'wb') as w:w.setparams((1,2,rate,len(a),'NONE','not compressed'));w.writeframes(np.rint(a*32767).astype('<i2').tobytes())
 wav2=P/(key+'.wav');subprocess.run([r'C:/Users/etqdo/Downloads/LosslessCut-win-x64/resources/ffmpeg.exe','-v','error','-y','-i',str(wav),'-ar','44100',str(wav2)],check=True)
 wem=P/(key+'.wem');subprocess.run([str(T/'wav2wem.exe'),'-q','4','-o',str(wem),str(wav2)],check=True);audio[key]=wem.read_bytes()
 decoded=P/(key+'_decoded.wav');p=subprocess.run([str(T/'vgmstream/vgmstream-cli.exe'),'-o',str(decoded),str(wem)],capture_output=True,text=True,check=True);(R/f'evidence/c08_{key}_decode.txt').write_text(p.stdout+p.stderr)
 with wave.open(str(decoded)) as w:duration=w.getnframes()/w.getframerate();pcm=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2');assert abs(duration-len(a)/rate)<.02 and np.max(abs(pcm.astype(float)))<32767
 records.append(dict(role=key,source=name,source_sha256=sha(source.read_bytes()),seconds=duration,full_clip=True,wem_sha256=sha(audio[key])))
# E onset uses native OnCast. Release keeps original stop-charge action only.
src=R/'work/c07-audio/Briar.wad.client';c,i,o=bank(src/bp/'Briar_Base_SFX_events.bnk')
target(o,26936025,261100005);o[375044477]=[4,u32(375044477)+b'\1'+u32(210751008)]
# Retire C07 custom laugh start; native VO Laugh drives the clip now.
o[2023201858]=[4,u32(2023201858)+b'\0']
save(Path('Briar.wad.client')/bp/'Briar_Base_SFX_events.bnk',bankbytes(c,i,o))
save(Path('Briar.wad.client')/bp/'Briar_Base_SFX_audio.bnk',(src/bp/'Briar_Base_SFX_audio.bnk').read_bytes())
ap=Path('DATA/Characters/Briar/Animations/Skin0.bin');an=BIN().read(str(src/ap));get=lambda x,h:next((f for f in x.data if f.hash==h),None);changes=0
for cl in get(an.entries[0],'45e122f8').data.values():
 ev=get(cl,'f598463e')
 if ev:
  for e in ev.data.values():
   f=get(e,'9d477e74')
   if f and f.data=='Play_sfx_RedMistBriar_Laugh':f.data='Play_sfx_Briar_Laugh3D_buffactivate';changes+=1
assert changes==1
p=D/'Briar.wad.client'/ap;p.parent.mkdir(parents=True,exist_ok=True);an.write(str(p));strict=StrictPROP(p.read_bytes()).run()
# Every registered purchase variant shares the one existing capped Sound.
c,i,o=bank(R/'work/c07-audio/Common.wad.client'/hp/'HUD_Global_events.bnk')
shop={1989001022:246810958,1504941814:463200912,486956839:706494478,3162797915:490893084,2493453670:14565971,2673763793:95257756,329350197:1018985529}
for event,action in shop.items():target(o,action,1048964796);o[event]=[4,u32(event)+b'\1'+u32(action)]
save(Path('Common.wad.client')/hp/'HUD_Global_events.bnk',bankbytes(c,i,o));save(Path('Common.wad.client')/hp/'HUD_Global_audio.bnk',(R/'work/c07-audio/Common.wad.client'/hp/'HUD_Global_audio.bnk').read_bytes())
# Original random playlists/cadence/parent voice limit 1 are retained. Silence remains in unselected slots.
vp=R/'work/original-voice';base=R/'work/c06-audio/Briar.en_US.wad.client';c,i,o=bank(base/'0bf1d74ba8e576a0.bnk');_,_,native=bank(vp/'0bf1d74ba8e576a0.bnk');nodes=fields(R/'evidence/c06_native_voice.xml')
restored=[660848939,4037733169,2609962115,2737102358]
for event in restored:o[event]=native[event]
slots={697490069:(711994501,'future'),101406140:(952355956,'scream0'),161564829:(864556338,'scream1'),207429644:(371331112,'scream3'),60179366:(912339945,'move'),324274736:(748080020,'move')}
raw=(base/'d3bb103ed206538d.wpk').read_bytes();wpk=WPK().read(str(base/'d3bb103ed206538d.wpk'));media={w.id:raw[w.offset:w.offset+w.size] for w in wpk.wems}
for sid,(mid,key) in slots.items():
 media[mid]=audio[key];typ,b=o[sid];b=bytearray(b);struct.pack_into('<I',b,fieldoffset(nodes,sid,'uInMemoryMediaSize'),len(audio[key]));o[sid]=[typ,bytes(b)]
save(Path('Briar.en_US.wad.client')/'0bf1d74ba8e576a0.bnk',bankbytes(c,i,o));p=D/'Briar.en_US.wad.client/d3bb103ed206538d.wpk';wpk.write(str(p),[media[w.id] for w in wpk.wems])
report={'status':'BUILT; independent validation pending','clips':records,'E':'OnCast Play26936025 now targets custom release container261100005. Missile release event retains stopcharge210751008 only. Full E plays once from charge onset.','purchase':shop,'purchase_sound':1048964796,'purchase_scope':'Common HUD applies all champions; modern basic/components/legendary/mythic/upgrade plus legacy buy/upgrade. Map30 Arena separate HUD bank not overridden.','purchase_diagnosis':'C07 omitted five modern registered events; stop-before-play is not proven defective. Single Play uses existing native Sound max-instance1.','laugh':'Restored native registered VO event660848939; full14.694s future media711994501. Retired custom animation start to avoid duplicate. Exact cause of C07 custom hook failure unproven.','restored_voice_events':restored,'slots':slots,'selection':'Attack3/15 equal-weight native slots; standard movement1/17; long movement1/11. Native shuffle/avoid-repeat can change conditional odds. Parent VO cap1 preserved; game command cooldown remains inherited, no new time cooldown asserted. All remaining VO media silent.','streaming':'Native StreamType2 and plugin retained. In-memory size set to available full WEM; external WPK media span validated.','strict_animation':strict,'outputs':{str(p.relative_to(D)):sha(p.read_bytes()) for p in D.rglob('*') if p.is_file()},'runtime_gate':'E charge timing; basic/consumable/component/completed purchase and rapid buys; laugh emote; sparse attack/movement clips and native interruption; footsteps/death regression. R audio reserved.'}
(R/'evidence/c08_audio_validation.json').write_text(json.dumps(report,indent=2));(R/'evidence/c08_audio_replacement_map.json').write_text(json.dumps({'inherits':'evidence/c07_audio_replacement_map.json',**report},indent=2));print(json.dumps({'outputs':len(report['outputs']),'clips':records}))
