"""Disposable saved-data fixtures only; never imports an acquisition helper."""
from copy import deepcopy
import numpy as np
import pytest

from analysis.statistics.fmx_crossed_mixed_effects import (
    build_crossed_table, crossover_design, fit_descriptive_crossover, full_package,
)


def sample():
    policy = dict(aql_by_ac=[[500, 1000]] * 4, aql_threshold_us=4000,
                  fq_quantum_bytes=256, rc_per_thresh=28, dscp_micro_vo_steering=False)
    records, crossed = [], []
    for arm in (0, 1):
        records.append(dict(round_id="R48", iteration=f"arm{arm}", workload_regime="bidir_6flow",
                            active_flow_count=6, bidirectional=True, ap_policy=deepcopy(policy),
                            cpe_policy=deepcopy(policy), distance_meters=3000, coverage_class=6,
                            associated_cpes=["lab-peer"], encryption_mode="psk2",
                            restoration_verified=True, station_drops=0, packet_loss_pct=0,
                            source_position=f"/iterations/{arm}"))
        for index in range(4):
            period = arm if index % 2 == 0 else 1 - arm
            crossed.append(dict(round_id="R48", treatment_id=f"arm{arm}", block_index=index,
                                crossover_step=period, source_position=f"/iterations/{arm}/blocks/{index}",
                                observation=dict(p95_rtt_ms=10 + index + period - 3 * arm,
                                                 restoration_verified=True, station_drops=0, packet_loss_pct=0)))
    return {"records": records}, {"crossed": crossed, "sequential": [{"preserved": "no fit"}]}


def test_preserves_rows_complete_package_and_sequential_without_inventing_range():
    d, b = sample()
    d["records"][0].update(ap_ack_pps=0, cpe_ack_pps=None, force_tx_status=1)
    t = build_crossed_table(d, b)
    assert t["counts"] == dict(records=2, crossed_rows=8, matched_round_scoped_ids=4, sequential_rows=1)
    assert t["sequential_rows_excluded_from_crossed_model"] == b["sequential"]
    assert t["rows"][0]["endpoint_policies"][0]["ack_pps"] == 0
    assert t["rows"][0]["endpoint_policies"][1]["ack_pps"] is None
    assert t["rows"][0]["endpoint_policies"][1]["force_tx_status"] == 1
    assert t["rows"][0]["context"]["distance_meters"] == 3000
    assert not t["physical_acceptance"] and not t["random_effects_specification"]["fitted"]
    t["rows"][0]["source_block"]["observation"]["p95_rtt_ms"] = 999
    assert b["crossed"][0]["observation"]["p95_rtt_ms"] != 999


def test_full_carryover_alias_blocks_arbitrary_coefficients():
    t = build_crossed_table(*sample())
    _, x, d = crossover_design(t, "R48", "arm1")
    assert x.shape == (8, 7) and d["rank"] == 6 and not d["estimable"]
    result = fit_descriptive_crossover(t, "R48", "arm1")
    assert result["status"] == "NOT_ESTIMABLE" and result["coefficients"] is None


def test_restricted_descriptive_fit_recovers_known_shift_not_causal_pvalue():
    t = build_crossed_table(*sample())
    r = fit_descriptive_crossover(t, "R48", "arm1", include_carryover=False)
    assert r["status"] == "FITTED_DESCRIPTIVE_RESTRICTED_OLS"
    assert r["coefficients"]["current_treatment"] == pytest.approx(-3)
    assert r["coefficients"]["period"] == pytest.approx(1)
    assert r["p_values"] is None and not r["causal_acceptance"]


@pytest.mark.parametrize("kind", ["loss", "restore", "drops", "unknown", "crash"])
def test_negative_and_unknown_quality_preserved_but_cannot_fit(kind):
    d, b = sample()
    if kind == "loss": d["records"][0]["packet_loss_pct"] = 5
    if kind == "restore": d["records"][0]["restoration_verified"] = False
    if kind == "drops": d["records"][0]["station_drops"] = 1
    if kind == "unknown": b["crossed"][0]["observation"].pop("restoration_verified")
    if kind == "crash": d["records"][0]["source_failure_metadata"] = {"crash": True}
    t = build_crossed_table(d, b)
    assert len(t["rows"]) == 8 and t["rows"][0]["quality_reasons"]
    assert fit_descriptive_crossover(t, "R48", "arm1", include_carryover=False)["status"] == "SOURCE_QUALITY_BLOCKED"


@pytest.mark.parametrize("field,value", [("station_drops", True), ("restoration_verified", 1), ("packet_loss_pct", float("nan")), ("packet_loss_pct", True), ("source_failure_metadata", {"crash": 1})])
def test_malformed_quality_is_not_zero_or_healthy(field, value):
    d, b = sample(); d["records"][0][field] = value
    with pytest.raises(ValueError): build_crossed_table(d, b)


@pytest.mark.parametrize("change", ["duplicate", "unbound", "bool_index", "unknown_period", "nonfinite_metric"])
def test_malformed_join_fails_closed(change):
    d, b = sample()
    if change == "duplicate": b["crossed"].append(deepcopy(b["crossed"][0]))
    if change == "unbound": b["crossed"][0]["treatment_id"] = "missing"
    if change == "bool_index": b["crossed"][0]["block_index"] = True
    if change == "unknown_period": b["crossed"][0]["crossover_step"] = True
    if change == "nonfinite_metric": b["crossed"][0]["observation"]["p95_rtt_ms"] = float("inf")
    with pytest.raises(ValueError): build_crossed_table(d, b)


def test_missing_period_is_preserved_in_table_but_not_falsely_imputed_for_fit():
    d, b = sample(); b["crossed"][0]["crossover_step"] = None
    t = build_crossed_table(d, b)
    with pytest.raises(ValueError): crossover_design(t, "R48", "arm1")


def test_old_multiarm_period_preserved_not_forced_into_two_period_model():
    d, b = sample(); b["crossed"][0]["crossover_step"] = 2
    t = build_crossed_table(d, b)
    assert t["rows"][0]["period"] == 2
    with pytest.raises(ValueError): crossover_design(t, "R48", "arm1")


def test_complete_policy_identity_distinguishes_endpoint_and_hooks():
    d, _ = sample(); a = d["records"][0]; b = deepcopy(a)
    b["cpe_policy"]["aql_by_ac"][2] = [2100, 4200]
    assert full_package(a) != full_package(b)
    b = deepcopy(a); b["short_retry_limit"] = 5
    assert full_package(a) != full_package(b)
    b["ap_policy"]["aql_by_ac"][0][0] = True
    with pytest.raises(ValueError): full_package(b)


@pytest.mark.parametrize('round_id', ['R57', 'R58', 'R59', 'R60'])
def test_ao_new_rounds_join_without_relabeling_or_old_round_imputation(round_id):
    d,b=sample()
    for row in d['records']:row['round_id']=round_id
    for block in b['crossed']:block['round_id']=round_id
    table=build_crossed_table(d,b)
    assert {r['round_id']for r in table['rows']}=={round_id}
    assert table['counts']['matched_round_scoped_ids']==4


@pytest.mark.parametrize('round_id',['R76','R99','R060',True])
def test_ao_future_or_malformed_rounds_still_rejected(round_id):
    d,b=sample();d['records'][0]['round_id']=round_id
    with pytest.raises(ValueError):build_crossed_table(d,b)


def test_ao_canonical_220_and_historical_212_table_contracts_preserve_prefix():
    import json
    from orchestration.autoresearch.fmx_live_dataset import (
        load_live_dataset,load_crossed_dataset,load_r1_to_r56_dataset,
    )
    historical=build_crossed_table(load_r1_to_r56_dataset(),load_crossed_dataset(through_round=56))
    current=build_crossed_table(load_live_dataset(through_round=60),load_crossed_dataset(through_round=60))
    assert historical['counts']==dict(records=212,crossed_rows=988,matched_round_scoped_ids=406,sequential_rows=16)
    assert current['counts']==dict(records=220,crossed_rows=1116,matched_round_scoped_ids=470,sequential_rows=16)
    serialized=lambda value:json.loads(json.dumps(value,allow_nan=False))
    assert serialized(current['rows'][:988])==serialized(historical['rows'])
    assert serialized(current['sequential_rows_excluded_from_crossed_model'])==serialized(historical['sequential_rows_excluded_from_crossed_model'])
    assert {r['round_id']for r in current['rows'][988:]}=={'R57','R58','R59','R60'}
    assert all(r['context']['distance_meters']==100 and r['context']['coverage_class']==0 for r in current['rows'][988:])


@pytest.mark.parametrize('round_id', ['R61', 'R62', 'R63', 'R64', 'R65'])
def test_as_new_rounds_join_preserving_exact_saved_identity(round_id):
    data, blocks = sample()
    for record in data['records']:
        record['round_id'] = round_id
    for block in blocks['crossed']:
        block['round_id'] = round_id
    table = build_crossed_table(data, blocks)
    assert table['counts'] == dict(records=2, crossed_rows=8, matched_round_scoped_ids=4, sequential_rows=1)
    assert {r['round_id'] for r in table['rows']} == {round_id}
    assert fit_descriptive_crossover(table, round_id, 'arm1')['status'] == 'NOT_ESTIMABLE'
    assert fit_descriptive_crossover(table, round_id, 'arm1', include_carryover=False)['coefficients']['current_treatment'] == pytest.approx(-3)


def test_as_canonical_230_and_historical_220_table_contracts_preserve_prefix():
    import json
    from orchestration.autoresearch.fmx_live_dataset import load_live_dataset, load_crossed_dataset
    historical = build_crossed_table(load_live_dataset(through_round=60), load_crossed_dataset(through_round=60))
    current = build_crossed_table(load_live_dataset(through_round=65), load_crossed_dataset(through_round=65))
    assert current['counts'] == dict(records=230, crossed_rows=1276, matched_round_scoped_ids=550, sequential_rows=16)
    serial = lambda value: json.loads(json.dumps(value, allow_nan=False))
    assert serial(current['rows'][:1116]) == serial(historical['rows'])
    assert serial(current['sequential_rows_excluded_from_crossed_model']) == serial(historical['sequential_rows_excluded_from_crossed_model'])
    added = current['rows'][1116:]
    assert {r['round_id'] for r in added} == {'R61', 'R62', 'R63', 'R64', 'R65'}
    expected = {'R61': (3000, 6), 'R62': (6000, 13), 'R63': (100, 0), 'R64': (100, 0), 'R65': (100, 0)}
    assert all((r['context']['distance_meters'], r['context']['coverage_class']) == expected[r['round_id']] for r in added)


@pytest.mark.parametrize('round_id', ['R66', 'R67', 'R68', 'R69', 'R70'])
def test_aw_new_saved_rounds_join_without_aliasing_earlier_observations(round_id):
    data, blocks = sample()
    for record in data['records']:
        record['round_id'] = round_id
    for block in blocks['crossed']:
        block['round_id'] = round_id
    table = build_crossed_table(data, blocks)
    assert {r['round_id'] for r in table['rows']} == {round_id}
    assert table['counts']['crossed_rows'] == 8
    assert fit_descriptive_crossover(table, round_id, 'arm1')['status'] == 'NOT_ESTIMABLE'
    assert fit_descriptive_crossover(table, round_id, 'arm1', include_carryover=False)['coefficients']['current_treatment'] == pytest.approx(-3)


def test_aw_canonical_240_preserves_230_prefix_and_all_new_timing_contexts():
    import json
    from orchestration.autoresearch.fmx_live_dataset import load_live_dataset, load_crossed_dataset
    historical = build_crossed_table(load_live_dataset(through_round=65), load_crossed_dataset(through_round=65))
    current = build_crossed_table(load_live_dataset(through_round=70), load_crossed_dataset(through_round=70))
    assert current['counts'] == dict(records=240, crossed_rows=1436, matched_round_scoped_ids=630, sequential_rows=16)
    serial = lambda value: json.loads(json.dumps(value, allow_nan=False))
    assert serial(current['rows'][:1276]) == serial(historical['rows'])
    assert serial(current['sequential_rows_excluded_from_crossed_model']) == serial(historical['sequential_rows_excluded_from_crossed_model'])
    expected = {'R66': (100, 0, 2), 'R67': (100, 0, 8), 'R68': (4500, 10, 6),
                'R69': (9000, 20, 6), 'R70': (4500, 10, 6)}
    added = current['rows'][1276:]
    assert {r['round_id'] for r in added} == set(expected)
    assert all((r['context']['distance_meters'], r['context']['coverage_class'],
                r['context']['active_flow_count']) == expected[r['round_id']] for r in added)
    targets = {r['round_id']: r['endpoint_policies'] for r in added if '_iter1_' in r['treatment_id']}
    assert tuple(targets['R67'][0]['aql_by_ac'][2]) == (1480, 2960)
    assert (targets['R67'][0]['fq_target_us'], targets['R67'][0]['fq_interval_us']) == (7000, 35000)
    assert (targets['R67'][1]['fq_target_us'], targets['R67'][1]['fq_interval_us']) == (9000, 45000)
    assert tuple(targets['R70'][0]['aql_by_ac'][2]) == (1560, 3120)


@pytest.mark.parametrize('round_id', ['R71', 'R72', 'R73', 'R74', 'R75'])
def test_ba_new_saved_rounds_keep_matched_window_design_and_endpoint_packages(round_id):
    data, blocks = sample()
    for record in data['records']:
        record['round_id'] = round_id
    for block in blocks['crossed']:
        block['round_id'] = round_id
    table = build_crossed_table(data, blocks)
    assert table['counts']['matched_round_scoped_ids'] == 4
    assert {r['round_id'] for r in table['rows']} == {round_id}
    assert fit_descriptive_crossover(table, round_id, 'arm1')['status'] == 'NOT_ESTIMABLE'
    restricted = fit_descriptive_crossover(table, round_id, 'arm1', include_carryover=False)
    assert restricted['coefficients']['current_treatment'] == pytest.approx(-3)
    data['records'][0]['packet_loss_pct'] = 1
    blocked = build_crossed_table(data, blocks)
    assert len(blocked['rows']) == 8
    assert fit_descriptive_crossover(blocked, round_id, 'arm1', include_carryover=False)['status'] == 'SOURCE_QUALITY_BLOCKED'


def test_ba_canonical_250_preserves_240_prefix_and_recorded_seven_context_coordinates():
    import json
    from orchestration.autoresearch.fmx_live_dataset import load_live_dataset, load_crossed_dataset
    historical = build_crossed_table(load_live_dataset(through_round=70), load_crossed_dataset(through_round=70))
    current = build_crossed_table(load_live_dataset(through_round=75), load_crossed_dataset(through_round=75))
    assert current['counts'] == dict(records=250, crossed_rows=1596, matched_round_scoped_ids=710, sequential_rows=16)
    serial = lambda v: json.loads(json.dumps(v, allow_nan=False))
    assert serial(current['rows'][:1436]) == serial(historical['rows'])
    assert serial(current['sequential_rows_excluded_from_crossed_model']) == serial(historical['sequential_rows_excluded_from_crossed_model'])
    expected = {'R71': (100, 0, 2), 'R72': (100, 0, 8), 'R73': (12000, 27, 6),
                'R74': (100, 0, 8), 'R75': (15000, 33, 6)}
    added = current['rows'][1436:]
    assert all((r['context']['distance_meters'], r['context']['coverage_class'], r['context']['active_flow_count']) == expected[r['round_id']] for r in added)
    targets = {r['round_id']: r['endpoint_policies'] for r in added if '_iter1_' in r['treatment_id']}
    assert tuple(targets['R71'][0]['aql_by_ac'][2]) == (1350, 2700)
    assert tuple(targets['R71'][1]['aql_by_ac'][2]) == (2200, 4400)
    assert tuple(targets['R74'][0]['aql_by_ac'][0]) == (900, 1800)
    assert tuple(targets['R74'][1]['aql_by_ac'][2]) == (2150, 4300)
