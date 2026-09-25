exec(open('work/inspect_c06_r.py').read().split('out=[]')[0])
for e in b.entries:
 name=next((f.data for f in e.data if f.hash=='particleName'),'')
 if name=='Briar_Base_R_Berserk_Target_Detailed':
  for em in next(f.data for f in e.data if f.hash=='complexEmitterDefinitionData'):
   if next(f.data for f in em.data if f.hash=='emitterName')=='glowBacker':print(json.dumps(em,default=lambda o:o.__json__(),indent=1))
