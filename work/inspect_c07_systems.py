exec(open('work/inspect_c06_r.py').read().split('out=[]')[0])
for e in b.entries:
 n=next((f.data for f in e.data if f.hash=='particleName'),'')
 if n: print(e.hash,n)
