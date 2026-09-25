exec(open('work/inspect_c06_r.py').read().split('out=[]')[0])
for e in b.entries:
 name=next((f.data for f in e.data if f.hash=='particleName'),'')
 if name in ['Briar_Base_R_warning','Briar_Base_R_AoE']:
  for em in next(f.data for f in e.data if f.hash=='complexEmitterDefinitionData'):
   en=next(f.data for f in em.data if f.hash=='emitterName')
   if en in ['Blend_FLoor','Ground_Scorch','CenterRing']:
    print(name,en,json.dumps(em,default=lambda o:o.__json__(),indent=1))
