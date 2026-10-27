#!/usr/bin/env python3
"""Unit & Binary Verification Suite for Stage 128A:
Reddit & GitHub Release Package for `PowerBeam 5AC Gen2` and `LiteBeam 5AC Gen2` (`WA` Family) Testers.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parent.parent
RECEIPT_PATH = (
    REPO_ROOT
    / "artifacts"
    / "autoresearch"
    / "stage128a_reddit_tester_release_package.json"
)
REDDIT_DOC_PATH = REPO_ROOT / "docs" / "REDDIT_REPLY_FIRMWARE_TESTERS_WA_FAMILY.md"


def test_stage128a_receipt_passes_5pillar_gate_and_safety():
    assert RECEIPT_PATH.exists(), f"Missing {RECEIPT_PATH}"
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))

    gate = audit_stage_receipt_5pillars(data)
    assert gate["compliant"] is True, f"5-pillar gate failed: {gate}"
    assert data["stage"] == "128A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_verification"]["pbe5ac_241_242_touched"] is False
    assert data["safety_verification"]["guarida_poe_switches_200_201_touched"] is False
    assert data["safety_verification"]["flash_writes_performed"] == 0


def test_reddit_tester_reply_doc_budget_and_commands():
    assert REDDIT_DOC_PATH.exists(), f"Missing {REDDIT_DOC_PATH}"
    raw = REDDIT_DOC_PATH.read_bytes()
    txt = raw.decode("utf-8")
    lines = txt.splitlines()

    assert len(lines) < 120, f"Expected < 120 lines, got {len(lines)}"
    assert sum(1 for ln in lines if "<!-- doc-head:" in ln) == 1
    assert "/sbin/fwupdate.real -c" in txt
    assert "/sbin/fwupdate.real -m" in txt
    assert "sysupgrade -v" in txt
    assert "sysupgrade -n" in txt
    assert "for m in mtd0 mtd1 mtd4 mtd5" in txt
    assert "iperf3 -c" in txt
    assert "p50=" in txt and "p95=" in txt and "p99=" in txt

    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    doc_meta = data["reddit_reply_doc_verification"]
    assert doc_meta["all_checks_passed"] is True
    assert hashlib.sha256(raw).hexdigest() == doc_meta["sha256"]


def test_all_16_wa_family_sha256_checksums_present_in_reddit_reply():
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    txt = REDDIT_DOC_PATH.read_text(encoding="utf-8")
    table = data["wa_family_tester_checksum_table"]

    assert set(table.keys()) == {
        "powerbeam-5ac-gen2",
        "litebeam-5ac-gen2",
        "lap-120",
        "nanostation-ac-loco",
    }
    for slug, entry in table.items():
        assert entry["all_4_sha256_in_reddit_doc"] is True, f"{slug} missing SHA-256 in doc"
        for k in ("factory_ap_sha256", "factory_sta_sha256", "sysupgrade_ap_sha256", "sysupgrade_sta_sha256"):
            assert len(entry[k]) == 64
            assert entry[k] in txt, f"{slug} {k} missing from {REDDIT_DOC_PATH}"
