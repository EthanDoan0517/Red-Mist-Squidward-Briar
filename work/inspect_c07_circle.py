exec(open('work/inspect_c06_r.py').read().split('out=[]')[0])
for e in b.entries:
 name=next((f.data for f in e.data if f.hash=='particleName'),'')
 if name in ['Briar_Base_R_warning','Briar_Base_R_AoE']:
  print('\n',name)
  for em in next(f.data for f in e.data if f.hash=='complexEmitterDefinitionData'):
   print([(f.hash,json.loads(json.dumps(f,default=lambda o:o.__json__()))['data']) for f in em.data if f.hash in ['emitterName','texture','birthScale0','particleLifetime','lifetime','primitive']])
