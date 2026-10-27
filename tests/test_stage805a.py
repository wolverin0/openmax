"""Stage 805A — regression tests.

Pins the firmware naming refutation, the host-side ratefind walk, the two WAL debug ids, and the
absence of any sounding sequence.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "dissect_stage805a_xtensa_wal_rc_ratefind_and_txbf_sounding_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage805a_xtensa_wal_rc_ratefind_and_txbf_sounding_re.json")

WALK = {"rcGetFirstValidTxRate", "rcGetNextValidTxRate"}
WAL_DBG = {"wal_rcquery", "wal_rcupdate"}


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "805A"
    for k in ("meta", "container", "firmware_tokens", "host_tokens", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_two_sgmt_segments(report: dict) -> None:
    c = report["container"]
    assert c["segments"] == 2
    assert c["segment_bytes"] == 204677
    assert c["bytes"] == 204796


def test_firmware_carries_no_names(report: dict) -> None:
    s = report["summary"]
    assert s["firmware_named_token_hits"] == 0
    assert s["firmware_names_absent"] == 1
    for k, v in report["firmware_tokens"].items():
        assert v == 0, k


def test_ratefind_walk_is_host_side(report: dict) -> None:
    s = report["summary"]
    assert s["ratefind_walk_complete"] == 1
    assert s["ratefind_is_host_side"] == 1
    assert set(s["ratefind_walk"]) == WALK


def test_wal_debug_ids(report: dict) -> None:
    s = report["summary"]
    assert s["host_wal_dbg_count"] == 2
    assert set(s["host_wal_dbg_ids"]) == WAL_DBG


def test_no_sounding_sequence(report: dict) -> None:
    s = report["summary"]
    assert s["sounding_token_hits"] == 0
    assert s["sounding_absent"] == 1
    assert s["txbf_capability_hits"] == 7
    assert s["txbf_sounding_sequence_recovered"] == 0


def test_host_ratecontrol_family(report: dict) -> None:
    s = report["summary"]
    assert s["host_ratecontrol_symbol_count"] == 16
    assert s["sgi_mask_setter"] == 1
    assert s["xretry_penalty_present"] == 1


def test_firmware_table_not_claimed(report: dict) -> None:
    assert report["summary"]["firmware_rate_table_recovered"] == 0


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no firmware loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
