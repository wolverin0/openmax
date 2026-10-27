"""Disposable model fixtures only: no loader, bench, device or network import."""

from dataclasses import dataclass, replace
import ast
from pathlib import Path
import json
import math

import pytest

from controller.adaptive_aql_regime_controller import AdaptiveAQLRegimeController, policy_metadata


def _r15_observed_rows():
    from orchestration.autoresearch.fmx_offline_data import load_all15_measurements
    return [row for row in load_all15_measurements()[0] if row.round_id=='R15']


def test_r15_allow_asymmetric_preserves_complete_observed_endpoint_packages():
    rows=_r15_observed_rows();ratio=rows[2].ul_goodput_mbps/rows[2].dl_goodput_mbps
    result=AdaptiveAQLRegimeController(rows[2:]).select(6,ratio,.1,allow_asymmetric=True)
    assert result['status']=='SELECTED' and result['asymmetric_package'] is True
    assert result['automatic_execution_allowed'] is result['physical_safety_qualified'] is False
    allowed={(row.policy_key) for row in rows[2:]}
    assert result['policy_id'] in allowed
    assert result['ap_policy']['aql_by_ac'][2] in [[1500,3000],[1350,2700]]
    assert result['cpe_policy']['aql_by_ac'][2]==[2100,4200]
    assert result['cpe_policy']['fq_target_us']==12000
    assert result['cpe_policy']['tcp_limit_output_bytes']==327680
    assert result['ap_policy']['tcp_limit_output_bytes'] in [204800,196608]
    assert all(c['asymmetric_package'] for c in result['candidates'])


def test_r15_asymmetry_opt_out_and_constructor_override_filter_before_ranking():
    rows=_r15_observed_rows()[2:];ratio=rows[0].ul_goodput_mbps/rows[0].dl_goodput_mbps
    controller=AdaptiveAQLRegimeController(rows,allow_asymmetric=False)
    assert controller.select(6,ratio,.1)['status']=='ABSTAIN'
    assert controller.select(6,ratio,.1,allow_asymmetric=True)['status']=='SELECTED'
    assert AdaptiveAQLRegimeController(rows).select(6,ratio,.1,allow_asymmetric=False)['status']=='ABSTAIN'


def test_r15_symmetric_only_query_never_borrows_ratio_support_from_asymmetric_rows():
    rows=_r15_observed_rows();ratio=rows[2].ul_goodput_mbps/rows[2].dl_goodput_mbps
    controller=AdaptiveAQLRegimeController(rows)
    result=controller.select(6,ratio,.1,allow_asymmetric=False)
    assert result['status']=='ABSTAIN' and result['reason']=='UL_DL_RATIO_OUTSIDE_OBSERVED_ENVELOPE'
    symmetric=rows[1]
    result=controller.select(6,symmetric.ul_goodput_mbps/symmetric.dl_goodput_mbps,.1,allow_asymmetric=False)
    assert result['status']=='SELECTED' and result['asymmetric_package'] is False
    assert all(c['asymmetric_package'] is False for c in result['candidates'])


def test_asymmetric_negative_observation_quarantines_positive_alias_and_previous_selection():
    rows=_r15_observed_rows();first,second=rows[2:]
    prior=AdaptiveAQLRegimeController([first]).select(6,first.ul_goodput_mbps/first.dl_goodput_mbps,.1)
    failed=replace(first,iteration='synthetic_negative_asymmetric_alias',packet_loss_pct=5)
    result=AdaptiveAQLRegimeController([first,second,failed],min_switch_gain=10).select(
        6,second.ul_goodput_mbps/second.dl_goodput_mbps,.1,previous=prior,allow_asymmetric=True)
    assert result['status']=='SELECTED' and result['policy_id']==second.policy_key
    assert result['policy_id']!=prior['policy_id']
    assert any(e['policy_id']==first.policy_key for e in result['excluded_policy_evidence'])


@pytest.mark.parametrize('bad',[1,0,'true',[],{}])
def test_asymmetry_flags_reject_truthy_non_booleans(bad):
    with pytest.raises(ValueError):AdaptiveAQLRegimeController([],allow_asymmetric=bad)
    with pytest.raises(ValueError):AdaptiveAQLRegimeController([]).select(0,0,0,allow_asymmetric=bad)


def test_default_selector_replays_all_ten_accepted_ijkl_examples_without_behavior_change():
    from orchestration.autoresearch.fmx_offline_data import IJKL_ARTIFACTS,load_all14_measurements
    saved=json.loads((IJKL_ARTIFACTS/'wave_k_offline_examples.json').read_text(encoding='utf-8'))
    controller=AdaptiveAQLRegimeController(load_all14_measurements()[0])
    assert len(saved['examples'])==10
    for example in saved['examples']:
        args=dict(example['inputs'])
        if 'associated_cpes' in args:args['associated_cpes']=tuple(args['associated_cpes'])
        result=controller.select(**args);expected=example['result']
        for field in ('status','reason','policy_id','ap_policy','cpe_policy','score'):
            assert result[field]==expected[field],(example['name'],field)


@dataclass(frozen=True)
class Policy:
    aql_by_ac: tuple = ((1000, 2000),)*4
    aql_threshold_us: int = 8000
    fq_quantum_bytes: int = 300
    rc_per_thresh: int = 28
    rts_threshold: int | None = None
    ct_baseband_rifs: int | None = None
    ct_pshack: int | None = None
    htt_max_amsdu: int | None = None
    htt_max_ampdu: int | None = None
    dscp_micro_vo_steering: bool = False


@dataclass(frozen=True)
class Row:
    round_id: str = "fixture"
    iteration: str = "one"
    workload_regime: str = "bidir_2flow"
    active_flow_count: int = 2
    bidirectional: bool = True
    ap_policy: Policy = Policy()
    cpe_policy: Policy | None = Policy()
    goodput_mbps: float = 100
    dl_goodput_mbps: float = 50
    ul_goodput_mbps: float = 50
    p50_ms: float = 2
    p95_ms: float = 5
    p99_ms: float = 6
    packet_loss_pct: float = 0
    restoration_verified: bool = True
    station_drops: int = 0


def with_envelope(*rows):
    """Same policy samples provide an explicit fixture ratio envelope [.25,4]."""
    first = rows[0]
    return [*rows, replace(first, iteration='low-ratio', dl_goodput_mbps=80, ul_goodput_mbps=20),
            replace(first, iteration='high-ratio', dl_goodput_mbps=20, ul_goodput_mbps=80)]


def test_idle_and_supported_flow_direction_regimes_do_not_invent_bulk_cpe():
    bulk = Row(workload_regime='bulk_unidirectional', bidirectional=False,
               cpe_policy=None, dl_goodput_mbps=None, ul_goodput_mbps=None)
    six = Row(iteration='six', workload_regime='bidir_6flow', active_flow_count=6)
    controller = AdaptiveAQLRegimeController([bulk, Row(iteration='two'), six])
    assert controller.select(0, 0, 0)['status'] == 'IDLE'
    assert controller.select(2, 0, 0)['cpe_policy'] is None
    assert controller.select(2, 1, 0)['workload_regime'] == 'bidir_2flow'
    assert controller.select(6, 1, 0)['workload_regime'] == 'bidir_6flow'
    for count, ratio in ((1, 0), (3, 1), (6, 0), (16, 1)):
        assert controller.select(count, ratio, 0)['status'] == 'ABSTAIN'


@pytest.mark.parametrize('count,ratio,retry', [
    (True, 1, 0), (2.0, 1, 0), (-1, 1, 0), (2, True, 0),
    (2, -1, 0), (2, float('inf'), 0), (2, float('nan'), 0),
    (2, 1, True), (2, 1, -.01), (2, 1, 1.01), (2, 1, float('nan')),
])
def test_invalid_telemetry_never_clips_or_selects(count, ratio, retry):
    with pytest.raises(ValueError):
        AdaptiveAQLRegimeController([Row()]).select(count, ratio, retry)


def test_finite_ratio_extreme_abstains_and_empty_or_incomplete_pool_abstains():
    assert AdaptiveAQLRegimeController([Row()]).select(2, 1e300, 0)['status'] == 'ABSTAIN'
    assert AdaptiveAQLRegimeController([]).select(2, 1, 0)['status'] == 'ABSTAIN'
    c = AdaptiveAQLRegimeController([replace(Row(), cpe_policy=None)])
    assert c.select(2, 1, 0)['status'] == 'ABSTAIN'


@pytest.mark.parametrize('change,reason', [
    ({'packet_loss_pct': 5}, 'OBSERVED_PACKET_LOSS'),
    ({'restoration_verified': False}, 'RESTORATION_NOT_REPORTED_TRUE'),
    ({'restoration_verified': None}, 'RESTORATION_NOT_REPORTED_TRUE'),
    ({'station_drops': 1}, 'OBSERVED_STATION_DROP'),
])
def test_loss_unrestored_and_drops_are_excluded(change, reason):
    c = AdaptiveAQLRegimeController([replace(Row(), **change)])
    assert c.excluded[0]['reason'] == reason
    assert c.select(2, 1, 0)['status'] == 'ABSTAIN'


def test_asymmetric_endpoint_policies_and_unknown_fields_are_preserved():
    ap = Policy(dscp_micro_vo_steering=True)
    cpe = Policy(aql_by_ac=((200, 400), (300, 600), (400, 800), (500, 1000)),
                 fq_quantum_bytes=1514, rc_per_thresh=50)
    row = Row(ap_policy=ap, cpe_policy=cpe)
    selected = AdaptiveAQLRegimeController([row]).select(2, 1, .2)
    assert selected['ap_policy'] == policy_metadata(ap)
    assert selected['cpe_policy'] == policy_metadata(cpe)
    assert selected['cpe_policy']['htt_max_ampdu'] is None
    rules = selected['dscp_metadata']['rules']
    assert rules[0]['enabled'] is True and rules[1]['enabled'] is False
    assert all(r['dscp'] == 46 and r['packet_length_lt_bytes'] == 256 for r in rules)
    assert selected['dscp_metadata']['ef_to_vo_mapping'] == 'UNKNOWN'
    assert not selected['dscp_metadata']['executable']


def test_ratio_changes_directional_costs_and_ranking_without_mixing_policies():
    small, large = Policy(), Policy(aql_by_ac=((5000, 12000),)*4)
    a = Row(ap_policy=small, cpe_policy=large)
    b = replace(a, iteration='other', ap_policy=large, cpe_policy=small)
    c = AdaptiveAQLRegimeController(with_envelope(a, b), min_switch_gain=0)
    dl = c.select(2, .25, .8)
    ul = c.select(2, 4, .8)
    assert dl['ap_policy'] == policy_metadata(small)
    assert ul['cpe_policy'] == policy_metadata(small)
    assert dl['policy_id'] != ul['policy_id']
    assert {x['policy_id'] for x in dl['candidates']} == {x['policy_id'] for x in ul['candidates']}


def test_retry_changes_defined_score_and_can_change_choice():
    low = Policy()
    high = Policy(aql_by_ac=((5000, 12000),)*4, rc_per_thresh=50)
    rows = [Row(ap_policy=high, cpe_policy=high, goodput_mbps=120),
            Row(iteration='other', ap_policy=low, cpe_policy=low)]
    c = AdaptiveAQLRegimeController(rows, min_switch_gain=0)
    quiet, busy = c.select(2, 1, 0), c.select(2, 1, 1)
    assert quiet['ap_policy'] == policy_metadata(high)
    assert busy['ap_policy'] == policy_metadata(low)
    assert quiet['score'] != busy['score']
    assert busy['cost_kind'] == 'ASSUMED_POLICY_COST'


def test_deterministic_ties_hysteresis_revalidation_and_nonactuation():
    a = Row()
    b = replace(a, iteration='other', ap_policy=replace(Policy(), dscp_micro_vo_steering=True))
    rows = [a, b]
    c = AdaptiveAQLRegimeController(rows)
    first = c.select(2, 1, 0)
    assert first == AdaptiveAQLRegimeController(list(reversed(rows))).select(2, 1, 0)
    alternative = next(p for p in first['candidates'] if p['policy_id'] != first['policy_id'])
    previous = {**first, 'policy_id': alternative['policy_id'], 'score': 1e100}
    kept = c.select(2, 1, 0, previous=previous)
    assert kept['hysteresis_held'] and kept['score'] != 1e100
    assert c.select(6, 1, 0, previous=previous)['status'] == 'ABSTAIN'
    absent = AdaptiveAQLRegimeController([a]).select(2, 1, 0, previous=previous)
    assert absent['policy_id'] == first['policy_id']
    assert first['automatic_execution_allowed'] is False
    assert first['physical_safety_qualified'] is False
    assert math.isfinite(first['score'])
    json.dumps(first, allow_nan=False)


def test_round_balance_no_duplicate_identity_and_no_silent_type_coercion():
    c = AdaptiveAQLRegimeController([Row(), Row(round_id='round2', goodput_mbps=80)])
    selected = c.select(2, 1, 0)
    assert selected['candidates'][0]['terms']['goodput'] == .9
    with pytest.raises(ValueError, match='Duplicate'):
        AdaptiveAQLRegimeController([Row(), Row()])
    bad = replace(Row(), ap_policy=replace(Policy(), rc_per_thresh=True))
    assert AdaptiveAQLRegimeController([bad]).select(2, 1, 0)['status'] == 'ABSTAIN'


def test_returned_policy_metadata_cannot_mutate_future_selections():
    c = AdaptiveAQLRegimeController([Row()])
    first = c.select(2, 1, .2)
    expected = json.loads(json.dumps(first))
    first['ap_policy']['rc_per_thresh'] = 256
    first['candidates'][0]['ap_policy']['aql_by_ac'][2][1] = 999999
    assert c.select(2, 1, .2) == expected


def test_frozen_58_window_pool_retains_regime_and_endpoint_context():
    from orchestration.autoresearch.fmx_offline_data import load_all_measurements
    rows, provenance = load_all_measurements()
    c = AdaptiveAQLRegimeController(rows)
    assert len(rows) == 58 and len(provenance) == 9
    expected_lossful = {r.iteration for r in rows if r.packet_loss_pct > 0}
    assert len(expected_lossful) == 5
    assert {e['iteration'] for e in c.excluded if e['reason'] == 'OBSERVED_PACKET_LOSS'} == expected_lossful
    assert sum(e['reason'] == 'KNOWN_FAILED_JOINT_POLICY_IN_SAME_REGIME' for e in c.excluded) == 2
    for flows, ratio in ((2, 0), (2, .15), (6, .15)):
        result = c.select(flows, ratio, .1)
        assert result['status'] == 'SELECTED'
        keys = {json.dumps([policy_metadata(r.ap_policy), policy_metadata(r.cpe_policy)],
                           sort_keys=True, separators=(',', ':')) for r in rows
                if r.workload_regime == result['workload_regime'] and r.iteration not in expected_lossful}
        assert result['policy_id'] in keys
        assert not any(e['iteration'] in expected_lossful for p in result['candidates'] for e in p['evidence'])
    assert c.select(2, 1, .1)['status'] == 'ABSTAIN'
    assert c.select(6, 1, .1)['status'] == 'ABSTAIN'


def test_controller_has_no_io_or_actuator_dependency():
    source = Path(__file__).resolve().parents[1]/'controller/adaptive_aql_regime_controller.py'
    tree = ast.parse(source.read_text(encoding='utf-8'))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in {'open', 'exec', 'eval', '__import__', 'compile'}
    assert imports <= {'collections', 'copy', 'json', 'math'}


def test_real_failed_joint_pairs_cannot_reenter_via_successful_duplicate_rows():
    from orchestration.autoresearch.fmx_offline_data import load_all_measurements
    rows, _ = load_all_measurements()
    negative = {(r.workload_regime, r.policy_key) for r in rows
                if r.packet_loss_pct or r.station_drops or not r.restoration_verified}
    c = AdaptiveAQLRegimeController(rows)
    results = [c.select(flows, ratio, .1) for flows, ratio in ((2, 0), (2, .15), (6, .15))]
    for result in results:
        for candidate in result['candidates']:
            assert (result['workload_regime'], candidate['policy_id']) not in negative
    for result in results:
        evidence = result['excluded_policy_evidence']
        known = {(x['workload_regime'], x['policy_id']) for x in evidence}
        assert {p for p in negative if p[0] == result['workload_regime']} <= known
        assert all(x['negative_windows'] for x in evidence)


@pytest.mark.parametrize('negative_change', [
    {'packet_loss_pct': 5}, {'restoration_verified': False}, {'station_drops': 1},
])
def test_known_failed_pair_quarantine_is_order_independent_and_blocks_hysteresis(negative_change):
    good = Row(iteration='previously-passed')
    negative = replace(good, iteration='later-negative', **negative_change)
    previous = AdaptiveAQLRegimeController([good]).select(2, 1, .1)
    for records in ([good, negative], [negative, good]):
        c = AdaptiveAQLRegimeController(records)
        result = c.select(2, 1, .1, previous=previous)
        assert result['status'] == 'ABSTAIN' and result['candidates'] == []
        evidence = result['excluded_policy_evidence'][0]
        assert evidence['negative_windows'][0]['iteration'] == 'later-negative'
        assert evidence['negative_windows'][0]['reasons']
        assert evidence['quarantined_windows'][0]['iteration'] == 'previously-passed'


def test_failed_pair_quarantine_does_not_merge_other_regimes_or_endpoint_asymmetry():
    bad = replace(Row(), iteration='bad', packet_loss_pct=5)
    six = replace(Row(), iteration='six', workload_regime='bidir_6flow', active_flow_count=6)
    asym = replace(Row(), iteration='asymmetric', cpe_policy=replace(Policy(), fq_quantum_bytes=1514))
    c = AdaptiveAQLRegimeController([bad, six, asym])
    assert c.select(6, 1, .1)['status'] == 'SELECTED'
    result = c.select(2, 1, .1)
    assert result['status'] == 'SELECTED'
    assert result['cpe_policy'] == policy_metadata(asym.cpe_policy)
    result['excluded_policy_evidence'][0]['negative_windows'].clear()
    assert c.select(2, 1, .1)['excluded_policy_evidence'][0]['negative_windows']


@dataclass(frozen=True)
class CrossPolicy(Policy):
    fq_target_us: int | None = 10000
    fq_interval_us: int | None = 50000
    tcp_limit_output_bytes: int | None = 262144
    tcp_notsent_lowat: int | None = 131072
    distance_meters: int | None = 3000
    encryption_mode: str | None = 'psk2'


@dataclass(frozen=True)
class CrossRow(Row):
    ap_policy: Policy = CrossPolicy()
    cpe_policy: Policy = CrossPolicy()
    window_kind: str = 'primary'
    source_position: int = 2
    distance_meters: int | None = 3000
    encryption_mode: str | None = 'psk2'
    associated_cpes: tuple = ('Loco195',)
    encryption_evidence: str = 'INFERRED_NOT_EFFECTIVE_READBACK'
    topology_evidence: str = 'OBSERVED_SINGLE_ASSOCIATED_CPE'


@pytest.mark.parametrize('field,value', [
    ('fq_target_us', True), ('fq_target_us', 10000.0), ('fq_interval_us', -1),
    ('tcp_limit_output_bytes', 262144.0), ('tcp_limit_output_bytes', 0),
    ('tcp_notsent_lowat', False), ('tcp_notsent_lowat', 2**32),
    ('distance_meters', 3000.0), ('distance_meters', -1),
    ('distance_meters', True), ('encryption_mode', 'WPA2'),
])
def test_cross_layer_input_domains_do_not_coerce_or_invent_safe_ranges(field, value):
    with pytest.raises(ValueError):
        policy_metadata(replace(CrossPolicy(), **{field: value}))


def test_cross_layer_none_vs_zero_units_and_codel_order_are_preserved():
    p = CrossPolicy(distance_meters=0, tcp_notsent_lowat=0)
    result = policy_metadata(p)
    assert result['distance_meters'] == 0 and result['tcp_notsent_lowat'] == 0
    assert result['fq_target_us'] == 10000 and result['tcp_limit_output_bytes'] == 262144
    unknown = policy_metadata(replace(p, fq_target_us=None, fq_interval_us=None,
        tcp_limit_output_bytes=None, tcp_notsent_lowat=None, distance_meters=None))
    assert unknown['distance_meters'] is None and unknown['tcp_limit_output_bytes'] is None
    with pytest.raises(ValueError, match='target exceeds'):
        policy_metadata(replace(p, fq_interval_us=9999))


def test_whole_codel_tsq_endpoint_packages_and_provenance_select_without_synthesis():
    first = CrossRow()
    second = replace(first, iteration='different-codel-tsq', goodput_mbps=120,
        ap_policy=replace(CrossPolicy(), fq_target_us=5000, fq_interval_us=30000),
        cpe_policy=replace(CrossPolicy(), tcp_limit_output_bytes=131072, tcp_notsent_lowat=65536))
    c = AdaptiveAQLRegimeController([first, second])
    s = c.select(2, 1, .1, distance_meters=3000, encryption_mode='psk2')
    assert s['status'] == 'SELECTED'
    assert s['ap_policy'] == policy_metadata(second.ap_policy)
    assert s['cpe_policy'] == policy_metadata(second.cpe_policy)
    assert len({x['policy_id'] for x in s['candidates']}) == 2
    evidence = next(x for x in s['candidates'] if x['policy_id'] == s['policy_id'])['evidence'][0]
    assert evidence['source_position'] == 2 and evidence['window_kind'] == 'primary'
    assert evidence['encryption_evidence'] == first.encryption_evidence
    assert s['automatic_execution_allowed'] is False


def test_contexts_do_not_average_cipher_topology_or_timing_and_unknown_never_matches_explicit():
    secure = CrossRow()
    open_row = replace(secure, iteration='open', encryption_mode='none',
        ap_policy=replace(CrossPolicy(), encryption_mode='none'),
        cpe_policy=replace(CrossPolicy(), encryption_mode='none'), goodput_mbps=200)
    topology = replace(secure, iteration='two-associated', associated_cpes=('SXT', 'Loco195'))
    different_distance = replace(secure, iteration='nearer', distance_meters=1500,
        ap_policy=replace(CrossPolicy(), distance_meters=1500),
        cpe_policy=replace(CrossPolicy(), distance_meters=1500))
    c = AdaptiveAQLRegimeController([secure, open_row, topology, different_distance, Row(iteration='unknown')])
    assert c.select(2, 1, .1)['reason'] == 'AMBIGUOUS_CONTEXT_REQUIRE_EXPLICIT_CONSTRAINTS'
    s = c.select(2, 1, .1, distance_meters=3000, encryption_mode='psk2', associated_cpes=('Loco195',))
    assert s['status'] == 'SELECTED' and len(s['candidates']) == 1
    assert s['context']['associated_cpes'] == ['Loco195']
    assert s['candidates'][0]['evidence'][0]['iteration'] == secure.iteration
    for kw in ({'distance_meters':3000}, {'encryption_mode':'none'}, {'associated_cpes':('Loco195',)}):
        assert AdaptiveAQLRegimeController([Row()]).select(2, 1, .1, **kw)['status'] == 'ABSTAIN'
    with pytest.raises(ValueError):
        c.select(2, 1, .1, associated_cpes=('Loco195', 'Loco195'))


def test_missing_summary_quality_excluded_before_quarantine_and_context_conflicts_rejected():
    summary = replace(CrossRow(), window_kind='summary_validation',
        packet_loss_pct=None, restoration_verified=None, station_drops=None)
    conflict = replace(CrossRow(), iteration='conflict', distance_meters=0)
    c = AdaptiveAQLRegimeController([summary, CrossRow(), conflict])
    s = c.select(2, 1, .1, distance_meters=3000)
    assert s['status'] == 'SELECTED' and len(s['candidates']) == 1
    assert not s['excluded_policy_evidence']
    assert {e['reason'] for e in c.excluded} == {
        'SUMMARY_OR_UNSUPPORTED_WINDOW_NOT_POLICY_EVIDENCE', 'MALFORMED_OR_INCOMPLETE_MEASUREMENT'}


@pytest.mark.parametrize('change', [{'packet_loss_pct':5}, {'station_drops':1}, {'restoration_verified':False}])
def test_new_fields_negative_alias_quarantine_does_not_contaminate_different_whole_package(change):
    good = CrossRow(iteration='good')
    bad = replace(good, iteration='bad', **change)
    alternative = replace(good, iteration='tsq-different',
        cpe_policy=replace(CrossPolicy(), tcp_limit_output_bytes=131072))
    previous = AdaptiveAQLRegimeController([good]).select(2, 1, .1)
    for rows in ([good, bad, alternative], [alternative, bad, good]):
        s = AdaptiveAQLRegimeController(rows).select(2, 1, .1, previous=previous)
        assert s['status'] == 'SELECTED' and s['policy_id'] != previous['policy_id']
        assert s['cpe_policy']['tcp_limit_output_bytes'] == 131072
        assert s['excluded_policy_evidence'][0]['negative_windows'][0]['iteration'] == 'bad'
        assert s['excluded_policy_evidence'][0]['quarantined_windows'][0]['source_position'] == 2


def test_distance_selects_only_measured_be_options_and_never_extrapolates():
    base = CrossRow()
    scaled_policy = replace(CrossPolicy(), aql_by_ac=((1000, 2000),)*2+((1900, 3800), (1000, 2000)),
                            aql_threshold_us=7600)
    scaled = replace(base, iteration='scaled-package', ap_policy=scaled_policy,
                     cpe_policy=scaled_policy, goodput_mbps=130)
    c = AdaptiveAQLRegimeController([base, scaled])
    s = c.select(2, 1, .1, distance_meters=3000)
    assert s['distance_scaling']['selected_be_us']['AP'] == [1900, 3800]
    assert s['distance_scaling']['synthesized_policy'] is False
    assert s['distance_scaling']['physical_distance_verified'] is False
    assert c.select(2, 1, .1, distance_meters=3001)['status'] == 'ABSTAIN'
    s['distance_scaling']['observed_be_options'][0]['AP'][0] = 999
    assert c.select(2, 1, .1, distance_meters=3000)['distance_scaling']['selected_be_us']['AP'] == [1900, 3800]


def test_real_all14_corpus_preserves_summary_exclusions_r13_scaling_and_r14_one_cpe_context():
    from orchestration.autoresearch.fmx_offline_data import load_all14_measurements
    rows, refs = load_all14_measurements()
    assert len(rows) == 85 and len(refs) == 14
    c = AdaptiveAQLRegimeController(rows)
    assert sum(e['reason']=='SUMMARY_OR_UNSUPPORTED_WINDOW_NOT_POLICY_EVIDENCE' for e in c.excluded) == 2
    for distance, encryption, selected_round in ((3000, 'psk2', 'R13'), (None, 'none', 'R14')):
        supported = [r for r in rows if r.window_kind=='primary' and r.distance_meters==distance
                     and r.encryption_mode==encryption and r.packet_loss_pct==0]
        ratio = supported[0].ul_goodput_mbps/supported[0].dl_goodput_mbps
        s = c.select(6, ratio, .1, distance_meters=distance, encryption_mode=encryption,
                     associated_cpes=('Loco195',))
        assert s['status'] == 'SELECTED'
        assert {e['round_id'] for p in s['candidates'] for e in p['evidence']} == {selected_round}
        assert s['context']['associated_cpes'] == ['Loco195']
        if distance==3000:
            assert {tuple(o['AP']) for o in s['distance_scaling']['observed_be_options']} >= {(1800,3600),(1900,3800)}
        else:
            assert not s['physical_safety_qualified']
    assert c.select(6, .15, .1, encryption_mode='psk2', associated_cpes=('Loco195','SXT','LBM5'))['status']=='ABSTAIN'


def test_context_omitted_none_and_exact_are_three_distinct_queries():
    unknown = replace(CrossRow(), distance_meters=None,
        ap_policy=replace(CrossPolicy(), distance_meters=None),
        cpe_policy=replace(CrossPolicy(), distance_meters=None))
    known = replace(CrossRow(), iteration='known')
    c = AdaptiveAQLRegimeController([unknown, known])
    assert c.select(2, 1, .1)['status']=='ABSTAIN'
    s = c.select(2, 1, .1, distance_meters=None)
    assert s['status']=='SELECTED' and s['context']['distance_meters'] is None
    assert s['context_constraints']['distance_meters'] is True
    assert c.select(2, 1, .1, distance_meters=3000)['context']['distance_meters']==3000
    assert c.select(2, 1, .1, encryption_mode=None)['status']=='ABSTAIN'


def test_hysteresis_cannot_carry_policy_preference_across_topology_context():
    a = CrossRow(iteration='a')
    b = replace(a, iteration='b', ap_policy=replace(CrossPolicy(), fq_quantum_bytes=256), goodput_mbps=100.1)
    old = AdaptiveAQLRegimeController([a]).select(2, 1, 0)
    rows = [replace(r, associated_cpes=('SXT','Loco195')) for r in (a,b)]
    c = AdaptiveAQLRegimeController(rows, min_switch_gain=1)
    result = c.select(2, 1, 0, previous=old, associated_cpes=('Loco195','SXT'))
    assert result['policy_id'] != old['policy_id'] and result['hysteresis_held'] is False


@pytest.mark.parametrize('kwargs', [
    {'distance_meters':True}, {'distance_meters':3000.0}, {'distance_meters':float('nan')},
    {'encryption_mode':False}, {'encryption_mode':[]}, {'associated_cpes':[]},
])
def test_invalid_explicit_context_is_rejected(kwargs):
    with pytest.raises(ValueError):
        AdaptiveAQLRegimeController([CrossRow()]).select(2,1,.1,**kwargs)


@pytest.mark.parametrize('endpoint', ['ap_policy', 'cpe_policy'])
@pytest.mark.parametrize('field', ['distance_meters', 'encryption_mode'])
def test_cross_layer_explicit_unknown_endpoint_cannot_inherit_known_window_context(endpoint, field):
    bad = replace(CrossRow(), **{endpoint: replace(CrossPolicy(), **{field: None})})
    result = AdaptiveAQLRegimeController([bad]).select(2, 1, .1,
        distance_meters=3000, encryption_mode='psk2')
    assert result['status'] == 'ABSTAIN'


@pytest.mark.parametrize('endpoint', ['ap_policy', 'cpe_policy'])
def test_legacy_endpoint_without_context_fields_cannot_satisfy_explicit_cross_layer_context(endpoint):
    row = replace(CrossRow(), **{endpoint: Policy()})
    result = AdaptiveAQLRegimeController([row]).select(2, 1, .1,
        distance_meters=3000, encryption_mode='psk2')
    assert result['status'] == 'ABSTAIN'


def test_explicit_codel_tsq_constraints_select_whole_observed_package_before_ranking():
    wanted = CrossRow(iteration='wanted')
    faster = replace(wanted, iteration='faster-but-wrong-tsq', goodput_mbps=1000,
                     cpe_policy=replace(CrossPolicy(), tcp_limit_output_bytes=131072))
    unknown = Row(iteration='unknown', goodput_mbps=2000)
    c = AdaptiveAQLRegimeController([wanted, faster, unknown])
    s = c.select(2, 1, .1, fq_target_us=10000, fq_interval_us=50000,
                 tcp_limit_output_bytes=262144, tcp_notsent_lowat=131072)
    assert s['status']=='SELECTED' and len(s['candidates'])==1
    assert s['ap_policy']==policy_metadata(wanted.ap_policy)
    assert s['cpe_policy']==policy_metadata(wanted.cpe_policy)
    assert all(v['specified'] for v in s['policy_constraints'].values())
    assert s['policy_constraints']['fq_target_us']['value']==10000
    assert c.select(2,1,.1,fq_target_us=None)['ap_policy']==policy_metadata(unknown.ap_policy)
    assert AdaptiveAQLRegimeController([unknown]).select(2,1,.1,fq_target_us=10000)['status']=='ABSTAIN'


@pytest.mark.parametrize('name,value', [
    ('fq_target_us', True), ('fq_target_us', 10000.0), ('fq_target_us', 0),
    ('fq_interval_us', float('inf')), ('fq_interval_us', -1),
    ('tcp_limit_output_bytes', '262144'), ('tcp_limit_output_bytes', 2**32),
    ('tcp_notsent_lowat', False), ('tcp_notsent_lowat', float('nan')),
])
def test_invalid_explicit_codel_tsq_constraints_do_not_coerce(name,value):
    with pytest.raises(ValueError):
        AdaptiveAQLRegimeController([CrossRow()]).select(2,1,.1,**{name:value})


def test_knob_constraints_preserve_zero_uint32_and_unknown_cpe_without_fabrication():
    p = replace(CrossPolicy(), tcp_notsent_lowat=2**32-1)
    row = replace(CrossRow(), ap_policy=p, cpe_policy=p)
    assert AdaptiveAQLRegimeController([row]).select(2,1,.1,tcp_notsent_lowat=2**32-1)['status']=='SELECTED'
    zero = replace(p,tcp_notsent_lowat=0)
    bulk = replace(row, workload_regime='bulk_unidirectional',bidirectional=False,
                   ap_policy=zero,cpe_policy=None,ul_goodput_mbps=None,dl_goodput_mbps=None)
    result=AdaptiveAQLRegimeController([bulk]).select(2,0,.1,tcp_notsent_lowat=0)
    assert result['status']=='SELECTED' and result['cpe_policy'] is None
    assert result['ap_policy']['tcp_notsent_lowat']==0


def test_real_all14_explicit_codel_tsq_package_query_has_no_unknown_endpoints():
    from orchestration.autoresearch.fmx_offline_data import load_all14_measurements
    rows,_=load_all14_measurements()
    actual=next(r for r in rows if r.round_id=='R12' and r.iteration=='r12_iter1_r9_r11_universal_winner_n40')
    s=AdaptiveAQLRegimeController(rows).select(6,actual.ul_goodput_mbps/actual.dl_goodput_mbps,.1,distance_meters=None,
        encryption_mode='psk2',fq_target_us=10000,fq_interval_us=50000,
        tcp_limit_output_bytes=262144,tcp_notsent_lowat=131072)
    assert s['status']=='SELECTED'
    for candidate in s['candidates']:
        for endpoint in ('ap_policy','cpe_policy'):
            assert [candidate[endpoint][k] for k in ('fq_target_us','fq_interval_us',
                'tcp_limit_output_bytes','tcp_notsent_lowat')]==[10000,50000,262144,131072]


@dataclass(frozen=True)
class ThreeTierRow(CrossRow):
    ap_ack_pps: int | None = 50
    cpe_ack_pps: int | None = 0
    ap_tcp_ack_vi: bool | None = True
    cpe_tcp_ack_vi: bool | None = False
    ap_ack_burst: int | None = 64
    cpe_ack_burst: int | None = 64
    cpu_telemetry: dict | None = None
    summary_consistency: dict | None = None
    flags: tuple = ()


def test_three_tier_opt_in_required_and_legacy_default_result_unchanged():
    old=CrossRow(iteration='old')
    new=ThreeTierRow(iteration='new',goodput_mbps=1000)
    original=AdaptiveAQLRegimeController([old]).select(2,1,.1)
    c=AdaptiveAQLRegimeController([old,new])
    assert c.select(2,1,.1)==original
    assert c.excluded==[dict(round_id=new.round_id,iteration='new',reason='THREE_TIER_OPT_IN_REQUIRED')]
    with pytest.raises(ValueError,match='include_three_tier'):
        c.select(2,1,.1,ap_ack_pps=None)
    with pytest.raises(ValueError):AdaptiveAQLRegimeController([],include_three_tier=1)


def test_endpoint_ack_constraints_return_complete_observed_package_and_provenance():
    row=ThreeTierRow(cpu_telemetry={'AP':{'idle_pct':80}})
    result=AdaptiveAQLRegimeController([row],include_three_tier=True).select(
        2,1,.1,ap_ack_pps=50,cpe_ack_pps=0,ap_tcp_ack_vi=True,cpe_tcp_ack_vi=False)
    assert result['status']=='SELECTED'
    assert result['ap_policy']['ack_pps']==50 and result['cpe_policy']['ack_pps']==0
    assert result['ap_policy']['tcp_ack_vi'] is True and result['cpe_policy']['tcp_ack_vi'] is False
    assert result['ap_policy']['ack_burst']==64
    assert result['candidates'][0]['evidence'][0]['cpu_telemetry_available'] is True
    assert result['candidates'][0]['evidence'][0]['cpu_telemetry_used_for_score'] is False
    assert not result['automatic_execution_allowed'] and not result['physical_safety_qualified']
    assert all(x['specified'] for x in result['ack_constraints'].values())


def test_unknown_disabled_and_enabled_ack_fields_never_pool_or_match_each_other():
    none=dict(ap_ack_pps=None,cpe_ack_pps=None,ap_tcp_ack_vi=None,cpe_tcp_ack_vi=None,
              ap_ack_burst=None,cpe_ack_burst=None)
    unknown=ThreeTierRow(iteration='unknown',**none)
    disabled=replace(unknown,iteration='disabled',ap_ack_pps=0,cpe_ack_pps=0,
                     ap_tcp_ack_vi=False,cpe_tcp_ack_vi=False)
    on=replace(unknown,iteration='on',ap_ack_pps=50,cpe_ack_pps=500,
               ap_tcp_ack_vi=True,cpe_tcp_ack_vi=True)
    c=AdaptiveAQLRegimeController([unknown,disabled,on],include_three_tier=True)
    unfiltered=c.select(2,1,.1)
    assert len(unfiltered['candidates'])==len({p['policy_id'] for p in unfiltered['candidates']})==3
    for rate,vi,name in ((None,None,'unknown'),(0,False,'disabled'),(50,True,'on')):
        r=c.select(2,1,.1,ap_ack_pps=rate,ap_tcp_ack_vi=vi)
        assert r['status']=='SELECTED' and len(r['candidates'])==1
        assert r['candidates'][0]['evidence'][0]['iteration']==name
    assert c.select(2,1,.1,ap_ack_pps=50,cpe_ack_pps=0)['status']=='ABSTAIN'


@pytest.mark.parametrize('change',[
    {'ap_ack_pps':True},{'ap_ack_pps':50.0},{'cpe_ack_pps':-1},{'cpe_ack_pps':2**32},
    {'ap_tcp_ack_vi':1},{'cpe_tcp_ack_vi':'true'},
])
def test_invalid_ack_queries_reject_without_boolean_or_numeric_coercion(change):
    c=AdaptiveAQLRegimeController([ThreeTierRow()],include_three_tier=True)
    with pytest.raises(ValueError):c.select(2,1,.1,**change)


@pytest.mark.parametrize('change',[
    {'ap_ack_pps':True},{'ap_ack_burst':64.0},{'cpe_ack_burst':-1},
    {'cpe_ack_pps':float('nan')},{'ap_tcp_ack_vi':0},
])
def test_invalid_observed_ack_fields_exclude_package_instead_of_guessing(change):
    c=AdaptiveAQLRegimeController([replace(ThreeTierRow(),**change)],include_three_tier=True)
    assert c.select(2,1,.1)['status']=='ABSTAIN'
    assert c.excluded[0]['reason']=='MALFORMED_OR_INCOMPLETE_MEASUREMENT'


def test_burst_and_endpoint_direction_are_part_of_full_package_identity():
    a=ThreeTierRow(iteration='burst1',ap_ack_burst=1)
    b=replace(a,iteration='burst64',ap_ack_burst=64,goodput_mbps=120)
    c=replace(a,iteration='endpoint-swapped',ap_ack_pps=0,cpe_ack_pps=50,
              ap_tcp_ack_vi=False,cpe_tcp_ack_vi=True)
    ctrl=AdaptiveAQLRegimeController([a,b,c],include_three_tier=True)
    r=ctrl.select(2,1,.1)
    assert len({p['policy_id'] for p in r['candidates']})==3
    assert r['ap_policy']['ack_burst']==64
    r['ap_policy']['ack_pps']=999
    assert ctrl.select(2,1,.1)['ap_policy']['ack_pps']==50


def test_ack_filter_precedes_ratio_support_and_hysteresis():
    a=ThreeTierRow(iteration='a',dl_goodput_mbps=80,ul_goodput_mbps=20)
    b=replace(a,iteration='b',ap_ack_pps=500,dl_goodput_mbps=20,ul_goodput_mbps=80)
    c=AdaptiveAQLRegimeController([a,b],include_three_tier=True,min_switch_gain=10)
    previous=c.select(2,.25,.1,ap_ack_pps=50)
    assert c.select(2,.25,.1,ap_ack_pps=500,previous=previous)['status']=='ABSTAIN'
    result=c.select(2,4,.1,ap_ack_pps=500,previous=previous)
    assert result['status']=='SELECTED' and result['ap_policy']['ack_pps']==500


@pytest.mark.parametrize('change',[{'packet_loss_pct':5},{'station_drops':1},{'restoration_verified':False}])
def test_three_tier_negative_pair_cannot_reenter_through_positive_alias_or_previous(change):
    good=ThreeTierRow(iteration='good')
    bad=replace(good,iteration='bad',**change)
    other=replace(good,iteration='other',ap_ack_burst=1)
    prior=AdaptiveAQLRegimeController([good],include_three_tier=True).select(2,1,.1)
    for rows in ([good,bad,other],[other,bad,good]):
        r=AdaptiveAQLRegimeController(rows,include_three_tier=True).select(2,1,.1,previous=prior)
        assert r['status']=='SELECTED' and r['ap_policy']['ack_burst']==1
        assert r['excluded_policy_evidence'][0]['quarantined_windows'][0]['iteration']=='good'


def test_legacy_negative_and_new_all_unknown_ack_alias_remain_same_failed_package():
    bad=replace(CrossRow(),iteration='legacy-bad',packet_loss_pct=5)
    new=ThreeTierRow(iteration='new-unknown',ap_ack_pps=None,cpe_ack_pps=None,
        ap_tcp_ack_vi=None,cpe_tcp_ack_vi=None,ap_ack_burst=None,cpe_ack_burst=None)
    r=AdaptiveAQLRegimeController([bad,new],include_three_tier=True).select(2,1,.1)
    assert r['status']=='ABSTAIN'
    assert r['excluded_policy_evidence'][0]['negative_windows'][0]['iteration']=='legacy-bad'
    assert r['excluded_policy_evidence'][0]['quarantined_windows'][0]['iteration']=='new-unknown'


@pytest.mark.parametrize('consistency,flags',[
    ({'consistent':False},()),({'consistent':True},('reported_summary_disagrees_with_repetition_blocks',)),
    ({'consistent':0},()),
])
def test_inconsistent_or_malformed_summary_is_preserved_but_not_promoted(consistency,flags):
    row=ThreeTierRow(goodput_mbps=9999,summary_consistency=consistency,flags=flags)
    c=AdaptiveAQLRegimeController([row],include_three_tier=True)
    r=c.select(2,1,.1,ap_ack_pps=50)
    assert r['status']=='ABSTAIN' and r['candidates']==[]
    assert r['unusable_three_tier_evidence'][0]['summary_consistency']==consistency
    assert r['unusable_three_tier_evidence'][0]['ack_controls']['AP']['ack_pps']==50
    assert r['excluded_policy_evidence']==[] # Measurement conflict is not a wireless failure.
    r['unusable_three_tier_evidence'][0]['summary_consistency']['consistent']='tampered'
    assert c.select(2,1,.1)['unusable_three_tier_evidence'][0]['summary_consistency']==consistency


def test_quality_negative_priority_is_not_erased_by_summary_inconsistency():
    bad=ThreeTierRow(iteration='bad',packet_loss_pct=2.5,summary_consistency={'consistent':False})
    alias=replace(bad,iteration='positive-alias',packet_loss_pct=0,summary_consistency={'consistent':True})
    c=AdaptiveAQLRegimeController([bad,alias],include_three_tier=True)
    r=c.select(2,1,.1)
    assert r['status']=='ABSTAIN' and len(r['unusable_three_tier_evidence'])==1
    assert r['excluded_policy_evidence'][0]['negative_windows'][0]['reasons']==['OBSERVED_PACKET_LOSS']
    assert r['excluded_policy_evidence'][0]['quarantined_windows'][0]['iteration']=='positive-alias'


def test_real112_opt_in_ingests_and_preserves_all_inconsistent_rows_without_promoting_them():
    from orchestration.autoresearch.fmx_offline_data import load_all21_measurements,ThreeTierMeasurement
    rows,refs=load_all21_measurements();new=[r for r in rows if isinstance(r,ThreeTierMeasurement)]
    assert len(rows)==112 and len(refs)==21 and len(new)==23
    c=AdaptiveAQLRegimeController(rows,include_three_tier=True)
    result=c.select(6,.3,.1,distance_meters=None,encryption_mode='psk2')
    assert len(result['unusable_three_tier_evidence'])==23
    assert all(not e['summary_consistency']['consistent'] for e in result['unusable_three_tier_evidence'])
    for row in new:
        evidence=next(e for e in result['unusable_three_tier_evidence']
                      if (e['round_id'],e['iteration'])==(row.round_id,row.iteration))
        assert evidence['source_policy_id']==row.policy_key
        for end in ('AP','CPE'):
            assert evidence['ack_controls'][end]=={name:getattr(row,end.lower()+'_'+name)
                for name in ('ack_pps','tcp_ack_vi','ack_burst')}
    assert all(int(e['round_id'][1:])<=15 for p in result['candidates'] for e in p['evidence'])
    assert sum(e['reason']=='OBSERVED_PACKET_LOSS' for e in c.excluded)==9 # sevenold+twonew
    for kwargs in ({'ap_ack_pps':50},{'ap_ack_pps':0},{'ap_tcp_ack_vi':True},{'cpe_tcp_ack_vi':False}):
        assert c.select(6,.3,.1,**kwargs)['status']=='ABSTAIN'


def test_real112_default_exactly_matches_legacy89_result_and_source_constructor_is_nonmutating():
    from orchestration.autoresearch.fmx_offline_data import load_all21_measurements,load_all15_measurements
    allrows,_=load_all21_measurements();oldrows,_=load_all15_measurements()
    c=AdaptiveAQLRegimeController(allrows)
    assert sum(e['reason']=='THREE_TIER_OPT_IN_REQUIRED' for e in c.excluded)==23
    for ratio in (.2,.3):
        kw=dict(distance_meters=None,encryption_mode='psk2')
        assert c.select(6,ratio,.1,**kw)==AdaptiveAQLRegimeController(oldrows).select(6,ratio,.1,**kw)
    before=[r.policy_key for r in allrows]
    AdaptiveAQLRegimeController(allrows,include_three_tier=True).select(6,.3,.1)
    assert [r.policy_key for r in allrows]==before


@dataclass(frozen=True)
class LowerMACRow(ThreeTierRow):
    short_retry_limit: int | None = 6
    long_retry_limit: int | None = 3
    force_tx_status: int | None = 1
    ani_enable: int | None = 1
    airtime_flags: int | None = 1
    fq_limit: int | None = 2048
    lower_mac_evidence: str = 'SYNTHETIC_DECLARATION_NOT_EFFECTIVE_HARDWARE_PROOF'
    summary_consistency: dict | None = None


def lower_row(**kwargs):
    return LowerMACRow(summary_consistency={'consistent':True},**kwargs)


def test_lower_mac_opt_in_is_separate_and_default_and_three_tier_results_stay_exact():
    old=ThreeTierRow(iteration='old')
    new=lower_row(iteration='new',goodput_mbps=999)
    for kwargs in ({},{'include_three_tier':True}):
        c=AdaptiveAQLRegimeController([old,new],**kwargs)
        assert c.select(2,1,.1)==AdaptiveAQLRegimeController([old],**kwargs).select(2,1,.1)
        assert any(e['reason']=='LOWER_MAC_OPT_IN_REQUIRED' for e in c.excluded)
    c=AdaptiveAQLRegimeController([new],include_lower_mac=True)
    r=c.select(2,1,.1,short_retry_limit=6,long_retry_limit=3,force_tx_status=1,
               ani_enable=1,airtime_flags=1,fq_limit=2048)
    assert r['status']=='SELECTED' and r['three_tier_policy_schema'] is True
    assert r['lower_mac_policy_schema'] is True
    for name in ('short_retry_limit','long_retry_limit','force_tx_status','ani_enable','airtime_flags','fq_limit'):
        assert r['ap_policy'][name]==r['cpe_policy'][name]==getattr(new,name)
    assert r['ap_policy']['ack_pps']==50 and r['cpe_policy']['ack_pps']==0
    assert r['automatic_execution_allowed'] is r['physical_safety_qualified'] is False


def test_lower_mac_constraints_cannot_be_used_without_explicit_opt_in():
    c=AdaptiveAQLRegimeController([ThreeTierRow()],include_three_tier=True)
    with pytest.raises(ValueError,match='include_lower_mac'):
        c.select(2,1,.1,force_tx_status=None)
    with pytest.raises(ValueError):AdaptiveAQLRegimeController([],include_lower_mac=1)


@pytest.mark.parametrize('name,bad',[
    ('short_retry_limit',True),('short_retry_limit',256),('short_retry_limit',6.0),
    ('long_retry_limit',-1),('long_retry_limit','3'),('force_tx_status',True),
    ('force_tx_status',2),('ani_enable',False),('ani_enable',-1),
    ('airtime_flags',4),('airtime_flags',float('nan')),('fq_limit',0),
    ('fq_limit',2**32),('fq_limit',2048.0),
])
def test_lower_mac_query_and_source_exact_encoding_domains(name,bad):
    c=AdaptiveAQLRegimeController([lower_row()],include_lower_mac=True)
    with pytest.raises(ValueError):c.select(2,1,.1,**{name:bad})
    malformed=replace(lower_row(),**{name:bad})
    c=AdaptiveAQLRegimeController([malformed],include_lower_mac=True)
    assert c.select(2,1,.1)['status']=='ABSTAIN'
    assert c.excluded[0]['reason']=='MALFORMED_OR_INCOMPLETE_MEASUREMENT'


def test_lower_mac_unknown_zero_and_one_identity_and_returned_metadata_are_independent():
    from controller.adaptive_aql_regime_controller import LOWER_MAC_DOMAINS
    unknown=replace(lower_row(),iteration='unknown',**{name:None for name in LOWER_MAC_DOMAINS})
    zero=replace(unknown,iteration='zero',short_retry_limit=0,long_retry_limit=0,
                 force_tx_status=0,ani_enable=0,airtime_flags=0,fq_limit=1)
    one=replace(zero,iteration='one',force_tx_status=1)
    c=AdaptiveAQLRegimeController([unknown,zero,one],include_lower_mac=True)
    assert len(c.select(2,1,.1)['candidates'])==3
    for value,iteration in ((None,'unknown'),(0,'zero'),(1,'one')):
        r=c.select(2,1,.1,force_tx_status=value)
        assert r['status']=='SELECTED' and len(r['candidates'])==1
        assert r['candidates'][0]['evidence'][0]['iteration']==iteration
        assert r['ap_policy']['force_tx_status']==r['cpe_policy']['force_tx_status']==value
    r=c.select(2,1,.1,force_tx_status=1)
    r['ap_policy']['fq_limit']=9999
    r['candidates'][0]['evidence'][0]['lower_mac_controls']['force_tx_status']=9
    again=c.select(2,1,.1,force_tx_status=1)
    assert again['ap_policy']['fq_limit']==1
    assert again['candidates'][0]['evidence'][0]['lower_mac_controls']['force_tx_status']==1


def test_every_lower_mac_field_and_ack_burst_participates_in_complete_pair_identity():
    from controller.adaptive_aql_regime_controller import LOWER_MAC_DOMAINS
    first=lower_row(iteration='first')
    rows=[first]+[replace(first,iteration=name,**{name:getattr(first,name)-1})
                  for name in LOWER_MAC_DOMAINS]
    rows+=[replace(first,iteration='burst',cpe_ack_burst=3)]
    r=AdaptiveAQLRegimeController(rows,include_lower_mac=True).select(2,1,.1)
    assert len(r['candidates'])==len(rows)==len({p['policy_id'] for p in r['candidates']})
    assert all(json.loads(p['policy_id'])==[p['ap_policy'],p['cpe_policy']] for p in r['candidates'])


def test_lower_mac_filter_precedes_ratio_support_hysteresis_and_never_synthesizes_mixed_fields():
    first=lower_row(iteration='good_old',goodput_mbps=1000,force_tx_status=0,
                    dl_goodput_mbps=80,ul_goodput_mbps=20)
    second=replace(first,iteration='new',goodput_mbps=100,force_tx_status=1,fq_limit=8192,
                   dl_goodput_mbps=20,ul_goodput_mbps=80)
    c=AdaptiveAQLRegimeController([first,second],include_lower_mac=True,min_switch_gain=10)
    prior=c.select(2,.25,.1,force_tx_status=0)
    assert c.select(2,.25,.1,force_tx_status=1,previous=prior)['status']=='ABSTAIN'
    current=c.select(2,4,.1,force_tx_status=1,previous=prior)
    assert current['status']=='SELECTED' and current['policy_id']!=prior['policy_id']
    assert current['ap_policy']['fq_limit']==current['cpe_policy']['fq_limit']==8192
    assert c.select(2,4,.1,force_tx_status=1,fq_limit=2048)['status']=='ABSTAIN'


@pytest.mark.parametrize('change',[{'packet_loss_pct':1},{'station_drops':1},{'restoration_verified':False}])
def test_lower_mac_failed_complete_package_is_quarantined_even_with_previous(change):
    row=lower_row(iteration='positive')
    c=AdaptiveAQLRegimeController([row],include_lower_mac=True)
    prior=c.select(2,1,.1)
    negative=replace(row,iteration='negative',**change)
    c=AdaptiveAQLRegimeController([row,negative],include_lower_mac=True)
    result=c.select(2,1,.1,previous=prior)
    assert result['status']=='ABSTAIN'
    assert result['excluded_policy_evidence'][0]['policy_id']==prior['policy_id']
    assert result['excluded_policy_evidence'][0]['quarantined_windows'][0]['iteration']=='positive'


def test_old_negative_cannot_reenter_as_new_unknown_lower_mac_package():
    from controller.adaptive_aql_regime_controller import LOWER_MAC_DOMAINS
    old=ThreeTierRow(iteration='negative',packet_loss_pct=1)
    new=replace(lower_row(),iteration='alias',**{name:None for name in LOWER_MAC_DOMAINS})
    c=AdaptiveAQLRegimeController([old,new],include_lower_mac=True)
    r=c.select(2,1,.1)
    assert r['status']=='ABSTAIN'
    assert r['excluded_policy_evidence'][0]['quarantined_windows'][0]['iteration']=='alias'


@pytest.mark.parametrize('consistency,reason',[
    (None,'MISSING_LOWER_MAC_SUMMARY_CONSISTENCY'),
    ({},'MALFORMED_SUMMARY_CONSISTENCY'),
    ({'consistent':1},'MALFORMED_SUMMARY_CONSISTENCY'),
    ({'consistent':False},'REPORTED_SUMMARY_DISAGREES_WITH_REPETITION_BLOCKS'),
])
def test_lower_mac_missing_malformed_or_disagreeing_source_cannot_promote(consistency,reason):
    row=LowerMACRow(summary_consistency=consistency)
    c=AdaptiveAQLRegimeController([row],include_lower_mac=True)
    r=c.select(2,1,.1)
    assert r['status']=='ABSTAIN' and c.excluded[0]['reason']==reason
    assert r['unusable_three_tier_evidence'][0]['summary_consistency']==consistency
    assert r['excluded_policy_evidence']==[] # an acquisition issue is not an RF failure


def test_lower_mac_disagreement_does_not_mask_a_real_negative_and_flag_cannot_bypass_consistency():
    row=lower_row(iteration='positive')
    bad=replace(row,iteration='negative',packet_loss_pct=5,
                summary_consistency={'consistent':False})
    c=AdaptiveAQLRegimeController([row,bad],include_lower_mac=True)
    r=c.select(2,1,.1)
    assert r['status']=='ABSTAIN' and r['excluded_policy_evidence'][0]['negative_windows'][0]['iteration']=='negative'
    assert r['unusable_three_tier_evidence'][0]['reason']=='REPORTED_SUMMARY_DISAGREES_WITH_REPETITION_BLOCKS'
    flagged=replace(row,flags=('reported_summary_disagrees_with_repetition_blocks',))
    assert AdaptiveAQLRegimeController([flagged],include_lower_mac=True).select(2,1,.1)['status']=='ABSTAIN'


def test_real131_lower_mac_preserves_sources_and_abstains_on_all_known_new_hooks():
    from orchestration.autoresearch.fmx_offline_data import load_all26_measurements,LowerMACMeasurement
    from controller.adaptive_aql_regime_controller import LOWER_MAC_DOMAINS
    rows,refs=load_all26_measurements()
    new=[r for r in rows if isinstance(r,LowerMACMeasurement)]
    assert len(rows)==131 and len(new)==19 and len(refs)==26
    before=[r.policy_key for r in rows]
    c=AdaptiveAQLRegimeController(rows,include_lower_mac=True)
    r=c.select(6,.3,.1,distance_meters=None,encryption_mode='psk2',associated_cpes=('Loco195',))
    assert len(r['unusable_three_tier_evidence'])==42 # old23+new19, including real quality negatives
    for row in new:
        evidence=next(e for e in r['unusable_three_tier_evidence']
                      if (e['round_id'],e['iteration'])==(row.round_id,row.iteration))
        assert evidence['source_policy_id']==row.policy_key
        assert evidence['lower_mac_controls']=={name:getattr(row,name) for name in LOWER_MAC_DOMAINS}
        assert evidence['summary_consistency']==row.summary_consistency
        assert evidence['summary_consistency']['consistent'] is False
        assert json.loads(row.policy_key)[0]['ack_burst']==row.ap_ack_burst
        assert json.loads(row.policy_key)[1]['ack_burst']==row.cpe_ack_burst
    assert sum(row.packet_loss_pct>0 for row in new)==4
    for name,value in [('short_retry_limit',6),('long_retry_limit',3),('force_tx_status',1),
                       ('ani_enable',0),('airtime_flags',1),('fq_limit',2048)]:
        assert c.select(6,.3,.1,**{name:value})['status']=='ABSTAIN'
    assert all(int(e['round_id'][1:])<22 for p in r['candidates'] for e in p['evidence'])
    assert [row.policy_key for row in rows]==before


def test_real131_without_lower_mac_exactly_replays_prior112_both_default_and_three_tier():
    from orchestration.autoresearch.fmx_offline_data import load_all26_measurements,load_all21_measurements
    rows,_=load_all26_measurements();old,_=load_all21_measurements()
    for kwargs in ({},{'include_three_tier':True}):
        c=AdaptiveAQLRegimeController(rows,**kwargs)
        assert sum(e['reason']=='LOWER_MAC_OPT_IN_REQUIRED' for e in c.excluded)==19
        for ratio in (.2,.3):
            query=dict(distance_meters=None,encryption_mode='psk2',associated_cpes=('Loco195',))
            assert c.select(6,ratio,.1,**query)==AdaptiveAQLRegimeController(old,**kwargs).select(6,ratio,.1,**query)
