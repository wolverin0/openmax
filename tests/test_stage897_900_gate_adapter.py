# PUBLIC_REDACTED_DERIVATIVE; historical source_sha256=9a95d2efb57267567a3ba91752afe9dff0ce837b730658e8bfb0007450037821
"""Public metadata contract only; PRIVATE_NATIVE_REPLAY_NOT_EXECUTED.

Original historical tests remain local and are not reproduced by this test.
"""
import json
from pathlib import Path

def test_public_projection_metadata_contract():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / 'projection_manifest.json').read_text())
    row = next(x for x in manifest['files'] if x['path'] == 'tests/test_stage897_900_gate_adapter.py')
    assert row['original_sha256'] == '9a95d2efb57267567a3ba91752afe9dff0ce837b730658e8bfb0007450037821'
    assert row['test_scope'] == 'PUBLIC_METADATA_CONTRACT_NOT_NATIVE_REPLAY'
    assert manifest['physical_acceptance'] == 'NOT_ACCEPTED'
    assert manifest['network_access'] is False
