"""Stage 615A — regression tests.

Pins the TXBF-as-capability reading, the absent sounding identifiers, the `bf_` TX-buffer
disambiguation with its twelve markers, and the XW feature-free UMAC.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "build_stage615a_qca988x_txbf_beamforming_and_stbc_ldpc_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage615a_qca988x_txbf_beamforming_and_stbc_ldpc_re.json")

GETTERS = {"Getting LDPC", "Getting TX STBC", "Getting RX STBC", "Getting VHT MCS MAP"}


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "615A"
    for k in ("meta", "modules", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_seven_modules(ok: list[dict], report: dict) -> None:
    assert len(ok) == 7
    assert report["summary"]["modules_ok"] == 7
    names = {r["module"].split(":")[1] for r in ok}
    assert names == {"umac.ko", "ath_dev.ko", "ath_hal.ko"}


def test_token_totals(report: dict) -> None:
    s = report["summary"]
    assert s["txbf_tokens"] == 14
    assert s["stbc_tokens"] == 38
    assert s["ldpc_tokens"] == 18
    assert s["txbf_named"] == 1


def test_no_sounding(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["sounding_token_hits"] == 0
    assert s["sounding_absent"] == 1
    for r in ok:
        assert r["tokens"]["sounding"] == 0
        assert r["tokens"]["SU-BF"] == 0
        assert r["tokens"]["beamform"] == 0


def test_capability_table_and_rejection(report: dict) -> None:
    s = report["summary"]
    assert s["capability_table_modules"] == 2
    assert s["capability_table_named"] == 1
    assert s["txbf_not_supported_modules"] == 2
    assert s["maxregpwr_txbf_modules"] == 2


def test_runtime_getters(report: dict) -> None:
    s = report["summary"]
    assert s["runtime_getter_count"] == 4
    assert set(s["runtime_getters"]) == GETTERS
    assert s["capability_readable"] == 1
    assert set(s["proc_knobs"]) == {"LDPC", "getLDPC"}


def test_bf_underscore_is_a_tx_buffer(report: dict) -> None:
    s = report["summary"]
    assert s["bf_means_buffer"] == 1
    assert s["bf_buffer_marker_hits"] == 12
    assert s["bf_underscore_modules"] == 2
    joined = " ".join(report["gaps"])
    assert "TX buffer struct" in joined


def test_xw_has_no_feature_vocabulary(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["xw_umac_token_total"] == 0
    assert s["xw_umac_feature_free"] == 1
    xw = [r for r in ok if r["module"].startswith("XW")]
    assert len(xw) == 1
    assert sum(xw[0]["tokens"].values()) == 0
    assert xw[0]["bytes"] == 884988


def test_engine_not_recovered(report: dict) -> None:
    s = report["summary"]
    assert s["txbf_engine_recovered"] == 0
    assert s["sounding_sequence_recovered"] == 0


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
