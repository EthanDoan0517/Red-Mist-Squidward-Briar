"""Fill native attack/movement pools with supplied laughter; retain three screams."""
import sys,struct,json,hashlib,subprocess
from pathlib import Path
from audio_bank_utils import *
R=Path(__file__).resolve().parents[1];sys.path.insert(0,r'C:/Users/etqdo/Documents/maya/LtMAO/src')
from LtMAO.pyRitoFile.wpk import WPK
D=R/'work/c09-voice/Briar.en_US.wad.client';D.mkdir(parents=True,exist_ok=True)
S=R/'work/c08-audio/Briar.en_US.wad.client';nodes=fields(R/'evidence/c06_native_voice.xml');sha=lambda b:hashlib.sha256(b).hexdigest()
bn='0bf1d74ba8e576a0.bnk';wn='d3bb103ed206538d.wpk'
parts=chunks((S/bn).read_bytes());hi=next(i for i,p in enumerate(parts) if p[0]==b'HIRC');obs=objects(parts[hi][1]);before={struct.unpack_from('<I',b)[0]:[t,b] for t,b in obs}
raw=(S/wn).read_bytes();wpk=WPK().read(str(S/wn));media={w.id:raw[w.offset:w.offset+w.size] for w in wpk.wems};oldmedia=media.copy()
laugh=(R/'work/c08-audio-prepared/move.wem').read_bytes();assert sha(laugh)=='12edaf15f1ca7ebe3c8dff6dfa8cce762dba7d1bc339809121204358cbb20384'
screams={101406140,161564829,207429644};slots={};pools={}
for oid,label,count in [(92383177,'attack',15),(936266281,'movement_standard',17),(26817330,'movement_long',11)]:
 node=nodes[oid];children=[int(f.get('value')) for f in node.iter('field') if f.get('name')=='ulChildID'];playlist=[int(f.get('value')) for f in node.iter('field') if f.get('name')=='ulPlayID'];weights=[int(f.get('value')) for f in node.iter('field') if f.get('name')=='weight'];assert len(children)==count and set(children)==set(playlist) and weights==[50000]*count
 pools[label]={'container':oid,'slots':count,'laugh_slots':count-(3 if label=='attack' else 0),'scream_slots':3 if label=='attack' else 0,'silent_slots':0,'native_avoid_repeat':int(next(f for f in node.iter('field') if f.get('name')=='wAvoidRepeatCount').get('value')),'native_weights':weights}
 for sid in children:
  mid=int(next(f for f in nodes[sid].iter('field') if f.get('name')=='sourceID').get('value'));assert int(next(f for f in nodes[sid].iter('field') if f.get('name')=='DirectParentID').get('value'))==oid
  # A modified media must not affect any other Sound; a modified Sound must not occur in another playlist.
  consumers=[k for k,n in nodes.items() if any(f.get('name')=='sourceID' and f.get('value')==str(mid) for f in n.iter('field'))];assert consumers==[sid]
  playlistowners=[k for k,n in nodes.items() if any(f.get('name')=='ulPlayID' and f.get('value')==str(sid) for f in n.iter('field'))];assert playlistowners==[oid]
  slots[sid]={'media':mid,'role':'scream' if sid in screams else 'laugh','pool':label}
  if sid not in screams:media[mid]=laugh
for index,(typ,b) in enumerate(obs):
 sid=struct.unpack_from('<I',b)[0]
 if sid in slots and sid not in screams:
  b=bytearray(b);struct.pack_into('<I',b,fieldoffset(nodes,sid,'uInMemoryMediaSize'),len(laugh));obs[index]=[typ,bytes(b)]
parts[hi][1]=packobj(obs);(D/bn).write_bytes(pack(parts));wpk.write(str(D/wn),[media[w.id] for w in wpk.wems])
# Independent framing and exact delta checks; WPK parsed without writer/library.
after={struct.unpack_from('<I',b)[0]:[t,b] for t,b in objects(dict(chunks((D/bn).read_bytes()))[b'HIRC'])};assert before.keys()==after.keys();changed={i for i in before if before[i]!=after[i]};expected={s for s,v in slots.items() if oldmedia[v['media']]!=media[v['media']]};assert changed==expected and len(changed)==38
for sid in changed:
 a=bytearray(before[sid][1]);off=fieldoffset(nodes,sid,'uInMemoryMediaSize');a[off:off+4]=u32(len(laugh));assert bytes(a)==after[sid][1]
out=(D/wn).read_bytes();assert out[:8]==b'r3d2\1\0\0\0';n=struct.unpack_from('<I',out,8)[0];assert n==164;parsed={};spans=[]
for off in struct.unpack_from('<'+str(n)+'I',out,12):
 pos,size,chars=struct.unpack_from('<III',out,off);mid=int(out[off+12:off+12+chars*2].decode('utf-16-le').removesuffix('.wem'));assert pos+size<=len(out) and mid not in parsed;parsed[mid]=out[pos:pos+size];spans.append((pos,pos+size))
assert parsed==media and all(a[1]==b[0] for a,b in zip(spans,spans[1:])) and spans[-1][1]==len(out)
assert {i for i in oldmedia if oldmedia[i]!=parsed[i]}=={slots[s]['media'] for s in changed}
for sid in slots:
 assert parsed[slots[sid]['media']] == (oldmedia[slots[sid]['media']] if sid in screams else laugh)
assert after[660848939]==before[660848939] and parsed[711994501]==oldmedia[711994501]
p=subprocess.run([sys.executable,str(R/'work/c05-audio-tools/wwiser/wwiser.py'),str(D/bn),'-d','xml','-dn',str(R/'evidence/c09_voice')],capture_output=True,text=True,check=True);(R/'evidence/c09_voice_parse.txt').write_text(p.stdout+p.stderr)
import xml.etree.ElementTree as ET
assert not list(ET.parse(R/'evidence/c09_voice.xml').iter('error'))
report={'status':'PASS OFFLINE; GAMEPLAY PENDING','baseline':'C08 en_US voice','outputs':{p.name:sha(p.read_bytes()) for p in D.iterdir() if p.is_file()},'changed_Sounds':sorted(changed),'changed_media_count':38,'WPK_media_count':164,'native_pool_objects_actions_events_unchanged':True,'all_changed_media_single_consumer':True,'pools':pools,'slots':slots,'audio':'Reuse independently decoded full6.122562s Squidward laugh1; no new conversion or source edits. Three prior scream clips and future emote unchanged.','rates':'Eligible attack selections:12/15 laugh(80%),3/15 scream(20%). Both movement pools100%laugh. Native shuffle/avoid-repeat produces correlated selections; these are pool shares, not independent per-hit probabilities.','limits':'Native command cadence and voice parent max1/killNewest retained. New VO may be rejected while a full clip plays. No guaranteed every-step/every-hit trigger, no engine cooldown reduction.','preserved':'Only two en_US voice files produced. Future emote, all other voice slots/events, native pool cadence, E/steps/death/R-reserved and all visuals untouched.'}
(R/'evidence/c09_voice_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({'status':report['status'],'changed':len(changed),'files':2,'attack_laugh':'80%','movement_laugh':'100%'}))
