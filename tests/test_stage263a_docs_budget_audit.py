from pathlib import Path
import pytest
from tools.verify.audit_all_docs_line_budget_and_dochead import inspect_markdown, audit, active_routers


GOOD = b'<!-- doc-head: test -->\nsummary\n<!-- /doc-head -->\n\nbody\n'


def test_good_and_bom():
    assert inspect_markdown(GOOD)["compliant"]
    assert inspect_markdown(b'\xef\xbb\xbf' + GOOD)["compliant"]


@pytest.mark.parametrize('data,error', [
    (b'body\n'+GOOD, 'requires_single_doc_head_at_line_1'),
    (GOOD+GOOD, 'requires_single_doc_head_at_line_1'),
    (b'<!-- doc-head: x\nsummary\n<!-- /doc-head -->\n', 'requires_single_doc_head_at_line_1'),
    (b'prefix <!-- doc-head: x -->\n<!-- /doc-head -->\n', 'requires_single_doc_head_at_line_1'),
    (GOOD.replace(b'<!-- /doc-head -->', b''), 'requires_paired_header_with_at_most_six_summary_lines'),
    (GOOD+b'\n'*215, 'line_budget_requires_less_than_220'),
    (b'<!-- doc-head: x -->\n'+b'x\n'*7+b'<!-- /doc-head -->', 'requires_paired_header_with_at_most_six_summary_lines'),
])
def test_contract_failures(data, error):
    assert error in inspect_markdown(data)['errors']


def test_recursive_inventory_distinguishes_active_history_and_missing(tmp_path):
    (tmp_path/'docs/archive').mkdir(parents=True)
    (tmp_path/'AGENTS.md').write_text('[router](docs/router.md)')
    for rel in active_routers(tmp_path):
        (tmp_path/rel).write_bytes(GOOD)
    (tmp_path/'docs/archive/history.MD').write_bytes(b'old\n'*300)
    result = audit(tmp_path)
    assert result['compliant']
    assert result['summary']['all_docs_noncompliant'] == 1
    (tmp_path/'docs/router.md').unlink()
    result = audit(tmp_path)
    assert not result['compliant'] and result['missing_active_routers'] == ['docs/router.md']


def test_invalid_encoding_is_not_silently_skipped(tmp_path):
    (tmp_path/'docs').mkdir()
    (tmp_path/'docs/CURRENT_STATE.md').write_bytes(b'\xff')
    result = audit(tmp_path)
    assert result['summary']['active_failures'] == ['docs/CURRENT_STATE.md']
    assert len(result['static_sources'][0]['sha256']) == 64
    assert result['static_sources'][0]['bytes'] == 1


def test_real_inventory_binds_current_docs():
    root = Path(__file__).resolve().parents[1]
    result = audit(root)
    assert result['summary']['scanned'] > 100
    assert all(len(row.get('sha256', '')) == 64 for row in result['static_sources'])
    assert any(row['path'] == 'docs/CURRENT_STATE.md' for row in result['static_sources'])
