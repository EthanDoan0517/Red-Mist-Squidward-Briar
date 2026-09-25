"""Independent byte-layout guard, including the v2/v4 footer pyRitoFile omits.
Reference: LeagueToolkit/league-toolkit crates/ltk_mesh/src/skinned/{read,mod}.rs
"""
import struct

def inspect(data):
    magic,major,minor=struct.unpack_from('<IHH',data)
    assert magic==0x00112233 and major in (0,1,2,4) and minor==1
    offset=8; ranges=[];flags=0;stride=52;kind=0
    if major:
        count,=struct.unpack_from('<I',data,offset);offset+=4
        for _ in range(count):
            name=data[offset:offset+64].split(b'\0')[0].decode()
            vs,vc,ist,ic=struct.unpack_from('<4I',data,offset+64)
            ranges.append((name,vs,vc,ist,ic));offset+=80
        if major==4:flags,=struct.unpack_from('<I',data,offset);offset+=4
    ni,nv=struct.unpack_from('<II',data,offset);offset+=8
    if major==4:
        stride,kind=struct.unpack_from('<II',data,offset);offset+=48
        assert stride=={0:52,1:56,2:72,3:104}[kind]
    assert not flags&~3
    if flags&1:
        n,=struct.unpack_from('<H',data,offset);offset+=2+n
    assert nv<=65536 or flags&2
    vertex_end=offset+ni*2+nv*stride
    footer=12 if major>=2 else 0
    assert len(data)>=vertex_end,'Truncated vertex/index payload'
    indices=struct.unpack_from(f'<{ni}H',data,offset)
    assert ni%3==0
    for name,vs,vc,ist,ic in ranges:
        assert vs+vc<=nv and ist+ic<=ni and ic%3==0
        assert all((0<=i<vc if flags&2 else vs<=i<vs+vc) for i in indices[ist:ist+ic]),name
    return {'version':f'{major}.{minor}','vertices':nv,'indices':ni,'stride':stride,'flags':flags,'vertex_end':vertex_end,'required_bytes':vertex_end+footer,'actual_bytes':len(data),'footer_bytes':len(data)-vertex_end,'complete':len(data)==vertex_end+footer}

def require_complete(data):
    info=inspect(data)
    assert info['complete'],f"SKN truncated/extra bytes: expected {info['required_bytes']}, got {len(data)}; footer {info['footer_bytes']}/12"
    return info
