"""Disposable source fixtures; Git is modeled read-only, never add/commit/push."""
import hashlib
import socket
import subprocess

import pytest

from tools.firmware import build_stage849a_universal_wa_xc_xw_v22_release_matrix as matrix


@pytest.fixture
def source_root(tmp_path, monkeypatch):
    originals = {}
    calls = []
    for label in matrix.REQUIRED_SOURCES:
        data = ('# fixture source: ' + label + '\n').encode()
        path = tmp_path / label
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        originals[label] = data

    def git_read(root, *args):
        assert root == tmp_path
        calls.append(args)
        label = args[-1]
        if args[0] == 'cat-file':
            for raw in originals.values():
                oid = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
                if oid == args[-1]:
                    return str(len(raw)).encode() if args[1] == '-s' else raw
            raise ValueError('unknown fixture blob')
        if args[:3] == ('ls-files', '--stage', '--'):
            if label not in originals:
                return b''
            raw = originals[label]
            oid = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
            return f'100644 {oid} 0\t{label}\n'.encode()
        assert args in (('diff', '--quiet', '--', label), ('diff', '--cached', '--quiet', 'HEAD', '--', label))
        if (tmp_path / label).read_bytes() != originals[label]:
            raise ValueError('fixture source is dirty')
        return b''

    def denied(*args, **kwargs):
        raise AssertionError('No native process or network is permitted in this fixture')

    monkeypatch.setattr(matrix, 'git_read', git_read)
    monkeypatch.setattr(subprocess, 'run', denied)
    monkeypatch.setattr(subprocess, 'Popen', denied)
    monkeypatch.setattr(socket.socket, 'connect', denied)
    return tmp_path, originals, calls


def test_v22_is_a_deterministic_source_matrix_not_a_champion(source_root):
    root, originals, calls = source_root
    first = matrix.build(root)
    artifact = root / f'artifacts/autoresearch/{matrix.STEM}.json'
    before = artifact.read_bytes()
    assert matrix.build(root) == first and artifact.read_bytes() == before
    assert {row['family'] for row in first['families']} == {'WA', 'XC', 'XW'}
    assert all(row['runtime_compatibility'] == 'UNKNOWN' for row in first['families'])
    assert first['hardware_champion'] is False and first['built_firmware_images'] == 0
    assert first['proprietary_binary_bytes_packaged'] == 0
    assert first['boundary']['network_access'] is False
    assert first['device_commands_executed'] is False
    assert all(row['sha256'] == hashlib.sha256(originals[row['path']]).hexdigest() for row in first['sources'])
    assert all(row['tracked'] and row['index_clean'] and row['head_clean'] for row in first['source_git_checks'])
    assert all(row == matrix.c.snapshot(root, row['path']) for row in first['sources'])
    assert any(call[:3] == ('diff', '--cached', '--quiet') for call in calls)
    assert all(row['available'] is False for row in first['optional_references'])
    doc = (root / f'docs/{matrix.STEM.upper()}.md').read_text()
    assert len(doc.splitlines()) < 180 and doc.count('<!-- doc-head:') == doc.count('<!-- /doc-head -->') == 1
    assert not list(root.rglob('*.zip')) and not list(root.rglob('*.bin'))


def test_required_source_missing_or_tampered_fails_before_outputs(source_root):
    root, originals, _ = source_root
    path = root / matrix.REQUIRED_SOURCES[0]
    path.unlink()
    with pytest.raises(ValueError):
        matrix.build(root)
    path.write_bytes(originals[matrix.REQUIRED_SOURCES[0]] + b'# tampered\n')
    with pytest.raises(ValueError, match='dirty'):
        matrix.build(root)
    assert not (root / 'artifacts').exists()


def test_present_untracked_optional_reference_is_excluded(source_root):
    root, _, _ = source_root
    path = root / matrix.OPTIONAL_REFERENCES[0]
    path.parent.mkdir(parents=True)
    path.write_text('{"status":"CONFIRMED","runtime_compatibility":"CONFIRMED"}')
    report = matrix.build(root)
    row = next(row for row in report['optional_references'] if row['path'] == matrix.OPTIONAL_REFERENCES[0])
    assert row['available'] is False
    assert row['reason'] == 'EXCLUDED_NOT_CLEAN_TRACKED_JSON'
    assert report['compatibility_acceptance'] == 'UNKNOWN'


def test_hidden_worktree_tampering_cannot_rely_on_git_stat_cache(source_root, monkeypatch):
    root, originals, _ = source_root
    original_git = matrix.git_read
    def hidden_diff(repo, *args):
        return b'' if args[0] == 'diff' else original_git(repo, *args)
    monkeypatch.setattr(matrix, 'git_read', hidden_diff)
    label = matrix.REQUIRED_SOURCES[0]
    (root / label).write_bytes(originals[label] + b'# hidden change\n')
    with pytest.raises(ValueError, match='differs from Git blob'):
        matrix.build(root)
    assert not (root / 'artifacts').exists()


def test_read_only_git_inspection_propagates_failures(tmp_path, monkeypatch):
    class Failed:
        returncode = 1
        stdout = b''
    calls = []
    def run(args, **kwargs):
        calls.append(args)
        return Failed()
    monkeypatch.setattr(subprocess, 'run', run)
    with pytest.raises(ValueError, match='inspection'):
        matrix.git_read(tmp_path, 'diff', '--quiet', '--', 'fixture.py')
    assert calls == [['git', '-C', str(tmp_path), 'diff', '--quiet', '--', 'fixture.py']]


def test_escaping_reference_is_rejected_before_git(tmp_path, monkeypatch):
    monkeypatch.setattr(matrix, 'git_read', lambda *args: (_ for _ in ()).throw(AssertionError('Git must not run')))
    with pytest.raises(ValueError):
        matrix.clean_source(tmp_path, '../outside.py')
