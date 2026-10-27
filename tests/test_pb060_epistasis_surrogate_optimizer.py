"""Disposable numerical and retained-input contract checks; no device acquisition."""
from __future__ import annotations

from copy import deepcopy
from collections import Counter
import hashlib
import json
from pathlib import Path
import socket
import subprocess

import numpy as np
import pytest

from orchestration.autoresearch import pb060_epistasis_surrogate_optimizer as pb


def observation(rid, baseline, treatment, outcome=(0.01, .05), *, context=None, quality=None):
    context = context or dict(radio="FIXTURE", workload="FIXTURE", cpe_count=1, distance_m=10)
    return pb.Comparison(rid, pb.canonical(context), baseline, treatment, outcome,
                         (100.0, 100.0), (100 * (1 + outcome[0]), 100 * (1 - outcome[1])),
                         dict(kind="SYNTHETIC_TEST_ONLY"),
                         quality or dict(loss_pct=0.0, restoration_reported=True, station_drops=0),
                         "SYNTHETIC_TEST_ONLY")


@pytest.fixture(scope="module")
def evidence():
    return pb.load_search_evidence()


@pytest.fixture(scope="module")
def report():
    return pb.build_report(samples=512)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -float("inf"), "12", True, None])
def test_nonfinite_or_untyped_measurements_rejected(bad):
    with pytest.raises(ValueError):
        pb.finite(bad, "measurement")


def test_bound_input_rejects_tamper_duplicate_keys_and_escape(tmp_path):
    path = tmp_path / "sample.json"
    path.write_text('{"a":1}', encoding="utf-8")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert pb.read_bound(tmp_path, "sample.json", digest)[0] == {"a": 1}
    path.write_text('{"a":2}', encoding="utf-8")
    with pytest.raises(ValueError, match="digest"):
        pb.read_bound(tmp_path, "sample.json", digest)
    path.write_text('{"a":1,"a":2}', encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate"):
        pb.read_bound(tmp_path, "sample.json", hashlib.sha256(path.read_bytes()).hexdigest())
    with pytest.raises(ValueError, match="outside"):
        pb.read_bound(tmp_path, "../outside.json", digest)


def test_hypervolume_matches_known_union_not_sum_of_rectangles():
    assert pb.hypervolume([[1, 2], [2, 1]], (0, 0)) == pytest.approx(3)
    assert pb.hypervolume([[1, 2], [2, 1], [1, 1], [2, 1]], (0, 0)) == pytest.approx(3)
    assert pb.hypervolume([[-1, 5], [5, -1]], (0, 0)) == 0
    assert pb.hypervolume([], (0, 0)) == 0


def test_ehvi_zero_variance_equals_exact_hypervolume_increment():
    front = [[.1, .1], [.0, .3]]
    mean = [.2, .2]
    result = pb.expected_hypervolume_improvement(mean, [0, 0], front, samples=128)
    expected = pb.hypervolume(front + [mean]) - pb.hypervolume(front)
    assert result["ehvi"] == pytest.approx(expected, abs=1e-12)
    assert result["mc_standard_error"] < 1e-14
    dominated = pb.expected_hypervolume_improvement([-.1, -.1], [0, 0], front, samples=128)
    assert dominated["ehvi"] == 0


def test_mc_ehvi_matches_bruteforce_same_posterior_draws():
    mean, sd, front = [.03, .12], [.1, .2], [[.1, .1], [0, .4], [.3, -.2]]
    count, seed = 256, 71
    result = pb.expected_hypervolume_improvement(mean, sd, front, samples=count, seed=seed)
    draws = np.asarray(mean) + np.asarray(sd) * np.random.default_rng(seed).standard_normal((count, 2))
    expected = [pb.hypervolume(front + [x.tolist()]) - pb.hypervolume(front) for x in draws]
    assert result["ehvi"] == pytest.approx(np.mean(expected), abs=1e-12)
    assert result["mc_standard_error"] == pytest.approx(np.std(expected, ddof=1) / np.sqrt(count), abs=1e-12)
    assert result == pb.expected_hypervolume_improvement(mean, sd, front, samples=count, seed=seed)


def test_log_ratio_gp_reversal_and_ehvi_transform_are_coherent():
    forward = observation("R1", {"x": 0}, {"x": 1}, (1.0, .5))
    reverse = observation("R2", {"x": 1}, {"x": 0}, (-.5, -1.0))
    assert np.asarray(forward.model_outcome) == pytest.approx(-np.asarray(reverse.model_outcome))
    mean = [np.log(1.1), -np.log(.8)]
    result = pb.expected_hypervolume_improvement(mean, [0, 0], [[0, 0]], samples=32, log_ratio_posterior=True)
    expected = pb.hypervolume([[0, 0], [.1, .2]]) - pb.hypervolume([[0, 0]])
    assert result["ehvi"] == pytest.approx(expected)


@pytest.mark.parametrize("mean,sd,samples", [([0], [1, 1], 32), ([0, 0], [-1, 1], 32),
    ([float("nan"), 0], [1, 1], 32), ([0, 0], [1, 1], 1)])
def test_invalid_posterior_rejected(mean, sd, samples):
    with pytest.raises(ValueError):
        pb.expected_hypervolume_improvement(mean, sd, [[0, 0]], samples=samples)


def test_state_missingness_not_imputed_zero_and_ap_cpe_not_aliased():
    states = [{"endpoint.ap.be_low_us": 0, "endpoint.cpe.be_low_us": 3},
              {"endpoint.ap.be_low_us": 3, "endpoint.cpe.be_low_us": 0}]
    encoder = pb.StateEncoder(states)
    assert not np.array_equal(encoder.encode(states[0]), encoder.encode(states[1]))
    unknown = dict(states[0], **{"endpoint.ap.be_low_us": None})
    assert not np.array_equal(encoder.encode(states[0]), encoder.encode(unknown))
    with pytest.raises(ValueError, match="Unseen"):
        encoder.encode(dict(states[0], new_coordinate=4))


def test_historical_aql_ac_order_is_vo_vi_be_bk_and_codel_not_api_aliased():
    row = dict(ap_policy=dict(aql_by_ac=[[1, 2], [3, 4], [5, 6], [7, 8]]), cpe_policy=None)
    state = pb._wa_policy(row)
    assert state["endpoint.ap.vo_low_us"] == 1
    assert state["endpoint.ap.vi_low_us"] == 3
    assert state["endpoint.ap.be_low_us"] == 5
    assert state["endpoint.ap.bk_low_us"] == 7
    assert "codel_target" not in pb.BINDINGS
    assert "codel_interval" not in pb.BINDINGS


def test_gp_contrast_kernel_psd_and_noop_exactly_zero():
    rows = [observation(f"R{i+1}", {"x": 0}, {"x": i + 1}) for i in range(4)]
    model = pb.EpistasisSurrogate(rows)
    gram = model._contrast_kernel(model.a, model.b, model.a, model.b)
    assert np.linalg.eigvalsh(gram).min() >= -1e-10
    mean, sd = model.posterior({"x": 0}, {"x": 0}, context=rows[0].context)
    assert np.array_equal(mean, [0, 0])
    assert np.array_equal(sd, [0, 0])
    changed, changed_sd = model.posterior({"x": 0}, {"x": 3}, context=rows[0].context)
    assert np.isfinite(changed).all() and np.all(changed_sd > 0)


def test_conditional_epistasis_depends_on_baseline_not_delta_only():
    key_a, key_f = "endpoint.ap.be_low_us", "endpoint.ap.fq_quantum_bytes"
    rows = []
    for i, aql in enumerate((1000, 5000)):
        for j, quantum in enumerate((300, 1514)):
            baseline, treatment = {key_a: aql, key_f: 300}, {key_a: aql, key_f: quantum}
            gain = .12 if aql == 1000 and quantum == 1514 else 0
            rows.append(observation(f"R{i*2+j+1}", baseline, treatment, (gain, gain)))
    model = pb.EpistasisSurrogate(rows, prior_sd=(.5, .5), noise_sd=(.001, .001))
    low, _ = model.posterior({key_a: 1000, key_f: 300}, {key_a: 1000, key_f: 1514}, context=rows[0].context)
    high, _ = model.posterior({key_a: 5000, key_f: 300}, {key_a: 5000, key_f: 1514}, context=rows[0].context)
    assert low[0] > .1
    assert abs(high[0]) < .01


def test_no_cross_hardware_regime_or_objective_semantics_transfer():
    one = observation("R1", {"x": 0}, {"x": 1})
    two = observation("R2", {"x": 0}, {"x": 2}, context={"radio": "OTHER"})
    with pytest.raises(ValueError, match="exact"):
        pb.EpistasisSurrogate([one, two])
    model = pb.EpistasisSurrogate([one])
    with pytest.raises(ValueError, match="Cross-context"):
        model.posterior(one.baseline, one.treatment, context=two.context)
    assert len(pb.fit_context_surrogates([one, two])) == 2


def test_training_encoder_does_not_fit_on_heldout_values():
    rows = [observation("R1", {"x": 0}, {"x": 1}), observation("R2", {"x": 2}, {"x": 3})]
    model = pb.EpistasisSurrogate(rows)
    spec = deepcopy(model.encoder.spec)
    model.posterior({"x": 0}, {"x": 10000}, context=rows[0].context)
    assert model.encoder.spec == spec


def test_whole_round_and_both_package_purge_retains_unsupported_folds():
    rows = [observation("R1", {"x": 0}, {"x": 1}),
            observation("R2", {"x": 0}, {"x": 1}),
            observation("R3", {"x": 2}, {"x": 3}),
            observation("R4", {"x": 3}, {"x": 4})]
    result = pb.grouped_validation(rows)
    fold = next(f for f in result["folds"] if f["round_id"] == "R1")
    assert fold["train_rounds"] == ["R3", "R4"]
    assert fold["purge"] == "BOTH_COMPLETE_PACKAGES_AND_WHOLE_ROUND"
    result = pb.grouped_validation(rows[:2])
    assert result["predicted_comparisons"] == 0
    assert all(f["status"] == "UNSUPPORTED_AFTER_PACKAGE_PURGE" for f in result["folds"])


def test_failed_loss_or_missing_restore_not_acceptable_front_but_not_deleted():
    for quality in (dict(loss_pct=.625, restoration_reported=True, station_drops=0),
                    dict(loss_pct=0, restoration_reported=None, station_drops=0),
                    dict(loss_pct=0, restoration_reported=True, station_drops=1)):
        row = observation("R1", {"x": 0}, {"x": 1}, quality=quality)
        assert not row.front_eligible
        model = pb.EpistasisSurrogate([row])
        assert model.observations == [row]


def test_wall_pivots_only_single_context_current_clean_trailing_streak():
    catalog = [{"id": "phy", "name": "ldpc", "classification": "characterization_only"}]
    one = observation("R1", {"x": 0}, {"x": 1}, (.001, .01))
    two = observation("R2", {"x": 0}, {"x": 2}, (.002, .02))
    result = pb.regime_switch([one, two], catalog)[0]
    assert result["wall_reached"]
    assert len(result["pivot_dimensions"]) == 4
    assert result["automatic_execution_allowed"] is False
    assert result["pivot_dimensions"][0]["requested_values_mhz"] == [5, 10]
    old_hit_then_gain = [one, two, observation("R3", {"x": 0}, {"x": 3}, (.1, .1))]
    assert not pb.regime_switch(old_hit_then_gain, catalog)[0]["wall_reached"]
    dirty = observation("R3", {"x": 0}, {"x": 3}, (.001, .01),
                        quality=dict(loss_pct=.1, restoration_reported=True, station_drops=0))
    assert not pb.regime_switch([one, two, dirty], catalog)[0]["wall_reached"]
    other = observation("R2", {"x": 0}, {"x": 2}, (.001, .01),
                        context=dict(radio="FIXTURE", workload="OTHER", cpe_count=1, distance_m=10))
    assert not any(x["wall_reached"] for x in pb.regime_switch([one, other], catalog))


def test_phase_proxies_not_mislabeled_ota_or_expanded_as_raw_trials(evidence):
    rows = evidence["comparisons"]
    multi = [x for x in rows if "AGGREGATES" in x.evidence_kind]
    assert len(multi) == 118
    semantics = {json.loads(x.context)["metric"] for x in multi}
    assert "SSH_STREAM_NOT_OTA_MBPS" in semantics
    assert "HTTP_FIVE_REQUESTS_PER_SECOND_DERIVED" in semantics
    assert "THREE_HOST_SSH_STREAM_NOT_SECTOR_CAPACITY" in semantics
    assert all(x.quality["raw_trial_samples"] is False for x in multi)
    assert all(x.quality["restoration_reported"] is None for x in multi)


def test_exact_catalog_roster_and_absent_rounds_stay_absent(evidence):
    audit = evidence["audit"]
    assert len(evidence["catalog"]) == 571
    assert audit["requested_rounds"] == 320
    assert audit["observed_unique_rounds"] == 308
    assert set(audit["missing_round_ids"]) == {"R110", "R111", "R112", "R113", "PBM5-R6", "PBM5-R7", "PBM5-R8",
                                             "R5AC-R1", "R5AC-R2", "R5AC-R3", "R5AC-R4", "R5AC-R5"}
    assert audit["family_counts"] == {"WA": 190, "PBM5": 33, "R5AC": 16, "R2AC": 21, "LTU": 20, "LTU-S15": 8, "AF4X": 20}
    assert audit["stage16_new_measurement_rounds"] == 0
    assert Counter(x["round_id"] for x in audit["excluded_comparisons"]) == {"R13": 4, "R17": 1, "R36": 3}
    for excluded in audit["excluded_comparisons"]:
        if excluded["round_id"] == "R36":
            assert excluded["reason"] == "Positive baseline response required"
        else:
            assert excluded["reason"] == "WITHIN_ROUND_CONTEXT_CHANGED_NO_MATCHED_BASELINE"


def test_complete_legacy_lower_control_identity_retained(evidence):
    rows = evidence["records"]
    r22 = [pb._wa_policy(x) for x in rows if x["round_id"] == "R22"]
    assert {x["endpoint.ap.short_retry_limit"] for x in r22} == {5, 7}
    assert {x["endpoint.ap.long_retry_limit"] for x in r22} == {3, 4}
    assert {x["endpoint.ap.force_tx_status"] for x in r22} == {0, 1}
    r23 = [pb._wa_policy(x) for x in rows if x["round_id"] == "R23"]
    assert {x["endpoint.ap.ani_enable"] for x in r23} == {0, 1}
    assert {x["endpoint.ap.airtime_flags"] for x in r23} == {1, 3}
    assert {x["endpoint.ap.fq_limit"] for x in r23} == {2048, 8192}
    r122 = [pb._wa_policy(x) for x in rows if x["round_id"] == "R122"]
    assert {x["new_source_controls.ap_ack_clocking"] for x in r122} == {False, True}
    assert len({pb.canonical(x) for x in r22}) == len(r22)


def test_actual_epistasis_claims_are_source_specific_not_causal(report, evidence):
    claims = report["epistasis"]
    assert claims["causal_interaction_identified"] is False
    assert claims["codel_factorial_complete"] is False
    r174 = next(x for x in evidence["comparisons"] if x.round_id == "R174")
    assert r174.outcome[0] * 100 == pytest.approx(4.1314393033828, abs=.0001)
    assert r174.treatment["endpoint.ap.be_low_us"] == 1850
    assert r174.treatment["endpoint.cpe.be_low_us"] == 2400
    rows = [x for x in evidence["records"] if x["round_id"] == "R173"]
    assert rows[-1]["jain_fairness"] == pytest.approx(.95196533203125)
    assert "REFUTED" in claims["combined_4_13_percent_and_0_9520_same_round"]


def test_all571_evaluated_top15_unique_disabled_and_no_fake_ehvi(report):
    assert pb.validate_search_artifact(report)
    frontier = report["frontier"]
    assert len(frontier["all_catalog_evaluations"]) == 571
    assert len({x["id"] for x in frontier["top15"]}) == 15
    assert frontier["catalog_counts"]["EXCLUDED_FROM_SEARCH"] == 127
    assert frontier["catalog_counts"]["OBSERVATION_ONLY"] == 142
    assert sum(v for k, v in frontier["catalog_counts"].items() if k in ("SUPPORTED_CONDITIONAL_EHVI", "PRIOR_ONLY_RESEARCH_PRIORITY")) == 302
    supported = [x for x in frontier["top15"] if x["status"] == "SUPPORTED_CONDITIONAL_EHVI"]
    assert supported
    assert [x["evidence_based_ehvi"] for x in supported] == sorted([x["evidence_based_ehvi"] for x in supported], reverse=True)
    for item in frontier["top15"]:
        assert item["classification"] not in ("excluded", "observation_only")
        assert item["automatic_execution_allowed"] is False
        assert item["physical_status"] == "BLOCKED_UNQUALIFIED"
        if item["status"] == "PRIOR_ONLY_RESEARCH_PRIORITY":
            assert item["evidence_based_ehvi"] is None
            assert item["intervention"] is None
            assert len(item["hypothetical_prior_sensitivity"]) == 3


def test_unsupported_hardware_promotions_rejected(report):
    altered = deepcopy(report)
    altered["automatic_execution_allowed"] = True
    with pytest.raises(ValueError, match="Offline"):
        pb.validate_search_artifact(altered)
    altered = deepcopy(report)
    prior = next(x for x in altered["frontier"]["all_catalog_evaluations"] if x["status"] == "PRIOR_ONLY_RESEARCH_PRIORITY")
    prior["evidence_based_ehvi"] = 1
    with pytest.raises(ValueError, match="Unsupported"):
        pb.validate_search_artifact(altered)
    altered = deepcopy(report)
    excluded = next(x for x in altered["frontier"]["all_catalog_evaluations"] if x["status"] == "EXCLUDED_FROM_SEARCH")
    forged = dict(excluded, classification="characterization_only", rank=1)
    altered["frontier"]["top15"][0] = forged
    with pytest.raises(ValueError, match="Top15"):
        pb.validate_search_artifact(altered)


def test_frontier_reproducible_and_invariant_to_input_catalog_order(evidence):
    one = pb.rank_frontier(evidence["catalog"], evidence["comparisons"], samples=128)
    two = pb.rank_frontier(list(reversed(evidence["catalog"])), evidence["comparisons"], samples=128)
    assert one["top15"] == two["top15"]


def test_build_report_cannot_network_spawn_or_import_acquisition(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Offline model attempted network/process acquisition")
    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    import sys
    before = set(sys.modules)
    result = pb.build_report(samples=32)
    added = set(sys.modules) - before
    assert not any(x.startswith("tools.bench") for x in added)
    assert result["automatic_execution_allowed"] is False
    assert result["physical_acceptance"] is False
    assert result["E2"] == "NOT_ACCEPTED"


def test_default_cli_writes_only_explicit_disposable_output(tmp_path, monkeypatch):
    output = tmp_path / "frontier.json"
    sentinel = dict(status="FIXTURE_ONLY", corpus_audit=dict(observed_unique_rounds=0), frontier=dict(top15=[]))
    monkeypatch.setattr(pb, "build_report", lambda **kwargs: sentinel)
    assert pb.main(["--output", str(output), "--samples", "32"]) == 0
    assert json.loads(output.read_text()) == sentinel


def test_committed_artifact_when_present_matches_current_inputs_and_implementation():
    path = pb.ROOT / pb.OUTPUT
    if not path.exists():
        return  # Generation occurs after the first requested test run.
    report = json.loads(path.read_text(encoding="utf-8"))
    assert pb.validate_search_artifact(report)
    for pin in report["input_bindings"] + report["implementation_bindings"]:
        assert hashlib.sha256((pb.ROOT / pin["path"]).read_bytes()).hexdigest() == pin["sha256"]
