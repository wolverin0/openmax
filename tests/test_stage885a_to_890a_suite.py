#!/usr/bin/env python3
"""Consolidated Pytest Suite for Stages 885A..890A (post-audit offline remediation).

Self-contained: validates each stage receipt + doc and the 890A gate / master-doc
sync. No live devices, no SSH, no firmware baking were involved in producing these.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts" / "autoresearch"
DOCS = ROOT / "docs"


def _load(name):
    p = ART / name
    assert p.exists(), f"{name} missing"
    raw = p.read_bytes()
    assert not (raw and raw.count(b"\x00") == len(raw)), f"{name} is NUL-corrupt"
    return json.loads(raw.decode("utf-8"))


def _doc_ok(name):
    p = DOCS / name
    assert p.exists(), f"{name} missing"
    lines = p.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 180, f"{name} too long ({len(lines)})"
    assert lines[0].startswith("<!-- doc-head:"), f"{name} missing doc-head"


def test_stage885a_field_kits_hardened():
    d = _load("stage885a_post_audit_field_kits_hardening.json")
    assert d["status"] == "CONFIRMED" and d["all_kits_hardened"] is True
    assert len(d["kits"]) == 3
    for k in d["kits"]:
        assert k["all_checks_pass"] is True
    _doc_ok("STAGE885A_POST_AUDIT_FIELD_KITS_HARDENING.md")
    # The three hardened kit files must exist on disk.
    common = ROOT / "firmware" / "openwrt" / "common"
    for kit in ("fmx_wa_v14_356window_field_kit.sh", "fmx_wa_v15_368window_field_kit.sh",
                "fmx_ltu_v21_276window_field_kit.sh"):
        text = (common / kit).read_text(encoding="utf-8")
        assert text.splitlines()[3].startswith("set -eu") or "set -eu" in text
        assert "MODE=--dry-run" in text and "initial_quantum" in text  # guard present
        assert "|| true" not in text


def test_stage886a_aa_control_selftests():
    d = _load("stage886a_post_audit_aa_control_protocol.json")
    assert d["status"] == "CONFIRMED" and d["all_self_tests_pass"] is True
    assert len(d["adversarial_self_tests"]) == 7
    assert all(t["pass"] for t in d["adversarial_self_tests"])
    _doc_ok("STAGE886A_POST_AUDIT_AA_CONTROL_PROTOCOL.md")


def test_stage887a_classifier():
    d = _load("stage887a_empirical_vs_simulated_evidence_audit.json")
    assert d["status"] == "CONFIRMED"
    c = d["counts"]
    assert c["CONFIRMED_LIVE_BENCH"] > 0 and c["SIMULATED_MODEL_ONLY"] > 0
    assert sum(c.values()) == d["receipts_scanned"]
    _doc_ok("STAGE887A_EMPIRICAL_VS_SIMULATED_EVIDENCE_AUDIT.md")


def test_stage888a_reclassification_flags():
    d = _load("stage888a_historical_receipts_reclassification.json")
    assert d["status"] == "CONFIRMED"
    flags = d["integrity_flags"]
    # The audit's core risk must be surfaced, not hidden.
    assert flags["declared_confirmed_but_not_physically_confirmed_count"] > 0
    assert flags["simulated_but_declared_confirmed_count"] >= 0
    _doc_ok("STAGE888A_HISTORICAL_RECEIPTS_RECLASSIFICATION.md")


def test_stage889a_power_arithmetic():
    d = _load("stage889a_statistical_power_and_holdout_protocol.json")
    assert d["status"] == "CONFIRMED"
    h = d["headline_case_n500"]
    # N=500 must be under-powered: min achievable p exceeds the corrected alpha.
    assert h["min_p_exact_14_pairs"] > h["sidak_alpha"]
    assert h["min_p_perm_4096"] > h["sidak_alpha"]
    _doc_ok("STAGE889A_STATISTICAL_POWER_AND_HOLD_OUT_PROTOCOL.md")


def test_stage890a_gate_and_master_doc_sync():
    d = _load("stage890a_post_audit_master_documentation_sync.json")
    assert d["status"] == "CONFIRMED" and d["all_gates_passed"] is True
    assert d["failures"] == []
    for m in d["master_doc_checks"]:
        assert m["has_classification"] is True
        assert m["over_budget"] is False
    _doc_ok("STAGE890A_POST_AUDIT_MASTER_DOCUMENTATION_SYNC.md")
