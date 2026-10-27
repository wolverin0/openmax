import json
from pathlib import Path
import pytest
from tools.verify import build_stage357a_ground_up_350stage_reconciliation as m


def put(root, name, obj):
    p = root/'artifacts'/name; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj), encoding='utf-8'); return p


def receipt():
    return {'stage': '10A', 'summary': {'claimed': 'CONFIRMED'}, 'boundary': {},
            'static_sources': [{'path': 'source.txt', 'sha256': m.c.sha(b'source')}],
            'task_id': 'saved', 'rounds': [{'round_id': 'R1', 'windows': [
                {'window': key, 'goodput_mbps': 10 if key[0] == 'A' else 11,
                 'rtt_p95_ms': 5 if key[0] == 'A' else 4} for key in ('A1', 'B1', 'A2', 'B2')]}]}


def test_snapshot_duplicates_and_summary_arithmetic_are_not_physical_experiments(tmp_path):
    (tmp_path/'source.txt').write_bytes(b'source')
    obj = receipt(); put(tmp_path, 'autoresearch/stage10a_wa_bench.json', obj)
    put(tmp_path, 'verification/repro/stage10a_wa_bench.json', obj)
    r = m.reconcile(tmp_path)
    assert r['summary']['receipt_files'] == 2 and r['summary']['unique_content_hashes'] == 1
    assert r['summary']['numeric_stage_ids_present'] == 1
    assert r['summary']['saved_comparison_fingerprints'] == 1
    comp = r['saved_comparisons'][0]
    assert comp['percent_change'] == {'goodput_mbps': 10., 'p95_ms': -20.}
    assert len(comp['source_locations']) == 2
    assert len(r['summary']['numeric_stage_ids_missing']) == 349
    assert {row['role'] for row in r['receipt_inventory']} == {'REPORTED_RECEIPT', 'SUPPORT_OR_COPY'}
    assert all(row['empirical_acceptance'] == 'NOT_INDEPENDENTLY_ASSESSED' for row in r['receipt_inventory'])
    assert not r['boundary']['physical_acceptance']
    assert r['reference_integrity']['status_counts'] == {'MATCH': 1}


@pytest.mark.parametrize('name,expected', [('stage350a_more.json', '350A'), ('stage1.json', '1'),
    ('stage0a.json', None), ('stage351a.json', None), ('stage3500a.json', None), ('badstage10a.json', None)])
def test_cutoff_and_filename_domain(name, expected):
    assert m.stage_id(name) == expected


@pytest.mark.parametrize('raw', ['{"stage":"2A","stage":"2A"}', '{"x":NaN}', '[1,2]', '{broken'])
def test_malformed_duplicate_nonfinite_or_nonobject_stays_invalid(tmp_path, raw):
    p = put(tmp_path, 'stage2a_bad.json', {}); p.write_text(raw)
    r = m.reconcile(tmp_path)
    assert r['summary']['valid_objects'] == 0
    assert 2 in r['summary']['numeric_stage_ids_missing']
    assert r['receipt_inventory'][0]['parse_status'] == 'INVALID_OR_UNSAFE'


def test_identity_conflict_and_structural_gate_never_prove_science(tmp_path):
    obj = receipt(); obj['stage'] = '9A'; obj['meta'] = {'stage': '10A'}; obj['gaps'] = []
    put(tmp_path, 'stage10a_model.json', obj)
    row = m.reconcile(tmp_path)['receipt_inventory'][0]
    assert row['stage_identity_conflict'] and row['declared_stage_ids'] == ['10A', '9A']
    assert row['structural_five_pillar_gate']['compliant']
    assert row['empirical_acceptance'] == 'NOT_INDEPENDENTLY_ASSESSED'


def test_source_drift_missing_unsafe_and_budget_skips_are_not_matches(tmp_path):
    (tmp_path/'source').write_bytes(b'changed')
    h = m.c.sha(b'original')
    refs = {('source', h), ('missing', h), ('../outside', h), ('https://example/a', h)}
    r = m.check_references(tmp_path, refs)
    assert r['status_counts'] == {'DRIFT': 1, 'MISSING_OR_UNSAFE': 1, 'UNRESOLVED_NON_REPO_RELATIVE_REFERENCE': 2}
    assert m.check_references(tmp_path, {('source', h)}, byte_budget=0)['status_counts'] == {'UNVERIFIED_READ_BUDGET': 1}


def test_unspecified_letter_suffix_is_not_a_false_conflict(tmp_path):
    put(tmp_path, 'stage16_ltu.json', {'stage': '16A'})
    row = m.reconcile(tmp_path)['receipt_inventory'][0]
    assert not row['stage_identity_conflict']
    assert row['declared_identity_relations'] == {'16A': 'COMPATIBLE_UNDERSPECIFIED_SUFFIX'}
    assert m.identity_relation('16A', '16B') == 'CONFLICT'


def test_bad_quantiles_and_duplicate_windows_rejected_with_pointer(tmp_path):
    obj = receipt(); obj['rounds'][0]['windows'][3]['window'] = 'B1'
    put(tmp_path, 'stage10a_wa_bench.json', obj)
    r = m.reconcile(tmp_path)
    assert r['summary']['saved_comparison_fingerprints'] == 0
    assert r['rejected_comparisons'][0]['pointer'] == '/rounds/0/windows'
    assert r['rejected_comparisons'][0]['reason'] == 'duplicate_or_unordered_window_ids'


def test_structure_and_file_limits_fail_closed(tmp_path, monkeypatch):
    put(tmp_path, 'stage10a_a.json', {})
    monkeypatch.setattr(m, 'MAX_FILES', 0)
    with pytest.raises(ValueError, match='receipt_file_limit'): m.reconcile(tmp_path)
    with pytest.raises(ValueError, match='json_structure_limit'): list(m.nodes([[[1]]], depth=40))


@pytest.mark.parametrize('shape', ['separate_arms', 'named_keys'])
def test_reconstructed_and_named_phase_order_keep_source_provenance(tmp_path, shape):
    obj = receipt(); rows = obj.pop('rounds')[0]['windows']
    if shape == 'separate_arms':
        obj['arm_a_windows'] = [rows[0], rows[2]]; obj['arm_b_windows'] = [rows[1], rows[3]]
        expected = 'RECONSTRUCTED_FROM_SEPARATE_ARM_ARRAYS'; pointers = ['/arm_a_windows', '/arm_b_windows']
    else:
        obj['phases'] = {row['window']: row for row in rows}
        expected = 'NAMED_PHASE_KEYS_ORDER_ASSUMED'; pointers = ['/phases/'+k for k in ('A1','B1','A2','B2')]
    put(tmp_path, 'stage10a_wa_bench.json', obj)
    location = m.reconcile(tmp_path)['saved_comparisons'][0]['source_locations'][0]
    assert location['order_provenance'] == expected and location['source_array_pointers'] == pointers


def test_generated_snapshot_pins_boundaries_and_compact_doc():
    r = m.c.load(m.ROOT/m.OUT)
    assert r['cutoff_stage'] == 350 and r['summary']['new_hardware_results'] == 0
    assert not r['snapshot']['receipt_drift_during_scan']
    for source in r['static_sources']:
        assert m.c.sha(m.c.read(m.ROOT/source['path'])) == source['sha256']
    assert all(int(m.re.match(r'\d+', row['filename_stage'])[0]) <= 350 for row in r['receipt_inventory'])
    text = (m.ROOT/m.DOC).read_text(encoding='utf-8')
    assert len(text.splitlines()) < 220 and text.startswith('<!-- doc-head:')
    assert text.count('<!-- doc-head:') == text.count('<!-- /doc-head -->') == 1
    assert 'PRESENCE_HEURISTIC' in r['structural_gate_meaning']
