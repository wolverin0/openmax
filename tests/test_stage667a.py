"""Stage 667A — regression tests.

Pins the ath10k absence, the complete vendor descriptor lifecycle, the two descriptor flags, the
T2H completion handlers with their priority split, and the AQL/BQL refutation.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "dissect_stage667a_ath10k_htt_tx_desc_and_comp_ring_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage667a_ath10k_htt_tx_desc_and_comp_ring_re.json")

DESC = {"htt_tx_attach", "htt_tx_detach", "htt_tx_desc_alloc", "htt_tx_desc_free"}
FLAGS = ["htt_tx_desc_flag_batch_more", "htt_tx_desc_flag_postponed"]
COMPL = {"htt_tx_compl_desc_id", "htt_t2h_msg_handler", "htt_t2h_lp_msg_handler",
         "ol_tx_completion_handler"}


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "667A"
    for k in ("meta", "modules", "summary", "gaps", "ath10k_modules"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_ath10k_absent(report: dict) -> None:
    assert report["ath10k_modules"] == 0
    assert report["summary"]["ath10k_core_present"] is False


def test_four_vendor_modules(ok: list[dict], report: dict) -> None:
    assert len(ok) == 4
    assert report["summary"]["modules_ok"] == 4
    assert {r["module"].split(":")[1] for r in ok} == {"umac.ko", "ath_dev.ko"}


def test_descriptor_lifecycle_complete(report: dict) -> None:
    s = report["summary"]
    assert s["desc_lifecycle_complete"] == 1
    assert s["desc_lifecycle_count"] == 4
    assert set(s["desc_lifecycle"]) == DESC
    assert s["htt_tx_symbol_count"] == 9


def test_two_descriptor_flags(report: dict) -> None:
    s = report["summary"]
    assert s["desc_flag_count"] == 2
    assert s["desc_flags"] == FLAGS


def test_completion_path(report: dict) -> None:
    s = report["summary"]
    assert s["completion_symbol_count"] == 4
    assert set(s["completion_symbols"]) == COMPL
    assert s["compl_desc_id_present"] == 1
    assert s["os_completion_present"] == 1


def test_t2h_has_low_priority_handler(report: dict) -> None:
    s = report["summary"]
    assert s["t2h_msg_handler_present"] == 1
    assert s["t2h_lp_handler_present"] == 1


def test_aql_bql_do_not_exist(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["ath10k_only_token_hits"] == 0
    assert s["frag_desc_absent"] == 1
    assert s["aql_bql_absent"] == 1
    for r in ok:
        assert r["ath10k"]["frag_desc"] == 0
        assert r["ath10k"]["aql"] == 0
        assert r["ath10k"]["bql"] == 0


def test_peer_and_vdev_are_only_traces(report: dict) -> None:
    s = report["summary"]
    assert s["peer_id_hits"] == 2
    assert s["vdev_id_hits"] == 2
    assert s["tx_desc_layout_recovered"] == 0
    assert s["aql_bql_accounting_recovered"] == 0


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
