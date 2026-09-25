exec((__import__('pathlib').Path(__file__).parent/'inspect_c06_face.py').read_text().split('b=BIN()')[0])
result=[]
for p in (R/'work/original').rglob('*.bin'):
 if len(str(p))>250:continue
 b=BIN().read(str(p))
 for e in b.entries:
  if e.type==BINHasher.raw_to_hex('StaticMaterialDef'):
   result.append({'source':str(p.relative_to(R)), 'entry':friendly(json.loads(json.dumps(e,default=lambda o:o.__json__())))})
(R/'work/c06/materials.json').write_text(json.dumps(result,indent=2));print('native material count',len(result))
for x in result:
 print(x['source'],x['entry']['hash'],[(f['hash'],f['data']) for f in x['entry']['data'] if f['hash']=='name'])
