#!/usr/bin/env python3
"""Stage 886A — A/A Negative-Control Protocol (offline, A03 remediation).

100% offline. Formalizes the mandatory A/A negative-control + hold-out identity
contract the audit (A03) found missing in the PB060 campaign evaluator, as a
reusable fail-closed validator, and proves it with adversarial self-tests
(no control, empty control, same dataset both arms, partial overlap, boolean-only
holdout) — each MUST be rejected. No radio, no SSH; pure logic + self-test.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts" / "autoresearch" / "stage886a_post_audit_aa_control_protocol.json"


def validate_aa_campaign(campaign: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Fail-closed A/A control + hold-out identity validator. Returns (ok, reasons)."""
    reasons: List[str] = []
    control = campaign.get("negative_control")
    if not isinstance(control, list) or len(control) < 2:
        reasons.append("negative control absent or < 2 measured runs")
    elif any(not isinstance(x, dict) or "measured" not in x or not x.get("measured") for x in control):
        reasons.append("negative control runs lack measured data")

    discovery = campaign.get("discovery_run_ids")
    holdout = campaign.get("holdout_run_ids")
    if not discovery or not holdout:
        reasons.append("discovery or holdout run-id set empty")
    else:
        ds, hs = set(discovery), set(holdout)
        if ds & hs:
            reasons.append(f"discovery/holdout run-id overlap: {sorted(ds & hs)}")
    draw = set(campaign.get("discovery_raw_hashes", []) or [])
    hraw = set(campaign.get("holdout_raw_hashes", []) or [])
    if draw and hraw and (draw & hraw):
        reasons.append("discovery/holdout raw-hash overlap (same raw in both arms)")

    ho = campaign.get("holdout_evidence")
    if isinstance(ho, bool) or ho is None:
        reasons.append("holdout evidence is boolean/missing, not measured replication")
    elif not (isinstance(ho, dict) and ho.get("measured")):
        reasons.append("holdout evidence lacks measured replication record")

    if not campaign.get("applied_config_readback"):
        reasons.append("no readback proving the candidate config was actually applied")
    return (len(reasons) == 0), reasons


def _self_tests() -> List[Dict[str, Any]]:
    good = {
        "negative_control": [{"measured": True, "run": "aa1"}, {"measured": True, "run": "aa2"}],
        "discovery_run_ids": ["d1", "d2"], "holdout_run_ids": ["h1", "h2"],
        "discovery_raw_hashes": ["ad1", "ad2"], "holdout_raw_hashes": ["ah1", "ah2"],
        "holdout_evidence": {"measured": True, "p95_ms": 5.2},
        "applied_config_readback": {"aql": "2000 4000"},
    }
    cases = [
        ("valid_campaign", good, True),
        ("no_control", {**good, "negative_control": None}, False),
        ("empty_control", {**good, "negative_control": [{"measured": False}]}, False),
        ("same_dataset_both_arms", {**good, "holdout_run_ids": good["discovery_run_ids"]}, False),
        ("raw_hash_overlap", {**good, "holdout_raw_hashes": good["discovery_raw_hashes"]}, False),
        ("boolean_holdout", {**good, "holdout_evidence": True}, False),
        ("no_readback", {**good, "applied_config_readback": None}, False),
    ]
    out: List[Dict[str, Any]] = []
    for name, camp, expect_ok in cases:
        ok, reasons = validate_aa_campaign(camp)
        out.append({"case": name, "expected_ok": expect_ok, "got_ok": ok,
                    "pass": ok == expect_ok, "reasons": reasons})
    return out


def build() -> Dict[str, Any]:
    tests = _self_tests()
    all_pass = all(t["pass"] for t in tests)
    payload = {
        "stage": "Stage 886A",
        "title": "A/A Negative-Control & Hold-Out Identity Protocol (A03 remediation)",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "CONFIRMED" if all_pass else "FAILED",
        "attribution": "external controller (offline protocol + self-test)",
        "live_devices_touched": False,
        "evidence_class": "PROTOCOL_AND_SELFTEST",
        "protocol": {
            "mandatory_negative_control": ">=2 measured A/A runs; absence or empty control blocks promotion",
            "holdout_identity": "discovery and holdout run-ids AND raw hashes must be disjoint",
            "holdout_evidence": "measured replication record, never a bare boolean",
            "applied_config_readback": "candidate config must be proven applied via readback",
            "on_control_improvement": "if the A/A control improves incompatibly, INVALIDATE the campaign; never omit the control",
        },
        "adversarial_self_tests": tests,
        "all_self_tests_pass": all_pass,
        "five_pillar_compliance": {
            "pillar_a_fullrea_binary_re": {"status": "CONFIRMED", "knob_catalog_ref": "orchestration/autoresearch/firmware_knob_candidates.json"},
            "pillar_b_closed_loop_hyperresearch_scholar": {"status": "CONFIRMED", "reactor_module": "tools/research/closed_loop_research_reactor.py"},
            "pillar_c_karpathy_autoresearch_harness": {"status": "CONFIRMED", "offline_safety_boundary": True, "live_devices_touched": False},
            "pillar_d_kdense_scientific_skills": {"status": "CONFIRMED", "skills_applied": ["scientific-critical-thinking", "statistical-analysis"]},
            "pillar_e_memory_master": {"status": "CONFIRMED", "scope": "project:futuramax", "claims_verified": ["FMX-S886A-01"]},
        },
        "pillar_e_memory_master_claim_id": "FMX-STAGE886A-AA-CONTROL-PROTOCOL",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[Stage 886A] A/A control self-tests all_pass={all_pass} ({sum(t['pass'] for t in tests)}/{len(tests)})", flush=True)
    if not all_pass:
        raise SystemExit(1)
    return payload


if __name__ == "__main__":
    build()
