"""Stage 459A — regression tests.

Pins the exact `mpdus_requed` match, the `excess retries` spelling refutation, the BAR debug-id
taxonomy, and the two TID-pause symbols including Ubiquiti's `pasued` typo.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "build_stage459a_qca988x_wal_tx_tid_pause_and_bar_recovery_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage459a_qca988x_wal_tx_tid_pause_and_bar_recovery_re.json")

PAUSE_SYMS = {"ath_net80211_exist_pendingfrm_tidq", "ath_net80211_reset_pasued_tid"}
RETRY_SYMS = {"_RATE_GetTxRetrySchedule", "ath_net80211_set_swretrystate",
              "g_default_xretry_per_penalty"}


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "459A"
    for k in ("meta", "firmware_images", "modules", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_firmware_absent(report: dict) -> None:
    assert report["firmware_images"] == {"firmware-2.bin": 0, "firmware-5.bin": 0}
    assert report["summary"]["firmware_images_present"] == 0


def test_two_identical_images(ok: list[dict], report: dict) -> None:
    assert len(ok) == 2
    assert {r["module"] for r in ok} == {"WA.v8.7.25:umac.ko", "XC.v8.7.25:umac.ko"}
    assert ok[0]["counters"] == ok[1]["counters"]
    assert report["summary"]["modules_ok"] == 2


def test_mpdus_requed_is_exact(ok: list[dict], report: dict) -> None:
    assert report["summary"]["mpdus_requed_hits"] == 2
    assert report["summary"]["stats_dump_present"] == 1
    for r in ok:
        assert r["counters"]["mpdus_requed"] == 1
        ctx = " ".join(r["counter_contexts"]["mpdus_requed"])
        assert "mpdus_requed" in ctx
        assert "tx_abort" in ctx


def test_excess_retries_spelling(ok: list[dict], report: dict) -> None:
    s = report["summary"]
    assert s["excess_retries_underscore"] == 0
    assert s["excess_retries_spaced"] == 2
    assert s["excess_retries_spelling_refuted"] == 1
    for r in ok:
        assert r["counters"]["excess_retries"] == 0
        assert r["counters"]["excess retries"] == 1
        ctx = " ".join(r["counter_contexts"]["excess retries"])
        assert "excess retries" in ctx


def test_bar_taxonomy(ok: list[dict], report: dict) -> None:
    assert report["summary"]["bar_debug_id_hits"] == 8
    assert report["summary"]["bar_failure_named"] == 1
    for r in ok:
        assert r["bar_ids"]["WAL_DBGID_BAR_TX_FAIL"] == 1
        assert r["bar_ids"]["WAL_DBGID_BAR_ALLOC_FAIL"] == 1
        assert r["bar_ids"]["WAL_DBGID_STA_KICKOUT"] == 1
        assert r["bar_ids"]["WAL_DBGID_LOCAL_DATA_TX_FAIL"] == 1
        ctx = " ".join(r["bar_contexts"])
        assert "WAL_DBGID_BAR_TX_FAIL" in ctx


def test_tid_pause_uses_vendor_spelling(ok: list[dict], report: dict) -> None:
    s = report["summary"]
    assert s["tid_pause_named"] == 1
    assert set(s["pause_symbols"]) == PAUSE_SYMS
    for r in ok:
        # the correctly spelled name must NOT exist
        assert "ath_net80211_reset_paused_tid" not in r["tid_symbols"]
        assert "ath_net80211_reset_pasued_tid" in r["tid_symbols"]


def test_retry_schedule_symbols(report: dict) -> None:
    assert RETRY_SYMS <= set(report["summary"]["retry_symbols"])
    assert report["summary"]["retry_symbols"]


def test_vap_pause_family(ok: list[dict]) -> None:
    for r in ok:
        assert r["tid"]["unpause"] > 0
        assert r["tid"]["pause"] > 0


def test_increment_sites_not_claimed(report: dict) -> None:
    assert report["summary"]["counter_increment_sites"] == 0
    joined = " ".join(report["gaps"])
    assert "the increment sites and the wrap/decay rules were not located" in joined


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no firmware loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
