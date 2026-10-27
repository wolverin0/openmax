"""Stage 647A — regression tests.

Pins the three ring-config message forms, the attention bit-31 mask, the decap-means-decryption
refutation, the host_80211 boolean boundary, and the mixed A-MSDU family.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "build_stage647a_qca988x_htt_rx_ring_decap_and_amsdu_subframe_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage647a_qca988x_htt_rx_ring_decap_and_amsdu_subframe_re.json")

RING_CFG = {"htt_h2t_rx_ring_cfg_msg", "htt_h2t_rx_ring_cfg_msg_hl",
            "htt_h2t_rx_ring_cfg_msg_ll"}


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "647A"
    for k in ("meta", "modules", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_four_modules(ok: list[dict], report: dict) -> None:
    assert len(ok) == 4
    assert report["summary"]["modules_ok"] == 4
    assert {r["module"].split(":")[1] for r in ok} == {"umac.ko", "ath_dev.ko"}


def test_three_ring_config_forms(report: dict) -> None:
    s = report["summary"]
    assert s["ring_cfg_variant_count"] == 3
    assert s["ring_cfg_has_hl_ll"] == 1
    assert set(s["ring_cfg_variants"]) == RING_CFG
    assert s["htt_symbol_count"] == 30


def test_attention_mask_is_bit31(report: dict) -> None:
    s = report["summary"]
    assert s["attention_mask"] == "0x80000000"
    assert s["attention_flag_recovered"] == 1
    assert s["attention_assert_hits"] >= 1
    assert s["attention_retriever_present"] == 1


def test_decap_means_decryption(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["decap_is_crypto_modules"] == 2
    assert s["native_raw_enum_absent"] == 1
    assert s["native_wifi_hits"] == 0
    assert s["raw_mode_hits"] == 0
    assert s["decap_mode_hits"] == 0
    for r in ok:
        assert r["tokens"]["native_wifi"] == 0
        assert r["tokens"]["raw_mode"] == 0


def test_host_80211_boundary(report: dict) -> None:
    s = report["summary"]
    assert s["host_80211_modules"] == 2
    assert s["host_80211_boundary"] == 1


def test_amsdu_family_is_mixed(report: dict) -> None:
    s = report["summary"]
    assert s["amsdu_symbol_count"] == 17
    assert s["amsdu_tx_symbols"] == 9
    assert s["amsdu_rx_symbols"] == 3
    assert s["amsdu_is_mixed"] == 1
    assert s["rx_amsdu_pop_hits"] == 8
    assert s["rx_amsdu_present"] == 1


def test_deaggregation_not_decoded(report: dict) -> None:
    assert report["summary"]["subframe_deagg_decoded"] == 0
    joined = " ".join(report["gaps"])
    assert "reading it as decapsulation would be wrong" in joined


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
