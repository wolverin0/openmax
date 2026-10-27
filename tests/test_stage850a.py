"""LTU v22 manifest software contracts, without native Git mutation or radio calls."""
import hashlib
import socket
import subprocess

import pytest

from tools.firmware import build_stage850a_ltu_safe_kit_v22_atpc_and_dfs_guard as kit


@pytest.fixture
def source_root(tmp_path, monkeypatch):
    originals = {}
    for label in kit.REQUIRED_SOURCES:
        data = ('# fixture LTU source: ' + label + '\n').encode()
        path = tmp_path / label
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        originals[label] = data

    def git_read(root, *args):
        assert root == tmp_path
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
        if (root / label).read_bytes() != originals[label]:
            raise ValueError('fixture source is dirty')
        return b''

    def denied(*args, **kwargs):
        raise AssertionError('Native process or network action is forbidden')

    monkeypatch.setattr(kit.matrix, 'git_read', git_read)
    monkeypatch.setattr(subprocess, 'run', denied)
    monkeypatch.setattr(subprocess, 'Popen', denied)
    monkeypatch.setattr(socket.socket, 'connect', denied)
    return tmp_path, originals


def test_ltu_v22_is_deterministic_with_unknown_features(source_root):
    root, originals = source_root
    first = kit.build(root)
    artifact = root / f'artifacts/autoresearch/{kit.STEM}.json'
    before = artifact.read_bytes()
    assert kit.build(root) == first and artifact.read_bytes() == before
    assert first['artifact_type'] == 'SOURCE_SAFE_KIT_MANIFEST'
    assert all(row['status'] == 'UNKNOWN' and row['activation_available'] is False for row in first['features'].values())
    assert first['guard_policy']['actions_dispatched'] == 0
    assert first['guard_policy']['atpc_enable'] is False and first['guard_policy']['dfs_disable'] is False
    assert first['physical_acceptance'] == 'UNKNOWN'
    assert first['device_commands_executed'] is False
    assert first['proprietary_binary_bytes_packaged'] == 0
    assert all(row['sha256'] == hashlib.sha256(originals[row['path']]).hexdigest() for row in first['sources'])
    assert all(row == kit.matrix.c.snapshot(root, row['path']) for row in first['sources'])
    assert all(not row['available'] for row in first['optional_references'])
    assert not list(root.rglob('*.zip')) and not list(root.rglob('*.bin'))
    text = (root / f'docs/{kit.STEM.upper()}.md').read_text()
    assert len(text.splitlines()) < 180 and text.count('<!-- doc-head:') == text.count('<!-- /doc-head -->') == 1


def test_required_ltu_sources_cannot_be_missing_or_tampered(source_root):
    root, originals = source_root
    label = kit.REQUIRED_SOURCES[0]
    path = root / label
    path.unlink()
    with pytest.raises(ValueError):
        kit.build(root)
    path.write_bytes(originals[label] + b'# changed\n')
    with pytest.raises(ValueError, match='dirty'):
        kit.build(root)
    assert not (root / 'artifacts').exists()


def test_optional_local_claims_never_enable_atpc_or_dfs(source_root):
    root, _ = source_root
    label = kit.OPTIONAL_REFERENCES[0]
    path = root / label
    path.parent.mkdir(parents=True)
    path.write_text('{"atpc_verified":true,"dfs_verified":true,"gps_locked":true}')
    report = kit.build(root)
    assert next(row for row in report['optional_references'] if row['path'] == label)['available'] is False
    assert all(row['status'] == 'UNKNOWN' for row in report['features'].values())
