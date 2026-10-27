#!/usr/bin/env python3
"""Independent, read-only container/CRC inventory of every held OpenWrt .bin."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
import zlib

ROOT = Path(__file__).resolve().parents[2]
RECEIPT = 'artifacts/autoresearch/stage264a_all_firmware_crc32_verification_receipt.json'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def crc(data):
    return zlib.crc32(data) & 0xffffffff


def u32(data, offset):
    require(0 <= offset <= len(data)-4, 'truncated_integer')
    return struct.unpack_from('>I', data, offset)[0]


def uimage(data):
    require(len(data) >= 64 and data[:4] == bytes.fromhex('27051956'), 'uImage_magic')
    size = u32(data, 12)
    require(0 < size <= len(data)-64, 'uImage_size')
    require(crc(data[:4]+b'\0'*4+data[8:64]) == u32(data, 4), 'uImage_header_crc32')
    require(crc(data[64:64+size]) == u32(data, 24), 'uImage_data_crc32')
    return {'size': size, 'header_crc32': True, 'data_crc32': True}


def squashfs(data, offset):
    require(offset >= 0 and offset+96 <= len(data) and data[offset:offset+4] == b'hsqs', 'hsqs_superblock_missing')
    sb = data[offset:offset+96]
    block = struct.unpack_from('<I', sb, 12)[0]
    compression, block_log = struct.unpack_from('<HH', sb, 20)
    major, minor = struct.unpack_from('<HH', sb, 28)
    used = struct.unpack_from('<Q', sb, 40)[0]
    require(major == 4 and minor == 0 and block >= 4096 and block <= 1048576 and block & (block-1) == 0,
            'hsqs_version_or_block_size')
    require(96 <= used <= len(data)-offset, 'hsqs_bytes_used_bounds')
    require(1 <= compression <= 6 and block_log == block.bit_length()-1, 'hsqs_compression_or_block_log')
    return {'offset': offset, 'bytes_used': used, 'block_size': block,
            'compression_id': compression, 'block_log': block_log,
            'crc32': 'NOT_PRESENT_IN_SQUASHFS_FORMAT', 'decompression_verified': False}


def strict_pairs(pairs):
    obj = {}
    for key, value in pairs:
        require(key not in obj, 'FWx0_duplicate_JSON_key')
        obj[key] = value
    return obj


def invalid_constant(value):
    raise ValueError('FWx0_nonfinite_JSON_constant:'+value)


def trailers(data):
    end, rows = len(data), []
    while end >= 16 and data[end-16:end-12] == b'FWx0':
        require(len(rows) < 8, 'too_many_FWx0_trailers')
        magic, stored, kind, pad, size = struct.unpack_from('>4sIB3sI', data, end-16)
        require(16 <= size <= end and pad == b'\0'*3 and kind in (0, 1), 'FWx0_length_kind_pad')
        require(crc(data[:end-16]) ^ 0xffffffff == stored, 'FWx0_crc32')
        row = {'kind': kind, 'size': size, 'crc32': True}
        if kind == 1:
            payload = data[end-size:end-16]
            require(payload[:8] == b'\0'*8, 'FWx0_metadata_prefix')
            meta = json.loads(payload[8:], object_pairs_hook=strict_pairs, parse_constant=invalid_constant)
            # parse_constant does not catch exponent overflow such as 1e999.
            try:
                json.dumps(meta, allow_nan=False)
            except ValueError as exc:
                raise ValueError('FWx0_nonfinite_JSON_number') from exc
            require(isinstance(meta, dict), 'FWx0_metadata_object')
            row['supported_devices'] = meta.get('supported_devices', [])
        rows.append(row)
        end -= size
    if rows:
        require([r['kind'] for r in rows] in ([0, 1], [1]), 'FWx0_order')
    return data[:end], rows


def inspect_image(data):
    body, fw = trailers(data)
    result = {'FWx0': fw, 'authentication_verified': False}
    if body[:4] == b'OPEN':
        require(len(body) >= 268 and crc(body[:260]) == u32(body, 260) and body[264:268] == b'\0'*4,
                'OPEN_header_crc32_or_padding')
        pos, parts = 268, []
        for expected in (b'kernel', b'rootfs'):
            header = body[pos:pos+56]
            require(len(header) == 56 and header[:4] == b'PART' and header[4:20].rstrip(b'\0') == expected,
                    'PART_name_or_order')
            size, capacity = struct.unpack_from('>II', header, 48)
            end = pos+56+size
            require(0 < size <= capacity and end+8 <= len(body), 'PART_bounds')
            require(crc(body[pos:end]) == u32(body, end) and body[end+4:end+8] == b'\0'*4, 'PART_crc32_or_padding')
            parts.append({'name': expected.decode(), 'size': size, 'capacity': capacity,
                          'crc32': True, 'data': body[pos+56:end]})
            pos = end+8
        suffix = body[pos:]
        if suffix[:4] == b'ENDS':
            require(suffix == b'ENDS'+b'\0'*260, 'ENDS_placeholder_structure')
            result['ENDS'] = {'structure': True, 'crc32': 'NOT_PRESENT', 'rsa_signature': 'ZERO_PLACEHOLDER_NOT_AUTHENTICATED'}
        else:
            require(len(suffix) == 12 and suffix[:4] == b'END.' and crc(body[:pos]) == u32(suffix, 4)
                    and suffix[8:] == b'\0'*4, 'END_dot_crc32_or_structure')
            result['END.'] = {'crc32': True}
        payload = b''.join(p['data'] for p in parts)
        kernel = uimage(payload)
        # WA splits PARTkernel at 1 MiB, inside the larger uImage. Reassemble
        # the flash payload before using the kernel's declared aligned end.
        sq = squashfs(payload, (64+kernel['size']+0xffff) & ~0xffff)
        result.update(format='OPEN_factory', OPEN={'crc32': True},
                      partitions=[{k:v for k,v in p.items() if k != 'data'} for p in parts],
                      uImage=kernel, hsqs=sq, status='VERIFIED_CONTAINER')
    elif body[:4] == bytes.fromhex('27051956'):
        kernel = uimage(body)
        end = 64+kernel['size']
        if end == len(body):
            require(not fw, 'initramfs_with_unexpected_metadata')
            result.update(format='uImage_kernel_only', uImage=kernel, hsqs='NOT_APPLICABLE', status='VERIFIED_KERNEL_ONLY')
        else:
            # OpenWrt append-rootfs aligns to 64 KiB; validate exact boundary.
            offset = (end+0xffff) & ~0xffff
            sq = squashfs(body, offset)
            require(body[-4:] == bytes.fromhex('deadc0de') and (len(body)-4) % 65536 == 0,
                    'sysupgrade_jffs2_padding')
            require(fw, 'sysupgrade_FWx0_missing')
            result.update(format='uImage_sysupgrade', uImage=kernel, hsqs=sq, status='VERIFIED_CONTAINER')
    else:
        raise ValueError('UNSUPPORTED_FORMAT_'+body[:4].hex())
    return result


def audit(root=ROOT):
    root = Path(root).resolve()
    rows = []
    for path in sorted((root/'firmware/openwrt').rglob('*')):
        if not path.is_file() or path.suffix.lower() != '.bin':
            continue
        row = {'path': path.relative_to(root).as_posix()}
        try:
            require(not path.is_symlink() and path.resolve().is_relative_to(root/'firmware/openwrt'), 'external_link')
            require(path.stat().st_size <= 64*1024*1024, 'size_limit_64MiB')
            data = path.read_bytes()
            row.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
            row.update(inspect_image(data))
        except (OSError, ValueError, struct.error) as exc:
            row.update(status='FAILED_OR_UNSUPPORTED', error=str(exc))
        rows.append(row)
    counts = dict(Counter(row['status'] for row in rows))
    return {'stage':'264A', 'task_id':'T-S264A-ALL-FIRMWARE-CRC', 'static_sources':rows,
            'summary':{'images':len(rows), 'bytes':sum(r.get('bytes',0) for r in rows), 'statuses':counts},
            'compliant':bool(rows) and not counts.get('FAILED_OR_UNSUPPORTED'),
            'boundary':{'local_read_only':True,'hardware_access':False,'signature_verification':False,
                        'sha256_is_inventory_not_trusted_upstream_authentication':True},
            'format_source':'https://github.com/openwrt/firmware-utils/blob/master/src/mkfwimage.c'}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=ROOT)
    p.add_argument('--output',type=Path)
    args=p.parse_args(argv)
    result=audit(args.root)
    output=args.output or args.root/RECEIPT
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result['summary']))
    return 0 if result['compliant'] else 1


if __name__=='__main__':
    raise SystemExit(main())
