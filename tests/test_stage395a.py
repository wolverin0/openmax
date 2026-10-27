"""Stage 395A — regression tests.

The stage's own premise fails, so the tests guard both halves: the absence of `ath10k_core.ko`,
and the fact that the vendor `umac.ko` never pulls 84 bytes and that `htt_rx_amsdu_pop` never
calls `skb_pull`. `patch_emitted` must stay 0.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "qca988x_htt_rx_amsdu_pop_skb_pull_patch_re.py"
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage395a_qca988x_htt_rx_skb_pull_patch_re.json")

EXPECTED_HIST = {"2": 2, "4": 2, "8": 20, "14": 4, "60": 2, "248": 2}


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "395A"
    for k in ("meta", "modules", "summary", "gaps", "ath10k_modules_found"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_ath10k_module_absent(report: dict) -> None:
    assert report["ath10k_modules_found"] == []
    assert report["summary"]["ath10k_core_present"] is False
    joined = " ".join(report["meta"]["premise_corrections"])
    assert "ath10k_core.ko does not exist" in joined


def test_only_an_aql_dossier_exists(report: dict) -> None:
    docs = report["ath10k_documents_found"]
    assert docs == ["artifacts/praisonai_aql_ath10k_dossier.md"]


def test_two_vendor_modules(ok: list[dict]) -> None:
    assert len(ok) == 2
    for r in ok:
        assert r["module"].endswith("umac.ko")
        assert r["total_relocs"] == 50694
        assert r["total_pull_relocs"] == 35


def test_pull_length_histogram(report: dict, ok: list[dict]) -> None:
    assert report["summary"]["lengths_histogram"] == EXPECTED_HIST
    assert report["summary"]["distinct_pull_lengths"] == 6
    for r in ok:
        assert r["unresolved_lengths"] == 19
        assert r["total_pull_relocs"] == 16 + 19
        for k, v in EXPECTED_HIST.items():
            assert r["pull_length_histogram"][k] == v // 2


def test_84_never_pulled(report: dict, ok: list[dict]) -> None:
    assert report["summary"]["length_84_found"] == 0
    assert "84" not in report["summary"]["lengths_histogram"]
    for r in ok:
        assert "84" not in r["pull_length_histogram"]


def test_pop_function_does_not_pull(ok: list[dict], report: dict) -> None:
    assert report["summary"]["pop_symbol_present"] == 2
    assert report["summary"]["pop_calls_skb_pull"] == 0
    for r in ok:
        pop = r["functions"]["htt_rx_amsdu_pop"]
        assert pop is not None
        assert pop["start"] == "0x01bee4"
        assert pop["end"] == "0x01c2cc"
        assert pop["bytes"] == 1000
        assert r["pop_pull_count"] == 0


def test_ppdu_symbol_absent(ok: list[dict], report: dict) -> None:
    assert report["summary"]["ppdu_symbol_present"] == 0
    for r in ok:
        assert r["functions"]["htt_rx_h_ppdu"] is None
        assert r["functions"]["ath10k_htt_rx_amsdu_pop"] is None


def test_vendor_uses_netbuf_api(report: dict, ok: list[dict]) -> None:
    funcs = report["summary"]["functions_with_pulls"]
    assert "a_netbuf_pull" in funcs
    assert "a_netbuf_pull_data" in funcs
    for r in ok:
        assert r["pulls_per_function"]["ol_rx_deliver"] == 5
        assert "ieee80211_amsdu_input" in r["pulls_per_function"]


def test_no_patch_emitted(report: dict) -> None:
    assert report["summary"]["patch_emitted"] == 0
    assert "hook_offsets" not in report["summary"]
    joined = " ".join(report["gaps"])
    assert "no patch and no hook were emitted" in joined


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no binary patched" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
