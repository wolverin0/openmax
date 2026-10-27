"""Disposable offline projection contracts; no historical/native replay."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import socket

import pytest

from tools.verify import stage911_916_public_projection as p


@pytest.fixture
def fixture_repo(tmp_path):
    address = '10.0.0.1'
    device = ':'.join(['aa','bb','cc','dd','ee','01'])
    files = {
        'tools/example.py': '''import socket as wire
def pure(values):
    return sum(x*x for x in values)
def capture(host):
    return wire.create_connection((host,22))
def credential():
    raise AssertionError('private provider must never run')
ADDRESS='{address}'
DEVICE='{device}'
'''.format(address=address,device=device),
        'docs/STAGE879A_EXAMPLE.md': f'<!-- doc-head: Original -->\n<!-- /doc-head -->\nIdentity {address} {device} PRIVATE_CUSTOMER\n',
        'artifacts/autoresearch/example.json': json.dumps({'status': 'FAILED', 'source_bindings': [{'sha256': 'a'*64}], 'topology': {device: address, device.upper(): 'PRIVATE_CUSTOMER'}, 'stdout': 'PRIVATE_CAPTURE_BODY'}),
        'tests/test_stage879a.py': "raise AssertionError('private replay requires absent evidence')\n",
    }
    for label, body in files.items():
        target = tmp_path / label
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body)
    local = tmp_path / '.git/stage911_916'
    local.mkdir(parents=True)
    (local/'publication_plan.json').write_text(json.dumps({'primary_paths': list(files), 'file_inventory': []}))
    policy = tmp_path / '.git/stage826a/private_terms.json'
    policy.parent.mkdir(parents=True)
    policy.write_text(json.dumps(['PRIVATE_CUSTOMER']))
    return tmp_path, files


def test_projection_preserves_algorithm_blocks_capabilities_and_originals(fixture_repo, monkeypatch):
    root, originals = fixture_repo
    monkeypatch.setattr(socket, 'create_connection', lambda *a, **k: pytest.fail('socket attempted'))
    report = p.build(root)
    assert report['status'] == 'PREPARED'
    output = root/'.git/stage911_916/public_projection'
    spec = importlib.util.spec_from_file_location('public_fixture', output/'tools/example.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.pure([2, -3, 0]) == 13
    for action in [lambda: module.capture(None), module.credential]:
        with pytest.raises(RuntimeError, match='PUBLIC_TRANSPORT_OR_CREDENTIAL_DISABLED'):
            action()
    for label, original in originals.items():
        assert (root/label).read_text() == original
    assert report['network_access'] is False
    assert report['native_replay_executed'] is False
    assert (output/'pytest.ini').read_text() == '[pytest]\npythonpath = .\ntestpaths = tests\n'


def test_global_aliases_receipt_status_hashes_and_test_scope(fixture_repo):
    root, originals = fixture_repo
    report = p.build(root)
    output = root/'.git/stage911_916/public_projection'
    code = (output/'tools/example.py').read_text()
    doc = (output/'docs/STAGE879A_EXAMPLE.md').read_text()
    receipt = json.loads((output/'artifacts/autoresearch/example.json').read_text())
    address = ast.literal_eval(next(x.value for x in ast.parse(code).body if isinstance(x, ast.Assign) and x.targets[0].id == 'ADDRESS'))
    assert address in doc and address in receipt['topology'].values()
    assert len(receipt['topology']) == 2  # case-distinct identities cannot collapse keys
    assert receipt['status'] == 'FAILED'
    assert receipt['source_bindings'][0]['sha256'] == 'a'*64
    assert receipt['stdout'] == {'publication_state':'PRIVATE_CAPTURE_WITHHELD'}
    assert receipt['publication_redaction']['source_bindings'] == 'NOT_REPINNED_PRIVATE_ORIGINALS_REQUIRED'
    assert receipt['publication_redaction']['original_sha256'] == hashlib.sha256(originals['artifacts/autoresearch/example.json'].encode()).hexdigest()
    test_code = (output/'tests/test_stage879a.py').read_text()
    assert 'PRIVATE_NATIVE_REPLAY_NOT_EXECUTED' in test_code
    assert 'private replay requires absent evidence' not in test_code
    assert report['physical_acceptance'] == 'NOT_ACCEPTED'
    assert doc.count('<!-- doc-head:') == doc.count('<!-- /doc-head -->') == 1


@pytest.mark.parametrize('label', ['../escape.py', '/absolute.py', 'tools/firmware.bin'])
def test_reject_nonpublic_or_escape_sources(fixture_repo, label):
    root, _ = fixture_repo
    plan = root/'.git/stage911_916/publication_plan.json'
    plan.write_text(json.dumps({'primary_paths':[label], 'file_inventory':[]}))
    with pytest.raises(ValueError):
        p.build(root)


def test_private_provider_import_replaced_without_export(fixture_repo):
    root, _ = fixture_repo
    target = root/'tools/example.py'
    target.write_text('from controller.stage18_wmi_rate_schedule_and_sub20mhz_controller import local_path\ndef parse(data):\n return len(data)\n')
    p.build(root)
    output=root/'.git/stage911_916/public_projection'
    code=(output/'tools/example.py').read_text()
    assert 'from tools.verify.stage911_916_public_projection import projected_local_path as local_path' in code
    assert not (output/p.EXCLUDED).exists()


def test_fail_closed_duplicate_json_alias_collision_and_existing_output(fixture_repo):
    root, _ = fixture_repo
    with pytest.raises(ValueError, match='duplicate JSON'):
        p.unique_json('{"a":1,"a":2}')
    with pytest.raises(ValueError, match='alias collision'):
        p.aliases_for(['198.18.0.2'], [])
    p.build(root)
    with pytest.raises(ValueError, match='must be empty'):
        p.build(root)


def test_local_guard_rejects_remote_and_url_before_io():
    for value in [r'\\server\share\x', 'ssh://device/path', r'\\?\device']:
        with pytest.raises(ValueError):
            p.projected_local_path(value)
