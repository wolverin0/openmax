# PUBLIC_REDACTED_DERIVATIVE; historical source_sha256=78cf7eda76bb8377f95044254b82155a80af190d9d9ca16f155ad76a250aabcc
"""Public metadata contract only; PRIVATE_NATIVE_REPLAY_NOT_EXECUTED.

Original historical tests remain local and are not reproduced by this test.
"""
import json
from pathlib import Path

def test_public_projection_metadata_contract():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / 'projection_manifest.json').read_text())
    row = next(x for x in manifest['files'] if x['path'] == 'tests/test_stage879a.py')
    assert row['original_sha256'] == '78cf7eda76bb8377f95044254b82155a80af190d9d9ca16f155ad76a250aabcc'
    assert row['test_scope'] == 'PUBLIC_METADATA_CONTRACT_NOT_NATIVE_REPLAY'
    assert manifest['physical_acceptance'] == 'NOT_ACCEPTED'
    assert manifest['network_access'] is False
