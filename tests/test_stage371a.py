"""Stage 371A — regression tests.

Pins the two refuted premises (no ath10k_core.ko, no rx_ppdu_end/evm_p0 field names), the one
real symbol (`htt_rx_amsdu_pop` in umac.ko), and the ranging arithmetic. The EVM table must
never be reported recovered.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "qca988x_rx_ppdu_end_84byte_evm_ranging_re.py"
RECEIPT = REPO / "artifacts" / "autoresearch" / "stage371a_qca988x_rx_ppdu_end_evm_ranging_re.json"


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "371A"
    for k in ("meta", "modules", "summary", "gaps", "ranging_math"):
        assert k in report


def test_ath10k_core_absent(report: dict) -> None:
    assert report["ath10k_modules_found"] == []
    assert report["summary"]["ath10k_core_present"] is False
    assert "ath10k_core.ko does not exist" in " ".join(report["meta"]["premise_corrections"])


def test_field_names_absent(ok: list[dict]) -> None:
    # exclusions: the ath10k descriptor names must not appear anywhere
    for r in ok:
        hits = r["field_string_hits"]
        assert hits["rx_ppdu_end"] == 0
        assert hits["evm_p0"] == 0
        assert hits["evm_p15"] == 0
        assert hits["locationing_timestamp"] == 0
        assert hits["ppdu_end"] == 0


def test_amsdu_pop_is_real(ok: list[dict], report: dict) -> None:
    umacs = [r for r in ok if r["module"].endswith("umac.ko")]
    assert len(umacs) == 2
    for r in umacs:
        assert "htt_rx_amsdu_pop" in r["amsdu_pop_symbols"]
        assert r["field_string_hits"]["htt_rx_amsdu_pop"] == 4
    assert report["summary"]["amsdu_pop_hits"] == 4


def test_no_geometry_constants_found(ok: list[dict], report: dict) -> None:
    for r in ok:
        assert r["geometry"]["histogram"] == {}
    assert report["summary"]["geometry_constants"] == 0


def test_evm_table_not_recovered(report: dict) -> None:
    assert report["summary"]["evm_table_recovered"] == 0
    assert "no EVM table was recovered" in " ".join(report["gaps"])


def test_ranging_arithmetic(report: dict) -> None:
    rm = report["ranging_math"]
    assert rm["sample_ns"] == 12.5
    assert rm["sample_rate_mhz"] == 80.0
    assert 1.87 <= rm["round_trip_metres"] <= 1.88


def test_four_modules(ok: list[dict]) -> None:
    assert len(ok) == 4
    assert {r["module"].split(":")[1] for r in ok} == {"umac.ko", "ath_dev.ko"}


def test_radio_safety(report: dict) -> None:
    assert "no module loaded" in report["meta"]["scope"]
    assert "no radio contacted" in report["meta"]["scope"]


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
