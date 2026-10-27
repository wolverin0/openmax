"""Stage 901A..904A suite — provenance remediation, full-corpus audit, restoration and gate.

The suite asserts the remediation outcome, the independence of the restoration check, the honest split
between "scope clean" and "corpus clean", the documentation contract and reproducibility.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
AR = REPO / "artifacts" / "autoresearch"

R = {
    "901A": AR / "stage901a_provenance_remediation_receipt.json",
    "902A": AR / "stage902a_full_corpus_provenance_audit.json",
    "903A": AR / "stage903a_provenance_restoration_registry.json",
    "904A": AR / "stage904a_zero_ambiguous_receipts_gate.json",
}

TOOLS = {
    "901A": REPO / "tools" / "verify" / "remediate_stage901a_undeclared_provenance_receipts.py",
    "902A": REPO / "tools" / "verify" / "audit_stage902a_full_corpus_provenance.py",
    "903A": REPO / "tools" / "verify" / "verify_stage903a_provenance_restoration_registry.py",
    "904A": REPO / "tools" / "verify" / "gate_stage904a_zero_ambiguous_receipts.py",
}

DOCS = {
    "901A": REPO / "docs" / "STAGE901A_PROVENANCE_REMEDIATION.md",
    "902A": REPO / "docs" / "STAGE902A_FULL_CORPUS_PROVENANCE_AUDIT.md",
    "903A": REPO / "docs" / "STAGE903A_PROVENANCE_RESTORATION_REGISTRY.md",
    "904A": REPO / "docs" / "STAGE904A_ZERO_AMBIGUOUS_RECEIPTS_GATE.md",
}

CLASSES = ("CONFIRMED_LIVE_HARDWARE", "CONFIRMED_STATIC_BINARY", "SIMULATED_MODEL_ONLY")
END_TOKEN = b'"post_audit_remediation_source": "stage901a",'


def load(stage: str) -> dict:
    assert R[stage].exists(), f"missing receipt: {R[stage]}"
    return json.loads(R[stage].read_text(encoding="utf-8-sig"))


def strip_block(raw: bytes) -> bytes:
    start = raw.find(b'\n  "evidence_provenance_class":')
    if start < 0:
        return raw
    end = raw.find(END_TOKEN, start)
    if end < 0:
        return raw
    return raw[:start] + raw[end + len(END_TOKEN):]


def test_all_four_receipts_and_tools_and_docs_exist() -> None:
    for stage in R:
        assert R[stage].exists(), stage
        assert TOOLS[stage].exists(), stage
        assert DOCS[stage].exists(), stage


def test_docs_respect_the_contract() -> None:
    for stage, path in DOCS.items():
        text = path.read_text(encoding="utf-8")
        lines = text.count("\n") + (0 if text.endswith("\n") else 1)
        assert lines < 180, f"{stage} doc has {lines} lines"
        assert text.count("<!-- doc-head") == 1, stage
        prose = re.sub(r"```.*?```", "", re.sub(r"<!--.*?-->", "", text, flags=re.S), flags=re.S)
        assert "!" not in prose, f"{stage} doc contains an exclamation mark in prose"


def test_901a_remediated_all_targets() -> None:
    summary = load("901A")["summary"]
    assert summary["targets"] == 31
    assert summary["ambiguous_remaining"] == 0
    assert summary["failed"] == 0
    assert summary["restoration_verified_all"] == 1
    assert summary["live_hardware"] + summary["static_binary"] + summary["simulated_model"] == 31


def test_901a_every_target_file_carries_the_fields_and_a_valid_class() -> None:
    report = load("901A")
    for name in report["targets"]:
        receipt = json.loads((AR / name).read_text(encoding="utf-8-sig"))
        assert "evidence_provenance_class" in receipt, name
        assert "post_audit_reclassified_at" in receipt, name
        assert "preserved_raw_sha256" in receipt, name
        assert receipt["evidence_provenance_class"] in CLASSES, name


def test_901a_restoration_holds_independently_of_the_receipt() -> None:
    report = load("901A")
    for name in report["targets"]:
        raw = (AR / name).read_bytes()
        receipt = json.loads(raw.decode("utf-8-sig"))
        preserved = receipt["preserved_raw_sha256"]
        recomputed = hashlib.sha256(strip_block(raw)).hexdigest()
        assert recomputed == preserved, name


def test_902a_audits_the_whole_directory() -> None:
    summary = load("902A")["summary"]
    # the audit family excludes its own four receipts so a run cannot change the population it
    # measures; every other file must still be classified
    assert summary["receipts_classified"] + summary["audit_receipts_excluded"] == \
        summary["receipts_in_directory"]
    assert summary["audit_receipts_excluded"] == 4
    assert summary["receipts_in_directory"] >= 1000
    assert summary["coverage_fraction"] == 1.0


def test_902a_reports_the_residual_instead_of_hiding_it() -> None:
    report = load("902A")
    summary = report["summary"]
    assert summary["undeclared"] == len(report["undeclared"])
    assert summary["zero_ambiguous"] == 0
    assert summary["undeclared"] > 0
    # the remediated 31 must not appear in the residual
    remediated = set(load("901A")["targets"])
    assert remediated.isdisjoint(set(report["undeclared"]))


def test_903a_verifies_every_remediation() -> None:
    summary = load("903A")["summary"]
    assert summary["receipts"] == 31
    assert summary["verified"] == 31
    assert summary["restoration_verified"] == 31
    assert summary["class_valid"] == 31
    assert summary["all_restored"] == 1


def test_903a_counts_agree_with_901a() -> None:
    a = load("901A")["summary"]
    b = load("903A")["summary"]
    assert b["live_hardware"] == a["live_hardware"]
    assert b["static_binary"] == a["static_binary"]
    assert b["simulated_model"] == a["simulated_model"]


def test_904a_gate_compliant_and_honest() -> None:
    summary = load("904A")["summary"]
    assert summary["failures"] == 0
    assert summary["compliant"] == 1
    assert summary["checks_run"] == summary["checks_passed"]
    assert summary["remediation_zero_ambiguous"] == 1
    # the gate must never be quotable as a clean corpus
    assert summary["full_corpus_zero"] == 0
    assert summary["full_corpus_undeclared"] == load("902A")["summary"]["undeclared"]


def test_904a_outstanding_split_is_reported() -> None:
    outstanding = load("904A")["outstanding"]
    assert outstanding["historical_stage_receipts"] > 0
    assert outstanding["auxiliary_artefacts"] > 0
    assert (outstanding["historical_stage_receipts"] + outstanding["auxiliary_artefacts"]
            == outstanding["full_corpus_undeclared"])


def test_every_tool_is_reproducible() -> None:
    for tool in TOOLS.values():
        subprocess.run([sys.executable, str(tool)], check=True, cwd=str(REPO),
                       stdout=subprocess.DEVNULL)
    before = {stage: path.read_bytes() for stage, path in R.items()}
    for tool in TOOLS.values():
        subprocess.run([sys.executable, str(tool)], check=True, cwd=str(REPO),
                       stdout=subprocess.DEVNULL)
    for stage, path in R.items():
        assert path.read_bytes() == before[stage], f"{stage} receipt is not deterministic"
