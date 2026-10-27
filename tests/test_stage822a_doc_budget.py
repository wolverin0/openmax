"""Offline document-budget regression fixtures; no repository docs are mutated."""
from pathlib import Path

import pytest

from tools.verify import normalize_stage822a_doc_budget as n


def doc(root: Path, name: str, text: str) -> Path:
    path = root / 'docs' / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')
    return path


def payload(blob: bytes) -> list[str]:
    lines = blob.decode('utf-8').splitlines()
    return lines[lines.index(n.OPEN) + 1:lines.index(n.CLOSE)]


def test_missing_header_and_original_backup(tmp_path):
    path = doc(tmp_path, 'A.md', '# A\n\nOriginal content.\n')
    original = path.read_bytes(); proposed = n.plan(tmp_path)
    result = n.apply(tmp_path, proposed)
    assert n.inspect(path.read_bytes())['compliant']
    rec = result['revisions'][0]
    assert (tmp_path / rec['original_backup']).read_bytes() == original
    assert rec['original_sha256'] == n.sha(original)
    assert n.body_lines(path.read_bytes())[-3:] == ['# A', '', 'Original content.']


def test_multiple_headers_only_metadata_removed(tmp_path):
    source = '<!-- doc-head: old -->\nsummary remains\n<!-- /doc-head -->\n# A\n<!-- doc-head: later -->\nlater summary\n<!-- /doc-head -->\n'
    path = doc(tmp_path, 'A.md', source)
    n.apply(tmp_path, n.plan(tmp_path))
    text = path.read_text(encoding='utf-8')
    assert text.count('<!-- doc-head:') == text.count('<!-- /doc-head -->') == 1
    assert 'summary remains' in text and 'later summary' in text


def test_long_document_every_line_preserved_and_fences_atomic(tmp_path):
    source = '# Top\n' + '\n'.join(f'line {i}' for i in range(150)) + '\n```sh\n' + '\n'.join('echo fixture' for _ in range(140)) + '\n```\n## Later\n[Top](#top)\n'
    path = doc(tmp_path, 'LONG.md', source); original = path.read_bytes()
    proposed = n.plan(tmp_path); result = n.apply(tmp_path, proposed)
    rec = result['revisions'][0]
    restored = []
    for part in rec['parts']:
        data = (tmp_path / part['path']).read_bytes()
        assert n.inspect(data)['compliant']
        lines = payload(data); restored.extend(lines)
        assert lines.count('```sh') == lines.count('```')
    assert restored == n.body_lines(original)
    root_text = path.read_text(encoding='utf-8')
    assert '<a id="later"></a>' in root_text
    assert '[Exact original bytes]' in root_text


def test_long_table_repeated_header_outside_payload(tmp_path):
    source = '# Table\n\n| Key | Value |\n| --- | --- |\n' + '\n'.join(f'| {i} | fixture |' for i in range(320)) + '\n'
    path = doc(tmp_path, 'TABLE.md', source); original = path.read_bytes()
    result = n.apply(tmp_path, n.plan(tmp_path)); rec = result['revisions'][0]
    restored = [line for part in rec['parts'] for line in payload((tmp_path / part['path']).read_bytes())]
    assert restored == n.body_lines(original)
    assert any(part['repeated_table_header'] for part in rec['parts'])


def test_replay_is_idempotent_and_keeps_first_backup(tmp_path):
    path = doc(tmp_path, 'A.md', '# A\nunchanged\n')
    first = n.apply(tmp_path, n.plan(tmp_path)); normalized = path.read_bytes()
    assert n.plan(tmp_path) == []
    second = n.apply(tmp_path, n.plan(tmp_path))
    assert first == second and path.read_bytes() == normalized


def test_changed_shared_document_stops_before_mutation(tmp_path):
    path = doc(tmp_path, 'A.md', '# A\noriginal\n'); proposed = n.plan(tmp_path)
    path.write_text('# A\nconcurrent owner update\n', encoding='utf-8')
    with pytest.raises(ValueError, match='changed after planning'):
        n.apply(tmp_path, proposed)
    assert 'concurrent owner update' in path.read_text(encoding='utf-8')
    assert not (tmp_path / n.MANIFEST).exists()


def test_unclosed_or_oversized_fence_fails_closed():
    with pytest.raises(ValueError, match='unclosed'):
        n.chunks(['```python', 'print(1)'])
    with pytest.raises(ValueError, match='fenced block exceeds'):
        n.chunks(['```'] + ['fixture'] * 156 + ['```'])


def test_escaped_output_path_rejected(tmp_path):
    with pytest.raises(ValueError):
        n.bounded(tmp_path, '../outside')
