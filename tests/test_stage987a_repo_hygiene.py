"""Disposable Git/filesystem fixtures; no production cleanup or Git mutation."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

import pytest

from tools.verify import audit_stage987a_repo_status_and_orphan_artifacts as audit

ROOT = Path(__file__).resolve().parents[1]
LABEL = 'artifacts/autoresearch/stage123a_summary.json.abcdefgh.tmp'


def make_orphan(root, label=LABEL):
    if not (root/'.git').exists():
        subprocess.run(['git', 'init', '-q', str(root)], check=True)
        (root/'.gitignore').write_text('artifacts/**/*.tmp\n')
    path = root / label
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({'schema_version': 1, 'stage': '123A', 'status': 'CONFIRMED'}))
    path.with_name(path.name.rsplit('.', 2)[0]).write_text(path.read_text())
    old = time.time()-audit.MIN_AGE_S-10
    os.utime(path, (old, old))
    return path


def plan(root, label=LABEL):
    return audit.candidate(root, label, ignored={label}, tracked=set(), now_s=time.time())


def test_recognized_ignored_stale_summary_requires_reference_scan(tmp_path):
    path = make_orphan(tmp_path)
    row = plan(tmp_path)
    assert row['eligible'] and row['sha256'] == audit.sha(path.read_bytes())
    complete, found = audit.reference_scan(tmp_path, [row], {LABEL})
    assert complete and found == {LABEL: False}


@pytest.mark.parametrize('kind', ['tracked', 'not_ignored', 'young', 'raw_content', 'wrong_stage', 'manual'])
def test_user_active_and_unclassified_files_are_retained(tmp_path, kind):
    label = LABEL if kind != 'manual' else 'artifacts/autoresearch/manual.tmp'
    path = make_orphan(tmp_path, label)
    ignored, tracked = {label}, set()
    if kind == 'tracked':
        tracked.add(label)
    elif kind == 'not_ignored':
        ignored.clear()
    elif kind == 'young':
        os.utime(path, None)
    elif kind == 'raw_content':
        path.write_text(json.dumps({'schema_version': 1, 'stage': '123A', 'stdout': 'raw capture fixture'}))
        old = time.time()-audit.MIN_AGE_S-10
        os.utime(path, (old, old))
    elif kind == 'wrong_stage':
        path.write_text(json.dumps({'schema_version': 1, 'stage': '999A'}))
        old = time.time()-audit.MIN_AGE_S-10
        os.utime(path, (old, old))
    result = audit.candidate(tmp_path, label, ignored=ignored, tracked=tracked, now_s=time.time())
    assert not result['eligible']
    assert path.exists()


def test_referenced_temporary_is_never_proven_orphan(tmp_path):
    make_orphan(tmp_path)
    reference = tmp_path / 'source.py'
    reference.write_text(repr(LABEL))
    complete, found = audit.reference_scan(tmp_path, [plan(tmp_path)], {LABEL, 'source.py'})
    assert complete and found[LABEL]


def test_no_completed_replacement_or_duplicate_json_is_retained(tmp_path):
    path = make_orphan(tmp_path)
    completed = path.with_name(path.name.rsplit('.', 2)[0])
    completed.unlink()
    assert not plan(tmp_path)['eligible']
    completed.write_text('{"stage":"123A"}')
    path.write_text('{"stage":"123A","stage":"123A","schema_version":1}')
    old = time.time()-audit.MIN_AGE_S-10
    os.utime(path, (old, old))
    assert not plan(tmp_path)['eligible']


def test_incomplete_reference_scan_cannot_authorize_cleanup(tmp_path):
    make_orphan(tmp_path)
    reference = tmp_path / 'oversize.json'
    reference.write_bytes(b'x'*(audit.MAX_FILE_BYTES+1))
    complete, _ = audit.reference_scan(tmp_path, [plan(tmp_path)], {LABEL, 'oversize.json'})
    assert complete is False


def test_hardlink_is_retained(tmp_path):
    path = make_orphan(tmp_path)
    (tmp_path / 'external-link').hardlink_to(path)
    assert not plan(tmp_path)['eligible']


def test_busy_candidate_is_retained(tmp_path, monkeypatch):
    make_orphan(tmp_path)
    @contextmanager
    def busy(path):
        raise OSError('fixture writer is active')
        yield
    monkeypatch.setattr(audit, 'exclusive_read', busy)
    assert not plan(tmp_path)['eligible']


def test_actual_writer_prevents_candidate_proof(tmp_path):
    path = make_orphan(tmp_path)
    with path.open('r+b') as writer:
        if os.name != 'nt':
            import fcntl
            fcntl.flock(writer.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert not plan(tmp_path)['eligible']


def test_symlink_or_reparse_metadata_rejected(tmp_path, monkeypatch):
    path = make_orphan(tmp_path)
    original = Path.lstat
    def malicious(self):
        metadata = original(self)
        if self == path:
            from types import SimpleNamespace
            return SimpleNamespace(st_mode=metadata.st_mode, st_file_attributes=0x400)
        return metadata
    monkeypatch.setattr(Path, 'lstat', malicious)
    assert not plan(tmp_path)['eligible']


def test_quarantine_verifies_bytes_and_keeps_restore_map(tmp_path):
    path = make_orphan(tmp_path)
    row = plan(tmp_path)
    run = tmp_path / '.git/stage983_988/stage987a/runs/test-run'
    result = audit.apply_quarantine(tmp_path, run, [row])
    assert result['complete'] and result['quarantined'] == 1
    assert not path.exists()
    journal = json.loads((run/'restore_map.json').read_text())
    item = journal['moves'][0]
    assert audit.sha((run/item['quarantine_path']).read_bytes()) == row['sha256']
    assert item['original_path'] == LABEL


def test_mutated_candidate_never_moves(tmp_path):
    path = make_orphan(tmp_path)
    row = plan(tmp_path)
    path.write_text('new user data')
    run = tmp_path / '.git/stage983_988/stage987a/runs/test-run'
    result = audit.apply_quarantine(tmp_path, run, [row])
    assert not result['complete'] and result['quarantined'] == 0
    assert path.read_text() == 'new user data'


def test_failed_batch_restores_all_completed_moves(tmp_path):
    first = make_orphan(tmp_path)
    label2 = 'artifacts/autoresearch/stage123a_other.json.ijklmnop.tmp'
    second = make_orphan(tmp_path, label2)
    rows = [plan(tmp_path), plan(tmp_path, label2)]
    calls = []
    def failure(source, target):
        calls.append(source)
        if len(calls) == 2:
            raise OSError('injected second move failure')
        os.rename(source, target)
    run = tmp_path / '.git/stage983_988/stage987a/runs/test-run'
    result = audit.apply_quarantine(tmp_path, run, rows, move=failure)
    assert result['transaction_state'] == 'FAILED_ROLLED_BACK'
    assert result['restored_after_failure'] == 1 and result['quarantined'] == 0
    assert first.exists() and second.exists()
    assert [audit.sha(path.read_bytes()) for path in (first, second)] == [row['sha256'] for row in rows]


def test_path_escape_rejected(tmp_path):
    with pytest.raises(ValueError):
        audit.repo_path(tmp_path, '../outside')
    with pytest.raises(ValueError):
        audit.checked(tmp_path.parent/'outside', tmp_path)


def test_status_parser_keeps_rename_and_nonignored_user_entries():
    rows = audit.status_rows(b'R  moved.py\0original.py\0?? user.py\0 M modified.py\0')
    assert rows[0]['original_path'] == 'original.py'
    assert rows[1] == {'status': '??', 'path': 'user.py'}
    with pytest.raises(ValueError):
        audit.status_rows(b'R  moved.py\0')


def test_complete_git_audit_noop_preserves_index_and_user_work(tmp_path):
    subprocess.run(['git', 'init', '-q', str(tmp_path)], check=True)
    for key, value in [('user.name', 'Fixture'), ('user.email', 'test@example.invalid')]:
        subprocess.run(['git', '-C', str(tmp_path), 'config', key, value], check=True)
    for label in (audit.SELF, audit.TEST, 'tools/verify/stage779_822_offline_common.py'):
        target = tmp_path / label
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/label, target)
    (tmp_path/'.gitignore').write_text('artifacts/**/*.tmp\n')
    (tmp_path/'tracked.py').write_text('original\n')
    subprocess.run(['git', '-C', str(tmp_path), 'add', '--all'], check=True)
    subprocess.run(['git', '-C', str(tmp_path), '-c', 'core.hooksPath=.git/fixture-hooks',
                    'commit', '-qm', 'fixture'], check=True)
    (tmp_path/'tracked.py').write_text('modified user work\n')
    (tmp_path/'user.py').write_text('untracked user work\n')
    before = subprocess.check_output(['git', '-C', str(tmp_path), 'ls-files', '--stage', '-z'])
    result = audit.build(tmp_path, quarantine=True)
    assert result['all_gates_passed']
    assert result['cleanup']['transaction_state'] == 'NO_PROVEN_ORPHANS'
    assert result['cleanup']['quarantined'] == 0
    assert (tmp_path/'tracked.py').read_text() == 'modified user work\n'
    assert (tmp_path/'user.py').read_text() == 'untracked user work\n'
    assert subprocess.check_output(['git', '-C', str(tmp_path), 'ls-files', '--stage', '-z']) == before
    gitdir = tmp_path / '.git'
    for pin in result['private_evidence']:
        assert pin['path'].startswith(audit.PRIVATE+'/runs/')
        assert audit.sha((gitdir/pin['path']).read_bytes()) == pin['sha256']
