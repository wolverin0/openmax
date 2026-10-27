"""Stage 156A — regression tests for the 571-knob vs umac/ath_dev handler audit.

The decisive result is a partition: every knob whose name appears in a driver module belongs
to `airOS_UMAC_UPH`; the `QCA_10_1_FW` and `LTU_AME_FW` boundaries have **zero** presence in
`umac.ko`/`ath_dev.ko`, because they live in firmware, not in the host driver. These tests pin
that partition and the claim limit (a string match is not proof of effect).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "audit_stage156a_571knobs_umac_athdev_handler_audit.py"
RECEIPT = REPO / "artifacts" / "autoresearch" / "stage156a_571knobs_umac_athdev_handler_audit.json"


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"receipt missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


def test_receipt_shape(report: dict) -> None:
    for key in ("meta", "modules", "summary", "knobs", "gaps"):
        assert key in report
    assert report["meta"]["stage"] == "156A"


def test_eight_modules(report: dict) -> None:
    assert len(report["modules"]) == 8, "WA/XC/XW614/XW636 x (umac, ath_dev)"
    for key, m in report["modules"].items():
        assert m["bytes"] > 200_000
        assert m["strings"] > 1000


def test_571_knobs_covered(report: dict) -> None:
    assert report["summary"]["knobs"] == 571
    assert len(report["knobs"]) == 571


def test_every_knob_has_a_verdict(report: dict) -> None:
    for k in report["knobs"]:
        assert isinstance(k["handler_name_present"], bool)
        if k["handler_name_present"]:
            assert k["matched_literal"]
        else:
            assert k["matched_literal"] is None
        assert k["effect_on_registers"] == "UNKNOWN"


def test_no_register_effect_is_claimed(report: dict) -> None:
    assert report["summary"]["effect_on_registers_confirmed"] == 0
    assert "UNKNOWN for all 571" in " ".join(report["gaps"])


def test_claim_limit_is_explicit(report: dict) -> None:
    limit = report["meta"]["claim_limit"]
    assert "NECESSARY condition" in limit
    assert "not proof of effect" in limit


def test_boundary_partition(report: dict) -> None:
    by = report["summary"]["by_boundary"]
    # every matched knob is airOS_UMAC_UPH
    assert by["airOS_UMAC_UPH"]["present"] == report["summary"]["handler_name_present"]
    # firmware boundaries have zero presence in the host driver modules
    assert by["QCA_10_1_FW"].get("present", 0) == 0
    assert by["LTU_AME_FW"].get("present", 0) == 0
    assert by["QCA_10_1_FW"]["absent"] == 103
    assert by["LTU_AME_FW"]["absent"] == 20


def test_coverage_is_plausible(report: dict) -> None:
    pct = report["summary"]["coverage_pct"]
    assert 0.0 < pct < 100.0
    assert 50.0 <= pct <= 70.0, f"coverage drifted: {pct}%"


def test_source_hash_recorded(report: dict) -> None:
    assert len(report["meta"]["source_sha256"]) == 64
    assert report["meta"]["source"].endswith("firmware_knob_candidates.json")


def test_radio_safety_declared(report: dict) -> None:
    assert "no radio contacted" in report["meta"]["scope"]


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    after = RECEIPT.read_bytes()
    assert before == after, "receipt is not deterministic across runs"
