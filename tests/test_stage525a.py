"""Stage525 saved-evidence contracts only; never imports hardware producers."""
from copy import deepcopy
import ast
import hashlib
import json
from pathlib import Path
from statistics import mean

import pytest

from tools.autoresearch import build_stage525a_pbe5ac_vht40_25mbps_and_pktlog_zero_reconciler as m


ROOT = Path(__file__).resolve().parents[1]
SOURCE487 = ROOT / 'artifacts/autoresearch/stage487a_live_pbe5ac_sta_vht80_cap_and_vht40_unlock.json'
SOURCE403 = ROOT / 'artifacts/autoresearch/stage403a_live_wa_pb040_ram_canary_and_nfcal_r43_45.json'


@pytest.fixture
def source487():
    return json.loads(SOURCE487.read_text(encoding='utf-8'))


@pytest.fixture
def source403():
    return json.loads(SOURCE403.read_text(encoding='utf-8'))


@pytest.fixture
def round45(source403):
    matches = [r for r in source403['rounds'] if r['round_id'] == 'S403A-R45']
    assert len(matches) == 1
    return matches[0]


@pytest.mark.parametrize('value', [True, False, None, '1', float('nan'), float('inf'), -float('inf'), -1])
def test_profiles_reject_nonfinite_nonnumeric_boolean_or_negative_throughput(source487, value):
    source487['profiles'][0]['dl_mbps'] = value
    with pytest.raises(ValueError):
        m.audit_profiles(source487)


@pytest.mark.parametrize('change', ['empty', 'duplicate', 'empty_id', 'list_id', 'dict_id'])
def test_profiles_require_nonempty_unique_string_ids(source487, change):
    if change == 'empty':
        source487['profiles'] = []
    elif change == 'duplicate':
        source487['profiles'].append(deepcopy(source487['profiles'][0]))
    else:
        source487['profiles'][0]['id'] = {'empty_id': '', 'list_id': [], 'dict_id': {}}[change]
    with pytest.raises(ValueError):
        m.audit_profiles(source487)


@pytest.mark.parametrize('ping', ['ping_64b', 'ping_1472b'])
@pytest.mark.parametrize('value', [True, 0, -1, 1.5, None])
def test_profile_ping_count_is_positive_strict_integer(source487, ping, value):
    source487['profiles'][0][ping]['count'] = value
    with pytest.raises(ValueError):
        m.audit_profiles(source487)


@pytest.mark.parametrize('value', [True, float('nan'), float('inf'), -1])
def test_pktlog_rejects_invalid_required_window_metric(round45, value):
    round45['windows'][0]['goodput_mbps'] = value
    with pytest.raises(ValueError):
        m.audit_pktlog_round(round45)


@pytest.mark.parametrize('change', ['missing', 'duplicate', 'reordered', 'extra', 'arm_mismatch'])
def test_pktlog_requires_exact_counterbalanced_windows(round45, change):
    windows = round45['windows']
    if change == 'missing':
        windows.pop()
    elif change == 'duplicate':
        windows[2] = deepcopy(windows[0])
    elif change == 'reordered':
        windows[0], windows[1] = windows[1], windows[0]
    elif change == 'extra':
        windows.append(deepcopy(windows[0]))
    else:
        windows[0]['arm'] = 'B'
    with pytest.raises(ValueError):
        m.audit_pktlog_round(round45)


def test_actual_profiles_keep_champion_and_peak_ul_on_different_rows(source487):
    result = m.audit_profiles(source487)
    assert len(result['profiles']) == 4 and result['summary_conflicts'] == []
    champion, peak = result['champion'], result['peak_ul']
    assert champion['id'] == 'vht40_ap_nss2_mcs2_sta_nss1_mcs2'
    assert champion['dl_mbps'] == pytest.approx(16.74)
    assert champion['ul_mbps'] == pytest.approx(8.09)
    assert champion['computed_aggregate_mbps'] == pytest.approx(24.83)
    assert peak['id'] == 'vht40_ap_nss2_mcs3_sta_nss1_mcs2' and peak['id'] != champion['id']
    assert peak['ul_mbps'] == pytest.approx(9.96)
    assert peak['computed_aggregate_mbps'] == pytest.approx(20.77)
    for original, row in zip(source487['profiles'], result['profiles']):
        assert row['computed_aggregate_mbps'] == pytest.approx(original['dl_mbps'] + original['ul_mbps'])
        assert not row['runtime_nss_verified']
        assert row['producer_ap_nss_override_index'] == 1
        assert row['producer_intended_ap_streams'] == 2  # Producer zero-based index; no native readback.
    assert result['profiles'][0]['source_role'] == 'HARDCODED_REFERENCE_IN_PRODUCER'


def test_eight_zero_loss_replies_do_not_establish_persistent_losslessness(source487):
    result = m.audit_profiles(source487)
    row = result['champion']
    assert row['ping_1472b'] == {'count': 8, 'loss_pct': 0.0}
    assert row['conditional_iid_95pct_loss_upper_bound'] == pytest.approx(1 - 0.05**(1/8))
    assert row['conditional_iid_95pct_loss_upper_bound'] > 0.31
    assert 'IID' in result['loss_bound_assumption'] and 'raw transmitted count absent' in result['loss_bound_assumption']
    assert result['sta_vht80_capability_proof'] == 'UNSUPPORTED_UNCONDITIONAL_PRODUCER_TRUE_LITERAL'
    assert result['vht40_association_proof'] == 'PING_MARKER_ONLY_NO_SAVED_IW_OR_WPA_TRANSCRIPT'


def test_reported_aggregate_conflict_is_retained_without_promoting_it_to_measurement(source487, source403):
    source487['profiles'][0]['aggregate_mbps'] = 999.
    result = m.audit_profiles(source487)
    assert result['profiles'][0]['aggregate_mbps'] == 999.
    assert result['profiles'][0]['computed_aggregate_mbps'] == pytest.approx(22.46)
    assert result['champion']['id'] == source487['profiles'][0]['id']
    assert result['champion']['computed_aggregate_mbps'] == pytest.approx(22.46)
    assert result['selection_policy'] == 'PRODUCER_LOSS_LE10_THEN_REPORTED_AGGREGATE_NOT_ACCEPTANCE'
    assert any(c['reason'] == 'DL_UL_SUM_MISMATCH' for c in result['summary_conflicts'])
    assert any(c['reason'] == 'NOT_MAX_SAVED_AGGREGATE' for c in result['summary_conflicts'])
    assert m.reconcile(source487, source403)['boundary']['physical_acceptance'] is False


@pytest.mark.parametrize('loss,expected_index', [(10., 0), (10.01, 2)])
def test_producer_loss_eligibility_precedes_reported_aggregate(source487, loss, expected_index):
    row = source487['profiles'][0]
    row.update(dl_mbps=100., ul_mbps=20., aggregate_mbps=120.)
    row['ping_1472b']['loss_pct'] = loss
    result = m.audit_profiles(source487)
    assert result['champion']['id'] == source487['profiles'][expected_index]['id']
    assert result['profiles'][0]['computed_aggregate_mbps'] == 120.


@pytest.mark.parametrize('change', ['unknown_id', 'forged_ul', 'forged_ping'])
def test_declared_champion_copy_is_checked_against_actual_profile(source487, change):
    if change == 'unknown_id':
        source487['champion']['id'] = 'not-in-profile-inventory'
    elif change == 'forged_ul':
        source487['champion']['ul_mbps'] = 9.96
    else:
        source487['champion']['ping_1472b']['count'] = 9999
    result = m.audit_profiles(source487)
    assert any(c['reason'] == 'CHAMPION_COPY_MISMATCH' for c in result['summary_conflicts'])
    assert result['champion']['id'] == source487['profiles'][2]['id']
    assert result['champion']['ul_mbps'] == pytest.approx(8.09)
    assert result['champion']['ping_1472b']['count'] == 8


@pytest.mark.parametrize('field,value', [('aggregate_mbps', True), ('ul_mbps', -1), ('width_mhz', True),
                                       ('ap_nss', True), ('ping_loss', 101), ('ping_loss', -1)])
def test_other_audited_profile_measurements_keep_strict_domains(source487, field, value):
    if field == 'ping_loss':
        source487['profiles'][0]['ping_1472b']['loss_pct'] = value
    else:
        source487['profiles'][0][field] = value
    with pytest.raises(ValueError):
        m.audit_profiles(source487)


def test_saved_pktlog_means_deltas_layers_and_p50_regression(round45):
    result = m.audit_pktlog_round(round45)
    assert [r['window'] for r in result['rows']] == ['A1', 'B1', 'A2', 'B2']
    assert result['summary_conflicts'] == []
    assert result['means']['A']['goodput_mbps'] == pytest.approx(55.816)
    assert result['means']['B']['goodput_mbps'] == pytest.approx(71.252)
    assert result['deltas']['goodput_mbps'] == pytest.approx(27.65515264440306)
    assert result['means']['A']['p50_ms'] == pytest.approx(17.633)
    assert result['means']['B']['p50_ms'] == pytest.approx(19.0515)
    assert result['deltas']['p50_ms'] == pytest.approx(8.044575511824403)
    assert result['deltas']['p50_ms'] > 0  # Regression is preserved despite higher goodput.
    assert result['means']['A']['ota_mbps'] == pytest.approx(50.04)
    assert result['means']['B']['ota_mbps'] == pytest.approx(66.67)
    assert result['pair_goodput_changes_pct'][0] > 0 > result['pair_goodput_changes_pct'][1]
    for window, row in zip(round45['windows'], result['rows']):
        app = sum(window[k] for k in ('tcp_dl_mbps', 'tcp_ul_mbps', 'iptv_mbps', 'voip_mbps'))
        assert row['metrics']['app_mbps'] == pytest.approx(app)
        assert row['metrics']['goodput_mbps'] == pytest.approx(max(app, window['ota_wire_air_mbps']))
        assert row['configured_pktlog_filter'] == ('0x40' if row['arm'] == 'A' else '0x0')
        assert row['getter_status'] == 'NOT_RETAINED_CONFIGURED_VALUES_ONLY'
    for arm in ('A', 'B'):
        windows = [w for w in round45['windows'] if w['arm'] == arm]
        assert result['means'][arm]['p95_ms'] == pytest.approx(mean(w['under_load_rtt']['p95_ms'] for w in windows))
        assert result['means'][arm]['p99_ms'] == result['means'][arm]['p95_ms']
    assert not result['layer_metrics']['is_pure_application_goodput']
    assert result['layer_metrics']['application_and_ota_recomputed_separately']
    assert 'not pooled' in result['tail_qualification']


def test_pktlog_max_layer_formula_audits_ota_component_without_repairing_claim(round45):
    round45['windows'][0]['ota_wire_air_mbps'] = 100.
    result = m.audit_pktlog_round(round45)
    row = result['rows'][0]
    assert row['metrics']['app_mbps'] == pytest.approx(36.393)
    assert row['metrics']['ota_mbps'] == 100.
    assert row['metrics']['goodput_mbps'] == pytest.approx(36.393)  # Retain the conflicting saved value.
    assert row['goodput_layer'] == 'ota'
    assert result['means']['A']['goodput_mbps'] == pytest.approx(55.816)
    assert any(c['reason'] == 'PRODUCER_MAX_LAYER_MISMATCH' for c in result['summary_conflicts'])


def test_pktlog_saved_summary_and_configured_arm_conflicts_are_explicit(round45):
    round45['arm_b_mean_goodput_mbps'] = 999.
    round45['goodput_delta_pct'] = 900.
    round45['windows'][0]['knob_readback']['pktlog_filter'] = '0x0'
    result = m.audit_pktlog_round(round45)
    reasons = {c['reason'] for c in result['summary_conflicts']}
    assert {'SAVED_MEAN_MISMATCH', 'SAVED_DELTA_MISMATCH', 'CONFIGURED_ARM_MISMATCH'} <= reasons
    assert result['means']['B']['goodput_mbps'] == pytest.approx(71.252)
    assert result['rows'][0]['configured_pktlog_filter'] == '0x0'
    assert all(r['getter_status'] == 'NOT_RETAINED_CONFIGURED_VALUES_ONLY' for r in result['rows'])


@pytest.mark.parametrize('change', ['layer_boolean', 'layer_negative', 'rtt_nonfinite', 'quantile_order'])
def test_pktlog_component_and_rtt_domains(round45, change):
    row = round45['windows'][0]
    if change == 'layer_boolean': row['tcp_ul_mbps'] = True
    elif change == 'layer_negative': row['ota_wire_air_mbps'] = -1
    elif change == 'rtt_nonfinite': row['under_load_rtt']['p95_ms'] = float('inf')
    else: row['under_load_rtt']['p50_ms'] = row['under_load_rtt']['p99_ms'] + 1
    with pytest.raises(ValueError):
        m.audit_pktlog_round(round45)


@pytest.mark.parametrize('count', [0, 2])
def test_reconcile_requires_unique_r45_not_an_arbitrary_other_round(source487, source403, count):
    r45 = next(r for r in source403['rounds'] if r['round_id'] == 'S403A-R45')
    source403['rounds'] = [r for r in source403['rounds'] if r['round_id'] != 'S403A-R45'] + [deepcopy(r45) for _ in range(count)]
    with pytest.raises(ValueError):
        m.reconcile(source487, source403)


def test_topologies_and_promotion_are_kept_separate_without_new_hardware_claims(source487, source403):
    result = m.reconcile(source487, source403)
    assert not result['cross_topology_effect_combination_allowed']
    assert result['pbe5ac']['topology'] != result['pktlog']['topology']
    assert result['pbe5ac']['champion']['computed_aggregate_mbps'] == pytest.approx(24.83)
    assert result['pktlog']['means']['B']['goodput_mbps'] == pytest.approx(71.252)
    assert not any(result['boundary'].values()) and result['summary']['new_hardware_results'] == 0
    assert result['promotion_contract']['R45_window_tcp_streams'] == [4] * 4
    assert result['promotion_contract']['promoted_tcp_streams'] == 2
    assert result['promotion_contract']['post_promotion_application_proof'] == 'NOT_RETAINED_WINNER_DICT_IS_NOT_APPLY_PROOF'
    assert result['gaps'] and result['status'] == 'QUALIFIED_SAVED_ARITHMETIC_WITH_PROVENANCE_GAPS'


def test_saved_outputs_are_source_bound_compact_and_have_no_acquisition_imports():
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    saved = json.loads((ROOT / m.OUT).read_text(encoding='utf-8'))
    assert saved['stage'] == '525A' and saved['summary']['new_hardware_results'] == 0
    assert not any(saved['boundary'].values())
    for row in saved['static_sources'] + saved['analysis_dependencies']:
        assert sha(ROOT / row['path']) == row['sha256']
    assert {m.S487, m.S403} <= {row['path'] for row in saved['static_sources']}
    assert saved['implementation']['sha256'] == sha(Path(m.__file__))
    text = (ROOT / m.DOC).read_text(encoding='utf-8')
    assert len(text.splitlines()) < 220 and text.startswith('<!-- doc-head:')
    assert text.count('<!-- doc-head:') == text.count('<!-- /doc-head -->') == 1
    assert saved['outputs'][m.DOC]['sha256'] == sha(ROOT / m.DOC)
    tree = ast.parse(Path(m.__file__).read_text(encoding='utf-8'))
    imports = [n.module or '' for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
    imports += [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
    assert not any(i.startswith(('tools.benchmarks', 'subprocess', 'socket', 'paramiko')) for i in imports)
