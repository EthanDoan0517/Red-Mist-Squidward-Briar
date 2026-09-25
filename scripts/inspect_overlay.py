from pathlib import Path
import struct,json,hashlib
paths={'original':Path(r'C:/Riot Games/League of Legends/Game/DATA/FINAL/Champions/Briar.wad.client'),'overlay':Path(r'C:/Users/etqdo/Downloads/cslol-go/profiles/Clash Lightning v1/overlay/DATA/FINAL/Champions/Briar.wad.client')}
d={}
for name,p in paths.items():
 b=p.read_bytes();n=struct.unpack_from('<I',b,268)[0]; entries={struct.unpack_from('<Q',b,272+i*32)[0]:b[272+i*32:304+i*32] for i in range(n)};d[name]=entries
 print(name,'bytes',len(b),'version',list(b[:4]),'entries',n,'skinbin',0xf279b76afd0f0a62 in entries)
print('missing',len(set(d['original'])-set(d['overlay'])),'extra',len(set(d['overlay'])-set(d['original'])))
print('changed_checksums',[f'{h:016x}' for h in d['original'].keys() & d['overlay'].keys() if d['original'][h][24:]!=d['overlay'][h][24:]])
