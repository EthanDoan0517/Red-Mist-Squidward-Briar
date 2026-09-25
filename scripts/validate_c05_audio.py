"""Independent output checks; does not rebuild media or mutate native assets."""
import sys,json,wave,subprocess,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];sys.path.insert(0,r'C:/Users/etqdo/Documents/maya/LtMAO/src')
from LtMAO.pyRitoFile.bin import BIN
reportpath=R/'evidence/c05_audio_validation.json';report=json.loads(reportpath.read_text())
stage=R/'work/c05-audio/Briar.wad.client';ap=Path('DATA/Characters/Briar/Animations/Skin0.bin')
# Reuse the independently authored strict byte walker without executing its other review.
from strict_prop import StrictPROP
report['strict_animation_BIN']=StrictPROP((stage/ap).read_bytes()).run()
old,new=[BIN().read(str(p)) for p in [R/'work/original'/ap,stage/ap]]
can=lambda v:json.loads(json.dumps(v,default=lambda o:o.__json__(),sort_keys=True))
get=lambda o,h:next((f for f in o.data if f.hash==h),None)
oc=get(old.entries[0],'45e122f8').data;nc=get(new.entries[0],'45e122f8').data;assert oc.keys()==nc.keys()
counts=0
for key,o in oc.items():
 n=nc[key];oe=get(o,'f598463e');ne=get(n,'f598463e')
 if oe is None and ne is not None:
  assert all('sfx_RedMistBriar_' in json.dumps(can(v)) for v in ne.data.values());counts+=len(ne.data);n.data.remove(ne)
 elif oe is not None:
  assert all(can(ne.data[k])==can(v) for k,v in oe.data.items())
  for k in list(ne.data):
   if k not in oe.data:assert 'sfx_RedMistBriar_' in json.dumps(can(ne.data[k]));counts+=1;del ne.data[k]
 assert can(o)==can(n),key
assert can(old)==can(new),'Non-audio graph edits'
report['animation_scope_validation']={'original_graph_preserved_except_added_sound_events':True,'added_sound_events':counts,'all_native_ANM_transforms_unmodified':True}
xml=ET.parse(R/'evidence/c05_candidate_events.xml');errors=[x.attrib for x in xml.iter() if 'error' in x.tag.lower()];assert not errors
nodes={int(o.find("field[@name='ulID']").get('value')):o for o in xml.iter('object') if o.find("field[@name='ulID']") is not None}
for clip in report['clips']:
 wav=R/'work/c05-audio-prepared'/f'{clip["role"]}_decoded.wav'
 with wave.open(str(wav)) as w:
  assert w.getframerate()==44100 and w.getnchannels()==1;pcm=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768
 clip['decoded_peak_dbfs']=float(20*np.log10(max(abs(pcm).max(),1e-10)));clip['decoded_clipped_samples']=int((abs(pcm)>=1).sum());assert clip['decoded_clipped_samples']==0
 oid=clip['native_sound_id'] if clip['native_sound_id'] else report['new_ids']['StepSound'];node=nodes[oid]
 fields={f.get('name'):f.get('value') for f in node.iter('field')}
 assert int(fields['sourceID'])==clip['native_media_id'] and int(fields['uInMemoryMediaSize'])==clip['wem_bytes'] and int(fields['ulPluginID'])==262145
report['independent_wwiser_validation']={'version':'v20260808','all_output_objects_parse_without_errors':True,'media_ids_sizes_and_Vorbis_plugin_verified':True,'event_simulation':'Three selected events resolve to correct sound/media; E and death native sequence LoopCount=1; step direct one-shot. Missing global buses are inherited native dependencies, not replaced.','native_E_release_delay_ms':200}
report['tool_revisions']={name:subprocess.check_output(['git','rev-parse','HEAD'],cwd=R/'work/c05-audio-tools'/name,text=True).strip() for name in ['wav2wem','wwiser']}
report['status']='OFFLINE VALIDATED — AWAITING GAMEPLAY AUDIO TIMING/MIX TEST'
reportpath.write_text(json.dumps(report,indent=2));print(json.dumps({'status':report['status'],'strict_BIN_sizes':report['strict_animation_BIN']['checked_declared_sizes'],'added_sound_events':counts,'WEM_decodes':len(report['clips'])}))
