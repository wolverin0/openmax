"""Stage 713A — regression tests.

Pins the per-engine CE implementation, the watermark API, the separate TX/RX completion walkers, the
runtime queue allocation, the pktlog lifecycle, the MSN negotiation, and the CE0..CE7 refutation.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "dissect_stage713a_ath10k_pci_copy_engine_rings_and_msi_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage713a_ath10k_pci_copy_engine_rings_and_msi_re.json")

PER_ENGINE = {"CE_per_engine_handler", "CE_per_engine_service",
              "CE_per_engine_service_any", "CE_per_engine_servicereap"}
RECV = {"CE_recv_buf_enqueue", "CE_recv_entries_avail", "CE_recv_entries_done",
        "CE_recv_watermarks_set", "CE_recv_cb_register"}


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "713A"
    for k in ("meta", "modules", "summary", "gaps", "ath10k_modules"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_ath10k_absent(report: dict) -> None:
    assert report["ath10k_modules"] == 0
    assert report["summary"]["ath10k_core_present"] is False


def test_two_vendor_modules(ok: list[dict], report: dict) -> None:
    assert len(ok) == 2
    assert report["summary"]["modules_ok"] == 2
    assert {r["module"] for r in ok} == {"WA:umac.ko", "XC:umac.ko"}


def test_ce_is_per_engine(report: dict) -> None:
    s = report["summary"]
    assert s["ce_symbol_count"] == 24
    assert s["per_engine_service_present"] == 1
    assert s["per_engine_service_variants"] == 4
    assert PER_ENGINE <= set(s["ce_symbols"]) or len(
        [n for n in s["ce_symbols"] if "per_engine" in n]) >= 1


def test_separate_tx_rx_completions(ok: list[dict]) -> None:
    joined = " ".join(n for r in ok for n in r["ce_symbols"])
    assert "CE_completed_send_next" in joined
    assert "CE_completed_recv_next" in joined
    assert "CE_completed_send_next_nolock" in joined


def test_watermark_api(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["watermark_api_present"] == 1
    assert s["recv_control_count"] == 5
    for r in ok:
        for k in RECV:
            assert r["recv"][k] >= 1, k


def test_engines_are_not_numbered(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["numbered_ce_hits"] == 0
    assert s["engines_are_numbered"] == 0
    assert s["engine_count_proven"] == 0
    for r in ok:
        for i in range(8):
            assert r["numbered"][f"CE{i}"] == 0


def test_queue_allocation_is_runtime(report: dict) -> None:
    s = report["summary"]
    assert s["hif_queue_alloc"] == 1
    assert "HIFGetFreeQueueNumber" in s["hif_queue_symbols"]
    assert s["ring_service_map_recovered"] == 0


def test_pktlog_lifecycle(report: dict) -> None:
    s = report["summary"]
    assert s["pktlog_lifecycle"] == 1
    # alloc_buf is an ELF symbol; release_buf and setsize are string-level names,
    # so the lifecycle is proven from the raw token counts
    joined = " ".join(s["pktlog_symbols"])
    assert "pktlog_alloc_buf" in joined
    raw = s["pktlog_raw_counts"]
    for key in ("pktlog_alloc_buf", "pktlog_release_buf", "pktlog_setsize"):
        assert raw[key] >= 1, key


def test_msi_is_negotiated(report: dict) -> None:
    s = report["summary"]
    assert s["msi_is_negotiated"] == 1
    assert s["msi_negotiation_msg"] == 2
    assert s["legacy_fallback_msg"] >= 1


def test_nentries_not_recovered(report: dict) -> None:
    assert report["summary"]["ce_nentries_table_recovered"] == 0


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
