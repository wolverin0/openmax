"""Regression evidence for modeled/claimed/accepted separation, no radio access."""
import json
import math
import socket
import subprocess

import pytest

from tools.sim import run_stage819a_guarida_tower_v10_triple_patch_and_xw_mixed_tdma_pareto as sim
from tools.observability import build_stage820a_executive_1line_progress_and_tester_matrix_v10 as progress
from tools.verify import build_stage821a_960window_cross_lane_master_scorecard as score
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars


def write(root, name, obj):
    path = root / "artifacts" / "autoresearch" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding="utf-8")


@pytest.fixture(autouse=True)
def prohibit_network_and_producers(monkeypatch):
    def denied(*args, **kwargs):
        raise AssertionError("offline contract forbids network and producer execution")
    monkeypatch.setattr(socket, "create_connection", denied)
    monkeypatch.setattr(socket.socket, "connect", denied)
    monkeypatch.setattr(subprocess, "run", denied)
    monkeypatch.setattr(subprocess, "Popen", denied)


def test_grid_reproducible_and_topology(tmp_path):
    first = sim.build(tmp_path)
    second = sim.build(tmp_path)
    assert first == second
    assert first["status"] == "INFERRED"
    assert first["scenario_count"] == 27
    assert first["candidate_count"] == 324
    assert first["topology"]["registered_by_panel"] == [4, 22, 6]
    assert first["topology"]["active_by_panel"] == [3, 22, 6]
    assert not first["model"]["calibrated"]
    assert first["boundary"]["new_live_windows"] == 0
    assert all(math.isfinite(v) for s in first["scenarios"]
               for c in s["candidates"] for v in c["objectives"])


def test_zero_patch_gain_is_not_forced_improvement():
    baseline = sim.evaluate(False, .5, 4, .1, 1.2, 0)
    candidate = sim.evaluate(True, .5, 4, .1, 1.2, 0)
    assert baseline["aggregate_mbps"] == candidate["aggregate_mbps"]
    assert baseline["p99_ms"] == candidate["p99_ms"]
    assert candidate["assumption_risk_units"] > baseline["assumption_risk_units"]


def test_frontier_uses_dominance_and_retains_ties():
    rows = [{"objectives": obj} for obj in ([1, 1], [2, 2], [0, 3], [1, 1])]
    assert sim.frontier(rows) == [0, 2, 3]


@pytest.mark.parametrize("xw,load", [(-.1, 1), (1.1, 1), (.2, 0), (.2, float("nan"))])
def test_invalid_scenarios_fail_closed(xw, load):
    with pytest.raises(ValueError):
        sim.evaluate(False, xw, 4, .1, load, 1)


def test_score_missing_inputs_are_unknown(tmp_path):
    receipt = score.build(tmp_path)
    assert receipt["reported_windows_total"] is None
    assert receipt["reported_target_reached"] is None
    assert receipt["accepted_live_windows"] is None
    assert not receipt["live_target_accepted"]


def test_maximum_per_lane_not_sum_and_synthetic_excluded(tmp_path):
    write(tmp_path, score.INPUTS["wa"][0][0], {"cumulative_wa_windows": 344})
    write(tmp_path, score.INPUTS["wa"][1][0], {"cumulative_windows_all_10_e2e_rounds": 400})
    write(tmp_path, score.INPUTS["multi_radio"][0][0], {"cumulative_multi_radio_windows": 240,
          "windows": [{"window_id": "W1"}, {"window_id": "W1"}]})
    write(tmp_path, score.INPUTS["multi_radio"][1][0], {"execution_mode": "FALLBACK_SYNTHESIS",
          "milestone_summary": {"cumulative_multi_radio_windows": 264}, "windows": [{"window_id": "W2"}]})
    receipt = score.summarize(tmp_path)
    lanes = {row["lane"]: row for row in receipt["lanes"]}
    assert lanes["wa"]["reported_cumulative_max"] == 400
    assert lanes["multi_radio"]["reported_cumulative_max"] == 240
    assert lanes["multi_radio"]["reported_distinct_window_ids"] == ["W1"]
    assert lanes["multi_radio"]["duplicate_window_ids_removed"] == 1
    assert receipt["reported_windows_subtotal"] == 640


def test_960_reported_never_implies_live_acceptance(tmp_path):
    write(tmp_path, score.INPUTS["wa"][0][0], {"cumulative_wa_windows": 400})
    write(tmp_path, score.INPUTS["ltu"][0][0], {"cumulative_ltu_windows": 264})
    write(tmp_path, score.INPUTS["multi_radio"][0][0], {"cumulative_multi_radio_windows": 244})
    write(tmp_path, score.INPUTS["ptp"][0][0], {"cumulative_ptp_windows": 52})
    receipt = score.summarize(tmp_path)
    assert receipt["reported_windows_total"] == 960
    assert receipt["reported_target_reached"] is True
    assert receipt["live_target_accepted"] is False
    assert receipt["accepted_live_windows"] is None


@pytest.mark.parametrize("value", [-1, True, 1.2, "264"])
def test_invalid_counts_not_coerced(value):
    with pytest.raises(ValueError):
        score.nested_count({"count": value}, ("count",))


def test_progress_presence_does_not_promote(tmp_path):
    for _, slug in progress.INPUTS:
        write(tmp_path, slug + ".json", {"status": "CONFIRMED"})
    receipt = progress.build(tmp_path)
    assert "3/3" in receipt["executive_1line"]
    assert "\n" not in receipt["executive_1line"]
    assert all(row["physical_status"] == "UNKNOWN" for row in receipt["tester_matrix"])
    assert all(not row["deployment_approved"] for row in receipt["tester_matrix"])
    assert receipt["false_positive_rate_pct"] is None


def test_strict_sources_reject_duplicates_nonfinite_and_escape(tmp_path):
    with pytest.raises(ValueError):
        sim.strict_json(b'{"n": 1, "n": 2}')
    with pytest.raises(ValueError):
        sim.strict_json(b'{"n": NaN}')
    with pytest.raises(ValueError):
        sim.source(tmp_path, "../outside.json")


def test_all_docs_and_canonical_pillars(tmp_path):
    for module in (sim, progress, score):
        receipt = module.build(tmp_path)
        assert audit_stage_receipt_5pillars(receipt)["compliant"]
        text = (tmp_path / receipt["outputs"]["doc"]).read_text(encoding="utf-8")
        assert len(text.splitlines()) < 180
        assert text.count("<!-- doc-head:") == 1
        assert text.count("<!-- /doc-head -->") == 1
        assert receipt["five_pillar_compliance"]["pillar_e_memory_master_claim_id"]["ingested"] is False
