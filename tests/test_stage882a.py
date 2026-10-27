# PUBLIC_REDACTED_DERIVATIVE; historical source_sha256=0effbd086ad307e0c244e5e44ecf70df7cce6d215819c6a96054bca823f7ba45
"""Public metadata contract only; PRIVATE_NATIVE_REPLAY_NOT_EXECUTED.

Original historical tests remain local and are not reproduced by this test.
"""
import json
from pathlib import Path

def test_public_projection_metadata_contract():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / 'projection_manifest.json').read_text())
    row = next(x for x in manifest['files'] if x['path'] == 'tests/test_stage882a.py')
    assert row['original_sha256'] == '0effbd086ad307e0c244e5e44ecf70df7cce6d215819c6a96054bca823f7ba45'
    assert row['test_scope'] == 'PUBLIC_METADATA_CONTRACT_NOT_NATIVE_REPLAY'
    assert manifest['physical_acceptance'] == 'NOT_ACCEPTED'
    assert manifest['network_access'] is False
