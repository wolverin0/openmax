"""Stage 259A — regression tests for the XW ath_rate_atheros dissection.

Pins the structural fact that determines everything else: the module is stripped to only 74
defined symbols, which is why the rate ladder and PER thresholds are not reconstructible by
symbol lookup. A future run that reports a decoded ladder from 74 symbols is fabricating.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "dissect_stage259a_xw_ath_rate_atheros_re.py"
RECEIPT = REPO / "artifacts" / "autoresearch" / "stage259a_xw_ath_rate_atheros_re.json"


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "259A"
    for k in ("meta", "module", "summary", "gaps"):
        assert k in report


def test_module_present_and_sized(report: dict) -> None:
    assert report["summary"]["module_present"] is True
    assert report["module"]["status"] == "ok"
    assert report["module"]["bytes"] == 139128


def test_kernel_abi_is_71_not_68(report: dict) -> None:
    assert "2.6.32.71" in report["meta"]["module"]
    assert "2.6.32.68" not in report["meta"]["module"]


def test_symbol_budget_is_seventy_four(report: dict) -> None:
    assert report["summary"]["symbols"] == 74, \
        "the module is stripped; a much larger symbol count means a different module"


def test_surface_counts(report: dict) -> None:
    s = report["summary"]
    assert s["rate_symbols"] == 34
    assert s["per_symbols"] == 6
    assert s["retry_symbols"] == 0


def test_per_and_retry_histograms_are_empty(report: dict) -> None:
    # the stage must not manufacture thresholds it did not find
    assert report["per"]["constant_histogram"] == {}
    assert report["retry"]["constant_histogram"] == {}


def test_single_data_array_and_no_ladder_claim(report: dict) -> None:
    s = report["summary"]
    assert s["data_arrays"] == 1
    assert s["largest_array_entries"] == 20
    gaps = " ".join(report["gaps"])
    assert "not as decoded descriptors" in gaps


def test_no_retry_symbols_means_no_retry_ladder(report: dict) -> None:
    assert report["retry"]["symbols"] == []
    gaps = " ".join(report["gaps"])
    assert "not a retry ladder" in gaps


def test_relocations_are_the_available_lead(report: dict) -> None:
    m = report["meta"]["method"]
    assert ".rel.data" in m


def test_radio_safety(report: dict) -> None:
    assert "no module loaded" in report["meta"]["scope"]
    assert "no radio contacted" in report["meta"]["scope"]


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
