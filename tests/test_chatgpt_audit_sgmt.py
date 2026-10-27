"""Adversarial SGMT fixtures: software validation never establishes target execution."""
from dataclasses import replace
import hashlib
from pathlib import Path
import random
import struct
import subprocess
import sys

import pytest

from firmware import xtensa_sgmt_surgical_patcher as patcher
from tools.qca988x import sgmt_container_inspector as inspector


def image(segments=((0x00983C00, b'abc123'),), flags=1, entry=0x00983C00):
    blob = bytearray(struct.pack('<II', patcher.SGMT_MAGIC_LE, flags))
    for address, data in segments:
        payload = patcher.bmi_lz_compress(data) if flags == 1 else data
        blob.extend(struct.pack('<II', address, len(data)))
        blob.extend(payload)
    blob.extend(struct.pack('<II', entry, patcher.BMI_SGMTFILE_BEGINADDR))
    blob.extend(struct.pack('<II', 0, patcher.BMI_SGMTFILE_DONE))
    return bytes(blob)


def spec(**updates):
    base = patcher.SurgicalPatchSpec('TEST', 'AUDIT', 'synthetic mutation', 'fixture_ap',
        0, 0x00983C00, b'a', b'A', {}, 'offline fixture only')
    return replace(base, **updates)


def test_raw_flag_zero_patch_stays_raw():
    container = patcher.SgmtContainer.from_bytes(image(flags=0))
    modified, receipt = patcher.SgmtSurgicalPatcher.validate_and_apply(container, spec())
    reparsed = patcher.SgmtContainer.from_bytes(modified.to_bytes(recompress=False))
    assert reparsed.file_flags == 0
    assert reparsed.segments[0].decoded_bytes == b'Abc123'
    assert reparsed.segments[0].compressed_bytes == b'Abc123'
    assert receipt['bmi_lz_roundtrip_verified'] is False


def test_duplicate_beginaddr_rejected():
    blob = image()
    malformed = blob[:-8] + struct.pack('<II', 0x00983C00, patcher.BMI_SGMTFILE_BEGINADDR) + blob[-8:]
    with pytest.raises(ValueError, match='[Dd]uplicate'):
        patcher.SgmtContainer.from_bytes(malformed)


def test_overlapping_segments_rejected():
    blob = image(((0x00983C00, b'abcdef'), (0x00983C03, b'xyz')))
    with pytest.raises(ValueError, match='[Oo]verlap'):
        patcher.SgmtContainer.from_bytes(blob)


def test_address_wrap_and_unknown_region_rejected():
    for address in (0xFFFFFFFD, 0x00000010):
        with pytest.raises(ValueError):
            patcher.SgmtContainer.from_bytes(image(((address, b'abcdef'),)))


def test_inspector_invalid_header_flags_and_trailing_bytes_rejected():
    blob = image()
    with pytest.raises(ValueError):
        inspector.parse_sgmt_container(blob[:4] + struct.pack('<I', 2) + blob[8:])
    with pytest.raises(ValueError):
        inspector.parse_sgmt_container(blob + b'trailer')


def test_inspection_retains_diagnostic_but_validation_rejects():
    diagnostic = inspector.inspect_sgmt_container(image() + b'trailer')
    assert diagnostic['exact_eof_match'] is False
    assert diagnostic['validation_passed'] is False
    with pytest.raises(ValueError):
        inspector.validate_sgmt_container(diagnostic)


@pytest.mark.parametrize('board_ok,eof_ok', [(False, True), (True, False), (True, True)])
def test_report_never_passes_bad_board_data(tmp_path, monkeypatch, board_ok, eof_ok):
    blob = image()
    board = struct.pack('<H', 2116) + b'\0' * 2114
    if board_ok:
        board = board[:2] + struct.pack('<H', 2116 ^ 0xFFFF) + board[4:]
    data = blob * len(inspector.EMBEDDED_FIRMWARE_SYMBOLS) + board
    symbols = [dict(name=name, value=i * len(blob), size=len(blob))
               for i, name in enumerate(inspector.EMBEDDED_FIRMWARE_SYMBOLS)]
    symbols.append(dict(name='raw_Data', value=len(blob) * len(inspector.EMBEDDED_FIRMWARE_SYMBOLS), size=2116))
    class FakeElf:
        def __init__(self, path):
            self.symbols = symbols
        def section_bytes(self, name):
            return data
    held = tmp_path / 'fixture.ko'; held.write_bytes(b'fixture')
    monkeypatch.setattr(inspector, 'Elf32Image', FakeElf)
    monkeypatch.setattr(inspector, 'WA_UMAC_PATH', held)
    monkeypatch.setattr(inspector, 'XC_UMAC_PATH', held)
    if not eof_ok:
        parse = inspector.parse_sgmt_container
        def diagnostic(blob):
            result = parse(blob)
            result['exact_eof_match'] = False
            return result
        monkeypatch.setattr(inspector, 'parse_sgmt_container', diagnostic)
    result = inspector.build_pb_011_sgmt_audit_report()
    assert result['status'] == ('PASSED' if board_ok and eof_ok else 'FAILED')
    assert result['board_check_passes'] is board_ok
    assert result['all_eof_match'] is eof_ok


def test_python_optimized_mode_keeps_entry_acceptance_guard():
    program = '''
import struct
from firmware.xtensa_sgmt_surgical_patcher import *
payload=bmi_lz_compress(b'abc123')
blob=struct.pack('<II',SGMT_MAGIC_LE,1)+struct.pack('<II',0x00983c00,6)+payload
blob+=struct.pack('<II',0x00984000,BMI_SGMTFILE_BEGINADDR)+struct.pack('<II',0,BMI_SGMTFILE_DONE)
container=SgmtContainer.from_bytes(blob)
spec=SurgicalPatchSpec('TEST','TEST','fixture','fixture_ap',0,0x00983c00,b'a',b'A',{},'fixture')
try:
    SgmtSurgicalPatcher.validate_and_apply(container,spec)
except (ValueError,RuntimeError):
    raise SystemExit(0)
raise SystemExit(3)
'''
    result = subprocess.run([sys.executable, '-O', '-c', program], capture_output=True)
    assert result.returncode == 0, result.stderr.decode(errors='replace')


def test_complete_identity_binding_and_mismatches():
    blob = image()
    digest = hashlib.sha256(blob).hexdigest()
    container = patcher.SgmtContainer.from_bytes(blob, image_role='fixture_ap', image_version='fixture-v1')
    bound = spec(expected_container_sha256=digest, expected_segment_base=0x00983C00,
                 expected_image_role='fixture_ap', expected_image_version='fixture-v1')
    _, receipt = patcher.SgmtSurgicalPatcher.validate_and_apply(container, bound)
    assert receipt['identity_binding_verified'] is True
    for bad in (replace(bound, expected_container_sha256='0' * 64),
                replace(bound, expected_segment_base=0x00983C10),
                replace(bound, expected_image_role='fixture_sta'),
                replace(bound, expected_image_version='fixture-v2')):
        with pytest.raises(ValueError, match='[Ii]dentity|[Hh]ash|[Rr]ole|[Vv]ersion|[Bb]ase'):
            patcher.SgmtSurgicalPatcher.validate_and_apply(container, bad)


def test_unbound_legacy_mutation_never_claims_loader_acceptance():
    _, receipt = patcher.SgmtSurgicalPatcher.validate_and_apply(patcher.SgmtContainer.from_bytes(image()), spec())
    assert receipt['identity_binding_verified'] is False
    assert receipt['target_execution'] == 'UNKNOWN'
    assert receipt['activation'] == 'BLOCKED'


def test_partial_identity_cannot_claim_bound_image():
    container = patcher.SgmtContainer.from_bytes(image())
    with pytest.raises(ValueError, match='Complete image identity'):
        patcher.SgmtSurgicalPatcher.validate_and_apply(container,
            spec(expected_container_sha256=hashlib.sha256(image()).hexdigest()))


def test_identity_binds_current_preimage_and_other_segments():
    container = patcher.SgmtContainer.from_bytes(image(), image_role='fixture_ap', image_version='fixture-v1')
    modified, _ = patcher.SgmtSurgicalPatcher.validate_and_apply(container, spec())
    bound = spec(expected_container_sha256=hashlib.sha256(image()).hexdigest(),
                 expected_segment_base=0x00983C00, expected_image_role='fixture_ap',
                 expected_image_version='fixture-v1')
    with pytest.raises(ValueError, match='identity'):
        patcher.SgmtSurgicalPatcher.validate_and_apply(modified, replace(bound, expected_orig_bytes=b'A'))


def test_bounded_parser_and_decompressor():
    with pytest.raises(ValueError):
        patcher.bmi_lz_decompress_from(b'\0a', 0, patcher.MAX_SEGMENT_BYTES + 1)
    oversized = struct.pack('<II', patcher.SGMT_MAGIC_LE, 1) + struct.pack('<II', 0x00983C00, 0x1000000)
    with pytest.raises(ValueError):
        patcher.SgmtContainer.from_bytes(oversized)


def test_independent_codec_reference_vectors():
    # Hand-encoded BCL literals, escaped marker and overlapping length/distance.
    assert patcher.bmi_lz_decompress(b'\xffABC\xff\x03\x03', 6) == b'ABCABC'
    assert patcher.bmi_lz_decompress(b'\xff\xff\x00A', 2) == b'\xffA'
    assert patcher.bmi_lz_decompress(b'\xffA\xff\x05\x01', 6) == b'AAAAAA'


def test_deterministic_truncation_fuzz_never_accepts_partial_stream():
    blob = image()
    rng = random.Random(823)
    for length in rng.sample(range(len(blob)), min(len(blob), 30)):
        with pytest.raises(ValueError):
            patcher.SgmtContainer.from_bytes(blob[:length])
