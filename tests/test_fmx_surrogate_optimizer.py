from copy import deepcopy
import pytest

from orchestration.autoresearch.fmx_surrogate_optimizer import (
    SavedPackageSurrogate, grouped_validation, propose_observed,
)


def row(round_id="R48", name="a", low=1500):
    def p(lo):
        return dict(aql_by_ac=[[500, 1000], [500, 1000], [lo, 2 * lo], [500, 1000]],
                    aql_threshold_us=4 * lo, fq_quantum_bytes=256, rc_per_thresh=28,
                    dscp_micro_vo_steering=True)
    return dict(round_id=round_id, iteration=name, workload_regime="bidir_6flow",
                active_flow_count=6, bidirectional=True, ap_policy=p(low), cpe_policy=p(2100),
                encryption_mode="psk2", distance_meters=None, associated_cpes=["lab-peer"],
                goodput_mbps=100 + low / 1000, p95_ms=30 - low / 1000, p99_ms=40 - low / 1000,
                restoration_verified=True, station_drops=0, packet_loss_pct=0,
                summary_consistency={"consistent": True})


def corpus():
    return [row("R48", "a", 1000), row("R49", "b", 1200), row("R50", "c", 1500), row("R51", "d", 1800)]


def test_native_fit_deterministic_full_endpoint_predictors_and_no_actuation():
    data = corpus()
    a = SavedPackageSurrogate(data).predict(data[0]); b = SavedPackageSurrogate(data).predict(data[0])
    assert a == b and not a["automatic_execution_allowed"]
    assert a["prediction_kind"] == "EXPLORATORY_NOT_PHYSICAL_OR_PROMOTION"
    model = SavedPackageSurrogate(data)
    assert any("[0].aql_by_ac[2]" in k for k in model.keys)
    assert any("[1].aql_by_ac[2]" in k for k in model.keys)
    changed = deepcopy(data[0]); changed["cpe_policy"]["aql_by_ac"][2] = [3000, 6000]
    assert model.predict(changed)["nearest_feature_distance"] > 0


def test_all_policy_fields_not_only_aql_affect_identity_and_features():
    data = corpus()
    data[0].update(ap_ack_pps=0, cpe_ack_pps=10, short_retry_limit=5)
    for r in data[1:]: r.update(ap_ack_pps=None, cpe_ack_pps=20, short_retry_limit=7)
    model = SavedPackageSurrogate(data)
    assert any("ack_pps" in k for k in model.keys) and any("short_retry_limit" in k for k in model.keys)


def test_holdout_excludes_round_and_every_test_package_from_all_rounds():
    data = corpus(); alias = deepcopy(data[0]); alias.update(round_id="R52", iteration="alias"); data.append(alias)
    out = grouped_validation(data)
    assert out["predicted_windows"] == 5
    for fold in out["folds"]:
        assert all(x[0] != fold["held_out_round"] for x in fold["train_ids"])
        assert not set(fold["training_package_ids"]) & set(fold["held_out_package_ids"])
    assert out["independent_sector_replications"] == 0
    assert len(out["rmse"]) == len(out["training_mean_rmse"]) == 3


def test_same_package_all_rounds_yields_no_leak_free_score_not_fake_zero_rmse():
    data = [row("R48", "a"), row("R49", "b")]
    out = grouped_validation(data)
    assert out["rmse"] is None and out["predicted_windows"] == 0
    assert all(x["status"] == "NO_LEAK_FREE_TRAINING_SUPPORT" for x in out["folds"])


@pytest.mark.parametrize("field,value", [("distance_meters", 3000), ("encryption_mode", "none"), ("workload_regime", "bidir_8flow"), ("coverage_class", 6)])
def test_context_no_crypto_workload_timing_transfer(field, value):
    data = corpus(); model = SavedPackageSurrogate(data); query = deepcopy(data[0]); query[field] = value
    with pytest.raises(ValueError, match="context"): model.predict(query)


@pytest.mark.parametrize("field,value", [("p95_ms", True), ("p95_ms", float("nan")), ("p95_ms", 10**400), ("p99_ms", -1), ("restoration_verified", 1), ("station_drops", False)])
def test_malformed_metrics_health_not_accepted(field, value):
    data = corpus(); data[0][field] = value
    with pytest.raises(ValueError): SavedPackageSurrogate(data)


def test_negative_source_summary_is_preserved_excluded_not_silently_repaired():
    data = corpus(); data[0]["summary_consistency"]["consistent"] = False
    out = grouped_validation(data)
    assert out["excluded"][0]["reasons"] == ["source_summary_inconsistent"]
    assert data[0]["goodput_mbps"] == 101
    with pytest.raises(ValueError): SavedPackageSurrogate(data)


def test_unseen_feature_is_unsupported_not_filled_as_zero():
    data = corpus(); model = SavedPackageSurrogate(data); q = deepcopy(data[0]); q["force_tx_status"] = 1
    with pytest.raises(ValueError): model.predict(q)


def test_proposals_only_complete_observed_packages_and_real_objectives():
    data = corpus(); data[0]["cpe_policy"] = None
    out = propose_observed(data, max_candidates=2)
    assert out["synthesized_packages"] == 0 and not out["automatic_execution_allowed"]
    assert out["excluded"][0]["reasons"] == ["endpoint_package_unknown"]
    identities = {(r["round_id"], r["iteration"]) for r in data}
    assert all(tuple(p["source_identity"]) in identities and p["enabled"] is False for p in out["proposals"])
    assert all(p["endpoint_policies"][0]["aql_by_ac"][2] != p["endpoint_policies"][1]["aql_by_ac"][2] for p in out["proposals"])


@pytest.mark.parametrize("method,arg", [(grouped_validation, {"max_rounds": True}), (propose_observed, {"max_candidates": 0})])
def test_bounded_integer_budgets(method, arg):
    with pytest.raises(ValueError): method(corpus(), **arg)


def test_training_copies_do_not_mutate_callers_or_allow_duplicate_ids():
    data = corpus(); model = SavedPackageSurrogate(data); before=model.predict(data[0])
    data[1]["goodput_mbps"] = 99999
    assert model.predict(data[0]) == before
    with pytest.raises(ValueError): grouped_validation([data[0], data[0]])


def test_good_duplicate_cannot_hide_same_context_full_package_negative():
    data = corpus(); bad=deepcopy(data[0]); bad.update(round_id="R52", iteration="bad", packet_loss_pct=5)
    out=propose_observed(data+[bad])
    excluded={tuple(x["identity"]):x for x in out["excluded"]}
    assert "known_negative_package_context" in excluded[("R48","a")]["reasons"]
    assert excluded[("R48","a")]["known_negative_evidence"][0]["identity"] == ["R52","bad"]
    assert not any(p["source_identity"]==["R48","a"] for p in out["proposals"])
    # A distinct timing context is not assumed exchangeable with the failure.
    separate=deepcopy(data[0]); separate.update(round_id="R53",iteration="timing",distance_meters=3000,coverage_class=6)
    assert any(p["source_identity"]==["R53","timing"] for p in propose_observed([bad,separate])["proposals"])


def test_ao_profiles_keep_retry_rc_codel_and_endpoint_aql_in_identity_features():
    a=row('R59','retry64',1550);b=row('R60','codel8',1520)
    for item in (a,b):
        item.update(distance_meters=100,coverage_class=0,short_retry_limit=6,long_retry_limit=4)
        for end in ('ap_policy','cpe_policy'):
            item[end].update(rc_per_thresh=24,fq_target_us=10000,fq_interval_us=50000)
    b['ap_policy'].update(fq_target_us=8000,fq_interval_us=40000)
    model=SavedPackageSurrogate([a,b])
    assert any('short_retry_limit'in k for k in model.keys)
    assert any('fq_target_us'in k for k in model.keys)
    assert any('rc_per_thresh'in k for k in model.keys)
    proposals=propose_observed([a,b])
    assert proposals['synthesized_packages']==0
    for p in proposals['proposals']:
        ap,cpe=p['endpoint_policies']
        assert ap['rc_per_thresh']==cpe['rc_per_thresh']==24
        assert ap['short_retry_limit']==cpe['short_retry_limit']==6
        assert cpe['aql_by_ac'][2]==[2100,4200]
        assert not p['enabled']


def test_ao_historical_56_serialization_invariant_and_old_inventory_values_preserved():
    from pathlib import Path
    import json
    from orchestration.autoresearch.fmx_live_dataset import load_r1_to_r56_dataset
    root=Path(__file__).resolve().parents[1]
    prior=root/'artifacts/autoresearch/waves_ak_to_an_20261024'
    records=load_r1_to_r56_dataset()['records']
    # The old sealed model had a tuple-support bug; do not force its artificial
    # unsupported folds into the repaired revision. Same values must now have
    # identical predictions regardless of Python/dataclass vs JSON arrays.
    serialized=lambda value:json.loads(json.dumps(value,allow_nan=False))
    assert grouped_validation(records)==grouped_validation(serialized(records))
    assert serialized(propose_observed(records))==json.loads((prior/'wave_ak_models_observed_proposals.json').read_text())


def test_ao_supported_array_representation_cannot_change_feature_or_prediction_support():
    as_lists=corpus();as_tuples=deepcopy(as_lists)
    for record in as_tuples:
        for side in ('ap_policy','cpe_policy'):
            record[side]['aql_by_ac']=tuple(tuple(pair)for pair in record[side]['aql_by_ac'])
    a=SavedPackageSurrogate(as_lists);b=SavedPackageSurrogate(as_tuples)
    assert a.keys==b.keys
    assert a.predict(as_lists[0])==b.predict(as_tuples[0])
    assert grouped_validation(as_lists)==grouped_validation(as_tuples)


def test_as_65_fold_budget_and_new_retry54_rc22_package_are_not_relabelled():
    data = [row('R61', 'distance', 1520), row('R65', 'retry54', 1520)]
    for record in data:
        record.update(short_retry_limit=6, long_retry_limit=4)
        record['ap_policy'].update(rc_per_thresh=24, fq_target_us=8000, fq_interval_us=40000)
        record['cpe_policy'].update(rc_per_thresh=24, fq_target_us=10000, fq_interval_us=50000)
    data[1]['short_retry_limit'] = 5
    for side in ('ap_policy', 'cpe_policy'):
        data[1][side]['rc_per_thresh'] = 22
    model = SavedPackageSurrogate(data)
    assert model.predict(data[0])['nearest_feature_distance'] == 0
    assert model.predict(data[1])['nearest_feature_distance'] == 0
    out = grouped_validation(data, max_rounds=65)
    assert {fold['held_out_round'] for fold in out['folds']} == {'R61', 'R65'}
    proposals = propose_observed(data)
    assert {p['endpoint_policies'][0]['rc_per_thresh'] for p in proposals['proposals']} == {22, 24}
    assert all(not p['enabled'] for p in proposals['proposals'])
    with pytest.raises(ValueError):
        grouped_validation(data, max_rounds=76)


def test_aw_70_fold_bound_and_distinct_ap_codel_aql_coordinates_remain_observed_only():
    data = [row('R67', 'synthetic_tighter', 1480), row('R70', 'synthetic_wider', 1560)]
    for record in data:
        record.update(distance_meters=4500, coverage_class=10, short_retry_limit=6, long_retry_limit=4)
        record['ap_policy'].update(rc_per_thresh=24, fq_target_us=8000, fq_interval_us=40000)
        record['cpe_policy'].update(rc_per_thresh=24, fq_target_us=10000, fq_interval_us=50000)
    data[0]['ap_policy'].update(fq_target_us=7000, fq_interval_us=35000)
    model = SavedPackageSurrogate(data)
    assert len(model.records) == 2
    assert model.predict(data[0])['nearest_feature_distance'] == model.predict(data[1])['nearest_feature_distance'] == 0
    validation = grouped_validation(data, max_rounds=70)
    assert {f['held_out_round'] for f in validation['folds']} == {'R67', 'R70'}
    packages = [p['endpoint_policies'] for p in propose_observed(data)['proposals']]
    # The synthetic 1560 observation dominates 1480 in all objectives. Both
    # remain training packages; observed frontier membership is a narrower set.
    assert packages and {p[0]['aql_by_ac'][2][0] for p in packages} <= {1480, 1560}
    assert all(p[1]['aql_by_ac'][2] == [2100, 4200] for p in packages)
    outside = deepcopy(data[0]); outside.update(distance_meters=9000, coverage_class=20)
    with pytest.raises(ValueError, match='context'):
        model.predict(outside)
    with pytest.raises(ValueError):
        grouped_validation(data, max_rounds=76)


def test_ba_75_round_limit_preserves_distinct_vo_be_codel_and_context_support():
    data = [row('R71', 'twoflow', 1350), row('R74', 'eightflow', 1510)]
    for record in data:
        record.update(short_retry_limit=6, long_retry_limit=4)
        record['ap_policy'].update(rc_per_thresh=24, fq_target_us=6000, fq_interval_us=30000)
    data[0]['cpe_policy']['aql_by_ac'][2] = [2200, 4400]
    data[1]['ap_policy']['aql_by_ac'][0] = [900, 1800]
    data[1]['ap_policy'].update(fq_target_us=5000, fq_interval_us=25000)
    model = SavedPackageSurrogate(data)
    assert model.predict(data[0])['nearest_feature_distance'] == model.predict(data[1])['nearest_feature_distance'] == 0
    result = grouped_validation(data, max_rounds=75)
    assert {f['held_out_round'] for f in result['folds']} == {'R71', 'R74'}
    assert all(p['enabled'] is False for p in propose_observed(data)['proposals'])
    outside = deepcopy(data[0]); outside.update(distance_meters=15000, coverage_class=33)
    with pytest.raises(ValueError, match='context'):
        model.predict(outside)
    with pytest.raises(ValueError):
        grouped_validation(data, max_rounds=76)
