import struct,xml.etree.ElementTree as ET
u32=lambda v:struct.pack('<I',v)
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
def fields(path):
 tree=ET.parse(path);return {int(o.find("field[@name='ulID']").get('value')):o for o in tree.iter('object') if o.find("field[@name='ulID']") is not None}
def fieldoffset(nodes,oid,name):
 n=nodes[oid];start=int(n.find("field[@name='ulID']").get('offset'));return int(next(f for f in n.iter('field') if f.get('name')==name).get('offset'))-start
def media_read(raw):
 c=dict(chunks(raw));return {mid:c[b'DATA'][off:off+n] for mid,off,n in struct.iter_unpack('<III',c[b'DIDX'])}
def media_write(raw,replacements):
 parts=chunks(raw);media=media_read(raw);media.update(replacements);data=bytearray();idx=bytearray()
 for mid,b in media.items():data+=bytes((-len(data))%16);idx+=struct.pack('<III',mid,len(data),len(b));data+=b
 for p in parts:
  if p[0]==b'DIDX':p[1]=bytes(idx)
  if p[0]==b'DATA':p[1]=bytes(data)
 return pack(parts)
