import subprocess

import pytest

from tools.verify.verify_stage853a_public_git_sync_and_push_v2 import (
    stage_selection, update_text, redact_public_text, unique_object, assert_tested_index)
from tools.verify.verify_stage826a_public_git_hygiene_and_push_gate import audit


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root)


def init_repo(root):
    git(root, 'init', '-q')
    git(root, 'config', 'user.email', 'test@example.invalid')
    git(root, 'config', 'user.name', 'Local Test')


def test_doc_update_idempotent_and_preserves_continuity():
    before = '<!-- doc-head: initial -->\n<!-- /doc-head -->\n\n# State\n\nPrior evidence UNKNOWN.\n'
    result = update_text(before, True)
    assert 'Prior evidence UNKNOWN.' in result
    assert update_text(result, True) == result
    assert '(STAGE854A_' in result
    assert result.count('<!-- doc-head:') == 1


def test_index_not_worktree_is_audited(tmp_path):
    init_repo(tmp_path)
    (tmp_path / 'safe.py').write_text('value = 1\n')
    (tmp_path / '.gitignore').write_text('*.bin\n*.ko\n*.sqfs\n.env*\n*[hH][aA][cC][kK][eE][rR][oO][nN][eE]*\n*stage8[1-9][a-c]*\n*stage9[0-8][a-c]*\n')
    git(tmp_path, 'add', 'safe.py', '.gitignore')
    git(tmp_path, 'commit', '-qm', 'fixture')
    (tmp_path / 'safe.py').write_text('value = 2\n')
    git(tmp_path, 'add', 'safe.py')
    # A vendor binary remains blocked even if ignore policy is otherwise correct.
    (tmp_path / 'vendor.bin').write_bytes(b'vendor')
    git(tmp_path, 'add', '-f', 'vendor.bin')
    result, _, findings = audit(tmp_path)
    assert not result['compliant']
    assert any(row['path'] == 'vendor.bin' for row in findings)


def test_unrelated_staged_changes_preserved(tmp_path):
    init_repo(tmp_path)
    (tmp_path / 'other.py').write_text('pass\n')
    git(tmp_path, 'add', 'other.py')
    with pytest.raises(ValueError, match='unrelated staged'):
        stage_selection(tmp_path, ['new.py'])
    assert git(tmp_path, 'diff', '--cached', '--name-only').decode().strip() == 'other.py'


def test_document_stage_preserves_unrelated_working_edits(tmp_path):
    init_repo(tmp_path)
    base = '<!-- doc-head: initial -->\n<!-- /doc-head -->\n\n# Original\n'
    path = tmp_path / 'README.md'
    path.write_text(base)
    git(tmp_path, 'add', 'README.md')
    git(tmp_path, 'commit', '-qm', 'fixture')
    path.write_text(update_text(base + '\nConcurrent edit.\n'))
    stage_selection(tmp_path, ['README.md'])
    indexed = git(tmp_path, 'show', ':README.md').decode()
    assert 'Concurrent edit.' not in indexed
    assert 'Concurrent edit.' in path.read_text()
    assert 'Stages849A..854A' in indexed


def test_public_aliases_preserve_distinct_json_keys():
    import json
    prefix = '.'.join(['10', '10', '7'])
    text = json.dumps({prefix + '.1': 'one', prefix + '.2': 'two'})
    result = json.loads(redact_public_text(text, []))
    assert len(result) == 2
    assert set(result.values()) == {'one', 'two'}
    assert prefix not in str(result)


def test_case_distinct_identifiers_preserve_distinct_keys():
    import json
    device = ':'.join(['ab'] * 6)
    text = json.dumps({device: 1, device.upper(): 2})
    result = json.loads(redact_public_text(text, []), object_pairs_hook=unique_object)
    assert len(result) == 2
    assert set(result.values()) == {1, 2}


def test_reserved_alias_or_duplicate_key_fails_closed():
    import json
    with pytest.raises(ValueError, match='reserved'):
        redact_public_text('PRIVATE_DEVICE_001', [])
    with pytest.raises(ValueError, match='duplicate'):
        json.loads('{"same":1,"same":2}', object_pairs_hook=unique_object)


def test_staged_revision_must_match_tested_bytes(tmp_path):
    import hashlib
    init_repo(tmp_path)
    path = tmp_path / 'code.py'
    path.write_bytes(b'value=1\n')
    git(tmp_path, 'add', 'code.py')
    pins = {'verification_sources': [{'path': 'code.py',
             'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}], 'sources': []}
    assert_tested_index(tmp_path, pins)
    path.write_bytes(b'value=2\n')
    git(tmp_path, 'add', 'code.py')
    # Put tested bytes back only in the working file; the index remains untested.
    path.write_bytes(b'value=1\n')
    with pytest.raises(ValueError, match='indexed tested revision drift'):
        assert_tested_index(tmp_path, pins)
