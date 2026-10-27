# PUBLIC_REDACTED_DERIVATIVE; original_sha256=e0a098735244edcdb7f7827e5a22c2bc0c7ae717f54a695fb0d2ee1fa8b63c4c
# Private originals are required for native replay.
"""Native ath10k container/SGMT composition, with absent PB070/PB080 withheld."""
from __future__ import annotations
import argparse
import dataclasses
from itertools import islice
from pathlib import Path
import struct
import sys
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.autoresearch import stage861_866_common as c
from firmware.xtensa_sgmt_surgical_patcher import SgmtContainer
OUT = ROOT / 'artifacts/autoresearch/stage879a_verified_pb070_and_pb080_native_sgmt_binaries.json'
BASE = ROOT / 'artifacts/firmware_re_xc_ltu/openwrt_qca988x_hw20_firmware_2_ct.bin'
BASE_SHA = '398e4380e7e55105f3da0f78af29d1e437404ed3a82597aa4b6daaa7dce1a38e'
MAGIC = b'QCA-ATH10K\x00\x00'
QUAD = frozenset(('PB040', 'PB050', 'PB060', 'PB070'))
PENTA = QUAD | {'PB080'}

def parse_native(blob):
    """Length-bounded, 4-byte aligned IE parsing; preserve all original bytes."""
    if len(blob) > 4 * 1024 * 1024 or not blob.startswith(MAGIC):
        raise ValueError('invalid_native_magic_or_size')
    offset, entries, seen = (12, [], set())
    while offset < len(blob):
        if offset + 8 > len(blob):
            raise ValueError('truncated_ie_header')
        ident, length = struct.unpack_from('<II', blob, offset)
        end = offset + 8 + length
        padded = end + 3 & ~3
        if ident in seen or end > len(blob) or padded > len(blob):
            raise ValueError('duplicate_or_truncated_ie')
        if any(blob[end:padded]):
            raise ValueError('nonzero_ie_padding')
        seen.add(ident)
        entries.append(dict(id=ident, payload=blob[offset + 8:end], raw=blob[offset:padded]))
        offset = padded
    if not entries or 3 not in seen:
        raise ValueError('missing_operational_ie3')
    return entries

def replace_operational(blob, sgmt):
    SgmtContainer.from_bytes(sgmt)
    entries = parse_native(blob)
    out = bytearray(MAGIC)
    for entry in entries:
        if entry['id'] != 3:
            out.extend(entry['raw'])
            continue
        out.extend(struct.pack('<II', 3, len(sgmt)))
        out.extend(sgmt)
        out.extend(bytes(-len(sgmt) % 4))
    result = bytes(out)
    parsed = parse_native(result)
    for old, new in zip(entries, parsed):
        if old['id'] != new['id'] or (old['id'] != 3 and old['raw'] != new['raw']):
            raise ValueError('metadata_or_ie_order_changed')
    return result

def validate_segment_layout(container):
    ranges = []
    for seg in container.segments:
        lo, hi = (seg.destination, seg.destination + len(seg.decoded_bytes))
        if not len(seg.decoded_bytes) or hi > 2 ** 32:
            raise ValueError('invalid_segment_extent')
        if any((lo < b and a < hi for a, b in ranges)):
            raise ValueError('overlapping_segment_va')
        ranges.append((lo, hi))
    return ranges

def apply_verified_specs(blob, expected_sha, specs, required):
    """Pure composition core. Fixture success is NOT patch-semantic approval.

    Callers must independently establish each site's semantics before publishing
    or activation. This API is not exposed as an unchecked recipe-loading CLI.
    """
    if c.sha(blob) != expected_sha:
        raise ValueError('source_sha_mismatch')
    specs = tuple(islice(specs, 65))
    if len(specs) > 64 or any((not isinstance(item, dict) for item in specs)):
        raise ValueError('invalid_or_excessive_patch_sites')
    if required not in (QUAD, PENTA) or {x.get('patch') for x in specs} != required:
        raise ValueError('incomplete_or_unexpected_patch_set')
    entries = parse_native(blob)
    original = SgmtContainer.from_bytes(next((x['payload'] for x in entries if x['id'] == 3)))
    layout = validate_segment_layout(original)
    decoded = [bytearray(seg.decoded_bytes) for seg in original.segments]
    ranges, expected_changes = ([], set())
    for spec in specs:
        idx, va = (spec['segment'], spec['va'])
        before, after = (spec['before'], spec['after'])
        if type(idx) is not int or not 0 <= idx < len(decoded) or type(va) is not int:
            raise ValueError('invalid_site')
        if not isinstance(before, bytes) or not isinstance(after, bytes) or (not before) or (len(before) != len(after)) or (before == after):
            raise ValueError('invalid_patch_lengths_or_noop')
        lo, hi = (va, va + len(before))
        if not layout[idx][0] <= lo < hi <= layout[idx][1]:
            raise ValueError('patch_outside_segment')
        if any((lo < b and a < hi for a, b in ranges)):
            raise ValueError('patch_va_collision')
        ranges.append((lo, hi))
        off = va - layout[idx][0]
        if bytes(decoded[idx][off:off + len(before)]) != before:
            raise ValueError('preimage_mismatch')
        decoded[idx][off:off + len(after)] = after
        expected_changes.update(((idx, off + i) for i, (a, b) in enumerate(zip(before, after)) if a != b))
    from firmware.xtensa_sgmt_surgical_patcher import bmi_lz_compress
    segments = tuple((dataclasses.replace(seg, decoded_bytes=bytes(decoded[i]), compressed_bytes=bmi_lz_compress(bytes(decoded[i])) if original.file_flags == 1 else bytes(decoded[i])) if bytes(decoded[i]) != seg.decoded_bytes else seg for i, seg in enumerate(original.segments)))
    changed = dataclasses.replace(original, segments=segments)
    sgmt = changed.to_bytes(recompress=False)
    parsed = SgmtContainer.from_bytes(sgmt)
    if validate_segment_layout(parsed) != layout or parsed.entry_point != original.entry_point or parsed.done_address != original.done_address:
        raise ValueError('layout_or_entry_changed')
    actual = {(i, off) for i, (a, b) in enumerate(zip(original.segments, parsed.segments)) for off, (x, y) in enumerate(zip(a.decoded_bytes, b.decoded_bytes)) if x != y}
    if actual != expected_changes:
        raise ValueError('unattributed_decoded_diff')
    native = replace_operational(blob, sgmt)
    return dict(native=native, sgmt=sgmt, collision_count=0, changed_bytes=len(actual), native_sha256=c.sha(native), sgmt_sha256=c.sha(sgmt), semantics_approved=False)

def inspect_base(blob, expected_sha):
    if c.sha(blob) != expected_sha:
        raise ValueError('source_sha_mismatch')
    ies = parse_native(blob)
    sgmt = next((item['payload'] for item in ies if item['id'] == 3))
    parsed = SgmtContainer.from_bytes(sgmt)
    layout = validate_segment_layout(parsed)
    if replace_operational(blob, sgmt) != blob:
        raise ValueError('native_roundtrip_changed_bytes')
    return dict(container_sha256=c.sha(blob), container_bytes=len(blob), operational_sgmt_sha256=c.sha(sgmt), native_roundtrip_exact=True, segment_va_collision_count=0, ie_inventory=[dict(id=x['id'], bytes=len(x['payload']), sha256=c.sha(x['payload'])) for x in ies], segments=[dict(index=i, start=lo, end=hi) for i, (lo, hi) in enumerate(layout)], entry_point=parsed.entry_point)

def build(source=BASE, expected_sha=BASE_SHA):
    source = Path(source)
    base = inspect_base(source.read_bytes(), expected_sha)
    inputs = [c.pin(source)]
    availability = {}
    for label, name in [('PB070', 'stage806a_pb070_xtensa_rc_probe_per_sgmt_patch.json'), ('PB080', 'stage833a_pb080_xtensa_peer_tid_qdepth_sgmt_patch.json')]:
        path = ROOT / 'artifacts/autoresearch' / name
        report = c.load(path)
        inputs.append(c.pin(path))
        availability[label] = dict(reported_patch_emitted=report['summary']['patch_emitted'], executable_spec_available=False)
    return dict(schema_version=1, stage='879A', status='BLOCKED', acceptance='NOT_ACCEPTED', question='Can exact native Quad/Penta binaries be composed from verified instruction specifications?', attribution=['external controller', 'QCA firmware'], source_bindings=inputs, implementation=c.pin(__file__), analysis_dependencies=[c.pin(c.__file__), c.pin(ROOT / 'firmware/xtensa_sgmt_surgical_patcher.py')], inspected_base=base, source_kind='EXPLICIT_HASH_BOUND_NATIVE_CONTAINER', requested_firmware_5_present=source.name == 'firmware-5.bin', availability=availability, base_runtime_identity='HELD_REFERENCE_NOT_CURRENT_APPLIED_IMAGE', blockers=['PB070_RC_BEHAVIOR_AND_NATIVE_SITE_UNSPECIFIED', 'PB080_QUEUE_TARGET_AND_NATIVE_SITE_UNSPECIFIED', 'FIRMWARE_API5_COMPATIBILITY_NOT_PROVEN'], emitted_binaries=[], quad_emitted=False, penta_emitted=False, target_writes=False, quad_patch_collision_count=None, penta_patch_collision_count=None, note='Zero base-segment VA collisions is not proof of unimplemented Quad/Penta patch collisions or safety', next_action='Resolve semantics and exact native preimages/replacements, independently review, then compose and qualify RAM recovery')

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=BASE)
    parser.add_argument('--sha256', default=BASE_SHA)
    args = parser.parse_args(argv)
    result = build(args.source, args.sha256)
    c.write(OUT, result)
    print('879A BLOCKED: native baseline verified; Quad/Penta emitted=0')
    return 2
if __name__ == '__main__':
    raise SystemExit(main())
