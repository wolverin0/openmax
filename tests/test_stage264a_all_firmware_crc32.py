import struct
import zlib
import pytest
from tools.firmware.verify_all_openmax_kit_checksums_and_headers import inspect_image, audit


def crc(d): return zlib.crc32(d)&0xffffffff


def make_image():
    kernel=b'kernel fixture'
    h=bytearray(64);h[:4]=bytes.fromhex('27051956')
    struct.pack_into('>I',h,12,len(kernel));struct.pack_into('>I',h,24,crc(kernel))
    struct.pack_into('>I',h,4,crc(h))
    sq=bytearray(128);sq[:4]=b'hsqs'
    struct.pack_into('<I',sq,12,262144);struct.pack_into('<HH',sq,28,4,0)
    struct.pack_into('<HH',sq,20,4,18)
    struct.pack_into('<Q',sq,40,128)
    header=bytearray(268);header[:4]=b'OPEN';struct.pack_into('>I',header,260,crc(header[:260]))
    payload=bytes(h)+kernel
    payload=payload.ljust(65536,b'\xff')+bytes(sq)
    data=bytes(header)
    for name,payload in [(b'kernel',payload[:32]),(b'rootfs',payload[32:])]:
        ph=bytearray(56);ph[:4]=b'PART';ph[4:4+len(name)]=name
        struct.pack_into('>II',ph,48,len(payload),0x100000)
        part=bytes(ph)+payload;data+=part+struct.pack('>II',crc(part),0)
    return data+b'ENDS'+bytes(260)


def wrap(d,kind,payload):
    covered=d+payload
    return covered+struct.pack('>4sIB3sI',b'FWx0',crc(covered)^0xffffffff,kind,b'\0'*3,len(payload)+16)


def test_valid_container_and_metadata():
    d=make_image();r=inspect_image(d)
    assert r['OPEN']['crc32'] and r['hsqs']['bytes_used']==128
    assert r['ENDS']['crc32']=='NOT_PRESENT' and not r['authentication_verified']
    wrapped=wrap(wrap(d,1,b'\0'*8+b'{"supported_devices":["fixture"]}'),0,b'# fake certificate')
    assert [r['kind'] for r in inspect_image(wrapped)['FWx0']]==[0,1]


@pytest.mark.parametrize('offset',[0,10,260,268,330,-1])
def test_corruption_fails(offset):
    d=bytearray(make_image());d[offset]^=1
    with pytest.raises(ValueError):inspect_image(bytes(d))


def test_fwx0_crc_and_bounds_fail():
    d=wrap(make_image(),1,b'\0'*8+b'{}')
    bad=bytearray(d);bad[-12]^=1
    with pytest.raises(ValueError,match='FWx0_crc'):inspect_image(bad)
    bad=bytearray(d);struct.pack_into('>I',bad,len(bad)-4,len(bad)+1)
    with pytest.raises(ValueError,match='FWx0_length'):inspect_image(bad)


@pytest.mark.parametrize('metadata',[b'{"supported_devices":NaN}',b'{"x":1,"x":2}',b'{"supported_devices":1e999}'])
def test_nonstandard_metadata_rejected(metadata):
    with pytest.raises(ValueError,match='JSON'):inspect_image(wrap(make_image(),1,b'\0'*8+metadata))


@pytest.mark.parametrize('field,value',[(20,0),(22,0),(22,17)])
def test_invalid_squashfs_fields_rejected_with_correct_crcs(field,value):
    d=bytearray(make_image());pos=d.index(b'hsqs');struct.pack_into('<H',d,pos+field,value)
    header=268+56+32+8;end=pos+128;struct.pack_into('>I',d,end,crc(d[header:end]))
    with pytest.raises(ValueError,match='compression_or_block_log'):inspect_image(d)


def test_bad_rootfs_is_rejected_even_with_recomputed_partition_crc():
    d=bytearray(make_image());pos=d.index(b'hsqs');d[pos:pos+4]=b'fake'
    header=268+56+32+8;end=pos+128;struct.pack_into('>I',d,end,crc(d[header:end]))
    with pytest.raises(ValueError,match='hsqs'):inspect_image(d)


def test_inventory_never_skips_unknown_and_does_not_write_images(tmp_path):
    p=tmp_path/'firmware/openwrt/sub';p.mkdir(parents=True)
    (p/'good.bin').write_bytes(make_image());(p/'unknown.BIN').write_bytes(b'ELF!')
    result=audit(tmp_path)
    assert result['summary']['images']==2 and not result['compliant']
    assert (p/'good.bin').read_bytes()==make_image()
