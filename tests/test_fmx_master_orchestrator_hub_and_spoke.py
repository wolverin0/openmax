#!/usr/bin/env python3
"""Unit tests for the FuturaMAX Hub-and-Spoke Master Orchestrator & Worker Isolation Contract."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.orchestration import fmx_master_orchestrator as orch

ROOT = Path(__file__).resolve().parents[1]


def test_hub_and_spoke_state_alignment() -> None:
    state = orch.load_state()
    al = orch.alignment_check(state)
    assert al["status"] == "CONFIRMED", f"Alignment failed: {al['failures']}"
    hsc = state.get("hub_and_spoke_contract") or {}
    assert hsc.get("topology") == "STRICT_STAR_HUB_AND_SPOKE"
    assert hsc.get("orchestrator_terminal_handle") in {
        "term_83338289-c8b3-4e0a-8243-33f1f7c8b283",
        "term_55e75368-b08d-4290-9a81-7deca4f34d34",
    }
    assert hsc.get("orchestrator_run_id") in {
        "run_265172f88f41",
        "run_fecc7c4d0e76",
    }


def test_isolated_worker_contracts_never_leak_other_lanes() -> None:
    import copy
    state = copy.deepcopy(orch.load_state())
    lanes = list(state["lanes"].keys())
    assert len(lanes) == 5
    for lane_id in lanes:
        lane = state["lanes"][lane_id]
        if not lane.get("active_round") and not lane.get("queued_rounds"):
            dom = (lane.get("owned_domains") or ["D3_PTMP_GUARIDA"])[0]
            lane["queued_rounds"] = [{
                "wave": "Wave Test",
                "stages": "9990A..9991A",
                "domain": dom,
                "objective": f"Synthetic isolated test task for {lane_id}",
                "expected_gate": f"artifacts/verification/test_{lane_id}_gate.json",
            }]
        contract = orch.build_isolated_worker_contract(state, lane_id)
        assert contract["lane_id"] == lane_id
        assert "task" in contract
        brief = orch.format_isolated_worker_brief(contract)
        assert f"=== FUTURAMAX WORKER TASK CONTRACT [{lane_id}] ===" in brief
        assert f"--to run:{state['orchestrator_run_id']}" in brief
        # Ensure other lanes' terminal handles never appear in a worker's isolated brief
        for other_id, other_lane in state["lanes"].items():
            if other_id != lane_id:
                assert other_lane["terminal_handle"] not in brief


def test_domain_and_filter_affinity_guard() -> None:
    state = orch.load_state()
    # 1. /fullrea or decompilation is strictly forbidden on any lane except lane_4_opencode_deepseek
    opus_lane = state["lanes"]["lane_3_opus"]
    codex_lane = state["lanes"]["lane_1_codex"]
    deepseek_lane = state["lanes"]["lane_4_opencode_deepseek"]

    errs_opus = orch.validate_domain_and_filter_affinity(
        "lane_3_opus", opus_lane, "D3_PTMP_GUARIDA", "Run /fullrea decompile on ubnt_poll_host.ko"
    )
    assert errs_opus, "Opus lane must reject /fullrea and decompile"

    errs_codex = orch.validate_domain_and_filter_affinity(
        "lane_1_codex", codex_lane, "D3_PTMP_GUARIDA", "Run /fullrea decompile on ubnt_poll_host.ko"
    )
    assert errs_codex, "Codex lane must reject /fullrea exclusive to lane_4_opencode_deepseek"

    errs_deepseek = orch.validate_domain_and_filter_affinity(
        "lane_4_opencode_deepseek", deepseek_lane, "D5_FULLREA_DEEPSEEK_DECOMP", "Run /fullrea decompile on ubnt_poll_host.ko"
    )
    assert not errs_deepseek, f"DeepSeek lane must allow /fullrea, got: {errs_deepseek}"

    # 2. Cross-domain assignment must be rejected
    errs_wrong_dom = orch.validate_domain_and_filter_affinity(
        "lane_1_codex", codex_lane, "D7_HYPERRESEARCH_VAULT", "Index vault notes"
    )
    assert errs_wrong_dom, "Cross-domain assignment outside owned_domains must fail"


def test_all_five_wave337_dispatches_pass_dry_run() -> None:
    import copy
    state = copy.deepcopy(orch.load_state())
    order = (state.get("wave_alignment") or {}).get("lane_priority_queue") or list(state["lanes"].keys())
    assert order == [
        "lane_3_opus",
        "lane_4_opencode_deepseek",
        "lane_2_codex",
        "lane_1_codex",
        "lane_5_opus",
    ]
    for lid in order:
        lane = state["lanes"][lid]
        if not lane.get("active_round") and not lane.get("queued_rounds"):
            dom = (lane.get("owned_domains") or ["D3_PTMP_GUARIDA"])[0]
            lane["queued_rounds"] = [{
                "wave": "Wave Test",
                "stages": "9990A..9991A",
                "domain": dom,
                "objective": f"Synthetic dry-run task for {lid}",
                "expected_gate": f"artifacts/verification/test_{lid}_gate.json",
            }]
        res = orch.dispatch_lane(state, lid, dry_run=True)
        assert res["dispatched"] is True, f"Failed dry-run for {lid}: {res}"
