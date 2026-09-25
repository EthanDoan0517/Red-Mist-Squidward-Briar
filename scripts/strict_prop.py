"""Independent strict PROP binary length validator shared by candidate reviews."""
class StrictPROP:
 def __init__(self,data):self.b=data;self.p=0;self.sizes=0;self.fields=0
 def take(self,n):
  assert 0<=n<=len(self.b)-self.p,('truncated',self.p,n)
  v=self.b[self.p:self.p+n];self.p+=n;return v
 def num(self,n):return int.from_bytes(self.take(n),'little')
 def sized(self,fn):
  n=self.num(4);start=self.p;fn();assert self.p-start==n,('length mismatch',start,n,self.p-start);self.sizes+=1
 def field(self):self.take(4);self.value(self.num(1));self.fields+=1
 def value(self,t):
  fixed={0:0,1:1,2:1,3:1,4:2,5:2,6:4,7:4,8:8,9:8,10:4,11:8,12:12,13:16,14:64,15:4,17:4,18:8,132:4,135:1}
  if t in fixed:self.take(fixed[t])
  elif t==16:self.take(self.num(2))
  elif t in (128,129):
   subtype=self.num(1);self.sized(lambda:[self.value(subtype) for _ in range(self.num(4))])
  elif t in (130,131):
   if self.num(4):self.sized(lambda:[self.field() for _ in range(self.num(2))])
  elif t==133:
   subtype=self.num(1);n=self.num(1);assert n in (0,1);[self.value(subtype) for _ in range(n)]
  elif t==134:
   key=self.num(1);val=self.num(1);self.sized(lambda:[(self.value(key),self.value(val)) for _ in range(self.num(4))])
  else:raise AssertionError(('unknown type',t,self.p))
 def run(self):
  assert self.take(4)==b'PROP';version=self.num(4);assert version==3
  for _ in range(self.num(4)):self.take(self.num(2))
  count=self.num(4);self.take(count*4)
  for _ in range(count):self.sized(lambda:(self.take(4),[self.field() for _ in range(self.num(2))]))
  assert self.p==len(self.b),('trailing data',len(self.b)-self.p)
  return {'bytes':self.p,'entries':count,'checked_declared_sizes':self.sizes,'fields':self.fields,'eof_exact':True}
